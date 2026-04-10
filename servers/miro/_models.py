"""
Miro MCP Server - Pydantic Models

Generated: 2026-04-10 09:37:06 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AttachTagToItemRequest",
    "CopyBoardRequest",
    "CreateAppCardItemRequest",
    "CreateBoardRequest",
    "CreateCardItemRequest",
    "CreateCaseRequest",
    "CreateConnectorRequest",
    "CreateDocFormatItemRequest",
    "CreateDocumentItemUsingFileFromDeviceRequest",
    "CreateDocumentItemUsingUrlRequest",
    "CreateEmbedItemRequest",
    "CreateFrameItemRequest",
    "CreateImageItemUsingLocalFileRequest",
    "CreateImageItemUsingUrlRequest",
    "CreateItemsRequest",
    "CreateLegalHoldRequest",
    "CreateMindmapNodesExperimentalRequest",
    "CreateShapeItemFlowchartRequest",
    "CreateShapeItemRequest",
    "CreateStickyNoteItemRequest",
    "CreateTagRequest",
    "CreateTextItemRequest",
    "CreateUserRequest",
    "DeleteAppCardItemRequest",
    "DeleteBoardRequest",
    "DeleteCardItemRequest",
    "DeleteCaseRequest",
    "DeleteConnectorRequest",
    "DeleteDocFormatItemRequest",
    "DeleteDocumentItemRequest",
    "DeleteEmbedItemRequest",
    "DeleteFrameItemRequest",
    "DeleteGroupRequest",
    "DeleteImageItemRequest",
    "DeleteItemExperimentalRequest",
    "DeleteItemRequest",
    "DeleteLegalHoldRequest",
    "DeleteMindmapNodeExperimentalRequest",
    "DeleteShapeItemFlowchartRequest",
    "DeleteShapeItemRequest",
    "DeleteStickyNoteItemRequest",
    "DeleteTagRequest",
    "DeleteTextItemRequest",
    "DeleteUserRequest",
    "EditCaseRequest",
    "EditLegalHoldRequest",
    "EnterpriseAddProjectMemberRequest",
    "EnterpriseBoardContentItemLogsFetchRequest",
    "EnterpriseBoardExportJobResultsRequest",
    "EnterpriseBoardExportJobsRequest",
    "EnterpriseBoardExportJobStatusRequest",
    "EnterpriseBoardExportJobTasksRequest",
    "EnterpriseBoardsCreateGroupRequest",
    "EnterpriseBoardsDeleteGroupsRequest",
    "EnterpriseBoardsGetGroupsRequest",
    "EnterpriseCreateBoardExportRequest",
    "EnterpriseCreateBoardExportTaskExportLinkRequest",
    "EnterpriseCreateGroupMemberRequest",
    "EnterpriseCreateGroupRequest",
    "EnterpriseCreateProjectRequest",
    "EnterpriseCreateTeamRequest",
    "EnterpriseDataclassificationBoardGetRequest",
    "EnterpriseDataclassificationTeamBoardsBulkRequest",
    "EnterpriseDeleteGroupMemberRequest",
    "EnterpriseDeleteGroupRequest",
    "EnterpriseDeleteProjectMemberRequest",
    "EnterpriseDeleteProjectRequest",
    "EnterpriseDeleteTeamMemberRequest",
    "EnterpriseDeleteTeamRequest",
    "EnterpriseGetAuditLogsRequest",
    "EnterpriseGetGroupMemberRequest",
    "EnterpriseGetGroupMembersRequest",
    "EnterpriseGetGroupRequest",
    "EnterpriseGetGroupsRequest",
    "EnterpriseGetOrganizationMemberRequest",
    "EnterpriseGetOrganizationMembersRequest",
    "EnterpriseGetOrganizationRequest",
    "EnterpriseGetProjectMemberRequest",
    "EnterpriseGetProjectMembersRequest",
    "EnterpriseGetProjectRequest",
    "EnterpriseGetProjectsRequest",
    "EnterpriseGetTeamMemberRequest",
    "EnterpriseGetTeamMembersRequest",
    "EnterpriseGetTeamRequest",
    "EnterpriseGetTeamsRequest",
    "EnterpriseGroupsGetTeamRequest",
    "EnterpriseGroupsGetTeamsRequest",
    "EnterpriseInviteTeamMemberRequest",
    "EnterprisePostUserSessionsResetRequest",
    "EnterpriseProjectCreateGroupRequest",
    "EnterpriseProjectDeleteGroupsRequest",
    "EnterpriseProjectsGetGroupsRequest",
    "EnterpriseTeamsCreateGroupRequest",
    "EnterpriseTeamsDeleteGroupRequest",
    "EnterpriseTeamsGetGroupRequest",
    "EnterpriseTeamsGetGroupsRequest",
    "EnterpriseUpdateBoardExportJobRequest",
    "EnterpriseUpdateGroupMembersRequest",
    "EnterpriseUpdateGroupRequest",
    "EnterpriseUpdateProjectMemberRequest",
    "EnterpriseUpdateProjectRequest",
    "EnterpriseUpdateTeamMemberRequest",
    "EnterpriseUpdateTeamRequest",
    "GetAllCasesRequest",
    "GetAllGroupsRequest",
    "GetAllLegalHoldsRequest",
    "GetAppCardItemRequest",
    "GetBoardMembersRequest",
    "GetBoardsRequest",
    "GetCardItemRequest",
    "GetCaseRequest",
    "GetConnectorRequest",
    "GetConnectorsRequest",
    "GetDocFormatItemRequest",
    "GetDocumentItemRequest",
    "GetEmbedItemRequest",
    "GetFrameItemRequest",
    "GetGroupByIdRequest",
    "GetGroupRequest",
    "GetImageItemRequest",
    "GetItemsByGroupIdRequest",
    "GetItemsByTagRequest",
    "GetItemsExperimentalRequest",
    "GetItemsRequest",
    "GetItemsWithinFrameRequest",
    "GetLegalHoldContentItemsRequest",
    "GetLegalHoldExportJobsRequest",
    "GetLegalHoldRequest",
    "GetMetricsRequest",
    "GetMetricsTotalRequest",
    "GetMindmapNodeExperimentalRequest",
    "GetMindmapNodesExperimentalRequest",
    "GetResourceTypeRequest",
    "GetSchemaRequest",
    "GetShapeItemFlowchartRequest",
    "GetShapeItemRequest",
    "GetSpecificBoardMemberRequest",
    "GetSpecificBoardRequest",
    "GetSpecificItemExperimentalRequest",
    "GetSpecificItemRequest",
    "GetStickyNoteItemRequest",
    "GetTagRequest",
    "GetTagsFromBoardRequest",
    "GetTagsFromItemRequest",
    "GetTextItemRequest",
    "GetUserRequest",
    "ListGroupsRequest",
    "ListUsersRequest",
    "PatchGroupRequest",
    "PatchUserRequest",
    "RemoveBoardMemberRequest",
    "RemoveTagFromItemRequest",
    "ReplaceUserRequest",
    "ShareBoardRequest",
    "UnGroupRequest",
    "UpdateAppCardItemRequest",
    "UpdateBoardMemberRequest",
    "UpdateBoardRequest",
    "UpdateCardItemRequest",
    "UpdateConnectorRequest",
    "UpdateDocumentItemUsingFileFromDeviceRequest",
    "UpdateDocumentItemUsingUrlRequest",
    "UpdateEmbedItemRequest",
    "UpdateFrameItemRequest",
    "UpdateGroupRequest",
    "UpdateImageItemUsingFileFromDeviceRequest",
    "UpdateImageItemUsingUrlRequest",
    "UpdateItemPositionOrParentRequest",
    "UpdateShapeItemFlowchartRequest",
    "UpdateShapeItemRequest",
    "UpdateStickyNoteItemRequest",
    "UpdateTagRequest",
    "UpdateTextItemRequest",
    "Caption",
    "CreateUserBodyPhotosItem",
    "CreateUserBodyRolesItem",
    "CustomField",
    "ItemCreate",
    "LegalHoldRequestScopeUsers",
    "PatchGroupBodyOperationsItem",
    "PatchUserBodyOperationsItem",
    "ReplaceUserBodyEmailsItem",
    "ReplaceUserBodyGroupsItem",
    "ReplaceUserBodyPhotosItem",
    "ReplaceUserBodyRolesItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_audit_logs
class EnterpriseGetAuditLogsRequestQuery(StrictModel):
    created_after: str = Field(default=..., validation_alias="createdAfter", serialization_alias="createdAfter", description="Start of the date range for audit log retrieval in UTC ISO 8601 format with milliseconds (e.g., 2023-03-30T17:26:50.000Z). Audit logs created on or after this timestamp will be included.")
    created_before: str = Field(default=..., validation_alias="createdBefore", serialization_alias="createdBefore", description="End of the date range for audit log retrieval in UTC ISO 8601 format with milliseconds (e.g., 2023-04-30T17:26:50.000Z). Audit logs created before this timestamp will be included.")
    limit: int | None = Field(default=None, description="Maximum number of audit log entries to return per request. Defaults to 100. Use pagination with the cursor from the response to retrieve additional results beyond this limit.")
    sorting: Literal["ASC", "DESC"] | None = Field(default=None, description="Sort order for results based on audit log creation date. Choose ASC for oldest-first or DESC for newest-first ordering. Defaults to ASC.")
class EnterpriseGetAuditLogsRequest(StrictModel):
    """Retrieve audit events from your enterprise within a specified date range (limited to the last 90 days). Use pagination and sorting to navigate large result sets efficiently."""
    query: EnterpriseGetAuditLogsRequestQuery

# Operation: update_team_boards_classification_bulk
class EnterpriseDataclassificationTeamBoardsBulkRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization. This is a numeric ID that identifies which organization owns the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team whose boards will be updated. This is a numeric ID that identifies the specific team within the organization.")
class EnterpriseDataclassificationTeamBoardsBulkRequestBody(StrictModel):
    label_id: int | None = Field(default=None, validation_alias="labelId", serialization_alias="labelId", description="The numeric ID of the data classification label to assign to the boards. This label must be valid for the organization.", json_schema_extra={'format': 'int64'})
    not_classified_only: bool | None = Field(default=None, validation_alias="notClassifiedOnly", serialization_alias="notClassifiedOnly", description="When true, applies the classification label only to boards that are not yet classified. When false or omitted, applies the label to all boards in the team regardless of current classification status.")
class EnterpriseDataclassificationTeamBoardsBulkRequest(StrictModel):
    """Bulk update data classification labels for boards within a team. Optionally target only unclassified boards or apply the classification to all boards in the team."""
    path: EnterpriseDataclassificationTeamBoardsBulkRequestPath
    body: EnterpriseDataclassificationTeamBoardsBulkRequestBody | None = None

# Operation: get_board_data_classification
class EnterpriseDataclassificationBoardGetRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the board. Use the organization ID provided in your Enterprise account.")
    team_id: str = Field(default=..., description="The unique identifier of the team within the organization that contains the board.")
    board_id: str = Field(default=..., description="The unique identifier of the board whose data classification you want to retrieve.")
class EnterpriseDataclassificationBoardGetRequest(StrictModel):
    """Retrieves the data classification level assigned to a specific board within an organization and team. This enterprise-only endpoint requires Company Admin role and the boards:read scope."""
    path: EnterpriseDataclassificationBoardGetRequestPath

# Operation: create_markdown_doc
class CreateDocFormatItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the markdown document will be created.")
class CreateDocFormatItemRequestBodyData(StrictModel):
    content_type: Literal["markdown"] = Field(default=..., validation_alias="contentType", serialization_alias="contentType", description="The format type for the document content. Must be set to 'markdown' to specify markdown formatting.")
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The markdown-formatted text content for the document.")
class CreateDocFormatItemRequestBody(StrictModel):
    data: CreateDocFormatItemRequestBodyData
class CreateDocFormatItemRequest(StrictModel):
    """Creates a new markdown document item on a board. The document is formatted as markdown text and will be added to the specified board."""
    path: CreateDocFormatItemRequestPath
    body: CreateDocFormatItemRequestBody

# Operation: get_doc_format_item
class GetDocFormatItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the doc format item to retrieve.")
class GetDocFormatItemRequestQuery(StrictModel):
    text_content_type: Literal["html", "markdown"] | None = Field(default=None, validation_alias="textContentType", serialization_alias="textContentType", description="Specifies the format for the returned doc's content as either HTML or Markdown. If not specified, the default format is used.")
class GetDocFormatItemRequest(StrictModel):
    """Retrieves a specific doc format item from a board. Returns the item's metadata and content, with optional control over the content format."""
    path: GetDocFormatItemRequestPath
    query: GetDocFormatItemRequestQuery | None = None

# Operation: delete_doc_format_item
class DeleteDocFormatItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the doc format item to delete from the board.")
class DeleteDocFormatItemRequest(StrictModel):
    """Permanently removes a doc format item from a board. This action cannot be undone and requires write access to the board."""
    path: DeleteDocFormatItemRequestPath

# Operation: list_cases
class GetAllCasesRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the cases to retrieve.", pattern='^[0-9]+$')
class GetAllCasesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of cases to return in the response, between 1 and 100 items (defaults to 100).", json_schema_extra={'format': 'int32'})
class GetAllCasesRequest(StrictModel):
    """Retrieves all eDiscovery cases in an organization. Requires Enterprise Guard add-on and eDiscovery Admin role."""
    path: GetAllCasesRequestPath
    query: GetAllCasesRequestQuery | None = None

# Operation: create_case
class CreateCaseRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization where the case will be created.", pattern='^[0-9]+$')
class CreateCaseRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the case that identifies the legal matter or investigation.")
    description: str | None = Field(default=None, description="Optional additional details or context about the case to help organize and document the legal hold.")
class CreateCaseRequest(StrictModel):
    """Create a new legal hold case in your organization to initiate the eDiscovery process. Cases serve as containers for grouping multiple legal holds together during litigation or investigations. Requires Enterprise Guard add-on and eDiscovery Admin role."""
    path: CreateCaseRequestPath
    body: CreateCaseRequestBody

# Operation: get_case
class GetCaseRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the case. Must be a numeric string.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case to retrieve. Must be a numeric string.", pattern='^[0-9]+$')
class GetCaseRequest(StrictModel):
    """Retrieve detailed information about a specific case within an organization. This operation requires Enterprise Guard add-on and appropriate admin roles (Company Admin and eDiscovery Admin)."""
    path: GetCaseRequestPath

# Operation: update_case
class EditCaseRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the case to be edited.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case to be edited.", pattern='^[0-9]+$')
class EditCaseRequestBody(StrictModel):
    name: str = Field(default=..., description="The updated name for the case. This field is required and helps maintain clarity and consistency across stakeholders.")
    description: str | None = Field(default=None, description="An optional description providing additional context or details about the case, such as scope, focus, or internal documentation standards.")
class EditCaseRequest(StrictModel):
    """Update case details such as name and description to keep case information accurate and aligned with the evolving scope of a legal matter. This operation is restricted to eDiscovery Admins and requires the Enterprise Guard add-on."""
    path: EditCaseRequestPath
    body: EditCaseRequestBody

# Operation: close_case
class DeleteCaseRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the case to close.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case to close and delete.", pattern='^[0-9]+$')
class DeleteCaseRequest(StrictModel):
    """Permanently close and delete a case, marking the conclusion of a legal matter or investigation. All associated legal holds must be closed before closing the case. Requires Enterprise Guard add-on with Company Admin and eDiscovery Admin roles."""
    path: DeleteCaseRequestPath

# Operation: list_legal_holds_in_case
class GetAllLegalHoldsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the case. Must be a numeric string.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case for which to retrieve legal holds. Must be a numeric string.", pattern='^[0-9]+$')
class GetAllLegalHoldsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of legal holds to return in the response. Accepts values between 1 and 100, with a default of 100 items.", json_schema_extra={'format': 'int32'})
class GetAllLegalHoldsRequest(StrictModel):
    """Retrieves all legal holds associated with a specific case within an organization. This operation is restricted to Enterprise Guard users with Company Admin and eDiscovery Admin roles."""
    path: GetAllLegalHoldsRequestPath
    query: GetAllLegalHoldsRequestQuery | None = None

# Operation: create_legal_hold_for_case
class CreateLegalHoldRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization where the legal hold will be created.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case within the organization where the legal hold will be applied.", pattern='^[0-9]+$')
class CreateLegalHoldRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the legal hold to identify its purpose or scope.")
    description: str | None = Field(default=None, description="An optional detailed description providing additional context or information about the legal hold.")
    scope: LegalHoldRequestScopeUsers = Field(default=..., description="The scope criteria for the legal hold, currently supporting only the 'users' variant. Specify a list of up to 200 users to place under hold; this list must include all users for new holds or updates, as it replaces any previous user list.")
class CreateLegalHoldRequest(StrictModel):
    """Create a new legal hold within a case to preserve content owned, co-owned, created, edited, or accessed by specified users. Legal holds may take up to 24 hours to process."""
    path: CreateLegalHoldRequestPath
    body: CreateLegalHoldRequestBody

# Operation: list_legal_hold_export_jobs
class GetLegalHoldExportJobsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the case. Must be a valid organization ID in numeric format.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the legal hold case for which to retrieve export jobs. Must be a valid case ID in numeric format.", pattern='^[0-9]+$')
class GetLegalHoldExportJobsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of export jobs to return in the response. Accepts values between 1 and 100, with a default of 100 items.", json_schema_extra={'format': 'int32'})
class GetLegalHoldExportJobsRequest(StrictModel):
    """Retrieves all board export jobs for a specific legal hold case. This operation is available only to Enterprise Guard users with both Company Admin and eDiscovery Admin roles."""
    path: GetLegalHoldExportJobsRequestPath
    query: GetLegalHoldExportJobsRequestQuery | None = None

# Operation: get_legal_hold
class GetLegalHoldRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the legal hold. Must be a numeric string.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case containing the legal hold. Must be a numeric string.", pattern='^[0-9]+$')
    legal_hold_id: str = Field(default=..., description="The numeric ID of the legal hold to retrieve. Must be a numeric string.", pattern='^[0-9]+$')
class GetLegalHoldRequest(StrictModel):
    """Retrieve detailed information about a specific legal hold within a case. This operation requires Enterprise Guard add-on and appropriate admin roles (Company Admin and eDiscovery Admin)."""
    path: GetLegalHoldRequestPath

# Operation: update_legal_hold
class EditLegalHoldRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the legal hold. Must be a numeric string.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case containing the legal hold. Must be a numeric string.", pattern='^[0-9]+$')
    legal_hold_id: str = Field(default=..., description="The numeric ID of the legal hold to update. Must be a numeric string.", pattern='^[0-9]+$')
class EditLegalHoldRequestBody(StrictModel):
    name: str = Field(default=..., description="The name assigned to the legal hold. Used to identify the hold within the case.")
    description: str | None = Field(default=None, description="Optional description providing additional context or details about the legal hold and its scope.")
    scope: LegalHoldRequestScopeUsers = Field(default=..., description="The scope criteria determining which content items are preserved under this hold. Currently supports the `users` variant to place specific users under hold. Provide a complete list of all users to be preserved (up to 200 users per hold), including both newly added and previously held users. The system will ignore any unexpected scope variants for forward compatibility.")
class EditLegalHoldRequest(StrictModel):
    """Update an existing legal hold to adjust preservation scope as case requirements evolve. Modify the hold's name, description, and add or remove users and boards to ensure accurate data preservation throughout the legal process."""
    path: EditLegalHoldRequestPath
    body: EditLegalHoldRequestBody

# Operation: close_legal_hold
class DeleteLegalHoldRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the legal hold to close.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case containing the legal hold to close.", pattern='^[0-9]+$')
    legal_hold_id: str = Field(default=..., description="The numeric ID of the legal hold to close and permanently delete.", pattern='^[0-9]+$')
class DeleteLegalHoldRequest(StrictModel):
    """Close and permanently delete a legal hold in a case, releasing preserved Miro boards and custodians back to normal operations. Note: content release may take up to 24 hours to complete."""
    path: DeleteLegalHoldRequestPath

# Operation: list_legal_hold_content_items
class GetLegalHoldContentItemsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The numeric ID of the organization containing the case and legal hold.", pattern='^[0-9]+$')
    case_id: str = Field(default=..., description="The numeric ID of the case containing the legal hold.", pattern='^[0-9]+$')
    legal_hold_id: str = Field(default=..., description="The numeric ID of the legal hold for which to retrieve preserved content items.", pattern='^[0-9]+$')
class GetLegalHoldContentItemsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of content items to return in a single response, between 1 and 100 items. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class GetLegalHoldContentItemsRequest(StrictModel):
    """Retrieve all content items (Miro boards) currently under a specific legal hold within a case. Verify the legal hold is in 'ACTIVE' state to ensure all preserved content has finished processing."""
    path: GetLegalHoldContentItemsRequestPath
    query: GetLegalHoldContentItemsRequestQuery | None = None

# Operation: list_board_export_jobs
class EnterpriseBoardExportJobsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization whose board export jobs you want to retrieve.")
class EnterpriseBoardExportJobsRequestQuery(StrictModel):
    status: list[str] | None = Field(default=None, description="Filter results by job status. Accepts multiple statuses such as JOB_STATUS_CREATED, JOB_STATUS_IN_PROGRESS, JOB_STATUS_CANCELLED, or JOB_STATUS_FINISHED. If not specified, all statuses are returned.")
    creator_id: list[int] | None = Field(default=None, validation_alias="creatorId", serialization_alias="creatorId", description="Filter results by the user ID of the job creator. Accepts multiple creator IDs to retrieve jobs created by specific users.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 500. Defaults to 50. If the total results exceed this limit, a cursor is provided for pagination.", json_schema_extra={'format': 'int32'})
class EnterpriseBoardExportJobsRequest(StrictModel):
    """Retrieves a list of board export jobs for an organization, filtered by status, creator, and pagination limits. Enterprise-only endpoint requiring Company Admin role with eDiscovery enabled."""
    path: EnterpriseBoardExportJobsRequestPath
    query: EnterpriseBoardExportJobsRequestQuery | None = None

# Operation: create_board_export_job
class EnterpriseCreateBoardExportRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the boards to be exported.")
class EnterpriseCreateBoardExportRequestQuery(StrictModel):
    request_id: str = Field(default=..., description="A unique identifier (UUID format) for this export job request, used to track and reference the job.", json_schema_extra={'format': 'uuid'})
class EnterpriseCreateBoardExportRequestBody(StrictModel):
    board_ids: list[str] | None = Field(default=None, validation_alias="boardIds", serialization_alias="boardIds", description="List of board IDs to include in the export. Accepts 1 to 50 board IDs. If omitted, the behavior depends on your organization's default settings.", min_length=1, max_length=50)
    board_format: Literal["SVG", "HTML", "PDF"] | None = Field(default=None, validation_alias="boardFormat", serialization_alias="boardFormat", description="The output file format for the exported boards. Choose from SVG (default), HTML, or PDF. Defaults to SVG if not specified.")
class EnterpriseCreateBoardExportRequest(StrictModel):
    """Initiates an asynchronous export job for one or more boards in a specified format (SVG, HTML, or PDF). This enterprise-only operation requires Company Admin role and eDiscovery enablement."""
    path: EnterpriseCreateBoardExportRequestPath
    query: EnterpriseCreateBoardExportRequestQuery
    body: EnterpriseCreateBoardExportRequestBody | None = None

# Operation: get_board_export_job_status
class EnterpriseBoardExportJobStatusRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the export job.")
    job_id: str = Field(default=..., description="The unique identifier of the board export job, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class EnterpriseBoardExportJobStatusRequest(StrictModel):
    """Retrieves the current status of a board export job, including completion progress and results. Available only for Enterprise plan users with Company Admin role and eDiscovery enabled."""
    path: EnterpriseBoardExportJobStatusRequestPath

# Operation: get_board_export_job_results
class EnterpriseBoardExportJobResultsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization. This is a numeric string that identifies which organization's board export job to retrieve results for.")
    job_id: str = Field(default=..., description="The unique identifier of the export job. This is a UUID that identifies the specific board export job whose results you want to retrieve.", json_schema_extra={'format': 'uuid'})
class EnterpriseBoardExportJobResultsRequest(StrictModel):
    """Retrieves the results of a completed board export job, including the S3 link to the exported files. This operation is available only for Enterprise plan users with Company Admin role and eDiscovery enabled."""
    path: EnterpriseBoardExportJobResultsRequestPath

# Operation: cancel_board_export_job
class EnterpriseUpdateBoardExportJobRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the export job. This is a numeric string identifier.")
    job_id: str = Field(default=..., description="The unique identifier of the board export job to cancel. This must be a valid UUID format.", json_schema_extra={'format': 'uuid'})
class EnterpriseUpdateBoardExportJobRequestBody(StrictModel):
    status: Literal["CANCELLED"] = Field(default=..., description="The target status for the export job. Only CANCELLED is supported, which stops the ongoing export operation.")
class EnterpriseUpdateBoardExportJobRequest(StrictModel):
    """Cancel an ongoing board export job. This operation allows you to stop a board export job that is currently in progress by updating its status to CANCELLED."""
    path: EnterpriseUpdateBoardExportJobRequestPath
    body: EnterpriseUpdateBoardExportJobRequestBody

# Operation: list_board_export_job_tasks
class EnterpriseBoardExportJobTasksRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the export job.")
    job_id: str = Field(default=..., description="The unique identifier of the board export job (UUID format).", json_schema_extra={'format': 'uuid'})
class EnterpriseBoardExportJobTasksRequestQuery(StrictModel):
    status: list[str] | None = Field(default=None, description="Filter tasks by one or more statuses (e.g., TASK_STATUS_CREATED, TASK_STATUS_SCHEDULED, TASK_STATUS_SUCCESS, TASK_STATUS_ERROR, TASK_STATUS_CANCELLED). Omit to return tasks of all statuses.")
    limit: int | None = Field(default=None, description="Maximum number of tasks to return per request, between 1 and 500. Defaults to 50. Use pagination with the cursor parameter if more results are available.", json_schema_extra={'format': 'int32'})
class EnterpriseBoardExportJobTasksRequest(StrictModel):
    """Retrieves the list of tasks associated with a board export job. Use this to monitor the progress and status of individual export tasks within a job."""
    path: EnterpriseBoardExportJobTasksRequestPath
    query: EnterpriseBoardExportJobTasksRequestQuery | None = None

# Operation: create_board_export_task_download_link
class EnterpriseCreateBoardExportTaskExportLinkRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the export job. This is a numeric ID specific to your enterprise account.")
    job_id: str = Field(default=..., description="The unique identifier of the board export job. This must be a valid UUID that corresponds to an existing export job.", json_schema_extra={'format': 'uuid'})
    task_id: str = Field(default=..., description="The unique identifier of the specific task within the export job for which you want to create a download link. This must be a valid UUID that corresponds to an existing task.", json_schema_extra={'format': 'uuid'})
class EnterpriseCreateBoardExportTaskExportLinkRequest(StrictModel):
    """Generate a downloadable link for the results of a specific board export task within an enterprise export job. This endpoint is available only to Enterprise plan users with Company Admin role and eDiscovery enabled."""
    path: EnterpriseCreateBoardExportTaskExportLinkRequestPath

# Operation: list_board_item_content_logs
class EnterpriseBoardContentItemLogsFetchRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of your organization.")
class EnterpriseBoardContentItemLogsFetchRequestQuery(StrictModel):
    board_ids: list[str] | None = Field(default=None, description="Optional list of up to 15 board IDs to filter logs. If omitted, logs for all boards are returned.", max_length=15)
    emails: list[str] | None = Field(default=None, description="Optional list of up to 15 user email addresses to filter logs by who created, modified, or deleted board items.", max_length=15)
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="Start of the time range (UTC, ISO 8601 format with Z offset) for filtering logs by last modification date, inclusive.", json_schema_extra={'format': 'date-time'})
    to: str = Field(default=..., description="End of the time range (UTC, ISO 8601 format with Z offset) for filtering logs by last modification date, inclusive.", json_schema_extra={'format': 'date-time'})
    limit: int | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 1000. Defaults to 1000. Use pagination with the cursor parameter if results exceed this limit.", json_schema_extra={'format': 'int32'})
    sorting: Literal["asc", "desc"] | None = Field(default=None, description="Sort results by modification date in ascending (oldest first) or descending (newest first) order. Defaults to ascending.")
class EnterpriseBoardContentItemLogsFetchRequest(StrictModel):
    """Retrieve content change logs for board items within your organization over a specified time period. Filter by board IDs, user emails, and modification dates to track all updates, modifications, and deletions of board item content."""
    path: EnterpriseBoardContentItemLogsFetchRequestPath
    query: EnterpriseBoardContentItemLogsFetchRequestQuery

# Operation: delete_user_all_sessions
class EnterprisePostUserSessionsResetRequestQuery(StrictModel):
    email: str = Field(default=..., description="The email address of the user whose sessions should be terminated. The user will be signed out from all devices and applications immediately.")
class EnterprisePostUserSessionsResetRequest(StrictModel):
    """Immediately terminate all active sessions for a user across all devices, forcing them to sign in again. Use this to restrict access during security incidents, credential compromises, or when a user leaves the organization."""
    query: EnterprisePostUserSessionsResetRequestQuery

# Operation: list_users
class ListUsersRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results using expressions with attribute names and operators (eq, ne, co, sw, ew, pr, gt, ge, lt, le) combined with logical operators (and, or, not). Attribute names and operators are case-insensitive. Examples: userName eq \"user@miro.com\", active eq true, displayName co \"user\", groups.value eq \"3458764577585056871\", userType ne \"Full\".")
    start_index: int | None = Field(default=None, validation_alias="startIndex", serialization_alias="startIndex", description="The starting position for paginated results (1-based indexing). Use with count to retrieve specific pages of results.")
    count: int | None = Field(default=None, description="Maximum number of results to return per page. Defaults to 100; maximum allowed is 1000. Use with startIndex for pagination.")
    sort_by: str | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Attribute name to sort results by. Examples: userName, emails.value.")
    sort_order: Literal["ascending", "descending"] | None = Field(default=None, validation_alias="sortOrder", serialization_alias="sortOrder", description="Sort direction for the sortBy attribute: ascending or descending.")
class ListUsersRequest(StrictModel):
    """Retrieves a paginated list of users in your organization. Note: Only returns users who are organization members, not guest users."""
    query: ListUsersRequestQuery | None = None

# Operation: create_user
class CreateUserRequestBodyName(StrictModel):
    family_name: str = Field(default=..., validation_alias="familyName", serialization_alias="familyName", description="The user's last name. Combined with givenName, the total character count cannot exceed 60 characters. Used to construct the user's full name if displayName is not provided.")
    given_name: str = Field(default=..., validation_alias="givenName", serialization_alias="givenName", description="The user's first name. Combined with familyName, the total character count cannot exceed 60 characters. Used to construct the user's full name if displayName is not provided.")
class CreateUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20UserManager(StrictModel):
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The manager's identifier as a numeric value. Non-numeric values are ignored. This field maps to Miro's internal managerId field which expects a Long type.")
class CreateUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20User(StrictModel):
    employee_number: str | None = Field(default=None, validation_alias="employeeNumber", serialization_alias="employeeNumber", description="An internal employee identifier for the user, up to 20 characters.")
    cost_center: str | None = Field(default=None, validation_alias="costCenter", serialization_alias="costCenter", description="The cost center associated with the user, up to 120 characters.")
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="The organization name or identifier associated with the user, up to 120 characters.")
    division: str | None = Field(default=None, validation_alias="division", serialization_alias="division", description="The division within the organization associated with the user, up to 120 characters.")
    department: str | None = Field(default=None, validation_alias="department", serialization_alias="department", description="The department within the organization associated with the user, up to 120 characters.")
    manager: CreateUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20UserManager | None = Field(default=None, validation_alias="0:User", serialization_alias="0:User")
class CreateUserRequestBody(StrictModel):
    user_name: str = Field(default=..., validation_alias="userName", serialization_alias="userName", description="The unique email address that serves as the user's login identifier and username. This email becomes the user's full name if displayName or name attributes are not provided.")
    display_name: str | None = Field(default=None, validation_alias="displayName", serialization_alias="displayName", description="A human-readable full name for the user, up to 60 characters. When provided, this takes precedence over constructed names from givenName and familyName.")
    user_type: str | None = Field(default=None, validation_alias="userType", serialization_alias="userType", description="The user's license type in the organization. Supported values include: Full, Free, Free Restricted, Full (Trial), and Basic. When not specified, the license is assigned automatically based on the organization's plan.")
    active: bool | None = Field(default=None, description="Whether the user is active or deactivated in the organization. Defaults to active when not specified.")
    photos: list[CreateUserBodyPhotosItem] | None = Field(default=None, description="An array of profile photos for the user. Each photo must be a publicly accessible URL (jpg, jpeg, bmp, png, or gif format) with a maximum file size of 31 MB. The URL must include the file extension or the server response must include the appropriate Content-Type header.")
    roles: list[CreateUserBodyRolesItem] | None = Field(default=None, description="An array of roles assigned to the user. Organization-level roles include ORGANIZATION_INTERNAL_ADMIN and ORGANIZATION_INTERNAL_USER. Admin roles include Content Admin, User Admin, Security Admin, or custom admin role names. Each role entry specifies the role value, display name, type, and primary flag.")
    preferred_language: str | None = Field(default=None, validation_alias="preferredLanguage", serialization_alias="preferredLanguage", description="The user's preferred language in locale format (e.g., en_US for English). This setting controls the language used in the user's interface.")
    name: CreateUserRequestBodyName
    urn_ietf_params_scim_schemas_extension_enterprise_2_0_user: CreateUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20User | None = Field(default=None, validation_alias="urn:ietf:params:scim:schemas:extension:enterprise:2", serialization_alias="urn:ietf:params:scim:schemas:extension:enterprise:2")
class CreateUserRequest(StrictModel):
    """Creates a new user in the organization and automatically adds them to the default team. The user's identity is established via email address provided in the userName field."""
    body: CreateUserRequestBody

# Operation: get_user
class GetUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to retrieve. Must be a valid user ID for an organization member.")
class GetUserRequest(StrictModel):
    """Retrieves a single user resource by ID. Returns only users that are members of the organization; guest users are not included."""
    path: GetUserRequestPath

# Operation: update_user
class ReplaceUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique server-assigned identifier for the user being updated.")
class ReplaceUserRequestBodyName(StrictModel):
    family_name: str | None = Field(default=None, validation_alias="familyName", serialization_alias="familyName", description="The user's last name or surname.")
    given_name: str | None = Field(default=None, validation_alias="givenName", serialization_alias="givenName", description="The user's first name.")
class ReplaceUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20UserManager(StrictModel):
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The manager ID value. Must be numeric; non-numeric values are ignored by the system.")
class ReplaceUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20User(StrictModel):
    employee_number: str | None = Field(default=None, validation_alias="employeeNumber", serialization_alias="employeeNumber", description="A unique identifier for the user within the organization, up to 20 characters maximum.")
    cost_center: str | None = Field(default=None, validation_alias="costCenter", serialization_alias="costCenter", description="The cost center associated with the user, up to 120 characters maximum.")
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="The name of the organization the user belongs to, up to 120 characters maximum.")
    division: str | None = Field(default=None, validation_alias="division", serialization_alias="division", description="The division within the organization to which the user belongs, up to 120 characters maximum.")
    department: str | None = Field(default=None, validation_alias="department", serialization_alias="department", description="The department within the organization to which the user belongs, up to 120 characters maximum.")
    manager: ReplaceUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20UserManager | None = Field(default=None, validation_alias="0:User", serialization_alias="0:User")
class ReplaceUserRequestBody(StrictModel):
    """Payload to update user information."""
    user_name: str | None = Field(default=None, validation_alias="userName", serialization_alias="userName", description="The unique username or login identifier, typically an email address format.")
    display_name: str | None = Field(default=None, validation_alias="displayName", serialization_alias="displayName", description="A human-readable display name for the user, typically their full name.")
    user_type: str | None = Field(default=None, validation_alias="userType", serialization_alias="userType", description="A free-form string indicating the user's license type within the organization (e.g., 'Full'). Cannot be updated if the user is deactivated.")
    active: bool | None = Field(default=None, description="Boolean flag indicating whether the user is active or deactivated in the organization.")
    emails: list[ReplaceUserBodyEmailsItem] | None = Field(default=None, description="An array of email address objects, each containing a value, display name, and primary flag. Updates to this field are ignored for deactivated users.")
    photos: list[ReplaceUserBodyPhotosItem] | None = Field(default=None, description="An array of profile picture objects, each specifying a type.")
    groups: list[ReplaceUserBodyGroupsItem] | None = Field(default=None, description="An array of group/team objects the user belongs to, each containing the team's id and display name.")
    roles: list[ReplaceUserBodyRolesItem] | None = Field(default=None, description="An array of role objects assigned to the user, each containing role type, value, display name, and primary flag. Cannot be updated if the user is deactivated.")
    preferred_language: str | None = Field(default=None, validation_alias="preferredLanguage", serialization_alias="preferredLanguage", description="The user's preferred language, specified in locale format (e.g., en_US for English).")
    name: ReplaceUserRequestBodyName | None = None
    urn_ietf_params_scim_schemas_extension_enterprise_2_0_user: ReplaceUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20User | None = Field(default=None, validation_alias="urn:ietf:params:scim:schemas:extension:enterprise:2", serialization_alias="urn:ietf:params:scim:schemas:extension:enterprise:2")
class ReplaceUserRequest(StrictModel):
    """Replace an existing user resource with updated information. Note that deactivated users cannot have their userName, userType, or roles modified, and email updates for deactivated users are silently ignored. Only active organization members (non-guests) can be updated."""
    path: ReplaceUserRequestPath
    body: ReplaceUserRequestBody | None = None

# Operation: update_user_partial
class PatchUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique server-assigned identifier for the user being updated.")
class PatchUserRequestBody(StrictModel):
    """Payload to update user information. <br><br> The body of a PATCH request must contain the attribute `Operations`, and its value is an array of one or more PATCH operations. Each PATCH operation object must have exactly one "op" member."""
    schemas: list[Literal["urn:ietf:params:scim:api:messages:2.0:PatchOp"]] = Field(default=..., description="Schema identifier array that designates this request as a SCIM PatchOp. Must include the SCIM patch operation schema.")
    operations: list[PatchUserBodyOperationsItem] = Field(default=..., validation_alias="Operations", serialization_alias="Operations", description="Array of patch operations to apply to the user. Each operation specifies an action (Replace, Add, Remove), a target path, and a value. Supports operations for: activation status, display name, user type (license upgrade only), username, primary role (ORGANIZATION_INTERNAL_ADMIN or ORGANIZATION_INTERNAL_USER only), admin roles, and enterprise attributes (department, employeeNumber, costCenter, organization, division, manager). Guest roles and license downgrades are not supported.")
class PatchUserRequest(StrictModel):
    """Partially update a user resource by applying SCIM patch operations. Only specified fields are modified; unmodified fields remain unchanged. The user must be an active organization member (not a guest) to be updated."""
    path: PatchUserRequestPath
    body: PatchUserRequestBody

# Operation: delete_user
class DeleteUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to delete, assigned by the server.")
class DeleteUserRequest(StrictModel):
    """Permanently removes a user from the organization and transfers ownership of their boards to the oldest admin team member. The user must be an organization member (not a guest) and cannot be the last admin in their team or organization."""
    path: DeleteUserRequestPath

# Operation: list_groups
class ListGroupsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results using expressions with attribute names and operators (eq, ne, co, sw, ew, pr, gt, ge, lt, le) combined with logical operators (and, or, not). Values must be enclosed in parentheses. Filtering on complex attributes is not supported. Example: displayName eq \"Product Team\"")
    start_index: int | None = Field(default=None, validation_alias="startIndex", serialization_alias="startIndex", description="The starting position for paginated results (1-based indexing). Use with count to retrieve a specific page of results.")
    count: int | None = Field(default=None, description="Maximum number of results to return per page. Defaults to 100 with a maximum allowed value of 1000. Use with startIndex for pagination.")
    sort_by: str | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Attribute name to sort results by. Example: displayName")
    sort_order: Literal["ascending", "descending"] | None = Field(default=None, validation_alias="sortOrder", serialization_alias="sortOrder", description="Sort direction for the sortBy attribute. Must be either ascending or descending.")
class ListGroupsRequest(StrictModel):
    """Retrieves all groups (teams) in the organization along with their member users. Only users with member role in the organization are included in the results."""
    query: ListGroupsRequestQuery | None = None

# Operation: get_group
class GetGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique server-assigned identifier for the group (team) to retrieve.")
class GetGroupRequest(StrictModel):
    """Retrieves a single group (team) resource along with its member users. Only users with member role in the organization are included in the response."""
    path: GetGroupRequestPath

# Operation: update_group_members_and_details
class PatchGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique server-assigned identifier for the group (team) to update.")
class PatchGroupRequestBody(StrictModel):
    """Payload to add, replace, remove members in the specified group (team). <br><br> The body of a PATCH request must contain the attribute `Operations` and its value is an array of one or more PATCH operations. Each PATCH operation object must have exactly one `op` member."""
    schemas: Literal["urn:ietf:params:scim:api:messages:2.0:PatchOp"] = Field(default=..., description="Must be set to the PatchOp schema identifier to indicate this is a patch operation request.")
    operations: list[PatchGroupBodyOperationsItem] = Field(default=..., validation_alias="Operations", serialization_alias="Operations", description="An array of patch operations to perform on the group. Each operation specifies an action (add, remove, or replace), a target path, and values. Multiple users can be added or removed in a single request. To update the group display name, use replace operation with the new displayName value.")
class PatchGroupRequest(StrictModel):
    """Updates an existing group (team) by adding, removing, or replacing members, and modifying group properties like display name. Only specified attributes are updated; unchanged attributes remain as-is."""
    path: PatchGroupRequestPath
    body: PatchGroupRequestBody

# Operation: get_resource_type
class GetResourceTypeRequestPath(StrictModel):
    resource: Literal["User", "Group"] = Field(default=..., description="The resource type to retrieve metadata for. Must be either 'User' or 'Group'.")
class GetResourceTypeRequest(StrictModel):
    """Retrieve metadata for a supported resource type (User or Group). Use this to understand the structure and properties of the specified resource type."""
    path: GetResourceTypeRequestPath

# Operation: get_schema
class GetSchemaRequestPath(StrictModel):
    uri: Literal["urn:ietf:params:scim:schemas:core:2.0:User", "urn:ietf:params:scim:schemas:core:2.0:Group", "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"] = Field(default=..., description="The SCIM schema URI identifying the resource type: User, Group, or Enterprise User extension schema.")
class GetSchemaRequest(StrictModel):
    """Retrieve the SCIM schema definition for a specific resource type (User, Group, or Enterprise User), including details about supported attributes and their formatting requirements."""
    path: GetSchemaRequestPath

# Operation: get_organization
class EnterpriseGetOrganizationRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization to retrieve.")
class EnterpriseGetOrganizationRequest(StrictModel):
    """Retrieve detailed information about an organization. This endpoint is available only to Enterprise plan users with Company Admin role."""
    path: EnterpriseGetOrganizationRequestPath

# Operation: enterprise_get_organization_members
class EnterpriseGetOrganizationMembersRequestPath(StrictModel):
    org_id: str = Field(default=..., description="id of the organization")
class EnterpriseGetOrganizationMembersRequestQuery(StrictModel):
    emails: str | None = Field(default=None, description="Emails of the organization members you want to retrieve. If you specify a value for the `emails` parameter, only the `emails` parameter is considered. All other filtering parameters are ignored. Maximum emails size is 10. Example: `emails=someEmail1@miro.com,someEmail2@miro.com`")
    role: Literal["organization_internal_admin", "organization_internal_user", "organization_external_user", "organization_team_guest_user", "unknown"] | None = Field(default=None, description="Filter organization members by role")
    license_: Literal["full", "occasional", "free", "free_restricted", "full_trial", "unknown"] | None = Field(default=None, validation_alias="license", serialization_alias="license", description="Filter organization members by license")
    active: bool | None = Field(default=None, description="Filter results based on whether the user is active or deactivated. Learn more about <a target=\"blank\" href=\"https://help.miro.com/hc/en-us/articles/360025025894-Deactivated-users\">user deactivation</a>.")
    limit: int | None = Field(default=None, description="Limit for the number of organization members returned in the result list.", json_schema_extra={'format': 'int32'})
class EnterpriseGetOrganizationMembersRequest(StrictModel):
    """Get organization members"""
    path: EnterpriseGetOrganizationMembersRequestPath
    query: EnterpriseGetOrganizationMembersRequestQuery | None = None

# Operation: get_organization_member
class EnterpriseGetOrganizationMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the member.")
    member_id: str = Field(default=..., description="The unique identifier of the organization member whose information you want to retrieve.")
class EnterpriseGetOrganizationMemberRequest(StrictModel):
    """Retrieve detailed information about a specific member within an organization. This operation requires Enterprise plan access and Company Admin role."""
    path: EnterpriseGetOrganizationMemberRequestPath

# Operation: list_boards
class GetBoardsRequestQuery(StrictModel):
    team_id: str | None = Field(default=None, description="Filter results to boards within a specific team. When provided, overrides query and owner filters for faster results.")
    query: str | None = Field(default=None, description="Search for boards by name or description. Supports partial text matching up to 500 characters. Can be combined with the owner parameter to narrow results.", max_length=500)
    owner: str | None = Field(default=None, description="Filter results to boards owned by a specific user. Provide the owner's numeric ID, not their name. Can be combined with query to narrow results; ignored if team_id is provided.")
    limit: str | None = Field(default=None, description="Maximum number of boards to return per request. Must be between 1 and 50 boards; defaults to 20.")
    offset: str | None = Field(default=None, description="Zero-based offset for pagination. Use with limit to retrieve subsequent pages of results; defaults to 0.")
    sort: Literal["default", "last_modified", "last_opened", "last_created", "alphabetically"] | None = Field(default=None, description="Sort results by creation date, modification date, last opened date, or alphabetically by name. Defaults to last_created when filtering by team, otherwise last_opened.")
class GetBoardsRequest(StrictModel):
    """Retrieve a list of boards accessible to the authenticated user. Filter by team, project, owner, or search query, with support for pagination and sorting. Enterprise users with Content Admin permissions can access all boards including private ones (contents remain restricted)."""
    query: GetBoardsRequestQuery | None = None

# Operation: create_board
class CreateBoardRequestBodyPolicyPermissionsPolicy(StrictModel):
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field(default=None, validation_alias="collaborationToolsStartAccess", serialization_alias="collaborationToolsStartAccess", description="Controls who can initiate or stop collaboration features like timers, voting, video chat, and screen sharing. Other users can only join these features. Defaults to allowing all editors. Contact Miro support to modify this setting.")
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field(default=None, validation_alias="copyAccess", serialization_alias="copyAccess", description="Determines who can copy the board, duplicate objects, export images, or save as template/PDF. Defaults to allowing anyone. Options range from open access to board owner only.")
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field(default=None, validation_alias="sharingAccess", serialization_alias="sharingAccess", description="Controls who can modify board access permissions and invite new users. Defaults to team members with editing rights. Contact Miro support to change this setting.")
class CreateBoardRequestBodyPolicySharingPolicy(StrictModel):
    access: Literal["private", "view", "edit", "comment"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="Sets the public access level for the board. Defaults to private. Options include private (no public access), view-only, comment, or full edit access.")
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "no_access"] | None = Field(default=None, validation_alias="inviteToAccountAndBoardLinkAccess", serialization_alias="inviteToAccountAndBoardLinkAccess", description="Specifies the default user role when inviting users via team and board links. Defaults to no access. Enterprise users are always set to no access regardless of this value.")
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field(default=None, validation_alias="organizationAccess", serialization_alias="organizationAccess", description="Controls organization-level access to the board. Defaults to private. Only applies if the team belongs to an organization; otherwise defaults are used.")
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(default=None, validation_alias="teamAccess", serialization_alias="teamAccess", description="Sets team-level access to the board. Defaults to edit access on free plans and private on other plans. Options include private, view-only, comment, or edit access.")
class CreateBoardRequestBodyPolicy(StrictModel):
    permissions_policy: CreateBoardRequestBodyPolicyPermissionsPolicy | None = Field(default=None, validation_alias="permissionsPolicy", serialization_alias="permissionsPolicy")
    sharing_policy: CreateBoardRequestBodyPolicySharingPolicy | None = Field(default=None, validation_alias="sharingPolicy", serialization_alias="sharingPolicy")
class CreateBoardRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Optional description of the board's purpose or content. Limited to 300 characters.", min_length=0, max_length=300)
    name: str | None = Field(default=None, description="Display name for the board. Defaults to 'Untitled' if not provided. Must be between 1 and 60 characters.", min_length=1, max_length=60)
    team_id: str | None = Field(default=None, validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team where the board will be created. If not specified, the board is created in the default team. On Enterprise plans, board owners and admins can move boards between teams via API.")
    policy: CreateBoardRequestBodyPolicy | None = None
class CreateBoardRequest(StrictModel):
    """Creates a new board with a specified name, description, and access control policies. Configure sharing permissions, collaboration tool access, and team placement to control who can view, edit, and manage the board."""
    body: CreateBoardRequestBody | None = None

# Operation: create_board_copy
class CopyBoardRequestQuery(StrictModel):
    copy_from: str = Field(default=..., description="The unique identifier of the source board to duplicate. This board must exist and be accessible to the requesting user.")
class CopyBoardRequestBodyPolicyPermissionsPolicy(StrictModel):
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field(default=None, validation_alias="collaborationToolsStartAccess", serialization_alias="collaborationToolsStartAccess", description="Controls who can initiate or stop collaboration features like timers, voting, video chat, and screen sharing. Other users can only join these features. Defaults to allowing all editors. Contact Miro support to modify this setting.")
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field(default=None, validation_alias="copyAccess", serialization_alias="copyAccess", description="Determines who can copy the board, duplicate objects, export images, or save as template/PDF. Options range from unrestricted (anyone) to board owner only. Defaults to anyone.")
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field(default=None, validation_alias="sharingAccess", serialization_alias="sharingAccess", description="Controls who can modify board access settings and send invitations. Restricted to team members with editing rights or owner/co-owners only. Defaults to team members with editing rights. Contact Miro support to change this setting.")
class CopyBoardRequestBodyPolicySharingPolicy(StrictModel):
    access: Literal["private", "view", "edit", "comment"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="Sets the public access level for the board: private (no public access), view (read-only), edit (collaborative), or comment (feedback only). Defaults to private.")
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "no_access"] | None = Field(default=None, validation_alias="inviteToAccountAndBoardLinkAccess", serialization_alias="inviteToAccountAndBoardLinkAccess", description="Specifies the default user role when inviting via team and board link: viewer, commenter, editor, or no access. Enterprise users are always set to no access. Defaults to no access.")
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field(default=None, validation_alias="organizationAccess", serialization_alias="organizationAccess", description="Controls organization-level access to the board if it belongs to an organization. Options: private, view, comment, or edit. Defaults to private and is ignored for teams outside an organization.")
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(default=None, validation_alias="teamAccess", serialization_alias="teamAccess", description="Sets team-level access permissions: private (restricted), view (read-only), comment (feedback), or edit (collaborative). Defaults to edit on free plans and private on paid plans.")
class CopyBoardRequestBodyPolicy(StrictModel):
    permissions_policy: CopyBoardRequestBodyPolicyPermissionsPolicy | None = Field(default=None, validation_alias="permissionsPolicy", serialization_alias="permissionsPolicy")
    sharing_policy: CopyBoardRequestBodyPolicySharingPolicy | None = Field(default=None, validation_alias="sharingPolicy", serialization_alias="sharingPolicy")
class CopyBoardRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Optional text describing the new board's purpose or content. Limited to 300 characters maximum.", min_length=0, max_length=300)
    name: str | None = Field(default=None, description="Display name for the new board. Must be between 1 and 60 characters. Defaults to 'Untitled' if not provided.", min_length=1, max_length=60)
    team_id: str | None = Field(default=None, validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team where the new board should be created. If omitted, the board is placed in the default team.")
    policy: CopyBoardRequestBodyPolicy | None = None
class CopyBoardRequest(StrictModel):
    """Creates a duplicate of an existing board with optional customization of name, description, and access control policies. The new board can be placed in a specific team and configured with granular sharing and permission settings."""
    query: CopyBoardRequestQuery
    body: CopyBoardRequestBody | None = None

# Operation: get_board
class GetSpecificBoardRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board to retrieve. This is a required string that identifies which board's information should be returned.")
class GetSpecificBoardRequest(StrictModel):
    """Retrieve detailed information about a specific board by its unique identifier. This operation requires boards:read scope and is rate-limited at Level 1."""
    path: GetSpecificBoardRequestPath

# Operation: update_board
class UpdateBoardRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board to update.")
class UpdateBoardRequestBodyPolicyPermissionsPolicy(StrictModel):
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field(default=None, validation_alias="collaborationToolsStartAccess", serialization_alias="collaborationToolsStartAccess", description="Controls who can initiate collaboration tools (timer, voting, video chat, screen sharing, attention management). Others can only join. Defaults to all editors. Contact Miro Support to change this setting.")
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field(default=None, validation_alias="copyAccess", serialization_alias="copyAccess", description="Controls who can copy the board, copy objects, download images, and export as template or PDF. Options range from anyone to board owner only. Defaults to anyone.")
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field(default=None, validation_alias="sharingAccess", serialization_alias="sharingAccess", description="Controls who can modify board access and invite users. Defaults to team members with editing rights. Contact Miro Support to change this setting.")
class UpdateBoardRequestBodyPolicySharingPolicy(StrictModel):
    access: Literal["private", "view", "edit", "comment"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="Sets public-level access to the board: private (no public access), view (public read-only), edit (public editable), or comment (public comment-only). Defaults to private.")
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "no_access"] | None = Field(default=None, validation_alias="inviteToAccountAndBoardLinkAccess", serialization_alias="inviteToAccountAndBoardLinkAccess", description="Defines the user role assigned when inviting users via team and board link. Defaults to no_access. For Enterprise users, this is always set to no_access regardless of the value provided.")
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field(default=None, validation_alias="organizationAccess", serialization_alias="organizationAccess", description="Sets organization-level access to the board. Only applies if the board's team belongs to an organization. Defaults to private. Defaults to private if the team is not part of an organization.")
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(default=None, validation_alias="teamAccess", serialization_alias="teamAccess", description="Sets team-level access to the board. Defaults to edit on free plans and private on other plans.")
class UpdateBoardRequestBodyPolicy(StrictModel):
    permissions_policy: UpdateBoardRequestBodyPolicyPermissionsPolicy | None = Field(default=None, validation_alias="permissionsPolicy", serialization_alias="permissionsPolicy")
    sharing_policy: UpdateBoardRequestBodyPolicySharingPolicy | None = Field(default=None, validation_alias="sharingPolicy", serialization_alias="sharingPolicy")
class UpdateBoardRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Board description text. Must be between 0 and 300 characters.", min_length=0, max_length=300)
    name: str | None = Field(default=None, description="Board display name. Must be between 1 and 60 characters. Defaults to 'Untitled' if not specified.", min_length=1, max_length=60)
    team_id: str | None = Field(default=None, validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team where the board should be moved. On Enterprise plans, Board Owners, Co-Owners, and Content Admins can move boards. On non-Enterprise plans, only Board Owners can move boards.")
    policy: UpdateBoardRequestBodyPolicy | None = None
class UpdateBoardRequest(StrictModel):
    """Update board settings including name, description, and access control permissions. Requires boards:write scope and is subject to rate limiting at Level 2."""
    path: UpdateBoardRequestPath
    body: UpdateBoardRequestBody | None = None

# Operation: delete_board
class DeleteBoardRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board to delete. This is a required string that identifies which board will be removed.")
class DeleteBoardRequest(StrictModel):
    """Permanently delete a board, moving it to Trash on paid plans where it can be restored within 90 days. On free plans, deletion may be immediate."""
    path: DeleteBoardRequestPath

# Operation: create_app_card
class CreateAppCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the app card will be created.")
class CreateAppCardItemRequestBodyData(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A short text description providing context about the app card's purpose or content.")
    fields: list[CustomField] | None = Field(default=None, validation_alias="fields", serialization_alias="fields", description="An array of custom preview field objects that will be displayed in the bottom half of the app card in compact view. Each field object defines a key-value pair for the preview.")
    status: Literal["disconnected", "connected", "disabled"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The synchronization status of the app card with its source. Use 'disconnected' for new cards, 'connected' when synced with an active source, or 'disabled' if the source has been deleted. Defaults to 'disconnected'.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text header identifying the app card. Defaults to 'sample app card item'.")
class CreateAppCardItemRequestBodyStyle(StrictModel):
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The hex color code for the app card's border. Defaults to '#2d9bf0' (blue).")
class CreateAppCardItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the app card in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the app card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the app card in pixels.", json_schema_extra={'format': 'double'})
class CreateAppCardItemRequestBody(StrictModel):
    data: CreateAppCardItemRequestBodyData | None = None
    style: CreateAppCardItemRequestBodyStyle | None = None
    geometry: CreateAppCardItemRequestBodyGeometry | None = None
class CreateAppCardItemRequest(StrictModel):
    """Adds a new app card item to a board. App cards display custom content with optional preview fields and can be styled with colors, dimensions, and rotation."""
    path: CreateAppCardItemRequestPath
    body: CreateAppCardItemRequestBody | None = None

# Operation: get_app_card_item
class GetAppCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the app card item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the specific app card item to retrieve.")
class GetAppCardItemRequest(StrictModel):
    """Retrieves detailed information about a specific app card item on a board. Use this to fetch properties and content of an individual app card."""
    path: GetAppCardItemRequestPath

# Operation: update_app_card_item
class UpdateAppCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the app card item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the app card item to update.")
class UpdateAppCardItemRequestBodyData(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A short text description providing context about the app card's purpose or content.")
    fields: list[CustomField] | None = Field(default=None, validation_alias="fields", serialization_alias="fields", description="An array of custom preview field objects displayed in the compact view on the bottom half of the app card. Each field object defines a key-value pair shown to users.")
    status: Literal["disconnected", "connected", "disabled"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The connection status of the app card. Use 'connected' when synced with the source, 'disconnected' when not synced, or 'disabled' when the source has been deleted. Defaults to 'disconnected'.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text header identifying the app card. Defaults to 'sample app card item'.")
class UpdateAppCardItemRequestBodyStyle(StrictModel):
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The hex color value for the app card's border. Specify as a six-digit hex code (e.g., #2d9bf0).")
class UpdateAppCardItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the app card in pixels. Specify as a numeric value.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the app card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the app card in pixels. Specify as a numeric value.", json_schema_extra={'format': 'double'})
class UpdateAppCardItemRequestBody(StrictModel):
    data: UpdateAppCardItemRequestBodyData | None = None
    style: UpdateAppCardItemRequestBodyStyle | None = None
    geometry: UpdateAppCardItemRequestBodyGeometry | None = None
class UpdateAppCardItemRequest(StrictModel):
    """Update an app card item on a board by modifying its content, styling, and metadata. Changes are applied to the specified item and reflected immediately on the board."""
    path: UpdateAppCardItemRequestPath
    body: UpdateAppCardItemRequestBody | None = None

# Operation: delete_app_card_item
class DeleteAppCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the app card item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the app card item to delete from the board.")
class DeleteAppCardItemRequest(StrictModel):
    """Removes an app card item from a specified board. Requires boards:write scope and is subject to Level 3 rate limiting."""
    path: DeleteAppCardItemRequestPath

# Operation: create_card_item
class CreateCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the card will be created.")
class CreateCardItemRequestBodyData(StrictModel):
    assignee_id: str | None = Field(default=None, validation_alias="assigneeId", serialization_alias="assigneeId", description="The numeric user ID of the person assigned to own this card. User IDs are automatically assigned when users first sign up.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A short text description providing context or details about the card's content.")
    due_date: str | None = Field(default=None, validation_alias="dueDate", serialization_alias="dueDate", description="The completion deadline for the task or activity, specified in UTC using ISO 8601 format with a trailing Z offset (e.g., 2023-10-12T22:00:55.000Z).", json_schema_extra={'format': 'date-time'})
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text header or title for the card.")
class CreateCardItemRequestBodyStyle(StrictModel):
    card_theme: str | None = Field(default=None, validation_alias="cardTheme", serialization_alias="cardTheme", description="The hex color code for the card's border. Defaults to #2d9bf0 (blue) if not specified.")
class CreateCardItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the card in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the card in pixels.", json_schema_extra={'format': 'double'})
class CreateCardItemRequestBody(StrictModel):
    data: CreateCardItemRequestBodyData | None = None
    style: CreateCardItemRequestBodyStyle | None = None
    geometry: CreateCardItemRequestBodyGeometry | None = None
class CreateCardItemRequest(StrictModel):
    """Creates a new card item on a specified board. Cards can include a title, description, due date, assignee, and visual styling to organize tasks and activities."""
    path: CreateCardItemRequestPath
    body: CreateCardItemRequestBody | None = None

# Operation: get_card_item
class GetCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the card item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the card item you want to retrieve.")
class GetCardItemRequest(StrictModel):
    """Retrieves detailed information about a specific card item on a board. Use this to fetch card properties, content, and metadata."""
    path: GetCardItemRequestPath

# Operation: update_card_item
class UpdateCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the card item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the card item to update.")
class UpdateCardItemRequestBodyData(StrictModel):
    assignee_id: str | None = Field(default=None, validation_alias="assigneeId", serialization_alias="assigneeId", description="The numeric user ID of the person assigned to this card. This ID is automatically assigned when a user first signs up.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A short text description providing context or details about the card's content.")
    due_date: str | None = Field(default=None, validation_alias="dueDate", serialization_alias="dueDate", description="The date when the task or activity is due, formatted as an ISO 8601 UTC timestamp with a trailing Z offset (e.g., 2023-10-12T22:00:55.000Z).", json_schema_extra={'format': 'date-time'})
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text title or header for the card.")
class UpdateCardItemRequestBodyStyle(StrictModel):
    card_theme: str | None = Field(default=None, validation_alias="cardTheme", serialization_alias="cardTheme", description="The hex color code for the card's border, used to visually theme or categorize the card.")
class UpdateCardItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the card in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the card in pixels.", json_schema_extra={'format': 'double'})
class UpdateCardItemRequestBody(StrictModel):
    data: UpdateCardItemRequestBodyData | None = None
    style: UpdateCardItemRequestBodyStyle | None = None
    geometry: UpdateCardItemRequestBodyGeometry | None = None
class UpdateCardItemRequest(StrictModel):
    """Update a card item on a board with new content, styling, and metadata. Modify the card's title, description, due date, assignee, dimensions, rotation, and theme color."""
    path: UpdateCardItemRequestPath
    body: UpdateCardItemRequestBody | None = None

# Operation: delete_card_item
class DeleteCardItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the card item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the card item to delete from the board.")
class DeleteCardItemRequest(StrictModel):
    """Permanently removes a card item from a board. This action cannot be undone and requires write access to the board."""
    path: DeleteCardItemRequestPath

# Operation: list_connectors_for_board
class GetConnectorsRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board from which to retrieve connectors.")
class GetConnectorsRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of connectors to return per request, between 10 and 50. Defaults to 10. If more results exist, the response includes a cursor for fetching the next page.")
class GetConnectorsRequest(StrictModel):
    """Retrieves a list of connectors for a specific board using cursor-based pagination. Use the cursor from the response to fetch subsequent pages of results."""
    path: GetConnectorsRequestPath
    query: GetConnectorsRequestQuery | None = None

# Operation: create_connector
class CreateConnectorRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the connector will be created.")
class CreateConnectorRequestBodyStartItem(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the item where the connector starts. Frames are not supported.")
    snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(default=None, validation_alias="snapTo", serialization_alias="snapTo", description="The side of the start item where the connector attaches (top, right, bottom, or left). Use 'auto' to automatically select the optimal connection point. Defaults to 'auto' if neither this nor position is specified.")
class CreateConnectorRequestBodyEndItem(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the item where the connector ends. Frames are not supported.")
    snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(default=None, validation_alias="snapTo", serialization_alias="snapTo", description="The side of the end item where the connector attaches (top, right, bottom, or left). Use 'auto' to automatically select the optimal connection point. Defaults to 'auto' if neither this nor position is specified.")
class CreateConnectorRequestBodyStyle(StrictModel):
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The hex color code for the caption text. Defaults to '#1a1a1a' (dark gray).")
    end_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(default=None, validation_alias="endStrokeCap", serialization_alias="endStrokeCap", description="The decoration style at the end of the connector line, such as arrows, circles, or ERD symbols. Defaults to 'stealth'.")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="The font size for captions in density-independent pixels, ranging from 10 to 288. Defaults to 14.")
    start_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(default=None, validation_alias="startStrokeCap", serialization_alias="startStrokeCap", description="The decoration style at the start of the connector line, such as arrows, circles, or ERD symbols. Defaults to 'none'.")
    stroke_color: str | None = Field(default=None, validation_alias="strokeColor", serialization_alias="strokeColor", description="The hex color code for the connector line. Defaults to '#000000' (black).")
    stroke_style: Literal["normal", "dotted", "dashed"] | None = Field(default=None, validation_alias="strokeStyle", serialization_alias="strokeStyle", description="The stroke pattern of the connector line: 'normal' for solid, 'dotted' for dots, or 'dashed' for dashes. Defaults to 'normal'.")
    stroke_width: str | None = Field(default=None, validation_alias="strokeWidth", serialization_alias="strokeWidth", description="The thickness of the connector line in density-independent pixels, ranging from 1 to 24. Defaults to 1.0.")
    text_orientation: Literal["horizontal", "aligned"] | None = Field(default=None, validation_alias="textOrientation", serialization_alias="textOrientation", description="The orientation of captions relative to the connector line: 'horizontal' for fixed horizontal text or 'aligned' to follow the line's curvature. Defaults to 'aligned'.")
class CreateConnectorRequestBody(StrictModel):
    shape: Literal["straight", "elbowed", "curved"] | None = Field(default=None, description="The visual path type of the connector line: 'straight' for direct lines, 'elbowed' for right-angle turns, or 'curved' for smooth curves. Defaults to 'curved'.")
    captions: list[Caption] | None = Field(default=None, description="An array of text blocks to display on the connector, with a maximum of 20 captions.", max_length=20, min_length=0)
    start_item: CreateConnectorRequestBodyStartItem | None = Field(default=None, validation_alias="startItem", serialization_alias="startItem")
    end_item: CreateConnectorRequestBodyEndItem | None = Field(default=None, validation_alias="endItem", serialization_alias="endItem")
    style: CreateConnectorRequestBodyStyle | None = None
class CreateConnectorRequest(StrictModel):
    """Creates a connector between two items on a board, with customizable styling, line shape, and optional text captions. Connectors can be attached to specific sides of items or automatically positioned."""
    path: CreateConnectorRequestPath
    body: CreateConnectorRequestBody | None = None

# Operation: get_connector
class GetConnectorRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the connector you want to retrieve.")
    connector_id: str = Field(default=..., description="The unique identifier of the connector whose information you want to retrieve.")
class GetConnectorRequest(StrictModel):
    """Retrieves detailed information about a specific connector on a board, including its configuration and properties."""
    path: GetConnectorRequestPath

# Operation: update_connector
class UpdateConnectorRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the connector to update.")
    connector_id: str = Field(default=..., description="The unique identifier of the connector to update.")
class UpdateConnectorRequestBodyStartItem(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the item to attach the connector's start point to. Frames are not supported.")
    snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(default=None, validation_alias="snapTo", serialization_alias="snapTo", description="Which side of the start item to attach the connector: auto (automatic placement), top, right, bottom, or left. Cannot be combined with position-based attachment. Defaults to auto if not specified.")
class UpdateConnectorRequestBodyEndItem(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the item to attach the connector's end point to. Frames are not supported.")
    snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(default=None, validation_alias="snapTo", serialization_alias="snapTo", description="Which side of the end item to attach the connector: auto (automatic placement), top, right, bottom, or left. Cannot be combined with position-based attachment. Defaults to auto if not specified.")
class UpdateConnectorRequestBodyStyle(StrictModel):
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for caption text (e.g., #9510ac).")
    end_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(default=None, validation_alias="endStrokeCap", serialization_alias="endStrokeCap", description="The decorative end cap style for the connector's endpoint: none, stealth, rounded_stealth, diamond, filled_diamond, oval, filled_oval, arrow, triangle, filled_triangle, or ERD notation styles (erd_one, erd_many, erd_only_one, erd_zero_or_one, erd_one_or_many, erd_zero_or_many, unknown).")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size for captions in density-independent pixels, between 10 and 288.")
    start_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(default=None, validation_alias="startStrokeCap", serialization_alias="startStrokeCap", description="The decorative start cap style for the connector's starting point: none, stealth, rounded_stealth, diamond, filled_diamond, oval, filled_oval, arrow, triangle, filled_triangle, or ERD notation styles (erd_one, erd_many, erd_only_one, erd_zero_or_one, erd_one_or_many, erd_zero_or_many, unknown).")
    stroke_color: str | None = Field(default=None, validation_alias="strokeColor", serialization_alias="strokeColor", description="Hex color code for the connector line (e.g., #2d9bf0).")
    stroke_style: Literal["normal", "dotted", "dashed"] | None = Field(default=None, validation_alias="strokeStyle", serialization_alias="strokeStyle", description="The line pattern style: normal (solid), dotted, or dashed.")
    stroke_width: str | None = Field(default=None, validation_alias="strokeWidth", serialization_alias="strokeWidth", description="Line thickness in density-independent pixels, between 1 and 24.")
    text_orientation: Literal["horizontal", "aligned"] | None = Field(default=None, validation_alias="textOrientation", serialization_alias="textOrientation", description="Caption orientation relative to the connector line: horizontal (fixed orientation) or aligned (follows line curvature).")
class UpdateConnectorRequestBody(StrictModel):
    shape: Literal["straight", "elbowed", "curved"] | None = Field(default=None, description="The connector line path type: straight (direct line), elbowed (right angles), or curved (smooth bends). Defaults to curved.")
    captions: list[Caption] | None = Field(default=None, description="Text labels to display on the connector. Supports up to 20 caption blocks.", max_length=20, min_length=0)
    start_item: UpdateConnectorRequestBodyStartItem | None = Field(default=None, validation_alias="startItem", serialization_alias="startItem")
    end_item: UpdateConnectorRequestBodyEndItem | None = Field(default=None, validation_alias="endItem", serialization_alias="endItem")
    style: UpdateConnectorRequestBodyStyle | None = None
class UpdateConnectorRequest(StrictModel):
    """Modify a connector's visual styling, path shape, and attachment points on a board. Update properties like line color, stroke style, captions, and connection endpoints to customize how the connector appears and connects items."""
    path: UpdateConnectorRequestPath
    body: UpdateConnectorRequestBody | None = None

# Operation: delete_connector
class DeleteConnectorRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the connector to delete.")
    connector_id: str = Field(default=..., description="The unique identifier of the connector to delete from the board.")
class DeleteConnectorRequest(StrictModel):
    """Removes a connector from a board. The connector is permanently deleted and cannot be recovered."""
    path: DeleteConnectorRequestPath

# Operation: add_document_to_board
class CreateDocumentItemUsingUrlRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the document item will be created.")
class CreateDocumentItemUsingUrlRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text label to identify the document on the board. If not provided, the document will be added without a custom title.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The complete URL where the document is hosted and publicly accessible. Supports standard document formats like PDF.")
class CreateDocumentItemUsingUrlRequestBody(StrictModel):
    data: CreateDocumentItemUsingUrlRequestBodyData
class CreateDocumentItemUsingUrlRequest(StrictModel):
    """Adds a document item to a board by hosting it at a specified URL. The document will be displayed on the board with an optional title for identification."""
    path: CreateDocumentItemUsingUrlRequestPath
    body: CreateDocumentItemUsingUrlRequestBody

# Operation: get_document_item
class GetDocumentItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the document item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the specific document item to retrieve.")
class GetDocumentItemRequest(StrictModel):
    """Retrieves detailed information about a specific document item on a board. Use this to fetch properties and metadata for a document you've identified by its ID."""
    path: GetDocumentItemRequestPath

# Operation: update_document_item
class UpdateDocumentItemUsingUrlRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the document item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the document item to update.")
class UpdateDocumentItemUsingUrlRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text header to identify the document.")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="The URL where the document is hosted (e.g., a link to a PDF or other document file).")
class UpdateDocumentItemUsingUrlRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the item in pixels, specified as a decimal number.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the item in pixels, specified as a decimal number.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the item in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
class UpdateDocumentItemUsingUrlRequestBody(StrictModel):
    data: UpdateDocumentItemUsingUrlRequestBodyData | None = None
    geometry: UpdateDocumentItemUsingUrlRequestBodyGeometry | None = None
class UpdateDocumentItemUsingUrlRequest(StrictModel):
    """Update a document item on a board by modifying its properties such as title, URL, dimensions, and rotation angle."""
    path: UpdateDocumentItemUsingUrlRequestPath
    body: UpdateDocumentItemUsingUrlRequestBody | None = None

# Operation: delete_document_item
class DeleteDocumentItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the document item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the document item to delete from the board.")
class DeleteDocumentItemRequest(StrictModel):
    """Permanently removes a document item from a board. This action cannot be undone and requires write access to the board."""
    path: DeleteDocumentItemRequestPath

# Operation: add_embed_item_to_board
class CreateEmbedItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the embed item will be created.")
class CreateEmbedItemRequestBodyData(StrictModel):
    mode: Literal["inline", "modal"] | None = Field(default=None, validation_alias="mode", serialization_alias="mode", description="Controls how the embedded content appears: 'inline' displays it directly on the board, while 'modal' shows it in an overlay. Defaults to inline if not specified.")
    preview_url: str | None = Field(default=None, validation_alias="previewUrl", serialization_alias="previewUrl", description="URL of an image to display as the preview thumbnail for the embed item on the board.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="A valid URL (HTTP or HTTPS) pointing to the external content resource to embed. This is the actual content that will be displayed.")
class CreateEmbedItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The vertical size of the embed item in pixels. If not specified, a default height will be applied.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The horizontal size of the embed item in pixels. If not specified, a default width will be applied.", json_schema_extra={'format': 'double'})
class CreateEmbedItemRequestBody(StrictModel):
    data: CreateEmbedItemRequestBodyData
    geometry: CreateEmbedItemRequestBodyGeometry | None = None
class CreateEmbedItemRequest(StrictModel):
    """Embeds external content on a board by creating an embed item. The content can be displayed inline on the board or in a modal overlay, with optional custom preview image and dimensions."""
    path: CreateEmbedItemRequestPath
    body: CreateEmbedItemRequestBody

# Operation: get_embed_item
class GetEmbedItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the embed item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the specific embed item to retrieve.")
class GetEmbedItemRequest(StrictModel):
    """Retrieves detailed information about a specific embed item on a board. Use this to fetch properties and metadata for an embedded content item."""
    path: GetEmbedItemRequestPath

# Operation: update_embed_item
class UpdateEmbedItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the embed item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the embed item to update.")
class UpdateEmbedItemRequestBodyData(StrictModel):
    mode: Literal["inline", "modal"] | None = Field(default=None, validation_alias="mode", serialization_alias="mode", description="Controls how the embedded content displays on the board: 'inline' shows content directly on the board, while 'modal' displays it in an overlay.")
    preview_url: str | None = Field(default=None, validation_alias="previewUrl", serialization_alias="previewUrl", description="URL of an image to use as the preview thumbnail for the embedded item.")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="A valid URL (HTTP or HTTPS) pointing to the content resource to embed on the board, such as a video or web page.")
class UpdateEmbedItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the embed item in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the embed item in pixels.", json_schema_extra={'format': 'double'})
class UpdateEmbedItemRequestBody(StrictModel):
    data: UpdateEmbedItemRequestBodyData | None = None
    geometry: UpdateEmbedItemRequestBodyGeometry | None = None
class UpdateEmbedItemRequest(StrictModel):
    """Updates an embed item on a board, allowing you to modify its display mode, preview image, source URL, and dimensions. Requires boards:write scope."""
    path: UpdateEmbedItemRequestPath
    body: UpdateEmbedItemRequestBody | None = None

# Operation: delete_embed_item
class DeleteEmbedItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the embed item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the embed item to delete from the board.")
class DeleteEmbedItemRequest(StrictModel):
    """Removes an embed item from a board. The embed item is permanently deleted and cannot be recovered."""
    path: DeleteEmbedItemRequestPath

# Operation: add_image_to_board
class CreateImageItemUsingUrlRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the image will be added.")
class CreateImageItemUsingUrlRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text label to identify the image on the board.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The URL of the image to add. Must be a valid, publicly accessible image URL.")
class CreateImageItemUsingUrlRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the image in pixels. If not specified, the image's original height is used.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the image in pixels. If not specified, the image's original width is used.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle in degrees. Use positive values to rotate clockwise and negative values to rotate counterclockwise.", json_schema_extra={'format': 'double'})
class CreateImageItemUsingUrlRequestBody(StrictModel):
    data: CreateImageItemUsingUrlRequestBodyData
    geometry: CreateImageItemUsingUrlRequestBodyGeometry | None = None
class CreateImageItemUsingUrlRequest(StrictModel):
    """Adds an image item to a board by URL. Optionally customize the image with a title, dimensions, and rotation angle."""
    path: CreateImageItemUsingUrlRequestPath
    body: CreateImageItemUsingUrlRequestBody

# Operation: get_image_item
class GetImageItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the image item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the image item you want to retrieve.")
class GetImageItemRequest(StrictModel):
    """Retrieves detailed information about a specific image item on a board, including its properties and metadata."""
    path: GetImageItemRequestPath

# Operation: update_image_item
class UpdateImageItemUsingUrlRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the image item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the image item to update.")
class UpdateImageItemUsingUrlRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short text header to identify the image on the board.")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="The URL pointing to the image resource to display.")
class UpdateImageItemUsingUrlRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the image item in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the image item in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the image in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
class UpdateImageItemUsingUrlRequestBody(StrictModel):
    data: UpdateImageItemUsingUrlRequestBodyData | None = None
    geometry: UpdateImageItemUsingUrlRequestBodyGeometry | None = None
class UpdateImageItemUsingUrlRequest(StrictModel):
    """Update an image item on a board by modifying its URL, title, dimensions, or rotation angle. Requires boards:write scope."""
    path: UpdateImageItemUsingUrlRequestPath
    body: UpdateImageItemUsingUrlRequestBody | None = None

# Operation: delete_image_item
class DeleteImageItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the image item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the image item to delete from the board.")
class DeleteImageItemRequest(StrictModel):
    """Permanently removes an image item from a board. Requires boards:write scope and is subject to Level 3 rate limiting."""
    path: DeleteImageItemRequestPath

# Operation: list_board_items
class GetItemsRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board from which to retrieve items.")
class GetItemsRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of items to return per request, between 10 and 50. Defaults to 10. If more items exist, use the cursor from the response to fetch the next batch.")
    type_: Literal["text", "shape", "sticky_note", "image", "document", "card", "app_card", "preview", "frame", "embed", "doc_format", "data_table_format"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results to a specific item type (e.g., cards, sticky notes, shapes). Omit to retrieve all item types on the board.")
class GetItemsRequest(StrictModel):
    """Retrieves a paginated list of items on a board, with optional filtering by item type. Use cursor-based pagination to navigate through results."""
    path: GetItemsRequestPath
    query: GetItemsRequestQuery | None = None

# Operation: get_item
class GetSpecificItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the item you want to retrieve from the board.")
class GetSpecificItemRequest(StrictModel):
    """Retrieve detailed information about a specific item on a board. This operation requires read access to the board and is rate-limited at Level 1."""
    path: GetSpecificItemRequestPath

# Operation: update_item_position_or_parent
class UpdateItemPositionOrParentRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the item whose position or parent you want to change.")
class UpdateItemPositionOrParentRequestBodyPosition(StrictModel):
    x: float | None = Field(default=None, validation_alias="x", serialization_alias="x", description="X-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: `0`.\nThe center point of the board has `x: 0` and `y: 0` coordinates.", json_schema_extra={'format': 'double'})
    y: float | None = Field(default=None, validation_alias="y", serialization_alias="y", description="Y-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: `0`.\nThe center point of the board has `x: 0` and `y: 0` coordinates.", json_schema_extra={'format': 'double'})
class UpdateItemPositionOrParentRequestBodyParent(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the parent frame for the item.", json_schema_extra={'format': 'int64'})
class UpdateItemPositionOrParentRequestBody(StrictModel):
    position: UpdateItemPositionOrParentRequestBodyPosition | None = None
    parent: UpdateItemPositionOrParentRequestBodyParent | None = None
class UpdateItemPositionOrParentRequest(StrictModel):
    """Reposition an item on a board or move it to a different parent container. Use this operation to reorganize board layout or change item hierarchy."""
    path: UpdateItemPositionOrParentRequestPath
    body: UpdateItemPositionOrParentRequestBody | None = None

# Operation: delete_item
class DeleteItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the item to delete from the board.")
class DeleteItemRequest(StrictModel):
    """Permanently removes an item from a board. This action cannot be undone and requires boards:write scope."""
    path: DeleteItemRequestPath

# Operation: list_board_members
class GetBoardMembersRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board whose members you want to retrieve.")
class GetBoardMembersRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of board members to return per request, between 1 and 50. Defaults to 20 if not specified.")
    offset: str | None = Field(default=None, description="The zero-based starting position for retrieving results, used for pagination. Defaults to 0 to start from the first member.")
class GetBoardMembersRequest(StrictModel):
    """Retrieves a pageable list of all members assigned to a specific board. Use pagination parameters to control the number of results and navigate through large member lists."""
    path: GetBoardMembersRequestPath
    query: GetBoardMembersRequestQuery | None = None

# Operation: invite_members_to_board
class ShareBoardRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where members will be invited.")
class ShareBoardRequestBody(StrictModel):
    emails: list[str] = Field(default=..., description="Email addresses of users to invite to the board. You can invite between 1 and 20 members per request.", min_length=1, max_length=20)
    role: Literal["viewer", "commenter", "editor", "coowner", "owner"] | None = Field(default=None, description="The role assigned to invited members. Defaults to 'commenter' if not specified. Valid roles are: viewer, commenter, editor, coowner, or owner (owner and coowner have equivalent effects).")
    message: str | None = Field(default=None, description="Optional custom message to include in the invitation email sent to members.")
class ShareBoardRequest(StrictModel):
    """Invite new members to collaborate on a board by sending invitation emails. Membership requirements depend on the board's sharing policy."""
    path: ShareBoardRequestPath
    body: ShareBoardRequestBody

# Operation: get_board_member
class GetSpecificBoardMemberRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the member you want to retrieve.")
    board_member_id: str = Field(default=..., description="The unique identifier of the board member whose information you want to retrieve.")
class GetSpecificBoardMemberRequest(StrictModel):
    """Retrieves detailed information about a specific member of a board, including their role and permissions."""
    path: GetSpecificBoardMemberRequestPath

# Operation: update_board_member_role
class UpdateBoardMemberRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the member whose role you want to update.")
    board_member_id: str = Field(default=..., description="The unique identifier of the board member whose role you want to change.")
class UpdateBoardMemberRequestBody(StrictModel):
    role: Literal["viewer", "commenter", "editor", "coowner", "owner"] | None = Field(default=None, description="The new role to assign to the board member. Valid roles are viewer (read-only access), commenter (can view and comment), editor (can view, comment, and edit), coowner (full access with administrative capabilities), or owner (full ownership). Defaults to commenter if not specified.")
class UpdateBoardMemberRequest(StrictModel):
    """Update the role assigned to a board member, controlling their access level and permissions on the board."""
    path: UpdateBoardMemberRequestPath
    body: UpdateBoardMemberRequestBody | None = None

# Operation: remove_board_member
class RemoveBoardMemberRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board from which you want to remove the member.")
    board_member_id: str = Field(default=..., description="The unique identifier of the board member you want to remove from the board.")
class RemoveBoardMemberRequest(StrictModel):
    """Remove a member from a board. This operation deletes the specified board member's access and role from the board."""
    path: RemoveBoardMemberRequestPath

# Operation: add_shape_to_board
class CreateShapeItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the shape will be created.")
class CreateShapeItemRequestBodyData(StrictModel):
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="Optional text content to display on the shape. Not supported for flow_chart_or and flow_chart_summing_junction shapes.")
    shape: str | None = Field(default=None, validation_alias="shape", serialization_alias="shape", description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart shapes (decision, process, terminator, etc.), or arrow/callout variants. Defaults to rectangle.")
class CreateShapeItemRequestBodyStyle(StrictModel):
    border_color: str | None = Field(default=None, validation_alias="borderColor", serialization_alias="borderColor", description="Hex color code for the shape border. Defaults to dark gray (#1a1a1a).")
    border_opacity: str | None = Field(default=None, validation_alias="borderOpacity", serialization_alias="borderOpacity", description="Opacity of the border as a decimal between 0 (fully transparent) and 1 (fully opaque). Defaults to 1.0.")
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(default=None, validation_alias="borderStyle", serialization_alias="borderStyle", description="Visual style of the border: normal (solid), dotted, or dashed. Defaults to normal.")
    border_width: str | None = Field(default=None, validation_alias="borderWidth", serialization_alias="borderWidth", description="Border thickness in display pixels, ranging from 1 to 24. Defaults to 2.0.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for the text content. Defaults to dark gray (#1a1a1a).")
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="Hex color code for the shape fill. Accepts predefined palette colors or custom hex values. Defaults to white (#ffffff).")
    fill_opacity: str | None = Field(default=None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="Opacity of the fill color as a decimal between 0 (fully transparent) and 1 (fully opaque). Defaults to 1.0 for flowchart shapes, or 1.0 if fillColor is specified for basic shapes, otherwise 0.0.")
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Font family for text rendering. Choose from standard fonts (Arial, Georgia, Times New Roman) or decorative options (Bangers, Permanent Marker, etc.). Defaults to Arial.")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size for text in display pixels, ranging from 10 to 288. Defaults to 14.")
    text_align: Literal["left", "right", "center", "unknown"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="Horizontal text alignment: left, right, or center. Defaults to center for flowchart shapes, left for basic shapes.")
    text_align_vertical: Literal["top", "middle", "bottom", "unknown"] | None = Field(default=None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="Vertical text alignment: top, middle, or bottom. Defaults to middle for flowchart shapes, top for basic shapes.")
class CreateShapeItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Height of the shape in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Rotation angle in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Width of the shape in pixels.", json_schema_extra={'format': 'double'})
class CreateShapeItemRequestBody(StrictModel):
    data: CreateShapeItemRequestBodyData | None = None
    style: CreateShapeItemRequestBodyStyle | None = None
    geometry: CreateShapeItemRequestBodyGeometry | None = None
class CreateShapeItemRequest(StrictModel):
    """Adds a shape item to a board with customizable geometry, styling, and text formatting. Requires boards:write scope."""
    path: CreateShapeItemRequestPath
    body: CreateShapeItemRequestBody | None = None

# Operation: get_shape_item
class GetShapeItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the shape item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the shape item you want to retrieve.")
class GetShapeItemRequest(StrictModel):
    """Retrieves detailed information about a specific shape item on a board, including its properties and metadata."""
    path: GetShapeItemRequestPath

# Operation: update_shape_item
class UpdateShapeItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the shape item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the shape item to update.")
class UpdateShapeItemRequestBodyData(StrictModel):
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="The text content to display on the shape. Note: Changing the shape type to flow_chart_or or flow_chart_summing_junction will clear any existing content.")
    shape: str | None = Field(default=None, validation_alias="shape", serialization_alias="shape", description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart shapes (flow_chart_process, flow_chart_decision, etc.), or specialized shapes (cloud, star, arrows). Defaults to rectangle.")
class UpdateShapeItemRequestBodyStyle(StrictModel):
    border_color: str | None = Field(default=None, validation_alias="borderColor", serialization_alias="borderColor", description="The hex color code for the shape's border outline.")
    border_opacity: str | None = Field(default=None, validation_alias="borderOpacity", serialization_alias="borderOpacity", description="The transparency level of the border, from 0.0 (fully transparent) to 1.0 (fully opaque).")
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(default=None, validation_alias="borderStyle", serialization_alias="borderStyle", description="The visual style of the border: solid (normal), dotted, or dashed.")
    border_width: str | None = Field(default=None, validation_alias="borderWidth", serialization_alias="borderWidth", description="The thickness of the border in display pixels, ranging from 1 to 24.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The hex color code for the text displayed within the shape.")
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The hex color code for the shape's fill background. Supports predefined palette colors or custom hex values.")
    fill_opacity: str | None = Field(default=None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="The transparency level of the fill color, from 0.0 (fully transparent) to 1.0 (fully opaque).")
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="The typeface for text rendering. Choose from a curated set including sans-serif (Arial, Open Sans, Roboto), serif (Georgia, Times New Roman), and decorative fonts.")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="The size of the text in display pixels, ranging from 10 to 288.")
    text_align: Literal["left", "right", "center"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="The horizontal alignment of text within the shape: left, right, or center.")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(default=None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="The vertical alignment of text within the shape: top, middle, or bottom.")
class UpdateShapeItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the shape in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the shape in pixels.", json_schema_extra={'format': 'double'})
class UpdateShapeItemRequestBody(StrictModel):
    data: UpdateShapeItemRequestBodyData | None = None
    style: UpdateShapeItemRequestBodyStyle | None = None
    geometry: UpdateShapeItemRequestBodyGeometry | None = None
class UpdateShapeItemRequest(StrictModel):
    """Modify a shape item's geometry, styling, and text content on a board. Updates only the properties you specify; omitted properties remain unchanged."""
    path: UpdateShapeItemRequestPath
    body: UpdateShapeItemRequestBody | None = None

# Operation: delete_shape_item
class DeleteShapeItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the shape item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the shape item to delete from the board.")
class DeleteShapeItemRequest(StrictModel):
    """Permanently removes a shape item from a board. This action cannot be undone and requires write access to the board."""
    path: DeleteShapeItemRequestPath

# Operation: add_sticky_note
class CreateStickyNoteItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the sticky note will be created.")
class CreateStickyNoteItemRequestBodyData(StrictModel):
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="The text content displayed in the sticky note (e.g., 'Hello').")
    shape: Literal["square", "rectangle"] | None = Field(default=None, validation_alias="shape", serialization_alias="shape", description="The geometric shape of the sticky note: either square or rectangle. Defaults to square.")
class CreateStickyNoteItemRequestBodyStyle(StrictModel):
    fill_color: Literal["gray", "light_yellow", "yellow", "orange", "light_green", "green", "dark_green", "cyan", "light_pink", "pink", "violet", "red", "light_blue", "blue", "dark_blue", "black"] | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The fill color of the sticky note. Choose from: gray, light_yellow, yellow, orange, light_green, green, dark_green, cyan, light_pink, pink, violet, red, light_blue, blue, dark_blue, or black. Defaults to light_yellow.")
    text_align: Literal["left", "right", "center"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="Horizontal text alignment within the sticky note: left, right, or center. Defaults to center.")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(default=None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="Vertical text alignment within the sticky note: top, middle, or bottom. Defaults to top.")
class CreateStickyNoteItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the sticky note in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the sticky note in pixels.", json_schema_extra={'format': 'double'})
class CreateStickyNoteItemRequestBody(StrictModel):
    data: CreateStickyNoteItemRequestBodyData | None = None
    style: CreateStickyNoteItemRequestBodyStyle | None = None
    geometry: CreateStickyNoteItemRequestBodyGeometry | None = None
class CreateStickyNoteItemRequest(StrictModel):
    """Adds a sticky note item to a board with customizable text content, shape, colors, and alignment. Requires boards:write scope."""
    path: CreateStickyNoteItemRequestPath
    body: CreateStickyNoteItemRequestBody | None = None

# Operation: get_sticky_note_item
class GetStickyNoteItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the sticky note item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the sticky note item you want to retrieve.")
class GetStickyNoteItemRequest(StrictModel):
    """Retrieves detailed information about a specific sticky note item on a board. Use this to fetch the content, styling, and metadata of an individual sticky note."""
    path: GetStickyNoteItemRequestPath

# Operation: update_sticky_note
class UpdateStickyNoteItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the sticky note to update.")
    item_id: str = Field(default=..., description="The unique identifier of the sticky note item to update.")
class UpdateStickyNoteItemRequestBodyData(StrictModel):
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="The text content to display in the sticky note.")
    shape: Literal["square", "rectangle"] | None = Field(default=None, validation_alias="shape", serialization_alias="shape", description="The geometric shape of the sticky note: square (default) or rectangle, which affects the aspect ratio of the item's dimensions.")
class UpdateStickyNoteItemRequestBodyStyle(StrictModel):
    fill_color: Literal["gray", "light_yellow", "yellow", "orange", "light_green", "green", "dark_green", "cyan", "light_pink", "pink", "violet", "red", "light_blue", "blue", "dark_blue", "black"] | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The background color of the sticky note. Choose from 15 preset colors including gray, yellows, greens, blues, pinks, and more.")
    text_align: Literal["left", "right", "center"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="The horizontal alignment of text within the sticky note: left, center, or right.")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(default=None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="The vertical alignment of text within the sticky note: top, middle, or bottom.")
class UpdateStickyNoteItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the sticky note in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the sticky note in pixels.", json_schema_extra={'format': 'double'})
class UpdateStickyNoteItemRequestBody(StrictModel):
    data: UpdateStickyNoteItemRequestBodyData | None = None
    style: UpdateStickyNoteItemRequestBodyStyle | None = None
    geometry: UpdateStickyNoteItemRequestBodyGeometry | None = None
class UpdateStickyNoteItemRequest(StrictModel):
    """Modify the content, appearance, and layout of a sticky note item on a board. Update text, colors, alignment, shape, and dimensions as needed."""
    path: UpdateStickyNoteItemRequestPath
    body: UpdateStickyNoteItemRequestBody | None = None

# Operation: delete_sticky_note_item
class DeleteStickyNoteItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the sticky note to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the sticky note item to delete.")
class DeleteStickyNoteItemRequest(StrictModel):
    """Permanently removes a sticky note item from a board. This action cannot be undone."""
    path: DeleteStickyNoteItemRequestPath

# Operation: add_text_to_board
class CreateTextItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the text item will be created.")
class CreateTextItemRequestBodyData(StrictModel):
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The text content to display in the item.")
class CreateTextItemRequestBodyStyle(StrictModel):
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for the text itself. Defaults to black (#1a1a1a).")
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="Hex color code for the background fill of the text item. Defaults to white (#ffffff).")
    fill_opacity: str | None = Field(default=None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="Opacity of the background color, ranging from 0.0 (fully transparent) to 1.0 (fully opaque). Defaults to 1.0 if a fill color is specified, otherwise 0.0.")
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Font family for the text. Choose from a curated set of web-safe and decorative fonts. Defaults to Arial.")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size in display pixels. Must be at least 1 pixel. Defaults to 14 pixels.")
    text_align: Literal["left", "right", "center"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="Horizontal text alignment within the item: left, right, or center. Defaults to center.")
class CreateTextItemRequestBodyGeometry(StrictModel):
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Rotation angle in degrees. Positive values rotate clockwise, negative values rotate counterclockwise.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Width of the item in pixels. Must be at least 1.7 times the font size (e.g., minimum 24 pixels for 14pt font).", json_schema_extra={'format': 'double'})
class CreateTextItemRequestBody(StrictModel):
    data: CreateTextItemRequestBodyData
    style: CreateTextItemRequestBodyStyle | None = None
    geometry: CreateTextItemRequestBodyGeometry | None = None
class CreateTextItemRequest(StrictModel):
    """Adds a text item to a board with customizable styling, positioning, and formatting options. Requires boards:write scope."""
    path: CreateTextItemRequestPath
    body: CreateTextItemRequestBody

# Operation: get_text_item
class GetTextItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the text item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the text item you want to retrieve.")
class GetTextItemRequest(StrictModel):
    """Retrieves a specific text item from a board by its ID. Returns the text item's properties and content."""
    path: GetTextItemRequestPath

# Operation: update_text_item
class UpdateTextItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the text item to update.")
    item_id: str = Field(default=..., description="The unique identifier of the text item to update.")
class UpdateTextItemRequestBodyData(StrictModel):
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The text content to display in the item (e.g., 'Hello').")
class UpdateTextItemRequestBodyStyle(StrictModel):
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for the text itself (e.g., '#1a1a1a' for dark text).")
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="Hex color code for the background fill of the text item (e.g., '#e6e6e6' for light gray).")
    fill_opacity: str | None = Field(default=None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="Transparency level of the background color, ranging from 0.0 (completely transparent) to 1.0 (completely opaque).")
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Font family for the text. Choose from: arial, abril_fatface, bangers, eb_garamond, georgia, graduate, gravitas_one, fredoka_one, nixie_one, open_sans, permanent_marker, pt_sans, pt_sans_narrow, pt_serif, rammetto_one, roboto, roboto_condensed, roboto_slab, caveat, times_new_roman, titan_one, lemon_tuesday, roboto_mono, noto_sans, plex_sans, plex_serif, plex_mono, spoof, tiempos_text, or formular.")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size in display pixels. Must be at least 1 pixel.")
    text_align: Literal["left", "right", "center"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="Horizontal alignment of the text content: left, right, or center.")
class UpdateTextItemRequestBodyGeometry(StrictModel):
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Width of the item in pixels. Minimum width is 1.7 times the font size (e.g., font size 14 requires minimum width of 24).", json_schema_extra={'format': 'double'})
class UpdateTextItemRequestBody(StrictModel):
    data: UpdateTextItemRequestBodyData
    style: UpdateTextItemRequestBodyStyle | None = None
    geometry: UpdateTextItemRequestBodyGeometry | None = None
class UpdateTextItemRequest(StrictModel):
    """Modify the content, styling, and layout of a text item on a board. Update text content, colors, fonts, alignment, rotation, and dimensions as needed."""
    path: UpdateTextItemRequestPath
    body: UpdateTextItemRequestBody

# Operation: delete_text_item
class DeleteTextItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the text item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the text item to delete from the board.")
class DeleteTextItemRequest(StrictModel):
    """Permanently removes a text item from a board. Requires boards:write scope and is subject to Level 3 rate limiting."""
    path: DeleteTextItemRequestPath

# Operation: create_items_bulk
class CreateItemsRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where items will be created.")
class CreateItemsRequestBody(StrictModel):
    body: list[ItemCreate] = Field(default=..., description="Array of item objects to create. Must contain between 1 and 20 items. Items can be of different types (cards, shapes, sticky notes, etc.) and are processed together as a single transaction.", min_length=1, max_length=20)
class CreateItemsRequest(StrictModel):
    """Create multiple items of different types on a board in a single transactional operation. Supports up to 20 items per call (cards, shapes, sticky notes, etc.), and all items are created together or none are created if any item fails."""
    path: CreateItemsRequestPath
    body: CreateItemsRequestBody

# Operation: add_frame_to_board
class CreateFrameItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the frame will be created.")
class CreateFrameItemRequestBodyData(StrictModel):
    format_: Literal["custom"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The frame format type. Currently, only custom frames are supported.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The title displayed at the top of the frame.")
    type_: Literal["freeform"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The frame layout type. Currently, only freeform frames are supported, allowing flexible content arrangement.")
    show_content: bool | None = Field(default=None, validation_alias="showContent", serialization_alias="showContent", description="Whether to show or hide the content inside the frame. This feature is available only on Enterprise plans.")
class CreateFrameItemRequestBodyStyle(StrictModel):
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The background fill color for the frame, specified as a hexadecimal color code. Supports a predefined palette of colors or transparent (default).")
class CreateFrameItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the frame in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the frame in pixels.", json_schema_extra={'format': 'double'})
class CreateFrameItemRequestBody(StrictModel):
    data: CreateFrameItemRequestBodyData | None = None
    style: CreateFrameItemRequestBodyStyle | None = None
    geometry: CreateFrameItemRequestBodyGeometry | None = None
class CreateFrameItemRequest(StrictModel):
    """Adds a new frame to a board. Frames serve as containers for organizing and grouping content on a board, with customizable appearance and dimensions."""
    path: CreateFrameItemRequestPath
    body: CreateFrameItemRequestBody | None = None

# Operation: get_frame
class GetFrameItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the frame you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the frame you want to retrieve.")
class GetFrameItemRequest(StrictModel):
    """Retrieves detailed information about a specific frame on a board, including its properties and content."""
    path: GetFrameItemRequestPath

# Operation: update_frame
class UpdateFrameItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the frame to update.")
    item_id: str = Field(default=..., description="The unique identifier of the frame to update.")
class UpdateFrameItemRequestBodyData(StrictModel):
    format_: Literal["custom"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The frame format type. Currently, only custom frames are supported.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The title displayed at the top of the frame.")
    type_: Literal["freeform"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The frame layout type. Currently, only freeform frames are supported.")
    show_content: bool | None = Field(default=None, validation_alias="showContent", serialization_alias="showContent", description="Whether to show or hide the content inside the frame. This feature is available on Enterprise plans only.")
class UpdateFrameItemRequestBodyStyle(StrictModel):
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The fill color for the frame, specified as a hexadecimal color code. Supported colors include neutral grays, greens, teals, blues, purples, yellows, oranges, reds, and pinks.")
class UpdateFrameItemRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the frame in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the frame in pixels.", json_schema_extra={'format': 'double'})
class UpdateFrameItemRequestBody(StrictModel):
    data: UpdateFrameItemRequestBodyData | None = None
    style: UpdateFrameItemRequestBodyStyle | None = None
    geometry: UpdateFrameItemRequestBodyGeometry | None = None
class UpdateFrameItemRequest(StrictModel):
    """Update a frame's properties on a board, including its title, appearance, dimensions, and content visibility. Requires boards:write scope."""
    path: UpdateFrameItemRequestPath
    body: UpdateFrameItemRequestBody | None = None

# Operation: delete_frame
class DeleteFrameItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the frame to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the frame to delete from the board.")
class DeleteFrameItemRequest(StrictModel):
    """Permanently removes a frame from a board. The frame and all its contents will be deleted and cannot be recovered."""
    path: DeleteFrameItemRequestPath

# Operation: list_items_in_frame
class GetItemsWithinFrameRequestPath(StrictModel):
    board_id_platform_containers: str = Field(default=..., validation_alias="board_id_PlatformContainers", serialization_alias="board_id_PlatformContainers", description="The unique identifier of the board containing the frame.")
class GetItemsWithinFrameRequestQuery(StrictModel):
    parent_item_id: str = Field(default=..., description="The unique identifier of the frame (parent item) whose child items you want to retrieve.")
    limit: str | None = Field(default=None, description="Maximum number of items to return per request, between 10 and 50. If the total exceeds this limit, use the cursor from the response to fetch the next batch.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results to a specific item type (e.g., cards, shapes, sticky notes, images, text, embeds, documents, frames, or app cards). Omit to retrieve all item types.")
class GetItemsWithinFrameRequest(StrictModel):
    """Retrieves all child items contained within a specific frame on a board. Results are returned using cursor-based pagination to handle large collections efficiently."""
    path: GetItemsWithinFrameRequestPath
    query: GetItemsWithinFrameRequestQuery

# Operation: get_app_metrics
class GetMetricsRequestPath(StrictModel):
    app_id: str = Field(default=..., description="The unique identifier of the app for which to retrieve metrics.")
class GetMetricsRequestQuery(StrictModel):
    start_date: str = Field(default=..., validation_alias="startDate", serialization_alias="startDate", description="The start date for the metrics period in UTC format (YYYY-MM-DD). Metrics will be retrieved from this date onwards.", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., validation_alias="endDate", serialization_alias="endDate", description="The end date for the metrics period in UTC format (YYYY-MM-DD). Metrics will be retrieved up to and including this date.", json_schema_extra={'format': 'date'})
    period: Literal["DAY", "WEEK", "MONTH"] | None = Field(default=None, description="The time period to group metrics by. Accepts 'DAY', 'WEEK', or 'MONTH'. Defaults to 'WEEK' if not specified.")
class GetMetricsRequest(StrictModel):
    """Retrieve usage metrics for a specific app over a specified time range, with data grouped by the requested time period (day, week, or month). Requires an app management API token generated from the Developer Hub."""
    path: GetMetricsRequestPath
    query: GetMetricsRequestQuery

# Operation: get_app_metrics_total
class GetMetricsTotalRequestPath(StrictModel):
    app_id: str = Field(default=..., description="The unique identifier of the app for which to retrieve total metrics.")
class GetMetricsTotalRequest(StrictModel):
    """Retrieve cumulative usage metrics for a specific app since its creation. Returns total metrics data for the app identified by the provided app ID."""
    path: GetMetricsTotalRequestPath

# Operation: get_mindmap_node
class GetMindmapNodeExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the mind map node you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the specific mind map node to retrieve.")
class GetMindmapNodeExperimentalRequest(StrictModel):
    """Retrieve a specific mind map node from a board. Returns detailed information about the node including its content, position, and relationships within the mind map structure."""
    path: GetMindmapNodeExperimentalRequestPath

# Operation: delete_mindmap_node
class DeleteMindmapNodeExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the mind map node to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the mind map node to delete. Deleting a node also removes all of its child nodes.")
class DeleteMindmapNodeExperimentalRequest(StrictModel):
    """Permanently deletes a mind map node and all of its child nodes from a board. This operation requires write access to the board."""
    path: DeleteMindmapNodeExperimentalRequestPath

# Operation: list_mindmap_nodes
class GetMindmapNodesExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the mind map nodes you want to retrieve.")
class GetMindmapNodesExperimentalRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of mind map nodes to return per request. Use this with the cursor parameter to paginate through large result sets.")
class GetMindmapNodesExperimentalRequest(StrictModel):
    """Retrieves mind map nodes for a specific board using cursor-based pagination. Use the cursor from each response to fetch subsequent pages of results."""
    path: GetMindmapNodesExperimentalRequestPath
    query: GetMindmapNodesExperimentalRequestQuery | None = None

# Operation: create_mindmap_node
class CreateMindmapNodesExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the mind map node will be created.")
class CreateMindmapNodesExperimentalRequestBodyDataNodeViewData(StrictModel):
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of mind map node. Currently only 'text' is supported.")
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="The text content displayed in the mind map node.")
class CreateMindmapNodesExperimentalRequestBodyDataNodeView(StrictModel):
    data: CreateMindmapNodesExperimentalRequestBodyDataNodeViewData
class CreateMindmapNodesExperimentalRequestBodyData(StrictModel):
    node_view: CreateMindmapNodesExperimentalRequestBodyDataNodeView = Field(default=..., validation_alias="nodeView", serialization_alias="nodeView")
class CreateMindmapNodesExperimentalRequestBodyGeometry(StrictModel):
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the node in pixels.", json_schema_extra={'format': 'double'})
class CreateMindmapNodesExperimentalRequestBody(StrictModel):
    data: CreateMindmapNodesExperimentalRequestBodyData
    geometry: CreateMindmapNodesExperimentalRequestBodyGeometry | None = None
class CreateMindmapNodesExperimentalRequest(StrictModel):
    """Create a new mind map node on a board. Nodes can be root nodes (starting points) or child nodes nested under existing nodes. Node positioning uses explicit x, y coordinates; if not provided, nodes default to the board center (0, 0)."""
    path: CreateMindmapNodesExperimentalRequestPath
    body: CreateMindmapNodesExperimentalRequestBody

# Operation: list_board_items_experimental
class GetItemsExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board from which to retrieve items.")
class GetItemsExperimentalRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of items to return per request, between 10 and 50. Defaults to 10 items. Use the cursor from the response to fetch subsequent pages.")
    type_: Literal["shape"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results to return only items of a specific type. Currently supports 'shape' type items.")
class GetItemsExperimentalRequest(StrictModel):
    """Retrieves a paginated list of items on a specific board. Supports filtering by item type and uses cursor-based pagination to handle large result sets efficiently."""
    path: GetItemsExperimentalRequestPath
    query: GetItemsExperimentalRequestQuery | None = None

# Operation: get_board_item
class GetSpecificItemExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the specific item you want to retrieve from the board.")
class GetSpecificItemExperimentalRequest(StrictModel):
    """Retrieves detailed information about a specific item on a board. Use this to fetch properties and metadata for an individual item by its ID."""
    path: GetSpecificItemExperimentalRequestPath

# Operation: delete_item_beta
class DeleteItemExperimentalRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the item to delete from the board.")
class DeleteItemExperimentalRequest(StrictModel):
    """Permanently removes an item from a board. This action cannot be undone and requires write access to the board."""
    path: DeleteItemExperimentalRequestPath

# Operation: add_shape_to_board_flowchart
class CreateShapeItemFlowchartRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the shape will be created.")
class CreateShapeItemFlowchartRequestBodyData(StrictModel):
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="Optional text to display on the shape. Not supported for OR gates and summing junction flowchart shapes.")
    shape: str | None = Field(default=None, validation_alias="shape", serialization_alias="shape", description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart shapes (decision, process, terminator, etc.), or arrows. Defaults to rectangle.")
class CreateShapeItemFlowchartRequestBodyStyle(StrictModel):
    border_color: str | None = Field(default=None, validation_alias="borderColor", serialization_alias="borderColor", description="Hex color code for the shape's border. Defaults to dark gray (#1a1a1a).")
    border_opacity: str | None = Field(default=None, validation_alias="borderOpacity", serialization_alias="borderOpacity", description="Transparency level of the border, from 0 (fully transparent) to 1 (fully opaque). Defaults to 1.")
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(default=None, validation_alias="borderStyle", serialization_alias="borderStyle", description="Visual style of the border: solid (normal), dotted, or dashed. Defaults to normal.")
    border_width: str | None = Field(default=None, validation_alias="borderWidth", serialization_alias="borderWidth", description="Thickness of the border in display pixels, ranging from 1 to 24. Defaults to 2.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for the text inside the shape. Defaults to dark gray (#1a1a1a).")
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="Hex color code for the shape's fill. Supports predefined colors like #8fd14f, #f5d128, #ff9d48, and others. Defaults to white (#ffffff).")
    fill_opacity: str | None = Field(default=None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="Transparency level of the fill color, from 0 (fully transparent) to 1 (fully opaque). Flowchart shapes default to 1; basic shapes default to 1 if fillColor is set, otherwise 0.")
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Font family for the shape's text. Choose from standard fonts (Arial, Georgia, Times New Roman) or decorative options (Bangers, Permanent Marker, etc.). Defaults to Arial.")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size for the text in display pixels, ranging from 10 to 288. Defaults to 14.")
    text_align: Literal["left", "right", "center", "unknown"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="Horizontal text alignment: left, right, or center. Flowchart shapes default to center; basic shapes default to left.")
    text_align_vertical: Literal["top", "middle", "bottom", "unknown"] | None = Field(default=None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="Vertical text alignment: top, middle, or bottom. Flowchart shapes default to middle; basic shapes default to top.")
class CreateShapeItemFlowchartRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Height of the shape in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Width of the shape in pixels.", json_schema_extra={'format': 'double'})
class CreateShapeItemFlowchartRequestBody(StrictModel):
    data: CreateShapeItemFlowchartRequestBodyData | None = None
    style: CreateShapeItemFlowchartRequestBodyStyle | None = None
    geometry: CreateShapeItemFlowchartRequestBodyGeometry | None = None
class CreateShapeItemFlowchartRequest(StrictModel):
    """Adds a flowchart or basic shape item to a board with customizable styling, text, and dimensions. Requires boards:write scope."""
    path: CreateShapeItemFlowchartRequestPath
    body: CreateShapeItemFlowchartRequestBody | None = None

# Operation: get_shape_item_experimental
class GetShapeItemFlowchartRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the shape item you want to retrieve.")
    item_id: str = Field(default=..., description="The unique identifier of the shape item you want to retrieve.")
class GetShapeItemFlowchartRequest(StrictModel):
    """Retrieves detailed information about a specific shape item on a board, including its properties and positioning data."""
    path: GetShapeItemFlowchartRequestPath

# Operation: update_shape_item_flowchart
class UpdateShapeItemFlowchartRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the shape to update.")
    item_id: str = Field(default=..., description="The unique identifier of the shape item to update.")
class UpdateShapeItemFlowchartRequestBodyData(StrictModel):
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="The text content to display on the shape. Note that changing the shape type to flow_chart_or or flow_chart_summing_junction will clear any existing content.")
    shape: str | None = Field(default=None, validation_alias="shape", serialization_alias="shape", description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart-specific shapes (flow_chart_decision, flow_chart_process, etc.), or arrow/callout variants. Defaults to rectangle.")
class UpdateShapeItemFlowchartRequestBodyStyle(StrictModel):
    border_color: str | None = Field(default=None, validation_alias="borderColor", serialization_alias="borderColor", description="The color of the shape's border, specified as a hex value.")
    border_opacity: str | None = Field(default=None, validation_alias="borderOpacity", serialization_alias="borderOpacity", description="The transparency level of the border, from 0.0 (fully transparent) to 1.0 (fully opaque).")
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(default=None, validation_alias="borderStyle", serialization_alias="borderStyle", description="The visual style of the border: normal (solid), dotted, or dashed.")
    border_width: str | None = Field(default=None, validation_alias="borderWidth", serialization_alias="borderWidth", description="The thickness of the border in display pixels, ranging from 1 to 24.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The color of the text within the shape, specified as a hex value.")
    fill_color: str | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The fill color of the shape, specified as a hex value. Supports standard palette colors like #8fd14f, #23bfe7, #ff9d48, and others.")
    fill_opacity: str | None = Field(default=None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="The transparency level of the fill color, from 0.0 (fully transparent) to 1.0 (fully opaque).")
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="The font family for text within the shape. Choose from standard fonts (Arial, Georgia, Times New Roman) or design-focused options (Abril Fatface, Bangers, Permanent Marker, etc.).")
    font_size: str | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="The font size for text in the shape, in display pixels, ranging from 10 to 288.")
    text_align: Literal["left", "right", "center"] | None = Field(default=None, validation_alias="textAlign", serialization_alias="textAlign", description="The horizontal alignment of text within the shape: left, right, or center.")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(default=None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="The vertical alignment of text within the shape: top, middle, or bottom.")
class UpdateShapeItemFlowchartRequestBodyGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="The height of the shape in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="The rotation angle of the shape in degrees, relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="The width of the shape in pixels.", json_schema_extra={'format': 'double'})
class UpdateShapeItemFlowchartRequestBody(StrictModel):
    data: UpdateShapeItemFlowchartRequestBodyData | None = None
    style: UpdateShapeItemFlowchartRequestBodyStyle | None = None
    geometry: UpdateShapeItemFlowchartRequestBodyGeometry | None = None
class UpdateShapeItemFlowchartRequest(StrictModel):
    """Update a flowchart shape item on a board by modifying its geometry, styling, content, and layout properties. Changes are applied immediately to the specified shape."""
    path: UpdateShapeItemFlowchartRequestPath
    body: UpdateShapeItemFlowchartRequestBody | None = None

# Operation: delete_shape_item_experimental
class DeleteShapeItemFlowchartRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the shape item to delete.")
    item_id: str = Field(default=..., description="The unique identifier of the shape item to delete from the board.")
class DeleteShapeItemFlowchartRequest(StrictModel):
    """Permanently removes a flowchart shape item from a board. This action cannot be undone."""
    path: DeleteShapeItemFlowchartRequestPath

# Operation: create_document_item_from_file
class CreateDocumentItemUsingFileFromDeviceRequestPath(StrictModel):
    board_id_platform_file_upload: str = Field(default=..., validation_alias="board_id_PlatformFileUpload", serialization_alias="board_id_PlatformFileUpload", description="The unique identifier of the board where the document item will be created.")
class CreateDocumentItemUsingFileFromDeviceRequestBodyDataGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Optional height of the document item on the board, specified in pixels.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Optional width of the document item on the board, specified in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Optional rotation angle of the document item in degrees, relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
class CreateDocumentItemUsingFileFromDeviceRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Optional title for the document item. If not provided, the uploaded filename will be used.")
    geometry: CreateDocumentItemUsingFileFromDeviceRequestBodyDataGeometry | None = None
class CreateDocumentItemUsingFileFromDeviceRequestBody(StrictModel):
    resource: str = Field(default=..., description="The file to upload from your device. Maximum file size is 6 MB.", json_schema_extra={'format': 'binary'})
    data: CreateDocumentItemUsingFileFromDeviceRequestBodyData | None = None
class CreateDocumentItemUsingFileFromDeviceRequest(StrictModel):
    """Uploads a document file from your device and adds it as a document item to a board. The file must not exceed 6 MB in size."""
    path: CreateDocumentItemUsingFileFromDeviceRequestPath
    body: CreateDocumentItemUsingFileFromDeviceRequestBody

# Operation: update_document_item_with_file
class UpdateDocumentItemUsingFileFromDeviceRequestPath(StrictModel):
    board_id_platform_file_upload: str = Field(default=..., validation_alias="board_id_PlatformFileUpload", serialization_alias="board_id_PlatformFileUpload", description="The unique identifier of the board containing the document item you want to update.")
    item_id: str = Field(default=..., description="The unique identifier of the document item you want to replace with a new file.")
class UpdateDocumentItemUsingFileFromDeviceRequestBodyDataGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Optional height of the item in pixels. Specify as a decimal number.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Optional width of the item in pixels. Specify as a decimal number.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Optional rotation angle in degrees, relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
class UpdateDocumentItemUsingFileFromDeviceRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Optional title for the document (e.g., 'foo.png'). If not provided, the existing title is retained.")
    alt_text: str | None = Field(default=None, validation_alias="altText", serialization_alias="altText", description="Optional alt-text description to improve accessibility and help viewers understand the document content.")
    geometry: UpdateDocumentItemUsingFileFromDeviceRequestBodyDataGeometry | None = None
class UpdateDocumentItemUsingFileFromDeviceRequestBody(StrictModel):
    resource: str = Field(default=..., description="The file to upload from your device. Maximum file size is 6 MB. Provide the file as binary data.", json_schema_extra={'format': 'binary'})
    data: UpdateDocumentItemUsingFileFromDeviceRequestBodyData | None = None
class UpdateDocumentItemUsingFileFromDeviceRequest(StrictModel):
    """Replace a document item on a board with a new file uploaded from your device. The file must not exceed 6 MB in size."""
    path: UpdateDocumentItemUsingFileFromDeviceRequestPath
    body: UpdateDocumentItemUsingFileFromDeviceRequestBody

# Operation: create_image_item_from_local_file
class CreateImageItemUsingLocalFileRequestPath(StrictModel):
    board_id_platform_file_upload: str = Field(default=..., validation_alias="board_id_PlatformFileUpload", serialization_alias="board_id_PlatformFileUpload", description="The unique identifier of the board where the image item will be created.")
class CreateImageItemUsingLocalFileRequestBodyDataGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Optional height of the image item in pixels. If not specified, the original image dimensions will be used.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Optional width of the image item in pixels. If not specified, the original image dimensions will be used.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Optional rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation.", json_schema_extra={'format': 'double'})
class CreateImageItemUsingLocalFileRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Optional display title for the image item (e.g., 'foo.png'). If not provided, the filename may be used.")
    alt_text: str | None = Field(default=None, validation_alias="altText", serialization_alias="altText", description="Optional alt text describing the image content for accessibility purposes.")
    geometry: CreateImageItemUsingLocalFileRequestBodyDataGeometry | None = None
class CreateImageItemUsingLocalFileRequestBody(StrictModel):
    resource: str = Field(default=..., description="The image file to upload from your device. Maximum file size is 6 MB.", json_schema_extra={'format': 'binary'})
    data: CreateImageItemUsingLocalFileRequestBodyData | None = None
class CreateImageItemUsingLocalFileRequest(StrictModel):
    """Adds an image item to a board by uploading a file from your device. Supports images up to 6 MB with optional sizing, rotation, and accessibility metadata."""
    path: CreateImageItemUsingLocalFileRequestPath
    body: CreateImageItemUsingLocalFileRequestBody

# Operation: update_image_item_from_file
class UpdateImageItemUsingFileFromDeviceRequestPath(StrictModel):
    board_id_platform_file_upload: str = Field(default=..., validation_alias="board_id_PlatformFileUpload", serialization_alias="board_id_PlatformFileUpload", description="The unique identifier of the board containing the image item you want to update.")
    item_id: str = Field(default=..., description="The unique identifier of the image item on the board that you want to replace or modify.")
class UpdateImageItemUsingFileFromDeviceRequestBodyDataGeometry(StrictModel):
    height: float | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Optional height of the image in pixels. Specify as a decimal number to set or adjust the vertical dimension.", json_schema_extra={'format': 'double'})
    width: float | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Optional width of the image in pixels. Specify as a decimal number to set or adjust the horizontal dimension.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(default=None, validation_alias="rotation", serialization_alias="rotation", description="Optional rotation angle in degrees. Use positive values to rotate clockwise and negative values to rotate counterclockwise.", json_schema_extra={'format': 'double'})
class UpdateImageItemUsingFileFromDeviceRequestBodyData(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Optional display name for the image (e.g., 'foo.png'). If not provided, the existing title is retained.")
    alt_text: str | None = Field(default=None, validation_alias="altText", serialization_alias="altText", description="Optional alt text describing the image content for accessibility purposes. Helps users understand what the image depicts.")
    geometry: UpdateImageItemUsingFileFromDeviceRequestBodyDataGeometry | None = None
class UpdateImageItemUsingFileFromDeviceRequestBody(StrictModel):
    resource: str = Field(default=..., description="The image file to upload from your device. Maximum file size is 6 MB. This replaces the existing image on the item.", json_schema_extra={'format': 'binary'})
    data: UpdateImageItemUsingFileFromDeviceRequestBodyData | None = None
class UpdateImageItemUsingFileFromDeviceRequest(StrictModel):
    """Replace an image on a board with a new file from your device. Supports updating the image file itself along with optional metadata like title, alt text, dimensions, and rotation."""
    path: UpdateImageItemUsingFileFromDeviceRequestPath
    body: UpdateImageItemUsingFileFromDeviceRequestBody

# Operation: list_groups_on_board
class GetAllGroupsRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board from which to retrieve groups.")
class GetAllGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of groups to return per request, between 10 and 50 items (defaults to 10). Use this with the cursor parameter to paginate through results.", json_schema_extra={'format': 'int32'})
class GetAllGroupsRequest(StrictModel):
    """Retrieve all groups and their items from a specific board using cursor-based pagination. Results are returned in batches with a cursor for fetching subsequent pages."""
    path: GetAllGroupsRequestPath
    query: GetAllGroupsRequestQuery | None = None

# Operation: list_items_in_group
class GetItemsByGroupIdRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the group.")
class GetItemsByGroupIdRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of items to return per request, between 10 and 50 items (defaults to 10).", json_schema_extra={'format': 'int32'})
    group_item_id: str = Field(default=..., description="The unique identifier of the group whose items you want to retrieve.")
class GetItemsByGroupIdRequest(StrictModel):
    """Retrieve all items belonging to a specific group within a board using cursor-based pagination. Results are returned in batches with a cursor for fetching subsequent pages."""
    path: GetItemsByGroupIdRequestPath
    query: GetItemsByGroupIdRequestQuery

# Operation: get_group_by_id
class GetGroupByIdRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the group. This is a required string ID that identifies which board to query.")
    group_id: str = Field(default=..., description="The unique identifier of the group to retrieve. This is a required numeric ID that specifies which group's items should be returned.")
class GetGroupByIdRequest(StrictModel):
    """Retrieves a specific group and its contained items from a board. Requires boards:read scope and is subject to Level 2 rate limiting."""
    path: GetGroupByIdRequestPath

# Operation: update_group
class UpdateGroupRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the group to update.")
    group_id: str = Field(default=..., description="The unique identifier of the group to replace.")
class UpdateGroupRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the new user group.")
    name: str = Field(default=..., description="The name of the user group.")
    description: str | None = Field(default=None, description="Optional description providing additional context about the user group.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The object type, which must be set to 'user-group'.")
class UpdateGroupRequest(StrictModel):
    """Replaces an existing group on a board with new content. The original group is completely replaced and assigned a new ID."""
    path: UpdateGroupRequestPath
    body: UpdateGroupRequestBody

# Operation: remove_items_from_group
class UnGroupRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the group to ungroup items from.")
class UnGroupRequestQuery(StrictModel):
    delete_items: bool | None = Field(default=None, description="When true, removes the ungrouped items from the board entirely. When false (default), items remain on the board but are no longer grouped.")
class UnGroupRequest(StrictModel):
    """Ungroups items from a group on a board, optionally removing them entirely. Requires boards:write scope."""
    path: UnGroupRequestPath
    query: UnGroupRequestQuery | None = None

# Operation: delete_group
class DeleteGroupRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the group to delete.")
    group_id: str = Field(default=..., description="The unique identifier of the group to delete.")
class DeleteGroupRequestQuery(StrictModel):
    delete_items: bool = Field(default=..., description="Set to true to remove all items in the group along with the group itself. Set to false to preserve items.")
class DeleteGroupRequest(StrictModel):
    """Permanently deletes a group from a board, including all items contained within it. Note that this operation will delete locked items as well."""
    path: DeleteGroupRequestPath
    query: DeleteGroupRequestQuery

# Operation: list_tags_for_item
class GetTagsFromItemRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the item. This ID is required to locate the correct board context.")
    item_id: str = Field(default=..., description="The unique identifier of the item whose tags you want to retrieve. This ID must correspond to an item that exists on the specified board.")
class GetTagsFromItemRequest(StrictModel):
    """Retrieves all tags associated with a specific item on a board. Use this to view the complete set of tags currently applied to an item."""
    path: GetTagsFromItemRequestPath

# Operation: list_tags_from_board
class GetTagsFromBoardRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board from which to retrieve tags.")
class GetTagsFromBoardRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of tags to return in a single request. Must be between 1 and 50 items. Defaults to 20 if not specified.")
    offset: str | None = Field(default=None, description="The number of tags to skip before returning results, used for pagination. Defaults to 0 (starting from the first tag).")
class GetTagsFromBoardRequest(StrictModel):
    """Retrieves all tags associated with a specified board. Supports pagination to control the number of results returned."""
    path: GetTagsFromBoardRequestPath
    query: GetTagsFromBoardRequestQuery | None = None

# Operation: create_tag
class CreateTagRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board where the tag will be created.")
class CreateTagRequestBody(StrictModel):
    fill_color: Literal["red", "light_green", "cyan", "yellow", "magenta", "green", "blue", "gray", "violet", "dark_green", "dark_blue", "black"] | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The visual color for the tag. Choose from a predefined palette of 12 colors including red, green, blue, cyan, yellow, magenta, violet, gray, black, and their variants. Defaults to red if not specified.")
    title: str = Field(default=..., description="The display text for the tag, case-sensitive and must be unique within the board. Can be up to 120 characters long.", min_length=0, max_length=120)
class CreateTagRequest(StrictModel):
    """Creates a new tag on a board to organize and categorize board items. Tag titles must be unique within the board and can be assigned a color for visual distinction."""
    path: CreateTagRequestPath
    body: CreateTagRequestBody

# Operation: get_tag
class GetTagRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the tag you want to retrieve.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag whose information you want to retrieve.")
class GetTagRequest(StrictModel):
    """Retrieves detailed information about a specific tag on a board. Use this to fetch tag properties and metadata by providing the board and tag identifiers."""
    path: GetTagRequestPath

# Operation: update_tag
class UpdateTagRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the tag you want to update.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag you want to update.")
class UpdateTagRequestBody(StrictModel):
    fill_color: Literal["red", "light_green", "cyan", "yellow", "magenta", "green", "blue", "gray", "violet", "dark_green", "dark_blue", "black"] | None = Field(default=None, validation_alias="fillColor", serialization_alias="fillColor", description="The fill color for the tag. Choose from: red, light_green, cyan, yellow, magenta, green, blue, gray, violet, dark_green, dark_blue, or black.")
    title: str | None = Field(default=None, description="The text label for the tag, case-sensitive and must be unique within the board. Maximum 120 characters.", min_length=0, max_length=120)
class UpdateTagRequest(StrictModel):
    """Updates an existing tag on a board by modifying its title and/or fill color. Note that changes made via the REST API will not appear in real-time on the board; you must refresh the board to see updates."""
    path: UpdateTagRequestPath
    body: UpdateTagRequestBody | None = None

# Operation: delete_tag
class DeleteTagRequestPath(StrictModel):
    board_id: str = Field(default=..., description="The unique identifier of the board containing the tag to delete.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag to delete from the board.")
class DeleteTagRequest(StrictModel):
    """Permanently deletes a tag from the board and removes it from all associated cards and sticky notes. Note: Changes made via REST API may not appear in real-time on the board; refresh the board to see updates."""
    path: DeleteTagRequestPath

# Operation: list_items_by_tag
class GetItemsByTagRequestPath(StrictModel):
    board_id_platform_tags: str = Field(default=..., validation_alias="board_id_PlatformTags", serialization_alias="board_id_PlatformTags", description="The unique identifier of the board containing the items you want to retrieve.")
class GetItemsByTagRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of items to return in a single request. Must be between 1 and 50 items. Defaults to 20 if not specified.")
    offset: str | None = Field(default=None, description="The number of items to skip from the beginning of the result set, used for pagination. Defaults to 0 if not specified.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag used to filter items. Only items with this tag will be returned.")
class GetItemsByTagRequest(StrictModel):
    """Retrieves all items on a board that have been assigned a specific tag. Use pagination parameters to control the number of results returned."""
    path: GetItemsByTagRequestPath
    query: GetItemsByTagRequestQuery

# Operation: add_tag_to_item
class AttachTagToItemRequestPath(StrictModel):
    board_id_platform_tags: str = Field(default=..., validation_alias="board_id_PlatformTags", serialization_alias="board_id_PlatformTags", description="The unique identifier of the board containing the item you want to tag.")
    item_id: str = Field(default=..., description="The unique identifier of the item (card or sticky note) to which you want to attach the tag.")
class AttachTagToItemRequestQuery(StrictModel):
    tag_id: str = Field(default=..., description="The unique identifier of the existing tag you want to attach to the item.")
class AttachTagToItemRequest(StrictModel):
    """Attach an existing tag to an item on a board. Cards and sticky notes support up to 8 tags each. Note: Tag changes via REST API require a board refresh to appear in real-time."""
    path: AttachTagToItemRequestPath
    query: AttachTagToItemRequestQuery

# Operation: remove_tag_from_item
class RemoveTagFromItemRequestPath(StrictModel):
    board_id_platform_tags: str = Field(default=..., validation_alias="board_id_PlatformTags", serialization_alias="board_id_PlatformTags", description="The unique identifier of the board containing the item from which you want to remove the tag.")
    item_id: str = Field(default=..., description="The unique identifier of the item from which you want to remove the tag.")
class RemoveTagFromItemRequestQuery(StrictModel):
    tag_id: str = Field(default=..., description="The unique identifier of the tag to remove from the item.")
class RemoveTagFromItemRequest(StrictModel):
    """Removes a tag from an item on a board. The tag remains available on the board for use with other items. Note: Tag changes via REST API require a board refresh to appear in the UI."""
    path: RemoveTagFromItemRequestPath
    query: RemoveTagFromItemRequestQuery

# Operation: list_projects_in_team
class EnterpriseGetProjectsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team. Required to scope the request to the correct organization.")
    team_id: str = Field(default=..., description="The unique identifier of the team within the organization. Required to retrieve projects from the specific team.")
class EnterpriseGetProjectsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of projects to return in a single response, between 1 and 100. Defaults to 100. If more projects exist than the limit, the response includes a cursor for pagination.", json_schema_extra={'format': 'int32'})
class EnterpriseGetProjectsRequest(StrictModel):
    """Retrieves all projects (also called Spaces) within a specific team of an organization. With Content Admin permissions, you can access all projects including private ones not explicitly shared with you."""
    path: EnterpriseGetProjectsRequestPath
    query: EnterpriseGetProjectsRequestQuery | None = None

# Operation: create_project_in_team
class EnterpriseCreateProjectRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization where you want to create the project.")
    team_id: str = Field(default=..., description="The unique identifier of the team within the organization where you want to create the project.")
class EnterpriseCreateProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="The name for the new project. Must be between 1 and 60 characters.", min_length=1, max_length=60)
class EnterpriseCreateProjectRequest(StrictModel):
    """Create a new project (Space) within an existing team in your organization. Projects are organizational folders for boards that allow you to manage access and share multiple boards with a subset of team members."""
    path: EnterpriseCreateProjectRequestPath
    body: EnterpriseCreateProjectRequestBody

# Operation: get_project_in_team
class EnterpriseGetProjectRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The organization ID that contains the team and project. Use the numeric organization identifier provided in your Enterprise account.")
    team_id: str = Field(default=..., description="The team ID that contains the project. Use the numeric team identifier within the organization.")
    project_id: str = Field(default=..., description="The project ID to retrieve information for. Use the numeric project identifier within the team.")
class EnterpriseGetProjectRequest(StrictModel):
    """Retrieve detailed information about a specific project (Space) within a team, including its name and metadata. Enterprise-only endpoint requiring Company Admin role."""
    path: EnterpriseGetProjectRequestPath

# Operation: update_project
class EnterpriseUpdateProjectRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the project.")
    team_id: str = Field(default=..., description="The unique identifier of the team that owns the project.")
    project_id: str = Field(default=..., description="The unique identifier of the project to update.")
class EnterpriseUpdateProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="The new name for the project. Must be between 1 and 60 characters.", min_length=1, max_length=60)
class EnterpriseUpdateProjectRequest(StrictModel):
    """Update project details such as the project name. This operation is available only for Enterprise plan users with Company Admin role."""
    path: EnterpriseUpdateProjectRequestPath
    body: EnterpriseUpdateProjectRequestBody

# Operation: delete_project_in_team
class EnterpriseDeleteProjectRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The organization ID from which the project will be deleted. Use the numeric organization identifier.")
    team_id: str = Field(default=..., description="The team ID from which the project will be deleted. Use the numeric team identifier.")
    project_id: str = Field(default=..., description="The project ID to delete. Use the numeric project identifier.")
class EnterpriseDeleteProjectRequest(StrictModel):
    """Permanently deletes a project (Space) from a team within an organization. Boards and users associated with the project remain in the team after deletion. Requires Enterprise plan and Company Admin role."""
    path: EnterpriseDeleteProjectRequestPath

# Operation: list_project_members
class EnterpriseGetProjectMembersRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that contains the project.")
    team_id: str = Field(default=..., description="The unique identifier of the team that contains the project.")
    project_id: str = Field(default=..., description="The unique identifier of the project for which to retrieve members.")
class EnterpriseGetProjectMembersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of members to return per request, between 1 and 100. Defaults to 100. If the total exceeds this limit, use the cursor in the response to fetch additional results.", json_schema_extra={'format': 'int32'})
class EnterpriseGetProjectMembersRequest(StrictModel):
    """Retrieves all members assigned to a specific project (also called a Space) within an organization and team. Requires Enterprise plan access and Company Admin role."""
    path: EnterpriseGetProjectMembersRequestPath
    query: EnterpriseGetProjectMembersRequestQuery | None = None

# Operation: add_project_member
class EnterpriseAddProjectMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that owns the project.")
    team_id: str = Field(default=..., description="The unique identifier of the team that owns the project.")
    project_id: str = Field(default=..., description="The unique identifier of the project (Space) to which you want to add the user.")
class EnterpriseAddProjectMemberRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the Miro user to add to the project.")
    role: Literal["owner", "editor", "viewer", "commentator", "coowner"] = Field(default=..., description="The access level for the project member. Choose from: owner, coowner, editor, commentator, or viewer.")
class EnterpriseAddProjectMemberRequest(StrictModel):
    """Add a Miro user to a project (Space) with a specified role. This enterprise-only operation requires Company Admin privileges and the projects:write scope."""
    path: EnterpriseAddProjectMemberRequestPath
    body: EnterpriseAddProjectMemberRequestBody

# Operation: get_project_member
class EnterpriseGetProjectMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that contains the project. Use the organization ID provided in your enterprise account.")
    team_id: str = Field(default=..., description="The unique identifier of the team that owns the project. Use the team ID associated with your organization.")
    project_id: str = Field(default=..., description="The unique identifier of the project (Space) from which you want to retrieve member information.")
    member_id: str = Field(default=..., description="The unique identifier of the specific member whose information you want to retrieve.")
class EnterpriseGetProjectMemberRequest(StrictModel):
    """Retrieves detailed information about a specific member within a project (Space). This enterprise-only endpoint requires Company Admin role and the projects:read scope."""
    path: EnterpriseGetProjectMemberRequestPath

# Operation: update_project_member_role
class EnterpriseUpdateProjectMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The organization ID that contains the team and project. Use the numeric organization identifier (e.g., 3074457345618265000).")
    team_id: str = Field(default=..., description="The team ID that owns the project. Use the numeric team identifier (e.g., 3074457345619012000).")
    project_id: str = Field(default=..., description="The project (Space) ID where the member's role will be updated. Use the numeric project identifier (e.g., 3074457345618265000).")
    member_id: str = Field(default=..., description="The member ID whose role you want to update. Use the numeric member identifier (e.g., 307445734562315000).")
class EnterpriseUpdateProjectMemberRequestBody(StrictModel):
    role: Literal["owner", "editor", "viewer", "commentator", "coowner"] | None = Field(default=None, description="The new role to assign to the project member. Valid roles are: owner, coowner, editor, commentator, or viewer. Determines the member's access level and permissions within the project.")
class EnterpriseUpdateProjectMemberRequest(StrictModel):
    """Update a project member's role within a team's project space. This enterprise-only operation allows Company Admins to modify member permissions such as changing them from viewer to editor or assigning ownership roles."""
    path: EnterpriseUpdateProjectMemberRequestPath
    body: EnterpriseUpdateProjectMemberRequestBody | None = None

# Operation: remove_project_member
class EnterpriseDeleteProjectMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that contains the project.")
    team_id: str = Field(default=..., description="The unique identifier of the team that contains the project.")
    project_id: str = Field(default=..., description="The unique identifier of the project from which the member will be removed.")
    member_id: str = Field(default=..., description="The unique identifier of the member to remove from the project.")
class EnterpriseDeleteProjectMemberRequest(StrictModel):
    """Remove a member from a project within a team. The member will no longer have access to the project, but remains part of the team. This operation is available only to Company Admins on Enterprise plans."""
    path: EnterpriseDeleteProjectMemberRequestPath

# Operation: list_organization_teams
class EnterpriseGetTeamsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization whose teams you want to retrieve.")
class EnterpriseGetTeamsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of teams to return per request. Accepts values between 1 and 100, defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(default=None, description="Filters teams by name using case-insensitive partial matching. For example, 'dev' will match both 'Developer's team' and 'Team for developers'.")
class EnterpriseGetTeamsRequest(StrictModel):
    """Retrieves all teams within an organization. Supports filtering by team name and pagination. Available only to Company Admins on Enterprise plans."""
    path: EnterpriseGetTeamsRequestPath
    query: EnterpriseGetTeamsRequestQuery | None = None

# Operation: create_team
class EnterpriseCreateTeamRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization where the team will be created.")
class EnterpriseCreateTeamRequestBody(StrictModel):
    name: str = Field(default=..., description="The name for the new team. Must be between 1 and 60 characters long.", min_length=1, max_length=60)
class EnterpriseCreateTeamRequest(StrictModel):
    """Creates a new team within an existing organization. This enterprise-only operation requires Company Admin role and the organizations:teams:write scope."""
    path: EnterpriseCreateTeamRequestPath
    body: EnterpriseCreateTeamRequestBody

# Operation: get_team
class EnterpriseGetTeamRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that contains the team. Use the organization ID provided during enterprise setup.")
    team_id: str = Field(default=..., description="The unique identifier of the team to retrieve. This must be a valid team ID within the specified organization.")
class EnterpriseGetTeamRequest(StrictModel):
    """Retrieves detailed information about a specific team within an organization. This enterprise-only endpoint requires Company Admin role and the organizations:teams:read scope."""
    path: EnterpriseGetTeamRequestPath

# Operation: update_team
class EnterpriseUpdateTeamRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team to update.")
class EnterpriseUpdateTeamRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the team. Must be between 1 and 60 characters long.", min_length=1, max_length=60)
class EnterpriseUpdateTeamRequest(StrictModel):
    """Updates an existing team's properties within an organization. Requires Enterprise plan access and Company Admin role."""
    path: EnterpriseUpdateTeamRequestPath
    body: EnterpriseUpdateTeamRequestBody | None = None

# Operation: delete_team
class EnterpriseDeleteTeamRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team to delete.")
    team_id: str = Field(default=..., description="The unique identifier of the team to delete.")
class EnterpriseDeleteTeamRequest(StrictModel):
    """Permanently deletes an existing team from an organization. This operation is restricted to Enterprise plan users with Company Admin role."""
    path: EnterpriseDeleteTeamRequestPath

# Operation: list_team_members
class EnterpriseGetTeamMembersRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team whose members you want to retrieve.")
class EnterpriseGetTeamMembersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of team members to return per request. Must be between 1 and 100; defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
    role: str | None = Field(default=None, description="Filter results by member role using exact matching. Valid values are: 'member' (standard team member), 'admin' (team administrator), 'non_team' (external user without team access), or 'team_guest' (deprecated legacy guest access).")
class EnterpriseGetTeamMembersRequest(StrictModel):
    """Retrieves a paginated list of members in a team within an organization. Supports filtering by member role and pagination via cursor-based limits."""
    path: EnterpriseGetTeamMembersRequestPath
    query: EnterpriseGetTeamMembersRequestQuery | None = None

# Operation: add_team_member
class EnterpriseInviteTeamMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team to which the user will be invited.")
class EnterpriseInviteTeamMemberRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the existing Miro organization user to invite to the team.")
    role: Literal["member", "admin"] | None = Field(default=None, description="The role to assign to the team member. Use 'member' for standard team member permissions or 'admin' to grant team management capabilities. Defaults to 'member' if not specified.")
class EnterpriseInviteTeamMemberRequest(StrictModel):
    """Invite an existing Miro organization user to join a team. The user must already exist in your Miro organization; new users can be provisioned via SCIM and external identity providers like Okta or Azure Active Directory."""
    path: EnterpriseInviteTeamMemberRequestPath
    body: EnterpriseInviteTeamMemberRequestBody

# Operation: get_team_member
class EnterpriseGetTeamMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team containing the member.")
    member_id: str = Field(default=..., description="The unique identifier of the team member to retrieve.")
class EnterpriseGetTeamMemberRequest(StrictModel):
    """Retrieves a specific team member by their ID within an organization and team. This enterprise-only operation requires Company Admin role and the organizations:teams:read scope."""
    path: EnterpriseGetTeamMemberRequestPath

# Operation: update_team_member_role
class EnterpriseUpdateTeamMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team. Use the organization ID provided in your Enterprise account.")
    team_id: str = Field(default=..., description="The unique identifier of the team containing the member to update.")
    member_id: str = Field(default=..., description="The unique identifier of the team member whose role should be updated.")
class EnterpriseUpdateTeamMemberRequestBody(StrictModel):
    role: Literal["member", "admin"] | None = Field(default=None, description="The new role to assign to the team member. Choose 'member' for standard team member permissions or 'admin' to grant team management capabilities.")
class EnterpriseUpdateTeamMemberRequest(StrictModel):
    """Update a team member's role within a team. This operation allows Company Admins to change a team member's permissions between standard member and admin roles. Available only for Enterprise plan users."""
    path: EnterpriseUpdateTeamMemberRequestPath
    body: EnterpriseUpdateTeamMemberRequestBody | None = None

# Operation: remove_team_member
class EnterpriseDeleteTeamMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team from which the member will be removed.")
    member_id: str = Field(default=..., description="The unique identifier of the team member to be removed.")
class EnterpriseDeleteTeamMemberRequest(StrictModel):
    """Remove a team member from a team by their ID. This operation is only available for Enterprise plan users with Company Admin role."""
    path: EnterpriseDeleteTeamMemberRequestPath

# Operation: list_groups_enterprise
class EnterpriseGetGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization whose groups you want to retrieve.")
class EnterpriseGetGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of groups to return in a single response, between 1 and 100. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class EnterpriseGetGroupsRequest(StrictModel):
    """Retrieves all user groups within an organization. This operation is available only to Company Admins on Enterprise plans."""
    path: EnterpriseGetGroupsRequestPath
    query: EnterpriseGetGroupsRequestQuery | None = None

# Operation: create_group_organization
class EnterpriseCreateGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization where the group will be created.")
class EnterpriseCreateGroupRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the user group. Must be between 1 and 60 characters.", min_length=1, max_length=60)
    description: str | None = Field(default=None, description="An optional description of the user group's purpose or membership. Can be up to 300 characters.", min_length=0, max_length=300)
class EnterpriseCreateGroupRequest(StrictModel):
    """Creates a new user group within an organization. This enterprise-only operation requires Company Admin role and the organizations:groups:write scope."""
    path: EnterpriseCreateGroupRequestPath
    body: EnterpriseCreateGroupRequestBody

# Operation: get_group_enterprise
class EnterpriseGetGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the user group to retrieve.")
class EnterpriseGetGroupRequest(StrictModel):
    """Retrieves a specific user group within an organization. This enterprise-only endpoint requires Company Admin role and the organizations:groups:read scope."""
    path: EnterpriseGetGroupRequestPath

# Operation: update_group_org
class EnterpriseUpdateGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group to update.")
    group_id: str = Field(default=..., description="The unique identifier of the user group to update.")
class EnterpriseUpdateGroupRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the group. Must be between 1 and 60 characters long.", min_length=1, max_length=60)
    description: str | None = Field(default=None, description="The new description for the group. Can be empty or up to 300 characters long.", min_length=0, max_length=300)
class EnterpriseUpdateGroupRequest(StrictModel):
    """Updates the name and/or description of a user group within an organization. This operation is restricted to Enterprise plan users with Company Admin role."""
    path: EnterpriseUpdateGroupRequestPath
    body: EnterpriseUpdateGroupRequestBody | None = None

# Operation: delete_group_organization
class EnterpriseDeleteGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group to delete.")
    group_id: str = Field(default=..., description="The unique identifier of the user group to delete.")
class EnterpriseDeleteGroupRequest(StrictModel):
    """Permanently removes a user group from an organization. This operation is restricted to Enterprise plan users with Company Admin role."""
    path: EnterpriseDeleteGroupRequestPath

# Operation: list_group_members
class EnterpriseGetGroupMembersRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the user group whose members you want to retrieve.")
class EnterpriseGetGroupMembersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of members to return in the response, between 1 and 100. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class EnterpriseGetGroupMembersRequest(StrictModel):
    """Retrieves all members belonging to a specific user group within an organization. This enterprise-only operation requires Company Admin role and the organizations:groups:read scope."""
    path: EnterpriseGetGroupMembersRequestPath
    query: EnterpriseGetGroupMembersRequestQuery | None = None

# Operation: add_member_to_group
class EnterpriseCreateGroupMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group. Use the organization ID provided in your enterprise account.")
    group_id: str = Field(default=..., description="The unique identifier of the user group to which the member will be added.")
class EnterpriseCreateGroupMemberRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the user to add to the group. Must be a valid email format associated with an existing user in the organization.")
class EnterpriseCreateGroupMemberRequest(StrictModel):
    """Adds a user to a group within an organization. This enterprise-only operation requires Company Admin role and the organizations:groups:write scope."""
    path: EnterpriseCreateGroupMemberRequestPath
    body: EnterpriseCreateGroupMemberRequestBody

# Operation: update_group_members
class EnterpriseUpdateGroupMembersRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the user group to modify.")
class EnterpriseUpdateGroupMembersRequestBody(StrictModel):
    members_to_add: list[str] | None = Field(default=None, validation_alias="membersToAdd", serialization_alias="membersToAdd", description="List of user email addresses to add to the group. Each email must correspond to an existing user in the organization.")
    members_to_remove: list[str] | None = Field(default=None, validation_alias="membersToRemove", serialization_alias="membersToRemove", description="List of user email addresses to remove from the group. Each email must correspond to a current member of the group.")
class EnterpriseUpdateGroupMembersRequest(StrictModel):
    """Bulk add and remove members from a user group in a single request. Specify users to add and/or remove by email address."""
    path: EnterpriseUpdateGroupMembersRequestPath
    body: EnterpriseUpdateGroupMembersRequestBody | None = None

# Operation: get_group_member
class EnterpriseGetGroupMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the user group from which to retrieve the member.")
    member_id: str = Field(default=..., description="The unique identifier of the group member whose information should be retrieved.")
class EnterpriseGetGroupMemberRequest(StrictModel):
    """Retrieve detailed information about a specific user within a group in an organization. This operation requires Enterprise plan access and Company Admin role."""
    path: EnterpriseGetGroupMemberRequestPath

# Operation: remove_group_member
class EnterpriseDeleteGroupMemberRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the user group from which the member will be removed.")
    member_id: str = Field(default=..., description="The unique identifier of the group member to be removed.")
class EnterpriseDeleteGroupMemberRequest(StrictModel):
    """Remove a member from a user group within an organization. This operation is restricted to Enterprise plan users with Company Admin role."""
    path: EnterpriseDeleteGroupMemberRequestPath

# Operation: list_teams_for_group
class EnterpriseGroupsGetTeamsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group.")
    group_id: str = Field(default=..., description="The unique identifier of the user group whose team memberships you want to retrieve.")
class EnterpriseGroupsGetTeamsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of teams to return in the response, between 1 and 100. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class EnterpriseGroupsGetTeamsRequest(StrictModel):
    """Retrieves all teams that a user group is a member of within an organization. This operation is available only to Company Admins on Enterprise plans."""
    path: EnterpriseGroupsGetTeamsRequestPath
    query: EnterpriseGroupsGetTeamsRequestQuery | None = None

# Operation: get_group_team
class EnterpriseGroupsGetTeamRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the group and team.")
    group_id: str = Field(default=..., description="The unique identifier of the user group within the organization.")
    team_id: str = Field(default=..., description="The unique identifier of the team to retrieve information for.")
class EnterpriseGroupsGetTeamRequest(StrictModel):
    """Retrieve details about a specific team that a user group belongs to within an organization. This enterprise-only operation requires Company Admin role and appropriate organizational scopes."""
    path: EnterpriseGroupsGetTeamRequestPath

# Operation: list_groups_for_team
class EnterpriseTeamsGetGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team.")
    team_id: str = Field(default=..., description="The unique identifier of the team whose connected groups you want to retrieve.")
class EnterpriseTeamsGetGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of user groups to return in the response, between 1 and 100. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class EnterpriseTeamsGetGroupsRequest(StrictModel):
    """Retrieve all user groups that are connected to a specific team within an organization. This operation is available only for Enterprise plan users with Company Admin role."""
    path: EnterpriseTeamsGetGroupsRequestPath
    query: EnterpriseTeamsGetGroupsRequestQuery | None = None

# Operation: add_user_group_to_team
class EnterpriseTeamsCreateGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization where the team resides.")
    team_id: str = Field(default=..., description="The unique identifier of the team to which the user group will be added.")
class EnterpriseTeamsCreateGroupRequestBody(StrictModel):
    user_group_id: str = Field(default=..., validation_alias="userGroupId", serialization_alias="userGroupId", description="The unique identifier of the user group to be added to the team.")
    role: Literal["member"] = Field(default=..., description="The role assigned to the user group within the team. Currently supports member role.")
class EnterpriseTeamsCreateGroupRequest(StrictModel):
    """Adds a user group to a team within an organization, establishing the group's membership and role. This enterprise-only operation requires Company Admin privileges."""
    path: EnterpriseTeamsCreateGroupRequestPath
    body: EnterpriseTeamsCreateGroupRequestBody

# Operation: get_team_group
class EnterpriseTeamsGetGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization. Use the organization ID provided in your Enterprise account.")
    team_id: str = Field(default=..., description="The unique identifier of the team. Use the team ID to scope the group lookup within a specific team.")
    group_id: str = Field(default=..., description="The unique identifier of the user group. Use the group ID to retrieve information about a specific group within the team.")
class EnterpriseTeamsGetGroupRequest(StrictModel):
    """Retrieve details about a specific user group within a team. This operation requires Enterprise plan access and Company Admin role."""
    path: EnterpriseTeamsGetGroupRequestPath

# Operation: remove_group_from_team
class EnterpriseTeamsDeleteGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the team. Use the organization ID provided during setup (a numeric string).")
    team_id: str = Field(default=..., description="The unique identifier of the team from which the group will be removed. Use the team ID provided during setup (a numeric string).")
    group_id: str = Field(default=..., description="The unique identifier of the user group to remove from the team. Use the group ID provided during setup (a numeric string).")
class EnterpriseTeamsDeleteGroupRequest(StrictModel):
    """Remove a user group from a team within an organization. This operation disconnects the group's access to the team and is only available for Enterprise plan users with Company Admin role."""
    path: EnterpriseTeamsDeleteGroupRequestPath

# Operation: list_board_groups
class EnterpriseBoardsGetGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the board.")
    board_id: str = Field(default=..., description="The unique identifier of the board for which to retrieve group assignments.")
class EnterpriseBoardsGetGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of user groups to return in the response, between 1 and 100. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class EnterpriseBoardsGetGroupsRequest(StrictModel):
    """Retrieve all user groups that have been invited to a specific board. This operation is available only for Enterprise plan users with Company Admin role."""
    path: EnterpriseBoardsGetGroupsRequestPath
    query: EnterpriseBoardsGetGroupsRequestQuery | None = None

# Operation: share_board_with_groups
class EnterpriseBoardsCreateGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization. Format: numeric string (e.g., '3074457345618265000').")
    board_id: str = Field(default=..., description="The unique identifier of the board to share. Format: alphanumeric string (e.g., 'uXjVOfjm6tI=').")
class EnterpriseBoardsCreateGroupRequestBody(StrictModel):
    user_group_ids: list[str] = Field(default=..., validation_alias="userGroupIds", serialization_alias="userGroupIds", description="One or more user group IDs to grant access to the board. Provide as an array of group identifiers.")
    role: Literal["VIEWER", "COMMENTER", "EDITOR"] = Field(default=..., description="The permission level for the user groups on the board. Choose from: VIEWER (read-only access), COMMENTER (can view and comment), or EDITOR (full editing access). Defaults to VIEWER if not specified.")
class EnterpriseBoardsCreateGroupRequest(StrictModel):
    """Grant user groups access to a board with a specified role. If a group already has access, this operation updates their role. Enterprise-only operation requiring Company Admin privileges."""
    path: EnterpriseBoardsCreateGroupRequestPath
    body: EnterpriseBoardsCreateGroupRequestBody

# Operation: remove_group_from_board
class EnterpriseBoardsDeleteGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization that contains the board.")
    board_id: str = Field(default=..., description="The unique identifier of the board from which the user group will be removed.")
    group_id: str = Field(default=..., description="The unique identifier of the user group to be removed from the board.")
class EnterpriseBoardsDeleteGroupsRequest(StrictModel):
    """Remove a user group's access from a board. This operation revokes the specified user group's assignment to the board within an organization."""
    path: EnterpriseBoardsDeleteGroupsRequestPath

# Operation: list_project_groups
class EnterpriseProjectsGetGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the project.")
    project_id: str = Field(default=..., description="The unique identifier of the project for which to retrieve group assignments.")
class EnterpriseProjectsGetGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of groups to return in the response, between 1 and 100. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class EnterpriseProjectsGetGroupsRequest(StrictModel):
    """Retrieve user groups that have been invited to a specific project. Returns a paginated list of group assignments within the project."""
    path: EnterpriseProjectsGetGroupsRequestPath
    query: EnterpriseProjectsGetGroupsRequestQuery | None = None

# Operation: share_project_with_groups
class EnterpriseProjectCreateGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization containing the project.")
    project_id: str = Field(default=..., description="The unique identifier of the project to share with user groups.")
class EnterpriseProjectCreateGroupRequestBody(StrictModel):
    user_group_ids: list[str] = Field(default=..., validation_alias="userGroupIds", serialization_alias="userGroupIds", description="List of user group identifiers to grant or update access for. Each ID must be a valid group within the organization.")
    role: Literal["VIEWER", "COMMENTER", "EDITOR"] = Field(default=..., description="The access level to assign to the user groups. Choose from: VIEWER (read-only access), COMMENTER (read and comment), or EDITOR (full edit access). Defaults to VIEWER if not specified.")
class EnterpriseProjectCreateGroupRequest(StrictModel):
    """Grant user groups access to a project with a specified role. If a group already has access, this operation updates their role assignment."""
    path: EnterpriseProjectCreateGroupRequestPath
    body: EnterpriseProjectCreateGroupRequestBody

# Operation: remove_group_from_project
class EnterpriseProjectDeleteGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The organization ID that contains the project. Use the numeric organization identifier.")
    project_id: str = Field(default=..., description="The project ID from which to remove the group. Use the numeric project identifier.")
    group_id: str = Field(default=..., description="The user group ID to remove from the project. Use the numeric group identifier.")
class EnterpriseProjectDeleteGroupsRequest(StrictModel):
    """Remove a user group from a project. This operation unassigns the specified group from the project, revoking group members' access to the project resources."""
    path: EnterpriseProjectDeleteGroupsRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AppCardStyle(PermissiveModel):
    """Contains information about the style of an app card item, such as the fill color."""
    fill_color: str | None = Field(None, validation_alias="fillColor", serialization_alias="fillColor", description="Hex value of the border color of the app card.\nDefault: `#2d9bf0`.")

class BoardMember(PermissiveModel):
    """Contains the current user's board membership details. The current user could be different from the board owner."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the user.")
    name: str = Field(..., description="Name of the user.")
    role: Literal["viewer", "commenter", "editor", "coowner", "owner"] | None = Field(None, description="Role of the board member.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of the object that is returned. In this case, `type` returns `board_member`.")

class BoardPermissionsPolicy(PermissiveModel):
    """Defines the permissions policies for the board."""
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field('all_editors', validation_alias="collaborationToolsStartAccess", serialization_alias="collaborationToolsStartAccess", description="Defines who can start or stop timer, voting, video chat, screen sharing, attention management. Others will only be able to join. To change the value for the `collaborationToolsStartAccess` parameter, contact Miro Customer Support.")
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field('anyone', validation_alias="copyAccess", serialization_alias="copyAccess", description="Defines who can copy the board, copy objects, download images, and save the board as a template or PDF.")
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field('team_members_with_editing_rights', validation_alias="sharingAccess", serialization_alias="sharingAccess", description="Defines who can change access and invite users to this board. To change the value for the `sharingAccess` parameter, contact Miro Customer Support.")

class BoardProject(PermissiveModel):
    """Contains information about the project with which the board is associated."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the project.", json_schema_extra={'format': 'int64'})

class BoardSharingPolicy(PermissiveModel):
    """Defines the public-level, organization-level, and team-level access for the board. The access level that a user gets depends on the highest level of access that results from considering the public-level, team-level, organization-level, and direct sharing access."""
    access: Literal["private", "view", "edit", "comment"] | None = Field(None, description="Defines the public-level access to the board.")
    access_password_required: bool | None = Field(False, validation_alias="accessPasswordRequired", serialization_alias="accessPasswordRequired", description="Defines if a password is required to access the board.")
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "coowner", "owner", "guest", "no_access"] | None = Field('no_access', validation_alias="inviteToAccountAndBoardLinkAccess", serialization_alias="inviteToAccountAndBoardLinkAccess", description="Defines the user role when inviting a user via the invite to team and board link. For Enterprise users, the `inviteToAccountAndBoardLinkAccess` parameter is always set to `no_access`.")
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field('private', validation_alias="organizationAccess", serialization_alias="organizationAccess", description="Defines the organization-level access to the board. If the board is created for a team that does not belong to an organization, the `organizationAccess` parameter is always set to the default value.")
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(None, validation_alias="teamAccess", serialization_alias="teamAccess", description="Defines the team-level access to the board.")

class BoardPolicy(PermissiveModel):
    """Defines the permissions policies and sharing policies for the board."""
    permissions_policy: BoardPermissionsPolicy | None = Field(None, validation_alias="permissionsPolicy", serialization_alias="permissionsPolicy")
    sharing_policy: BoardSharingPolicy | None = Field(None, validation_alias="sharingPolicy", serialization_alias="sharingPolicy")

class Caption(PermissiveModel):
    """Contains the connector's caption data, such as content and its position."""
    content: str = Field(..., description="The text you want to display on the connector. Supports inline HTML tags.", min_length=0, max_length=200)
    position: str | None = Field(None, description="The relative position of the text on the connector, in percentage, minimum 0%, maximum 100%. With 50% value, the text will be placed in the middle of the connector line. Default: 50%")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="The vertical position of the text on the connector. Default: middle")

class CardData(PermissiveModel):
    """Contains card item data, such as the title, description, due date, or assignee ID."""
    assignee_id: str | None = Field(None, validation_alias="assigneeId", serialization_alias="assigneeId", description="Unique user identifier. In the GUI, the user ID is mapped to the name of the user who is assigned as the owner of the task or activity described in the card. The identifier is numeric, and it is automatically assigned to a user when they first sign up.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(None, description="A short text description to add context about the card.")
    due_date: str | None = Field(None, validation_alias="dueDate", serialization_alias="dueDate", description="The date when the task or activity described in the card is due to be completed. In the GUI, users can select the due date from a calendar. Format: UTC, adheres to [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), includes a [trailing Z offset](https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)).", json_schema_extra={'format': 'date-time'})
    title: str | None = Field(None, description="A short text header for the card.")

class CardStyle(PermissiveModel):
    """Contains information about the style of a card item, such as the card theme."""
    card_theme: str | None = Field(None, validation_alias="cardTheme", serialization_alias="cardTheme", description="Hex value of the border color of the card.\nDefault: `#2d9bf0`.")

class CreateUserBodyPhotosItem(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")
    value: str | None = None

class CreateUserBodyRolesItem(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the role. Supported values are organization_user_role and organization_admin_role. Only one role should in the same array can have type `organization_user_role`.")
    value: str | None = Field(None, description="The role assigned to the user. <br> For `organization_user_role` type, supported values include: ORGANIZATION_INTERNAL_ADMIN and ORGANIZATION_INTERNAL_USER. <br> For `organization_admin_role` type, supported values include: Content Admin, User Admin, Security Admin, or names of custom admin roles.")
    display: str | None = Field(None, description="A human-readable name or description of the role.")
    primary: bool | None = Field(None, description="Indicates whether this role is the primary role. Only one role can be marked as primary.")

class CreatedBy(PermissiveModel):
    """Contains information about the user who created the item."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the user.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Indicates the type of object returned. In this case, `type` returns `user`.")

class CustomField(PermissiveModel):
    """Array where each object represents a custom preview field. Preview fields are displayed on the bottom half of the app card in the compact view."""
    fill_color: str | None = Field(None, validation_alias="fillColor", serialization_alias="fillColor", description="Hex value representing the color that fills the background area of the preview field, when it's displayed on the app card.")
    icon_shape: Literal["round", "square"] | None = Field('round', validation_alias="iconShape", serialization_alias="iconShape", description="The shape of the icon on the preview field.")
    icon_url: str | None = Field(None, validation_alias="iconUrl", serialization_alias="iconUrl", description="A valid URL pointing to an image available online.\nThe transport protocol must be HTTPS.\nPossible image file formats: JPG/JPEG, PNG, SVG.")
    text_color: str | None = Field(None, validation_alias="textColor", serialization_alias="textColor", description="Hex value representing the color of the text string assigned to `value`.")
    tooltip: str | None = Field(None, description="A short text displayed in a tooltip when clicking or hovering over the preview field.")
    value: str | None = Field(None, description="The actual data value of the custom field.\nIt can be any type of information that you want to convey.")

class AppCardData(PermissiveModel):
    """Contains app card item data, such as the title, description, or fields."""
    description: str | None = Field(None, description="A short text description to add context about the app card.")
    fields: list[CustomField] | None = Field(None, description="Array where each object represents a custom preview field. Preview fields are displayed on the bottom half of the app card in the compact view.")
    owned: bool | None = Field(None, description="Defines whether the card is owned by the application making the call.")
    status: Literal["disconnected", "connected", "disabled"] | None = Field(None, description="Status indicating whether an app card is connected and in sync with the source. When the source for the app card is deleted, the status returns `disabled`.")
    title: str | None = Field(None, description="A short text header to identify the app card.")

class DocumentDataResponse(PermissiveModel):
    document_url: str | None = Field(None, validation_alias="documentUrl", serialization_alias="documentUrl", description="The URL to download the resource. You must use your access token to access the URL. The URL contains the `redirect` parameter to control the request execution.\n`redirect`: By default, the `redirect` parameter is set to `false` and the resource object containing the URL and the resource type is returned with a 200 OK HTTP code. This URL is valid for 60 seconds. You can use this URL to retrieve the resource file.\nIf the `redirect` parameter is set to `true`, a 307 TEMPORARY_REDIRECT HTTP response is returned. If you follow HTTP 3xx responses as redirects, you will automatically be redirected to the resource file and the content type returned is `application/octet-stream`.")
    title: str | None = Field(None, description="A short text header to identify the document.")

class DocumentUrlData(PermissiveModel):
    """Contains information about the document URL."""
    title: str | None = Field(None, description="A short text header to identify the document.")
    url: str = Field(..., description="URL where the document is hosted.")

class EmbedUrlData(PermissiveModel):
    """Contains information about the embed URL."""
    mode: Literal["inline", "modal"] | None = Field(None, description="Defines how the content in the embed item is displayed on the board.\n`inline`: The embedded content is displayed directly on the board.\n`modal`: The embedded content is displayed inside a modal overlay on the board.")
    preview_url: str | None = Field(None, validation_alias="previewUrl", serialization_alias="previewUrl", description="URL of the image to be used as the preview image for the embedded item.")
    url: str = Field(..., description="A [valid URL](https://developers.miro.com/reference/data#embeddata) pointing to the content resource that you want to embed in the board. Possible transport protocols: HTTP, HTTPS.")

class Geometry(PermissiveModel):
    """Contains geometrical information about the item, such as its width or height."""
    height: float | None = Field(None, description="Height of the item, in pixels.", json_schema_extra={'format': 'double'})
    rotation: float | None = Field(None, description="Rotation angle of an item, in degrees, relative to the board. You can rotate items clockwise (right) and counterclockwise (left) by specifying positive and negative values, respectively.", json_schema_extra={'format': 'double'})
    width: float | None = Field(None, description="Width of the item, in pixels.", json_schema_extra={'format': 'double'})

class Group(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="User group ID")
    name: str = Field(..., description="User group name")
    description: str | None = Field(None, description="User group description")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Object type")

class ImageDataResponse(PermissiveModel):
    image_url: str | None = Field(None, validation_alias="imageUrl", serialization_alias="imageUrl", description="The URL to download the resource. You must use your access token to access the URL. The URL contains the `redirect` parameter and the `format` parameter to control the request execution as described in the following parameters: `format` parameter: By default, the image format is set to the preview image. If you want to download the original image, set the `format` parameter in the URL to `original`. `redirect`: By default, the `redirect` parameter is set to `false` and the resource object containing the URL and the resource type is returned with a 200 OK HTTP code. This URL is valid for 60 seconds. You can use this URL to retrieve the resource file. If the `redirect` parameter is set to `true`, a 307 TEMPORARY_REDIRECT HTTP response is returned. If you follow HTTP 3xx responses as redirects, you will automatically be redirected to the resource file and the content type returned can be `image/png`, 'image/svg', or 'image/jpg', depending on the original image type.")
    title: str | None = Field(None, description="A short text header to identify the image.")

class ImageUrlData(PermissiveModel):
    """Contains information about the image URL."""
    title: str | None = Field(None, description="A short text header to identify the image.")
    url: str = Field(..., description="URL of the image.")

class LegalHoldRequestScopeUsersUsersItem(PermissiveModel):
    email: str = Field(..., description="Email of the user")

class LegalHoldRequestScopeUsers(PermissiveModel):
    users: list[LegalHoldRequestScopeUsersUsersItem] | None = None

class ModifiedBy(PermissiveModel):
    """Contains information about the user who last modified the item."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the user.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Indicates the type of object returned. In this case, `type` returns `user`.")

class Organization(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Id of the organization")
    full_licenses_purchased: int = Field(..., validation_alias="fullLicensesPurchased", serialization_alias="fullLicensesPurchased", description="Purchased FULL licenses", json_schema_extra={'format': 'int32'})
    name: str = Field(..., description="Name of the organization")
    plan: Literal["company", "consultant", "consultant_slf", "business", "paid_team_org", "integration_org", "professional_2022", "edu_team_org", "free_team_org", "dev_team_org", "unknown"] = Field(..., description="Organization plan type")
    type_: str | None = Field('organization', validation_alias="type", serialization_alias="type", description="Type of the object returned.")

class Parent(PermissiveModel):
    """Contains information about the parent frame for the item."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the parent frame for the item.", json_schema_extra={'format': 'int64'})

class PatchGroupBodyOperationsItemValueV0Item(PermissiveModel):
    value: str = Field(..., description="A server-assigned, unique identifier for the user to be added, removed, or replaced.")

class PatchGroupBodyOperationsItem(PermissiveModel):
    op: Literal["Add", "Remove", "Replace"] = Field(..., description="Supported operations for this Patch request.")
    path: Literal["members", "displayName"] | None = Field(None, description="The \"path\" attribute value is a string containing an attribute path describing the target of the operation. The \"path\" attribute is optional for the \"add\", and \"replace\" operations and is required for the \"remove\" operation. <br><br> ")
    value: list[PatchGroupBodyOperationsItemValueV0Item] | str | None = None

class PatchUserBodyOperationsItem(PermissiveModel):
    op: Literal["Add", "Remove", "Replace"] = Field(..., description="The operation to perform.")
    path: str = Field(..., description="Attribute path being modified.")
    value: str = Field(..., description="The value to apply in the operation.")

class Picture(PermissiveModel):
    id_: float | None = Field(None, validation_alias="id", serialization_alias="id", description="Id of the picture", json_schema_extra={'format': 'int64'})
    image_url: str | None = Field(None, validation_alias="imageURL", serialization_alias="imageURL", description="Url of the picture")
    original_url: str | None = Field(None, validation_alias="originalUrl", serialization_alias="originalUrl", description="Original team picture url for icon generation")
    type_: str | None = Field('picture', validation_alias="type", serialization_alias="type", description="Type of the object returned.")

class Position(PermissiveModel):
    """Contains location information about the item, such as its x coordinate, y coordinate, and the origin of the x and y coordinates."""
    origin: Literal["center"] | None = Field('center', description="Area of the item that is referenced by its x and y coordinates. For example, an item with a center origin will have its x and y coordinates point to its center. The center point of the board has x: 0 and y: 0 coordinates.\nCurrently, only one option is supported.")
    relative_to: Literal["canvas_center", "parent_top_left"] | None = Field(None, validation_alias="relativeTo", serialization_alias="relativeTo")
    x: float | None = Field(None, description="X-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: 0.\nThe center point of the board has `x: 0` and `y: 0` coordinates.", json_schema_extra={'format': 'double'})
    y: float | None = Field(None, description="Y-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: 0.\nThe center point of the board has `x: 0` and `y: 0` coordinates.", json_schema_extra={'format': 'double'})

class PositionChange(PermissiveModel):
    """Contains information about the item's position on the board, such as its `x` coordinate, `y` coordinate, and the origin of the `x` and `y` coordinates."""
    x: float | None = Field(0, description="X-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: `0`.\nThe center point of the board has `x: 0` and `y: 0` coordinates.", json_schema_extra={'format': 'double'})
    y: float | None = Field(0, description="Y-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: `0`.\nThe center point of the board has `x: 0` and `y: 0` coordinates.", json_schema_extra={'format': 'double'})

class ReplaceUserBodyEmailsItem(PermissiveModel):
    value: str | None = Field(None, description="E-mail addresses for the user")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A label that identifies the type of email address.")
    primary: bool | None = Field(None, description="Indicates the user's primary email address. Only one item in the list should have primary set to true.")

class ReplaceUserBodyGroupsItem(PermissiveModel):
    value: str | None = Field(None, description="The unique ID of the group.")
    display: str | None = Field(None, description="Human-readable name of the group.")

class ReplaceUserBodyPhotosItem(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Indicates the type of photo.")
    value: str | None = Field(None, description="The URL of the image")

class ReplaceUserBodyRolesItem(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the role. Supported values are organization_user_role and organization_admin_role. Only one role should have type organization_user_role.")
    value: str | None = Field(None, description="The role assigned to the user. <br> For `organization_user_role` type, supported values include: ORGANIZATION_INTERNAL_ADMIN and ORGANIZATION_INTERNAL_USER. <br> For `organization_admin_role` type, supported values include: Content Admin, User Admin, Security Admin, or names of custom admin roles.")
    display: str | None = Field(None, description="A human-readable name or description of the role.")
    primary: bool | None = Field(None, description="Indicates whether this role is the primary role. Only one role can be marked as primary.")

class SelfLink(PermissiveModel):
    """Contains applicable links for the current object."""
    self: str | None = Field(None, description="Link to obtain more information about the current object.")

class ParentWithLinks(PermissiveModel):
    """Contains information about the parent this item attached to."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of a container item.", json_schema_extra={'format': 'int64'})
    links: SelfLink | None = None

class Item(PermissiveModel):
    """Contains information about an item."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of item.")
    data: DocumentDataResponse | ImageDataResponse | None = None
    position: Position | None = None
    geometry: Geometry | None = None
    parent: ParentWithLinks | None = None
    created_by: CreatedBy | None = Field(None, validation_alias="createdBy", serialization_alias="createdBy")
    created_at: str | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt")
    modified_by: ModifiedBy | None = Field(None, validation_alias="modifiedBy", serialization_alias="modifiedBy")
    modified_at: str | None = Field(None, validation_alias="modifiedAt", serialization_alias="modifiedAt")
    links: SelfLink

class Items(PermissiveModel):
    """Contains items resulting from a bulk create or update operation."""
    data: list[Item] = Field(..., description="Contains the result data.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of the object.")

class ShapeData(PermissiveModel):
    """Contains shape item data, such as the content or shape type of the shape."""
    content: str | None = Field(None, description="The text you want to display on the shape.")
    shape: Literal["rectangle", "round_rectangle", "circle", "triangle", "rhombus", "parallelogram", "trapezoid", "pentagon", "hexagon", "octagon", "wedge_round_rectangle_callout", "star", "flow_chart_predefined_process", "cloud", "cross", "can", "right_arrow", "left_arrow", "left_right_arrow", "left_brace", "right_brace"] | None = Field('rectangle', description="Defines the geometric shape of the item when it is rendered on the board.")

class ShapeStyle(PermissiveModel):
    """Contains information about the shape style, such as the border color or opacity."""
    border_color: str | None = Field(None, validation_alias="borderColor", serialization_alias="borderColor", description="Defines the color of the border of the shape.\nDefault: `#1a1a1a` (dark gray).")
    border_opacity: str | None = Field(None, validation_alias="borderOpacity", serialization_alias="borderOpacity", description="Defines the opacity level of the shape border.\nPossible values: any number between `0.0` and `1.0`, where:\n`0.0`: the background color is completely transparent or invisible\n`1.0`: the background color is completely opaque or solid\nDefault: `1.0` (solid color).", ge=0, le=1)
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(None, validation_alias="borderStyle", serialization_alias="borderStyle", description="Defines the style used to represent the border of the shape.\nDefault: `normal`.")
    border_width: str | None = Field(None, validation_alias="borderWidth", serialization_alias="borderWidth", description="Defines the thickness of the shape border, in dp.\nDefault: `2.0`.", ge=1, le=24)
    color: str | None = Field(None, description="Hex value representing the color for the text within the shape item.\nDefault: `#1a1a1a`.")
    fill_color: str | None = Field(None, validation_alias="fillColor", serialization_alias="fillColor", description="Fill color for the shape.\nHex values: `#f5f6f8` `#d5f692` `#d0e17a` `#93d275` `#67c6c0` `#23bfe7` `#a6ccf5` `#7b92ff` `#fff9b1` `#f5d128` `#ff9d48` `#f16c7f` `#ea94bb` `#ffcee0` `#b384bb` `#000000`\nDefault: #ffffff.")
    fill_opacity: str | None = Field(None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="Opacity level of the fill color.\nPossible values: any number between `0` and `1`, where:\n`0.0`: the background color is completely transparent or invisible.\n`1.0`: the background color is completely opaque or solid.\n\n Default: `1.0` if `fillColor` is provided, `0.0` if `fillColor` is not provided.\n", ge=0, le=1)
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Defines the font type for the text in the shape item.\nDefault: `arial`.")
    font_size: str | None = Field(None, validation_alias="fontSize", serialization_alias="fontSize", description="Defines the font size, in dp, for the text on the shape.\nDefault: `14`.", ge=10, le=288)
    text_align: Literal["left", "right", "center"] | None = Field(None, validation_alias="textAlign", serialization_alias="textAlign", description="Defines how the sticky note text is horizontally aligned.\nDefault: `center`.")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="Defines how the sticky note text is vertically aligned.\nDefault: `top`.")

class StickyNoteData(PermissiveModel):
    """Contains sticky note item data, such as the content or shape of the sticky note."""
    content: str | None = Field(None, description="The actual text (content) that appears in the sticky note item.")
    shape: Literal["square", "rectangle"] | None = Field('square', description="Defines the geometric shape of the sticky note and aspect ratio for its dimensions.")

class StickyNoteStyle(PermissiveModel):
    """Contains information about the style of a sticky note item, such as the fill color or text alignment."""
    fill_color: Literal["gray", "light_yellow", "yellow", "orange", "light_green", "green", "dark_green", "cyan", "light_pink", "pink", "violet", "red", "light_blue", "blue", "dark_blue", "black"] | None = Field(None, validation_alias="fillColor", serialization_alias="fillColor", description="Fill color for the sticky note.\nDefault: `light_yellow`.")
    text_align: Literal["left", "right", "center"] | None = Field(None, validation_alias="textAlign", serialization_alias="textAlign", description="Defines how the sticky note text is horizontally aligned.\nDefault: `center`.")
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, validation_alias="textAlignVertical", serialization_alias="textAlignVertical", description="Defines how the sticky note text is vertically aligned.\nDefault: `top`.")

class Tag(PermissiveModel):
    fill_color: Literal["red", "light_green", "cyan", "yellow", "magenta", "green", "blue", "gray", "violet", "dark_green", "dark_blue", "black"] = Field(..., validation_alias="fillColor", serialization_alias="fillColor", description="Background color of the tag.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the tag.")
    title: str = Field(..., description="Text of the tag.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of the object that is returned. In this case, type returns `tag`.")

class Team(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Team id")
    name: str = Field(..., description="Team name")
    picture: Picture | None = None
    type_: str | None = Field('team', validation_alias="type", serialization_alias="type", description="Type of the object returned.")

class TextData(PermissiveModel):
    """Contains text item data, such as the title, content, or description. For more information on the JSON properties, see [Data](https://developers.miro.com/reference/data)."""
    content: str = Field(..., description="The actual text (content) that appears in the text item.")

class TextStyle(PermissiveModel):
    """Contains information about the style of a text item, such as the fill color or font family."""
    color: str | None = Field(None, description="Hex value representing the color for the text within the text item.\nDefault: `#1a1a1a`.")
    fill_color: str | None = Field(None, validation_alias="fillColor", serialization_alias="fillColor", description="Background color of the text item.\nDefault: `#ffffff`.")
    fill_opacity: str | None = Field(None, validation_alias="fillOpacity", serialization_alias="fillOpacity", description="Opacity level of the background color.\nPossible values: any number between `0.0` and `1.0`, where:\n`0.0`: the background color is completely transparent or invisible.\n`1.0`: the background color is completely opaque or solid.\nDefault: `1.0` if `fillColor` is provided, `0.0` if `fillColor` is not provided.", ge=0, le=1)
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Font type for the text in the text item.\nDefault: `arial`.")
    font_size: str | None = Field(None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size, in dp.\nDefault: `14`.", ge=1)
    text_align: Literal["left", "right", "center"] | None = Field(None, validation_alias="textAlign", serialization_alias="textAlign", description="Horizontal alignment for the item's content.\nDefault: `center.`")

class ItemCreate(PermissiveModel):
    """Creates one or more items in one request. You can create up to 20 items per request."""
    type_: Literal["app_card", "text", "shape", "sticky_note", "image", "document", "card", "frame", "embed"] = Field(..., validation_alias="type", serialization_alias="type")
    data: AppCardData | CardData | DocumentUrlData | EmbedUrlData | ImageUrlData | ShapeData | StickyNoteData | TextData | None = None
    style: AppCardStyle | CardStyle | ShapeStyle | StickyNoteStyle | TextStyle | None = None
    position: PositionChange | None = None
    geometry: Geometry | None = None
    parent: Parent | None = None

class User(PermissiveModel):
    """User information."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the user.")
    email: str = Field(..., description="User email.")
    first_name: str = Field(..., validation_alias="firstName", serialization_alias="firstName", description="First name of the user.")
    last_name: str = Field(..., validation_alias="lastName", serialization_alias="lastName", description="Last name of the user.")

class UserInfoLastOpenedBy(PermissiveModel):
    """Contains information about the user who opened the board last."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the user.")
    name: str | None = Field(None, description="Name of the user.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Indicates the type of object returned. In this case, `type` returns `user`.")

class UserInfoShort(PermissiveModel):
    """Contains information about the user who created the board."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the user.")
    name: str = Field(..., description="Name of the user.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Indicates the type of object returned. In this case, `type` returns `user`.")

class Board(PermissiveModel):
    """Contains the result data."""
    created_at: str | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt", description="Date and time when the board was created. Format: UTC, adheres to [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), includes a [trailing Z offset](https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)).", json_schema_extra={'format': 'date-time'})
    created_by: UserInfoShort | None = Field(None, validation_alias="createdBy", serialization_alias="createdBy")
    current_user_membership: BoardMember | None = Field(None, validation_alias="currentUserMembership", serialization_alias="currentUserMembership")
    description: str = Field(..., description="Description of the board.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier (ID) of the board.")
    last_opened_at: str | None = Field(None, validation_alias="lastOpenedAt", serialization_alias="lastOpenedAt", description="Date and time when the board was last opened by any user. Format: UTC, adheres to [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), includes a [trailing Z offset](https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)).", json_schema_extra={'format': 'date-time'})
    last_opened_by: UserInfoLastOpenedBy | None = Field(None, validation_alias="lastOpenedBy", serialization_alias="lastOpenedBy")
    modified_at: str | None = Field(None, validation_alias="modifiedAt", serialization_alias="modifiedAt", description="Date and time when the board was last modified. Format: UTC, adheres to [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), includes a [trailing Z offset](https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)).", json_schema_extra={'format': 'date-time'})
    modified_by: UserInfoShort | None = Field(None, validation_alias="modifiedBy", serialization_alias="modifiedBy")
    name: str = Field(..., description="Name of the board.")
    owner: UserInfoShort | None = None
    picture: Picture | None = None
    policy: BoardPolicy | None = None
    team: Team | None = None
    project: BoardProject | None = None
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of the object that is returned. In this case, type returns `board`.")
    view_link: str | None = Field(None, validation_alias="viewLink", serialization_alias="viewLink", description="URL to view the board.")


# Rebuild models to resolve forward references (required for circular refs)
AppCardData.model_rebuild()
AppCardStyle.model_rebuild()
Board.model_rebuild()
BoardMember.model_rebuild()
BoardPermissionsPolicy.model_rebuild()
BoardPolicy.model_rebuild()
BoardProject.model_rebuild()
BoardSharingPolicy.model_rebuild()
Caption.model_rebuild()
CardData.model_rebuild()
CardStyle.model_rebuild()
CreatedBy.model_rebuild()
CreateUserBodyPhotosItem.model_rebuild()
CreateUserBodyRolesItem.model_rebuild()
CustomField.model_rebuild()
DocumentDataResponse.model_rebuild()
DocumentUrlData.model_rebuild()
EmbedUrlData.model_rebuild()
Geometry.model_rebuild()
Group.model_rebuild()
ImageDataResponse.model_rebuild()
ImageUrlData.model_rebuild()
Item.model_rebuild()
ItemCreate.model_rebuild()
Items.model_rebuild()
LegalHoldRequestScopeUsers.model_rebuild()
LegalHoldRequestScopeUsersUsersItem.model_rebuild()
ModifiedBy.model_rebuild()
Organization.model_rebuild()
Parent.model_rebuild()
ParentWithLinks.model_rebuild()
PatchGroupBodyOperationsItem.model_rebuild()
PatchGroupBodyOperationsItemValueV0Item.model_rebuild()
PatchUserBodyOperationsItem.model_rebuild()
Picture.model_rebuild()
Position.model_rebuild()
PositionChange.model_rebuild()
ReplaceUserBodyEmailsItem.model_rebuild()
ReplaceUserBodyGroupsItem.model_rebuild()
ReplaceUserBodyPhotosItem.model_rebuild()
ReplaceUserBodyRolesItem.model_rebuild()
SelfLink.model_rebuild()
ShapeData.model_rebuild()
ShapeStyle.model_rebuild()
StickyNoteData.model_rebuild()
StickyNoteStyle.model_rebuild()
Tag.model_rebuild()
Team.model_rebuild()
TextData.model_rebuild()
TextStyle.model_rebuild()
User.model_rebuild()
UserInfoLastOpenedBy.model_rebuild()
UserInfoShort.model_rebuild()

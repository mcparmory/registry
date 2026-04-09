"""
Atlassian Jira MCP Server - Pydantic Models

Generated: 2026-04-09 12:10:21 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import AfterValidator, Field, RootModel


def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v


__all__ = [
    "AddActorUsersRequest",
    "AddAtlassianTeamRequest",
    "AddAttachmentRequest",
    "AddCommentRequest",
    "AddSharePermissionRequest",
    "AddUserToGroupRequest",
    "AddVoteRequest",
    "AddWatcherRequest",
    "AddWorklogRequest",
    "ArchiveIssuesAsyncRequest",
    "ArchiveIssuesRequest",
    "ArchivePlanRequest",
    "ArchiveProjectRequest",
    "AssignIssueRequest",
    "BulkDeleteIssuePropertyRequest",
    "BulkDeleteWorklogsRequest",
    "BulkEditDashboardsRequest",
    "BulkFetchIssuesRequest",
    "BulkGetGroupsRequest",
    "BulkGetUsersMigrationRequest",
    "BulkGetUsersRequest",
    "BulkMoveWorklogsRequest",
    "BulkSetIssuePropertiesByIssueRequest",
    "BulkSetIssuePropertyRequest",
    "BulkSetIssuesPropertiesListRequest",
    "CancelTaskRequest",
    "ChangeFilterOwnerRequest",
    "CopyDashboardRequest",
    "CountIssuesRequest",
    "CreateComponentRequest",
    "CreateCustomFieldOptionRequest",
    "CreateDashboardRequest",
    "CreateFilterRequest",
    "CreateGroupRequest",
    "CreateIssueFieldOptionRequest",
    "CreateIssueRequest",
    "CreateIssuesRequest",
    "CreateIssueTypeAvatarRequest",
    "CreateOrUpdateRemoteIssueLinkRequest",
    "CreatePlanOnlyTeamRequest",
    "CreatePlanRequest",
    "CreateProjectAvatarRequest",
    "CreateProjectCategoryRequest",
    "CreateProjectRequest",
    "CreateProjectWithCustomTemplateRequest",
    "CreateRelatedWorkRequest",
    "CreateUserRequest",
    "CreateVersionRequest",
    "DeleteActorRequest",
    "DeleteAndReplaceVersionRequest",
    "DeleteAvatarRequest",
    "DeleteCommentPropertyRequest",
    "DeleteCommentRequest",
    "DeleteComponentRequest",
    "DeleteCustomFieldOptionRequest",
    "DeleteCustomFieldRequest",
    "DeleteDashboardItemPropertyRequest",
    "DeleteDashboardRequest",
    "DeleteFavouriteForFilterRequest",
    "DeleteFilterRequest",
    "DeleteIssueLinkRequest",
    "DeleteIssueLinkTypeRequest",
    "DeleteIssuePropertyRequest",
    "DeleteIssueRequest",
    "DeleteIssueTypeRequest",
    "DeletePlanOnlyTeamRequest",
    "DeletePriorityRequest",
    "DeleteProjectAsynchronouslyRequest",
    "DeleteProjectAvatarRequest",
    "DeleteProjectPropertyRequest",
    "DeleteProjectRequest",
    "DeleteProjectRoleRequest",
    "DeleteRelatedWorkRequest",
    "DeleteRemoteIssueLinkByIdRequest",
    "DeleteResolutionRequest",
    "DeleteSharePermissionRequest",
    "DeleteStatusesByIdRequest",
    "DeleteUserPropertyRequest",
    "DeleteWorklogPropertyRequest",
    "DeleteWorklogRequest",
    "DoTransitionRequest",
    "DuplicatePlanRequest",
    "EditIssueRequest",
    "EvaluateJsisJiraExpressionRequest",
    "ExpandAttachmentForHumansRequest",
    "ExpandAttachmentForMachinesRequest",
    "ExportArchivedIssuesRequest",
    "FindAssignableUsersRequest",
    "FindBulkAssignableUsersRequest",
    "FindComponentsForProjectsRequest",
    "FindGroupsRequest",
    "FindUserKeysByQueryRequest",
    "FindUsersAndGroupsRequest",
    "FindUsersByQueryRequest",
    "FindUsersForPickerRequest",
    "FindUsersRequest",
    "FindUsersWithAllPermissionsRequest",
    "FindUsersWithBrowsePermissionRequest",
    "FullyUpdateProjectRoleRequest",
    "GetAccessibleProjectTypeByKeyRequest",
    "GetAllDashboardsRequest",
    "GetAllIssueFieldOptionsRequest",
    "GetAllIssueTypeSchemesRequest",
    "GetAllLabelsRequest",
    "GetAllProjectAvatarsRequest",
    "GetAllStatusesRequest",
    "GetAllSystemAvatarsRequest",
    "GetAllUserDataClassificationLevelsRequest",
    "GetAllUsersDefaultRequest",
    "GetAllUsersRequest",
    "GetAlternativeIssueTypesRequest",
    "GetAtlassianTeamRequest",
    "GetAttachmentContentRequest",
    "GetAttachmentRequest",
    "GetAttachmentThumbnailRequest",
    "GetAutoCompletePostRequest",
    "GetAvailablePrioritiesByPrioritySchemeRequest",
    "GetAvailableScreenFieldsRequest",
    "GetAvailableTransitionsRequest",
    "GetAvatarImageByIdRequest",
    "GetAvatarImageByOwnerRequest",
    "GetAvatarsRequest",
    "GetBulkChangelogsRequest",
    "GetBulkEditableFieldsRequest",
    "GetBulkOperationProgressRequest",
    "GetBulkPermissionsRequest",
    "GetChangeLogsByIdsRequest",
    "GetChangeLogsRequest",
    "GetColumnsRequest",
    "GetCommentPropertyKeysRequest",
    "GetCommentPropertyRequest",
    "GetCommentRequest",
    "GetCommentsByIdsRequest",
    "GetCommentsRequest",
    "GetComponentRelatedIssuesRequest",
    "GetComponentRequest",
    "GetCreateIssueMetaIssueTypeIdRequest",
    "GetCreateIssueMetaIssueTypesRequest",
    "GetCustomFieldOptionRequest",
    "GetDashboardItemPropertyKeysRequest",
    "GetDashboardItemPropertyRequest",
    "GetDashboardRequest",
    "GetDashboardsPaginatedRequest",
    "GetDefaultProjectClassificationRequest",
    "GetEditIssueMetaRequest",
    "GetFeaturesForProjectRequest",
    "GetFieldAutoCompleteForQueryStringRequest",
    "GetFieldsPaginatedRequest",
    "GetFilterRequest",
    "GetFiltersPaginatedRequest",
    "GetHierarchyRequest",
    "GetIdsOfWorklogsDeletedSinceRequest",
    "GetIdsOfWorklogsModifiedSinceRequest",
    "GetIssueFieldOptionRequest",
    "GetIssueLimitReportRequest",
    "GetIssueLinkRequest",
    "GetIssueLinkTypeRequest",
    "GetIssuePickerResourceRequest",
    "GetIssuePropertyKeysRequest",
    "GetIssuePropertyRequest",
    "GetIssueRequest",
    "GetIssueSecurityLevelRequest",
    "GetIssueTypeMappingsForContextsRequest",
    "GetIssueTypePropertyKeysRequest",
    "GetIssueTypePropertyRequest",
    "GetIssueTypeRequest",
    "GetIssueTypeSchemeForProjectsRequest",
    "GetIssueTypesForProjectRequest",
    "GetIssueWatchersRequest",
    "GetIssueWorklogRequest",
    "GetIsWatchingIssueBulkRequest",
    "GetMyFiltersRequest",
    "GetMyPermissionsRequest",
    "GetNotificationSchemeToProjectMappingsRequest",
    "GetOptionsForContextRequest",
    "GetPermittedProjectsRequest",
    "GetPlanOnlyTeamRequest",
    "GetPlanRequest",
    "GetPlansRequest",
    "GetPreferenceRequest",
    "GetPrioritiesByPrioritySchemeRequest",
    "GetPriorityRequest",
    "GetProjectCategoryByIdRequest",
    "GetProjectComponentsPaginatedRequest",
    "GetProjectComponentsRequest",
    "GetProjectEmailRequest",
    "GetProjectFieldsRequest",
    "GetProjectIssueTypeUsagesForStatusRequest",
    "GetProjectPropertyKeysRequest",
    "GetProjectPropertyRequest",
    "GetProjectRequest",
    "GetProjectRoleByIdRequest",
    "GetProjectRoleDetailsRequest",
    "GetProjectRoleRequest",
    "GetProjectRolesRequest",
    "GetProjectTypeByKeyRequest",
    "GetProjectUsagesForStatusRequest",
    "GetProjectUsagesForWorkflowRequest",
    "GetProjectUsagesForWorkflowSchemeRequest",
    "GetProjectVersionsPaginatedRequest",
    "GetProjectVersionsRequest",
    "GetRelatedWorkRequest",
    "GetRemoteIssueLinkByIdRequest",
    "GetRemoteIssueLinksRequest",
    "GetResolutionRequest",
    "GetScreensForFieldRequest",
    "GetSecurityLevelsForProjectRequest",
    "GetSelectableIssueFieldOptionsRequest",
    "GetSharePermissionRequest",
    "GetSharePermissionsRequest",
    "GetStatusCategoryRequest",
    "GetStatusesByIdRequest",
    "GetStatusesByNameRequest",
    "GetStatusRequest",
    "GetTaskRequest",
    "GetTeamsRequest",
    "GetTransitionsRequest",
    "GetTrashedFieldsPaginatedRequest",
    "GetUserGroupsRequest",
    "GetUserPropertyKeysRequest",
    "GetUserPropertyRequest",
    "GetUserRequest",
    "GetUsersFromGroupRequest",
    "GetValidProjectNameRequest",
    "GetVersionRelatedIssuesRequest",
    "GetVersionRequest",
    "GetVersionUnresolvedIssuesRequest",
    "GetVisibleIssueFieldOptionsRequest",
    "GetVotesRequest",
    "GetWorkflowProjectIssueTypeUsagesRequest",
    "GetWorkflowSchemeProjectAssociationsRequest",
    "GetWorkflowUsagesForStatusRequest",
    "GetWorklogPropertyKeysRequest",
    "GetWorklogPropertyRequest",
    "GetWorklogRequest",
    "GetWorklogsForIdsRequest",
    "LinkIssuesRequest",
    "ListWorkflowHistoryRequest",
    "MatchIssuesRequest",
    "MergeVersionsRequest",
    "MoveVersionRequest",
    "NotifyRequest",
    "ParseJqlQueriesRequest",
    "PartialUpdateProjectRoleRequest",
    "ReadWorkflowPreviewsRequest",
    "RedactRequest",
    "RemoveAtlassianTeamRequest",
    "RemoveAttachmentRequest",
    "RemoveGadgetRequest",
    "RemoveGroupRequest",
    "RemoveProjectCategoryRequest",
    "RemoveUserRequest",
    "RemoveVoteRequest",
    "RemoveWatcherRequest",
    "ReorderCustomFieldOptionsRequest",
    "ReplaceIssueFieldOptionRequest",
    "RestoreCustomFieldRequest",
    "RestoreRequest",
    "SearchAndReconsileIssuesUsingJqlPostRequest",
    "SearchAndReconsileIssuesUsingJqlRequest",
    "SearchProjectsRequest",
    "SearchRequest",
    "SearchResolutionsRequest",
    "SetActorsRequest",
    "SetFavouriteForFilterRequest",
    "StoreAvatarRequest",
    "SubmitBulkDeleteRequest",
    "SubmitBulkEditRequest",
    "SubmitBulkMoveRequest",
    "SubmitBulkTransitionRequest",
    "SubmitBulkUnwatchRequest",
    "SubmitBulkWatchRequest",
    "TrashCustomFieldRequest",
    "TrashPlanRequest",
    "UnarchiveIssuesRequest",
    "UpdateAtlassianTeamRequest",
    "UpdateCommentRequest",
    "UpdateComponentRequest",
    "UpdateCustomFieldOptionRequest",
    "UpdateCustomFieldValueRequest",
    "UpdateDashboardRequest",
    "UpdateFilterRequest",
    "UpdateGadgetRequest",
    "UpdateMultipleCustomFieldValuesRequest",
    "UpdatePlanOnlyTeamRequest",
    "UpdatePlanRequest",
    "UpdateProjectAvatarRequest",
    "UpdateProjectCategoryRequest",
    "UpdateProjectRequest",
    "UpdateRelatedWorkRequest",
    "UpdateRemoteIssueLinkRequest",
    "UpdateResolutionRequest",
    "UpdateVersionRequest",
    "UpdateWorklogRequest",
    "WorkflowCapabilitiesRequest",
    "AddCommentBodyVisibility",
    "AddWorklogBodyVisibility",
    "BulkEditDashboardsBodyChangeOwnerDetails",
    "BulkEditDashboardsBodyPermissionDetails",
    "BulkProjectPermissions",
    "BulkSetIssuePropertyBodyFilter",
    "BulkTransitionSubmitInput",
    "CreateCrossProjectReleaseRequest",
    "CreateCustomFieldRequest",
    "CreateIssueSourceRequest",
    "CreateOrUpdateRemoteIssueLinkBodyApplication",
    "CreateOrUpdateRemoteIssueLinkBodyObject",
    "CreatePermissionRequest",
    "CreatePlanBodyExclusionRules",
    "CreatePlanBodyScheduling",
    "CreateProjectWithCustomTemplateBodyDetails",
    "CreateProjectWithCustomTemplateBodyTemplate",
    "CustomFieldOptionCreate",
    "CustomFieldOptionUpdate",
    "CustomFieldReplacement",
    "CustomFieldValueUpdate",
    "DoTransitionBodyTransition",
    "EvaluateJsisJiraExpressionBodyContext",
    "FieldUpdateOperation",
    "IssueEntityPropertiesForMultiUpdate",
    "IssueUpdateDetails",
    "JsonNode",
    "LinkIssuesBodyCommentVisibility",
    "MultipartFile",
    "MultipleCustomFieldValuesUpdate",
    "NotifyBodyRestrict",
    "NotifyBodyTo",
    "SharePermission",
    "SingleRedactionRequest",
    "SubmitBulkEditBodyEditedFieldsInput",
    "TargetToSourcesMapping",
    "UpdateCommentBodyVisibility",
    "UpdateRemoteIssueLinkBodyApplication",
    "UpdateRemoteIssueLinkBodyObject",
    "UpdateWorklogBodyVisibility",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: update_custom_field_values
class UpdateMultipleCustomFieldValuesRequestQuery(StrictModel):
    generate_changelog: bool | None = Field(default=None, validation_alias="generateChangelog", serialization_alias="generateChangelog", description="Whether to generate a changelog entry for this update. Defaults to true if not specified.")
class UpdateMultipleCustomFieldValuesRequestBody(StrictModel):
    updates: list[MultipleCustomFieldValuesUpdate] | None = Field(default=None, description="Array of custom field value updates to apply. Each entry specifies a custom field and the issue(s) to update with their new values. Order is not significant.")
class UpdateMultipleCustomFieldValuesRequest(StrictModel):
    """Update the values of one or more custom fields across one or more issues. Each custom field and issue combination must be unique within the request. Only the app that owns the custom field can perform this operation."""
    query: UpdateMultipleCustomFieldValuesRequestQuery | None = None
    body: UpdateMultipleCustomFieldValuesRequestBody | None = None

# Operation: update_custom_field_value
class UpdateCustomFieldValueRequestPath(StrictModel):
    field_id_or_key: str = Field(default=..., validation_alias="fieldIdOrKey", serialization_alias="fieldIdOrKey", description="The ID or key of the custom field to update (e.g., customfield_10010).")
class UpdateCustomFieldValueRequestQuery(StrictModel):
    generate_changelog: bool | None = Field(default=None, validation_alias="generateChangelog", serialization_alias="generateChangelog", description="Whether to generate a changelog entry for this update. Defaults to true if not specified.")
class UpdateCustomFieldValueRequestBody(StrictModel):
    updates: list[CustomFieldValueUpdate] | None = Field(default=None, description="An array of custom field update details specifying which issues to update and their new values.")
class UpdateCustomFieldValueRequest(StrictModel):
    """Updates the value of a custom field across one or more issues. Only the app that owns the custom field can perform this operation."""
    path: UpdateCustomFieldValueRequestPath
    query: UpdateCustomFieldValueRequestQuery | None = None
    body: UpdateCustomFieldValueRequestBody | None = None

# Operation: download_attachment
class GetAttachmentContentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment to download.")
class GetAttachmentContentRequestQuery(StrictModel):
    redirect: bool | None = Field(default=None, description="Whether to follow HTTP redirects for the attachment download. Set to false if your client doesn't automatically follow redirects to avoid multiple requests. Defaults to true.")
class GetAttachmentContentRequest(StrictModel):
    """Download the full content of an attachment file. Supports partial downloads using HTTP Range headers to retrieve specific byte ranges. This operation can be accessed anonymously if you have the required project and issue permissions."""
    path: GetAttachmentContentRequestPath
    query: GetAttachmentContentRequestQuery | None = None

# Operation: get_attachment_thumbnail
class GetAttachmentThumbnailRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment for which to retrieve the thumbnail.")
class GetAttachmentThumbnailRequestQuery(StrictModel):
    redirect: bool | None = Field(default=None, description="Whether to return a redirect URL for the thumbnail instead of the image content directly. Set to false to avoid multiple requests if your client doesn't automatically follow redirects.")
    fallback_to_default: bool | None = Field(default=None, validation_alias="fallbackToDefault", serialization_alias="fallbackToDefault", description="Whether to return a default placeholder thumbnail when the requested attachment thumbnail cannot be generated or found.")
    width: int | None = Field(default=None, description="The maximum width in pixels to scale the thumbnail to. The thumbnail will be scaled proportionally to fit within this width.", json_schema_extra={'format': 'int32'})
    height: int | None = Field(default=None, description="The maximum height in pixels to scale the thumbnail to. The thumbnail will be scaled proportionally to fit within this height.", json_schema_extra={'format': 'int32'})
class GetAttachmentThumbnailRequest(StrictModel):
    """Retrieves a thumbnail image for an attachment. Supports optional scaling and fallback behavior when thumbnails are unavailable."""
    path: GetAttachmentThumbnailRequestPath
    query: GetAttachmentThumbnailRequestQuery | None = None

# Operation: get_attachment
class GetAttachmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment whose metadata you want to retrieve.")
class GetAttachmentRequest(StrictModel):
    """Retrieve metadata for an attachment, including details like filename, size, and creation date. The attachment content itself is not returned by this operation."""
    path: GetAttachmentRequestPath

# Operation: delete_attachment
class RemoveAttachmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment to delete.")
class RemoveAttachmentRequest(StrictModel):
    """Removes an attachment from an issue. Requires either permission to delete your own attachments or permission to delete any attachment in the project."""
    path: RemoveAttachmentRequestPath

# Operation: get_attachment_metadata_with_contents
class ExpandAttachmentForHumansRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment to retrieve metadata for.")
class ExpandAttachmentForHumansRequest(StrictModel):
    """Retrieve complete metadata for an attachment and its contents if it's an archive. Returns information about the attachment itself (ID, name) plus details about any files within supported archive formats like ZIP."""
    path: ExpandAttachmentForHumansRequestPath

# Operation: get_archive_contents_metadata
class ExpandAttachmentForMachinesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment to expand and retrieve contents metadata for.")
class ExpandAttachmentForMachinesRequest(StrictModel):
    """Retrieve metadata for the contents of an archive attachment, such as files within a ZIP archive. Use this operation when processing attachment data programmatically without user presentation."""
    path: ExpandAttachmentForMachinesRequestPath

# Operation: list_system_avatars
class GetAllSystemAvatarsRequestPath(StrictModel):
    type_: Literal["issuetype", "project", "user", "priority"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category of avatars to retrieve. Must be one of: issuetype, project, user, or priority.")
class GetAllSystemAvatarsRequest(StrictModel):
    """Retrieves a list of system avatars filtered by type (issue type, project, user, or priority). This operation is publicly accessible and requires no authentication."""
    path: GetAllSystemAvatarsRequestPath

# Operation: delete_issues_bulk
class SubmitBulkDeleteRequestBody(StrictModel):
    """The request body containing the issues to be deleted."""
    selected_issue_ids_or_keys: list[str] = Field(default=..., validation_alias="selectedIssueIdsOrKeys", serialization_alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to delete. Can include issues from different projects and types. Order is not significant.")
    send_bulk_notification: bool | None = Field(default=None, validation_alias="sendBulkNotification", serialization_alias="sendBulkNotification", description="Whether to send a bulk change notification email to users about the deletions. Enabled by default.")
class SubmitBulkDeleteRequest(StrictModel):
    """Submit a bulk delete request to remove multiple issues across projects in a single operation. You can delete up to 1,000 issues at once, with optional notification to affected users."""
    body: SubmitBulkDeleteRequestBody

# Operation: list_bulk_editable_fields
class GetBulkEditableFieldsRequestQuery(StrictModel):
    issue_ids_or_keys: str = Field(default=..., validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="One or more issue IDs or keys to determine which fields are eligible for bulk editing. Provide as a comma-separated list or array of values.")
    search_text: str | None = Field(default=None, validation_alias="searchText", serialization_alias="searchText", description="Optional text to filter the returned editable fields by name or description.")
class GetBulkEditableFieldsRequest(StrictModel):
    """Retrieve a list of fields that are editable in bulk operations for the specified issues. Returns up to 50 fields per page, optionally filtered by search text."""
    query: GetBulkEditableFieldsRequestQuery

# Operation: bulk_edit_issues
class SubmitBulkEditRequestBody(StrictModel):
    """The request body containing the issues to be edited and the new field values."""
    edited_fields_input: SubmitBulkEditBodyEditedFieldsInput = Field(default=..., validation_alias="editedFieldsInput", serialization_alias="editedFieldsInput", description="An object containing the new values for each field being edited. The structure varies by field type, and field IDs must correspond to those specified in selectedActions.")
    selected_actions: list[str] = Field(default=..., validation_alias="selectedActions", serialization_alias="selectedActions", description="List of field IDs to be modified in the bulk edit operation. Each ID must match a field in editedFieldsInput and corresponds to a specific issue attribute being updated. Obtain available field IDs from the Bulk Edit Get Fields API.")
    selected_issue_ids_or_keys: list[str] = Field(default=..., validation_alias="selectedIssueIdsOrKeys", serialization_alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to be edited, which may span multiple projects and issue types. Supports up to 1000 issues including subtasks per request.")
    send_bulk_notification: bool | None = Field(default=None, validation_alias="sendBulkNotification", serialization_alias="sendBulkNotification", description="Whether to send bulk change notification emails to affected users about the updates. Defaults to true if not specified.")
class SubmitBulkEditRequest(StrictModel):
    """Simultaneously edit multiple issues across projects by specifying field values and target issues. Supports up to 1000 issues and 200 fields per request, with optional bulk notification to affected users."""
    body: SubmitBulkEditRequestBody

# Operation: move_issues_bulk
class SubmitBulkMoveRequestBody(StrictModel):
    send_bulk_notification: bool | None = Field(default=None, validation_alias="sendBulkNotification", serialization_alias="sendBulkNotification", description="Whether to send a bulk notification email to users when issues are moved. Defaults to true if not specified.")
    target_to_sources_mapping: dict[str, TargetToSourcesMapping] | None = Field(default=None, validation_alias="targetToSourcesMapping", serialization_alias="targetToSourcesMapping", description="Mapping of destination configurations to source issues. Each mapping key combines destination project (ID or key), issue type ID, and optional parent (ID or key) in comma-separated format. The mapping defines field transformations and status mappings required for the move. Duplicate keys will be silently ignored without failing the operation.")
class SubmitBulkMoveRequest(StrictModel):
    """Move multiple issues across projects in a single operation. Supports moving up to 1,000 issues (including subtasks) to a single destination project, issue type, and parent, with automatic field mapping and optional bulk notifications."""
    body: SubmitBulkMoveRequestBody | None = None

# Operation: list_issue_transitions
class GetAvailableTransitionsRequestQuery(StrictModel):
    issue_ids_or_keys: str = Field(default=..., validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="Comma-separated list of issue IDs or keys to retrieve available transitions for. Supports up to 1,000 issues per request.")
class GetAvailableTransitionsRequest(StrictModel):
    """Retrieve available transitions for specified issues that can be used in bulk transition operations. Returns transitions organized by workflow, including only those common across all specified issues that don't require additional field updates."""
    query: GetAvailableTransitionsRequestQuery

# Operation: transition_issues_bulk
class SubmitBulkTransitionRequestBody(StrictModel):
    """The request body containing the issues to be transitioned."""
    bulk_transition_inputs: list[BulkTransitionSubmitInput] = Field(default=..., validation_alias="bulkTransitionInputs", serialization_alias="bulkTransitionInputs", description="Array of issue transition objects, each containing an issue identifier and its corresponding transition ID. Issues must share compatible workflows for their specified transitions. Maximum of 1,000 issues per request.")
    send_bulk_notification: bool | None = Field(default=None, validation_alias="sendBulkNotification", serialization_alias="sendBulkNotification", description="Whether to send bulk notification emails to affected users when issues are transitioned. Enabled by default.")
class SubmitBulkTransitionRequest(StrictModel):
    """Transition the status of multiple issues in a single operation. Submit up to 1,000 issues with their corresponding transition IDs to move them through your workflow states."""
    body: SubmitBulkTransitionRequestBody

# Operation: unwatch_issues_bulk
class SubmitBulkUnwatchRequestBody(StrictModel):
    """The request body containing the issues to be unwatched."""
    selected_issue_ids_or_keys: list[str] = Field(default=..., validation_alias="selectedIssueIdsOrKeys", serialization_alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to unwatch. You can include up to 1,000 issues from any projects or issue types in a single request.")
class SubmitBulkUnwatchRequest(StrictModel):
    """Remove your watch from multiple issues in a single operation. You can unwatch up to 1,000 issues across different projects and issue types."""
    body: SubmitBulkUnwatchRequestBody

# Operation: watch_issues
class SubmitBulkWatchRequestBody(StrictModel):
    """The request body containing the issues to be watched."""
    selected_issue_ids_or_keys: list[str] = Field(default=..., validation_alias="selectedIssueIdsOrKeys", serialization_alias="selectedIssueIdsOrKeys", description="List of issue IDs or keys to watch, supporting up to 1,000 items per request. Issues can be from different projects and types. Provide either numeric IDs or string keys (e.g., PROJ-123).")
class SubmitBulkWatchRequest(StrictModel):
    """Add up to 1,000 issues to your watch list in a single bulk operation. Watched issues will appear in your notifications and dashboards."""
    body: SubmitBulkWatchRequestBody

# Operation: get_bulk_operation_progress
class GetBulkOperationProgressRequestPath(StrictModel):
    task_id: str = Field(default=..., validation_alias="taskId", serialization_alias="taskId", description="The unique identifier of the bulk operation task whose progress you want to check.")
class GetBulkOperationProgressRequest(StrictModel):
    """Retrieve the current progress and status of a bulk issue operation. Returns real-time progress metrics while running, or final results upon completion. Task progress data is available for up to 14 days after creation."""
    path: GetBulkOperationProgressRequestPath

# Operation: fetch_issue_changelogs
class GetBulkChangelogsRequestBody(StrictModel):
    """A JSON object containing the bulk fetch changelog request filters such as issue IDs and field IDs."""
    field_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="fieldIds", serialization_alias="fieldIds", description="Optional list of field IDs to narrow changelog results to specific fields. You can filter by up to 10 fields.", min_length=0, max_length=10)
    issue_ids_or_keys: list[str] = Field(default=..., validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="List of issue identifiers (IDs or keys) to fetch changelogs for. You can request changelogs for up to 1000 issues. At least one issue identifier is required.", min_length=1, max_length=1000)
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of changelog items to return per page. Defaults to 1000 if not specified. Must be between 1 and 10000.", ge=1, le=10000, json_schema_extra={'format': 'int32'})
class GetBulkChangelogsRequest(StrictModel):
    """Retrieve change history for multiple issues in a paginated list, optionally filtered by specific fields. Results are sorted chronologically by changelog date and issue ID, starting from the oldest entries."""
    body: GetBulkChangelogsRequestBody

# Operation: list_classification_levels
class GetAllUserDataClassificationLevelsRequestQuery(StrictModel):
    status: Annotated[list[Literal["PUBLISHED", "ARCHIVED", "DRAFT"]], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Optional filter to return only classification levels matching the specified statuses. Provide as an array of status values.")
    order_by: Literal["rank", "-rank", "+rank"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Optional field to sort results by rank. Use 'rank' for ascending order, '+rank' for ascending, or '-rank' for descending order. If not specified, results are returned unsorted.")
class GetAllUserDataClassificationLevelsRequest(StrictModel):
    """Retrieves all available classification levels, optionally filtered by status and sorted by rank. No permissions are required to access this endpoint."""
    query: GetAllUserDataClassificationLevelsRequestQuery | None = None

# Operation: list_comments
class GetCommentsByIdsRequestBody(StrictModel):
    """The list of comment IDs."""
    ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., description="A list of comment IDs to retrieve. Specify up to 1000 IDs per request. Order is preserved in the response.")
class GetCommentsByIdsRequest(StrictModel):
    """Retrieve a paginated list of comments by their IDs. Returns comments where you have appropriate project browse permissions and any required issue-level security or visibility group/role permissions."""
    body: GetCommentsByIdsRequestBody

# Operation: list_comment_property_keys
class GetCommentPropertyKeysRequestPath(StrictModel):
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment whose property keys you want to retrieve.")
class GetCommentPropertyKeysRequest(StrictModel):
    """Retrieves all property keys associated with a specific comment. Useful for discovering what custom properties have been set on a comment."""
    path: GetCommentPropertyKeysRequestPath

# Operation: get_comment_property
class GetCommentPropertyRequestPath(StrictModel):
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment from which to retrieve the property.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The identifier of the property whose value should be retrieved from the comment.")
class GetCommentPropertyRequest(StrictModel):
    """Retrieves the value of a specific property attached to a comment. Requires appropriate project and issue permissions, and respects any visibility restrictions on the comment."""
    path: GetCommentPropertyRequestPath

# Operation: delete_comment_property
class DeleteCommentPropertyRequestPath(StrictModel):
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment containing the property to delete.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The key identifying the custom property to remove from the comment.")
class DeleteCommentPropertyRequest(StrictModel):
    """Removes a custom property from a comment. Requires either Edit All Comments permission or Edit Own Comments permission if you created the comment."""
    path: DeleteCommentPropertyRequestPath

# Operation: list_components
class FindComponentsForProjectsRequestQuery(StrictModel):
    project_ids_or_keys: list[str] | None = Field(default=None, validation_alias="projectIdsOrKeys", serialization_alias="projectIdsOrKeys", description="One or more project IDs or keys (case-sensitive) to filter components. If not provided, returns components from all accessible projects.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large result sets. Defaults to 0 (first item).", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of components to return in a single page. Defaults to 50 items per page.", json_schema_extra={'format': 'int32'})
    order_by: Literal["description", "-description", "+description", "name", "-name", "+name"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort results by component name or description. Use `name` or `description` for ascending order, prefix with `-` for descending order, or `+` for explicit ascending order.")
class FindComponentsForProjectsRequest(StrictModel):
    """Retrieve a paginated list of all components in specified projects, including global Compass components when applicable. Requires Browse Projects permission for the target project(s)."""
    query: FindComponentsForProjectsRequestQuery | None = None

# Operation: create_component
class CreateComponentRequestBody(StrictModel):
    assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(default=None, validation_alias="assigneeType", serialization_alias="assigneeType", description="Determines the default assignee for issues created with this component. Choose PROJECT_DEFAULT to use the project's default assignee, COMPONENT_LEAD to assign to the component lead, PROJECT_LEAD to assign to the project lead, or UNASSIGNED to leave issues unassigned. Defaults to PROJECT_DEFAULT if not specified.")
    description: str | None = Field(default=None, description="A brief text description of the component's purpose and scope. Optional and can be added or updated at any time.")
    name: str | None = Field(default=None, description="The unique name for the component in the project. Required when creating a component. Optional when updating a component. The maximum length is 255 characters.")
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project the component is assigned to.", json_schema_extra={'format': 'int64'})
class CreateComponentRequest(StrictModel):
    """Create a new component in a project to serve as a container for organizing and grouping related issues. Requires project administration permissions."""
    body: CreateComponentRequestBody | None = None

# Operation: get_component
class GetComponentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the component to retrieve.")
class GetComponentRequest(StrictModel):
    """Retrieve detailed information about a specific component by its ID. Requires Browse projects permission for the project containing the component."""
    path: GetComponentRequestPath

# Operation: update_component
class UpdateComponentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the component to update.")
class UpdateComponentRequestBody(StrictModel):
    assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(default=None, validation_alias="assigneeType", serialization_alias="assigneeType", description="Determines who is assigned to issues created with this component. Choose from: PROJECT_DEFAULT (project's default assignee), COMPONENT_LEAD (component lead), PROJECT_LEAD (project lead), or UNASSIGNED (no assignee). Defaults to PROJECT_DEFAULT if not specified.")
    description: str | None = Field(default=None, description="A text description of the component's purpose and scope.")
class UpdateComponentRequest(StrictModel):
    """Updates an existing component in a project, overwriting any provided fields. Use an empty string for leadAccountId to remove the component lead."""
    path: UpdateComponentRequestPath
    body: UpdateComponentRequestBody | None = None

# Operation: delete_component
class DeleteComponentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the component to delete.")
class DeleteComponentRequestQuery(StrictModel):
    move_issues_to: str | None = Field(default=None, validation_alias="moveIssuesTo", serialization_alias="moveIssuesTo", description="The unique identifier of a component to replace the deleted one. If not provided, issues associated with the deleted component will not be reassigned.")
class DeleteComponentRequest(StrictModel):
    """Deletes a component from a project. Optionally specify a replacement component to reassign any issues currently associated with the deleted component."""
    path: DeleteComponentRequestPath
    query: DeleteComponentRequestQuery | None = None

# Operation: get_component_issue_counts
class GetComponentRelatedIssuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the component for which to retrieve issue counts.")
class GetComponentRelatedIssuesRequest(StrictModel):
    """Retrieves the count of issues assigned to a specific component. This provides a summary of issue distribution for component management and reporting purposes."""
    path: GetComponentRelatedIssuesRequestPath

# Operation: get_custom_field_option
class GetCustomFieldOptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field option to retrieve.")
class GetCustomFieldOptionRequest(StrictModel):
    """Retrieve a custom field option by ID, such as an option from a select list. This operation works only with options created in Jira or via the Issue custom field options API, and can be accessed anonymously with appropriate permissions."""
    path: GetCustomFieldOptionRequestPath

# Operation: list_dashboards
class GetAllDashboardsRequestQuery(StrictModel):
    filter_: Literal["my", "favourite"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter the dashboard list by ownership or favorite status. Use 'my' to show only dashboards you own, or 'favourite' to show only dashboards you've marked as favorites.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of dashboards to return per page. Defaults to 20 if not specified.", json_schema_extra={'format': 'int32'})
class GetAllDashboardsRequest(StrictModel):
    """Retrieve a list of dashboards owned by or shared with the user. Results can be filtered to show only favorite or owned dashboards, with support for pagination."""
    query: GetAllDashboardsRequestQuery | None = None

# Operation: create_dashboard
class CreateDashboardRequestBody(StrictModel):
    """Dashboard details."""
    description: str | None = Field(default=None, description="Optional text describing the dashboard's purpose and content.")
    edit_permissions: list[SharePermission] = Field(default=..., validation_alias="editPermissions", serialization_alias="editPermissions", description="Required array specifying which users or groups can edit the dashboard and their permission levels.")
    name: str = Field(default=..., description="Required name for the dashboard. Used as the primary identifier and display label.")
    share_permissions: list[SharePermission] = Field(default=..., validation_alias="sharePermissions", serialization_alias="sharePermissions", description="Required array specifying which users or groups can view and access the dashboard and their permission levels.")
class CreateDashboardRequest(StrictModel):
    """Creates a new dashboard with specified name, description, and access permissions. The dashboard will be configured with edit and share permissions to control who can modify and access it."""
    body: CreateDashboardRequestBody

# Operation: update_dashboards_bulk
class BulkEditDashboardsRequestBody(StrictModel):
    """The details of dashboards being updated in bulk."""
    action: Literal["changeOwner", "changePermission", "addPermission", "removePermission"] = Field(default=..., description="The type of bulk operation to perform: change the dashboard owner, modify permissions, add new permissions, or remove existing permissions.")
    change_owner_details: BulkEditDashboardsBodyChangeOwnerDetails | None = Field(default=None, validation_alias="changeOwnerDetails", serialization_alias="changeOwnerDetails", description="Required when action is 'changeOwner'. Contains the details needed to transfer ownership of the dashboards to a new owner.")
    entity_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., validation_alias="entityIds", serialization_alias="entityIds", description="A list of dashboard IDs to be modified by the bulk operation. Maximum of 100 dashboard IDs per request.")
    permission_details: BulkEditDashboardsBodyPermissionDetails | None = Field(default=None, validation_alias="permissionDetails", serialization_alias="permissionDetails", description="Required when action is 'changePermission', 'addPermission', or 'removePermission'. Specifies the permission settings to apply to the selected dashboards.")
class BulkEditDashboardsRequest(StrictModel):
    """Perform bulk operations on multiple dashboards such as changing ownership or modifying permissions. You can update up to 100 dashboards in a single request. You must own the dashboards or have administrator privileges to make changes."""
    body: BulkEditDashboardsRequestBody

# Operation: search_dashboards
class GetDashboardsPaginatedRequestQuery(StrictModel):
    dashboard_name: str | None = Field(default=None, validation_alias="dashboardName", serialization_alias="dashboardName", description="Filter dashboards by name using case-insensitive partial matching.")
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="Filter dashboards to only those shared with a specific project by its ID.", json_schema_extra={'format': 'int64'})
    order_by: Literal["description", "-description", "+description", "favorite_count", "-favorite_count", "+favorite_count", "id", "-id", "+id", "is_favorite", "-is_favorite", "+is_favorite", "name", "-name", "+name", "owner", "-owner", "+owner"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort results by a field: description, favorite count, ID, favorite status, name, or owner. Prefix with `-` for descending order or `+` for ascending order. Defaults to sorting by name.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of dashboards to return per page. Defaults to 50.", json_schema_extra={'format': 'int32'})
    status: Literal["active", "archived", "deleted"] | None = Field(default=None, description="Filter dashboards by their status: active, archived, or deleted. Defaults to active.")
class GetDashboardsPaginatedRequest(StrictModel):
    """Search for dashboards with optional filtering by name, project, and status. Returns a paginated list of dashboards accessible to the user based on ownership, group membership, project sharing, or public availability."""
    query: GetDashboardsPaginatedRequestQuery | None = None

# Operation: update_dashboard_gadget
class UpdateGadgetRequestPath(StrictModel):
    dashboard_id: int = Field(default=..., validation_alias="dashboardId", serialization_alias="dashboardId", description="The unique identifier of the dashboard containing the gadget. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    gadget_id: int = Field(default=..., validation_alias="gadgetId", serialization_alias="gadgetId", description="The unique identifier of the gadget to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateGadgetRequestBody(StrictModel):
    color: str | None = Field(default=None, description="The visual color of the gadget. Choose from: blue, red, yellow, green, cyan, purple, gray, or white.")
    title: str | None = Field(default=None, description="The display title for the gadget shown on the dashboard.")
class UpdateGadgetRequest(StrictModel):
    """Modify a gadget's appearance and position on a dashboard by updating its title, color, and layout properties."""
    path: UpdateGadgetRequestPath
    body: UpdateGadgetRequestBody | None = None

# Operation: remove_gadget
class RemoveGadgetRequestPath(StrictModel):
    dashboard_id: int = Field(default=..., validation_alias="dashboardId", serialization_alias="dashboardId", description="The unique identifier of the dashboard containing the gadget to remove. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    gadget_id: int = Field(default=..., validation_alias="gadgetId", serialization_alias="gadgetId", description="The unique identifier of the gadget to remove from the dashboard. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class RemoveGadgetRequest(StrictModel):
    """Remove a gadget from a dashboard. When removed, other gadgets in the same column automatically shift up to fill the vacant position."""
    path: RemoveGadgetRequestPath

# Operation: list_dashboard_item_property_keys
class GetDashboardItemPropertyKeysRequestPath(StrictModel):
    dashboard_id: str = Field(default=..., validation_alias="dashboardId", serialization_alias="dashboardId", description="The unique identifier of the dashboard containing the item.")
    item_id: str = Field(default=..., validation_alias="itemId", serialization_alias="itemId", description="The unique identifier of the dashboard item whose property keys you want to retrieve.")
class GetDashboardItemPropertyKeysRequest(StrictModel):
    """Retrieves all property keys associated with a specific dashboard item. This operation allows you to discover what custom properties are available for a dashboard item without retrieving their values."""
    path: GetDashboardItemPropertyKeysRequestPath

# Operation: get_dashboard_item_property
class GetDashboardItemPropertyRequestPath(StrictModel):
    dashboard_id: str = Field(default=..., validation_alias="dashboardId", serialization_alias="dashboardId", description="The unique identifier of the dashboard containing the item.")
    item_id: str = Field(default=..., validation_alias="itemId", serialization_alias="itemId", description="The unique identifier of the dashboard item (gadget) whose property you want to retrieve.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The key name of the property to retrieve from the dashboard item.")
class GetDashboardItemPropertyRequest(StrictModel):
    """Retrieve a specific property value stored for a dashboard item. Dashboard items are gadgets that apps use to display user-specific information on dashboards, and properties store the item's content or configuration details."""
    path: GetDashboardItemPropertyRequestPath

# Operation: remove_dashboard_item_property
class DeleteDashboardItemPropertyRequestPath(StrictModel):
    dashboard_id: str = Field(default=..., validation_alias="dashboardId", serialization_alias="dashboardId", description="The unique identifier of the dashboard containing the item.")
    item_id: str = Field(default=..., validation_alias="itemId", serialization_alias="itemId", description="The unique identifier of the dashboard item whose property will be deleted.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The key identifying the specific property to delete from the dashboard item.")
class DeleteDashboardItemPropertyRequest(StrictModel):
    """Removes a custom property from a dashboard item. Requires edit permission on the dashboard."""
    path: DeleteDashboardItemPropertyRequestPath

# Operation: get_dashboard
class GetDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to retrieve.")
class GetDashboardRequest(StrictModel):
    """Retrieve a dashboard by its ID. The dashboard must be shared with the user, owned by the user, or the user must have Jira administration permissions to access it."""
    path: GetDashboardRequestPath

# Operation: update_dashboard
class UpdateDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to update.")
class UpdateDashboardRequestBody(StrictModel):
    """Replacement dashboard details."""
    description: str | None = Field(default=None, description="A brief text description of the dashboard's purpose or content.")
    edit_permissions: list[SharePermission] = Field(default=..., validation_alias="editPermissions", serialization_alias="editPermissions", description="An array of permission objects that define who can edit the dashboard and their access level.")
    name: str = Field(default=..., description="The display name of the dashboard.")
    share_permissions: list[SharePermission] = Field(default=..., validation_alias="sharePermissions", serialization_alias="sharePermissions", description="An array of permission objects that define who can view and access the dashboard.")
class UpdateDashboardRequest(StrictModel):
    """Update an existing dashboard by replacing all its details with the provided information. You must own the dashboard to update it."""
    path: UpdateDashboardRequestPath
    body: UpdateDashboardRequestBody

# Operation: delete_dashboard
class DeleteDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to delete.")
class DeleteDashboardRequest(StrictModel):
    """Permanently deletes a dashboard. You must be the owner of the dashboard to delete it."""
    path: DeleteDashboardRequestPath

# Operation: duplicate_dashboard
class CopyDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to copy.")
class CopyDashboardRequestBody(StrictModel):
    """Dashboard details."""
    description: str | None = Field(default=None, description="Optional text describing the purpose or content of the copied dashboard.")
    edit_permissions: list[SharePermission] = Field(default=..., validation_alias="editPermissions", serialization_alias="editPermissions", description="An array of user or group permissions that grants edit access to the dashboard. Specifies who can modify the dashboard after creation.")
    name: str = Field(default=..., description="The display name for the copied dashboard. This identifies the dashboard in lists and navigation.")
    share_permissions: list[SharePermission] = Field(default=..., validation_alias="sharePermissions", serialization_alias="sharePermissions", description="An array of user or group permissions that grants view and share access to the dashboard. Specifies who can view and redistribute access to the dashboard.")
class CopyDashboardRequest(StrictModel):
    """Creates a copy of an existing dashboard with customizable name, description, and permissions. The source dashboard must be owned by or shared with the requesting user."""
    path: CopyDashboardRequestPath
    body: CopyDashboardRequestBody

# Operation: evaluate_jira_expression
class EvaluateJsisJiraExpressionRequestBody(StrictModel):
    """The Jira expression and the evaluation context."""
    context: EvaluateJsisJiraExpressionBodyContext | None = Field(default=None, description="Optional context object that defines variables available to the expression, including built-in contexts (user, issue, issues, project, sprint, board, serviceDesk, customerRequest) and custom variables (user IDs, issue keys, JSON objects, or lists). Omit if using only automatic contexts.")
    expression: str = Field(default=..., description="The Jira expression to evaluate as a string. Can reference context variables and perform operations like field extraction, filtering, and mapping (e.g., extracting issue keys, types, and linked issue IDs).")
class EvaluateJsisJiraExpressionRequest(StrictModel):
    """Evaluates a Jira expression and returns its computed value using the enhanced search API for better performance and scalability. Supports flexible data retrieval with access to issues, projects, sprints, boards, and custom context variables."""
    body: EvaluateJsisJiraExpressionRequestBody

# Operation: list_fields_search
class GetFieldsPaginatedRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 if not specified.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of fields to return per page. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
    order_by: Literal["contextsCount", "-contextsCount", "+contextsCount", "lastUsed", "-lastUsed", "+lastUsed", "name", "-name", "+name", "screensCount", "-screensCount", "+screensCount", "projectsCount", "-projectsCount", "+projectsCount"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort the results by field attribute: contextsCount (number of related contexts), lastUsed (date of last value change), name (field name), screensCount (number of related screens), or projectsCount (number of related projects). Prefix with '-' for descending order or '+' for ascending order.")
    project_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="projectIds", serialization_alias="projectIds", description="Filter results to fields belonging only to the specified project IDs. Fields from projects you lack access to will be excluded. Provide as a comma-separated list of project identifiers.")
class GetFieldsPaginatedRequest(StrictModel):
    """Retrieve a paginated list of Jira fields, optionally filtered by field IDs, search query, or project IDs. Supports sorting by various field attributes and can be restricted to custom fields only."""
    query: GetFieldsPaginatedRequestQuery | None = None

# Operation: list_trashed_fields
class GetTrashedFieldsPaginatedRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results. Defaults to 0.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of fields to return per page. Defaults to 50 items per page.", json_schema_extra={'format': 'int32'})
    order_by: str | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort the results by field name, the date the field was moved to trash, or the planned deletion date.")
class GetTrashedFieldsPaginatedRequest(StrictModel):
    """Retrieve a paginated list of custom fields that have been moved to trash. Results can be filtered by field name or description, and sorted by name, trash date, or planned deletion date. Requires Administer Jira global permission."""
    query: GetTrashedFieldsPaginatedRequestQuery | None = None

# Operation: list_custom_field_context_issue_type_mappings
class GetIssueTypeMappingsForContextsRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the custom field for which to retrieve issue type mappings.")
class GetIssueTypeMappingsForContextsRequestQuery(StrictModel):
    context_id: list[int] | None = Field(default=None, validation_alias="contextId", serialization_alias="contextId", description="Filter results to specific contexts by providing one or more context IDs. Omit to retrieve mappings for all contexts.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large result sets.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of mappings to return per page. Defaults to 50 items if not specified.", json_schema_extra={'format': 'int32'})
class GetIssueTypeMappingsForContextsRequest(StrictModel):
    """Retrieve a paginated list of issue type mappings for a custom field across specified contexts. Results are ordered by context ID first, then by issue type ID."""
    path: GetIssueTypeMappingsForContextsRequestPath
    query: GetIssueTypeMappingsForContextsRequestQuery | None = None

# Operation: list_custom_field_options
class GetOptionsForContextRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the custom field.")
    context_id: int = Field(default=..., validation_alias="contextId", serialization_alias="contextId", description="The unique identifier of the context associated with the custom field.", json_schema_extra={'format': 'int64'})
class GetOptionsForContextRequestQuery(StrictModel):
    option_id: int | None = Field(default=None, validation_alias="optionId", serialization_alias="optionId", description="Filter results to a specific option by its unique identifier.", json_schema_extra={'format': 'int64'})
    only_options: bool | None = Field(default=None, validation_alias="onlyOptions", serialization_alias="onlyOptions", description="When enabled, returns only the direct options without cascading options.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index position to start returning results from for pagination.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of options to return per page, up to 100 items.", json_schema_extra={'format': 'int32'})
class GetOptionsForContextRequest(StrictModel):
    """Retrieve a paginated list of custom field options for a specific context, including both regular and cascading options in display order. Requires Jira administration or workflow edit permissions."""
    path: GetOptionsForContextRequestPath
    query: GetOptionsForContextRequestQuery | None = None

# Operation: create_custom_field_options
class CreateCustomFieldOptionRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the custom field to which options will be added.")
    context_id: int = Field(default=..., validation_alias="contextId", serialization_alias="contextId", description="The unique identifier of the field context where options will be created. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class CreateCustomFieldOptionRequestBody(StrictModel):
    options: list[CustomFieldOptionCreate] | None = Field(default=None, description="An array of option objects to create. Each option defines a select list choice, and for cascading select fields, can include nested cascading options. Order is preserved as provided.")
class CreateCustomFieldOptionRequest(StrictModel):
    """Create options for a custom select field within a specific context. Supports cascading options for cascading select fields, with a maximum of 1000 options per request and 10000 total options per field."""
    path: CreateCustomFieldOptionRequestPath
    body: CreateCustomFieldOptionRequestBody | None = None

# Operation: update_custom_field_options
class UpdateCustomFieldOptionRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the custom field to update options for.")
    context_id: int = Field(default=..., validation_alias="contextId", serialization_alias="contextId", description="The unique identifier of the context where the custom field options apply. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateCustomFieldOptionRequestBody(StrictModel):
    options: list[CustomFieldOptionUpdate] | None = Field(default=None, description="An array of custom field option objects to update. Each object should contain the option details to be modified. If any option is not found, the entire operation fails and no options are updated.")
class UpdateCustomFieldOptionRequest(StrictModel):
    """Updates the available options for a custom field within a specific context. Only options with changed values are updated; unchanged options are ignored in the response. This operation works exclusively with select list options created in Jira or via the Issue custom field options API, not with options created by Connect apps."""
    path: UpdateCustomFieldOptionRequestPath
    body: UpdateCustomFieldOptionRequestBody | None = None

# Operation: reorder_custom_field_options
class ReorderCustomFieldOptionsRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the custom field containing the options to reorder.")
    context_id: int = Field(default=..., validation_alias="contextId", serialization_alias="contextId", description="The unique identifier of the context in which the custom field options are defined.", json_schema_extra={'format': 'int64'})
class ReorderCustomFieldOptionsRequestBody(StrictModel):
    custom_field_option_ids: list[str] = Field(default=..., validation_alias="customFieldOptionIds", serialization_alias="customFieldOptionIds", description="An ordered list of custom field option IDs that defines their new sequence. All IDs must be either custom field options or cascading options, but not a mix of both types.")
    after: str | None = Field(default=None, description="The ID of the custom field option or cascading option to place the moved options after. Required if `position` isn't provided.")
    position: Literal["First", "Last"] | None = Field(default=None, description="The position the custom field options should be moved to. Required if `after` isn't provided.")
class ReorderCustomFieldOptionsRequest(StrictModel):
    """Reorder custom field options within a specific context. Rearranges the display order of custom field options or cascading options by specifying their desired sequence."""
    path: ReorderCustomFieldOptionsRequestPath
    body: ReorderCustomFieldOptionsRequestBody

# Operation: delete_custom_field_option
class DeleteCustomFieldOptionRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the custom field containing the option to delete.")
    context_id: int = Field(default=..., validation_alias="contextId", serialization_alias="contextId", description="The unique identifier of the context from which the option should be deleted. This is a numeric ID.", json_schema_extra={'format': 'int64'})
    option_id: int = Field(default=..., validation_alias="optionId", serialization_alias="optionId", description="The unique identifier of the option to delete. This is a numeric ID.", json_schema_extra={'format': 'int64'})
class DeleteCustomFieldOptionRequest(StrictModel):
    """Deletes a custom field option from a specific context. Options with cascading options cannot be deleted until their cascading options are removed first."""
    path: DeleteCustomFieldOptionRequestPath

# Operation: list_field_screens
class GetScreensForFieldRequestPath(StrictModel):
    field_id: str = Field(default=..., validation_alias="fieldId", serialization_alias="fieldId", description="The unique identifier of the field to retrieve screens for.")
class GetScreensForFieldRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index where the paginated results should start. Defaults to 0 if not specified.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of screens to return per page. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class GetScreensForFieldRequest(StrictModel):
    """Retrieve a paginated list of all screens where a specific field is used. Requires Jira administrator permissions."""
    path: GetScreensForFieldRequestPath
    query: GetScreensForFieldRequestQuery | None = None

# Operation: list_field_options
class GetAllIssueFieldOptionsRequestPath(StrictModel):
    field_key: str = Field(default=..., validation_alias="fieldKey", serialization_alias="fieldKey", description="The field key in the format app-key__field-key (e.g., example-add-on__example-issue-field). Find this value in the app's plugin descriptor or by running the Get fields operation.")
class GetAllIssueFieldOptionsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first item. Defaults to 0 if not specified.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of options to return per page. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetAllIssueFieldOptionsRequest(StrictModel):
    """Retrieve a paginated list of all options available for a Connect app-provided select list issue field. This operation only works with field options added by Connect apps, not those created directly in Jira."""
    path: GetAllIssueFieldOptionsRequestPath
    query: GetAllIssueFieldOptionsRequestQuery | None = None

# Operation: add_field_option
class CreateIssueFieldOptionRequestPath(StrictModel):
    field_key: str = Field(default=..., validation_alias="fieldKey", serialization_alias="fieldKey", description="The unique identifier for the Connect app's custom field, formatted as app-key__field-key (e.g., example-add-on__example-issue-field). Find this value in the app's plugin descriptor or by calling Get fields.")
class CreateIssueFieldOptionRequestBody(StrictModel):
    value: str = Field(default=..., description="The display name for the new option as it will appear in Jira. This is the user-facing label for the select list option.")
class CreateIssueFieldOptionRequest(StrictModel):
    """Add a new option to a Connect app's select list issue field. Each field supports up to 10,000 options, and requires Jira administrator permissions."""
    path: CreateIssueFieldOptionRequestPath
    body: CreateIssueFieldOptionRequestBody

# Operation: list_field_option_suggestions
class GetSelectableIssueFieldOptionsRequestPath(StrictModel):
    field_key: str = Field(default=..., validation_alias="fieldKey", serialization_alias="fieldKey", description="The field key in the format $(app-key)__$(field-key), such as example-add-on__example-issue-field. Find this value in the app's plugin descriptor or by calling Get fields.")
class GetSelectableIssueFieldOptionsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first item. Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of options to return per page. Defaults to 50 items.", json_schema_extra={'format': 'int32'})
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="Optionally filter results to show only options available in a specific project by providing its numeric ID.", json_schema_extra={'format': 'int64'})
class GetSelectableIssueFieldOptionsRequest(StrictModel):
    """Retrieve a paginated list of selectable options for a Connect app custom issue field that the user can view and select. This operation only works with field options added by Connect apps, not those created natively in Jira."""
    path: GetSelectableIssueFieldOptionsRequestPath
    query: GetSelectableIssueFieldOptionsRequestQuery | None = None

# Operation: search_field_options
class GetVisibleIssueFieldOptionsRequestPath(StrictModel):
    field_key: str = Field(default=..., validation_alias="fieldKey", serialization_alias="fieldKey", description="The field identifier in the format appKey__fieldKey (e.g., example-add-on__example-issue-field). Retrieve this value from the app's plugin descriptor or by calling Get fields.")
class GetVisibleIssueFieldOptionsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (0-based index). Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of options to return per page. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="Restrict results to options available in a specific project. When omitted, returns options available across all projects.", json_schema_extra={'format': 'int64'})
class GetVisibleIssueFieldOptionsRequest(StrictModel):
    """Search for visible options in a Connect app custom select list field. Returns paginated results filtered by user permissions and optionally by project."""
    path: GetVisibleIssueFieldOptionsRequestPath
    query: GetVisibleIssueFieldOptionsRequestQuery | None = None

# Operation: get_field_option
class GetIssueFieldOptionRequestPath(StrictModel):
    field_key: str = Field(default=..., validation_alias="fieldKey", serialization_alias="fieldKey", description="The field key in the format app-key__field-key (e.g., example-add-on__example-issue-field). Find this value in the app's plugin descriptor or by running Get fields to retrieve the key from field details.")
    option_id: int = Field(default=..., validation_alias="optionId", serialization_alias="optionId", description="The numeric ID of the option to retrieve. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetIssueFieldOptionRequest(StrictModel):
    """Retrieve a specific option from a Connect app-provided select list issue field. This operation only works with field options added by Connect apps, not those created directly in Jira."""
    path: GetIssueFieldOptionRequestPath

# Operation: replace_field_option
class ReplaceIssueFieldOptionRequestPath(StrictModel):
    field_key: str = Field(default=..., validation_alias="fieldKey", serialization_alias="fieldKey", description="The field key in the format app-key__field-key (e.g., example-add-on__example-issue-field). Retrieve this value from the app's plugin descriptor or by calling Get fields.")
    option_id: int = Field(default=..., validation_alias="optionId", serialization_alias="optionId", description="The numeric ID of the select-list option to be deselected from all issues.", json_schema_extra={'format': 'int64'})
class ReplaceIssueFieldOptionRequestQuery(StrictModel):
    replace_with: int | None = Field(default=None, validation_alias="replaceWith", serialization_alias="replaceWith", description="The numeric ID of the option that will replace the deselected option. If not provided, the option is simply removed without replacement.", json_schema_extra={'format': 'int64'})
    jql: str | None = Field(default=None, description="A JQL query that limits the operation to a specific set of issues (e.g., project=10000). If not provided, the operation applies to all issues with the option selected.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Whether to override screen security to allow editing of uneditable fields. Only available to Connect and Forge app users with Administer Jira permission. Defaults to false.")
class ReplaceIssueFieldOptionRequest(StrictModel):
    """Deselects a custom field select-list option from all issues where it is selected, optionally replacing it with a different option. This asynchronous operation works only with options added by Connect or Forge apps and can be scoped to specific issues using JQL."""
    path: ReplaceIssueFieldOptionRequestPath
    query: ReplaceIssueFieldOptionRequestQuery | None = None

# Operation: delete_custom_field
class DeleteCustomFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to delete.")
class DeleteCustomFieldRequest(StrictModel):
    """Permanently deletes a custom field from Jira, whether it's in the trash or active. This is an asynchronous operation; use the location link in the response to track the deletion task status."""
    path: DeleteCustomFieldRequestPath

# Operation: restore_custom_field
class RestoreCustomFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to restore from trash.")
class RestoreCustomFieldRequest(StrictModel):
    """Restore a custom field from trash back to active use. Requires Administer Jira global permission."""
    path: RestoreCustomFieldRequestPath

# Operation: move_custom_field_to_trash
class TrashCustomFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to move to trash.")
class TrashCustomFieldRequest(StrictModel):
    """Move a custom field to trash, making it unavailable for use while preserving the option to permanently delete it later. Requires Administer Jira global permission."""
    path: TrashCustomFieldRequestPath

# Operation: create_filter
class CreateFilterRequestBody(StrictModel):
    """The filter to create."""
    description: str | None = Field(default=None, description="A brief explanation of the filter's purpose and usage.")
    edit_permissions: list[SharePermission] | None = Field(default=None, validation_alias="editPermissions", serialization_alias="editPermissions", description="Groups and projects that are granted permission to edit this filter. Specify as an array of group and project objects.")
    favourite: bool | None = Field(default=None, description="Whether to automatically mark this filter as a favorite for the current user.")
    jql: str | None = Field(default=None, description="The JQL (Jira Query Language) query that defines which issues the filter returns. For example: project = SSP AND issuetype = Bug.")
    name: str = Field(default=..., description="The display name for the filter. Must be unique across all filters in the Jira instance.")
    share_permissions: list[SharePermission] | None = Field(default=None, validation_alias="sharePermissions", serialization_alias="sharePermissions", description="Groups and projects with whom this filter is shared. Specify as an array of group and project objects to control visibility and access.")
class CreateFilterRequest(StrictModel):
    """Creates a new filter with a JQL query and optional sharing settings. The filter is shared according to default scope settings and is not automatically marked as a favorite."""
    body: CreateFilterRequestBody

# Operation: list_my_filters
class GetMyFiltersRequestQuery(StrictModel):
    include_favourites: bool | None = Field(default=None, validation_alias="includeFavourites", serialization_alias="includeFavourites", description="When enabled, includes the user's favorite filters in the response alongside owned filters. Disabled by default.")
class GetMyFiltersRequest(StrictModel):
    """Retrieve filters owned by the authenticated user, with optional inclusion of their favorite filters. Favorite filters are only visible if they are owned by the user, shared with a group the user belongs to, shared with a private project the user can browse, shared with a public project, or shared publicly."""
    query: GetMyFiltersRequestQuery | None = None

# Operation: search_filters
class GetFiltersPaginatedRequestQuery(StrictModel):
    filter_name: str | None = Field(default=None, validation_alias="filterName", serialization_alias="filterName", description="Partial filter name to search for using case-insensitive matching. Matching behavior depends on the isSubstringMatch parameter.")
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="Filter results to only those shared with a specific project by its ID.", json_schema_extra={'format': 'int64'})
    order_by: Literal["description", "-description", "+description", "favourite_count", "-favourite_count", "+favourite_count", "id", "-id", "+id", "is_favourite", "-is_favourite", "+is_favourite", "name", "-name", "+name", "owner", "-owner", "+owner", "is_shared", "-is_shared", "+is_shared"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort results by a field: name, description, ID, owner, favorite count, whether marked as favorite, or whether shared. Prefix with '-' for descending or '+' for ascending order.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="Zero-based index for pagination, indicating which result to start from. Defaults to 0 for the first page.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of filters to return per page. Defaults to 50 results.", json_schema_extra={'format': 'int32'})
    is_substring_match: bool | None = Field(default=None, validation_alias="isSubstringMatch", serialization_alias="isSubstringMatch", description="When true, performs case-insensitive substring matching on the filter name. When false, uses full text search syntax. Defaults to false.")
class GetFiltersPaginatedRequest(StrictModel):
    """Search for filters with pagination support, returning filters based on ownership, sharing permissions, and optional search criteria. Only filters accessible to the authenticated user are returned."""
    query: GetFiltersPaginatedRequestQuery | None = None

# Operation: get_filter
class GetFilterRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to retrieve, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetFilterRequest(StrictModel):
    """Retrieve a filter by its ID. The filter is only returned if you have access to it through ownership, group sharing, project sharing, or public sharing."""
    path: GetFilterRequestPath

# Operation: update_filter
class UpdateFilterRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateFilterRequestBody(StrictModel):
    """The filter to update."""
    description: str | None = Field(default=None, description="A text description explaining the filter's purpose or usage.")
    edit_permissions: list[SharePermission] | None = Field(default=None, validation_alias="editPermissions", serialization_alias="editPermissions", description="An array of groups and projects that are granted permission to edit this filter. Order and format are determined by the API's permission structure.")
    favourite: bool | None = Field(default=None, description="A boolean flag indicating whether this filter should be marked as a favorite in the user's filter list.")
    jql: str | None = Field(default=None, description="The JQL (Jira Query Language) query string that defines which issues this filter returns. For example: project = SSP AND issuetype = Bug.")
    name: str = Field(default=..., description="The display name for the filter. Must be unique across all filters you own.")
    share_permissions: list[SharePermission] | None = Field(default=None, validation_alias="sharePermissions", serialization_alias="sharePermissions", description="An array of groups and projects with whom this filter is shared. Order and format are determined by the API's permission structure.")
class UpdateFilterRequest(StrictModel):
    """Update an existing filter's configuration including name, description, JQL query, and sharing settings. You must own the filter to make changes."""
    path: UpdateFilterRequestPath
    body: UpdateFilterRequestBody

# Operation: delete_filter
class DeleteFilterRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteFilterRequest(StrictModel):
    """Permanently delete a filter from Jira. Only the filter creator or users with Administer Jira permission can delete filters."""
    path: DeleteFilterRequestPath

# Operation: list_filter_columns
class GetColumnsRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetColumnsRequest(StrictModel):
    """Retrieves the columns configured for a filter, which are used when viewing filter results in List View with Columns set to Filter. Column details are only returned for filters you own, filters shared with your groups, or filters shared with projects you have access to."""
    path: GetColumnsRequestPath

# Operation: add_filter_to_favorites
class SetFavouriteForFilterRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to add as a favorite. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class SetFavouriteForFilterRequest(StrictModel):
    """Mark a filter as a favorite for the current user. You can only favorite filters you own, filters shared with your groups or projects, or publicly shared filters."""
    path: SetFavouriteForFilterRequestPath

# Operation: remove_filter_favorite
class DeleteFavouriteForFilterRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to remove from favorites, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteFavouriteForFilterRequest(StrictModel):
    """Remove a filter from the user's favorites list. This operation only removes filters that are currently visible to the user; filters that were favorited but subsequently made private cannot be removed through this operation."""
    path: DeleteFavouriteForFilterRequestPath

# Operation: transfer_filter_ownership
class ChangeFilterOwnerRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to transfer. This is a numeric ID that identifies the specific filter in your Jira instance.", json_schema_extra={'format': 'int64'})
class ChangeFilterOwnerRequestBody(StrictModel):
    """The account ID of the new owner of the filter."""
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The account ID of the new filter owner. This must be a valid Jira user account ID.")
class ChangeFilterOwnerRequest(StrictModel):
    """Transfer ownership of a filter to another user. The requesting user must own the filter or have Jira administrator permissions."""
    path: ChangeFilterOwnerRequestPath
    body: ChangeFilterOwnerRequestBody

# Operation: list_filter_permissions
class GetSharePermissionsRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetSharePermissionsRequest(StrictModel):
    """Retrieve all share permissions for a filter, including access granted to groups, projects, all logged-in users, or the public. Only returns permissions visible to the requesting user based on their access level."""
    path: GetSharePermissionsRequestPath

# Operation: grant_filter_share_permission
class AddSharePermissionRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to share. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class AddSharePermissionRequestBody(StrictModel):
    project_id: str | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The project identifier to share the filter with. Required when type is set to 'project'.")
    project_role_id: str | None = Field(default=None, validation_alias="projectRoleId", serialization_alias="projectRoleId", description="The project role identifier to share the filter with. Required when type is set to 'projectRole'; must be used together with projectId.")
    rights: int | None = Field(default=None, description="The access rights level for this share permission. Specified as a 32-bit integer representing the permission level.", json_schema_extra={'format': 'int32'})
    type_: Literal["user", "project", "group", "projectRole", "global", "authenticated"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The recipient type for the share permission. Choose from: 'user' (share with individual user), 'group' (share with group), 'project' (share with project), 'projectRole' (share with project role), 'global' (share with all users including anonymous), or 'authenticated' (share with all logged-in users). Global and authenticated types override all existing permissions.")
class AddSharePermissionRequest(StrictModel):
    """Grant share permission for a filter to a user, group, project, or project role. Global or authenticated permissions will override all existing share permissions for the filter."""
    path: AddSharePermissionRequestPath
    body: AddSharePermissionRequestBody

# Operation: get_filter_share_permission
class GetSharePermissionRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    permission_id: int = Field(default=..., validation_alias="permissionId", serialization_alias="permissionId", description="The unique identifier of the share permission to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetSharePermissionRequest(StrictModel):
    """Retrieves a specific share permission for a filter. Returns details about how a filter is shared with groups, projects, all logged-in users, or the public. This operation can be accessed anonymously, but only returns permissions for filters you own, are shared with your groups, or are in projects you can access."""
    path: GetSharePermissionRequestPath

# Operation: remove_filter_share_permission
class DeleteSharePermissionRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter from which to remove the share permission. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    permission_id: int = Field(default=..., validation_alias="permissionId", serialization_alias="permissionId", description="The unique identifier of the specific share permission to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteSharePermissionRequest(StrictModel):
    """Removes a share permission from a filter, restricting access for the specified user or group. Requires ownership of the filter and permission to access Jira."""
    path: DeleteSharePermissionRequestPath

# Operation: create_group
class CreateGroupRequestBody(StrictModel):
    """The name of the group."""
    name: str = Field(default=..., description="The name for the new group. This identifier is used to reference the group in Jira.")
class CreateGroupRequest(StrictModel):
    """Creates a new group in Jira. Requires site administration permissions to perform this action."""
    body: CreateGroupRequestBody

# Operation: delete_group
class RemoveGroupRequestQuery(StrictModel):
    swap_group_id: str | None = Field(default=None, validation_alias="swapGroupId", serialization_alias="swapGroupId", description="The ID of an existing group to receive the deleted group's restrictions. Only comments and worklogs are transferred. Omit this parameter if you want restrictions to be removed without transfer. Cannot be used together with the `swapGroup` parameter.")
    group_id: str | None = Field(default=None, validation_alias="groupId", serialization_alias="groupId", description="The ID of the group. This parameter cannot be used with the `groupname` parameter.")
class RemoveGroupRequest(StrictModel):
    """Permanently deletes a group from the system. Optionally transfer group restrictions to another group to preserve access to comments and worklogs; otherwise, these items become inaccessible after deletion."""
    query: RemoveGroupRequestQuery | None = None

# Operation: list_groups
class BulkGetGroupsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first group. Use this to navigate through large result sets.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of groups to return per page. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
    group_name: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="groupName", serialization_alias="groupName", description="Filter results by one or more group names. Specify multiple names to search for groups matching any of the provided names.")
    access_type: str | None = Field(default=None, validation_alias="accessType", serialization_alias="accessType", description="Filter groups by their access level within your Jira instance. Choose from site administrator, administrator, or standard user access levels.")
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Limit results to groups associated with a specific Jira product. Specify the product key to filter groups by their application context.")
class BulkGetGroupsRequest(StrictModel):
    """Retrieve a paginated list of groups from your Jira instance. Filter by group names, access level, or product application to find specific groups."""
    query: BulkGetGroupsRequestQuery | None = None

# Operation: list_group_members
class GetUsersFromGroupRequestQuery(StrictModel):
    include_inactive_users: bool | None = Field(default=None, validation_alias="includeInactiveUsers", serialization_alias="includeInactiveUsers", description="Whether to include inactive users in the results. Defaults to excluding inactive users.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index where the result page should start. Use this for pagination to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of users to return per page. Must be between 1 and 50 users.", json_schema_extra={'format': 'int32'})
    group_id: str | None = Field(default=None, validation_alias="groupId", serialization_alias="groupId", description="The ID of the group. This parameter cannot be used with the `groupName` parameter.")
class GetUsersFromGroupRequest(StrictModel):
    """Retrieve a paginated list of all users in a group. Users are ordered by username but usernames are not included in results for privacy reasons."""
    query: GetUsersFromGroupRequestQuery | None = None

# Operation: add_user_to_group
class AddUserToGroupRequestQuery(StrictModel):
    group_id: str | None = Field(default=None, validation_alias="groupId", serialization_alias="groupId", description="The ID of the group. This parameter cannot be used with the `groupName` parameter.")
class AddUserToGroupRequestBody(StrictModel):
    """The user to add to the group."""
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)
class AddUserToGroupRequest(StrictModel):
    """Adds a user to a group in Jira. Requires site administration permissions to perform this operation."""
    query: AddUserToGroupRequestQuery | None = None
    body: AddUserToGroupRequestBody | None = None

# Operation: search_groups
class FindGroupsRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of groups to return in the results. Limited by the system's autocomplete configuration, typically capped at a system-defined threshold.", json_schema_extra={'format': 'int32'})
    case_insensitive: bool | None = Field(default=None, validation_alias="caseInsensitive", serialization_alias="caseInsensitive", description="Whether the group name search should ignore case distinctions. Defaults to case-sensitive matching when not specified.")
class FindGroupsRequest(StrictModel):
    """Search for groups by name to populate group picker suggestions. Returns matching groups with query terms highlighted in HTML, sorted alphabetically, along with a count summary. Requires Browse projects permission; anonymous users and those without permission receive empty results."""
    query: FindGroupsRequestQuery | None = None

# Operation: search_users_and_groups
class FindUsersAndGroupsRequestQuery(StrictModel):
    query: str = Field(default=..., description="The search string to match against user display names, email addresses, and group names. User matches are case-insensitive; group matches are case-sensitive by default unless caseInsensitive is enabled.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of results to return per list (users and groups). Defaults to 50 items.", json_schema_extra={'format': 'int32'})
    field_id: str | None = Field(default=None, validation_alias="fieldId", serialization_alias="fieldId", description="The custom field ID to scope the search. When provided, results are filtered to users and groups with permissions for the specified field. Required to use projectId or issueTypeId filters.")
    project_id: list[str] | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="One or more project IDs to filter results. Returned users and groups must have permission to view all specified projects. Only applicable when fieldId is provided. Projects must be a subset of those enabled for the custom field.")
    issue_type_id: list[str] | None = Field(default=None, validation_alias="issueTypeId", serialization_alias="issueTypeId", description="One or more issue type IDs to filter results. Returned users and groups must have permission to view all specified issue types. Supports special values like -1 (all standard types) and -2 (all subtask types). Only applicable when fieldId is provided.")
    case_insensitive: bool | None = Field(default=None, validation_alias="caseInsensitive", serialization_alias="caseInsensitive", description="Whether group name matching should be case-insensitive. Defaults to false (case-sensitive matching).")
class FindUsersAndGroupsRequest(StrictModel):
    """Search for users and groups by name or email. Returns matching results with HTML-formatted highlights, useful for populating picker fields. Supports filtering by project, issue type, and custom field permissions."""
    query: FindUsersAndGroupsRequestQuery

# Operation: create_issue
class CreateIssueRequestQuery(StrictModel):
    update_history: bool | None = Field(default=None, validation_alias="updateHistory", serialization_alias="updateHistory", description="Whether to add the project to your recently viewed projects list and track the issue type and request type in your project history for future create screen defaults. Defaults to false.")
class CreateIssueRequestBody(StrictModel):
    fields: dict[str, Any] | None = Field(default=None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`.")
    update: dict[str, list[FieldUpdateOperation]] | None = Field(default=None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`.")
class CreateIssueRequest(StrictModel):
    """Create a new issue or subtask in a Jira project. Define the issue content using fields and optional workflow transitions, with field availability determined by the project's create issue metadata."""
    query: CreateIssueRequestQuery | None = None
    body: CreateIssueRequestBody | None = None

# Operation: archive_issues_by_jql
class ArchiveIssuesAsyncRequestBody(StrictModel):
    """A JQL query specifying the issues to archive. Note that subtasks can only be archived through their parent issues."""
    jql: str | None = Field(default=None, description="JQL query string to select issues for archival. Only issues from software, service management, and business projects can be archived; subtasks must be archived through their parent issues.")
class ArchiveIssuesAsyncRequest(StrictModel):
    """Asynchronously archive up to 100,000 issues matching a JQL query. Returns a task URL to monitor the archival progress. Requires Jira admin permissions and a Premium or Enterprise license."""
    body: ArchiveIssuesAsyncRequestBody | None = None

# Operation: archive_issues
class ArchiveIssuesRequestBody(StrictModel):
    """Contains a list of issue keys or IDs to be archived."""
    issue_ids_or_keys: list[str] | None = Field(default=None, validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="Array of issue IDs or keys to archive (up to 1000 per request). Subtasks cannot be archived directly; archive them through their parent issues. Only issues from software, service management, and business projects can be archived.")
class ArchiveIssuesRequest(StrictModel):
    """Archive up to 1000 issues by their ID or key in a single request. Returns details of successfully archived issues and any errors encountered. Requires Jira admin permissions and a Premium or Enterprise license."""
    body: ArchiveIssuesRequestBody | None = None

# Operation: create_issues_bulk
class CreateIssuesRequestBody(StrictModel):
    issue_updates: list[IssueUpdateDetails] | None = Field(default=None, validation_alias="issueUpdates", serialization_alias="issueUpdates", description="Array of issue or subtask definitions to create. Each item specifies fields and updates for one issue. For subtasks, include the parent issue ID or key and set issueType to a subtask type. Order is preserved in processing.")
class CreateIssuesRequest(StrictModel):
    """Create up to 50 issues and subtasks in bulk with optional workflow transitions and property assignments. Use the Get create issue metadata endpoint to determine available fields for your project."""
    body: CreateIssuesRequestBody | None = None

# Operation: fetch_issues
class BulkFetchIssuesRequestBody(StrictModel):
    """A JSON object containing the information about which issues and fields to fetch."""
    issue_ids_or_keys: list[str] = Field(default=..., validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="Array of issue identifiers to fetch, accepting up to 100 items. You can mix issue IDs and keys in the same request (e.g., both numeric IDs and text keys like 'PROJ-123'). Results are returned in ascending ID order.")
class BulkFetchIssuesRequest(StrictModel):
    """Retrieve details for multiple issues by their IDs or keys in a single request. Supports up to 100 issues per request with case-insensitive matching and automatic detection of moved issues."""
    body: BulkFetchIssuesRequestBody

# Operation: list_issue_types_for_creation
class GetCreateIssueMetaIssueTypesRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the project ID or project key.")
class GetCreateIssueMetaIssueTypesRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of issue types to return per page, with a maximum of 200. Defaults to 50 if not specified.", le=200, json_schema_extra={'format': 'int32'})
class GetCreateIssueMetaIssueTypesRequest(StrictModel):
    """Retrieve issue type metadata for a project to determine which issue types can be created and what fields are required. Use this information to populate requests when creating issues."""
    path: GetCreateIssueMetaIssueTypesRequestPath
    query: GetCreateIssueMetaIssueTypesRequestQuery | None = None

# Operation: get_issue_creation_fields
class GetCreateIssueMetaIssueTypeIdRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the project ID or project key.")
    issue_type_id: str = Field(default=..., validation_alias="issueTypeId", serialization_alias="issueTypeId", description="The ID of the issue type for which to retrieve creation field metadata.")
class GetCreateIssueMetaIssueTypeIdRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first item. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of fields to return per page, up to 200. Defaults to 50 if not specified.", le=200, json_schema_extra={'format': 'int32'})
class GetCreateIssueMetaIssueTypeIdRequest(StrictModel):
    """Retrieve the available fields and their metadata for creating issues of a specific type in a project. Use this information to populate requests when creating single or bulk issues."""
    path: GetCreateIssueMetaIssueTypeIdRequestPath
    query: GetCreateIssueMetaIssueTypeIdRequestQuery | None = None

# Operation: list_issue_limit_violations
class GetIssueLimitReportRequestQuery(StrictModel):
    is_returning_keys: bool | None = Field(default=None, validation_alias="isReturningKeys", serialization_alias="isReturningKeys", description="Return issue keys (e.g., PROJ-123) instead of numeric issue IDs in the response. Defaults to false, which returns issue IDs.")
class GetIssueLimitReportRequest(StrictModel):
    """Retrieve all issues that are breaching or approaching per-issue limits in Jira. Requires Browse projects permission for the relevant projects or Administer Jira global permission for complete results."""
    query: GetIssueLimitReportRequestQuery | None = None

# Operation: search_issues_picker
class GetIssuePickerResourceRequestQuery(StrictModel):
    current_jql: str | None = Field(default=None, validation_alias="currentJQL", serialization_alias="currentJQL", description="A JQL query that defines the pool of issues to search within. Note that username and userkey cannot be used for privacy reasons; use accountId instead.")
    current_issue_key: str | None = Field(default=None, validation_alias="currentIssueKey", serialization_alias="currentIssueKey", description="The key of an issue to exclude from the search results, typically the issue currently being viewed.")
    current_project_id: str | None = Field(default=None, validation_alias="currentProjectId", serialization_alias="currentProjectId", description="The ID of a project to limit suggestions to issues belonging only to that project.")
    show_sub_tasks: bool | None = Field(default=None, validation_alias="showSubTasks", serialization_alias="showSubTasks", description="Whether to include subtasks in the suggestions list.")
    show_sub_task_parent: bool | None = Field(default=None, validation_alias="showSubTaskParent", serialization_alias="showSubTaskParent", description="When the excluded issue is a subtask, whether to include its parent issue in the suggestions if it matches the query.")
    query: str | None = Field(default=None, description="A string to match against text fields in the issue such as title, description, or comments.")
class GetIssuePickerResourceRequest(StrictModel):
    """Search for issues matching a query string to provide auto-completion suggestions. Returns matching issues from the user's history and from a filtered set defined by JQL."""
    query: GetIssuePickerResourceRequestQuery | None = None

# Operation: set_issue_properties_bulk
class BulkSetIssuesPropertiesListRequestBody(StrictModel):
    """Issue properties to be set or updated with values."""
    entities_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="entitiesIds", serialization_alias="entitiesIds", description="List of issue IDs to update with the specified properties. Accepts between 1 and 10,000 issue identifiers.", min_length=1, max_length=10000)
    properties: dict[str, JsonNode] | None = Field(default=None, description="A list of entity property keys and values.", min_length=1, max_length=10)
class BulkSetIssuesPropertiesListRequest(StrictModel):
    """Bulk set or update custom properties on multiple issues in a single transactional operation. Supports up to 10 properties and 10,000 issues, with each property value limited to 32,768 characters."""
    body: BulkSetIssuesPropertiesListRequestBody | None = None

# Operation: set_issue_properties_bulk_per_issue
class BulkSetIssuePropertiesByIssueRequestBody(StrictModel):
    """Details of the issue properties to be set or updated. Note that if an issue is not found, it is ignored."""
    issues: list[IssueEntityPropertiesForMultiUpdate] | None = Field(default=None, description="A list of issues with their respective properties to set or update. Each entry should contain an issue ID and its associated property key-value pairs. Maximum of 100 issues per request, with up to 10 properties per issue.", min_length=1, max_length=100)
class BulkSetIssuePropertiesByIssueRequest(StrictModel):
    """Bulk set or update custom properties on multiple issues. Supports up to 100 issues with up to 10 properties each in a single asynchronous request. Updates are non-transactional, so some entities may succeed while others fail."""
    body: BulkSetIssuePropertiesByIssueRequestBody | None = None

# Operation: set_issue_property_bulk
class BulkSetIssuePropertyRequestPath(StrictModel):
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The property key identifier. Maximum length is 255 characters.")
class BulkSetIssuePropertyRequestBody(StrictModel):
    expression: str | None = Field(default=None, description="A Jira expression to dynamically calculate the property value for each issue. The expression must return a JSON-serializable object (number, boolean, string, list, or map) with a JSON representation not exceeding 32,768 characters. Available context variables are `issue` and `user`. Either this or `value` should be specified, but not both.")
    filter_: BulkSetIssuePropertyBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter criteria to identify which issues are eligible for update. Supports filtering by specific issue IDs, current property value, or property existence. Multiple criteria are combined with AND logic. Omit to update all issues where you have edit permission.")
    value: Any | None = Field(default=None, description="A static JSON value to set on the property. Must be a valid, non-empty JSON object with a maximum length of 32,768 characters. Either this or `expression` should be specified, but not both.")
class BulkSetIssuePropertyRequest(StrictModel):
    """Bulk set a property on multiple issues using a constant value or Jira expression. The operation is transactional and asynchronous—either all eligible issues are updated or none are updated. Use the returned task location to monitor progress."""
    path: BulkSetIssuePropertyRequestPath
    body: BulkSetIssuePropertyRequestBody | None = None

# Operation: delete_issue_property_bulk
class BulkDeleteIssuePropertyRequestPath(StrictModel):
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The unique identifier of the property to delete from issues.")
class BulkDeleteIssuePropertyRequestBody(StrictModel):
    current_value: Any | None = Field(default=None, validation_alias="currentValue", serialization_alias="currentValue", description="Optional filter to only delete the property from issues where it currently has this specific value.")
    entity_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="entityIds", serialization_alias="entityIds", description="Optional list of specific issue IDs to target for deletion. If provided with currentValue, only issues matching both criteria are affected.")
class BulkDeleteIssuePropertyRequest(StrictModel):
    """Bulk delete a property from multiple issues based on filter criteria. This operation is transactional and asynchronous—either the property is deleted from all matching issues or no changes are made if errors occur."""
    path: BulkDeleteIssuePropertyRequestPath
    body: BulkDeleteIssuePropertyRequestBody | None = None

# Operation: restore_issues
class UnarchiveIssuesRequestBody(StrictModel):
    """Contains a list of issue keys or IDs to be unarchived."""
    issue_ids_or_keys: list[str] | None = Field(default=None, validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="Array of issue keys or issue IDs to restore. You can restore up to 1000 issues per request. Subtasks cannot be restored directly; restore their parent issues instead. Only applicable to software, service management, and business projects.")
class UnarchiveIssuesRequest(StrictModel):
    """Restore up to 1000 archived issues in a single request using their issue keys or IDs. Returns details of successfully restored issues and any errors encountered. Requires Jira admin permissions and a Premium or Enterprise license."""
    body: UnarchiveIssuesRequestBody | None = None

# Operation: check_watched_issues_bulk
class GetIsWatchingIssueBulkRequestBody(StrictModel):
    """A list of issue IDs."""
    issue_ids: list[str] = Field(default=..., validation_alias="issueIds", serialization_alias="issueIds", description="A list of issue IDs to check the watched status for. The order of IDs in the list is preserved in the response.")
class GetIsWatchingIssueBulkRequest(StrictModel):
    """Check the watched status of multiple issues for the current user. Returns whether each issue is being watched, with invalid issue IDs returning a watched status of false."""
    body: GetIsWatchingIssueBulkRequestBody

# Operation: retrieve_issue
class GetIssueRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The unique identifier for the issue, either its numeric ID or alphanumeric key (e.g., PROJ-123). The search is case-insensitive and will locate moved issues.")
class GetIssueRequestQuery(StrictModel):
    update_history: bool | None = Field(default=None, validation_alias="updateHistory", serialization_alias="updateHistory", description="When enabled, adds the issue's project to your recently viewed projects list and updates the lastViewed field for JQL searches. Defaults to disabled.")
class GetIssueRequest(StrictModel):
    """Retrieve detailed information about a specific issue by its ID or key. The operation performs case-insensitive matching and checks for moved issues, returning the current issue details without redirects. Requires browse permission for the project and any applicable issue-level security permissions."""
    path: GetIssueRequestPath
    query: GetIssueRequestQuery | None = None

# Operation: update_issue
class EditIssueRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123).")
class EditIssueRequestQuery(StrictModel):
    notify_users: bool | None = Field(default=None, validation_alias="notifyUsers", serialization_alias="notifyUsers", description="Whether to send notification emails to all watchers about this update. Defaults to true; only users with Administer Jira or Administer project permissions can disable notifications.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Whether to bypass screen security restrictions to allow editing of normally uneditable fields. Only available to Connect and Forge apps with Administer Jira global permission. Defaults to false.")
    return_issue: bool | None = Field(default=None, validation_alias="returnIssue", serialization_alias="returnIssue", description="Whether to include the updated issue in the response with the same format as the Get issue endpoint. Defaults to false.")
class EditIssueRequestBody(StrictModel):
    fields: dict[str, Any] | None = Field(default=None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`.")
    update: dict[str, list[FieldUpdateOperation]] | None = Field(default=None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`.")
class EditIssueRequest(StrictModel):
    """Updates an issue's fields and properties. Use the Get edit issue metadata endpoint to determine which fields are editable. Note that issue transitions are not supported through this operation; use the Transition issue endpoint instead."""
    path: EditIssueRequestPath
    query: EditIssueRequestQuery | None = None
    body: EditIssueRequestBody | None = None

# Operation: delete_issue
class DeleteIssueRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The unique identifier or key of the issue to delete (e.g., PROJ-123 or 10001).")
class DeleteIssueRequestQuery(StrictModel):
    delete_subtasks: Literal["true", "false"] | None = Field(default=None, validation_alias="deleteSubtasks", serialization_alias="deleteSubtasks", description="Whether to automatically delete all subtasks when the issue is deleted. Set to 'true' to delete subtasks along with the issue, or 'false' to prevent deletion if subtasks exist. Defaults to 'false'.")
class DeleteIssueRequest(StrictModel):
    """Permanently deletes an issue from the project. Subtasks must be handled explicitly—either delete them along with the issue or remove them first."""
    path: DeleteIssueRequestPath
    query: DeleteIssueRequestQuery | None = None

# Operation: assign_issue
class AssignIssueRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class AssignIssueRequestBody(StrictModel):
    """The request object with the user that the issue is assigned to."""
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required in requests.", max_length=128)
class AssignIssueRequest(StrictModel):
    """Assigns an issue to a user or removes the assignment. Use this operation when you have the Assign Issues permission but lack Edit Issues permission. You can assign to a specific user, the project's default assignee, or leave the issue unassigned."""
    path: AssignIssueRequestPath
    body: AssignIssueRequestBody | None = None

# Operation: attach_files
class AddAttachmentRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., TEST-123).")
class AddAttachmentRequestBody(StrictModel):
    body: list[MultipartFile] = Field(default=..., description="Array of files to attach. Each file is submitted as a multipart form field named 'file'. Multiple files can be attached in a single request.")
class AddAttachmentRequest(StrictModel):
    """Attach one or more files to a Jira issue. Files are uploaded as multipart form data and require the X-Atlassian-Token: no-check header."""
    path: AddAttachmentRequestPath
    body: AddAttachmentRequestBody

# Operation: list_issue_changelogs
class GetChangeLogsRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123).")
class GetChangeLogsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first changelog entry. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of changelog entries to return per page. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class GetChangeLogsRequest(StrictModel):
    """Retrieve a paginated list of all changes made to an issue, sorted chronologically from oldest to newest. Requires browse permission for the project and any applicable issue-level security permissions."""
    path: GetChangeLogsRequestPath
    query: GetChangeLogsRequestQuery | None = None

# Operation: fetch_changelogs
class GetChangeLogsByIdsRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123). Used to locate the issue whose changelogs you want to retrieve.")
class GetChangeLogsByIdsRequestBody(StrictModel):
    changelog_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., validation_alias="changelogIds", serialization_alias="changelogIds", description="A list of changelog IDs to retrieve. Specify the exact IDs of the changelog entries you want to fetch; order is preserved in the response.")
class GetChangeLogsByIdsRequest(StrictModel):
    """Retrieve specific changelogs for an issue by their IDs. Returns detailed change history records for the specified changelog identifiers."""
    path: GetChangeLogsByIdsRequestPath
    body: GetChangeLogsByIdsRequestBody

# Operation: list_issue_comments
class GetCommentsRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123).")
class GetCommentsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of comments to return per page. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
    order_by: Literal["created", "-created", "+created"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort comments by creation date. Use 'created' for ascending order, '-created' for descending order, or '+created' for ascending order.")
class GetCommentsRequest(StrictModel):
    """Retrieve all comments for a specific issue, with support for pagination and sorting. Comments are filtered based on user permissions and visibility restrictions."""
    path: GetCommentsRequestPath
    query: GetCommentsRequestQuery | None = None

# Operation: add_comment
class AddCommentRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class AddCommentRequestBody(StrictModel):
    body: Any | None = Field(default=None, description="The comment text formatted using Atlassian Document Format. This field supports rich text formatting including mentions, links, and other document elements.")
    visibility: AddCommentBodyVisibility | None = Field(default=None, description="Restricts comment visibility to a specific group or role. When omitted, the comment is visible to all users with permission to view the issue.")
class AddCommentRequest(StrictModel):
    """Add a comment to a Jira issue. The comment can be formatted using Atlassian Document Format and optionally restricted to specific groups or roles."""
    path: AddCommentRequestPath
    body: AddCommentRequestBody | None = None

# Operation: get_comment
class GetCommentRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, which can be either the numeric issue ID or the issue key (e.g., PROJ-123).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to retrieve.")
class GetCommentRequest(StrictModel):
    """Retrieve a specific comment from an issue. Requires browse permissions on the project and any applicable issue-level security or comment visibility restrictions."""
    path: GetCommentRequestPath

# Operation: update_comment
class UpdateCommentRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key-based identifier (e.g., PROJ-123).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to update.")
class UpdateCommentRequestQuery(StrictModel):
    notify_users: bool | None = Field(default=None, validation_alias="notifyUsers", serialization_alias="notifyUsers", description="Controls whether users are notified about the comment update. Defaults to true.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Allows bypassing screen security restrictions to edit normally uneditable fields. Only available to administrators and Forge apps with admin privileges. Defaults to false.")
class UpdateCommentRequestBody(StrictModel):
    body: Any | None = Field(default=None, description="The updated comment text formatted as Atlassian Document Format (ADF).")
    visibility: UpdateCommentBodyVisibility | None = Field(default=None, description="Restricts comment visibility to a specific group or role. Child comments inherit visibility from their parent and cannot be modified independently.")
class UpdateCommentRequest(StrictModel):
    """Updates an existing comment on an issue. Requires appropriate permissions to edit the comment and view the issue."""
    path: UpdateCommentRequestPath
    query: UpdateCommentRequestQuery | None = None
    body: UpdateCommentRequestBody | None = None

# Operation: delete_comment
class DeleteCommentRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to delete.")
class DeleteCommentRequest(StrictModel):
    """Removes a comment from an issue. Requires appropriate permissions based on comment ownership and visibility restrictions."""
    path: DeleteCommentRequestPath

# Operation: get_issue_editable_fields
class GetEditIssueMetaRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123).")
class GetEditIssueMetaRequestQuery(StrictModel):
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="When enabled, returns non-editable fields by bypassing workflow editability checks. Only available to administrators. Defaults to false.")
class GetEditIssueMetaRequest(StrictModel):
    """Retrieve the fields that are editable for a specific issue based on the user's permissions, screen configuration, and workflow state. Use this to determine which fields can be modified before submitting an edit request."""
    path: GetEditIssueMetaRequestPath
    query: GetEditIssueMetaRequestQuery | None = None

# Operation: send_issue_notification
class NotifyRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., PROJ-123).")
class NotifyRequestBody(StrictModel):
    """The request object for the notification and recipients."""
    html_body: str | None = Field(default=None, validation_alias="htmlBody", serialization_alias="htmlBody", description="The HTML-formatted body content of the email notification. If provided, this takes precedence over plain text body for HTML-capable email clients.")
    restrict: NotifyBodyRestrict | None = Field(default=None, description="Restricts notification delivery to users who have the specified permission level for the issue.")
    subject: str | None = Field(default=None, description="The subject line of the email notification. If not provided, defaults to the issue key and summary.")
    text_body: str | None = Field(default=None, validation_alias="textBody", serialization_alias="textBody", description="The plain text body content of the email notification. Used as fallback for email clients that don't support HTML.")
    to: NotifyBodyTo | None = Field(default=None, description="The list of recipients who should receive the email notification for this issue.")
class NotifyRequest(StrictModel):
    """Send an email notification for an issue and queue it for delivery. The notification can be customized with subject and body content, and optionally restricted to users with specific permissions."""
    path: NotifyRequestPath
    body: NotifyRequestBody | None = None

# Operation: list_issue_property_keys
class GetIssuePropertyKeysRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, which can be either the issue key (e.g., PROJ-123) or the numeric issue ID.")
class GetIssuePropertyKeysRequest(StrictModel):
    """Retrieves all property keys and their URLs associated with a specific issue. This allows you to discover what custom properties are stored on an issue."""
    path: GetIssuePropertyKeysRequestPath

# Operation: get_issue_property
class GetIssuePropertyRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, which can be either the issue key (e.g., PROJ-123) or the numeric issue ID.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The unique identifier for the property to retrieve from the issue.")
class GetIssuePropertyRequest(StrictModel):
    """Retrieves a specific property value associated with an issue by its property key. Returns both the key and value of the requested issue property."""
    path: GetIssuePropertyRequestPath

# Operation: remove_issue_property
class DeleteIssuePropertyRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the issue key (e.g., PROJ-123) or the numeric issue ID.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The unique key identifying the property to delete from the issue.")
class DeleteIssuePropertyRequest(StrictModel):
    """Removes a custom property from an issue. Requires browse and edit permissions for the project, and issue-level security permission if configured."""
    path: DeleteIssuePropertyRequestPath

# Operation: list_remote_issue_links
class GetRemoteIssueLinksRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID (e.g., 10000) or the issue key (e.g., PROJ-123).")
class GetRemoteIssueLinksRequestQuery(StrictModel):
    global_id: str | None = Field(default=None, validation_alias="globalId", serialization_alias="globalId", description="Optional global ID to retrieve a specific remote issue link. If omitted, all remote issue links for the issue are returned. URL-reserved characters in the global ID must be percent-encoded.")
class GetRemoteIssueLinksRequest(StrictModel):
    """Retrieve remote issue links for an issue, optionally filtered by a specific global ID. Returns all linked remote issues or a single link matching the provided global ID."""
    path: GetRemoteIssueLinksRequestPath
    query: GetRemoteIssueLinksRequestQuery | None = None

# Operation: link_remote_issue
class CreateOrUpdateRemoteIssueLinkRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The Jira issue identifier, either the numeric ID or the issue key (e.g., PROJ-123).")
class CreateOrUpdateRemoteIssueLinkRequestBody(StrictModel):
    application: CreateOrUpdateRemoteIssueLinkBodyApplication | None = Field(default=None, description="Details about the remote application containing the linked item, such as the application name or identifier (e.g., trello, confluence).")
    global_id: str | None = Field(default=None, validation_alias="globalId", serialization_alias="globalId", description="A unique identifier for the remote item in the external system that enables updating or deleting the link using remote system details instead of the Jira record ID. Maximum length is 255 characters.")
    object_: CreateOrUpdateRemoteIssueLinkBodyObject = Field(default=..., validation_alias="object", serialization_alias="object", description="Details about the item being linked to, including its URL, title, and other metadata from the remote system.")
    relationship: str | None = Field(default=None, description="A description of how the issue relates to the linked item. If not specified, defaults to 'links to'.")
class CreateOrUpdateRemoteIssueLinkRequest(StrictModel):
    """Creates or updates a remote issue link to connect an issue with an item in an external system. If a globalId is provided and a matching link exists, it updates the link; otherwise, it creates a new one."""
    path: CreateOrUpdateRemoteIssueLinkRequestPath
    body: CreateOrUpdateRemoteIssueLinkRequestBody

# Operation: get_remote_link
class GetRemoteIssueLinkByIdRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, which can be either the numeric issue ID or the issue key (e.g., PROJECT-123).")
    link_id: str = Field(default=..., validation_alias="linkId", serialization_alias="linkId", description="The unique identifier of the remote issue link to retrieve.")
class GetRemoteIssueLinkByIdRequest(StrictModel):
    """Retrieves a specific remote issue link for an issue. Requires issue linking to be enabled and appropriate project permissions."""
    path: GetRemoteIssueLinkByIdRequestPath

# Operation: update_remote_link
class UpdateRemoteIssueLinkRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the issue key (e.g., 'PROJ-123').")
    link_id: str = Field(default=..., validation_alias="linkId", serialization_alias="linkId", description="The numeric ID of the remote issue link to update.")
class UpdateRemoteIssueLinkRequestBody(StrictModel):
    application: UpdateRemoteIssueLinkBodyApplication | None = Field(default=None, description="Details of the remote application containing the linked item, such as Trello or Confluence.")
    global_id: str | None = Field(default=None, validation_alias="globalId", serialization_alias="globalId", description="A unique identifier for the remote item in its external system (maximum 255 characters). For example, in Confluence this might be formatted as 'appId=456&pageId=123'. Enables updating or deleting the link using remote system details instead of the Jira link ID.")
    object_: UpdateRemoteIssueLinkBodyObject = Field(default=..., validation_alias="object", serialization_alias="object", description="Details of the item being linked to, including its title, URL, and other relevant metadata from the remote system.")
    relationship: str | None = Field(default=None, description="A description of the relationship between the issue and the linked item. If not provided, defaults to 'links to'.")
class UpdateRemoteIssueLinkRequest(StrictModel):
    """Updates an existing remote issue link for a Jira issue. Unspecified fields in the request will be set to null. Requires issue linking to be enabled and appropriate project permissions."""
    path: UpdateRemoteIssueLinkRequestPath
    body: UpdateRemoteIssueLinkRequestBody

# Operation: delete_remote_link_by_id
class DeleteRemoteIssueLinkByIdRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID (e.g., 10000) or the issue key (e.g., PROJ-123).")
    link_id: str = Field(default=..., validation_alias="linkId", serialization_alias="linkId", description="The numeric ID of the remote issue link to delete (e.g., 10000).")
class DeleteRemoteIssueLinkByIdRequest(StrictModel):
    """Removes a remote issue link from an issue. Requires issue linking to be enabled and appropriate project permissions including Browse projects, Edit issues, and Link issues."""
    path: DeleteRemoteIssueLinkByIdRequestPath

# Operation: list_issue_transitions_single
class GetTransitionsRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class GetTransitionsRequestQuery(StrictModel):
    transition_id: str | None = Field(default=None, validation_alias="transitionId", serialization_alias="transitionId", description="Optional ID of a specific transition to retrieve. When provided, only that transition is returned if it exists and is available.")
    include_unavailable_transitions: bool | None = Field(default=None, validation_alias="includeUnavailableTransitions", serialization_alias="includeUnavailableTransitions", description="Whether to include transitions that fail their conditions in the response. Defaults to false, returning only transitions that can currently be performed.")
class GetTransitionsRequest(StrictModel):
    """Retrieve available transitions for an issue based on its current status. Returns all possible transitions the user can perform, or a specific transition if requested. An empty list is returned if the requested transition doesn't exist or cannot be performed given the issue's current status."""
    path: GetTransitionsRequestPath
    query: GetTransitionsRequestQuery | None = None

# Operation: transition_issue
class DoTransitionRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class DoTransitionRequestBody(StrictModel):
    transition: DoTransitionBodyTransition | None = Field(default=None, description="Details of a transition. Required when performing a transition, optional when creating or editing an issue.")
    fields: dict[str, Any] | None = Field(default=None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`.")
    update: dict[str, list[FieldUpdateOperation]] | None = Field(default=None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`.")
class DoTransitionRequest(StrictModel):
    """Move an issue to a new status by performing a transition. If the transition includes a screen, you can update issue fields as part of the transition."""
    path: DoTransitionRequestPath
    body: DoTransitionRequestBody | None = None

# Operation: retrieve_issue_votes
class GetVotesRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class GetVotesRequest(StrictModel):
    """Retrieve voting details for an issue, including vote count and voter information. Requires the voting feature to be enabled in Jira configuration and appropriate project permissions."""
    path: GetVotesRequestPath

# Operation: vote_issue
class AddVoteRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class AddVoteRequest(StrictModel):
    """Register the user's vote on an issue. This action is equivalent to clicking the Vote button in Jira and requires voting to be enabled in Jira's general configuration."""
    path: AddVoteRequestPath

# Operation: remove_vote
class RemoveVoteRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class RemoveVoteRequest(StrictModel):
    """Remove a user's vote from an issue, equivalent to clicking Unvote in Jira. Requires voting to be enabled in Jira's general configuration."""
    path: RemoveVoteRequestPath

# Operation: list_issue_watchers
class GetIssueWatchersRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class GetIssueWatchersRequest(StrictModel):
    """Retrieve the list of users watching an issue. Requires the 'Allow users to watch issues' option to be enabled in Jira's general configuration."""
    path: GetIssueWatchersRequestPath

# Operation: add_issue_watcher
class AddWatcherRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class AddWatcherRequestBody(StrictModel):
    """The account ID of the user. Note that username cannot be used due to privacy changes."""
    body: str = Field(default=..., description="The account ID of the user to add as a watcher. If omitted, the authenticated user making the request is added instead.")
class AddWatcherRequest(StrictModel):
    """Add a user as a watcher to an issue. The user will receive notifications about changes to the issue. If no user is specified, the calling user is added as the watcher."""
    path: AddWatcherRequestPath
    body: AddWatcherRequestBody

# Operation: remove_issue_watcher
class RemoveWatcherRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
class RemoveWatcherRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required.", max_length=128)
class RemoveWatcherRequest(StrictModel):
    """Remove a user from watching an issue. Requires the 'Allow users to watch issues' option to be enabled in Jira's general configuration."""
    path: RemoveWatcherRequestPath
    query: RemoveWatcherRequestQuery | None = None

# Operation: list_issue_worklogs
class GetIssueWorklogRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key (e.g., PROJ-123).")
class GetIssueWorklogRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index for pagination, allowing you to retrieve results starting from a specific position in the list. Defaults to 0 (first page).", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of worklogs to return per page. Defaults to 5000 if not specified.", json_schema_extra={'format': 'int32'})
    started_after: int | None = Field(default=None, validation_alias="startedAfter", serialization_alias="startedAfter", description="Filter to return only worklogs that started on or after this date and time, specified as a UNIX timestamp in milliseconds.", json_schema_extra={'format': 'int64'})
    started_before: int | None = Field(default=None, validation_alias="startedBefore", serialization_alias="startedBefore", description="Filter to return only worklogs that started before this date and time, specified as a UNIX timestamp in milliseconds.", json_schema_extra={'format': 'int64'})
class GetIssueWorklogRequest(StrictModel):
    """Retrieve time tracking worklogs for an issue, ordered chronologically from oldest to newest. Optionally filter worklogs by start date range using UNIX timestamps in milliseconds."""
    path: GetIssueWorklogRequestPath
    query: GetIssueWorklogRequestQuery | None = None

# Operation: record_worklog
class AddWorklogRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue ID or key to record work against.")
class AddWorklogRequestQuery(StrictModel):
    notify_users: bool | None = Field(default=None, validation_alias="notifyUsers", serialization_alias="notifyUsers", description="Whether to notify users watching the issue via email about the worklog entry. Defaults to true.")
    adjust_estimate: Literal["new", "leave", "manual", "auto"] | None = Field(default=None, validation_alias="adjustEstimate", serialization_alias="adjustEstimate", description="How to adjust the issue's remaining time estimate: 'new' sets it to a specific value, 'leave' keeps it unchanged, 'manual' reduces it by a specified amount, or 'auto' reduces it by the time spent in this worklog. Defaults to 'auto'.")
    new_estimate: str | None = Field(default=None, validation_alias="newEstimate", serialization_alias="newEstimate", description="The new remaining time estimate for the issue when adjustEstimate is 'new'. Specify as days (e.g., 2d), hours (e.g., 3h), or minutes (e.g., 30m). Required only when adjustEstimate is 'new'.")
    reduce_by: str | None = Field(default=None, validation_alias="reduceBy", serialization_alias="reduceBy", description="The amount to reduce the issue's remaining estimate by when adjustEstimate is 'manual'. Specify as days (e.g., 2d), hours (e.g., 3h), or minutes (e.g., 30m). Required only when adjustEstimate is 'manual'.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Whether to force adding the worklog even if the issue is not editable (e.g., closed). Only available to Connect and Forge app users with Administer Jira permission. Defaults to false.")
class AddWorklogRequestBody(StrictModel):
    comment: Any | None = Field(default=None, description="An optional comment about the worklog in Atlassian Document Format.")
    started: str | None = Field(default=None, description="The date and time when the work effort started, in ISO 8601 format. Required when creating a worklog.", json_schema_extra={'format': 'date-time'})
    visibility: AddWorklogBodyVisibility | None = Field(default=None, description="Optional visibility restrictions for the worklog, such as restricting it to specific users or groups.")
    time_spent: str | None = Field(default=None, validation_alias="timeSpent", serialization_alias="timeSpent", description="The time spent working on the issue as days (\\#d), hours (\\#h), or minutes (\\#m or \\#). Required when creating a worklog if `timeSpentSeconds` isn't provided. Optional when updating a worklog. Cannot be provided if `timeSpentSecond` is provided.")
    time_spent_seconds: int | None = Field(default=None, validation_alias="timeSpentSeconds", serialization_alias="timeSpentSeconds", description="The time in seconds spent working on the issue. Required when creating a worklog if `timeSpent` isn't provided. Optional when updating a worklog. Cannot be provided if `timeSpent` is provided.", json_schema_extra={'format': 'int64'})
class AddWorklogRequest(StrictModel):
    """Record time spent working on an issue. Time tracking must be enabled in Jira for this operation to succeed. The worklog can optionally update the issue's remaining time estimate based on the time recorded."""
    path: AddWorklogRequestPath
    query: AddWorklogRequestQuery | None = None
    body: AddWorklogRequestBody | None = None

# Operation: delete_worklogs
class BulkDeleteWorklogsRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue ID or key identifying which issue to delete worklogs from.")
class BulkDeleteWorklogsRequestQuery(StrictModel):
    adjust_estimate: Literal["leave", "auto"] | None = Field(default=None, validation_alias="adjustEstimate", serialization_alias="adjustEstimate", description="Controls how the issue's time estimate is updated after deletion. Use 'leave' to keep the estimate unchanged, or 'auto' to automatically reduce it by the total time spent across all deleted worklogs. Defaults to 'auto'.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Set to true to force deletion of worklogs even if the issue is not editable (e.g., closed issues). Only available to Connect and Forge app users with admin permission. Defaults to false.")
class BulkDeleteWorklogsRequestBody(StrictModel):
    """A JSON object containing a list of worklog IDs."""
    ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., description="A list of worklog IDs to delete. All worklogs must belong to the specified issue. Maximum of 5000 IDs per request.")
class BulkDeleteWorklogsRequest(StrictModel):
    """Permanently delete multiple worklogs from an issue. This experimental operation supports bulk deletion of up to 5000 worklogs at once, with no notifications sent to users. Time tracking must be enabled in Jira for this operation to succeed."""
    path: BulkDeleteWorklogsRequestPath
    query: BulkDeleteWorklogsRequestQuery | None = None
    body: BulkDeleteWorklogsRequestBody

# Operation: move_worklogs
class BulkMoveWorklogsRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue ID or key of the source issue containing the worklogs to move.")
class BulkMoveWorklogsRequestQuery(StrictModel):
    adjust_estimate: Literal["leave", "auto"] | None = Field(default=None, validation_alias="adjustEstimate", serialization_alias="adjustEstimate", description="Determines how to update time estimates on both issues. Use 'leave' to keep estimates unchanged, or 'auto' to reduce the source issue estimate by the total time spent and increase the destination issue estimate accordingly. Defaults to 'auto'.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="When true, allows moving worklogs even if the source or destination issues are not editable (e.g., closed issues). Only available to Connect and Forge app users with admin permission. Defaults to false.")
class BulkMoveWorklogsRequestBody(StrictModel):
    """A JSON object containing a list of worklog IDs and the ID or key of the destination issue."""
    issue_id_or_key2: str | None = Field(default=None, validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue ID or key of the destination issue where worklogs will be moved to.")
    ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="A list of worklog IDs to move. Maximum of 5000 worklogs per request. Worklogs with attachments or project role visibility restrictions cannot be moved.")
class BulkMoveWorklogsRequest(StrictModel):
    """Moves a list of worklogs from one issue to another. This experimental operation has limitations: maximum 5000 worklogs per request, no support for worklogs with attachments or project role restrictions, and no notifications, webhooks, or issue history are generated. Time tracking must be enabled in Jira."""
    path: BulkMoveWorklogsRequestPath
    query: BulkMoveWorklogsRequestQuery | None = None
    body: BulkMoveWorklogsRequestBody | None = None

# Operation: get_worklog
class GetWorklogRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the worklog entry to retrieve.")
class GetWorklogRequest(StrictModel):
    """Retrieve a specific worklog entry for an issue. Time tracking must be enabled in Jira for this operation to succeed."""
    path: GetWorklogRequestPath

# Operation: update_worklog
class UpdateWorklogRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key (e.g., PROJ-123).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the worklog entry to update.")
class UpdateWorklogRequestQuery(StrictModel):
    notify_users: bool | None = Field(default=None, validation_alias="notifyUsers", serialization_alias="notifyUsers", description="Whether to send email notifications to users watching the issue. Defaults to true.")
    adjust_estimate: Literal["new", "leave", "manual", "auto"] | None = Field(default=None, validation_alias="adjustEstimate", serialization_alias="adjustEstimate", description="How to adjust the issue's remaining time estimate: 'new' sets a specific value, 'leave' keeps it unchanged, or 'auto' adjusts it based on the difference in time spent. Defaults to 'auto'.")
    new_estimate: str | None = Field(default=None, validation_alias="newEstimate", serialization_alias="newEstimate", description="The new remaining time estimate for the issue when adjustEstimate is set to 'new'. Specify as days (d), hours (h), or minutes (m). Required only when adjustEstimate is 'new'.")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Whether to allow updating the worklog even if the issue is not editable (e.g., closed). Only available to Connect and Forge app users with Administer Jira permission. Defaults to false.")
class UpdateWorklogRequestBody(StrictModel):
    comment: Any | None = Field(default=None, description="A comment about the worklog in Atlassian Document Format. Optional for updates.")
    started: str | None = Field(default=None, description="The date and time when the worklog effort started, in ISO 8601 format. Optional when updating an existing worklog.", json_schema_extra={'format': 'date-time'})
    visibility: UpdateWorklogBodyVisibility | None = Field(default=None, description="Visibility restrictions for the worklog, such as limiting access to specific groups or roles. Optional for updates.")
class UpdateWorklogRequest(StrictModel):
    """Updates an existing worklog entry for an issue. Requires time tracking to be enabled in Jira and appropriate permissions to edit the worklog."""
    path: UpdateWorklogRequestPath
    query: UpdateWorklogRequestQuery | None = None
    body: UpdateWorklogRequestBody | None = None

# Operation: remove_worklog
class DeleteWorklogRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the worklog entry to delete.")
class DeleteWorklogRequestQuery(StrictModel):
    notify_users: bool | None = Field(default=None, validation_alias="notifyUsers", serialization_alias="notifyUsers", description="Whether to send email notifications to users watching the issue. Defaults to true.")
    adjust_estimate: Literal["new", "leave", "manual", "auto"] | None = Field(default=None, validation_alias="adjustEstimate", serialization_alias="adjustEstimate", description="How to adjust the issue's remaining time estimate after deletion. Use 'auto' to reduce by the deleted worklog's time, 'new' to set a specific value, 'manual' to increase by an amount, or 'leave' to keep unchanged. Defaults to 'auto'.")
    new_estimate: str | None = Field(default=None, validation_alias="newEstimate", serialization_alias="newEstimate", description="The new remaining time estimate for the issue when adjustEstimate is set to 'new'. Specify as a duration using days (d), hours (h), or minutes (m).")
    increase_by: str | None = Field(default=None, validation_alias="increaseBy", serialization_alias="increaseBy", description="The amount to increase the remaining time estimate when adjustEstimate is set to 'manual'. Specify as a duration using days (d), hours (h), or minutes (m).")
    override_editable_flag: bool | None = Field(default=None, validation_alias="overrideEditableFlag", serialization_alias="overrideEditableFlag", description="Whether to allow deletion even if the issue is not editable (e.g., closed or read-only). Only available to Connect and Forge app users with admin permission. Defaults to false.")
class DeleteWorklogRequest(StrictModel):
    """Remove a worklog entry from an issue and optionally adjust the issue's time estimate. Requires time tracking to be enabled in Jira and appropriate permissions to delete worklogs."""
    path: DeleteWorklogRequestPath
    query: DeleteWorklogRequestQuery | None = None

# Operation: list_worklog_property_keys
class GetWorklogPropertyKeysRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, which can be either the numeric issue ID or the issue key (e.g., PROJECT-123).")
    worklog_id: str = Field(default=..., validation_alias="worklogId", serialization_alias="worklogId", description="The unique identifier of the worklog entry within the specified issue.")
class GetWorklogPropertyKeysRequest(StrictModel):
    """Retrieves all property keys associated with a specific worklog entry. Use this to discover what custom properties are available for a worklog before retrieving their values."""
    path: GetWorklogPropertyKeysRequestPath

# Operation: get_worklog_property
class GetWorklogPropertyRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the human-readable key (e.g., PROJ-123).")
    worklog_id: str = Field(default=..., validation_alias="worklogId", serialization_alias="worklogId", description="The unique identifier of the worklog entry from which to retrieve the property.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The name of the property to retrieve from the worklog.")
class GetWorklogPropertyRequest(StrictModel):
    """Retrieves a specific property value associated with a worklog entry. Requires appropriate project and issue permissions, plus any worklog visibility restrictions must be satisfied."""
    path: GetWorklogPropertyRequestPath

# Operation: remove_worklog_property
class DeleteWorklogPropertyRequestPath(StrictModel):
    issue_id_or_key: str = Field(default=..., validation_alias="issueIdOrKey", serialization_alias="issueIdOrKey", description="The issue identifier, either the numeric ID or the project key followed by issue number (e.g., PROJ-123).")
    worklog_id: str = Field(default=..., validation_alias="worklogId", serialization_alias="worklogId", description="The unique identifier of the worklog entry from which the property will be removed.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The identifier of the custom property to delete from the worklog.")
class DeleteWorklogPropertyRequest(StrictModel):
    """Removes a custom property from a worklog entry. Requires appropriate project and worklog visibility permissions."""
    path: DeleteWorklogPropertyRequestPath

# Operation: create_issue_link
class LinkIssuesRequestBodyComment(StrictModel):
    body: Any | None = Field(default=None, validation_alias="body", serialization_alias="body", description="The comment text to add to the outward issue, formatted as Atlassian Document Format. Optional on creation.")
    visibility: LinkIssuesBodyCommentVisibility | None = Field(default=None, validation_alias="visibility", serialization_alias="visibility", description="The group or role to which the comment visibility is restricted. Optional; if omitted, the comment is visible to all users with permission to view the issue.")
class LinkIssuesRequestBodyInwardIssue(StrictModel):
    key: str | None = Field(default=None, validation_alias="key", serialization_alias="key", description="The key of the inward (destination) issue. Required unless the issue ID is provided instead.")
class LinkIssuesRequestBodyOutwardIssue(StrictModel):
    key: str | None = Field(default=None, validation_alias="key", serialization_alias="key", description="The key of the outward (source) issue. Required unless the issue ID is provided instead.")
class LinkIssuesRequestBodyType(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the issue link type and is used as follows:\n\n *  In the [ issueLink](#api-rest-api-3-issueLink-post) resource it is the type of issue link. Required on create when `name` isn't provided. Otherwise, read only.\n *  In the [ issueLinkType](#api-rest-api-3-issueLinkType-post) resource it is read only.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the issue link type and is used as follows:\n\n *  In the [ issueLink](#api-rest-api-3-issueLink-post) resource it is the type of issue link. Required on create when `id` isn't provided. Otherwise, read only.\n *  In the [ issueLinkType](#api-rest-api-3-issueLinkType-post) resource it is required on create and optional on update. Otherwise, read only.")
class LinkIssuesRequestBody(StrictModel):
    """The issue link request."""
    comment: LinkIssuesRequestBodyComment | None = None
    inward_issue: LinkIssuesRequestBodyInwardIssue | None = Field(default=None, validation_alias="inwardIssue", serialization_alias="inwardIssue")
    outward_issue: LinkIssuesRequestBodyOutwardIssue | None = Field(default=None, validation_alias="outwardIssue", serialization_alias="outwardIssue")
    type_: LinkIssuesRequestBodyType | None = Field(default=None, validation_alias="type", serialization_alias="type")
class LinkIssuesRequest(StrictModel):
    """Creates a link between two issues to indicate a relationship. Optionally adds a comment to the outward issue. Requires Issue Linking to be enabled on the site."""
    body: LinkIssuesRequestBody | None = None

# Operation: get_issue_link
class GetIssueLinkRequestPath(StrictModel):
    link_id: str = Field(default=..., validation_alias="linkId", serialization_alias="linkId", description="The unique identifier of the issue link to retrieve.")
class GetIssueLinkRequest(StrictModel):
    """Retrieves details about a specific issue link by its ID. Returns the link information if you have permission to view both linked issues."""
    path: GetIssueLinkRequestPath

# Operation: remove_issue_link
class DeleteIssueLinkRequestPath(StrictModel):
    link_id: str = Field(default=..., validation_alias="linkId", serialization_alias="linkId", description="The unique identifier of the issue link to delete.")
class DeleteIssueLinkRequest(StrictModel):
    """Removes a link between two issues. Requires browse and link issue permissions for the affected projects, and view access if issue-level security is configured."""
    path: DeleteIssueLinkRequestPath

# Operation: get_issue_link_type
class GetIssueLinkTypeRequestPath(StrictModel):
    issue_link_type_id: str = Field(default=..., validation_alias="issueLinkTypeId", serialization_alias="issueLinkTypeId", description="The unique identifier of the issue link type to retrieve.")
class GetIssueLinkTypeRequest(StrictModel):
    """Retrieves the details of a specific issue link type by its ID. Requires issue linking to be enabled on the site and the user to have Browse projects permission."""
    path: GetIssueLinkTypeRequestPath

# Operation: delete_issue_link_type
class DeleteIssueLinkTypeRequestPath(StrictModel):
    issue_link_type_id: str = Field(default=..., validation_alias="issueLinkTypeId", serialization_alias="issueLinkTypeId", description="The unique identifier of the issue link type to delete.")
class DeleteIssueLinkTypeRequest(StrictModel):
    """Permanently deletes an issue link type from your Jira instance. Requires issue linking to be enabled and Administer Jira global permission."""
    path: DeleteIssueLinkTypeRequestPath

# Operation: export_archived_issues
class ExportArchivedIssuesRequestBodyArchivedDateRange(StrictModel):
    date_after: str = Field(default=..., validation_alias="dateAfter", serialization_alias="dateAfter", description="Include only issues archived on or after this date. Specify in YYYY-MM-DD format.")
    date_before: str = Field(default=..., validation_alias="dateBefore", serialization_alias="dateBefore", description="Include only issues archived on or before this date. Specify in YYYY-MM-DD format.")
class ExportArchivedIssuesRequestBody(StrictModel):
    """You can filter the issues in your request by the `projects`, `archivedBy`, `archivedDate`, `issueTypes`, and `reporters` fields. All filters are optional. If you don't provide any filters, you'll get a list of up to one million archived issues."""
    archived_by: list[str] | None = Field(default=None, validation_alias="archivedBy", serialization_alias="archivedBy", description="Filter results to include only issues archived by specific user account IDs. Provide as a list of account identifiers.")
    issue_types: list[str] | None = Field(default=None, validation_alias="issueTypes", serialization_alias="issueTypes", description="Filter results to include only issues of specified issue type IDs. Provide as a list of type identifiers.")
    projects: list[str] | None = Field(default=None, description="Filter results to include only issues from specified project keys. Provide as a list of project key identifiers.")
    reporters: list[str] | None = Field(default=None, description="Filter results to include only issues reported by specific user account IDs. Provide as a list of account identifiers.")
    archived_date_range: ExportArchivedIssuesRequestBodyArchivedDateRange = Field(default=..., validation_alias="archivedDateRange", serialization_alias="archivedDateRange")
class ExportArchivedIssuesRequest(StrictModel):
    """Export archived issues to a CSV file for download. An admin can filter archived issues by date range, project, issue type, reporter, or archival user, and will receive an email with a download link upon completion."""
    body: ExportArchivedIssuesRequestBody

# Operation: list_issue_types_project
class GetIssueTypesForProjectRequestQuery(StrictModel):
    project_id: int = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="The numeric identifier of the project. This is a 64-bit integer that uniquely identifies the project in your Jira instance.", json_schema_extra={'format': 'int64'})
    level: int | None = Field(default=None, description="Optional filter to retrieve issue types at a specific hierarchy level: use -1 for Subtasks, 0 for Base issue types, or 1 for Epics. Omit this parameter to retrieve all issue types regardless of level.", json_schema_extra={'format': 'int32'})
class GetIssueTypesForProjectRequest(StrictModel):
    """Retrieves all issue types available for a specific project, optionally filtered by type hierarchy level (Subtask, Base, or Epic)."""
    query: GetIssueTypesForProjectRequestQuery

# Operation: get_issue_type
class GetIssueTypeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue type to retrieve.")
class GetIssueTypeRequest(StrictModel):
    """Retrieves detailed information about a specific issue type by its ID. Requires either Browse projects permission in an associated project or Jira administrator access."""
    path: GetIssueTypeRequestPath

# Operation: delete_issue_type
class DeleteIssueTypeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue type to delete.")
class DeleteIssueTypeRequestQuery(StrictModel):
    alternative_issue_type_id: str | None = Field(default=None, validation_alias="alternativeIssueTypeId", serialization_alias="alternativeIssueTypeId", description="The unique identifier of the issue type to use as a replacement for any issues currently using the deleted type. Required if the issue type being deleted is in use.")
class DeleteIssueTypeRequest(StrictModel):
    """Deletes an issue type from your Jira instance. If the issue type is currently in use, all associated issues are automatically reassigned to a replacement issue type that you specify."""
    path: DeleteIssueTypeRequestPath
    query: DeleteIssueTypeRequestQuery | None = None

# Operation: list_alternative_issue_types
class GetAlternativeIssueTypesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue type for which to find compatible alternatives.")
class GetAlternativeIssueTypesRequest(StrictModel):
    """Retrieve a list of issue types that can replace a given issue type. The alternatives are those sharing the same workflow scheme, field configuration scheme, and screen scheme."""
    path: GetAlternativeIssueTypesRequestPath

# Operation: upload_issue_type_avatar
class CreateIssueTypeAvatarRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue type to which the avatar will be assigned.")
class CreateIssueTypeAvatarRequestQuery(StrictModel):
    x: int | None = Field(default=None, description="The horizontal pixel position of the top-left corner of the crop region. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    y: int | None = Field(default=None, description="The vertical pixel position of the top-left corner of the crop region. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    size: int = Field(default=..., description="The width and height in pixels of the square crop region. This determines the size of the cropped area before resizing.", json_schema_extra={'format': 'int32'})
class CreateIssueTypeAvatarRequest(StrictModel):
    """Upload and set a custom avatar image for an issue type. The image is automatically cropped to a square and resized into multiple formats (16x16, 24x24, 32x32, 48x48 pixels). Requires Administer Jira global permission."""
    path: CreateIssueTypeAvatarRequestPath
    query: CreateIssueTypeAvatarRequestQuery

# Operation: list_issue_type_property_keys
class GetIssueTypePropertyKeysRequestPath(StrictModel):
    issue_type_id: str = Field(default=..., validation_alias="issueTypeId", serialization_alias="issueTypeId", description="The unique identifier of the issue type whose property keys you want to retrieve.")
class GetIssueTypePropertyKeysRequest(StrictModel):
    """Retrieves all property keys stored on a specific issue type. Property keys are identifiers for custom data attached to the issue type entity."""
    path: GetIssueTypePropertyKeysRequestPath

# Operation: get_issue_type_property
class GetIssueTypePropertyRequestPath(StrictModel):
    issue_type_id: str = Field(default=..., validation_alias="issueTypeId", serialization_alias="issueTypeId", description="The unique identifier of the issue type whose property you want to retrieve.")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The key identifying which property to retrieve. Use the list issue type property keys operation to discover available property keys for an issue type.")
class GetIssueTypePropertyRequest(StrictModel):
    """Retrieves a specific property value stored on an issue type by its key. Returns both the key and value of the requested issue type property."""
    path: GetIssueTypePropertyRequestPath

# Operation: list_issue_type_schemes
class GetAllIssueTypeSchemesRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first item. Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of issue type schemes to return per page. Defaults to 50 items per page.", json_schema_extra={'format': 'int32'})
    order_by: Literal["name", "-name", "+name", "id", "-id", "+id"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort results by issue type scheme name or ID, with optional ascending (+) or descending (-) direction. Defaults to sorting by ID.")
    query_string: str | None = Field(default=None, validation_alias="queryString", serialization_alias="queryString", description="Filter results by performing a case-insensitive partial match against issue type scheme names.")
class GetAllIssueTypeSchemesRequest(StrictModel):
    """Retrieve a paginated list of issue type schemes used in classic Jira projects. Requires Administer Jira global permission."""
    query: GetAllIssueTypeSchemesRequestQuery | None = None

# Operation: list_issue_type_schemes_for_projects
class GetIssueTypeSchemeForProjectsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through large result sets.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of results to return per page. Defaults to 50 items if not specified.", json_schema_extra={'format': 'int32'})
    project_id: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="One or more project IDs to filter schemes by. Provide multiple IDs as an ampersand-separated list in the query string.")
class GetIssueTypeSchemeForProjectsRequest(StrictModel):
    """Retrieve issue type schemes used by specified projects in classic Jira instances. Returns a paginated list showing which projects use each scheme."""
    query: GetIssueTypeSchemeForProjectsRequestQuery

# Operation: list_jql_autocomplete_data_filtered
class GetAutoCompletePostRequestBody(StrictModel):
    include_collapsed_fields: bool | None = Field(default=None, validation_alias="includeCollapsedFields", serialization_alias="includeCollapsedFields", description="Include collapsed fields that allow searches across multiple fields with the same name and type. Disabled by default.")
    project_ids: list[int] | None = Field(default=None, validation_alias="projectIds", serialization_alias="projectIds", description="Filter returned field details by one or more project IDs. Invalid project IDs are ignored; system fields are always included regardless of this filter.")
class GetAutoCompletePostRequest(StrictModel):
    """Retrieve JQL field and function reference data to support programmatic query building and validation. Returns system fields always, with optional filtering by project and support for collapsed fields that enable cross-field searches."""
    body: GetAutoCompletePostRequestBody | None = None

# Operation: get_jql_autocomplete_suggestions
class GetFieldAutoCompleteForQueryStringRequestQuery(StrictModel):
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The JQL field name to get suggestions for (e.g., 'reporter'). Required to initiate any suggestion query.")
    field_value: str | None = Field(default=None, validation_alias="fieldValue", serialization_alias="fieldValue", description="Partial field value entered by the user to filter suggestions. When provided with fieldName, returns values containing this text.")
    predicate_name: str | None = Field(default=None, validation_alias="predicateName", serialization_alias="predicateName", description="The CHANGED operator predicate name for which to generate suggestions. Valid values are 'by', 'from', or 'to'. Use with fieldName to get predicate-specific suggestions.")
    predicate_value: str | None = Field(default=None, validation_alias="predicateValue", serialization_alias="predicateValue", description="Partial predicate value entered by the user to filter suggestions. When provided with predicateName and fieldName, returns predicate values containing this text.")
class GetFieldAutoCompleteForQueryStringRequest(StrictModel):
    """Retrieve JQL search autocomplete suggestions for a field, optionally filtered by field value or predicate criteria. Use this to populate autocomplete dropdowns when users are constructing JQL queries."""
    query: GetFieldAutoCompleteForQueryStringRequestQuery | None = None

# Operation: filter_issues_by_jql
class MatchIssuesRequestBody(StrictModel):
    issue_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., validation_alias="issueIds", serialization_alias="issueIds", description="A list of issue IDs to evaluate against the JQL queries. Each ID must correspond to an issue the user has permission to view.")
    jqls: list[str] = Field(default=..., description="A list of JQL (Jira Query Language) queries to match against the provided issues. Each query is evaluated independently for each issue.")
class MatchIssuesRequest(StrictModel):
    """Evaluate whether specified issues match one or more JQL queries. Returns matching results for each issue-query combination, respecting project permissions and issue-level security."""
    body: MatchIssuesRequestBody

# Operation: validate_jql_queries
class ParseJqlQueriesRequestQuery(StrictModel):
    validation: Literal["strict", "warn", "none"] = Field(default=..., description="Validation mode that determines how strictly to validate queries and what to return on errors. Use 'strict' to reject malformed queries entirely, 'warn' to return structure even if errors exist, or 'none' to skip validation and only check syntax.")
class ParseJqlQueriesRequestBody(StrictModel):
    queries: list[str] = Field(default=..., description="One or more JQL query strings to parse and validate. Each query is processed independently.", min_length=1)
class ParseJqlQueriesRequest(StrictModel):
    """Validates and parses JQL (Jira Query Language) queries to check syntax and structure. Returns parsed query details based on the specified validation mode."""
    query: ParseJqlQueriesRequestQuery
    body: ParseJqlQueriesRequestBody

# Operation: list_labels
class GetAllLabelsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to skip earlier results and navigate through pages.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of labels to return in a single page, with a default of 1000 items per page.", json_schema_extra={'format': 'int32'})
class GetAllLabelsRequest(StrictModel):
    """Retrieve a paginated list of all available labels in the system. Use pagination parameters to control which results are returned."""
    query: GetAllLabelsRequestQuery | None = None

# Operation: check_permissions
class GetMyPermissionsRequestQuery(StrictModel):
    project_id: str | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The project ID to check permissions within. When provided, project-level permissions are evaluated for this specific project.")
    issue_id: str | None = Field(default=None, validation_alias="issueId", serialization_alias="issueId", description="The issue ID to check permissions within. When provided, permissions are evaluated in the context of this specific issue, with issue-based permissions determined by the user's relationship to the issue.")
    permissions: str | None = Field(default=None, description="A comma-separated list of permission keys to check (required when querying specific permissions). Use the Get all permissions operation to discover available permission keys.")
    comment_id: str | None = Field(default=None, validation_alias="commentId", serialization_alias="commentId", description="The comment ID to check permissions within. Only the BROWSE_PROJECTS permission is supported for comment context. When provided, the user must have both permission to browse the comment and the project permission for the comment's parent issue.")
class GetMyPermissionsRequest(StrictModel):
    """Check which permissions the authenticated or anonymous user has in a specific context (global, project, issue, or comment). Permissions are evaluated based on the user's roles and the context provided, with issue-based permissions determined by the user's relationship to that issue."""
    query: GetMyPermissionsRequestQuery | None = None

# Operation: get_user_preference
class GetPreferenceRequestQuery(StrictModel):
    key: str = Field(default=..., description="The preference key to retrieve (e.g., jira.user.locale, jira.user.timezone, user.notifications.watcher). Note that some keys like jira.user.locale and jira.user.timezone are deprecated; use the user management API instead to manage timezone and locale.")
class GetPreferenceRequest(StrictModel):
    """Retrieves a specific preference value for the current user. Use this to fetch user settings like notifications, locale, or timezone preferences."""
    query: GetPreferenceRequestQuery

# Operation: list_notification_scheme_project_mappings
class GetNotificationSchemeToProjectMappingsRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through pages of results.")
    max_results: str | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of items to return per page. Defaults to 50 items if not specified.")
    notification_scheme_id: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="notificationSchemeId", serialization_alias="notificationSchemeId", description="One or more notification scheme IDs to filter the results. Only mappings for these schemes will be returned.")
    project_id: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="One or more project IDs to filter the results. Only mappings for these projects will be returned.")
class GetNotificationSchemeToProjectMappingsRequest(StrictModel):
    """Retrieve a paginated list of projects and their assigned notification schemes. Filter results by specific notification scheme IDs or project IDs, or retrieve all mappings. Only company-managed projects are supported."""
    query: GetNotificationSchemeToProjectMappingsRequestQuery | None = None

# Operation: check_permissions_bulk
class GetBulkPermissionsRequestBody(StrictModel):
    """Details of the permissions to check."""
    global_permissions: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="globalPermissions", serialization_alias="globalPermissions", description="List of global permission keys to check. Only permissions included in this list will be evaluated for the user.")
    project_permissions: Annotated[list[BulkProjectPermissions], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="projectPermissions", serialization_alias="projectPermissions", description="Project and issue-specific permissions to check. For each permission, specify the projects and issues to validate access against. Up to 1000 projects and 1000 issues can be checked per request; invalid IDs are ignored.")
class GetBulkPermissionsRequest(StrictModel):
    """Verify which global and project permissions a user has, optionally checking access to specific projects and issues. Returns granted permissions and accessible resources for the specified user or the authenticated user if no account ID is provided."""
    body: GetBulkPermissionsRequestBody | None = None

# Operation: list_permitted_projects
class GetPermittedProjectsRequestBody(StrictModel):
    permissions: list[str] = Field(default=..., description="A list of permission keys to filter projects by. Only projects where the user has all specified permissions will be returned. Permission keys should be provided as strings in the array.")
class GetPermittedProjectsRequest(StrictModel):
    """Retrieve all projects where the authenticated user has been granted specific permissions. This operation helps identify which projects a user can access based on their assigned permission keys."""
    body: GetPermittedProjectsRequestBody

# Operation: list_plans
class GetPlansRequestQuery(StrictModel):
    include_trashed: bool | None = Field(default=None, validation_alias="includeTrashed", serialization_alias="includeTrashed", description="Include trashed plans in the results. By default, only active plans are returned.")
    include_archived: bool | None = Field(default=None, validation_alias="includeArchived", serialization_alias="includeArchived", description="Include archived plans in the results. By default, only active plans are returned.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of plans to return per page. Must be between 1 and 50, defaults to 50.", json_schema_extra={'format': 'int32'})
class GetPlansRequest(StrictModel):
    """Retrieve a paginated list of plans. Requires Jira administrator permissions. Optionally filter results to include trashed or archived plans."""
    query: GetPlansRequestQuery | None = None

# Operation: create_plan
class CreatePlanRequestBody(StrictModel):
    cross_project_releases: Annotated[list[CreateCrossProjectReleaseRequest], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="crossProjectReleases", serialization_alias="crossProjectReleases", description="List of cross-project releases to include in the plan. Allows the plan to span multiple projects.")
    custom_fields: Annotated[list[CreateCustomFieldRequest], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="customFields", serialization_alias="customFields", description="Custom fields to associate with the plan. Specify as an array of field configurations.")
    exclusion_rules: CreatePlanBodyExclusionRules | None = Field(default=None, validation_alias="exclusionRules", serialization_alias="exclusionRules", description="Rules that define which issues should be excluded from the plan based on specified criteria.")
    issue_sources: Annotated[list[CreateIssueSourceRequest], AfterValidator(_check_unique_items)] = Field(default=..., validation_alias="issueSources", serialization_alias="issueSources", description="The issue sources that populate the plan. This determines which issues are included and must be specified as an array of source identifiers or configurations.")
    name: str = Field(default=..., description="The name of the plan. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    permissions: Annotated[list[CreatePermissionRequest], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Access control settings that define which users or groups can view or modify the plan.")
    scheduling: CreatePlanBodyScheduling = Field(default=..., description="Scheduling configuration for the plan, including timeline and release dates. Specifies how issues are scheduled within the plan.")
class CreatePlanRequest(StrictModel):
    """Creates a new plan in Jira with specified issue sources, scheduling configuration, and optional cross-project releases and custom fields. Requires Administer Jira global permission."""
    body: CreatePlanRequestBody

# Operation: retrieve_plan
class GetPlanRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to retrieve, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetPlanRequest(StrictModel):
    """Retrieves detailed information about a specific plan by its ID. Requires Jira administrator permissions."""
    path: GetPlanRequestPath

# Operation: update_plan
class UpdatePlanRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdatePlanRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="JSON Patch document (RFC 6902) containing one or more operations to update plan properties. Each operation specifies an action (add, replace, remove), a JSON pointer path to the target property, and the new value. Supports updates to: name, leadAccountId, scheduling (estimation type, start/end dates, inferred dates, dependencies), issueSources, exclusionRules, crossProjectReleases, customFields, and permissions.", examples=['[{"op": "replace", "path": "/scheduling/estimation", "value": "Days"}]\n'])
class UpdatePlanRequest(StrictModel):
    """Updates plan details including name, lead account, scheduling configuration, issue sources, exclusion rules, cross-project releases, custom fields, and permissions using JSON Patch operations. Requires Administer Jira global permission."""
    path: UpdatePlanRequestPath
    body: UpdatePlanRequestBody

# Operation: archive_plan
class ArchivePlanRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to archive, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class ArchivePlanRequest(StrictModel):
    """Archives a plan, removing it from active use while preserving its data. Requires Administer Jira global permission."""
    path: ArchivePlanRequestPath

# Operation: duplicate_plan
class DuplicatePlanRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to duplicate. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class DuplicatePlanRequestBody(StrictModel):
    name: str = Field(default=..., description="The name for the duplicated plan. This will be the display name of the new plan copy.")
class DuplicatePlanRequest(StrictModel):
    """Creates a duplicate copy of an existing plan with a new name. Requires Administer Jira global permission."""
    path: DuplicatePlanRequestPath
    body: DuplicatePlanRequestBody

# Operation: list_plan_teams
class GetTeamsRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan for which to retrieve teams.", json_schema_extra={'format': 'int64'})
class GetTeamsRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of teams to return per page, up to a maximum of 50. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetTeamsRequest(StrictModel):
    """Retrieve a paginated list of all teams associated with a plan, including both plan-only teams and Atlassian teams. Requires Administer Jira global permission."""
    path: GetTeamsRequestPath
    query: GetTeamsRequestQuery | None = None

# Operation: add_team_to_plan
class AddAtlassianTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to which the team will be added.", json_schema_extra={'format': 'int64'})
class AddAtlassianTeamRequestBody(StrictModel):
    capacity: float | None = Field(default=None, description="The team's capacity allocation for the plan, expressed as a numeric value.", json_schema_extra={'format': 'double'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Atlassian team to add to the plan.")
    issue_source_id: int | None = Field(default=None, validation_alias="issueSourceId", serialization_alias="issueSourceId", description="The identifier of the issue source that will supply work items for this team's planning.", json_schema_extra={'format': 'int64'})
    planning_style: Literal["Scrum", "Kanban"] = Field(default=..., validation_alias="planningStyle", serialization_alias="planningStyle", description="The planning methodology for the team: either Scrum for sprint-based planning or Kanban for continuous flow.")
    sprint_length: int | None = Field(default=None, validation_alias="sprintLength", serialization_alias="sprintLength", description="The duration of sprints in days for Scrum-based teams.", json_schema_extra={'format': 'int64'})
class AddAtlassianTeamRequest(StrictModel):
    """Adds an existing Atlassian team to a plan and configures their planning settings including capacity, planning methodology, and sprint configuration."""
    path: AddAtlassianTeamRequestPath
    body: AddAtlassianTeamRequestBody

# Operation: get_team
class GetAtlassianTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan containing the team. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
    atlassian_team_id: str = Field(default=..., validation_alias="atlassianTeamId", serialization_alias="atlassianTeamId", description="The unique identifier of the Atlassian team whose planning settings should be retrieved.")
class GetAtlassianTeamRequest(StrictModel):
    """Retrieve planning settings and configuration for an Atlassian team within a specific plan. Requires Administer Jira global permission."""
    path: GetAtlassianTeamRequestPath

# Operation: update_team_planning_settings
class UpdateAtlassianTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan containing the team. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    atlassian_team_id: str = Field(default=..., validation_alias="atlassianTeamId", serialization_alias="atlassianTeamId", description="The unique identifier of the Atlassian team to update within the plan.")
class UpdateAtlassianTeamRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="JSON Patch operations array specifying the updates to apply. Each operation must include 'op' (replace/add/remove), 'path' (e.g., /planningStyle, /sprintLength, /capacity, /issueSourceId), and 'value' for replace/add operations. Array order is not significant for add operations; retrieve the current team configuration to determine existing element positions.", examples=['[{"op": "replace", "path": "/planningStyle", "value": "Kanban"}]\n'])
class UpdateAtlassianTeamRequest(StrictModel):
    """Modify planning configuration for an Atlassian team within a plan, including planning style, issue source, sprint length, and capacity settings. Uses JSON Patch format for updates."""
    path: UpdateAtlassianTeamRequestPath
    body: UpdateAtlassianTeamRequestBody

# Operation: remove_team_from_plan
class RemoveAtlassianTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan from which the team will be removed. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
    atlassian_team_id: str = Field(default=..., validation_alias="atlassianTeamId", serialization_alias="atlassianTeamId", description="The unique identifier of the Atlassian team to remove from the plan.")
class RemoveAtlassianTeamRequest(StrictModel):
    """Remove an Atlassian team from a plan and delete their associated planning settings. Requires Administer Jira global permission."""
    path: RemoveAtlassianTeamRequestPath

# Operation: create_plan_only_team
class CreatePlanOnlyTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to which the team will be added.", json_schema_extra={'format': 'int64'})
class CreatePlanOnlyTeamRequestBody(StrictModel):
    capacity: float | None = Field(default=None, description="The team's capacity allocation for planning purposes, expressed as a decimal number.", json_schema_extra={'format': 'double'})
    issue_source_id: int | None = Field(default=None, validation_alias="issueSourceId", serialization_alias="issueSourceId", description="The unique identifier of the issue source that will supply work items to this plan-only team.", json_schema_extra={'format': 'int64'})
    member_account_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="memberAccountIds", serialization_alias="memberAccountIds", description="A list of Jira account IDs for the team members to be added to this plan-only team.")
    name: str = Field(default=..., description="The name of the plan-only team. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    planning_style: Literal["Scrum", "Kanban"] = Field(default=..., validation_alias="planningStyle", serialization_alias="planningStyle", description="The planning methodology for the team. Must be either 'Scrum' for sprint-based planning or 'Kanban' for continuous flow.")
    sprint_length: int | None = Field(default=None, validation_alias="sprintLength", serialization_alias="sprintLength", description="The duration of sprints for this team, specified in days. Only applicable when using Scrum planning style.", json_schema_extra={'format': 'int64'})
class CreatePlanOnlyTeamRequest(StrictModel):
    """Creates a plan-only team within a Jira plan and configures their planning settings, including capacity, members, and sprint configuration. Requires Administer Jira global permission."""
    path: CreatePlanOnlyTeamRequestPath
    body: CreatePlanOnlyTeamRequestBody

# Operation: get_plan_only_team
class GetPlanOnlyTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan containing the team. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    plan_only_team_id: int = Field(default=..., validation_alias="planOnlyTeamId", serialization_alias="planOnlyTeamId", description="The unique identifier of the plan-only team whose settings you want to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetPlanOnlyTeamRequest(StrictModel):
    """Retrieve planning settings and configuration for a specific plan-only team within a plan. Requires Jira administrator permissions."""
    path: GetPlanOnlyTeamRequestPath

# Operation: update_plan_team
class UpdatePlanOnlyTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan containing the team. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    plan_only_team_id: int = Field(default=..., validation_alias="planOnlyTeamId", serialization_alias="planOnlyTeamId", description="The unique identifier of the plan-only team to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdatePlanOnlyTeamRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="JSON Patch operations array specifying the updates to apply. Each operation must include 'op' (replace, add, remove), 'path' (target field), and 'value' (for replace/add operations). Note that add operations do not respect array indexes; retrieve the team first to determine current array order.", examples=['[{"op": "replace", "path": "/planningStyle", "value": "Kanban"}]\n'])
class UpdatePlanOnlyTeamRequest(StrictModel):
    """Update planning settings for a plan-only team, including name, planning style, issue source, sprint length, capacity, and team members. Uses JSON Patch format to specify changes."""
    path: UpdatePlanOnlyTeamRequestPath
    body: UpdatePlanOnlyTeamRequestBody

# Operation: remove_plan_only_team
class DeletePlanOnlyTeamRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan containing the team to be removed. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    plan_only_team_id: int = Field(default=..., validation_alias="planOnlyTeamId", serialization_alias="planOnlyTeamId", description="The unique identifier of the plan-only team to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeletePlanOnlyTeamRequest(StrictModel):
    """Removes a plan-only team from a plan and deletes their associated planning settings. Requires Jira administrator permissions."""
    path: DeletePlanOnlyTeamRequestPath

# Operation: trash_plan
class TrashPlanRequestPath(StrictModel):
    plan_id: int = Field(default=..., validation_alias="planId", serialization_alias="planId", description="The unique identifier of the plan to move to trash. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class TrashPlanRequest(StrictModel):
    """Move a plan to trash, removing it from active use. Requires Administer Jira global permission."""
    path: TrashPlanRequestPath

# Operation: get_priority
class GetPriorityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue priority to retrieve.")
class GetPriorityRequest(StrictModel):
    """Retrieve details of a specific issue priority in Jira. Returns the priority configuration including its name, description, and other metadata."""
    path: GetPriorityRequestPath

# Operation: remove_priority
class DeletePriorityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the priority to delete.")
class DeletePriorityRequest(StrictModel):
    """Removes an issue priority from the Jira instance. This is an asynchronous operation; check the returned location link to monitor task status."""
    path: DeletePriorityRequestPath

# Operation: list_available_priorities
class GetAvailablePrioritiesByPrioritySchemeRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through large result sets.")
    max_results: str | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of priorities to return per page. Defaults to 50 items if not specified.")
    scheme_id: str = Field(default=..., validation_alias="schemeId", serialization_alias="schemeId", description="The unique identifier of the priority scheme for which to retrieve available priorities.")
class GetAvailablePrioritiesByPrioritySchemeRequest(StrictModel):
    """Retrieves a paginated list of priorities that can be added to a specific priority scheme. Use this to discover which priorities are available for assignment within your priority scheme."""
    query: GetAvailablePrioritiesByPrioritySchemeRequestQuery

# Operation: list_priorities
class GetPrioritiesByPrioritySchemeRequestPath(StrictModel):
    scheme_id: str = Field(default=..., validation_alias="schemeId", serialization_alias="schemeId", description="The unique identifier of the priority scheme from which to retrieve priorities.")
class GetPrioritiesByPrioritySchemeRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large result sets. Defaults to 0 if not specified.")
    max_results: str | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of priorities to return in a single page of results. Defaults to 50 if not specified.")
class GetPrioritiesByPrioritySchemeRequest(StrictModel):
    """Retrieves a paginated list of priorities configured in a specific priority scheme. Use this to fetch all available priorities for a given scheme with optional pagination control."""
    path: GetPrioritiesByPrioritySchemeRequestPath
    query: GetPrioritiesByPrioritySchemeRequestQuery | None = None

# Operation: create_project
class CreateProjectRequestBody(StrictModel):
    """The JSON representation of the project being created."""
    assignee_type: Literal["PROJECT_LEAD", "UNASSIGNED"] | None = Field(default=None, validation_alias="assigneeType", serialization_alias="assigneeType", description="Determines who is automatically assigned to newly created issues in this project. Choose PROJECT_LEAD to assign to the project lead, or UNASSIGNED to leave issues unassigned by default.")
    avatar_id: int | None = Field(default=None, validation_alias="avatarId", serialization_alias="avatarId", description="The numeric ID of the avatar image to display for this project. Retrieve available avatar IDs from the project avatars endpoint.", json_schema_extra={'format': 'int64'})
    category_id: int | None = Field(default=None, validation_alias="categoryId", serialization_alias="categoryId", description="The numeric ID of the project category for organizational grouping. Retrieve available category IDs using the Get all project categories operation.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(default=None, description="A brief text description of the project's purpose and scope.")
    field_scheme: int | None = Field(default=None, validation_alias="fieldScheme", serialization_alias="fieldScheme", description="The numeric ID of the field scheme that defines which custom and standard fields are available in this project. Cannot be combined with projectTemplateKey. Retrieve available field scheme IDs using the Get field schemes operation.", json_schema_extra={'format': 'int64'})
    issue_security_scheme: int | None = Field(default=None, validation_alias="issueSecurityScheme", serialization_alias="issueSecurityScheme", description="The numeric ID of the issue security scheme that controls visibility and access permissions for issues. Retrieve available scheme IDs using the Get issue security schemes operation.", json_schema_extra={'format': 'int64'})
    issue_type_scheme: int | None = Field(default=None, validation_alias="issueTypeScheme", serialization_alias="issueTypeScheme", description="The numeric ID of the issue type scheme that defines which issue types are available in this project. Cannot be combined with projectTemplateKey. Retrieve available scheme IDs using the Get all issue type schemes operation.", json_schema_extra={'format': 'int64'})
    issue_type_screen_scheme: int | None = Field(default=None, validation_alias="issueTypeScreenScheme", serialization_alias="issueTypeScreenScheme", description="The numeric ID of the issue type screen scheme that maps issue types to their corresponding screens. Cannot be combined with projectTemplateKey. Retrieve available scheme IDs using the Get all issue type screen schemes operation.", json_schema_extra={'format': 'int64'})
    key: str = Field(default=..., description="A unique project identifier consisting of 1-10 uppercase alphanumeric characters, starting with a letter. This key is used in issue keys (e.g., PROJ-123) and cannot be changed after creation.")
    name: str = Field(default=..., description="The display name of the project, which appears in the Jira interface and project listings.")
    notification_scheme: int | None = Field(default=None, validation_alias="notificationScheme", serialization_alias="notificationScheme", description="The numeric ID of the notification scheme that defines how team members are notified of project events. Retrieve available scheme IDs using the Get notification schemes operation.", json_schema_extra={'format': 'int64'})
    permission_scheme: int | None = Field(default=None, validation_alias="permissionScheme", serialization_alias="permissionScheme", description="The numeric ID of the permission scheme that controls user access and actions within the project. Retrieve available scheme IDs using the Get all permission schemes operation.", json_schema_extra={'format': 'int64'})
    project_template_key: Literal["com.pyxis.greenhopper.jira:gh-simplified-agility-kanban", "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum", "com.pyxis.greenhopper.jira:gh-simplified-basic", "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic", "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic", "com.pyxis.greenhopper.jira:gh-cross-team-template", "com.pyxis.greenhopper.jira:gh-cross-team-planning-template", "com.atlassian.servicedesk:simplified-it-service-management", "com.atlassian.servicedesk:simplified-it-service-management-basic", "com.atlassian.servicedesk:simplified-it-service-management-operations", "com.atlassian.servicedesk:simplified-general-service-desk", "com.atlassian.servicedesk:simplified-internal-service-desk", "com.atlassian.servicedesk:simplified-external-service-desk", "com.atlassian.servicedesk:simplified-hr-service-desk", "com.atlassian.servicedesk:simplified-facilities-service-desk", "com.atlassian.servicedesk:simplified-legal-service-desk", "com.atlassian.servicedesk:simplified-marketing-service-desk", "com.atlassian.servicedesk:simplified-finance-service-desk", "com.atlassian.servicedesk:simplified-analytics-service-desk", "com.atlassian.servicedesk:simplified-design-service-desk", "com.atlassian.servicedesk:simplified-sales-service-desk", "com.atlassian.servicedesk:simplified-halp-service-desk", "com.atlassian.servicedesk:next-gen-it-service-desk", "com.atlassian.servicedesk:next-gen-hr-service-desk", "com.atlassian.servicedesk:next-gen-legal-service-desk", "com.atlassian.servicedesk:next-gen-marketing-service-desk", "com.atlassian.servicedesk:next-gen-facilities-service-desk", "com.atlassian.servicedesk:next-gen-general-service-desk", "com.atlassian.servicedesk:next-gen-analytics-service-desk", "com.atlassian.servicedesk:next-gen-finance-service-desk", "com.atlassian.servicedesk:next-gen-design-service-desk", "com.atlassian.servicedesk:next-gen-sales-service-desk", "com.atlassian.jira-core-project-templates:jira-core-simplified-content-management", "com.atlassian.jira-core-project-templates:jira-core-simplified-document-approval", "com.atlassian.jira-core-project-templates:jira-core-simplified-lead-tracking", "com.atlassian.jira-core-project-templates:jira-core-simplified-process-control", "com.atlassian.jira-core-project-templates:jira-core-simplified-procurement", "com.atlassian.jira-core-project-templates:jira-core-simplified-project-management", "com.atlassian.jira-core-project-templates:jira-core-simplified-recruitment", "com.atlassian.jira-core-project-templates:jira-core-simplified-task-", "com.atlassian.jcs:customer-service-management"] | None = Field(default=None, validation_alias="projectTemplateKey", serialization_alias="projectTemplateKey", description="A predefined project configuration template that sets up workflows, issue types, and screens. The template type must match the projectTypeKey (e.g., software templates for software projects). Cannot be combined with fieldScheme, issueTypeScheme, issueTypeScreenScheme, or workflowScheme.")
    url: str | None = Field(default=None, description="A URL pointing to project documentation, guidelines, or related resources.")
    workflow_scheme: int | None = Field(default=None, validation_alias="workflowScheme", serialization_alias="workflowScheme", description="The numeric ID of the workflow scheme that defines the issue lifecycle and transitions for this project. Cannot be combined with projectTemplateKey. Retrieve available scheme IDs using the Get all workflow schemes operation.", json_schema_extra={'format': 'int64'})
class CreateProjectRequest(StrictModel):
    """Creates a new Jira project based on a project type template (business, software, service_desk, or customer_service). Requires Administer Jira global permission and a unique project key."""
    body: CreateProjectRequestBody

# Operation: create_project_from_template
class CreateProjectWithCustomTemplateRequestBody(StrictModel):
    """The JSON payload containing the project details and capabilities"""
    details: CreateProjectWithCustomTemplateBodyDetails | None = Field(default=None, description="Project details: name, description, access level, assignee type, avatar, category, language, URL, and other project-level settings.")
    template: CreateProjectWithCustomTemplateBodyTemplate | None = Field(default=None, description="Project template configuration: boards, field schemes, issue types, notification schemes, permission schemes, roles, security levels, workflows, and their mappings.")
class CreateProjectWithCustomTemplateRequest(StrictModel):
    """Creates a new Jira project based on a custom template with specified capabilities. This asynchronous operation configures project details, workflows, permissions, fields, and other components. Requires Jira Enterprise edition and Administer Jira global permission."""
    body: CreateProjectWithCustomTemplateRequestBody | None = None

# Operation: list_projects
class SearchProjectsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of projects to return per page, capped at 100. Values exceeding 100 will be automatically limited to 100.", le=100, json_schema_extra={'format': 'int32'})
    order_by: Literal["category", "-category", "+category", "key", "-key", "+key", "name", "-name", "+name", "owner", "-owner", "+owner", "issueCount", "-issueCount", "+issueCount", "lastIssueUpdatedDate", "-lastIssueUpdatedDate", "+lastIssueUpdatedDate", "archivedDate", "+archivedDate", "-archivedDate", "deletedDate", "+deletedDate", "-deletedDate"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort results by a specific field: category, issue count, project key, last issue update time, project name, project owner/lead, archived date, or deleted date. Prefix with `-` for descending order or `+` for ascending order. Defaults to sorting by project key.")
    keys: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter results to include only specific projects by their keys. Provide up to 50 project keys as a comma-separated list.")
    type_key: str | None = Field(default=None, validation_alias="typeKey", serialization_alias="typeKey", description="Filter results by project type. Accepts comma-separated values: `business`, `service_desk`, or `software`.")
    category_id: int | None = Field(default=None, validation_alias="categoryId", serialization_alias="categoryId", description="Filter results by project category ID. Retrieve available category IDs using the Get all project categories operation.", json_schema_extra={'format': 'int64'})
    action: Literal["view", "browse", "edit", "create"] | None = Field(default=None, description="Filter results by the user's permission level on projects: `view` (has browse or admin permissions), `browse` (has browse permission), `edit` (has admin permission), or `create` (can create issues). Defaults to `view`.")
    status: list[Literal["live", "archived", "deleted"]] | None = Field(default=None, description="Filter results by project status: `live` for active projects, `archived` for archived projects, or `deleted` for projects in the recycle bin. This is an experimental feature.")
    property_query: str | None = Field(default=None, validation_alias="propertyQuery", serialization_alias="propertyQuery", description="Search projects by custom property values using dot-notation syntax. Enclose property keys in square brackets to support keys containing dots or equals signs. This is an experimental feature.")
class SearchProjectsRequest(StrictModel):
    """Retrieve a paginated list of projects visible to the user based on their permissions. Supports filtering by project keys, type, category, and status, with flexible sorting options."""
    query: SearchProjectsRequestQuery | None = None

# Operation: get_project_type
class GetProjectTypeByKeyRequestPath(StrictModel):
    project_type_key: Literal["software", "service_desk", "business", "product_discovery"] = Field(default=..., validation_alias="projectTypeKey", serialization_alias="projectTypeKey", description="The unique identifier for the project type. Must be one of the following: software, service_desk, business, or product_discovery.")
class GetProjectTypeByKeyRequest(StrictModel):
    """Retrieve detailed information about a specific project type by its key. This operation is publicly accessible and requires no authentication or permissions."""
    path: GetProjectTypeByKeyRequestPath

# Operation: get_accessible_project_type
class GetAccessibleProjectTypeByKeyRequestPath(StrictModel):
    project_type_key: Literal["software", "service_desk", "business", "product_discovery"] = Field(default=..., validation_alias="projectTypeKey", serialization_alias="projectTypeKey", description="The unique identifier for the project type. Must be one of the four supported project types: software, service_desk, business, or product_discovery.")
class GetAccessibleProjectTypeByKeyRequest(StrictModel):
    """Retrieves a project type if it is accessible to the authenticated user. Returns project type details for the specified project type key."""
    path: GetAccessibleProjectTypeByKeyRequestPath

# Operation: get_project
class GetProjectRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The unique identifier for the project, either as the project ID (numeric) or project key (case-sensitive alphanumeric code). Project keys are typically short uppercase abbreviations like 'PROJ'.")
class GetProjectRequest(StrictModel):
    """Retrieve detailed information about a specific project, including its configuration and metadata. Requires Browse projects permission for the target project."""
    path: GetProjectRequestPath

# Operation: update_project
class UpdateProjectRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
class UpdateProjectRequestBody(StrictModel):
    """The project details to be updated."""
    assignee_type: Literal["PROJECT_LEAD", "UNASSIGNED"] | None = Field(default=None, validation_alias="assigneeType", serialization_alias="assigneeType", description="The default assignee type for newly created issues in this project. Choose between the project lead or unassigned.")
    avatar_id: int | None = Field(default=None, validation_alias="avatarId", serialization_alias="avatarId", description="The numeric ID of the avatar image to display for this project.", json_schema_extra={'format': 'int64'})
    category_id: int | None = Field(default=None, validation_alias="categoryId", serialization_alias="categoryId", description="The numeric ID of the project category. Use the Get all project categories operation to find available category IDs, or set to -1 to remove the category.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(default=None, description="A brief description of the project's purpose and scope.")
    issue_security_scheme: int | None = Field(default=None, validation_alias="issueSecurityScheme", serialization_alias="issueSecurityScheme", description="The numeric ID of the issue security scheme that controls issue visibility and access permissions. Use the Get issue security schemes operation to find available scheme IDs.", json_schema_extra={'format': 'int64'})
    notification_scheme: int | None = Field(default=None, validation_alias="notificationScheme", serialization_alias="notificationScheme", description="The numeric ID of the notification scheme that defines how project members are notified of events. Use the Get notification schemes operation to find available scheme IDs.", json_schema_extra={'format': 'int64'})
    permission_scheme: int | None = Field(default=None, validation_alias="permissionScheme", serialization_alias="permissionScheme", description="The numeric ID of the permission scheme that defines user roles and permissions. Use the Get all permission schemes operation to find available scheme IDs.", json_schema_extra={'format': 'int64'})
    released_project_keys: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="releasedProjectKeys", serialization_alias="releasedProjectKeys", description="An array of previous project keys to release from the current project. Released keys must belong to the current project and cannot include the current project key.")
    url: str | None = Field(default=None, description="A URL pointing to project documentation or related information.")
class UpdateProjectRequest(StrictModel):
    """Update project details including name, description, avatar, category, and associated schemes. All parameters are optional; only included fields will be updated while omitted ones remain unchanged."""
    path: UpdateProjectRequestPath
    body: UpdateProjectRequestBody | None = None

# Operation: delete_project
class DeleteProjectRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The unique identifier for the project, either the numeric project ID or the project key (case-sensitive).")
class DeleteProjectRequestQuery(StrictModel):
    enable_undo: bool | None = Field(default=None, validation_alias="enableUndo", serialization_alias="enableUndo", description="Whether to move the project to the Jira recycle bin for later restoration instead of permanently deleting it. Defaults to true.")
class DeleteProjectRequest(StrictModel):
    """Permanently delete a Jira project. Archived projects must be restored before deletion. Requires Jira administrator permissions."""
    path: DeleteProjectRequestPath
    query: DeleteProjectRequestQuery | None = None

# Operation: archive_project
class ArchiveProjectRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The unique identifier for the project, either the project ID (numeric) or project key (case-sensitive alphanumeric code).")
class ArchiveProjectRequest(StrictModel):
    """Archive a project to prevent further modifications while preserving its data. Archived projects cannot be deleted directly; restore the project first if deletion is needed."""
    path: ArchiveProjectRequestPath

# Operation: set_project_avatar
class UpdateProjectAvatarRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key.")
class UpdateProjectAvatarRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the avatar image to display. This avatar must have been previously uploaded to the project.")
class UpdateProjectAvatarRequest(StrictModel):
    """Sets the avatar image displayed for a project. The avatar must first be uploaded using the load project avatar operation before it can be set as the displayed avatar."""
    path: UpdateProjectAvatarRequestPath
    body: UpdateProjectAvatarRequestBody

# Operation: remove_project_avatar
class DeleteProjectAvatarRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key.")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric identifier of the avatar to delete. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteProjectAvatarRequest(StrictModel):
    """Remove a custom avatar from a project. Only custom avatars can be deleted; system-provided avatars are protected and cannot be removed. Requires Administer projects permission."""
    path: DeleteProjectAvatarRequestPath

# Operation: upload_project_avatar
class CreateProjectAvatarRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key.")
class CreateProjectAvatarRequestQuery(StrictModel):
    x: int | None = Field(default=None, description="The X coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    y: int | None = Field(default=None, description="The Y coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="The side length (in pixels) of the square crop region. Defaults to 0, which uses the smaller of the image's height or width.", json_schema_extra={'format': 'int32'})
class CreateProjectAvatarRequest(StrictModel):
    """Upload and process an image file as a project avatar. The image is automatically cropped to a square and resized into multiple formats (16x16, 24x24, 32x32, 48x48). Requires the Administer projects permission."""
    path: CreateProjectAvatarRequestPath
    query: CreateProjectAvatarRequestQuery | None = None

# Operation: list_project_avatars
class GetAllProjectAvatarsRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the case-sensitive project key.")
class GetAllProjectAvatarsRequest(StrictModel):
    """Retrieves all avatars available for a project, organized into system-provided and custom avatar groups. Requires browse project permission and can be accessed anonymously."""
    path: GetAllProjectAvatarsRequestPath

# Operation: get_project_classification
class GetDefaultProjectClassificationRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The unique identifier for the project, either as the numeric project ID or the project key (which is case-sensitive).")
class GetDefaultProjectClassificationRequest(StrictModel):
    """Retrieve the default data classification level assigned to a project. This determines the default sensitivity or confidentiality level for issues and data within the project."""
    path: GetDefaultProjectClassificationRequestPath

# Operation: list_project_components
class GetProjectComponentsPaginatedRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the project ID or project key (case-sensitive).")
class GetProjectComponentsPaginatedRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index where the result page begins. Use this to navigate through paginated results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of components to return per page. Defaults to 50 items.", json_schema_extra={'format': 'int32'})
    order_by: Literal["description", "-description", "+description", "issueCount", "-issueCount", "+issueCount", "lead", "-lead", "+lead", "name", "-name", "+name"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort results by component attribute: name, description, issue count, or project lead. Prefix with `-` for descending or `+` for ascending order.")
    component_source: Literal["jira", "compass", "auto"] | None = Field(default=None, validation_alias="componentSource", serialization_alias="componentSource", description="The component source to return: `jira` for Jira components, `compass` for Compass components, or `auto` to return Compass components if available, otherwise Jira components.")
class GetProjectComponentsPaginatedRequest(StrictModel):
    """Retrieve a paginated list of all components in a project. Returns Jira components by default, or Compass components if configured. Requires Browse Projects permission."""
    path: GetProjectComponentsPaginatedRequestPath
    query: GetProjectComponentsPaginatedRequestQuery | None = None

# Operation: get_project_components_all
class GetProjectComponentsRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the project ID or project key (case-sensitive).")
class GetProjectComponentsRequestQuery(StrictModel):
    component_source: Literal["jira", "compass", "auto"] | None = Field(default=None, validation_alias="componentSource", serialization_alias="componentSource", description="The source of components to return: use 'jira' for Jira components (default), 'compass' for Compass components, or 'auto' to return Compass components if available, otherwise Jira components.")
class GetProjectComponentsRequest(StrictModel):
    """Retrieves all components in a project, including Compass components if the project is opted into Compass. Requires Browse Projects permission and can be accessed anonymously."""
    path: GetProjectComponentsRequestPath
    query: GetProjectComponentsRequestQuery | None = None

# Operation: delete_project_async
class DeleteProjectAsynchronouslyRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
class DeleteProjectAsynchronouslyRequest(StrictModel):
    """Asynchronously delete a project. The operation is transactional—if any part fails, the project remains unchanged. Monitor the returned task location to track deletion progress."""
    path: DeleteProjectAsynchronouslyRequestPath

# Operation: list_project_features
class GetFeaturesForProjectRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The unique identifier or key of the project. You can use either the numeric project ID or the case-sensitive project key to identify the project.")
class GetFeaturesForProjectRequest(StrictModel):
    """Retrieves all available features for a specified project. Features represent optional capabilities or modules that can be enabled or configured within the project."""
    path: GetFeaturesForProjectRequestPath

# Operation: list_project_property_keys
class GetProjectPropertyKeysRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (which is case-sensitive).")
class GetProjectPropertyKeysRequest(StrictModel):
    """Retrieves all property keys stored for a specific project. Property keys are identifiers for custom data associated with the project."""
    path: GetProjectPropertyKeysRequestPath

# Operation: get_project_property
class GetProjectPropertyRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The key identifying the project property to retrieve. Use the list project property keys operation to discover available property keys for a project.")
class GetProjectPropertyRequest(StrictModel):
    """Retrieves the value of a specific project property by its key. Requires Browse Projects permission for the project containing the property."""
    path: GetProjectPropertyRequestPath

# Operation: remove_project_property
class DeleteProjectPropertyRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The key identifying the project property to delete. Retrieve available property keys using the list project properties operation.")
class DeleteProjectPropertyRequest(StrictModel):
    """Removes a custom property from a project. Requires Administer Jira global permission or Administer Projects permission for the target project."""
    path: DeleteProjectPropertyRequestPath

# Operation: restore_project
class RestoreRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case sensitive).")
class RestoreRequest(StrictModel):
    """Restore a project that has been archived or moved to the Jira recycle bin. Requires Administer Jira global permission for Company managed projects, or Administer Jira global permission or Administer projects project permission for Team managed projects."""
    path: RestoreRequestPath

# Operation: list_project_roles
class GetProjectRolesRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (which is case-sensitive).")
class GetProjectRolesRequest(StrictModel):
    """Retrieve all project roles available for a specific project, including their names and API endpoints. Project roles are shared across all projects in Jira Cloud."""
    path: GetProjectRolesRequestPath

# Operation: get_project_role
class GetProjectRoleRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the project role to retrieve. Use the get_project_roles operation to discover available project role IDs.", json_schema_extra={'format': 'int64'})
class GetProjectRoleRequestQuery(StrictModel):
    exclude_inactive_users: bool | None = Field(default=None, validation_alias="excludeInactiveUsers", serialization_alias="excludeInactiveUsers", description="When enabled, filters out inactive users from the returned actors list. Defaults to false, including all users.")
class GetProjectRoleRequest(StrictModel):
    """Retrieve a project role's details and the list of actors (users and groups) assigned to it within a specific project. The actors are returned sorted by display name."""
    path: GetProjectRoleRequestPath
    query: GetProjectRoleRequestQuery | None = None

# Operation: add_project_role_actors
class AddActorUsersRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive string).")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the project role to add actors to. Retrieve available project role IDs using the get_project_roles operation.", json_schema_extra={'format': 'int64'})
class AddActorUsersRequestBody(StrictModel):
    """The groups or users to associate with the project role for this project. Provide the user account ID, group name, or group ID. As a group's name can change, use of group ID is recommended."""
    user: list[str] | None = Field(default=None, description="An array of user account IDs to add to the project role. Each entry should be a valid user account ID string.")
class AddActorUsersRequest(StrictModel):
    """Adds actors (users or groups) to a project role. Use this to grant role-based permissions to additional actors in a project."""
    path: AddActorUsersRequestPath
    body: AddActorUsersRequestBody | None = None

# Operation: replace_project_role_actors
class SetActorsRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive string).")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the project role to modify. Retrieve available project role IDs using the get all project roles operation.", json_schema_extra={'format': 'int64'})
class SetActorsRequestBody(StrictModel):
    """The groups or users to associate with the project role for this project. Provide the user account ID, group name, or group ID. As a group's name can change, use of group ID is recommended."""
    categorised_actors: dict[str, list[str]] | None = Field(default=None, validation_alias="categorisedActors", serialization_alias="categorisedActors", description="The actors to assign to the project role, replacing all current assignments. Specify groups by ID (recommended) or name, and users by account ID. Use the appropriate actor type key (atlassian-group-role-actor-id, atlassian-group-role-actor, or atlassian-user-role-actor) with an array of identifiers.")
class SetActorsRequest(StrictModel):
    """Replace all actors assigned to a project role. This operation overwrites the existing actor list entirely; to add actors without removing existing ones, use the add actors operation instead."""
    path: SetActorsRequestPath
    body: SetActorsRequestBody | None = None

# Operation: remove_actor_from_project_role
class DeleteActorRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the project role. Retrieve available project role IDs using the get all project roles operation.", json_schema_extra={'format': 'int64'})
class DeleteActorRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="The user account ID of the actor to remove from the project role. If omitted, the operation will fail as a user must be specified for removal.")
class DeleteActorRequest(StrictModel):
    """Remove an actor (user) from a project role. Requires project administration permissions or global Jira administration rights."""
    path: DeleteActorRequestPath
    query: DeleteActorRequestQuery | None = None

# Operation: list_project_roles_with_details
class GetProjectRoleDetailsRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
class GetProjectRoleDetailsRequestQuery(StrictModel):
    current_member: bool | None = Field(default=None, validation_alias="currentMember", serialization_alias="currentMember", description="Filter roles to show only those assigned to the current user. Defaults to false to return all roles.")
    exclude_other_service_roles: bool | None = Field(default=None, validation_alias="excludeOtherServiceRoles", serialization_alias="excludeOtherServiceRoles", description="Exclude service management roles that don't apply to the project type. Defaults to false to include all roles.")
class GetProjectRoleDetailsRequest(StrictModel):
    """Retrieve all project roles and their details for a specific project. Project roles are shared across all projects in the Jira instance."""
    path: GetProjectRoleDetailsRequestPath
    query: GetProjectRoleDetailsRequestQuery | None = None

# Operation: list_project_statuses
class GetAllStatusesRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (which is case-sensitive). Use the key for human-readable references or the ID for programmatic consistency.")
class GetAllStatusesRequest(StrictModel):
    """Retrieves all valid statuses for a project, organized by issue type. Each issue type within the project has its own set of valid statuses that can be used for workflow transitions."""
    path: GetAllStatusesRequestPath

# Operation: list_project_versions
class GetProjectVersionsPaginatedRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The project identifier, either the numeric project ID or the project key (case-sensitive).")
class GetProjectVersionsPaginatedRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index where the paginated results should start. Defaults to 0 for the first page.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of versions to return per page. Defaults to 50 items.", json_schema_extra={'format': 'int32'})
    order_by: Literal["description", "-description", "+description", "name", "-name", "+name", "releaseDate", "-releaseDate", "+releaseDate", "sequence", "-sequence", "+sequence", "startDate", "-startDate", "+startDate"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort the results by a specific field: description, name, releaseDate (oldest first), sequence (UI order), or startDate (oldest first). Prefix with '-' for descending order or '+' for ascending order.")
    status: str | None = Field(default=None, description="Filter versions by status using a comma-separated list. Valid statuses are: released, unreleased, and archived.")
class GetProjectVersionsPaginatedRequest(StrictModel):
    """Retrieve a paginated list of all versions in a project. Use this operation when you need to browse versions with pagination control; for a complete unpaginated list, use the alternative get_project_versions operation instead."""
    path: GetProjectVersionsPaginatedRequestPath
    query: GetProjectVersionsPaginatedRequestQuery | None = None

# Operation: list_project_versions_all
class GetProjectVersionsRequestPath(StrictModel):
    project_id_or_key: str = Field(default=..., validation_alias="projectIdOrKey", serialization_alias="projectIdOrKey", description="The unique identifier for the project, either as the project ID (numeric) or project key (case-sensitive alphanumeric code).")
class GetProjectVersionsRequest(StrictModel):
    """Retrieves all versions for a specified project in a single non-paginated response. Use this operation when you need the complete list of versions; for paginated results, use the paginated versions endpoint instead."""
    path: GetProjectVersionsRequestPath

# Operation: get_project_email
class GetProjectEmailRequestPath(StrictModel):
    project_id: int = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="The unique identifier of the project. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetProjectEmailRequest(StrictModel):
    """Retrieves the sender email address configured for a project. This email is used as the from address for project notifications and communications."""
    path: GetProjectEmailRequestPath

# Operation: get_issue_type_hierarchy
class GetHierarchyRequestPath(StrictModel):
    project_id: int = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="The numeric identifier of the project for which to retrieve the issue type hierarchy.", json_schema_extra={'format': 'int64'})
class GetHierarchyRequest(StrictModel):
    """Retrieve the issue type hierarchy for a next-gen project, which defines the structural levels of issue types (Epic, Story/Task/Bug, and Subtask) and their relationships. Requires Browse projects permission."""
    path: GetHierarchyRequestPath

# Operation: list_security_levels_project
class GetSecurityLevelsForProjectRequestPath(StrictModel):
    project_key_or_id: str = Field(default=..., validation_alias="projectKeyOrId", serialization_alias="projectKeyOrId", description="The project identifier, either the project key (case-sensitive) or the project ID.")
class GetSecurityLevelsForProjectRequest(StrictModel):
    """Retrieve all issue security levels available in a project that the authenticated user can access. Security levels are only returned for users with the Set Issue Security permission."""
    path: GetSecurityLevelsForProjectRequestPath

# Operation: create_project_category
class CreateProjectCategoryRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Optional text describing the purpose and scope of this project category.")
    name: str | None = Field(default=None, description="The name of the project category. Required on create, optional on update.")
class CreateProjectCategoryRequest(StrictModel):
    """Creates a new project category in Jira. Requires Administer Jira global permission."""
    body: CreateProjectCategoryRequestBody | None = None

# Operation: get_project_category
class GetProjectCategoryByIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project category as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetProjectCategoryByIdRequest(StrictModel):
    """Retrieve a specific project category by its ID. Returns the category details for use in project organization and filtering."""
    path: GetProjectCategoryByIdRequestPath

# Operation: update_project_category
class UpdateProjectCategoryRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project category to update. This is a numeric ID that identifies which category to modify.", json_schema_extra={'format': 'int64'})
class UpdateProjectCategoryRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The new description text for the project category. This field is optional and can be used to update the category's descriptive information.")
class UpdateProjectCategoryRequest(StrictModel):
    """Updates an existing project category with new metadata. Requires Jira administrator permissions to perform this action."""
    path: UpdateProjectCategoryRequestPath
    body: UpdateProjectCategoryRequestBody | None = None

# Operation: delete_project_category
class RemoveProjectCategoryRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project category to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class RemoveProjectCategoryRequest(StrictModel):
    """Permanently deletes a project category from Jira. Requires Administer Jira global permission."""
    path: RemoveProjectCategoryRequestPath

# Operation: list_project_fields
class GetProjectFieldsRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Use this to retrieve subsequent pages of results.", ge=0, json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of fields to return per page. Must be between 1 and 100 items.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    project_id: list[int] = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="One or more project IDs to retrieve fields for. Only fields available to these projects will be returned.")
    work_type_id: list[int] = Field(default=..., validation_alias="workTypeId", serialization_alias="workTypeId", description="One or more work type (issue type) IDs to retrieve fields for. Only fields applicable to these work types will be returned.")
    field_id: list[str] | None = Field(default=None, validation_alias="fieldId", serialization_alias="fieldId", description="Optional list of specific field IDs to retrieve. If omitted, all available fields for the project and work type combination are returned.")
class GetProjectFieldsRequest(StrictModel):
    """Retrieve available fields for specified projects and work types. Returns a paginated list of fields that are applicable to the given project and work type combination, with optional filtering by specific field IDs."""
    query: GetProjectFieldsRequestQuery

# Operation: validate_project_name
class GetValidProjectNameRequestQuery(StrictModel):
    name: str = Field(default=..., description="The desired project name to validate for availability.")
class GetValidProjectNameRequest(StrictModel):
    """Validates whether a project name is available. Returns the provided name if unused, attempts to generate an alternative name by appending a sequence number if the name is taken, or returns an error if no valid alternative can be generated."""
    query: GetValidProjectNameRequestQuery

# Operation: redact_issue_fields
class RedactRequestBody(StrictModel):
    """List of redaction requests"""
    redactions: Annotated[list[SingleRedactionRequest], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Array of field redaction specifications defining which issue fields should have their data redacted. Each item specifies the field identifier and redaction parameters.")
class RedactRequest(StrictModel):
    """Submit an asynchronous job to redact sensitive data from specified issue fields. Use the returned job ID to poll the redaction status."""
    body: RedactRequestBody | None = None

# Operation: list_resolutions
class SearchResolutionsRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to navigate through pages of results.")
    max_results: str | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of resolutions to return per page. Defaults to 50 items if not specified.")
    only_default: bool | None = Field(default=None, validation_alias="onlyDefault", serialization_alias="onlyDefault", description="When enabled, returns only default resolutions. If specific resolution IDs are provided and none are marked as default, an empty page is returned. Only applies to company-managed projects.")
class SearchResolutionsRequest(StrictModel):
    """Retrieve a paginated list of issue resolutions, optionally filtered by resolution IDs or default status. Useful for populating resolution dropdowns or validating resolution values in Jira."""
    query: SearchResolutionsRequestQuery | None = None

# Operation: get_resolution
class GetResolutionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the resolution value to retrieve.")
class GetResolutionRequest(StrictModel):
    """Retrieve the details of a specific issue resolution value by its ID. This returns metadata about how an issue can be resolved in Jira."""
    path: GetResolutionRequestPath

# Operation: update_resolution
class UpdateResolutionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue resolution to update.")
class UpdateResolutionRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The description of the resolution. Limited to 255 characters maximum.", max_length=255)
    name: str = Field(default=..., description="The name of the resolution. Must be unique across all resolutions and limited to 60 characters maximum.", max_length=60)
class UpdateResolutionRequest(StrictModel):
    """Updates an existing issue resolution in Jira. Requires Administer Jira global permission to perform this action."""
    path: UpdateResolutionRequestPath
    body: UpdateResolutionRequestBody

# Operation: delete_resolution
class DeleteResolutionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue resolution to delete.")
class DeleteResolutionRequestQuery(StrictModel):
    replace_with: str = Field(default=..., validation_alias="replaceWith", serialization_alias="replaceWith", description="The unique identifier of the issue resolution that will replace the deleted one for all affected issues. This parameter is required to ensure no issues are left without a resolution.")
class DeleteResolutionRequest(StrictModel):
    """Deletes an issue resolution from Jira. All issues currently using the deleted resolution will be reassigned to the specified replacement resolution. This is an asynchronous operation; check the returned task location to monitor completion status."""
    path: DeleteResolutionRequestPath
    query: DeleteResolutionRequestQuery

# Operation: get_project_role_global
class GetProjectRoleByIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project role as a 64-bit integer. Retrieve available project role IDs using the list project roles operation.", json_schema_extra={'format': 'int64'})
class GetProjectRoleByIdRequest(StrictModel):
    """Retrieve the details of a specific project role, including its default actors sorted by display name. Requires Jira administrator permissions."""
    path: GetProjectRoleByIdRequestPath

# Operation: update_project_role
class PartialUpdateProjectRoleRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project role to update. This is a 64-bit integer that can be obtained from the list of all project roles.", json_schema_extra={'format': 'int64'})
class PartialUpdateProjectRoleRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The new description for the project role. This field is optional for partial updates and will only be applied if the name is not provided in the same request.")
class PartialUpdateProjectRoleRequest(StrictModel):
    """Partially update a project role by modifying either its name or description. Note that only one field can be updated per request; if both are provided, only the name will be updated."""
    path: PartialUpdateProjectRoleRequestPath
    body: PartialUpdateProjectRoleRequestBody | None = None

# Operation: update_project_role_full
class FullyUpdateProjectRoleRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project role to update. This is a numeric ID that can be retrieved from the list of all project roles.", json_schema_extra={'format': 'int64'})
class FullyUpdateProjectRoleRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The new description for the project role. This field is required when fully updating a project role.")
    name: str | None = Field(default=None, description="The name of the project role. Must be unique. Cannot begin or end with whitespace. The maximum length is 255 characters. Required when creating a project role. Optional when partially updating a project role.")
class FullyUpdateProjectRoleRequest(StrictModel):
    """Fully update a project role by replacing its name and description. Both name and description are required for this operation."""
    path: FullyUpdateProjectRoleRequestPath
    body: FullyUpdateProjectRoleRequestBody | None = None

# Operation: delete_project_role
class DeleteProjectRoleRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project role to delete. Retrieve available project role IDs using the list project roles operation.", json_schema_extra={'format': 'int64'})
class DeleteProjectRoleRequestQuery(StrictModel):
    swap: int | None = Field(default=None, description="The unique identifier of a project role to replace the deleted role across all schemes, workflows, worklogs, and comments. Required if the role being deleted is currently in use.", json_schema_extra={'format': 'int64'})
class DeleteProjectRoleRequest(StrictModel):
    """Deletes a project role from your Jira instance. If the role is currently in use, you must specify a replacement role to reassign its associations in schemes, workflows, worklogs, and comments."""
    path: DeleteProjectRoleRequestPath
    query: DeleteProjectRoleRequestQuery | None = None

# Operation: list_screen_fields
class GetAvailableScreenFieldsRequestPath(StrictModel):
    screen_id: int = Field(default=..., validation_alias="screenId", serialization_alias="screenId", description="The unique identifier of the screen. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetAvailableScreenFieldsRequest(StrictModel):
    """Retrieve all fields available to be added to a screen tab. This helps identify which fields can be configured for a specific screen layout."""
    path: GetAvailableScreenFieldsRequestPath

# Operation: count_issues
class CountIssuesRequestBody(StrictModel):
    """A JSON object containing the search request."""
    jql: str | None = Field(default=None, description="A JQL query expression to filter issues. The query must include at least one search restriction (bounded query) for performance reasons.")
class CountIssuesRequest(StrictModel):
    """Get an estimated count of issues matching a JQL query. Returns a fast approximate count for issues the user has permission to view; note that recent updates may not be immediately reflected."""
    body: CountIssuesRequestBody | None = None

# Operation: search_issues
class SearchAndReconsileIssuesUsingJqlRequestQuery(StrictModel):
    jql: str | None = Field(default=None, description="A JQL expression to filter issues. Must include a search restriction (bounded query) for performance—for example, filtering by project, assignee, or status. The orderBy clause supports a maximum of 7 fields. Unbounded queries like 'order by key desc' are not permitted.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of issues to return per page, up to 5000. The API may return fewer items when many fields or properties are requested. Defaults to 50 items per page.", json_schema_extra={'format': 'int32'})
    reconcile_issues: list[int] | None = Field(default=None, validation_alias="reconcileIssues", serialization_alias="reconcileIssues", description="List of up to 50 issue IDs to reconcile with search results for stronger consistency guarantees. Use this when read-after-write consistency is critical. The same list should be included across all paginated requests.")
class SearchAndReconsileIssuesUsingJqlRequest(StrictModel):
    """Search for issues using JQL (Jira Query Language) with optional read-after-write consistency reconciliation. Results reflect issues where you have browse permissions on the containing project and any applicable issue-level security permissions."""
    query: SearchAndReconsileIssuesUsingJqlRequestQuery | None = None

# Operation: search_issues_jql
class SearchAndReconsileIssuesUsingJqlPostRequestBody(StrictModel):
    jql: str | None = Field(default=None, description="A JQL expression to filter issues. Must include at least one search restriction (e.g., assignee, project, status) to be considered bounded. The orderBy clause supports a maximum of 7 fields.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of issues to return per page, up to 5000. Defaults to 50 items per page. Actual results may be fewer when requesting many fields.", json_schema_extra={'format': 'int32'})
    reconcile_issues: list[int] | None = Field(default=None, validation_alias="reconcileIssues", serialization_alias="reconcileIssues", description="List of up to 50 issue IDs to reconcile with search results for stronger consistency guarantees. Use the same list across all paginated requests to ensure consistency.")
class SearchAndReconsileIssuesUsingJqlPostRequest(StrictModel):
    """Search for issues using JQL with optional read-after-write consistency reconciliation. Requires a bounded query with at least one search restriction for optimal performance."""
    body: SearchAndReconsileIssuesUsingJqlPostRequestBody | None = None

# Operation: get_security_level
class GetIssueSecurityLevelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue security level to retrieve.")
class GetIssueSecurityLevelRequest(StrictModel):
    """Retrieve detailed information about a specific issue security level. Use this to get security level properties after obtaining the level ID from the issue security scheme."""
    path: GetIssueSecurityLevelRequestPath

# Operation: get_status
class GetStatusRequestPath(StrictModel):
    id_or_name: str = Field(default=..., validation_alias="idOrName", serialization_alias="idOrName", description="The unique identifier or display name of the status. Using the status ID is preferred when the name may not be unique across your instance.")
class GetStatusRequest(StrictModel):
    """Retrieve a status associated with an active workflow by its ID or name. If multiple statuses share the same name, the first match is returned; using the status ID is recommended for precise identification."""
    path: GetStatusRequestPath

# Operation: get_status_category
class GetStatusCategoryRequestPath(StrictModel):
    id_or_key: str = Field(default=..., validation_alias="idOrKey", serialization_alias="idOrKey", description="The unique identifier or key of the status category to retrieve.")
class GetStatusCategoryRequest(StrictModel):
    """Retrieve a status category by its ID or key. Status categories are used to group and organize statuses in Jira workflows."""
    path: GetStatusCategoryRequestPath

# Operation: list_statuses_bulk
class GetStatusesByIdRequestQuery(StrictModel):
    id_: list[str] = Field(default=..., validation_alias="id", serialization_alias="id", description="One or more status IDs to retrieve. Provide between 1 and 50 IDs in a single request.")
class GetStatusesByIdRequest(StrictModel):
    """Retrieve detailed information for one or more statuses by their IDs. Useful for fetching status configurations needed for workflow operations or validation."""
    query: GetStatusesByIdRequestQuery

# Operation: delete_statuses
class DeleteStatusesByIdRequestQuery(StrictModel):
    id_: list[str] = Field(default=..., validation_alias="id", serialization_alias="id", description="One or more status IDs to delete. Provide between 1 and 50 IDs in a single request.")
class DeleteStatusesByIdRequest(StrictModel):
    """Permanently delete one or more statuses by their IDs. Requires either Administer projects or Administer Jira permission."""
    query: DeleteStatusesByIdRequestQuery

# Operation: list_statuses_by_name
class GetStatusesByNameRequestQuery(StrictModel):
    name: list[str] = Field(default=..., description="One or more status names to retrieve. Provide between 1 and 50 names as an ampersand-separated list.")
    project_id: str | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="Optional project ID to scope the status lookup to a specific project. Omit or use null to retrieve global statuses.")
class GetStatusesByNameRequest(StrictModel):
    """Retrieve a list of statuses by their names. Supports bulk lookup of up to 50 status names, optionally scoped to a specific project or global statuses."""
    query: GetStatusesByNameRequestQuery

# Operation: search_statuses
class SearchRequestQuery(StrictModel):
    project_id: str | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The project ID to filter statuses to a specific project, or omit to search global statuses.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 if not specified.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of statuses to return per page. Defaults to 200 if not specified.", json_schema_extra={'format': 'int32'})
    search_string: str | None = Field(default=None, validation_alias="searchString", serialization_alias="searchString", description="A search term to match against status names. Omit or leave empty to return all statuses in the search scope. Limited to 255 characters.", max_length=255)
    status_category: str | None = Field(default=None, validation_alias="statusCategory", serialization_alias="statusCategory", description="Filter results by status category: TODO, IN_PROGRESS, or DONE. Omit to include all categories.")
class SearchRequest(StrictModel):
    """Search for statuses by name or project, returning paginated results. Requires project administration or Jira administration permissions."""
    query: SearchRequestQuery | None = None

# Operation: list_issue_type_usages
class GetProjectIssueTypeUsagesForStatusRequestPath(StrictModel):
    status_id: str = Field(default=..., validation_alias="statusId", serialization_alias="statusId", description="The unique identifier of the status to query for issue type usage.")
    project_id: str = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="The unique identifier of the project to filter issue type usages.")
class GetProjectIssueTypeUsagesForStatusRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of results to return per page. Must be between 1 and 200, defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetProjectIssueTypeUsagesForStatusRequest(StrictModel):
    """Retrieves the issue types currently using a specific status within a project. Returns paginated results showing which issue types are associated with the given status."""
    path: GetProjectIssueTypeUsagesForStatusRequestPath
    query: GetProjectIssueTypeUsagesForStatusRequestQuery | None = None

# Operation: list_project_usages_by_status
class GetProjectUsagesForStatusRequestPath(StrictModel):
    status_id: str = Field(default=..., validation_alias="statusId", serialization_alias="statusId", description="The unique identifier of the status to query for project usage.")
class GetProjectUsagesForStatusRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of results to return per page. Must be between 1 and 200, defaults to 50 results.", json_schema_extra={'format': 'int32'})
class GetProjectUsagesForStatusRequest(StrictModel):
    """Retrieves a paginated list of projects that use a specific status. Useful for understanding status adoption and impact across your Jira instance."""
    path: GetProjectUsagesForStatusRequestPath
    query: GetProjectUsagesForStatusRequestQuery | None = None

# Operation: list_workflow_usages_by_status
class GetWorkflowUsagesForStatusRequestPath(StrictModel):
    status_id: str = Field(default=..., validation_alias="statusId", serialization_alias="statusId", description="The unique identifier of the status for which to retrieve workflow usages.")
class GetWorkflowUsagesForStatusRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of workflow results to return per page. Must be between 1 and 200, with a default of 50 results.", json_schema_extra={'format': 'int32'})
class GetWorkflowUsagesForStatusRequest(StrictModel):
    """Retrieve a paginated list of workflows that use a specific status. This helps identify which workflows are affected by changes to a given status."""
    path: GetWorkflowUsagesForStatusRequestPath
    query: GetWorkflowUsagesForStatusRequestQuery | None = None

# Operation: get_task
class GetTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., validation_alias="taskId", serialization_alias="taskId", description="The unique identifier of the task to retrieve status and results for.")
class GetTaskRequest(StrictModel):
    """Retrieve the status and results of a long-running asynchronous task. Once completed, returns the JSON response applicable to the task; details are retained for 14 days."""
    path: GetTaskRequestPath

# Operation: cancel_task
class CancelTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., validation_alias="taskId", serialization_alias="taskId", description="The unique identifier of the task to cancel.")
class CancelTaskRequest(StrictModel):
    """Cancels an active task in Jira. Requires either Jira administrator permissions or creator status of the task."""
    path: CancelTaskRequestPath

# Operation: list_avatars
class GetAvatarsRequestPath(StrictModel):
    type_: Literal["project", "issuetype", "priority"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category of avatar to retrieve: project, issue type, or priority.")
    entity_id: str = Field(default=..., validation_alias="entityId", serialization_alias="entityId", description="The unique identifier of the entity (project, issue type, or priority) associated with the avatars.")
class GetAvatarsRequest(StrictModel):
    """Retrieves all available avatars (system and custom) for a project, issue type, or priority. Supports anonymous access for system and priority avatars, with permission checks for custom project and issue type avatars."""
    path: GetAvatarsRequestPath

# Operation: upload_avatar
class StoreAvatarRequestPath(StrictModel):
    type_: Literal["project", "issuetype", "priority"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category of entity receiving the avatar. Must be one of: project, issuetype, or priority.")
    entity_id: str = Field(default=..., validation_alias="entityId", serialization_alias="entityId", description="The unique identifier of the entity (project, issue type, or priority) that will use this avatar.")
class StoreAvatarRequestQuery(StrictModel):
    x: int | None = Field(default=None, description="The X coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    y: int | None = Field(default=None, description="The Y coordinate (in pixels) of the top-left corner of the crop region. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    size: int = Field(default=..., description="The width and height (in pixels) of the square crop region. The cropped area is extracted from the uploaded image starting at the specified X and Y coordinates.", json_schema_extra={'format': 'int32'})
class StoreAvatarRequest(StrictModel):
    """Upload a custom avatar image for a project, issue type, or priority. The image is automatically cropped to a square and resized into multiple formats (16x16, 24x24, 32x32, 48x48 pixels). Requires Administer Jira global permission."""
    path: StoreAvatarRequestPath
    query: StoreAvatarRequestQuery

# Operation: delete_avatar
class DeleteAvatarRequestPath(StrictModel):
    type_: Literal["project", "issuetype", "priority"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category of object the avatar belongs to: project, issue type, or priority.")
    owning_object_id: str = Field(default=..., validation_alias="owningObjectId", serialization_alias="owningObjectId", description="The unique identifier of the project, issue type, or priority that owns the avatar.")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the avatar to delete.", json_schema_extra={'format': 'int64'})
class DeleteAvatarRequest(StrictModel):
    """Permanently removes a custom avatar from a project, issue type, or priority. Requires Jira administrator permissions."""
    path: DeleteAvatarRequestPath

# Operation: get_avatar_image_by_avatar_id
class GetAvatarImageByIdRequestPath(StrictModel):
    type_: Literal["issuetype", "project", "priority"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The avatar category: either 'issuetype' for issue type avatars, 'project' for project avatars, or 'priority' for priority avatars.")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the avatar to retrieve.", json_schema_extra={'format': 'int64'})
class GetAvatarImageByIdRequestQuery(StrictModel):
    size: Literal["xsmall", "small", "medium", "large", "xlarge"] | None = Field(default=None, description="The desired image size: 'xsmall', 'small', 'medium', 'large', or 'xlarge'. If omitted, the default size is returned.")
    format_: Literal["png", "svg"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The image format to return: either 'png' or 'svg'. If omitted, the avatar's original format is returned.")
class GetAvatarImageByIdRequest(StrictModel):
    """Retrieves an avatar image for a project, issue type, or priority by ID. Returns the image in the requested size and format, or defaults to the original if not specified."""
    path: GetAvatarImageByIdRequestPath
    query: GetAvatarImageByIdRequestQuery | None = None

# Operation: get_avatar_image_by_entity
class GetAvatarImageByOwnerRequestPath(StrictModel):
    type_: Literal["issuetype", "project", "priority"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The avatar type to retrieve: either 'issuetype', 'project', or 'priority'.")
    entity_id: str = Field(default=..., validation_alias="entityId", serialization_alias="entityId", description="The unique identifier of the entity (project or issue type) that owns the avatar.")
class GetAvatarImageByOwnerRequestQuery(StrictModel):
    size: Literal["xsmall", "small", "medium", "large", "xlarge"] | None = Field(default=None, description="The desired avatar image size: xsmall, small, medium, large, or xlarge. Defaults to the original size if not specified.")
    format_: Literal["png", "svg"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The image format to return: either 'png' or 'svg'. Defaults to the original content format if not specified.")
class GetAvatarImageByOwnerRequest(StrictModel):
    """Retrieves the avatar image for a project, issue type, or priority in the specified size and format. This operation can be accessed anonymously, though custom avatars may require project browse permissions."""
    path: GetAvatarImageByOwnerRequestPath
    query: GetAvatarImageByOwnerRequestQuery | None = None

# Operation: get_user
class GetUserRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required.", max_length=128)
class GetUserRequest(StrictModel):
    """Retrieve a user's profile information from Jira. Privacy controls are applied based on the user's preferences, which may hide sensitive details like email addresses."""
    query: GetUserRequestQuery | None = None

# Operation: create_user
class CreateUserRequestBody(StrictModel):
    """Details about the user to be created."""
    email_address: str = Field(default=..., validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address for the new user. This serves as the unique identifier for the user account.")
    products: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(default=..., description="An array of products the user should have access to. Valid options include jira-core, jira-servicedesk, jira-product-discovery, and jira-software. Pass an empty array to create a user without any product access.")
class CreateUserRequest(StrictModel):
    """Creates a new user in Jira with specified product access. Returns 201 if the user is created or already exists with access, or 400 if the user exists without access. Requires Administer Jira global permission and organization admin status."""
    body: CreateUserRequestBody

# Operation: delete_user
class RemoveUserRequestQuery(StrictModel):
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The unique account ID that identifies the user across all Atlassian products. This is a string identifier up to 128 characters long (for example, 5b10ac8d82e05b22cc7d4ef5).", max_length=128)
class RemoveUserRequest(StrictModel):
    """Permanently removes a user from Jira's user base. Note that this operation only deletes the user's Jira account and does not affect their Atlassian account."""
    query: RemoveUserRequestQuery

# Operation: list_assignable_users_multiproject
class FindBulkAssignableUsersRequestQuery(StrictModel):
    project_keys: str = Field(default=..., validation_alias="projectKeys", serialization_alias="projectKeys", description="Comma-separated list of project keys (case-sensitive) to search for assignable users. At least one project key is required.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="Zero-based index for pagination to specify which result page to return. Defaults to 0 if not provided.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of users to return per page. Defaults to 50 if not provided.", json_schema_extra={'format': 'int32'})
class FindBulkAssignableUsersRequest(StrictModel):
    """Retrieve users who can be assigned issues across one or more projects. Results are filtered based on user attributes and privacy settings, and may return fewer users than requested due to pagination constraints."""
    query: FindBulkAssignableUsersRequestQuery

# Operation: list_assignable_users
class FindAssignableUsersRequestQuery(StrictModel):
    issue_id: str | None = Field(default=None, validation_alias="issueId", serialization_alias="issueId", description="The issue ID to check assignability against. Required unless issueKey or project is specified.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination (zero-indexed). Defaults to 0 for the first page.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of users to return per page. Defaults to 50. Note: the operation may return fewer users than requested, as it filters results to only assignable users.", json_schema_extra={'format': 'int32'})
    action_descriptor_id: int | None = Field(default=None, validation_alias="actionDescriptorId", serialization_alias="actionDescriptorId", description="The workflow transition ID to check assignability during a state change. Use with issueKey or issueId to validate users for a specific transition.", json_schema_extra={'format': 'int32'})
    account_type: list[str] | None = Field(default=None, validation_alias="accountType", serialization_alias="accountType", description="Filter results by account type (e.g., atlassian, app, customer). Specify as a comma-separated list if multiple types are needed.")
class FindAssignableUsersRequest(StrictModel):
    """Retrieve a list of users who can be assigned to an issue, optionally filtered by project, issue, or workflow transition. Use this to populate assignee dropdowns or validate user assignment eligibility."""
    query: FindAssignableUsersRequestQuery | None = None

# Operation: list_users_by_account_ids
class BulkGetUsersRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first user. Use this to navigate through pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of users to return per page. Defaults to 10 if not specified.", json_schema_extra={'format': 'int32'})
    account_id: list[str] = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="One or more user account IDs to retrieve. Specify multiple account IDs to fetch multiple users in a single request. Each account ID must not exceed 128 characters.", max_length=128)
class BulkGetUsersRequest(StrictModel):
    """Retrieve a paginated list of Jira users by their account IDs. Requires permission to access Jira."""
    query: BulkGetUsersRequestQuery

# Operation: list_user_account_ids
class BulkGetUsersMigrationRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 represents the first item. Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of user results to return in a single page. Defaults to 10 items per page.", json_schema_extra={'format': 'int32'})
    key: list[str] | None = Field(default=None, description="Key of a user. To specify multiple users, pass multiple copies of this parameter. For example, `key=fred&key=barney`. Required if `username` isn't provided. Cannot be provided if `username` is present.")
    username: list[str] | None = Field(default=None, description="Username of a user. To specify multiple users, pass multiple copies of this parameter. For example, `username=fred&username=barney`. Required if `key` isn't provided. Cannot be provided if `key` is present.")
class BulkGetUsersMigrationRequest(StrictModel):
    """Retrieve account IDs for specified users by their key or username. This operation supports pagination and is useful for migrating or bulk-processing user data."""
    query: BulkGetUsersMigrationRequestQuery | None = None

# Operation: list_user_groups
class GetUserGroupsRequestQuery(StrictModel):
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The unique account ID of the user across all Atlassian products (up to 128 characters).", max_length=128)
class GetUserGroupsRequest(StrictModel):
    """Retrieve all groups that a user belongs to. Requires Browse users and groups global permission."""
    query: GetUserGroupsRequestQuery

# Operation: search_users_by_permissions
class FindUsersWithAllPermissionsRequestQuery(StrictModel):
    permissions: str = Field(default=..., description="Comma-separated list of permission identifiers to filter users. Use permission keys from the Jira permissions API, custom project permissions from Connect apps, or deprecated permission constants like BROWSE, CREATE_ISSUE, or PROJECT_ADMIN.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="Zero-based index for pagination to specify which result page to retrieve. Defaults to 0 for the first page.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of users to return per page, up to 50 results. Defaults to 50. Note that the actual number returned may be fewer due to search filtering.", json_schema_extra={'format': 'int32'})
    project_key: str | None = Field(default=None, validation_alias="projectKey", serialization_alias="projectKey", description="The project key for the project (case sensitive).")
    issue_key: str | None = Field(default=None, validation_alias="issueKey", serialization_alias="issueKey", description="The issue key for the issue.")
class FindUsersWithAllPermissionsRequest(StrictModel):
    """Search for users who have specific permissions in a project or issue and match optional search criteria. Returns matching users with privacy controls applied based on user preferences."""
    query: FindUsersWithAllPermissionsRequestQuery

# Operation: search_users_picker
class FindUsersForPickerRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query matched against user attributes such as displayName and emailAddress. Supports prefix matching, so partial names and email prefixes will return relevant results.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of users to return in the results, up to 1000. Defaults to 50 if not specified. The total count of matched users is provided separately.", json_schema_extra={'format': 'int32'})
    exclude_account_ids: list[str] | None = Field(default=None, validation_alias="excludeAccountIds", serialization_alias="excludeAccountIds", description="List of user account IDs to exclude from search results. Accepts comma-separated or ampersand-separated format for multiple IDs.")
class FindUsersForPickerRequest(StrictModel):
    """Search for users by matching query terms against user attributes like display name and email address. Returns matching users with highlighted query matches in HTML format, with optional filtering to exclude specific users."""
    query: FindUsersForPickerRequestQuery

# Operation: list_user_property_keys
class GetUserPropertyKeysRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)
class GetUserPropertyKeysRequest(StrictModel):
    """Retrieves all property keys associated with a user. These are custom properties stored at the user level, distinct from Jira user profile properties."""
    query: GetUserPropertyKeysRequestQuery | None = None

# Operation: get_user_property
class GetUserPropertyRequestPath(StrictModel):
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The unique identifier for the user property you want to retrieve.")
class GetUserPropertyRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)
class GetUserPropertyRequest(StrictModel):
    """Retrieves the value of a specific property associated with a user account. Requires either Jira administrator permissions to access any user's properties, or standard Jira access to retrieve properties from your own user record."""
    path: GetUserPropertyRequestPath
    query: GetUserPropertyRequestQuery | None = None

# Operation: remove_user_property
class DeleteUserPropertyRequestPath(StrictModel):
    property_key: str = Field(default=..., validation_alias="propertyKey", serialization_alias="propertyKey", description="The unique identifier for the user property to delete. This key must match an existing property on the user's profile.")
class DeleteUserPropertyRequest(StrictModel):
    """Removes a custom property from a user's profile. Requires either Jira administrator permissions to delete properties from any user, or standard Jira access to delete properties from your own user record."""
    path: DeleteUserPropertyRequestPath

# Operation: search_users
class FindUsersRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for paginated results, where 0 is the first user. Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The number of users to return per page. Defaults to 50 users per page.", json_schema_extra={'format': 'int32'})
    property_: str | None = Field(default=None, validation_alias="property", serialization_alias="property", description="A property query string to filter users by custom properties using dot notation for nested values (e.g., `propertykey.nested.field=value`). Required unless `accountId` or `query` is specified.")
    query: str | None = Field(default=None, description="A query string that is matched against user attributes ( `displayName`, and `emailAddress`) to find relevant users. The string can match the prefix of the attribute's value. For example, *query=john* matches a user with a `displayName` of *John Smith* and a user with an `emailAddress` of *johnson@example.com*. Required, unless `accountId` or `property` is specified.")
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="A query string that is matched exactly against a user `accountId`. Required, unless `query` or `property` is specified.", max_length=128)
class FindUsersRequest(StrictModel):
    """Search for active users by name or property. Returns matching users with privacy controls applied based on user preferences. Requires Browse users and groups permission; anonymous calls return empty results."""
    query: FindUsersRequestQuery | None = None

# Operation: search_users_query
class FindUsersByQueryRequestQuery(StrictModel):
    query: str = Field(default=..., description="A structured query string to filter users. Supports queries like 'is assignee of PROJ', 'is reporter of (PROJ-1, PROJ-2)', or custom property matching with AND/OR operators for complex filters.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index where the result page begins. Use this to paginate through results in combination with maxResults.", json_schema_extra={'format': 'int64'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of users to return per page. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class FindUsersByQueryRequest(StrictModel):
    """Search for users using structured queries based on their involvement with issues, projects, or custom properties. Returns a paginated list of matching user details."""
    query: FindUsersByQueryRequestQuery

# Operation: search_users_by_query
class FindUserKeysByQueryRequestQuery(StrictModel):
    query: str = Field(default=..., description="A structured query string using statements like 'is assignee of PROJ', 'is reporter of (PROJ-1, PROJ-2)', or property matching syntax. Multiple statements can be combined with AND/OR operators to create complex queries.")
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index where the result page begins. Use this to paginate through results in combination with maxResult.", json_schema_extra={'format': 'int64'})
    max_result: int | None = Field(default=None, validation_alias="maxResult", serialization_alias="maxResult", description="The maximum number of user keys to return per page, up to 100 items. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class FindUserKeysByQueryRequest(StrictModel):
    """Search for users using structured query syntax to find assignees, reporters, watchers, voters, commenters, or transitioners of specific issues, or match users by custom properties. Returns a paginated list of user keys matching the query criteria."""
    query: FindUserKeysByQueryRequestQuery

# Operation: search_browsable_users
class FindUsersWithBrowsePermissionRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The starting position for pagination, where 0 is the first user. Use this to retrieve subsequent pages of results.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of users to return per page, up to 50 by default. The operation may return fewer results if fewer users match the search criteria.", json_schema_extra={'format': 'int32'})
    query: str | None = Field(default=None, description="A query string that is matched against user attributes, such as `displayName` and `emailAddress`, to find relevant users. The string can match the prefix of the attribute's value. For example, *query=john* matches a user with a `displayName` of *John Smith* and a user with an `emailAddress` of *johnson@example.com*. Required, unless `accountId` is specified.")
    project_key: str | None = Field(default=None, validation_alias="projectKey", serialization_alias="projectKey", description="The project key for the project (case sensitive). Required, unless `issueKey` is specified.")
    issue_key: str | None = Field(default=None, validation_alias="issueKey", serialization_alias="issueKey", description="The issue key for the issue. Required, unless `projectKey` is specified.")
class FindUsersWithBrowsePermissionRequest(StrictModel):
    """Search for users who have permission to browse issues and match the given search criteria. Results can be filtered by a specific issue or project, with privacy controls applied based on user preferences."""
    query: FindUsersWithBrowsePermissionRequestQuery | None = None

# Operation: list_users_default
class GetAllUsersDefaultRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index position to start returning results from. Use this to paginate through large result sets.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of users to return per request, up to a limit of 1000. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetAllUsersDefaultRequest(StrictModel):
    """Retrieves a paginated list of all users in the Jira instance, including active, inactive, and previously deleted users with Atlassian accounts. Response data is filtered based on user privacy preferences."""
    query: GetAllUsersDefaultRequestQuery | None = None

# Operation: list_users
class GetAllUsersRequestQuery(StrictModel):
    start_at: int | None = Field(default=None, validation_alias="startAt", serialization_alias="startAt", description="The zero-based index position to start returning results from, enabling pagination through large user lists. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of users to return per request, capped at 1000. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetAllUsersRequest(StrictModel):
    """Retrieves a paginated list of all users in the Jira instance, including active, inactive, and previously deleted users with Atlassian accounts. Response visibility is filtered based on user privacy preferences."""
    query: GetAllUsersRequestQuery | None = None

# Operation: create_version
class CreateVersionRequestBody(StrictModel):
    archived: bool | None = Field(default=None, description="Whether the version should be marked as archived. Defaults to false if not specified.")
    description: str | None = Field(default=None, description="A text description of the version, up to 16,384 bytes in length.")
    driver: str | None = Field(default=None, description="The Atlassian account ID of the person responsible for driving this version's development.")
    move_unfixed_issues_to: str | None = Field(default=None, validation_alias="moveUnfixedIssuesTo", serialization_alias="moveUnfixedIssuesTo", description="The URL of the version to which unfixed issues should be moved when this version is released. Only applicable when updating a version.", json_schema_extra={'format': 'uri'})
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project to which this version belongs. Required when creating a version.", json_schema_extra={'format': 'int64'})
    release_date: str | None = Field(default=None, validation_alias="releaseDate", serialization_alias="releaseDate", description="The date when the version is released, specified in ISO 8601 format (yyyy-mm-dd).", json_schema_extra={'format': 'date'})
    released: bool | None = Field(default=None, description="Whether the version has been released. Once released, subsequent release requests are ignored. Only applicable when updating a version.")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="The date when work on the version begins, specified in ISO 8601 format (yyyy-mm-dd).", json_schema_extra={'format': 'date'})
    name: str | None = Field(default=None, description="The unique name of the version. Required when creating a version. Optional when updating a version. The maximum length is 255 characters.")
class CreateVersionRequest(StrictModel):
    """Creates a new project version in Jira. Requires the project ID and appropriate permissions to administer the project."""
    body: CreateVersionRequestBody | None = None

# Operation: get_version
class GetVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version to retrieve.")
class GetVersionRequest(StrictModel):
    """Retrieve details for a specific project version by its ID. This operation can be accessed anonymously and requires Browse projects permission for the project containing the version."""
    path: GetVersionRequestPath

# Operation: update_version
class UpdateVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version to update.")
class UpdateVersionRequestBody(StrictModel):
    archived: bool | None = Field(default=None, description="Set whether this version is archived. Archived versions are typically hidden from active workflows.")
    description: str | None = Field(default=None, description="A text description of the version. Maximum length is 16,384 bytes.")
    driver: str | None = Field(default=None, description="The Atlassian account ID of the person responsible for this version.")
    move_unfixed_issues_to: str | None = Field(default=None, validation_alias="moveUnfixedIssuesTo", serialization_alias="moveUnfixedIssuesTo", description="The URI of another version to automatically move all unfixed issues to when this version is released. Only applicable during updates, not creation.", json_schema_extra={'format': 'uri'})
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project this version belongs to. Only used during version creation; ignored when updating.", json_schema_extra={'format': 'int64'})
    release_date: str | None = Field(default=None, validation_alias="releaseDate", serialization_alias="releaseDate", description="The date when this version is released, specified in ISO 8601 format (yyyy-mm-dd).", json_schema_extra={'format': 'date'})
    released: bool | None = Field(default=None, description="Set whether this version is released. Once released, subsequent release requests are ignored.")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="The date when work on this version begins, specified in ISO 8601 format (yyyy-mm-dd).", json_schema_extra={'format': 'date'})
class UpdateVersionRequest(StrictModel):
    """Updates an existing project version with new metadata such as release dates, status, and driver assignment. Requires Administer Jira global permission or Administer Projects permission for the target project."""
    path: UpdateVersionRequestPath
    body: UpdateVersionRequestBody | None = None

# Operation: merge_versions
class MergeVersionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the version to delete. This version will be removed after all its issues are reassigned to the target version.")
    move_issues_to: str = Field(default=..., validation_alias="moveIssuesTo", serialization_alias="moveIssuesTo", description="The ID of the version to merge into. All issues currently assigned to the source version will be reassigned to this version.")
class MergeVersionsRequest(StrictModel):
    """Merges two project versions by deleting the source version and reassigning all issues from it to the target version. Requires Administer Jira or Administer Projects permission."""
    path: MergeVersionsRequestPath

# Operation: reorder_version
class MoveVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version to reorder.")
class MoveVersionRequestBody(StrictModel):
    after: str | None = Field(default=None, description="The URL (self link) of the version after which to place the moved version. Cannot be used with `position`.", json_schema_extra={'format': 'uri'})
    position: Literal["Earlier", "Later", "First", "Last"] | None = Field(default=None, description="An absolute position in which to place the moved version. Cannot be used with `after`.")
class MoveVersionRequest(StrictModel):
    """Changes the sequence position of a version within its project, affecting how versions are displayed in Jira. Requires browse permissions on the project containing the version."""
    path: MoveVersionRequestPath
    body: MoveVersionRequestBody | None = None

# Operation: count_version_related_issues
class GetVersionRelatedIssuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version for which to retrieve related issue counts.")
class GetVersionRelatedIssuesRequest(StrictModel):
    """Retrieves counts of issues related to a specific version, including issues where the version is set as a fix version, affected version, or in a custom version field. Requires Browse projects permission for the project containing the version."""
    path: GetVersionRelatedIssuesRequestPath

# Operation: list_related_work
class GetRelatedWorkRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version for which to retrieve related work items.")
class GetRelatedWorkRequest(StrictModel):
    """Retrieves all related work items associated with a specific version. Requires Browse projects permission for the project containing the version."""
    path: GetRelatedWorkRequestPath

# Operation: create_related_work
class CreateRelatedWorkRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version to which the related work will be linked.")
class CreateRelatedWorkRequestBody(StrictModel):
    category: str = Field(default=..., description="The category classification for the related work item.")
    title: str | None = Field(default=None, description="The display title or name of the related work item.")
    url: str | None = Field(default=None, description="The web address pointing to the related work item. Required for all related work types except native release notes, which will have a null URL. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
class CreateRelatedWorkRequest(StrictModel):
    """Creates a generic related work item linked to a specific version. The related work ID is automatically generated and does not need to be provided."""
    path: CreateRelatedWorkRequestPath
    body: CreateRelatedWorkRequestBody

# Operation: update_related_work
class UpdateRelatedWorkRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version containing the related work to update.")
class UpdateRelatedWorkRequestBody(StrictModel):
    category: str = Field(default=..., description="The classification type of the related work (e.g., generic link, release note).")
    title: str | None = Field(default=None, description="The display name or title for the related work.")
    url: str | None = Field(default=None, description="The web address pointing to the related work resource. Required for all related work types except native release notes, which use null.", json_schema_extra={'format': 'uri'})
    related_work_id: str | None = Field(default=None, validation_alias="relatedWorkId", serialization_alias="relatedWorkId", description="The id of the related work. For the native release note related work item, this will be null, and Rest API does not support updating it.")
class UpdateRelatedWorkRequest(StrictModel):
    """Updates an existing related work item for a version. Only generic link related works can be modified through this API; archived version-related works cannot be edited."""
    path: UpdateRelatedWorkRequestPath
    body: UpdateRelatedWorkRequestBody

# Operation: delete_and_replace_version
class DeleteAndReplaceVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version to delete. Must be a valid version ID from the target project.")
class DeleteAndReplaceVersionRequestBody(StrictModel):
    custom_field_replacement_list: list[CustomFieldReplacement] | None = Field(default=None, validation_alias="customFieldReplacementList", serialization_alias="customFieldReplacementList", description="An optional array of mappings to reassign custom fields containing the deleted version. Each mapping specifies a custom field ID and the replacement version ID to use. All replacement versions must belong to the same project as the deleted version and cannot be the version being deleted.")
class DeleteAndReplaceVersionRequest(StrictModel):
    """Deletes a project version and optionally reassigns issues to alternative versions. Issues referencing the deleted version in fixVersion, affectedVersion, or version picker custom fields will be updated with the provided replacements or cleared if no alternatives are specified."""
    path: DeleteAndReplaceVersionRequestPath
    body: DeleteAndReplaceVersionRequestBody | None = None

# Operation: get_version_unresolved_issues
class GetVersionUnresolvedIssuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the version for which to retrieve issue counts.")
class GetVersionUnresolvedIssuesRequest(StrictModel):
    """Retrieves the count of total and unresolved issues for a specific project version. Useful for tracking version completion status and identifying outstanding work."""
    path: GetVersionUnresolvedIssuesRequestPath

# Operation: delete_related_work
class DeleteRelatedWorkRequestPath(StrictModel):
    version_id: str = Field(default=..., validation_alias="versionId", serialization_alias="versionId", description="The unique identifier of the version containing the related work to be deleted.")
    related_work_id: str = Field(default=..., validation_alias="relatedWorkId", serialization_alias="relatedWorkId", description="The unique identifier of the related work item to remove.")
class DeleteRelatedWorkRequest(StrictModel):
    """Removes a related work item from a specific version. Requires permissions to resolve and edit issues in the project containing the version."""
    path: DeleteRelatedWorkRequestPath

# Operation: list_workflow_history
class ListWorkflowHistoryRequestBody(StrictModel):
    workflow_id: str | None = Field(default=None, validation_alias="workflowId", serialization_alias="workflowId", description="The unique identifier of the workflow whose history you want to retrieve.")
class ListWorkflowHistoryRequest(StrictModel):
    """Retrieves workflow history entries for a specified workflow, showing past changes and events. Note that historical data is only available for the last 60 days and entries before October 30th, 2025 are not accessible."""
    body: ListWorkflowHistoryRequestBody | None = None

# Operation: list_workflow_issue_type_usages
class GetWorkflowProjectIssueTypeUsagesRequestPath(StrictModel):
    workflow_id: str = Field(default=..., validation_alias="workflowId", serialization_alias="workflowId", description="The unique identifier of the workflow to query for issue type usage.")
    project_id: int = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="The unique identifier of the project in which to find issue type usages.", json_schema_extra={'format': 'int64'})
class GetWorkflowProjectIssueTypeUsagesRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of issue types to return per page. Must be between 1 and 200, defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetWorkflowProjectIssueTypeUsagesRequest(StrictModel):
    """Retrieve the issue types within a project that are currently using a specified workflow. Returns paginated results of issue type assignments."""
    path: GetWorkflowProjectIssueTypeUsagesRequestPath
    query: GetWorkflowProjectIssueTypeUsagesRequestQuery | None = None

# Operation: list_workflow_projects
class GetProjectUsagesForWorkflowRequestPath(StrictModel):
    workflow_id: str = Field(default=..., validation_alias="workflowId", serialization_alias="workflowId", description="The unique identifier of the workflow to query for project usage.")
class GetProjectUsagesForWorkflowRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of projects to return per page, between 1 and 200. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetProjectUsagesForWorkflowRequest(StrictModel):
    """Retrieve a paginated list of projects that use a specified workflow. Useful for understanding workflow adoption and impact across your Jira instance."""
    path: GetProjectUsagesForWorkflowRequestPath
    query: GetProjectUsagesForWorkflowRequestQuery | None = None

# Operation: list_workflow_capabilities
class WorkflowCapabilitiesRequestQuery(StrictModel):
    workflow_id: str | None = Field(default=None, validation_alias="workflowId", serialization_alias="workflowId", description="The unique identifier of the workflow. Use this to retrieve capabilities for a specific workflow by ID.")
    project_id: str | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The unique identifier of the project. Use this with issueTypeId as an alternative to workflowId to identify the workflow by project context.")
    issue_type_id: str | None = Field(default=None, validation_alias="issueTypeId", serialization_alias="issueTypeId", description="The unique identifier of the issue type. Use this with projectId as an alternative to workflowId to identify the workflow by issue type context.")
class WorkflowCapabilitiesRequest(StrictModel):
    """Retrieve available workflow capabilities including rules, scope, and project types. Requires either a workflow ID or a project and issue type ID pair to identify the target workflow."""
    query: WorkflowCapabilitiesRequestQuery | None = None

# Operation: preview_workflows
class ReadWorkflowPreviewsRequestBody(StrictModel):
    issue_type_ids: list[str] | None = Field(default=None, validation_alias="issueTypeIds", serialization_alias="issueTypeIds", description="List of issue type IDs to filter workflows. Specify up to 25 issue type IDs; at least one lookup criterion (issueTypeIds, workflowNames, or workflowIds) is required.", min_length=0, max_length=25)
    project_id: str = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="The project ID for permission validation and workflow association. Required to identify the project context and enforce access controls.")
class ReadWorkflowPreviewsRequest(StrictModel):
    """Retrieve a read-only preview of workflows for a specified project. Returns workflow configuration details filtered by issue types, project permissions, and lookup criteria."""
    body: ReadWorkflowPreviewsRequestBody

# Operation: list_workflow_schemes_by_projects
class GetWorkflowSchemeProjectAssociationsRequestQuery(StrictModel):
    project_id: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., validation_alias="projectId", serialization_alias="projectId", description="One or more project IDs to retrieve associated workflow schemes for. Provide between 1 and 100 project IDs; non-existent or team-managed projects are ignored without error.", min_length=1, max_length=100)
class GetWorkflowSchemeProjectAssociationsRequest(StrictModel):
    """Retrieves the workflow schemes associated with specified projects, showing which projects are linked to each scheme. Team-managed and non-existent projects are silently ignored. The Default Workflow Scheme is returned without an ID."""
    query: GetWorkflowSchemeProjectAssociationsRequestQuery

# Operation: list_workflow_scheme_projects
class GetProjectUsagesForWorkflowSchemeRequestPath(StrictModel):
    workflow_scheme_id: str = Field(default=..., validation_alias="workflowSchemeId", serialization_alias="workflowSchemeId", description="The unique identifier of the workflow scheme for which to retrieve associated projects.")
class GetProjectUsagesForWorkflowSchemeRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of projects to return per page, between 1 and 200. Defaults to 50 if not specified.", json_schema_extra={'format': 'int32'})
class GetProjectUsagesForWorkflowSchemeRequest(StrictModel):
    """Retrieve a paginated list of projects that are currently using a specified workflow scheme."""
    path: GetProjectUsagesForWorkflowSchemeRequestPath
    query: GetProjectUsagesForWorkflowSchemeRequestQuery | None = None

# Operation: list_deleted_worklogs
class GetIdsOfWorklogsDeletedSinceRequestQuery(StrictModel):
    since: int | None = Field(default=None, description="The UNIX timestamp in milliseconds marking the start of the deletion window. Only worklogs deleted after this timestamp are returned. Defaults to 0 (epoch start) if not specified.", json_schema_extra={'format': 'int64'})
class GetIdsOfWorklogsDeletedSinceRequest(StrictModel):
    """Retrieve a paginated list of worklog IDs and deletion timestamps for worklogs deleted after a specified date and time. Results are ordered from oldest to youngest, with up to 1000 worklogs per page."""
    query: GetIdsOfWorklogsDeletedSinceRequestQuery | None = None

# Operation: get_worklogs
class GetWorklogsForIdsRequestBody(StrictModel):
    """A JSON object containing a list of worklog IDs."""
    ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., description="A list of worklog IDs to retrieve. Only worklogs that are viewable by all users or where you have project role or group permissions will be returned, up to a maximum of 1000 items.")
class GetWorklogsForIdsRequest(StrictModel):
    """Retrieve detailed worklog information for a specified list of worklog IDs. Returns up to 1000 worklogs where you have permission to view them."""
    body: GetWorklogsForIdsRequestBody

# Operation: list_worklogs_modified_since
class GetIdsOfWorklogsModifiedSinceRequestQuery(StrictModel):
    since: int | None = Field(default=None, description="The UNIX timestamp in milliseconds marking the start of the time range. Only worklogs updated after this timestamp are returned. Defaults to 0 (epoch start) if not specified. Note: worklogs updated during the minute immediately preceding the request are excluded.", json_schema_extra={'format': 'int64'})
class GetIdsOfWorklogsModifiedSinceRequest(StrictModel):
    """Retrieve a paginated list of worklog IDs and their update timestamps for all worklogs modified after a specified date and time. Results are ordered from oldest to youngest, with a maximum of 1000 worklogs per page."""
    query: GetIdsOfWorklogsModifiedSinceRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class AddCommentBodyVisibility(PermissiveModel):
    """The group or role to which this comment is visible. Optional on create and update."""
    identifier: str | None = Field(None, description="The ID of the group or the name of the role that visibility of this item is restricted to.")
    type_: Literal["group", "role"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Whether visibility of this item is restricted to a group or role.")
    value: str | None = Field(None, description="The name of the group or role that visibility of this item is restricted to. Please note that the name of a group is mutable, to reliably identify a group use `identifier`.")

class AddWorklogBodyVisibility(PermissiveModel):
    """Details about any restrictions in the visibility of the worklog. Optional when creating or updating a worklog."""
    identifier: str | None = Field(None, description="The ID of the group or the name of the role that visibility of this item is restricted to.")
    type_: Literal["group", "role"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Whether visibility of this item is restricted to a group or role.")
    value: str | None = Field(None, description="The name of the group or role that visibility of this item is restricted to. Please note that the name of a group is mutable, to reliably identify a group use `identifier`.")

class AvatarUrlsBean(StrictModel):
    n16x16: str | None = Field(None, validation_alias="16x16", serialization_alias="16x16", description="The URL of the item's 16x16 pixel avatar.", json_schema_extra={'format': 'uri'})
    n24x24: str | None = Field(None, validation_alias="24x24", serialization_alias="24x24", description="The URL of the item's 24x24 pixel avatar.", json_schema_extra={'format': 'uri'})
    n32x32: str | None = Field(None, validation_alias="32x32", serialization_alias="32x32", description="The URL of the item's 32x32 pixel avatar.", json_schema_extra={'format': 'uri'})
    n48x48: str | None = Field(None, validation_alias="48x48", serialization_alias="48x48", description="The URL of the item's 48x48 pixel avatar.", json_schema_extra={'format': 'uri'})

class BoardFeaturePayload(StrictModel):
    """The payload for setting a board feature"""
    feature_key: Literal["ESTIMATION", "SPRINTS"] | None = Field(None, validation_alias="featureKey", serialization_alias="featureKey", description="The key of the feature")
    state: Literal[True, False] | None = Field(None, description="Whether the feature should be turned on or off")

class BulkEditDashboardsBodyChangeOwnerDetails(StrictModel):
    """The details of change owner action."""
    autofix_name: bool = Field(..., validation_alias="autofixName", serialization_alias="autofixName", description="Whether the name is fixed automatically if it's duplicated after changing owner.")
    new_owner: str = Field(..., validation_alias="newOwner", serialization_alias="newOwner", description="The account id of the new owner.")

class BulkProjectPermissions(StrictModel):
    """Details of project permissions and associated issues and projects to look up."""
    issues: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="List of issue IDs.")
    permissions: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(..., description="List of project permissions.")
    projects: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="List of project IDs.")

class BulkSetIssuePropertyBodyFilter(StrictModel):
    """The bulk operation filter."""
    current_value: Any | None = Field(None, validation_alias="currentValue", serialization_alias="currentValue", description="The value of properties to perform the bulk operation on.")
    entity_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="entityIds", serialization_alias="entityIds", description="List of issues to perform the bulk operation on.")
    has_property: bool | None = Field(None, validation_alias="hasProperty", serialization_alias="hasProperty", description="Whether the bulk operation occurs only when the property is present on or absent from an issue.")

class BulkTransitionSubmitInput(StrictModel):
    selected_issue_ids_or_keys: list[str] = Field(..., validation_alias="selectedIssueIdsOrKeys", serialization_alias="selectedIssueIdsOrKeys", description="List of all the issue IDs or keys that are to be bulk transitioned.")
    transition_id: str = Field(..., validation_alias="transitionId", serialization_alias="transitionId", description="The ID of the transition that is to be performed on the issues.")

class CardLayout(StrictModel):
    """Card layout configuration."""
    show_days_in_column: Literal[True, False] | None = Field(False, validation_alias="showDaysInColumn", serialization_alias="showDaysInColumn", description="Whether to show days in column")

class CardLayoutField(StrictModel):
    """Card layout settings of the board"""
    field_id: str | None = Field(None, validation_alias="fieldId", serialization_alias="fieldId")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    mode: Literal["PLAN", "WORK"] | None = None
    position: int | None = Field(None, json_schema_extra={'format': 'int32'})

class ContentItem(StrictModel):
    """Represents the content to redact"""
    entity_id: str = Field(..., validation_alias="entityId", serialization_alias="entityId", description="The ID of the content entity.\n\n *  For redacting an issue field, this will be the field ID (e.g., summary, customfield\\_10000).\n *  For redacting a comment, this will be the comment ID.\n *  For redacting a worklog, this will be the worklog ID.")
    entity_type: Literal["issuefieldvalue", "issue-comment", "issue-worklog"] = Field(..., validation_alias="entityType", serialization_alias="entityType", description="The type of the entity to redact; It will be one of the following:\n\n *  **issuefieldvalue** \\- To redact in issue fields\n *  **issue-comment** \\- To redact in issue comments.\n *  **issue-worklog** \\- To redact in issue worklogs")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="This would be the issue ID")

class CreateCrossProjectReleaseRequest(StrictModel):
    name: str = Field(..., description="The cross-project release name.")
    release_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="releaseIds", serialization_alias="releaseIds", description="The IDs of the releases to include in the cross-project release.")

class CreateCustomFieldRequest(StrictModel):
    custom_field_id: int = Field(..., validation_alias="customFieldId", serialization_alias="customFieldId", description="The custom field ID.", json_schema_extra={'format': 'int64'})
    filter_: bool | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Allows filtering issues based on their values for the custom field.")

class CreateDateFieldRequest(StrictModel):
    date_custom_field_id: int | None = Field(None, validation_alias="dateCustomFieldId", serialization_alias="dateCustomFieldId", description="A date custom field ID. This is required if the type is \"DateCustomField\".", json_schema_extra={'format': 'int64'})
    type_: Literal["DueDate", "TargetStartDate", "TargetEndDate", "DateCustomField"] = Field(..., validation_alias="type", serialization_alias="type", description="The date field type. This must be \"DueDate\", \"TargetStartDate\", \"TargetEndDate\" or \"DateCustomField\".")

class CreateExclusionRulesRequest(StrictModel):
    issue_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="issueIds", serialization_alias="issueIds", description="The IDs of the issues to exclude from the plan.")
    issue_type_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="issueTypeIds", serialization_alias="issueTypeIds", description="The IDs of the issue types to exclude from the plan.")
    number_of_days_to_show_completed_issues: int | None = Field(None, validation_alias="numberOfDaysToShowCompletedIssues", serialization_alias="numberOfDaysToShowCompletedIssues", description="Issues completed this number of days ago will be excluded from the plan.", json_schema_extra={'format': 'int32'})
    release_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="releaseIds", serialization_alias="releaseIds", description="The IDs of the releases to exclude from the plan.")
    work_status_category_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="workStatusCategoryIds", serialization_alias="workStatusCategoryIds", description="The IDs of the work status categories to exclude from the plan.")
    work_status_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="workStatusIds", serialization_alias="workStatusIds", description="The IDs of the work statuses to exclude from the plan.")

class CreateOrUpdateRemoteIssueLinkBodyApplication(PermissiveModel):
    """Details of the remote application the linked item is in. For example, trello."""
    name: str | None = Field(None, description="The name of the application. Used in conjunction with the (remote) object icon title to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank items are excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\". Grouping and sorting of links may place links without an application name last.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The name-spaced type of the application, used by registered rendering apps.")

class CreateOrUpdateRemoteIssueLinkBodyObjectIcon(PermissiveModel):
    """Details of the icon for the item. If no icon is defined, the default link icon is used in Jira."""
    link: str | None = Field(None, description="The URL of the tooltip, used only for a status icon. If not set, the status icon in Jira is not clickable.")
    title: str | None = Field(None, description="The title of the icon. This is used as follows:\n\n *  For a status icon it is used as a tooltip on the icon. If not set, the status icon doesn't display a tooltip in Jira.\n *  For the remote object icon it is used in conjunction with the application name to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank itemsare excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\".")
    url16x16: str | None = Field(None, description="The URL of an icon that displays at 16x16 pixel in Jira.")

class CreateOrUpdateRemoteIssueLinkBodyObjectStatusIcon(PermissiveModel):
    """Details of the icon representing the status. If not provided, no status icon displays in Jira."""
    link: str | None = Field(None, description="The URL of the tooltip, used only for a status icon. If not set, the status icon in Jira is not clickable.")
    title: str | None = Field(None, description="The title of the icon. This is used as follows:\n\n *  For a status icon it is used as a tooltip on the icon. If not set, the status icon doesn't display a tooltip in Jira.\n *  For the remote object icon it is used in conjunction with the application name to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank itemsare excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\".")
    url16x16: str | None = Field(None, description="The URL of an icon that displays at 16x16 pixel in Jira.")

class CreateOrUpdateRemoteIssueLinkBodyObjectStatus(PermissiveModel):
    """The status of the item."""
    icon: CreateOrUpdateRemoteIssueLinkBodyObjectStatusIcon | None = Field(None, description="Details of the icon representing the status. If not provided, no status icon displays in Jira.")
    resolved: bool | None = Field(None, description="Whether the item is resolved. If set to \"true\", the link to the issue is displayed in a strikethrough font, otherwise the link displays in normal font.")

class CreateOrUpdateRemoteIssueLinkBodyObject(PermissiveModel):
    """Details of the item linked to."""
    icon: CreateOrUpdateRemoteIssueLinkBodyObjectIcon | None = Field(None, description="Details of the icon for the item. If no icon is defined, the default link icon is used in Jira.")
    status: CreateOrUpdateRemoteIssueLinkBodyObjectStatus | None = Field(None, description="The status of the item.")
    summary: str | None = Field(None, description="The summary details of the item.")
    title: str = Field(..., description="The title of the item.")
    url: str = Field(..., description="The URL of the item.")

class CreatePlanBodyExclusionRules(StrictModel):
    """The exclusion rules for the plan."""
    issue_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="issueIds", serialization_alias="issueIds", description="The IDs of the issues to exclude from the plan.")
    issue_type_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="issueTypeIds", serialization_alias="issueTypeIds", description="The IDs of the issue types to exclude from the plan.")
    number_of_days_to_show_completed_issues: int | None = Field(None, validation_alias="numberOfDaysToShowCompletedIssues", serialization_alias="numberOfDaysToShowCompletedIssues", description="Issues completed this number of days ago will be excluded from the plan.", json_schema_extra={'format': 'int32'})
    release_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="releaseIds", serialization_alias="releaseIds", description="The IDs of the releases to exclude from the plan.")
    work_status_category_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="workStatusCategoryIds", serialization_alias="workStatusCategoryIds", description="The IDs of the work status categories to exclude from the plan.")
    work_status_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="workStatusIds", serialization_alias="workStatusIds", description="The IDs of the work statuses to exclude from the plan.")

class CreatePlanBodySchedulingEndDate(StrictModel):
    """The end date field for the plan."""
    date_custom_field_id: int | None = Field(None, validation_alias="dateCustomFieldId", serialization_alias="dateCustomFieldId", description="A date custom field ID. This is required if the type is \"DateCustomField\".", json_schema_extra={'format': 'int64'})
    type_: Literal["DueDate", "TargetStartDate", "TargetEndDate", "DateCustomField"] = Field(..., validation_alias="type", serialization_alias="type", description="The date field type. This must be \"DueDate\", \"TargetStartDate\", \"TargetEndDate\" or \"DateCustomField\".")

class CreatePlanBodySchedulingStartDate(StrictModel):
    """The start date field for the plan."""
    date_custom_field_id: int | None = Field(None, validation_alias="dateCustomFieldId", serialization_alias="dateCustomFieldId", description="A date custom field ID. This is required if the type is \"DateCustomField\".", json_schema_extra={'format': 'int64'})
    type_: Literal["DueDate", "TargetStartDate", "TargetEndDate", "DateCustomField"] = Field(..., validation_alias="type", serialization_alias="type", description="The date field type. This must be \"DueDate\", \"TargetStartDate\", \"TargetEndDate\" or \"DateCustomField\".")

class CreatePlanBodyScheduling(StrictModel):
    """The scheduling settings for the plan."""
    dependencies: Literal["Sequential", "Concurrent"] | None = Field(None, description="The dependencies for the plan. This must be \"Sequential\" or \"Concurrent\".")
    end_date: CreatePlanBodySchedulingEndDate | None = Field(None, validation_alias="endDate", serialization_alias="endDate", description="The end date field for the plan.")
    estimation: Literal["StoryPoints", "Days", "Hours"] = Field(..., description="The estimation unit for the plan. This must be \"StoryPoints\", \"Days\" or \"Hours\".")
    inferred_dates: Literal["None", "SprintDates", "ReleaseDates"] | None = Field(None, validation_alias="inferredDates", serialization_alias="inferredDates", description="The inferred dates for the plan. This must be \"None\", \"SprintDates\" or \"ReleaseDates\".")
    start_date: CreatePlanBodySchedulingStartDate | None = Field(None, validation_alias="startDate", serialization_alias="startDate", description="The start date field for the plan.")

class CreateProjectWithCustomTemplateBodyDetails(StrictModel):
    """Project details: name, description, access level, assignee type, avatar, category, language, URL, and other project-level settings."""
    access_level: Literal["open", "limited", "private", "free"] | None = Field(None, validation_alias="accessLevel", serialization_alias="accessLevel", description="The access level of the project. Only used by team-managed project")
    additional_properties: dict[str, str] | None = Field(None, validation_alias="additionalProperties", serialization_alias="additionalProperties", description="Additional properties of the project")
    assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, validation_alias="assigneeType", serialization_alias="assigneeType", description="The default assignee when creating issues in the project")
    avatar_id: int | None = Field(None, validation_alias="avatarId", serialization_alias="avatarId", description="The ID of the project's avatar. Use the \\[Get project avatars\\](\\#api-rest-api-3-project-projectIdOrKey-avatar-get) operation to list the available avatars in a project.", json_schema_extra={'format': 'int64'})
    category_id: int | None = Field(None, validation_alias="categoryId", serialization_alias="categoryId", description="The ID of the project's category. A complete list of category IDs is found using the [Get all project categories](#api-rest-api-3-projectCategory-get) operation.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(None, description="Brief description of the project")
    enable_components: bool | None = Field(False, validation_alias="enableComponents", serialization_alias="enableComponents", description="Whether components are enabled for the project. Only used by company-managed project")
    key: str | None = Field(None, description="Project keys must be unique and start with an uppercase letter followed by one or more uppercase alphanumeric characters. The maximum length is 10 characters.")
    language: str | None = Field(None, description="The default language for the project")
    lead_account_id: str | None = Field(None, validation_alias="leadAccountId", serialization_alias="leadAccountId", description="The account ID of the project lead. Either `lead` or `leadAccountId` must be set when creating a project. Cannot be provided with `lead`.")
    name: str | None = Field(None, description="Name of the project")
    url: str | None = Field(None, description="A link to information about this project, such as project documentation")

class CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutSchemeDefaultFieldLayout(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutSchemePcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateFieldFieldSchemePcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenSchemeDefaultScreenScheme(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenSchemePcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeSchemeDefaultIssueTypeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeSchemePcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateNotificationPcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplatePermissionSchemePcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectFieldLayoutSchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectIssueSecuritySchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectIssueTypeSchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectIssueTypeScreenSchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectNotificationSchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectPcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectPermissionSchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProjectWorkflowSchemeId(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateProject(StrictModel):
    """The payload for creating a project"""
    field_layout_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectFieldLayoutSchemeId | None = Field(None, validation_alias="fieldLayoutSchemeId", serialization_alias="fieldLayoutSchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    issue_security_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectIssueSecuritySchemeId | None = Field(None, validation_alias="issueSecuritySchemeId", serialization_alias="issueSecuritySchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    issue_type_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectIssueTypeSchemeId | None = Field(None, validation_alias="issueTypeSchemeId", serialization_alias="issueTypeSchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    issue_type_screen_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectIssueTypeScreenSchemeId | None = Field(None, validation_alias="issueTypeScreenSchemeId", serialization_alias="issueTypeScreenSchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    notification_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectNotificationSchemeId | None = Field(None, validation_alias="notificationSchemeId", serialization_alias="notificationSchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    pcri: CreateProjectWithCustomTemplateBodyTemplateProjectPcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    permission_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectPermissionSchemeId | None = Field(None, validation_alias="permissionSchemeId", serialization_alias="permissionSchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    project_type_key: Literal["software", "business", "service_desk", "product_discovery"] | None = Field(None, validation_alias="projectTypeKey", serialization_alias="projectTypeKey", description="The [project type](https://confluence.atlassian.com/x/GwiiLQ#Jiraapplicationsoverview-Productfeaturesandprojecttypes), which defines the application-specific feature set. If you don't specify the project template you have to specify the project type.")
    workflow_scheme_id: CreateProjectWithCustomTemplateBodyTemplateProjectWorkflowSchemeId | None = Field(None, validation_alias="workflowSchemeId", serialization_alias="workflowSchemeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class CreateProjectWithCustomTemplateBodyTemplateScope(StrictModel):
    """The payload for creating a scope. Defines if a project is team-managed project or company-managed project"""
    type_: Literal["GLOBAL", "PROJECT"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the scope. Use `GLOBAL` or empty for company-managed project, and `PROJECT` for team-managed project")

class CreateProjectWithCustomTemplateBodyTemplateSecurityPcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowSchemeDefaultWorkflow(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowSchemePcri(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateSchedulingRequest(StrictModel):
    dependencies: Literal["Sequential", "Concurrent"] | None = Field(None, description="The dependencies for the plan. This must be \"Sequential\" or \"Concurrent\".")
    end_date: CreateDateFieldRequest | None = Field(None, validation_alias="endDate", serialization_alias="endDate", description="The end date field for the plan.")
    estimation: Literal["StoryPoints", "Days", "Hours"] = Field(..., description="The estimation unit for the plan. This must be \"StoryPoints\", \"Days\" or \"Hours\".")
    inferred_dates: Literal["None", "SprintDates", "ReleaseDates"] | None = Field(None, validation_alias="inferredDates", serialization_alias="inferredDates", description="The inferred dates for the plan. This must be \"None\", \"SprintDates\" or \"ReleaseDates\".")
    start_date: CreateDateFieldRequest | None = Field(None, validation_alias="startDate", serialization_alias="startDate", description="The start date field for the plan.")

class CustomFieldOptionCreate(StrictModel):
    """Details of a custom field option to create."""
    disabled: bool | None = Field(None, description="Whether the option is disabled.")
    option_id: str | None = Field(None, validation_alias="optionId", serialization_alias="optionId", description="For cascading options, the ID of a parent option.")
    value: str = Field(..., description="The value of the custom field option.")

class CustomFieldOptionUpdate(StrictModel):
    """Details of a custom field option for a context."""
    disabled: bool | None = Field(None, description="Whether the option is disabled.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the custom field option.")
    value: str | None = Field(None, description="The value of the custom field option.")

class CustomFieldReplacement(StrictModel):
    """Details about the replacement for a deleted version."""
    custom_field_id: int | None = Field(None, validation_alias="customFieldId", serialization_alias="customFieldId", description="The ID of the custom field in which to replace the version number.", json_schema_extra={'format': 'int64'})
    move_to: int | None = Field(None, validation_alias="moveTo", serialization_alias="moveTo", description="The version number to use as a replacement for the deleted version.", json_schema_extra={'format': 'int64'})

class CustomFieldValueUpdate(StrictModel):
    """A list of issue IDs and the value to update a custom field to."""
    issue_ids: list[int] = Field(..., validation_alias="issueIds", serialization_alias="issueIds", description="The list of issue IDs.")
    value: Any = Field(..., description="The value for the custom field. The value must be compatible with the [custom field type](https://developer.atlassian.com/platform/forge/manifest-reference/modules/jira-custom-field/#data-types) as follows:\n\n *  `string` the value must be a string.\n *  `number` the value must be a number.\n *  `datetime` the value must be a string that represents a date in the ISO format or the simplified extended ISO format. For example, `\"2023-01-18T12:00:00-03:00\"` or `\"2023-01-18T12:00:00.000Z\"`. However, the milliseconds part is ignored.\n *  `user` the value must be an object that contains the `accountId` field.\n *  `group` the value must be an object that contains the group `name` or `groupId` field. Because group names can change, we recommend using `groupId`.\n\nA list of appropriate values must be provided if the field is of the `list` [collection type](https://developer.atlassian.com/platform/forge/manifest-reference/modules/jira-custom-field/#collection-types).")

class DoTransitionBodyTransitionToScopeProjectAvatarUrls(StrictModel):
    """The URLs of the project's avatars."""
    n16x16: str | None = Field(None, validation_alias="16x16", serialization_alias="16x16", description="The URL of the item's 16x16 pixel avatar.", json_schema_extra={'format': 'uri'})
    n24x24: str | None = Field(None, validation_alias="24x24", serialization_alias="24x24", description="The URL of the item's 24x24 pixel avatar.", json_schema_extra={'format': 'uri'})
    n32x32: str | None = Field(None, validation_alias="32x32", serialization_alias="32x32", description="The URL of the item's 32x32 pixel avatar.", json_schema_extra={'format': 'uri'})
    n48x48: str | None = Field(None, validation_alias="48x48", serialization_alias="48x48", description="The URL of the item's 48x48 pixel avatar.", json_schema_extra={'format': 'uri'})

class DoTransitionBodyTransitionToScopeProjectProjectCategory(StrictModel):
    """The category the project belongs to."""
    description: str | None = Field(None, description="The name of the project category.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project category.")
    name: str | None = Field(None, description="The description of the project category.")
    self: str | None = Field(None, description="The URL of the project category.")

class DoTransitionBodyTransitionToScopeProject(StrictModel):
    """The project the item has scope in."""
    avatar_urls: DoTransitionBodyTransitionToScopeProjectAvatarUrls | None = Field(None, validation_alias="avatarUrls", serialization_alias="avatarUrls", description="The URLs of the project's avatars.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project.")
    key: str | None = Field(None, description="The key of the project.")
    name: str | None = Field(None, description="The name of the project.")
    project_category: DoTransitionBodyTransitionToScopeProjectProjectCategory | None = Field(None, validation_alias="projectCategory", serialization_alias="projectCategory", description="The category the project belongs to.")
    project_type_key: Literal["software", "service_desk", "business"] | None = Field(None, validation_alias="projectTypeKey", serialization_alias="projectTypeKey", description="The [project type](https://confluence.atlassian.com/x/GwiiLQ#Jiraapplicationsoverview-Productfeaturesandprojecttypes) of the project.")
    self: str | None = Field(None, description="The URL of the project details.")
    simplified: bool | None = Field(None, description="Whether or not the project is simplified.")

class DoTransitionBodyTransitionToScope(PermissiveModel):
    """The scope of the field."""
    project: DoTransitionBodyTransitionToScopeProject | None = Field(None, description="The project the item has scope in.")
    type_: Literal["PROJECT", "TEMPLATE"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of scope.")

class DoTransitionBodyTransitionToStatusCategory(PermissiveModel):
    """The category assigned to the status."""
    color_name: str | None = Field(None, validation_alias="colorName", serialization_alias="colorName", description="The name of the color used to represent the status category.")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the status category.", json_schema_extra={'format': 'int64'})
    key: str | None = Field(None, description="The key of the status category.")
    name: str | None = Field(None, description="The name of the status category.")
    self: str | None = Field(None, description="The URL of the status category.")

class DoTransitionBodyTransitionTo(PermissiveModel):
    """Details of the issue status after the transition."""
    description: str | None = Field(None, description="The description of the status.")
    icon_url: str | None = Field(None, validation_alias="iconUrl", serialization_alias="iconUrl", description="The URL of the icon used to represent the status.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the status.")
    name: str | None = Field(None, description="The name of the status.")
    scope: DoTransitionBodyTransitionToScope | None = Field(None, description="The scope of the field.")
    self: str | None = Field(None, description="The URL of the status.")
    status_category: DoTransitionBodyTransitionToStatusCategory | None = Field(None, validation_alias="statusCategory", serialization_alias="statusCategory", description="The category assigned to the status.")

class EntityProperty(StrictModel):
    """An entity property, for more information see [Entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/)."""
    key: str | None = Field(None, description="The key of the property. Required on create and update.")
    value: Any | None = Field(None, description="The value of the property. Required on create and update.")

class EvaluateJsisJiraExpressionBodyContextIssue(StrictModel):
    """The issue that is available under the `issue` variable when evaluating the expression."""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the referenced item.", json_schema_extra={'format': 'int64'})
    key: str | None = Field(None, description="The key of the referenced item.")

class EvaluateJsisJiraExpressionBodyContextIssuesJql(StrictModel):
    """The JQL query that specifies the set of issues available in the Jira expression."""
    max_results: int | None = Field(None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of issues to return from the JQL query. max results value considered may be lower than the number specific here.", json_schema_extra={'format': 'int32'})
    next_page_token: str | None = Field(None, validation_alias="nextPageToken", serialization_alias="nextPageToken", description="The token for a page to fetch that is not the first page. The first page has a `nextPageToken` of `null`. Use the `nextPageToken` to fetch the next page of issues.")
    query: str | None = Field(None, description="The JQL query, required to be bounded. Additionally, `orderBy` clause can contain a maximum of 7 fields")

class EvaluateJsisJiraExpressionBodyContextIssues(StrictModel):
    """The collection of issues that is available under the `issues` variable when evaluating the expression."""
    jql: EvaluateJsisJiraExpressionBodyContextIssuesJql | None = Field(None, description="The JQL query that specifies the set of issues available in the Jira expression.")

class EvaluateJsisJiraExpressionBodyContextProject(StrictModel):
    """The project that is available under the `project` variable when evaluating the expression."""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the referenced item.", json_schema_extra={'format': 'int64'})
    key: str | None = Field(None, description="The key of the referenced item.")

class ExpandPrioritySchemePage(PermissiveModel):
    max_results: int | None = Field(None, validation_alias="maxResults", serialization_alias="maxResults", json_schema_extra={'format': 'int32'})
    start_at: int | None = Field(None, validation_alias="startAt", serialization_alias="startAt", json_schema_extra={'format': 'int64'})
    total: int | None = Field(None, json_schema_extra={'format': 'int64'})

class FieldUpdateOperation(StrictModel):
    """Details of an operation to perform on a field."""
    add: Any | None = Field(None, description="The value to add to the field.")
    copy_: Any | None = Field(None, validation_alias="copy", serialization_alias="copy", description="The field value to copy from another issue.")
    edit: Any | None = Field(None, description="The value to edit in the field.")
    remove: Any | None = Field(None, description="The value to removed from the field.")
    set_: Any | None = Field(None, validation_alias="set", serialization_alias="set", description="The value to set in the field.")

class GroupName(StrictModel):
    """Details about a group."""
    group_id: str | None = Field(None, validation_alias="groupId", serialization_alias="groupId", description="The ID of the group, which uniquely identifies the group across all Atlassian products. For example, *952d12c3-5b5b-4d04-bb32-44d383afc4b2*.")
    name: str | None = Field(None, description="The name of group.")
    self: str | None = Field(None, description="The URL for these group details.", json_schema_extra={'format': 'uri'})

class ApplicationRole(StrictModel):
    """Details of an application role."""
    default_groups: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="defaultGroups", serialization_alias="defaultGroups", description="The groups that are granted default access for this application role. As a group's name can change, use of `defaultGroupsDetails` is recommended to identify a groups.")
    default_groups_details: list[GroupName] | None = Field(None, validation_alias="defaultGroupsDetails", serialization_alias="defaultGroupsDetails", description="The groups that are granted default access for this application role.")
    defined: bool | None = Field(None, description="Deprecated.")
    group_details: list[GroupName] | None = Field(None, validation_alias="groupDetails", serialization_alias="groupDetails", description="The groups associated with the application role.")
    groups: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="The groups associated with the application role. As a group's name can change, use of `groupDetails` is recommended to identify a groups.")
    has_unlimited_seats: bool | None = Field(None, validation_alias="hasUnlimitedSeats", serialization_alias="hasUnlimitedSeats")
    key: str | None = Field(None, description="The key of the application role.")
    name: str | None = Field(None, description="The display name of the application role.")
    number_of_seats: int | None = Field(None, validation_alias="numberOfSeats", serialization_alias="numberOfSeats", description="The maximum count of users on your license.", json_schema_extra={'format': 'int32'})
    platform: bool | None = Field(None, description="Indicates if the application role belongs to Jira platform (`jira-core`).")
    remaining_seats: int | None = Field(None, validation_alias="remainingSeats", serialization_alias="remainingSeats", description="The count of users remaining on your license.", json_schema_extra={'format': 'int32'})
    selected_by_default: bool | None = Field(None, validation_alias="selectedByDefault", serialization_alias="selectedByDefault", description="Determines whether this application role should be selected by default on user creation.")
    user_count: int | None = Field(None, validation_alias="userCount", serialization_alias="userCount", description="The number of users counting against your license.", json_schema_extra={'format': 'int32'})
    user_count_description: str | None = Field(None, validation_alias="userCountDescription", serialization_alias="userCountDescription", description="The [type of users](https://confluence.atlassian.com/x/lRW3Ng) being counted against your license.")

class HistoryMetadataParticipant(PermissiveModel):
    """Details of user or system associated with a issue history metadata item."""
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl", description="The URL to an avatar for the user or system associated with a history record.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the user or system associated with a history record.")
    display_name_key: str | None = Field(None, validation_alias="displayNameKey", serialization_alias="displayNameKey", description="The key of the display name of the user or system associated with a history record.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the user or system associated with a history record.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the user or system associated with a history record.")
    url: str | None = Field(None, description="The URL of the user or system associated with a history record.")

class HistoryMetadata(PermissiveModel):
    """Details of issue history metadata."""
    activity_description: str | None = Field(None, validation_alias="activityDescription", serialization_alias="activityDescription", description="The activity described in the history record.")
    activity_description_key: str | None = Field(None, validation_alias="activityDescriptionKey", serialization_alias="activityDescriptionKey", description="The key of the activity described in the history record.")
    actor: HistoryMetadataParticipant | None = Field(None, description="Details of the user whose action created the history record.")
    cause: HistoryMetadataParticipant | None = Field(None, description="Details of the cause that triggered the creation the history record.")
    description: str | None = Field(None, description="The description of the history record.")
    description_key: str | None = Field(None, validation_alias="descriptionKey", serialization_alias="descriptionKey", description="The description key of the history record.")
    email_description: str | None = Field(None, validation_alias="emailDescription", serialization_alias="emailDescription", description="The description of the email address associated the history record.")
    email_description_key: str | None = Field(None, validation_alias="emailDescriptionKey", serialization_alias="emailDescriptionKey", description="The description key of the email address associated the history record.")
    extra_data: dict[str, str] | None = Field(None, validation_alias="extraData", serialization_alias="extraData", description="Additional arbitrary information about the history record.")
    generator: HistoryMetadataParticipant | None = Field(None, description="Details of the system that generated the history record.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the history record.")

class Icon(PermissiveModel):
    """An icon. If no icon is defined:

 *  for a status icon, no status icon displays in Jira.
 *  for the remote object icon, the default link icon displays in Jira."""
    link: str | None = Field(None, description="The URL of the tooltip, used only for a status icon. If not set, the status icon in Jira is not clickable.")
    title: str | None = Field(None, description="The title of the icon. This is used as follows:\n\n *  For a status icon it is used as a tooltip on the icon. If not set, the status icon doesn't display a tooltip in Jira.\n *  For the remote object icon it is used in conjunction with the application name to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank itemsare excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\".")
    url16x16: str | None = Field(None, description="The URL of an icon that displays at 16x16 pixel in Jira.")

class IssueContextVariable(PermissiveModel):
    """An [issue](https://developer.atlassian.com/cloud/jira/platform/jira-expressions-type-reference#issue) specified by ID or key. All the fields of the issue object are available in the Jira expression."""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The issue ID.", json_schema_extra={'format': 'int64'})
    key: str | None = Field(None, description="The issue key.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of custom context variable.")

class JiraColorInput(StrictModel):
    name: str

class JiraColorField(StrictModel):
    color: JiraColorInput
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")

class JiraComponentField(StrictModel):
    component_id: int = Field(..., validation_alias="componentId", serialization_alias="componentId", json_schema_extra={'format': 'int64'})

class JiraDateInput(StrictModel):
    formatted_date: str = Field(..., validation_alias="formattedDate", serialization_alias="formattedDate")

class JiraDateField(StrictModel):
    date: JiraDateInput | None = None
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")

class JiraDateTimeInput(StrictModel):
    formatted_date_time: str = Field(..., validation_alias="formattedDateTime", serialization_alias="formattedDateTime")

class JiraDateTimeField(StrictModel):
    date_time: JiraDateTimeInput = Field(..., validation_alias="dateTime", serialization_alias="dateTime")
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")

class JiraGroupInput(StrictModel):
    group_name: str = Field(..., validation_alias="groupName", serialization_alias="groupName")

class JiraLabelPropertiesInputJackson1(StrictModel):
    color: Literal["GREY_LIGHTEST", "GREY_LIGHTER", "GREY", "GREY_DARKER", "GREY_DARKEST", "PURPLE_LIGHTEST", "PURPLE_LIGHTER", "PURPLE", "PURPLE_DARKER", "PURPLE_DARKEST", "BLUE_LIGHTEST", "BLUE_LIGHTER", "BLUE", "BLUE_DARKER", "BLUE_DARKEST", "TEAL_LIGHTEST", "TEAL_LIGHTER", "TEAL", "TEAL_DARKER", "TEAL_DARKEST", "GREEN_LIGHTEST", "GREEN_LIGHTER", "GREEN", "GREEN_DARKER", "GREEN_DARKEST", "LIME_LIGHTEST", "LIME_LIGHTER", "LIME", "LIME_DARKER", "LIME_DARKEST", "YELLOW_LIGHTEST", "YELLOW_LIGHTER", "YELLOW", "YELLOW_DARKER", "YELLOW_DARKEST", "ORANGE_LIGHTEST", "ORANGE_LIGHTER", "ORANGE", "ORANGE_DARKER", "ORANGE_DARKEST", "RED_LIGHTEST", "RED_LIGHTER", "RED", "RED_DARKER", "RED_DARKEST", "MAGENTA_LIGHTEST", "MAGENTA_LIGHTER", "MAGENTA", "MAGENTA_DARKER", "MAGENTA_DARKEST"] | None = None
    name: str | None = None

class JiraLabelsInput(StrictModel):
    name: str

class JiraLabelsField(StrictModel):
    bulk_edit_multi_select_field_option: Literal["ADD", "REMOVE", "REPLACE", "REMOVE_ALL"] = Field(..., validation_alias="bulkEditMultiSelectFieldOption", serialization_alias="bulkEditMultiSelectFieldOption")
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    label_properties: list[JiraLabelPropertiesInputJackson1] | None = Field(None, validation_alias="labelProperties", serialization_alias="labelProperties")
    labels: list[JiraLabelsInput]

class JiraMultipleGroupPickerField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    groups: list[JiraGroupInput]

class JiraNumberField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    value: float | None = Field(None, json_schema_extra={'format': 'double'})

class JiraRichTextInput(StrictModel):
    adf_value: dict[str, Any] | None = Field(None, validation_alias="adfValue", serialization_alias="adfValue")

class JiraRichTextField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    rich_text: JiraRichTextInput = Field(..., validation_alias="richText", serialization_alias="richText")

class JiraSelectedOptionField(StrictModel):
    option_id: int | None = Field(None, validation_alias="optionId", serialization_alias="optionId", json_schema_extra={'format': 'int64'})

class JiraCascadingSelectField(StrictModel):
    child_option_value: JiraSelectedOptionField | None = Field(None, validation_alias="childOptionValue", serialization_alias="childOptionValue")
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    parent_option_value: JiraSelectedOptionField = Field(..., validation_alias="parentOptionValue", serialization_alias="parentOptionValue")

class JiraMultipleSelectField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    options: list[JiraSelectedOptionField]

class JiraSingleGroupPickerField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    group: JiraGroupInput

class JiraSingleLineTextField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    text: str

class JiraSingleSelectField(StrictModel):
    """Add or clear a single select field:

 *  To add, specify the option with an `optionId`.
 *  To clear, pass an option with `optionId` as `-1`."""
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    option: JiraSelectedOptionField

class JiraUrlField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    url: str

class JiraUserField(StrictModel):
    account_id: str = Field(..., validation_alias="accountId", serialization_alias="accountId")

class JiraMultipleSelectUserPickerField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    users: list[JiraUserField] | None = None

class JiraSingleSelectUserPickerField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    user: JiraUserField | None = None

class JiraVersionField(StrictModel):
    version_id: str | None = Field(None, validation_alias="versionId", serialization_alias="versionId")

class JiraMultipleVersionPickerField(StrictModel):
    bulk_edit_multi_select_field_option: Literal["ADD", "REMOVE", "REPLACE", "REMOVE_ALL"] = Field(..., validation_alias="bulkEditMultiSelectFieldOption", serialization_alias="bulkEditMultiSelectFieldOption")
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    versions: list[JiraVersionField]

class JiraSingleVersionPickerField(StrictModel):
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")
    version: JiraVersionField

class JsonContextVariable(PermissiveModel):
    """A JSON object with custom content."""
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of custom context variable.")
    value: dict[str, Any] | None = Field(None, description="A JSON object containing custom content.")

class JsonNode(StrictModel):
    array: bool | None = None
    big_decimal: bool | None = Field(None, validation_alias="bigDecimal", serialization_alias="bigDecimal")
    big_integer: bool | None = Field(None, validation_alias="bigInteger", serialization_alias="bigInteger")
    big_integer_value: int | None = Field(None, validation_alias="bigIntegerValue", serialization_alias="bigIntegerValue")
    binary: bool | None = None
    binary_value: list[str] | None = Field(None, validation_alias="binaryValue", serialization_alias="binaryValue")
    boolean: bool | None = None
    boolean_value: bool | None = Field(None, validation_alias="booleanValue", serialization_alias="booleanValue")
    container_node: bool | None = Field(None, validation_alias="containerNode", serialization_alias="containerNode")
    decimal_value: float | None = Field(None, validation_alias="decimalValue", serialization_alias="decimalValue")
    double: bool | None = None
    double_value: float | None = Field(None, validation_alias="doubleValue", serialization_alias="doubleValue", json_schema_extra={'format': 'double'})
    elements: dict[str, Any] | None = None
    field_names: dict[str, Any] | None = Field(None, validation_alias="fieldNames", serialization_alias="fieldNames")
    fields: dict[str, Any] | None = None
    floating_point_number: bool | None = Field(None, validation_alias="floatingPointNumber", serialization_alias="floatingPointNumber")
    int_: bool | None = Field(None, validation_alias="int", serialization_alias="int")
    int_value: int | None = Field(None, validation_alias="intValue", serialization_alias="intValue", json_schema_extra={'format': 'int32'})
    integral_number: bool | None = Field(None, validation_alias="integralNumber", serialization_alias="integralNumber")
    long: bool | None = None
    long_value: int | None = Field(None, validation_alias="longValue", serialization_alias="longValue", json_schema_extra={'format': 'int64'})
    missing_node: bool | None = Field(None, validation_alias="missingNode", serialization_alias="missingNode")
    null: bool | None = None
    number: bool | None = None
    number_type: Literal["INT", "LONG", "BIG_INTEGER", "FLOAT", "DOUBLE", "BIG_DECIMAL"] | None = Field(None, validation_alias="numberType", serialization_alias="numberType")
    number_value: float | None = Field(None, validation_alias="numberValue", serialization_alias="numberValue")
    object_: bool | None = Field(None, validation_alias="object", serialization_alias="object")
    pojo: bool | None = None
    text_value: str | None = Field(None, validation_alias="textValue", serialization_alias="textValue")
    textual: bool | None = None
    value_as_boolean: bool | None = Field(None, validation_alias="valueAsBoolean", serialization_alias="valueAsBoolean")
    value_as_double: float | None = Field(None, validation_alias="valueAsDouble", serialization_alias="valueAsDouble", json_schema_extra={'format': 'double'})
    value_as_int: int | None = Field(None, validation_alias="valueAsInt", serialization_alias="valueAsInt", json_schema_extra={'format': 'int32'})
    value_as_long: int | None = Field(None, validation_alias="valueAsLong", serialization_alias="valueAsLong", json_schema_extra={'format': 'int64'})
    value_as_text: str | None = Field(None, validation_alias="valueAsText", serialization_alias="valueAsText")
    value_node: bool | None = Field(None, validation_alias="valueNode", serialization_alias="valueNode")

class IssueEntityPropertiesForMultiUpdate(StrictModel):
    """An issue ID with entity property values. See [Entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/) for more information."""
    issue_id: int | None = Field(None, validation_alias="issueID", serialization_alias="issueID", description="The ID of the issue.", json_schema_extra={'format': 'int64'})
    properties: dict[str, JsonNode] | None = Field(None, description="Entity properties to set on the issue. The maximum length of an issue property value is 32768 characters.", min_length=1, max_length=10)

class JsonTypeBean(StrictModel):
    """The schema of a field."""
    configuration: dict[str, Any] | None = Field(None, description="If the field is a custom field, the configuration of the field.")
    custom: str | None = Field(None, description="If the field is a custom field, the URI of the field.")
    custom_id: int | None = Field(None, validation_alias="customId", serialization_alias="customId", description="If the field is a custom field, the custom ID of the field.", json_schema_extra={'format': 'int64'})
    items: str | None = Field(None, description="When the data type is an array, the name of the field items within the array.")
    system: str | None = Field(None, description="If the field is a system field, the name of the field.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The data type of the field.")

class FieldMetadata(StrictModel):
    """The metadata describing an issue field."""
    allowed_values: list[Any] | None = Field(None, validation_alias="allowedValues", serialization_alias="allowedValues", description="The list of values allowed in the field.")
    auto_complete_url: str | None = Field(None, validation_alias="autoCompleteUrl", serialization_alias="autoCompleteUrl", description="The URL that can be used to automatically complete the field.")
    configuration: dict[str, Any] | None = Field(None, description="The configuration properties.")
    default_value: Any | None = Field(None, validation_alias="defaultValue", serialization_alias="defaultValue", description="The default value of the field.")
    has_default_value: bool | None = Field(None, validation_alias="hasDefaultValue", serialization_alias="hasDefaultValue", description="Whether the field has a default value.")
    key: str = Field(..., description="The key of the field.")
    name: str = Field(..., description="The name of the field.")
    operations: list[str] = Field(..., description="The list of operations that can be performed on the field.")
    required: bool = Field(..., description="Whether the field is required.")
    schema_: JsonTypeBean = Field(..., validation_alias="schema", serialization_alias="schema", description="The data type of the field.")

class DoTransitionBodyTransition(PermissiveModel):
    """Details of a transition. Required when performing a transition, optional when creating or editing an issue."""
    expand: str | None = Field(None, description="Expand options that include additional transition details in the response.")
    fields: dict[str, FieldMetadata] | None = Field(None, description="Details of the fields associated with the issue transition screen. Use this information to populate `fields` and `update` in a transition request.")
    has_screen: bool | None = Field(None, validation_alias="hasScreen", serialization_alias="hasScreen", description="Whether there is a screen associated with the issue transition.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the issue transition. Required when specifying a transition to undertake.")
    is_available: bool | None = Field(None, validation_alias="isAvailable", serialization_alias="isAvailable", description="Whether the transition is available to be performed.")
    is_conditional: bool | None = Field(None, validation_alias="isConditional", serialization_alias="isConditional", description="Whether the issue has to meet criteria before the issue transition is applied.")
    is_global: bool | None = Field(None, validation_alias="isGlobal", serialization_alias="isGlobal", description="Whether the issue transition is global, that is, the transition is applied to issues regardless of their status.")
    is_initial: bool | None = Field(None, validation_alias="isInitial", serialization_alias="isInitial", description="Whether this is the initial issue transition for the workflow.")
    looped: bool | None = None
    name: str | None = Field(None, description="The name of the issue transition.")
    to: DoTransitionBodyTransitionTo | None = Field(None, description="Details of the issue status after the transition.")

class LinkIssuesBodyCommentVisibility(PermissiveModel):
    """The group or role to which this comment is visible. Optional on create and update."""
    identifier: str | None = Field(None, description="The ID of the group or the name of the role that visibility of this item is restricted to.")
    type_: Literal["group", "role"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Whether visibility of this item is restricted to a group or role.")
    value: str | None = Field(None, description="The name of the group or role that visibility of this item is restricted to. Please note that the name of a group is mutable, to reliably identify a group use `identifier`.")

class ListWrapperCallbackApplicationRole(RootModel[dict[str, Any]]):
    pass

class ListWrapperCallbackGroupName(RootModel[dict[str, Any]]):
    pass

class MandatoryFieldValue(PermissiveModel):
    """List of string of inputs"""
    retain: bool | None = Field(True, description="If `true`, will try to retain original non-null issue field values on move.")
    type_: Literal["adf", "raw"] | None = Field('raw', validation_alias="type", serialization_alias="type", description="Will treat as `MandatoryFieldValue` if type is `raw` or `empty`")
    value: list[str] = Field(..., description="Value for each field. Provide a `list of strings` for non-ADF fields.")

class MandatoryFieldValueForAdf(PermissiveModel):
    """An object notation input"""
    retain: bool | None = Field(True, description="If `true`, will try to retain original non-null issue field values on move.")
    type_: Literal["adf", "raw"] = Field(..., validation_alias="type", serialization_alias="type", description="Will treat as `MandatoryFieldValueForADF` if type is `adf`")
    value: dict[str, Any] = Field(..., description="Value for each field. Accepts Atlassian Document Format (ADF) for rich text fields like `description`, `environments`. For ADF format details, refer to: [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure)")

class MultipleCustomFieldValuesUpdate(StrictModel):
    """A custom field and its new value with a list of issue to update."""
    custom_field: str = Field(..., validation_alias="customField", serialization_alias="customField", description="The ID or key of the custom field. For example, `customfield_10010`.")
    issue_ids: list[int] = Field(..., validation_alias="issueIds", serialization_alias="issueIds", description="The list of issue IDs.")
    value: Any = Field(..., description="The value for the custom field. The value must be compatible with the [custom field type](https://developer.atlassian.com/platform/forge/manifest-reference/modules/jira-custom-field/#data-types) as follows:\n\n *  `string` the value must be a string.\n *  `number` the value must be a number.\n *  `datetime` the value must be a string that represents a date in the ISO format or the simplified extended ISO format. For example, `\"2023-01-18T12:00:00-03:00\"` or `\"2023-01-18T12:00:00.000Z\"`. However, the milliseconds part is ignored.\n *  `user` the value must be an object that contains the `accountId` field.\n *  `group` the value must be an object that contains the group `name` or `groupId` field. Because group names can change, we recommend using `groupId`.\n\nA list of appropriate values must be provided if the field is of the `list` [collection type](https://developer.atlassian.com/platform/forge/manifest-reference/modules/jira-custom-field/#collection-types).")

class NonWorkingDay(StrictModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    iso8601_date: str | None = Field(None, validation_alias="iso8601Date", serialization_alias="iso8601Date")

class NotificationSchemeEventIdPayload(StrictModel):
    """The event ID to use for reference in the payload"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The event ID to use for reference in the payload")

class NotificationSchemeNotificationDetailsPayload(StrictModel):
    """The configuration for notification recipents"""
    notification_type: str | None = Field(None, validation_alias="notificationType", serialization_alias="notificationType", description="The type of notification.")
    parameter: str | None = Field(None, description="The parameter of the notification, should be eiither null if not required, or PCRI.")

class NotificationSchemeEventPayload(StrictModel):
    """The payload for creating a notification scheme event. Defines which notifications should be sent for a specific event"""
    event: NotificationSchemeEventIdPayload | None = None
    notifications: list[NotificationSchemeNotificationDetailsPayload] | None = Field(None, description="The configuration for notification recipents")

class CreateProjectWithCustomTemplateBodyTemplateNotification(StrictModel):
    """The payload for creating a notification scheme. The user has to supply the ID for the default notification scheme. For CMP this is provided in the project payload and should be left empty, for TMP it's provided using this payload"""
    description: str | None = Field(None, description="The description of the notification scheme")
    name: str | None = Field(None, description="The name of the notification scheme")
    notification_scheme_events: list[NotificationSchemeEventPayload] | None = Field(None, validation_alias="notificationSchemeEvents", serialization_alias="notificationSchemeEvents", description="The events and notifications for the notification scheme")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use when there is a conflict with an existing entity")
    pcri: CreateProjectWithCustomTemplateBodyTemplateNotificationPcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class Priority(PermissiveModel):
    """An issue priority."""
    avatar_id: int | None = Field(None, validation_alias="avatarId", serialization_alias="avatarId", description="The avatarId of the avatar for the issue priority. This parameter is nullable and when set, this avatar references the universal avatar APIs.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(None, description="The description of the issue priority.")
    icon_url: str | None = Field(None, validation_alias="iconUrl", serialization_alias="iconUrl", description="The URL of the icon for the issue priority.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the issue priority.")
    is_default: bool | None = Field(None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether this priority is the default.")
    name: str | None = Field(None, description="The name of the issue priority.")
    schemes: ExpandPrioritySchemePage | None = Field(None, description="Priority schemes associated with the issue priority.")
    self: str | None = Field(None, description="The URL of the issue priority.")
    status_color: str | None = Field(None, validation_alias="statusColor", serialization_alias="statusColor", description="The color used to indicate the issue priority.")

class ProjectCategory(StrictModel):
    """A project category."""
    description: str | None = Field(None, description="The description of the project category.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project category.")
    name: str | None = Field(None, description="The name of the project category. Required on create, optional on update.")
    self: str | None = Field(None, description="The URL of the project category.", json_schema_extra={'format': 'uri'})

class ProjectCreateResourceIdentifier(StrictModel):
    """Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation"""
    an_id: bool | None = Field(None, validation_alias="anID", serialization_alias="anID")
    areference: bool | None = None
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId")
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["id", "ref"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BoardColumnPayload(StrictModel):
    """The payload for creating a board column"""
    maximum_issue_constraint: int | None = Field(None, validation_alias="maximumIssueConstraint", serialization_alias="maximumIssueConstraint", description="The maximum issue constraint for the column", json_schema_extra={'format': 'int64'})
    minimum_issue_constraint: int | None = Field(None, validation_alias="minimumIssueConstraint", serialization_alias="minimumIssueConstraint", description="The minimum issue constraint for the column", json_schema_extra={'format': 'int64'})
    name: str | None = Field(None, description="The name of the column")
    status_ids: list[ProjectCreateResourceIdentifier] | None = Field(None, validation_alias="statusIds", serialization_alias="statusIds", description="The status IDs for the column")

class CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutScheme(StrictModel):
    """Deprecated use [fieldAssociationScheme](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-field-schemes/#api-group-field-schemes) instead Defines the payload for the field layout schemes. See [ Field configuration scheme](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfigurationscheme-post).

[ How to configure a field configuration scheme](https://support.atlassian.com/jira-cloud-administration/docs/configure-a-field-configuration-scheme/)."""
    default_field_layout: CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutSchemeDefaultFieldLayout | None = Field(None, validation_alias="defaultFieldLayout", serialization_alias="defaultFieldLayout", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    description: str | None = Field(None, description="The description of the field layout scheme")
    explicit_mappings: dict[str, ProjectCreateResourceIdentifier] | None = Field(None, validation_alias="explicitMappings", serialization_alias="explicitMappings", description="There is a default configuration \"fieldlayout\" that is applied to all issue types using this scheme that don't have an explicit mapping users can create (or re-use existing) configurations for other issue types and map them to this scheme")
    name: str | None = Field(None, description="The name of the field layout scheme")
    pcri: CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutSchemePcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenScheme(StrictModel):
    """Defines the payload for the issue type screen schemes. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/\\#api-rest-api-3-issuetypescreenscheme-post"""
    default_screen_scheme: CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenSchemeDefaultScreenScheme | None = Field(None, validation_alias="defaultScreenScheme", serialization_alias="defaultScreenScheme", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    description: str | None = Field(None, description="The description of the issue type screen scheme")
    explicit_mappings: dict[str, ProjectCreateResourceIdentifier] | None = Field(None, validation_alias="explicitMappings", serialization_alias="explicitMappings", description="The IDs of the screen schemes for the issue type IDs and default. A default entry is required to create an issue type screen scheme, it defines the mapping for all issue types without a screen scheme.")
    name: str | None = Field(None, description="The name of the issue type screen scheme")
    pcri: CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenSchemePcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeScheme(StrictModel):
    """The payload for creating issue type schemes"""
    default_issue_type_id: CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeSchemeDefaultIssueTypeId | None = Field(None, validation_alias="defaultIssueTypeId", serialization_alias="defaultIssueTypeId", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    description: str | None = Field(None, description="The description of the issue type scheme")
    issue_type_ids: list[ProjectCreateResourceIdentifier] | None = Field(None, validation_alias="issueTypeIds", serialization_alias="issueTypeIds", description="The issue type IDs for the issue type scheme")
    name: str | None = Field(None, description="The name of the issue type scheme")
    pcri: CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeSchemePcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowScheme(StrictModel):
    """The payload for creating a workflow scheme. See https://www.atlassian.com/software/jira/guides/workflows/overview\\#what-is-a-jira-workflow-scheme"""
    default_workflow: CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowSchemeDefaultWorkflow | None = Field(None, validation_alias="defaultWorkflow", serialization_alias="defaultWorkflow", description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    description: str | None = Field(None, description="The description of the workflow scheme")
    explicit_mappings: dict[str, ProjectCreateResourceIdentifier] | None = Field(None, validation_alias="explicitMappings", serialization_alias="explicitMappings", description="Association between issuetypes and workflows")
    name: str | None = Field(None, description="The name of the workflow scheme")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use if there is a conflict with another workflow scheme")
    pcri: CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowSchemePcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class CustomFieldPayload(StrictModel):
    """Defines the payload for the custom field definitions. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/\\#api-rest-api-3-field-post"""
    cf_type: str | None = Field(None, validation_alias="cfType", serialization_alias="cfType", description="The type of the custom field")
    description: str | None = Field(None, description="The description of the custom field")
    name: str | None = Field(None, description="The name of the custom field")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use when there is a conflict with an existing custom field. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters")
    pcri: ProjectCreateResourceIdentifier | None = None
    scope: Literal["GLOBAL", "TEMPLATE", "PROJECT"] | None = Field(None, description="Allows an overwrite to declare the new Custom Field to be created as a GLOBAL-scoped field. Leave this as empty or null to use the project's default scope.")
    searcher_key: str | None = Field(None, validation_alias="searcherKey", serialization_alias="searcherKey", description="The searcher key of the custom field")

class FieldAssociationItemPayload(StrictModel):
    """Defines the payload for the field association scheme."""
    description: str | None = Field(None, description="The description of the field association item")
    pcri: ProjectCreateResourceIdentifier | None = None
    qualifier_id: ProjectCreateResourceIdentifier | None = Field(None, validation_alias="qualifierId", serialization_alias="qualifierId")
    qualifier_type: ProjectCreateResourceIdentifier | None = Field(None, validation_alias="qualifierType", serialization_alias="qualifierType")
    renderer_type: str | None = Field(None, validation_alias="rendererType", serialization_alias="rendererType", description="The renderer type of the field")
    required: bool | None = Field(None, description="Whether the field is required")

class CreateProjectWithCustomTemplateBodyTemplateFieldFieldScheme(StrictModel):
    """Defines the payload to configure the field scheme for a project. See [Field schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-field-schemes/#api-group-field-schemes)."""
    description: str | None = Field(None, description="The description of the field scheme")
    items: list[FieldAssociationItemPayload] | None = Field(None, description="The field association items for this field scheme.")
    name: str | None = Field(None, description="The name of the field scheme")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use when there is a conflict with an existing field scheme. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters")
    pcri: CreateProjectWithCustomTemplateBodyTemplateFieldFieldSchemePcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class FieldLayoutConfiguration(StrictModel):
    """Defines the payload for the field layout configuration. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/\\#api-rest-api-3-fieldconfiguration-post"""
    field: bool | None = Field(None, description="Whether to show the field")
    pcri: ProjectCreateResourceIdentifier | None = None
    required: bool | None = Field(None, description="Whether the field is required")

class FieldLayoutPayload(StrictModel):
    """Defines the payload for the field layouts. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/\\#api-group-issue-field-configurations" + fieldlayout is what users would see as "Field Configuration" in Jira's UI - https://support.atlassian.com/jira-cloud-administration/docs/manage-issue-field-configurations/"""
    configuration: list[FieldLayoutConfiguration] | None = Field(None, description="The field layout configuration. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/\\#api-rest-api-3-fieldconfiguration-post")
    description: str | None = Field(None, description="The description of the field layout")
    name: str | None = Field(None, description="The name of the field layout")
    pcri: ProjectCreateResourceIdentifier | None = None

class FromLayoutPayload(StrictModel):
    """The payload for the layout details for the start end of a transition"""
    from_port: int | None = Field(None, validation_alias="fromPort", serialization_alias="fromPort", description="The port that the transition can be made from", json_schema_extra={'format': 'int32'})
    status: ProjectCreateResourceIdentifier | None = None
    to_port_override: int | None = Field(None, validation_alias="toPortOverride", serialization_alias="toPortOverride", description="The port that the transition goes to", json_schema_extra={'format': 'int32'})

class IssueLayoutItemPayload(StrictModel):
    """Defines the payload to configure the issue layout item for a project."""
    item_key: ProjectCreateResourceIdentifier | None = Field(None, validation_alias="itemKey", serialization_alias="itemKey")
    properties: dict[str, Any] | None = Field(None, description="Additional properties for this item. This field is only used when the type is FIELD.")
    section_type: Literal["content", "primaryContext", "secondaryContext"] | None = Field(None, validation_alias="sectionType", serialization_alias="sectionType", description="The item section type")
    type_: Literal["FIELD"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The item type. Currently only support FIELD")

class IssueLayoutPayload(StrictModel):
    """Defines the payload to configure the issue layouts for a project."""
    container_id: ProjectCreateResourceIdentifier | None = Field(None, validation_alias="containerId", serialization_alias="containerId")
    issue_layout_type: Literal["ISSUE_VIEW", "ISSUE_CREATE", "REQUEST_FORM"] | None = Field(None, validation_alias="issueLayoutType", serialization_alias="issueLayoutType", description="The issue layout type")
    items: list[IssueLayoutItemPayload] | None = Field(None, description="The configuration of items in the issue layout")
    pcri: ProjectCreateResourceIdentifier | None = None

class IssueTypeHierarchyPayload(StrictModel):
    """The payload for creating an issue type hierarchy"""
    hierarchy_level: int | None = Field(None, validation_alias="hierarchyLevel", serialization_alias="hierarchyLevel", description="The hierarchy level of the issue type. 0, 1, 2, 3 .. n; Negative values for subtasks", json_schema_extra={'format': 'int32'})
    name: str | None = Field(None, description="The name of the issue type")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The conflict strategy to use when the issue type already exists. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters")
    pcri: ProjectCreateResourceIdentifier | None = None

class IssueTypePayload(StrictModel):
    """The payload for creating an issue type"""
    avatar_id: int | None = Field(None, validation_alias="avatarId", serialization_alias="avatarId", description="The avatar ID of the issue type. Go to https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/\\#api-rest-api-3-avatar-type-system-get to choose an avatarId existing in Jira", json_schema_extra={'format': 'int64'})
    description: str | None = Field(None, description="The description of the issue type")
    hierarchy_level: int | None = Field(None, validation_alias="hierarchyLevel", serialization_alias="hierarchyLevel", description="The hierarchy level of the issue type. 0, 1, 2, 3 .. n; Negative values for subtasks", json_schema_extra={'format': 'int32'})
    name: str | None = Field(None, description="The name of the issue type")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The conflict strategy to use when the issue type already exists. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters")
    pcri: ProjectCreateResourceIdentifier | None = None

class CreateProjectWithCustomTemplateBodyTemplateIssueType(StrictModel):
    """The payload for creating issue types in a project"""
    issue_type_hierarchy: list[IssueTypeHierarchyPayload] | None = Field(None, validation_alias="issueTypeHierarchy", serialization_alias="issueTypeHierarchy", description="Defines the issue type hierarhy to be created and used during this project creation. This will only add new levels if there isn't an existing level")
    issue_type_scheme: CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeScheme | None = Field(None, validation_alias="issueTypeScheme", serialization_alias="issueTypeScheme", description="The payload for creating issue type schemes")
    issue_types: list[IssueTypePayload] | None = Field(None, validation_alias="issueTypes", serialization_alias="issueTypes", description="Only needed if you want to create issue types, you can otherwise use the ids of issue types in the scheme configuration")

class PermissionGrantDto(StrictModel):
    """List of permission grants"""
    application_access: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="applicationAccess", serialization_alias="applicationAccess")
    group_custom_fields: Annotated[list[ProjectCreateResourceIdentifier], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="groupCustomFields", serialization_alias="groupCustomFields")
    groups: Annotated[list[ProjectCreateResourceIdentifier], AfterValidator(_check_unique_items)] | None = None
    permission_keys: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="permissionKeys", serialization_alias="permissionKeys")
    project_roles: Annotated[list[ProjectCreateResourceIdentifier], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="projectRoles", serialization_alias="projectRoles")
    special_grants: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="specialGrants", serialization_alias="specialGrants")
    user_custom_fields: Annotated[list[ProjectCreateResourceIdentifier], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="userCustomFields", serialization_alias="userCustomFields")
    users: Annotated[list[ProjectCreateResourceIdentifier], AfterValidator(_check_unique_items)] | None = None

class CreateProjectWithCustomTemplateBodyTemplatePermissionScheme(StrictModel):
    """The payload to create a permission scheme"""
    add_addon_role: bool | None = Field(None, validation_alias="addAddonRole", serialization_alias="addAddonRole", description="Configuration to generate addon role. Default is false if null. Only applies to GLOBAL-scoped permission scheme")
    description: str | None = Field(None, description="The description of the permission scheme")
    grants: Annotated[list[PermissionGrantDto], AfterValidator(_check_unique_items)] | None = Field(None, description="List of permission grants")
    name: str | None = Field(None, description="The name of the permission scheme")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field('FAIL', validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use when there is a conflict with an existing permission scheme. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters; NEW - If the entity exist, try and create a new one with a different name")
    pcri: CreateProjectWithCustomTemplateBodyTemplatePermissionSchemePcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")

class ProjectInsight(StrictModel):
    """Additional details about a project."""
    last_issue_update_time: str | None = Field(None, validation_alias="lastIssueUpdateTime", serialization_alias="lastIssueUpdateTime", description="The last issue update time.", json_schema_extra={'format': 'date-time'})
    total_issue_count: int | None = Field(None, validation_alias="totalIssueCount", serialization_alias="totalIssueCount", description="Total issue count.", json_schema_extra={'format': 'int64'})

class ProjectLandingPageInfo(StrictModel):
    attributes: dict[str, str] | None = None
    board_id: int | None = Field(None, validation_alias="boardId", serialization_alias="boardId", json_schema_extra={'format': 'int64'})
    board_name: str | None = Field(None, validation_alias="boardName", serialization_alias="boardName")
    project_key: str | None = Field(None, validation_alias="projectKey", serialization_alias="projectKey")
    project_type: str | None = Field(None, validation_alias="projectType", serialization_alias="projectType")
    queue_category: str | None = Field(None, validation_alias="queueCategory", serialization_alias="queueCategory")
    queue_id: int | None = Field(None, validation_alias="queueId", serialization_alias="queueId", json_schema_extra={'format': 'int64'})
    queue_name: str | None = Field(None, validation_alias="queueName", serialization_alias="queueName")
    simple_board: bool | None = Field(None, validation_alias="simpleBoard", serialization_alias="simpleBoard")
    simplified: bool | None = None
    url: str | None = None

class ProjectPermissions(StrictModel):
    """Permissions which a user has on a project."""
    can_edit: bool | None = Field(None, validation_alias="canEdit", serialization_alias="canEdit", description="Whether the logged user can edit the project.")

class ProjectRoleGroup(StrictModel):
    """Details of the group associated with the role."""
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the group.")
    group_id: str | None = Field(None, validation_alias="groupId", serialization_alias="groupId", description="The ID of the group.")
    name: str | None = Field(None, description="The name of the group. As a group's name can change, use of `groupId` is recommended to identify the group.")

class ProjectRoleUser(StrictModel):
    """Details of the user associated with the role."""
    account_id: str | None = Field(None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Returns *unknown* if the record is deleted and corrupted, for example, as the result of a server import.", max_length=128)

class PublishedWorkflowId(StrictModel):
    """Properties that identify a published workflow."""
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId", description="The entity ID of the workflow.")
    name: str = Field(..., description="The name of the workflow.")

class QuickFilterPayload(StrictModel):
    """The payload for defining quick filters"""
    description: str | None = Field(None, description="The description of the quick filter")
    jql_query: str | None = Field(None, validation_alias="jqlQuery", serialization_alias="jqlQuery", description="The jql query for the quick filter")
    name: str | None = Field(None, description="The name of the quick filter")

class RedactionPosition(StrictModel):
    """Represents the position of the redaction"""
    adf_pointer: str | None = Field(None, validation_alias="adfPointer", serialization_alias="adfPointer", description="The ADF pointer indicating the position of the text to be redacted. This is only required when redacting from rich text(ADF) fields. For plain text fields, this field can be omitted.")
    expected_text: str = Field(..., validation_alias="expectedText", serialization_alias="expectedText", description="The text which will be redacted, encoded using SHA256 hash and Base64 digest")
    from_: int = Field(..., validation_alias="from", serialization_alias="from", description="The start index(inclusive) for the redaction in specified content", json_schema_extra={'format': 'int32'})
    to: int = Field(..., description="The ending index(exclusive) for the redaction in specified content", json_schema_extra={'format': 'int32'})

class ResourceModel(StrictModel):
    content_as_byte_array: list[str] | None = Field(None, validation_alias="contentAsByteArray", serialization_alias="contentAsByteArray")
    description: str | None = None
    file_: str | None = Field(None, validation_alias="file", serialization_alias="file", json_schema_extra={'format': 'binary'})
    filename: str | None = None
    input_stream: dict[str, Any] | None = Field(None, validation_alias="inputStream", serialization_alias="inputStream")
    open_: bool | None = Field(None, validation_alias="open", serialization_alias="open")
    readable: bool | None = None
    uri: str | None = Field(None, json_schema_extra={'format': 'uri'})
    url: str | None = Field(None, json_schema_extra={'format': 'url'})

class MultipartFile(StrictModel):
    bytes_: list[str] | None = Field(None, validation_alias="bytes", serialization_alias="bytes")
    content_type: str | None = Field(None, validation_alias="contentType", serialization_alias="contentType")
    empty: bool | None = None
    input_stream: dict[str, Any] | None = Field(None, validation_alias="inputStream", serialization_alias="inputStream")
    name: str | None = None
    original_filename: str | None = Field(None, validation_alias="originalFilename", serialization_alias="originalFilename")
    resource: ResourceModel | None = None
    size: int | None = Field(None, json_schema_extra={'format': 'int64'})

class RestrictedPermission(PermissiveModel):
    """Details of the permission."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the permission. Either `id` or `key` must be specified. Use [Get all permissions](#api-rest-api-3-permissions-get) to get the list of permissions.")
    key: str | None = Field(None, description="The key of the permission. Either `id` or `key` must be specified. Use [Get all permissions](#api-rest-api-3-permissions-get) to get the list of permissions.")

class NotifyBodyRestrict(StrictModel):
    """Restricts the notifications to users with the specified permissions."""
    group_ids: list[str] | None = Field(None, validation_alias="groupIds", serialization_alias="groupIds", description="List of groupId memberships required to receive the notification.")
    groups: list[GroupName] | None = Field(None, description="List of group memberships required to receive the notification.")
    permissions: list[RestrictedPermission] | None = Field(None, description="List of permissions required to receive the notification.")

class RoleActor(StrictModel):
    """Details about a user assigned to a project role."""
    actor_group: ProjectRoleGroup | None = Field(None, validation_alias="actorGroup", serialization_alias="actorGroup")
    actor_user: ProjectRoleUser | None = Field(None, validation_alias="actorUser", serialization_alias="actorUser")
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl", description="The avatar of the role actor.", json_schema_extra={'format': 'uri'})
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the role actor. For users, depending on the user’s privacy setting, this may return an alternative value for the user's name.")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the role actor.", json_schema_extra={'format': 'int64'})
    name: str | None = Field(None, description="This property is no longer available and will be removed from the documentation soon. See the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.")
    type_: Literal["atlassian-group-role-actor", "atlassian-user-role-actor"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of role actor.")

class RolePayload(StrictModel):
    """The payload used to create a project role. It is optional for CMP projects, as a default role actor will be provided. TMP will add new role actors to the table."""
    default_actors: list[ProjectCreateResourceIdentifier] | None = Field(None, validation_alias="defaultActors", serialization_alias="defaultActors", description="The default actors for the role. By adding default actors, the role will be added to any future projects created")
    description: str | None = Field(None, description="The description of the role")
    name: str | None = Field(None, description="The name of the role")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field('USE', validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use when there is a conflict with an existing project role. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters")
    pcri: ProjectCreateResourceIdentifier | None = None
    type_: Literal["HIDDEN", "VIEWABLE", "EDITABLE", "GUEST"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the role. Only used by project-scoped project")

class CreateProjectWithCustomTemplateBodyTemplateRole(StrictModel):
    role_to_project_actors: dict[str, list[ProjectCreateResourceIdentifier]] | None = Field(None, validation_alias="roleToProjectActors", serialization_alias="roleToProjectActors", description="A map of role PCRI (can be ID or REF) to a list of user or group PCRI IDs to associate with the role and project.")
    roles: list[RolePayload] | None = Field(None, description="The list of roles to create.")

class RulePayload(StrictModel):
    """The payload for creating rules in a workflow"""
    parameters: dict[str, str] | None = Field(None, description="The parameters of the rule")
    rule_key: str | None = Field(None, validation_alias="ruleKey", serialization_alias="ruleKey", description="The key of the rule. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/\\#api-rest-api-3-workflows-capabilities-get")

class ScreenSchemePayload(StrictModel):
    """Defines the payload for the screen schemes. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/\\#api-rest-api-3-screenscheme-post"""
    default_screen: ProjectCreateResourceIdentifier | None = Field(None, validation_alias="defaultScreen", serialization_alias="defaultScreen")
    description: str | None = Field(None, description="The description of the screen scheme")
    name: str | None = Field(None, description="The name of the screen scheme")
    pcri: ProjectCreateResourceIdentifier | None = None
    screens: dict[str, ProjectCreateResourceIdentifier] | None = Field(None, description="Similar to the field layout scheme those mappings allow users to set different screens for different operations: default - always there, applied to all operations that don't have an explicit mapping `create`, `view`, `edit` - specific operations that are available and users can assign a different screen for each one of them https://support.atlassian.com/jira-cloud-administration/docs/manage-screen-schemes/\\#Associating-a-screen-with-an-issue-operation")

class SecurityLevelMemberPayload(StrictModel):
    """The payload for creating a security level member. See https://support.atlassian.com/jira-cloud-administration/docs/configure-issue-security-schemes/"""
    parameter: str | None = Field(None, description="Defines the value associated with the type. For reporter this would be \\{\"null\"\\}; for users this would be the names of specific users); for group this would be group names like \\{\"administrators\", \"jira-administrators\", \"jira-users\"\\}")
    type_: Literal["group", "reporter", "users"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the security level member")

class SecurityLevelPayload(StrictModel):
    """The payload for creating a security level. See https://support.atlassian.com/jira-cloud-administration/docs/configure-issue-security-schemes/"""
    description: str | None = Field(None, description="The description of the security level")
    is_default: Literal[True, False] | None = Field(None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether the security level is default for the security scheme")
    name: str | None = Field(None, description="The name of the security level")
    security_level_members: list[SecurityLevelMemberPayload] | None = Field(None, validation_alias="securityLevelMembers", serialization_alias="securityLevelMembers", description="The members of the security level")

class CreateProjectWithCustomTemplateBodyTemplateSecurity(StrictModel):
    """The payload for creating a security scheme. See https://support.atlassian.com/jira-cloud-administration/docs/configure-issue-security-schemes/"""
    description: str | None = Field(None, description="The description of the security scheme")
    name: str | None = Field(None, description="The name of the security scheme")
    pcri: CreateProjectWithCustomTemplateBodyTemplateSecurityPcri | None = Field(None, description="Every project-created entity has an ID that must be unique within the scope of the project creation. PCRI (Project Create Resource Identifier) is a standard format for creating IDs and references to other project entities. PCRI format is defined as follows: pcri:\\[entityType\\]:\\[type\\]:\\[entityId\\] entityType - the type of an entity, e.g. status, role, workflow type - PCRI type, either `id` - The ID of an entity that already exists in the target site, or `ref` - A unique reference to an entity that is being created entityId - entity identifier, if type is `id` - must be an existing entity ID that exists in the Jira site, if `ref` - must be unique across all entities in the scope of this project template creation")
    security_levels: list[SecurityLevelPayload] | None = Field(None, validation_alias="securityLevels", serialization_alias="securityLevels", description="The security levels for the security scheme")

class SimpleLink(StrictModel):
    """Details about the operations available in this version."""
    href: str | None = None
    icon_class: str | None = Field(None, validation_alias="iconClass", serialization_alias="iconClass")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    label: str | None = None
    style_class: str | None = Field(None, validation_alias="styleClass", serialization_alias="styleClass")
    title: str | None = None
    weight: int | None = Field(None, json_schema_extra={'format': 'int32'})

class SimpleListWrapperApplicationRole(StrictModel):
    callback: ListWrapperCallbackApplicationRole | None = None
    items: list[ApplicationRole] | None = None
    max_results: int | None = Field(None, validation_alias="max-results", serialization_alias="max-results", json_schema_extra={'format': 'int32'})
    paging_callback: ListWrapperCallbackApplicationRole | None = Field(None, validation_alias="pagingCallback", serialization_alias="pagingCallback")
    size: int | None = Field(None, json_schema_extra={'format': 'int32'})

class SimpleListWrapperGroupName(StrictModel):
    callback: ListWrapperCallbackGroupName | None = None
    items: list[GroupName] | None = None
    max_results: int | None = Field(None, validation_alias="max-results", serialization_alias="max-results", json_schema_extra={'format': 'int32'})
    paging_callback: ListWrapperCallbackGroupName | None = Field(None, validation_alias="pagingCallback", serialization_alias="pagingCallback")
    size: int | None = Field(None, json_schema_extra={'format': 'int32'})

class SimplifiedHierarchyLevel(StrictModel):
    above_level_id: int | None = Field(None, validation_alias="aboveLevelId", serialization_alias="aboveLevelId", description="The ID of the level above this one in the hierarchy. This property is deprecated, see [Change notice: Removing hierarchy level IDs from next-gen APIs](https://developer.atlassian.com/cloud/jira/platform/change-notice-removing-hierarchy-level-ids-from-next-gen-apis/).", json_schema_extra={'format': 'int64'})
    below_level_id: int | None = Field(None, validation_alias="belowLevelId", serialization_alias="belowLevelId", description="The ID of the level below this one in the hierarchy. This property is deprecated, see [Change notice: Removing hierarchy level IDs from next-gen APIs](https://developer.atlassian.com/cloud/jira/platform/change-notice-removing-hierarchy-level-ids-from-next-gen-apis/).", json_schema_extra={'format': 'int64'})
    external_uuid: str | None = Field(None, validation_alias="externalUuid", serialization_alias="externalUuid", description="The external UUID of the hierarchy level. This property is deprecated, see [Change notice: Removing hierarchy level IDs from next-gen APIs](https://developer.atlassian.com/cloud/jira/platform/change-notice-removing-hierarchy-level-ids-from-next-gen-apis/).", json_schema_extra={'format': 'uuid'})
    hierarchy_level_number: int | None = Field(None, validation_alias="hierarchyLevelNumber", serialization_alias="hierarchyLevelNumber", json_schema_extra={'format': 'int32'})
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the hierarchy level. This property is deprecated, see [Change notice: Removing hierarchy level IDs from next-gen APIs](https://developer.atlassian.com/cloud/jira/platform/change-notice-removing-hierarchy-level-ids-from-next-gen-apis/).", json_schema_extra={'format': 'int64'})
    issue_type_ids: list[int] | None = Field(None, validation_alias="issueTypeIds", serialization_alias="issueTypeIds", description="The issue types available in this hierarchy level.")
    level: int | None = Field(None, description="The level of this item in the hierarchy.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(None, description="The name of this hierarchy level.")
    project_configuration_id: int | None = Field(None, validation_alias="projectConfigurationId", serialization_alias="projectConfigurationId", description="The ID of the project configuration. This property is deprecated, see [Change oticen: Removing hierarchy level IDs from next-gen APIs](https://developer.atlassian.com/cloud/jira/platform/change-notice-removing-hierarchy-level-ids-from-next-gen-apis/).", json_schema_extra={'format': 'int64'})

class Hierarchy(StrictModel):
    """The project issue type hierarchy."""
    base_level_id: int | None = Field(None, validation_alias="baseLevelId", serialization_alias="baseLevelId", description="The ID of the base level. This property is deprecated, see [Change notice: Removing hierarchy level IDs from next-gen APIs](https://developer.atlassian.com/cloud/jira/platform/change-notice-removing-hierarchy-level-ids-from-next-gen-apis/).", json_schema_extra={'format': 'int64'})
    levels: list[SimplifiedHierarchyLevel] | None = Field(None, description="Details about the hierarchy level.")

class SingleRedactionRequest(StrictModel):
    content_item: ContentItem = Field(..., validation_alias="contentItem", serialization_alias="contentItem")
    external_id: str = Field(..., validation_alias="externalId", serialization_alias="externalId", description="Unique id for the redaction request; ID format should be of UUID", json_schema_extra={'format': 'uuid'})
    reason: str = Field(..., description="The reason why the content is being redacted")
    redaction_position: RedactionPosition = Field(..., validation_alias="redactionPosition", serialization_alias="redactionPosition")

class Status(PermissiveModel):
    """The status of the item."""
    icon: Icon | None = Field(None, description="Details of the icon representing the status. If not provided, no status icon displays in Jira.")
    resolved: bool | None = Field(None, description="Whether the item is resolved. If set to \"true\", the link to the issue is displayed in a strikethrough font, otherwise the link displays in normal font.")

class StatusCategory(PermissiveModel):
    """A status category."""
    color_name: str | None = Field(None, validation_alias="colorName", serialization_alias="colorName", description="The name of the color used to represent the status category.")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the status category.", json_schema_extra={'format': 'int64'})
    key: str | None = Field(None, description="The key of the status category.")
    name: str | None = Field(None, description="The name of the status category.")
    self: str | None = Field(None, description="The URL of the status category.")

class StatusPayload(StrictModel):
    """The payload for creating a status"""
    description: str | None = Field(None, description="The description of the status")
    name: str | None = Field(None, description="The name of the status")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field(None, validation_alias="onConflict", serialization_alias="onConflict", description="The conflict strategy for the status already exists. FAIL - Fail execution, this always needs to be unique; USE - Use the existing entity and ignore new entity parameters; NEW - Create a new entity")
    pcri: ProjectCreateResourceIdentifier | None = None
    status_category: Literal["TODO", "IN_PROGRESS", "DONE"] | None = Field(None, validation_alias="statusCategory", serialization_alias="statusCategory", description="The status category of the status. The value is case-sensitive.")

class SubmitBulkEditBodyEditedFieldsInputIssueType(StrictModel):
    """Set the issue type field by providing an `issueTypeId`."""
    issue_type_id: str = Field(..., validation_alias="issueTypeId", serialization_alias="issueTypeId")

class SubmitBulkEditBodyEditedFieldsInputMultiselectComponents(StrictModel):
    """Edit a multi select components field:

 *  Options include `ADD`, `REPLACE`, `REMOVE`, or `REMOVE_ALL` for bulk edits.
 *  To clear, use the `REMOVE_ALL` option with an empty `components` array."""
    bulk_edit_multi_select_field_option: Literal["ADD", "REMOVE", "REPLACE", "REMOVE_ALL"] = Field(..., validation_alias="bulkEditMultiSelectFieldOption", serialization_alias="bulkEditMultiSelectFieldOption")
    components: list[JiraComponentField]
    field_id: str = Field(..., validation_alias="fieldId", serialization_alias="fieldId")

class SubmitBulkEditBodyEditedFieldsInputOriginalEstimateField(StrictModel):
    """Edit the original estimate field."""
    original_estimate_field: str = Field(..., validation_alias="originalEstimateField", serialization_alias="originalEstimateField")

class SubmitBulkEditBodyEditedFieldsInputPriority(StrictModel):
    """Set the priority of an issue by specifying a `priorityId`."""
    priority_id: str = Field(..., validation_alias="priorityId", serialization_alias="priorityId")

class SubmitBulkEditBodyEditedFieldsInputStatus(StrictModel):
    status_id: str = Field(..., validation_alias="statusId", serialization_alias="statusId")

class SubmitBulkEditBodyEditedFieldsInputTimeTrackingField(StrictModel):
    """Edit the time tracking field."""
    time_remaining: str = Field(..., validation_alias="timeRemaining", serialization_alias="timeRemaining")

class SubmitBulkEditBodyEditedFieldsInput(StrictModel):
    """An object that defines the values to be updated in specified fields of an issue. The structure and content of this parameter vary depending on the type of field being edited. Although the order is not significant, ensure that field IDs align with those in selectedActions."""
    cascading_select_fields: list[JiraCascadingSelectField] | None = Field(None, validation_alias="cascadingSelectFields", serialization_alias="cascadingSelectFields", description="Add or clear a cascading select field:\n\n *  To add, specify `optionId` for both parent and child.\n *  To clear the child, set its `optionId` to null.\n *  To clear both, set the parent's `optionId` to null.")
    clearable_number_fields: list[JiraNumberField] | None = Field(None, validation_alias="clearableNumberFields", serialization_alias="clearableNumberFields", description="Add or clear a number field:\n\n *  To add, specify a numeric `value`.\n *  To clear, set `value` to `null`.")
    color_fields: list[JiraColorField] | None = Field(None, validation_alias="colorFields", serialization_alias="colorFields", description="Add or clear a color field:\n\n *  To add, specify the color `name`. Available colors are: `purple`, `blue`, `green`, `teal`, `yellow`, `orange`, `grey`, `dark purple`, `dark blue`, `dark green`, `dark teal`, `dark yellow`, `dark orange`, `dark grey`.\n *  To clear, set the color `name` to an empty string.")
    date_picker_fields: list[JiraDateField] | None = Field(None, validation_alias="datePickerFields", serialization_alias="datePickerFields", description="Add or clear a date picker field:\n\n *  To add, specify the date in `d/mmm/yy` format or ISO format `dd-mm-yyyy`.\n *  To clear, set `formattedDate` to an empty string.")
    date_time_picker_fields: list[JiraDateTimeField] | None = Field(None, validation_alias="dateTimePickerFields", serialization_alias="dateTimePickerFields", description="Add or clear the planned start date and time:\n\n *  To add, specify the date and time in ISO format for `formattedDateTime`.\n *  To clear, provide an empty string for `formattedDateTime`.")
    issue_type: SubmitBulkEditBodyEditedFieldsInputIssueType | None = Field(None, validation_alias="issueType", serialization_alias="issueType", description="Set the issue type field by providing an `issueTypeId`.")
    labels_fields: list[JiraLabelsField] | None = Field(None, validation_alias="labelsFields", serialization_alias="labelsFields", description="Edit a labels field:\n\n *  Options include `ADD`, `REPLACE`, `REMOVE`, or `REMOVE_ALL` for bulk edits.\n *  To clear labels, use the `REMOVE_ALL` option with an empty `labels` array.")
    multiple_group_picker_fields: list[JiraMultipleGroupPickerField] | None = Field(None, validation_alias="multipleGroupPickerFields", serialization_alias="multipleGroupPickerFields", description="Add or clear a multi-group picker field:\n\n *  To add groups, provide an array of groups with `groupName`s.\n *  To clear all groups, use an empty `groups` array.")
    multiple_select_clearable_user_picker_fields: list[JiraMultipleSelectUserPickerField] | None = Field(None, validation_alias="multipleSelectClearableUserPickerFields", serialization_alias="multipleSelectClearableUserPickerFields", description="Assign or unassign multiple users to/from a field:\n\n *  To assign, provide an array of user `accountId`s.\n *  To clear, set `users` to `null`.")
    multiple_select_fields: list[JiraMultipleSelectField] | None = Field(None, validation_alias="multipleSelectFields", serialization_alias="multipleSelectFields", description="Add or clear a multi-select field:\n\n *  To add, provide an array of options with `optionId`s.\n *  To clear, use an empty `options` array.")
    multiple_version_picker_fields: list[JiraMultipleVersionPickerField] | None = Field(None, validation_alias="multipleVersionPickerFields", serialization_alias="multipleVersionPickerFields", description="Edit a multi-version picker field like Fix Versions/Affects Versions:\n\n *  Options include `ADD`, `REPLACE`, `REMOVE`, or `REMOVE_ALL` for bulk edits.\n *  To clear the field, use the `REMOVE_ALL` option with an empty `versions` array.")
    multiselect_components: SubmitBulkEditBodyEditedFieldsInputMultiselectComponents | None = Field(None, validation_alias="multiselectComponents", serialization_alias="multiselectComponents", description="Edit a multi select components field:\n\n *  Options include `ADD`, `REPLACE`, `REMOVE`, or `REMOVE_ALL` for bulk edits.\n *  To clear, use the `REMOVE_ALL` option with an empty `components` array.")
    original_estimate_field: SubmitBulkEditBodyEditedFieldsInputOriginalEstimateField | None = Field(None, validation_alias="originalEstimateField", serialization_alias="originalEstimateField", description="Edit the original estimate field.")
    priority: SubmitBulkEditBodyEditedFieldsInputPriority | None = Field(None, description="Set the priority of an issue by specifying a `priorityId`.")
    rich_text_fields: list[JiraRichTextField] | None = Field(None, validation_alias="richTextFields", serialization_alias="richTextFields", description="Add or clear a rich text field:\n\n *  To add, provide `adfValue`. Note that rich text fields only support ADF values.\n *  To clear, use an empty `richText` object.\n\nFor ADF format details, refer to: [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure).")
    single_group_picker_fields: list[JiraSingleGroupPickerField] | None = Field(None, validation_alias="singleGroupPickerFields", serialization_alias="singleGroupPickerFields", description="Add or clear a single group picker field:\n\n *  To add, specify the group with `groupName`.\n *  To clear, set `groupName` to an empty string.")
    single_line_text_fields: list[JiraSingleLineTextField] | None = Field(None, validation_alias="singleLineTextFields", serialization_alias="singleLineTextFields", description="Add or clear a single line text field:\n\n *  To add, provide the `text` value.\n *  To clear, set `text` to an empty string.")
    single_select_clearable_user_picker_fields: list[JiraSingleSelectUserPickerField] | None = Field(None, validation_alias="singleSelectClearableUserPickerFields", serialization_alias="singleSelectClearableUserPickerFields", description="Edit assignment for single select user picker fields like Assignee/Reporter:\n\n *  To assign an issue, specify the user's `accountId`.\n *  To unassign an issue, set `user` to `null`.\n *  For automatic assignment, set `accountId` to `-1`.")
    single_select_fields: list[JiraSingleSelectField] | None = Field(None, validation_alias="singleSelectFields", serialization_alias="singleSelectFields", description="Add or clear a single select field:\n\n *  To add, specify the option with an `optionId`.\n *  To clear, pass an option with `optionId` as `-1`.")
    single_version_picker_fields: list[JiraSingleVersionPickerField] | None = Field(None, validation_alias="singleVersionPickerFields", serialization_alias="singleVersionPickerFields", description="Add or clear a single version picker field:\n\n *  To add, specify the version with a `versionId`.\n *  To clear, set `versionId` to `-1`.")
    status: SubmitBulkEditBodyEditedFieldsInputStatus | None = None
    time_tracking_field: SubmitBulkEditBodyEditedFieldsInputTimeTrackingField | None = Field(None, validation_alias="timeTrackingField", serialization_alias="timeTrackingField", description="Edit the time tracking field.")
    url_fields: list[JiraUrlField] | None = Field(None, validation_alias="urlFields", serialization_alias="urlFields", description="Add or clear a URL field:\n\n *  To add, provide the `url` with the desired URL value.\n *  To clear, set `url` to an empty string.")

class SwimlanePayload(StrictModel):
    """The payload for custom swimlanes"""
    description: str | None = Field(None, description="The description of the quick filter")
    jql_query: str | None = Field(None, validation_alias="jqlQuery", serialization_alias="jqlQuery", description="The jql query for the quick filter")
    name: str | None = Field(None, description="The name of the quick filter")

class SwimlanesPayload(StrictModel):
    """The payload for customising a swimlanes on a board"""
    custom_swimlanes: list[SwimlanePayload] | None = Field(None, validation_alias="customSwimlanes", serialization_alias="customSwimlanes", description="The custom swimlane definitions.")
    default_custom_swimlane_name: str | None = Field(None, validation_alias="defaultCustomSwimlaneName", serialization_alias="defaultCustomSwimlaneName", description="The name of the custom swimlane to use for work items that don't match any other swimlanes.")
    swimlane_strategy: Literal["none", "custom", "parentChild", "assignee", "assigneeUnassignedFirst", "epic", "project", "issueparent", "issuechildren", "request_type"] | None = Field(None, validation_alias="swimlaneStrategy", serialization_alias="swimlaneStrategy", description="The swimlane strategy for the board.")

class TabPayload(StrictModel):
    """Defines the payload for the tabs of the screen. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/\\#api-rest-api-3-screens-screenid-tabs-tabid-fields-post"""
    fields: list[ProjectCreateResourceIdentifier] | None = Field(None, description="The list of resource identifier of the field associated to the tab. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/\\#api-rest-api-3-screens-screenid-tabs-tabid-fields-post")
    name: str | None = Field(None, description="The name of the tab")

class ScreenPayload(StrictModel):
    """Defines the payload for the field screens. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/\\#api-rest-api-3-screens-post"""
    description: str | None = Field(None, description="The description of the screen")
    name: str | None = Field(None, description="The name of the screen")
    pcri: ProjectCreateResourceIdentifier | None = None
    tabs: list[TabPayload] | None = Field(None, description="The tabs of the screen. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/\\#api-rest-api-3-screens-screenid-tabs-tabid-fields-post")

class CreateProjectWithCustomTemplateBodyTemplateField(StrictModel):
    """Defines the payload for the fields, screens, screen schemes, issue type screen schemes, field layouts, and field layout schemes"""
    custom_field_definitions: list[CustomFieldPayload] | None = Field(None, validation_alias="customFieldDefinitions", serialization_alias="customFieldDefinitions", description="The custom field definitions. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/\\#api-rest-api-3-field-post")
    field_layout_scheme: CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutScheme | None = Field(None, validation_alias="fieldLayoutScheme", serialization_alias="fieldLayoutScheme", description="Deprecated use [fieldAssociationScheme](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-field-schemes/#api-group-field-schemes) instead Defines the payload for the field layout schemes. See [ Field configuration scheme](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfigurationscheme-post).\n\n[ How to configure a field configuration scheme](https://support.atlassian.com/jira-cloud-administration/docs/configure-a-field-configuration-scheme/).")
    field_layouts: list[FieldLayoutPayload] | None = Field(None, validation_alias="fieldLayouts", serialization_alias="fieldLayouts", description="The field layouts configuration.")
    field_scheme: CreateProjectWithCustomTemplateBodyTemplateFieldFieldScheme | None = Field(None, validation_alias="fieldScheme", serialization_alias="fieldScheme", description="Defines the payload to configure the field scheme for a project. See [Field schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-field-schemes/#api-group-field-schemes).")
    issue_layouts: list[IssueLayoutPayload] | None = Field(None, validation_alias="issueLayouts", serialization_alias="issueLayouts", description="The issue layouts configuration")
    issue_type_screen_scheme: CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenScheme | None = Field(None, validation_alias="issueTypeScreenScheme", serialization_alias="issueTypeScreenScheme", description="Defines the payload for the issue type screen schemes. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/\\#api-rest-api-3-issuetypescreenscheme-post")
    screen_scheme: list[ScreenSchemePayload] | None = Field(None, validation_alias="screenScheme", serialization_alias="screenScheme", description="The screen schemes See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/\\#api-rest-api-3-screenscheme-post")
    screens: list[ScreenPayload] | None = Field(None, description="The screens. See https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/\\#api-rest-api-3-screens-post")

class TargetClassification(StrictModel):
    """Classification mapping for classifications in source issues to respective target classification."""
    classifications: dict[str, list[str]] = Field(..., description="An object with the key as the ID of the target classification and value with the list of the IDs of the current source classifications.")
    issue_type: str | None = Field(None, validation_alias="issueType", serialization_alias="issueType", description="ID of the source issueType to which issues present in `issueIdOrKeys` belongs.")
    project_key_or_id: str | None = Field(None, validation_alias="projectKeyOrId", serialization_alias="projectKeyOrId", description="ID or key of the source project to which issues present in `issueIdOrKeys` belongs.")

class TargetMandatoryFields(StrictModel):
    """Field mapping for mandatory fields in target"""
    fields: dict[str, Any] = Field(..., description="Contains the value of mandatory fields")

class TargetMandatoryFieldsFieldsValue(StrictModel):
    """Can contain multiple field values of following types depending on `type` key"""
    target_mandatory_fields_fields_value: MandatoryFieldValue | MandatoryFieldValueForAdf

class TargetStatus(StrictModel):
    """Status mapping for statuses in source workflow to respective target status in target workflow."""
    statuses: dict[str, list[str]] = Field(..., description="An object with the key as the ID of the target status and value with the list of the IDs of the current source statuses.")

class TargetToSourcesMapping(StrictModel):
    """An object representing the mapping of issues and data related to destination entities, like fields and statuses, that are required during a bulk move."""
    infer_classification_defaults: bool = Field(..., validation_alias="inferClassificationDefaults", serialization_alias="inferClassificationDefaults", description="If `true`, when issues are moved into this target group, they will adopt the target project's default classification, if they don't have a classification already. If they do have a classification, it will be kept the same even after the move. Leave `targetClassification` empty when using this.\n\nIf `false`, you must provide a `targetClassification` mapping for each classification associated with the selected issues.\n\n[Benefit from data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)")
    infer_field_defaults: bool = Field(..., validation_alias="inferFieldDefaults", serialization_alias="inferFieldDefaults", description="If `true`, values from the source issues will be retained for the mandatory fields in the field configuration of the destination project. The `targetMandatoryFields` property shouldn't be defined.\n\nIf `false`, the user is required to set values for mandatory fields present in the field configuration of the destination project. Provide input by defining the `targetMandatoryFields` property")
    infer_status_defaults: bool = Field(..., validation_alias="inferStatusDefaults", serialization_alias="inferStatusDefaults", description="If `true`, the statuses of issues being moved in this target group that are not present in the target workflow will be changed to the default status of the target workflow (see below). Leave `targetStatus` empty when using this.\n\nIf `false`, you must provide a `targetStatus` for each status not present in the target workflow.\n\nThe default status in a workflow is referred to as the \"initial status\". Each workflow has its own unique initial status. When an issue is created, it is automatically assigned to this initial status. Read more about configuring initial statuses: [Configure the initial status | Atlassian Support.](https://support.atlassian.com/jira-cloud-administration/docs/configure-the-initial-status/)")
    infer_subtask_type_default: bool = Field(..., validation_alias="inferSubtaskTypeDefault", serialization_alias="inferSubtaskTypeDefault", description="When an issue is moved, its subtasks (if there are any) need to be moved with it. `inferSubtaskTypeDefault` helps with moving the subtasks by picking a random subtask type in the target project.\n\nIf `true`, subtasks will automatically move to the same project as their parent.\n\nWhen they move:\n\n *  Their `issueType` will be set to the default for subtasks in the target project.\n *  Values for mandatory fields will be retained from the source issues\n *  Specifying separate mapping for implicit subtasks won’t be allowed.\n\nIf `false`, you must manually move the subtasks. They will retain the parent which they had in the current project after being moved.")
    issue_ids_or_keys: list[str] | None = Field(None, validation_alias="issueIdsOrKeys", serialization_alias="issueIdsOrKeys", description="List of issue IDs or keys to be moved.")
    target_classification: list[TargetClassification] | None = Field(None, validation_alias="targetClassification", serialization_alias="targetClassification", description="List of the objects containing classifications in the source issues and their new values which need to be set during the bulk move operation.\n\nIt is mandatory to provide source classification to target classification mapping when the source classification is invalid for the target project and issue type.\n\n *  **You should only define this property when `inferClassificationDefaults` is `false`.**\n *  **In order to provide mapping for issues which don't have a classification, use `\"-1\"`.**")
    target_mandatory_fields: list[TargetMandatoryFields] | None = Field(None, validation_alias="targetMandatoryFields", serialization_alias="targetMandatoryFields", description="List of objects containing mandatory fields in the target field configuration and new values that need to be set during the bulk move operation.\n\nThe new values will only be applied if the field is mandatory in the target project and at least one issue from the source has that field empty, or if the field context is different in the target project (e.g. project-scoped version fields).\n\n**You should only define this property when `inferFieldDefaults` is `false`.**")
    target_status: list[TargetStatus] | None = Field(None, validation_alias="targetStatus", serialization_alias="targetStatus", description="List of the objects containing statuses in the source workflow and their new values which need to be set during the bulk move operation.\n\nThe new values will only be applied if the source status is invalid for the target project and issue type.\n\nIt is mandatory to provide source status to target status mapping when the source status is invalid for the target project and issue type.\n\n**You should only define this property when `inferStatusDefaults` is `false`.**")

class TimeTrackingDetails(StrictModel):
    """Time tracking details."""
    original_estimate: str | None = Field(None, validation_alias="originalEstimate", serialization_alias="originalEstimate", description="The original estimate of time needed for this issue in readable format.")
    original_estimate_seconds: int | None = Field(None, validation_alias="originalEstimateSeconds", serialization_alias="originalEstimateSeconds", description="The original estimate of time needed for this issue in seconds.", json_schema_extra={'format': 'int64'})
    remaining_estimate: str | None = Field(None, validation_alias="remainingEstimate", serialization_alias="remainingEstimate", description="The remaining estimate of time needed for this issue in readable format.")
    remaining_estimate_seconds: int | None = Field(None, validation_alias="remainingEstimateSeconds", serialization_alias="remainingEstimateSeconds", description="The remaining estimate of time needed for this issue in seconds.", json_schema_extra={'format': 'int64'})
    time_spent: str | None = Field(None, validation_alias="timeSpent", serialization_alias="timeSpent", description="Time worked on this issue in readable format.")
    time_spent_seconds: int | None = Field(None, validation_alias="timeSpentSeconds", serialization_alias="timeSpentSeconds", description="Time worked on this issue in seconds.", json_schema_extra={'format': 'int64'})

class ToLayoutPayload(StrictModel):
    """The payload for the layout details for the destination end of a transition"""
    port: int | None = Field(None, description="Defines where the transition line will be connected to a status. Port 0 to 7 are acceptable values.", json_schema_extra={'format': 'int32'})
    status: ProjectCreateResourceIdentifier | None = None

class TransitionScreenDetails(StrictModel):
    """The details of a transition screen."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the screen.")
    name: str | None = Field(None, description="The name of the screen.")

class UpdateCommentBodyVisibility(PermissiveModel):
    """The group or role to which this comment is visible. Optional on create and update."""
    identifier: str | None = Field(None, description="The ID of the group or the name of the role that visibility of this item is restricted to.")
    type_: Literal["group", "role"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Whether visibility of this item is restricted to a group or role.")
    value: str | None = Field(None, description="The name of the group or role that visibility of this item is restricted to. Please note that the name of a group is mutable, to reliably identify a group use `identifier`.")

class UpdateRemoteIssueLinkBodyApplication(PermissiveModel):
    """Details of the remote application the linked item is in. For example, trello."""
    name: str | None = Field(None, description="The name of the application. Used in conjunction with the (remote) object icon title to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank items are excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\". Grouping and sorting of links may place links without an application name last.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The name-spaced type of the application, used by registered rendering apps.")

class UpdateRemoteIssueLinkBodyObjectIcon(PermissiveModel):
    """Details of the icon for the item. If no icon is defined, the default link icon is used in Jira."""
    link: str | None = Field(None, description="The URL of the tooltip, used only for a status icon. If not set, the status icon in Jira is not clickable.")
    title: str | None = Field(None, description="The title of the icon. This is used as follows:\n\n *  For a status icon it is used as a tooltip on the icon. If not set, the status icon doesn't display a tooltip in Jira.\n *  For the remote object icon it is used in conjunction with the application name to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank itemsare excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\".")
    url16x16: str | None = Field(None, description="The URL of an icon that displays at 16x16 pixel in Jira.")

class UpdateRemoteIssueLinkBodyObjectStatusIcon(PermissiveModel):
    """Details of the icon representing the status. If not provided, no status icon displays in Jira."""
    link: str | None = Field(None, description="The URL of the tooltip, used only for a status icon. If not set, the status icon in Jira is not clickable.")
    title: str | None = Field(None, description="The title of the icon. This is used as follows:\n\n *  For a status icon it is used as a tooltip on the icon. If not set, the status icon doesn't display a tooltip in Jira.\n *  For the remote object icon it is used in conjunction with the application name to display a tooltip for the link's icon. The tooltip takes the format \"\\[application name\\] icon title\". Blank itemsare excluded from the tooltip title. If both items are blank, the icon tooltop displays as \"Web Link\".")
    url16x16: str | None = Field(None, description="The URL of an icon that displays at 16x16 pixel in Jira.")

class UpdateRemoteIssueLinkBodyObjectStatus(PermissiveModel):
    """The status of the item."""
    icon: UpdateRemoteIssueLinkBodyObjectStatusIcon | None = Field(None, description="Details of the icon representing the status. If not provided, no status icon displays in Jira.")
    resolved: bool | None = Field(None, description="Whether the item is resolved. If set to \"true\", the link to the issue is displayed in a strikethrough font, otherwise the link displays in normal font.")

class UpdateRemoteIssueLinkBodyObject(PermissiveModel):
    """Details of the item linked to."""
    icon: UpdateRemoteIssueLinkBodyObjectIcon | None = Field(None, description="Details of the icon for the item. If no icon is defined, the default link icon is used in Jira.")
    status: UpdateRemoteIssueLinkBodyObjectStatus | None = Field(None, description="The status of the item.")
    summary: str | None = Field(None, description="The summary details of the item.")
    title: str = Field(..., description="The title of the item.")
    url: str = Field(..., description="The URL of the item.")

class UpdateWorklogBodyVisibility(PermissiveModel):
    """Details about any restrictions in the visibility of the worklog. Optional when creating or updating a worklog."""
    identifier: str | None = Field(None, description="The ID of the group or the name of the role that visibility of this item is restricted to.")
    type_: Literal["group", "role"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Whether visibility of this item is restricted to a group or role.")
    value: str | None = Field(None, description="The name of the group or role that visibility of this item is restricted to. Please note that the name of a group is mutable, to reliably identify a group use `identifier`.")

class UpdatedProjectCategory(StrictModel):
    """A project category."""
    description: str | None = Field(None, description="The name of the project category.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project category.")
    name: str | None = Field(None, description="The description of the project category.")
    self: str | None = Field(None, description="The URL of the project category.")

class ProjectDetails(StrictModel):
    """Details about a project."""
    avatar_urls: AvatarUrlsBean | None = Field(None, validation_alias="avatarUrls", serialization_alias="avatarUrls", description="The URLs of the project's avatars.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project.")
    key: str | None = Field(None, description="The key of the project.")
    name: str | None = Field(None, description="The name of the project.")
    project_category: UpdatedProjectCategory | None = Field(None, validation_alias="projectCategory", serialization_alias="projectCategory", description="The category the project belongs to.")
    project_type_key: Literal["software", "service_desk", "business"] | None = Field(None, validation_alias="projectTypeKey", serialization_alias="projectTypeKey", description="The [project type](https://confluence.atlassian.com/x/GwiiLQ#Jiraapplicationsoverview-Productfeaturesandprojecttypes) of the project.")
    self: str | None = Field(None, description="The URL of the project details.")
    simplified: bool | None = Field(None, description="Whether or not the project is simplified.")

class Scope(PermissiveModel):
    """The projects the item is associated with. Indicated for items associated with [next-gen projects](https://confluence.atlassian.com/x/loMyO)."""
    project: ProjectDetails | None = Field(None, description="The project the item has scope in.")
    type_: Literal["PROJECT", "TEMPLATE"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of scope.")

class IssueTypeDetails(StrictModel):
    """Details about an issue type."""
    avatar_id: int | None = Field(None, validation_alias="avatarId", serialization_alias="avatarId", description="The ID of the issue type's avatar.", json_schema_extra={'format': 'int64'})
    description: str | None = Field(None, description="The description of the issue type.")
    entity_id: str | None = Field(None, validation_alias="entityId", serialization_alias="entityId", description="Unique ID for next-gen projects.", json_schema_extra={'format': 'uuid'})
    hierarchy_level: int | None = Field(None, validation_alias="hierarchyLevel", serialization_alias="hierarchyLevel", description="Hierarchy level of the issue type.", json_schema_extra={'format': 'int32'})
    icon_url: str | None = Field(None, validation_alias="iconUrl", serialization_alias="iconUrl", description="The URL of the issue type's avatar.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the issue type.")
    name: str | None = Field(None, description="The name of the issue type.")
    scope: Scope | None = Field(None, description="Details of the next-gen projects the issue type is available in.")
    self: str | None = Field(None, description="The URL of these issue type details.")
    subtask: bool | None = Field(None, description="Whether this issue type is used to create subtasks.")

class ProjectRole(StrictModel):
    """Details about the roles in a project."""
    actors: list[RoleActor] | None = Field(None, description="The list of users who act in this role.")
    admin: bool | None = Field(None, description="Whether this role is the admin role for the project.")
    current_user_role: bool | None = Field(None, validation_alias="currentUserRole", serialization_alias="currentUserRole", description="Whether the calling user is part of this role.")
    default: bool | None = Field(None, description="Whether this role is the default role for the project")
    description: str | None = Field(None, description="The description of the project role.")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project role.", json_schema_extra={'format': 'int64'})
    name: str | None = Field(None, description="The name of the project role.")
    role_configurable: bool | None = Field(None, validation_alias="roleConfigurable", serialization_alias="roleConfigurable", description="Whether the roles are configurable for this project.")
    scope: Scope | None = Field(None, description="The scope of the role. Indicated for roles associated with [next-gen projects](https://confluence.atlassian.com/x/loMyO).")
    self: str | None = Field(None, description="The URL the project role details.", json_schema_extra={'format': 'uri'})
    translated_name: str | None = Field(None, validation_alias="translatedName", serialization_alias="translatedName", description="The translated name of the project role.")

class StatusDetails(PermissiveModel):
    """A status."""
    description: str | None = Field(None, description="The description of the status.")
    icon_url: str | None = Field(None, validation_alias="iconUrl", serialization_alias="iconUrl", description="The URL of the icon used to represent the status.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the status.")
    name: str | None = Field(None, description="The name of the status.")
    scope: Scope | None = Field(None, description="The scope of the field.")
    self: str | None = Field(None, description="The URL of the status.")
    status_category: StatusCategory | None = Field(None, validation_alias="statusCategory", serialization_alias="statusCategory", description="The category assigned to the status.")

class IssueTransition(PermissiveModel):
    """Details of an issue transition."""
    expand: str | None = Field(None, description="Expand options that include additional transition details in the response.")
    fields: dict[str, FieldMetadata] | None = Field(None, description="Details of the fields associated with the issue transition screen. Use this information to populate `fields` and `update` in a transition request.")
    has_screen: bool | None = Field(None, validation_alias="hasScreen", serialization_alias="hasScreen", description="Whether there is a screen associated with the issue transition.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the issue transition. Required when specifying a transition to undertake.")
    is_available: bool | None = Field(None, validation_alias="isAvailable", serialization_alias="isAvailable", description="Whether the transition is available to be performed.")
    is_conditional: bool | None = Field(None, validation_alias="isConditional", serialization_alias="isConditional", description="Whether the issue has to meet criteria before the issue transition is applied.")
    is_global: bool | None = Field(None, validation_alias="isGlobal", serialization_alias="isGlobal", description="Whether the issue transition is global, that is, the transition is applied to issues regardless of their status.")
    is_initial: bool | None = Field(None, validation_alias="isInitial", serialization_alias="isInitial", description="Whether this is the initial issue transition for the workflow.")
    looped: bool | None = None
    name: str | None = Field(None, description="The name of the issue transition.")
    to: StatusDetails | None = Field(None, description="Details of the issue status after the transition.")

class IssueUpdateDetails(PermissiveModel):
    """Details of an issue update request."""
    fields: dict[str, Any] | None = Field(None, description="List of issue screen fields to update, specifying the sub-field to update and its value for each field. This field provides a straightforward option when setting a sub-field. When multiple sub-fields or other operations are required, use `update`. Fields included in here cannot be included in `update`.")
    history_metadata: HistoryMetadata | None = Field(None, validation_alias="historyMetadata", serialization_alias="historyMetadata", description="Additional issue history details.")
    properties: list[EntityProperty] | None = Field(None, description="Details of issue properties to be add or update.")
    transition: IssueTransition | None = Field(None, description="Details of a transition. Required when performing a transition, optional when creating or editing an issue.")
    update: dict[str, list[FieldUpdateOperation]] | None = Field(None, description="A Map containing the field field name and a list of operations to perform on the issue screen field. Note that fields included in here cannot be included in `fields`.")

class User(StrictModel):
    """A user with details as permitted by the user's Atlassian Account privacy settings. However, be aware of these exceptions:

 *  User record deleted from Atlassian: This occurs as the result of a right to be forgotten request. In this case, `displayName` provides an indication and other parameters have default values or are blank (for example, email is blank).
 *  User record corrupted: This occurs as a results of events such as a server import and can only happen to deleted users. In this case, `accountId` returns *unknown* and all other parameters have fallback values.
 *  User record unavailable: This usually occurs due to an internal service outage. In this case, all parameters have fallback values."""
    account_id: str | None = Field(None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required in requests.", max_length=128)
    account_type: Literal["atlassian", "app", "customer", "unknown"] | None = Field(None, validation_alias="accountType", serialization_alias="accountType", description="The user account type. Can take the following values:\n\n *  `atlassian` regular Atlassian user account\n *  `app` system account used for Connect applications and OAuth to represent external systems\n *  `customer` Jira Service Desk account representing an external service desk")
    active: bool | None = Field(None, description="Whether the user is active.")
    app_type: str | None = Field(None, validation_alias="appType", serialization_alias="appType", description="The app type of the user account when accountType is 'app'. Can take the following values:\n\n *  `service` Service Account\n *  `agent` Rovo Agent Account\n *  `unknown` Unknown app type")
    application_roles: SimpleListWrapperApplicationRole | None = Field(None, validation_alias="applicationRoles", serialization_alias="applicationRoles", description="The application roles the user is assigned to.")
    avatar_urls: AvatarUrlsBean | None = Field(None, validation_alias="avatarUrls", serialization_alias="avatarUrls", description="The avatars of the user.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the user. Depending on the user’s privacy setting, this may return an alternative value.")
    email_address: str | None = Field(None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address of the user. Depending on the user’s privacy setting, this may be returned as null.")
    expand: str | None = Field(None, description="Expand options that include additional user details in the response.")
    groups: SimpleListWrapperGroupName | None = Field(None, description="The groups that the user belongs to.")
    guest: bool | None = Field(None, description="Whether the user is a guest.")
    key: str | None = Field(None, description="This property is no longer available and will be removed from the documentation soon. See the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.")
    locale: str | None = Field(None, description="The locale of the user. Depending on the user’s privacy setting, this may be returned as null.")
    name: str | None = Field(None, description="This property is no longer available and will be removed from the documentation soon. See the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.")
    self: str | None = Field(None, description="The URL of the user.", json_schema_extra={'format': 'uri'})
    time_zone: str | None = Field(None, validation_alias="timeZone", serialization_alias="timeZone", description="The time zone specified in the user's profile. If the user's time zone is not visible to the current user (due to user's profile setting), or if a time zone has not been set, the instance's default time zone will be returned.")

class ProjectComponent(StrictModel):
    """Details about a project component."""
    ari: str | None = Field(None, description="Compass component's ID. Can't be updated. Not required for creating a Project Component.")
    assignee: User | None = Field(None, description="The details of the user associated with `assigneeType`, if any. See `realAssignee` for details of the user assigned to issues created with this component.")
    assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, validation_alias="assigneeType", serialization_alias="assigneeType", description="The nominal user type used to determine the assignee for issues created with this component. See `realAssigneeType` for details on how the type of the user, and hence the user, assigned to issues is determined. Can take the following values:\n\n *  `PROJECT_LEAD` the assignee to any issues created with this component is nominally the lead for the project the component is in.\n *  `COMPONENT_LEAD` the assignee to any issues created with this component is nominally the lead for the component.\n *  `UNASSIGNED` an assignee is not set for issues created with this component.\n *  `PROJECT_DEFAULT` the assignee to any issues created with this component is nominally the default assignee for the project that the component is in.\n\nDefault value: `PROJECT_DEFAULT`.  \nOptional when creating or updating a component.")
    description: str | None = Field(None, description="The description for the component. Optional when creating or updating a component.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier for the component.")
    is_assignee_type_valid: bool | None = Field(None, validation_alias="isAssigneeTypeValid", serialization_alias="isAssigneeTypeValid", description="Whether a user is associated with `assigneeType`. For example, if the `assigneeType` is set to `COMPONENT_LEAD` but the component lead is not set, then `false` is returned.")
    lead: User | None = Field(None, description="The user details for the component's lead user.")
    lead_account_id: str | None = Field(None, validation_alias="leadAccountId", serialization_alias="leadAccountId", description="The accountId of the component's lead user. The accountId uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)
    lead_user_name: str | None = Field(None, validation_alias="leadUserName", serialization_alias="leadUserName", description="This property is no longer available and will be removed from the documentation soon. See the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.")
    metadata: dict[str, str] | None = Field(None, description="Compass component's metadata. Can't be updated. Not required for creating a Project Component.")
    name: str | None = Field(None, description="The unique name for the component in the project. Required when creating a component. Optional when updating a component. The maximum length is 255 characters.")
    project: str | None = Field(None, description="The key of the project the component is assigned to. Required when creating a component. Can't be updated.")
    project_id: int | None = Field(None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project the component is assigned to.", json_schema_extra={'format': 'int64'})
    real_assignee: User | None = Field(None, validation_alias="realAssignee", serialization_alias="realAssignee", description="The user assigned to issues created with this component, when `assigneeType` does not identify a valid assignee.")
    real_assignee_type: Literal["PROJECT_DEFAULT", "COMPONENT_LEAD", "PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, validation_alias="realAssigneeType", serialization_alias="realAssigneeType", description="The type of the assignee that is assigned to issues created with this component, when an assignee cannot be set from the `assigneeType`. For example, `assigneeType` is set to `COMPONENT_LEAD` but no component lead is set. This property is set to one of the following values:\n\n *  `PROJECT_LEAD` when `assigneeType` is `PROJECT_LEAD` and the project lead has permission to be assigned issues in the project that the component is in.\n *  `COMPONENT_LEAD` when `assignee`Type is `COMPONENT_LEAD` and the component lead has permission to be assigned issues in the project that the component is in.\n *  `UNASSIGNED` when `assigneeType` is `UNASSIGNED` and Jira is configured to allow unassigned issues.\n *  `PROJECT_DEFAULT` when none of the preceding cases are true.")
    self: str | None = Field(None, description="The URL of the component.", json_schema_extra={'format': 'uri'})

class UserBeanAvatarUrls(StrictModel):
    n16x16: str | None = Field(None, validation_alias="16x16", serialization_alias="16x16", description="The URL of the user's 16x16 pixel avatar.", json_schema_extra={'format': 'uri'})
    n24x24: str | None = Field(None, validation_alias="24x24", serialization_alias="24x24", description="The URL of the user's 24x24 pixel avatar.", json_schema_extra={'format': 'uri'})
    n32x32: str | None = Field(None, validation_alias="32x32", serialization_alias="32x32", description="The URL of the user's 32x32 pixel avatar.", json_schema_extra={'format': 'uri'})
    n48x48: str | None = Field(None, validation_alias="48x48", serialization_alias="48x48", description="The URL of the user's 48x48 pixel avatar.", json_schema_extra={'format': 'uri'})

class UserBean(StrictModel):
    account_id: str | None = Field(None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)
    active: bool | None = Field(None, description="Whether the user is active.")
    avatar_urls: UserBeanAvatarUrls | None = Field(None, validation_alias="avatarUrls", serialization_alias="avatarUrls", description="The avatars of the user.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the user. Depending on the user’s privacy setting, this may return an alternative value.")
    key: str | None = Field(None, description="This property is deprecated in favor of `accountId` because of privacy changes. See the [migration guide](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.  \nThe key of the user.")
    name: str | None = Field(None, description="This property is deprecated in favor of `accountId` because of privacy changes. See the [migration guide](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.  \nThe username of the user.")
    self: str | None = Field(None, description="The URL of the user.", json_schema_extra={'format': 'uri'})

class UserContextVariable(PermissiveModel):
    """A [user](https://developer.atlassian.com/cloud/jira/platform/jira-expressions-type-reference#user) specified as an Atlassian account ID."""
    account_id: str = Field(..., validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of custom context variable.")

class CustomContextVariable(StrictModel):
    custom_context_variable: UserContextVariable | IssueContextVariable | JsonContextVariable

class EvaluateJsisJiraExpressionBodyContext(StrictModel):
    """The context in which the Jira expression is evaluated."""
    board: int | None = Field(None, description="The ID of the board that is available under the `board` variable when evaluating the expression.", json_schema_extra={'format': 'int64'})
    custom: list[CustomContextVariable] | None = Field(None, description="Custom context variables and their types. These variable types are available for use in a custom context:\n\n *  `user`: A [user](https://developer.atlassian.com/cloud/jira/platform/jira-expressions-type-reference#user) specified as an Atlassian account ID.\n *  `issue`: An [issue](https://developer.atlassian.com/cloud/jira/platform/jira-expressions-type-reference#issue) specified by ID or key. All the fields of the issue object are available in the Jira expression.\n *  `json`: A JSON object containing custom content.\n *  `list`: A JSON list of `user`, `issue`, or `json` variable types.")
    customer_request: int | None = Field(None, validation_alias="customerRequest", serialization_alias="customerRequest", description="The ID of the customer request that is available under the `customerRequest` variable when evaluating the expression. This is the same as the ID of the underlying Jira issue, but the customer request context variable will have a different type.", json_schema_extra={'format': 'int64'})
    issue: EvaluateJsisJiraExpressionBodyContextIssue | None = Field(None, description="The issue that is available under the `issue` variable when evaluating the expression.")
    issues: EvaluateJsisJiraExpressionBodyContextIssues | None = Field(None, description="The collection of issues that is available under the `issues` variable when evaluating the expression.")
    project: EvaluateJsisJiraExpressionBodyContextProject | None = Field(None, description="The project that is available under the `project` variable when evaluating the expression.")
    service_desk: int | None = Field(None, validation_alias="serviceDesk", serialization_alias="serviceDesk", description="The ID of the service desk that is available under the `serviceDesk` variable when evaluating the expression.", json_schema_extra={'format': 'int64'})
    sprint: int | None = Field(None, description="The ID of the sprint that is available under the `sprint` variable when evaluating the expression.", json_schema_extra={'format': 'int64'})

class UserDetails(StrictModel):
    """User details permitted by the user's Atlassian Account privacy settings. However, be aware of these exceptions:

 *  User record deleted from Atlassian: This occurs as the result of a right to be forgotten request. In this case, `displayName` provides an indication and other parameters have default values or are blank (for example, email is blank).
 *  User record corrupted: This occurs as a results of events such as a server import and can only happen to deleted users. In this case, `accountId` returns *unknown* and all other parameters have fallback values.
 *  User record unavailable: This usually occurs due to an internal service outage. In this case, all parameters have fallback values."""
    account_id: str | None = Field(None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user, which uniquely identifies the user across all Atlassian products. For example, *5b10ac8d82e05b22cc7d4ef5*.", max_length=128)
    account_type: str | None = Field(None, validation_alias="accountType", serialization_alias="accountType", description="The type of account represented by this user. This will be one of 'atlassian' (normal users), 'app' (application user) or 'customer' (Jira Service Desk customer user)")
    active: bool | None = Field(None, description="Whether the user is active.")
    avatar_urls: AvatarUrlsBean | None = Field(None, validation_alias="avatarUrls", serialization_alias="avatarUrls", description="The avatars of the user.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the user. Depending on the user’s privacy settings, this may return an alternative value.")
    email_address: str | None = Field(None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address of the user. Depending on the user’s privacy settings, this may be returned as null.")
    key: str | None = Field(None, description="This property is no longer available and will be removed from the documentation soon. See the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.")
    name: str | None = Field(None, description="This property is no longer available and will be removed from the documentation soon. See the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/) for details.")
    self: str | None = Field(None, description="The URL of the user.")
    time_zone: str | None = Field(None, validation_alias="timeZone", serialization_alias="timeZone", description="The time zone specified in the user's profile. Depending on the user’s privacy settings, this may be returned as null.")

class Fields(StrictModel):
    """Key fields from the linked issue."""
    assignee: UserDetails | None = Field(None, description="The assignee of the linked issue.")
    issue_type: IssueTypeDetails | None = Field(None, validation_alias="issueType", serialization_alias="issueType", description="The type of the linked issue.")
    issuetype: IssueTypeDetails | None = Field(None, description="The type of the linked issue.")
    priority: Priority | None = Field(None, description="The priority of the linked issue.")
    status: StatusDetails | None = Field(None, description="The status of the linked issue.")
    summary: str | None = Field(None, description="The summary description of the linked issue.")
    timetracking: TimeTrackingDetails | None = Field(None, description="The time tracking of the linked issue.")

class NotifyBodyTo(PermissiveModel):
    """The recipients of the email notification for the issue."""
    assignee: bool | None = Field(None, description="Whether the notification should be sent to the issue's assignees.")
    group_ids: list[str] | None = Field(None, validation_alias="groupIds", serialization_alias="groupIds", description="List of groupIds to receive the notification.")
    groups: list[GroupName] | None = Field(None, description="List of groups to receive the notification.")
    reporter: bool | None = Field(None, description="Whether the notification should be sent to the issue's reporter.")
    users: list[UserDetails] | None = Field(None, description="List of users to receive the notification.")
    voters: bool | None = Field(None, description="Whether the notification should be sent to the issue's voters.")
    watchers: bool | None = Field(None, description="Whether the notification should be sent to the issue's watchers.")

class PagedListUserDetailsApplicationUser(StrictModel):
    """A paged list. To access additional details append `[start-index:end-index]` to the expand request. For example, `?expand=sharedUsers[10:40]` returns a list starting at item 10 and finishing at item 40."""
    end_index: int | None = Field(None, validation_alias="end-index", serialization_alias="end-index", description="The index of the last item returned on the page.", json_schema_extra={'format': 'int32'})
    items: list[UserDetails] | None = Field(None, description="The list of items.")
    max_results: int | None = Field(None, validation_alias="max-results", serialization_alias="max-results", description="The maximum number of results that could be on the page.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(None, description="The number of items on the page.", json_schema_extra={'format': 'int32'})
    start_index: int | None = Field(None, validation_alias="start-index", serialization_alias="start-index", description="The index of the first item returned on the page.", json_schema_extra={'format': 'int32'})

class Group(StrictModel):
    expand: str | None = Field(None, description="Expand options that include additional group details in the response.")
    group_id: str | None = Field(None, validation_alias="groupId", serialization_alias="groupId", description="The ID of the group, which uniquely identifies the group across all Atlassian products. For example, *952d12c3-5b5b-4d04-bb32-44d383afc4b2*.")
    name: str | None = Field(None, description="The name of group.")
    self: str | None = Field(None, description="The URL for these group details.", json_schema_extra={'format': 'uri'})
    users: PagedListUserDetailsApplicationUser | None = Field(None, description="A paginated list of the users that are members of the group. A maximum of 50 users is returned in the list, to access additional users append `[start-index:end-index]` to the expand request. For example, to access the next 50 users, use`?expand=users[51:100]`.")

class CreatePermissionHolderRequest(StrictModel):
    type_: Literal["Group", "AccountId"] = Field(..., validation_alias="type", serialization_alias="type", description="The permission holder type. This must be \"Group\" or \"AccountId\".")
    value: str = Field(..., description="The permission holder value. This must be a group name if the type is \"Group\" or an account ID if the type is \"AccountId\".")

class CreatePermissionRequest(StrictModel):
    holder: CreatePermissionHolderRequest = Field(..., description="The permission holder.")
    type_: Literal["View", "Edit"] = Field(..., validation_alias="type", serialization_alias="type", description="The permission type. This must be \"View\" or \"Edit\".")

class UserPermission(PermissiveModel):
    """Details of a permission and its availability to a user."""
    deprecated_key: bool | None = Field(None, validation_alias="deprecatedKey", serialization_alias="deprecatedKey", description="Indicate whether the permission key is deprecated. Note that deprecated keys cannot be used in the `permissions parameter of Get my permissions. Deprecated keys are not returned by Get all permissions.`")
    description: str | None = Field(None, description="The description of the permission.")
    have_permission: bool | None = Field(None, validation_alias="havePermission", serialization_alias="havePermission", description="Whether the permission is available to the user in the queried context.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the permission. Either `id` or `key` must be specified. Use [Get all permissions](#api-rest-api-3-permissions-get) to get the list of permissions.")
    key: str | None = Field(None, description="The key of the permission. Either `id` or `key` must be specified. Use [Get all permissions](#api-rest-api-3-permissions-get) to get the list of permissions.")
    name: str | None = Field(None, description="The name of the permission.")
    type_: Literal["GLOBAL", "PROJECT"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the permission.")

class Permissions(StrictModel):
    """Details about permissions."""
    permissions: dict[str, UserPermission] | None = Field(None, description="List of permissions.")

class VersionApprover(PermissiveModel):
    """Contains details about a version approver."""
    account_id: str | None = Field(None, validation_alias="accountId", serialization_alias="accountId", description="The Atlassian account ID of the approver.")
    decline_reason: str | None = Field(None, validation_alias="declineReason", serialization_alias="declineReason", description="A description of why the user is declining the approval.")
    description: str | None = Field(None, description="A description of what the user is approving within the specified version.")
    status: str | None = Field(None, description="The status of the approval, which can be *PENDING*, *APPROVED*, or *DECLINED*")

class VersionIssuesStatus(PermissiveModel):
    """Counts of the number of issues in various statuses."""
    done: int | None = Field(None, description="Count of issues with status *done*.", json_schema_extra={'format': 'int64'})
    in_progress: int | None = Field(None, validation_alias="inProgress", serialization_alias="inProgress", description="Count of issues with status *in progress*.", json_schema_extra={'format': 'int64'})
    to_do: int | None = Field(None, validation_alias="toDo", serialization_alias="toDo", description="Count of issues with status *to do*.", json_schema_extra={'format': 'int64'})
    unmapped: int | None = Field(None, description="Count of issues with a status other than *to do*, *in progress*, and *done*.", json_schema_extra={'format': 'int64'})

class Version(StrictModel):
    """Details about a project version."""
    approvers: list[VersionApprover] | None = Field(None, description="If the expand option `approvers` is used, returns a list containing the approvers for this version.")
    archived: bool | None = Field(None, description="Indicates that the version is archived. Optional when creating or updating a version.")
    description: str | None = Field(None, description="The description of the version. Optional when creating or updating a version. The maximum size is 16,384 bytes.")
    driver: str | None = Field(None, description="The Atlassian account ID of the version driver. Optional when creating or updating a version. If the expand option `driver` is used, returns the Atlassian account ID of the driver.")
    expand: str | None = Field(None, description="Use [expand](em>#expansion) to include additional information about version in the response. This parameter accepts a comma-separated list. Expand options include:\n\n *  `operations` Returns the list of operations available for this version.\n *  `issuesstatus` Returns the count of issues in this version for each of the status categories *to do*, *in progress*, *done*, and *unmapped*. The *unmapped* property contains a count of issues with a status other than *to do*, *in progress*, and *done*.\n *  `driver` Returns the Atlassian account ID of the version driver.\n *  `approvers` Returns a list containing approvers for this version.\n\nOptional for create and update.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the version.")
    issues_status_for_fix_version: VersionIssuesStatus | None = Field(None, validation_alias="issuesStatusForFixVersion", serialization_alias="issuesStatusForFixVersion", description="If the expand option `issuesstatus` is used, returns the count of issues in this version for each of the status categories *to do*, *in progress*, *done*, and *unmapped*. The *unmapped* property contains a count of issues with a status other than *to do*, *in progress*, and *done*.")
    move_unfixed_issues_to: str | None = Field(None, validation_alias="moveUnfixedIssuesTo", serialization_alias="moveUnfixedIssuesTo", description="The URL of the self link to the version to which all unfixed issues are moved when a version is released. Not applicable when creating a version. Optional when updating a version.", json_schema_extra={'format': 'uri'})
    name: str | None = Field(None, description="The unique name of the version. Required when creating a version. Optional when updating a version. The maximum length is 255 characters.")
    operations: list[SimpleLink] | None = Field(None, description="If the expand option `operations` is used, returns the list of operations available for this version.")
    overdue: bool | None = Field(None, description="Indicates that the version is overdue.")
    project: str | None = Field(None, description="Deprecated. Use `projectId`.")
    project_id: int | None = Field(None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project to which this version is attached. Required when creating a version. Not applicable when updating a version.", json_schema_extra={'format': 'int64'})
    release_date: str | None = Field(None, validation_alias="releaseDate", serialization_alias="releaseDate", description="The release date of the version. Expressed in ISO 8601 format (yyyy-mm-dd). Optional when creating or updating a version.", json_schema_extra={'format': 'date'})
    released: bool | None = Field(None, description="Indicates that the version is released. If the version is released a request to release again is ignored. Not applicable when creating a version. Optional when updating a version.")
    self: str | None = Field(None, description="The URL of the version.", json_schema_extra={'format': 'uri'})
    start_date: str | None = Field(None, validation_alias="startDate", serialization_alias="startDate", description="The start date of the version. Expressed in ISO 8601 format (yyyy-mm-dd). Optional when creating or updating a version.", json_schema_extra={'format': 'date'})
    user_release_date: str | None = Field(None, validation_alias="userReleaseDate", serialization_alias="userReleaseDate", description="The date on which work on this version is expected to finish, expressed in the instance's *Day/Month/Year Format* date format.")
    user_start_date: str | None = Field(None, validation_alias="userStartDate", serialization_alias="userStartDate", description="The date on which work on this version is expected to start, expressed in the instance's *Day/Month/Year Format* date format.")

class Project(StrictModel):
    """Details about a project."""
    archived: bool | None = Field(None, description="Whether the project is archived.")
    archived_by: User | None = Field(None, validation_alias="archivedBy", serialization_alias="archivedBy", description="The user who archived the project.")
    archived_date: str | None = Field(None, validation_alias="archivedDate", serialization_alias="archivedDate", description="The date when the project was archived.", json_schema_extra={'format': 'date-time'})
    assignee_type: Literal["PROJECT_LEAD", "UNASSIGNED"] | None = Field(None, validation_alias="assigneeType", serialization_alias="assigneeType", description="The default assignee when creating issues for this project.")
    avatar_urls: AvatarUrlsBean | None = Field(None, validation_alias="avatarUrls", serialization_alias="avatarUrls", description="The URLs of the project's avatars.")
    components: list[ProjectComponent] | None = Field(None, description="List of the components contained in the project.")
    deleted: bool | None = Field(None, description="Whether the project is marked as deleted.")
    deleted_by: User | None = Field(None, validation_alias="deletedBy", serialization_alias="deletedBy", description="The user who marked the project as deleted.")
    deleted_date: str | None = Field(None, validation_alias="deletedDate", serialization_alias="deletedDate", description="The date when the project was marked as deleted.", json_schema_extra={'format': 'date-time'})
    description: str | None = Field(None, description="A brief description of the project.")
    email: str | None = Field(None, description="An email address associated with the project.")
    expand: str | None = Field(None, description="Expand options that include additional project details in the response.")
    favourite: bool | None = Field(None, description="Whether the project is selected as a favorite.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the project.")
    insight: ProjectInsight | None = Field(None, description="Insights about the project.")
    is_private: bool | None = Field(None, validation_alias="isPrivate", serialization_alias="isPrivate", description="Whether the project is private from the user's perspective. This means the user can't see the project or any associated issues.")
    issue_type_hierarchy: Hierarchy | None = Field(None, validation_alias="issueTypeHierarchy", serialization_alias="issueTypeHierarchy", description="The issue type hierarchy for the project.")
    issue_types: list[IssueTypeDetails] | None = Field(None, validation_alias="issueTypes", serialization_alias="issueTypes", description="List of the issue types available in the project.")
    key: str | None = Field(None, description="The key of the project.")
    landing_page_info: ProjectLandingPageInfo | None = Field(None, validation_alias="landingPageInfo", serialization_alias="landingPageInfo", description="The project landing page info.")
    lead: User | None = Field(None, description="The username of the project lead.")
    name: str | None = Field(None, description="The name of the project.")
    permissions: ProjectPermissions | None = Field(None, description="User permissions on the project")
    project_category: ProjectCategory | None = Field(None, validation_alias="projectCategory", serialization_alias="projectCategory", description="The category the project belongs to.")
    project_type_key: Literal["software", "service_desk", "business"] | None = Field(None, validation_alias="projectTypeKey", serialization_alias="projectTypeKey", description="The [project type](https://confluence.atlassian.com/x/GwiiLQ#Jiraapplicationsoverview-Productfeaturesandprojecttypes) of the project.")
    properties: dict[str, Any] | None = Field(None, description="Map of project properties")
    retention_till_date: str | None = Field(None, validation_alias="retentionTillDate", serialization_alias="retentionTillDate", description="The date when the project is deleted permanently.", json_schema_extra={'format': 'date-time'})
    roles: dict[str, str] | None = Field(None, description="The name and self URL for each role defined in the project. For more information, see [Create project role](#api-rest-api-3-role-post).")
    self: str | None = Field(None, description="The URL of the project details.", json_schema_extra={'format': 'uri'})
    simplified: bool | None = Field(None, description="Whether the project is simplified.")
    style: Literal["classic", "next-gen"] | None = Field(None, description="The type of the project.")
    url: str | None = Field(None, description="A link to information about this project, such as project documentation.")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="Unique ID for next-gen projects.", json_schema_extra={'format': 'uuid'})
    versions: list[Version] | None = Field(None, description="The versions defined in the project. For more information, see [Create version](#api-rest-api-3-version-post).")

class CreateIssueSourceRequest(StrictModel):
    type_: Literal["Board", "Project", "Filter"] = Field(..., validation_alias="type", serialization_alias="type", description="The issue source type. This must be \"Board\", \"Project\" or \"Filter\".")
    value: int = Field(..., description="The issue source value. This must be a board ID if the type is \"Board\", a project ID if the type is \"Project\" or a filter ID if the type is \"Filter\".", json_schema_extra={'format': 'int64'})

class SharePermission(StrictModel):
    """Details of a share permission for the filter."""
    group: GroupName | None = Field(None, description="The group that the filter is shared with. For a request, specify the `groupId` or `name` property for the group. As a group's name can change, use of `groupId` is recommended.")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier of the share permission.", json_schema_extra={'format': 'int64'})
    project: Project | None = Field(None, description="The project that the filter is shared with. This is similar to the project object returned by [Get project](#api-rest-api-3-project-projectIdOrKey-get) but it contains a subset of the properties, which are: `self`, `id`, `key`, `assigneeType`, `name`, `roles`, `avatarUrls`, `projectType`, `simplified`.  \nFor a request, specify the `id` for the project.")
    role: ProjectRole | None = Field(None, description="The project role that the filter is shared with.  \nFor a request, specify the `id` for the role. You must also specify the `project` object and `id` for the project that the role is in.")
    type_: Literal["user", "group", "project", "projectRole", "global", "loggedin", "authenticated", "project-unknown"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of share permission:\n\n *  `user` Shared with a user.\n *  `group` Shared with a group. If set in a request, then specify `sharePermission.group` as well.\n *  `project` Shared with a project. If set in a request, then specify `sharePermission.project` as well.\n *  `projectRole` Share with a project role in a project. This value is not returned in responses. It is used in requests, where it needs to be specify with `projectId` and `projectRoleId`.\n *  `global` Shared globally. If set in a request, no other `sharePermission` properties need to be specified.\n *  `loggedin` Shared with all logged-in users. Note: This value is set in a request by specifying `authenticated` as the `type`.\n *  `project-unknown` Shared with a project that the user does not have access to. Cannot be set in a request.")
    user: UserBean | None = Field(None, description="The user account ID that the filter is shared with. For a request, specify the `accountId` property for the user.")

class BulkEditDashboardsBodyPermissionDetails(StrictModel):
    """The permission details to be changed."""
    edit_permissions: list[SharePermission] = Field(..., validation_alias="editPermissions", serialization_alias="editPermissions", description="The edit permissions for the shareable entities.")
    share_permissions: list[SharePermission] = Field(..., validation_alias="sharePermissions", serialization_alias="sharePermissions", description="The share permissions for the shareable entities.")

class Dashboard(StrictModel):
    """Details of a dashboard."""
    automatic_refresh_ms: int | None = Field(None, validation_alias="automaticRefreshMs", serialization_alias="automaticRefreshMs", description="The automatic refresh interval for the dashboard in milliseconds.", json_schema_extra={'format': 'int32'})
    description: str | None = None
    edit_permissions: list[SharePermission] | None = Field(None, validation_alias="editPermissions", serialization_alias="editPermissions", description="The details of any edit share permissions for the dashboard.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the dashboard.")
    is_favourite: bool | None = Field(None, validation_alias="isFavourite", serialization_alias="isFavourite", description="Whether the dashboard is selected as a favorite by the user.")
    is_writable: bool | None = Field(None, validation_alias="isWritable", serialization_alias="isWritable", description="Whether the current user has permission to edit the dashboard.")
    name: str | None = Field(None, description="The name of the dashboard.")
    owner: UserBean | None = Field(None, description="The owner of the dashboard.")
    popularity: int | None = Field(None, description="The number of users who have this dashboard as a favorite.", json_schema_extra={'format': 'int64'})
    rank: int | None = Field(None, description="The rank of this dashboard.", json_schema_extra={'format': 'int32'})
    self: str | None = Field(None, description="The URL of these dashboard details.", json_schema_extra={'format': 'uri'})
    share_permissions: list[SharePermission] | None = Field(None, validation_alias="sharePermissions", serialization_alias="sharePermissions", description="The details of any view share permissions for the dashboard.")
    system_dashboard: bool | None = Field(None, validation_alias="systemDashboard", serialization_alias="systemDashboard", description="Whether the current dashboard is system dashboard.")
    view: str | None = Field(None, description="The URL of the dashboard.")

class Visibility(PermissiveModel):
    """The group or role to which this item is visible."""
    identifier: str | None = Field(None, description="The ID of the group or the name of the role that visibility of this item is restricted to.")
    type_: Literal["group", "role"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Whether visibility of this item is restricted to a group or role.")
    value: str | None = Field(None, description="The name of the group or role that visibility of this item is restricted to. Please note that the name of a group is mutable, to reliably identify a group use `identifier`.")

class WorkflowOperations(StrictModel):
    """Operations allowed on a workflow"""
    can_delete: bool = Field(..., validation_alias="canDelete", serialization_alias="canDelete", description="Whether the workflow can be deleted.")
    can_edit: bool = Field(..., validation_alias="canEdit", serialization_alias="canEdit", description="Whether the workflow can be updated.")

class WorkflowSchemeIdName(StrictModel):
    """The ID and the name of the workflow scheme."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the workflow scheme.")
    name: str = Field(..., description="The name of the workflow scheme.")

class WorkflowSimpleCondition(PermissiveModel):
    """A workflow transition rule condition. This object returns `nodeType` as `simple`."""
    configuration: dict[str, Any] | None = Field(None, description="EXPERIMENTAL. The configuration of the transition rule.")
    node_type: str = Field(..., validation_alias="nodeType", serialization_alias="nodeType")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The type of the transition rule.")

class WorkflowStatus(StrictModel):
    """Details of a workflow status."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the issue status.")
    name: str = Field(..., description="The name of the status in the workflow.")
    properties: dict[str, Any] | None = Field(None, description="Additional properties that modify the behavior of issues in this status. Supports the properties `jira.issue.editable` and `issueEditable` (deprecated) that indicate whether issues are editable.")

class WorkflowStatusLayoutPayload(StrictModel):
    """The layout of the workflow status."""
    x: float | None = Field(None, description="The x coordinate of the status.", json_schema_extra={'format': 'double'})
    y: float | None = Field(None, description="The y coordinate of the status.", json_schema_extra={'format': 'double'})

class WorkflowStatusPayload(StrictModel):
    """The statuses to be used in the workflow"""
    layout: WorkflowStatusLayoutPayload | None = None
    pcri: ProjectCreateResourceIdentifier | None = None
    properties: dict[str, str] | None = Field(None, description="The properties of the workflow status.")

class WorkflowTransitionRule(StrictModel):
    """A workflow transition rule."""
    configuration: Any | None = Field(None, description="EXPERIMENTAL. The configuration of the transition rule.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The type of the transition rule.")

class WorkingDaysConfig(StrictModel):
    """Working days configuration"""
    friday: bool | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    monday: bool | None = None
    non_working_days: Annotated[list[NonWorkingDay], AfterValidator(_check_unique_items)] | None = Field(None, validation_alias="nonWorkingDays", serialization_alias="nonWorkingDays")
    saturday: bool | None = None
    sunday: bool | None = None
    thursday: bool | None = None
    timezone_id: str | None = Field(None, validation_alias="timezoneId", serialization_alias="timezoneId")
    tuesday: bool | None = None
    wednesday: bool | None = None

class BoardPayload(StrictModel):
    """The payload for creating a board"""
    board_filter_jql: str | None = Field(None, validation_alias="boardFilterJQL", serialization_alias="boardFilterJQL", description="Takes in a JQL string to create a new filter. If no value is provided, it'll default to a JQL filter for the project creating")
    card_color_strategy: Literal["ISSUE_TYPE", "REQUEST_TYPE", "ASSIGNEE", "PRIORITY", "NONE", "CUSTOM"] | None = Field(None, validation_alias="cardColorStrategy", serialization_alias="cardColorStrategy", description="Card color settings of the board")
    card_layout: CardLayout | None = Field(None, validation_alias="cardLayout", serialization_alias="cardLayout")
    card_layouts: list[CardLayoutField] | None = Field(None, validation_alias="cardLayouts", serialization_alias="cardLayouts", description="Card layout settings of the board")
    columns: list[BoardColumnPayload] | None = Field(None, description="The columns of the board")
    features: list[BoardFeaturePayload] | None = Field(None, description="Feature settings for the board")
    name: str | None = Field(None, description="The name of the board")
    pcri: ProjectCreateResourceIdentifier | None = None
    quick_filters: list[QuickFilterPayload] | None = Field(None, validation_alias="quickFilters", serialization_alias="quickFilters", description="The quick filters for the board.")
    supports_sprint: bool | None = Field(True, validation_alias="supportsSprint", serialization_alias="supportsSprint", description="Whether sprints are supported on the board")
    swimlanes: SwimlanesPayload | None = None
    working_days_config: WorkingDaysConfig | None = Field(None, validation_alias="workingDaysConfig", serialization_alias="workingDaysConfig")

class CreateProjectWithCustomTemplateBodyTemplateBoards(StrictModel):
    boards: list[BoardPayload] | None = Field(None, description="The boards to be associated with the project.")

class ConditionGroupPayload(StrictModel):
    """The payload for creating a condition group in a workflow"""
    condition_group: list[ConditionGroupPayload] | None = Field(None, validation_alias="conditionGroup", serialization_alias="conditionGroup", description="The nested conditions of the condition group.")
    conditions: list[RulePayload] | None = Field(None, description="The rules for this condition.")
    operation: Literal["ANY", "ALL"] | None = Field(None, description="Determines how the conditions in the group are evaluated. Accepts either `ANY` or `ALL`. If `ANY` is used, at least one condition in the group must be true for the group to evaluate to true. If `ALL` is used, all conditions in the group must be true for the group to evaluate to true.")

class CreateProjectWithCustomTemplateBodyTemplate(StrictModel):
    """Project template configuration: boards, field schemes, issue types, notification schemes, permission schemes, roles, security levels, workflows, and their mappings."""
    boards: CreateProjectWithCustomTemplateBodyTemplateBoards | None = None
    field: CreateProjectWithCustomTemplateBodyTemplateField | None = Field(None, description="Defines the payload for the fields, screens, screen schemes, issue type screen schemes, field layouts, and field layout schemes")
    issue_type: CreateProjectWithCustomTemplateBodyTemplateIssueType | None = Field(None, validation_alias="issueType", serialization_alias="issueType", description="The payload for creating issue types in a project")
    notification: CreateProjectWithCustomTemplateBodyTemplateNotification | None = Field(None, description="The payload for creating a notification scheme. The user has to supply the ID for the default notification scheme. For CMP this is provided in the project payload and should be left empty, for TMP it's provided using this payload")
    permission_scheme: CreateProjectWithCustomTemplateBodyTemplatePermissionScheme | None = Field(None, validation_alias="permissionScheme", serialization_alias="permissionScheme", description="The payload to create a permission scheme")
    project: CreateProjectWithCustomTemplateBodyTemplateProject | None = Field(None, description="The payload for creating a project")
    role: CreateProjectWithCustomTemplateBodyTemplateRole | None = None
    scope: CreateProjectWithCustomTemplateBodyTemplateScope | None = Field(None, description="The payload for creating a scope. Defines if a project is team-managed project or company-managed project")
    security: CreateProjectWithCustomTemplateBodyTemplateSecurity | None = Field(None, description="The payload for creating a security scheme. See https://support.atlassian.com/jira-cloud-administration/docs/configure-issue-security-schemes/")
    workflow: CreateProjectWithCustomTemplateBodyTemplateWorkflow | None = Field(None, description="The payload for creating a workflows. See https://www.atlassian.com/software/jira/guides/workflows/overview\\#what-is-a-jira-workflow")

class CreateProjectWithCustomTemplateBodyTemplateWorkflow(StrictModel):
    """The payload for creating a workflows. See https://www.atlassian.com/software/jira/guides/workflows/overview\\#what-is-a-jira-workflow"""
    statuses: list[StatusPayload] | None = Field(None, description="The statuses for the workflow")
    workflow_scheme: CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowScheme | None = Field(None, validation_alias="workflowScheme", serialization_alias="workflowScheme", description="The payload for creating a workflow scheme. See https://www.atlassian.com/software/jira/guides/workflows/overview\\#what-is-a-jira-workflow-scheme")
    workflows: list[WorkflowPayload] | None = Field(None, description="The transitions for the workflow")

class Transition(StrictModel):
    """Details of a workflow transition."""
    description: str = Field(..., description="The description of the transition.")
    from_: list[str] = Field(..., validation_alias="from", serialization_alias="from", description="The statuses the transition can start from.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the transition.")
    name: str = Field(..., description="The name of the transition.")
    properties: dict[str, Any] | None = Field(None, description="The properties of the transition.")
    rules: WorkflowRules | None = None
    screen: TransitionScreenDetails | None = None
    to: str = Field(..., description="The status the transition goes to.")
    type_: Literal["global", "initial", "directed"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the transition.")

class TransitionPayload(StrictModel):
    """The payload for creating a transition in a workflow. Can be DIRECTED, GLOBAL, SELF-LOOPED, GLOBAL LOOPED"""
    actions: list[RulePayload] | None = Field(None, description="The actions that are performed when the transition is made")
    conditions: ConditionGroupPayload | None = None
    custom_issue_event_id: str | None = Field(None, validation_alias="customIssueEventId", serialization_alias="customIssueEventId", description="Mechanism in Jira for triggering certain actions, like notifications, automations, etc. Unless a custom notification scheme is configure, it's better not to provide any value here")
    description: str | None = Field(None, description="The description of the transition")
    from_: list[FromLayoutPayload] | None = Field(None, validation_alias="from", serialization_alias="from", description="The statuses that the transition can be made from")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The id of the transition", json_schema_extra={'format': 'int32'})
    name: str | None = Field(None, description="The name of the transition")
    properties: dict[str, str] | None = Field(None, description="The properties of the transition")
    to: ToLayoutPayload | None = None
    transition_screen: RulePayload | None = Field(None, validation_alias="transitionScreen", serialization_alias="transitionScreen")
    triggers: list[RulePayload] | None = Field(None, description="The triggers that are performed when the transition is made")
    type_: Literal["global", "initial", "directed"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the transition")
    validators: list[RulePayload] | None = Field(None, description="The validators that are performed when the transition is made")

class Workflow(StrictModel):
    """Details about a workflow."""
    created: str | None = Field(None, description="The creation date of the workflow.", json_schema_extra={'format': 'date-time'})
    description: str = Field(..., description="The description of the workflow.")
    has_draft_workflow: bool | None = Field(None, validation_alias="hasDraftWorkflow", serialization_alias="hasDraftWorkflow", description="Whether the workflow has a draft version.")
    id_: PublishedWorkflowId = Field(..., validation_alias="id", serialization_alias="id")
    is_default: bool | None = Field(None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether this is the default workflow.")
    operations: WorkflowOperations | None = None
    projects: list[ProjectDetails] | None = Field(None, description="The projects the workflow is assigned to, through workflow schemes.")
    schemes: list[WorkflowSchemeIdName] | None = Field(None, description="The workflow schemes the workflow is assigned to.")
    statuses: list[WorkflowStatus] | None = Field(None, description="The statuses of the workflow.")
    transitions: list[Transition] | None = Field(None, description="The transitions of the workflow.")
    updated: str | None = Field(None, description="The last edited date of the workflow.", json_schema_extra={'format': 'date-time'})

class WorkflowCompoundCondition(PermissiveModel):
    """A compound workflow transition rule condition. This object returns `nodeType` as `compound`."""
    conditions: list[WorkflowSimpleCondition | WorkflowCompoundCondition] = Field(..., description="The list of workflow conditions.")
    node_type: str = Field(..., validation_alias="nodeType", serialization_alias="nodeType")
    operator: Literal["AND", "OR"] = Field(..., description="The compound condition operator.")

class WorkflowPayload(StrictModel):
    """The payload for creating workflow, see https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/\\#api-rest-api-3-workflows-create-post"""
    description: str | None = Field(None, description="The description of the workflow")
    looped_transition_container_layout: WorkflowStatusLayoutPayload | None = Field(None, validation_alias="loopedTransitionContainerLayout", serialization_alias="loopedTransitionContainerLayout")
    name: str | None = Field(None, description="The name of the workflow")
    on_conflict: Literal["FAIL", "USE", "NEW"] | None = Field('NEW', validation_alias="onConflict", serialization_alias="onConflict", description="The strategy to use if there is a conflict with another workflow")
    pcri: ProjectCreateResourceIdentifier | None = None
    start_point_layout: WorkflowStatusLayoutPayload | None = Field(None, validation_alias="startPointLayout", serialization_alias="startPointLayout")
    statuses: list[WorkflowStatusPayload] | None = Field(None, description="The statuses to be used in the workflow")
    transitions: list[TransitionPayload] | None = Field(None, description="The transitions for the workflow")

class WorkflowRules(StrictModel):
    """A collection of transition rules."""
    conditions_tree: WorkflowSimpleCondition | WorkflowCompoundCondition | None = Field(None, validation_alias="conditionsTree", serialization_alias="conditionsTree")
    post_functions: list[WorkflowTransitionRule] | None = Field(None, validation_alias="postFunctions", serialization_alias="postFunctions", description="The workflow post functions.")
    validators: list[WorkflowTransitionRule] | None = Field(None, description="The workflow validators.")


# Rebuild models to resolve forward references (required for circular refs)
AddCommentBodyVisibility.model_rebuild()
AddWorklogBodyVisibility.model_rebuild()
ApplicationRole.model_rebuild()
AvatarUrlsBean.model_rebuild()
BoardColumnPayload.model_rebuild()
BoardFeaturePayload.model_rebuild()
BoardPayload.model_rebuild()
BulkEditDashboardsBodyChangeOwnerDetails.model_rebuild()
BulkEditDashboardsBodyPermissionDetails.model_rebuild()
BulkProjectPermissions.model_rebuild()
BulkSetIssuePropertyBodyFilter.model_rebuild()
BulkTransitionSubmitInput.model_rebuild()
CardLayout.model_rebuild()
CardLayoutField.model_rebuild()
ConditionGroupPayload.model_rebuild()
ContentItem.model_rebuild()
CreateCrossProjectReleaseRequest.model_rebuild()
CreateCustomFieldRequest.model_rebuild()
CreateDateFieldRequest.model_rebuild()
CreateExclusionRulesRequest.model_rebuild()
CreateIssueSourceRequest.model_rebuild()
CreateOrUpdateRemoteIssueLinkBodyApplication.model_rebuild()
CreateOrUpdateRemoteIssueLinkBodyObject.model_rebuild()
CreateOrUpdateRemoteIssueLinkBodyObjectIcon.model_rebuild()
CreateOrUpdateRemoteIssueLinkBodyObjectStatus.model_rebuild()
CreateOrUpdateRemoteIssueLinkBodyObjectStatusIcon.model_rebuild()
CreatePermissionHolderRequest.model_rebuild()
CreatePermissionRequest.model_rebuild()
CreatePlanBodyExclusionRules.model_rebuild()
CreatePlanBodyScheduling.model_rebuild()
CreatePlanBodySchedulingEndDate.model_rebuild()
CreatePlanBodySchedulingStartDate.model_rebuild()
CreateProjectWithCustomTemplateBodyDetails.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplate.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateBoards.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateField.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutSchemeDefaultFieldLayout.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldFieldLayoutSchemePcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldFieldScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldFieldSchemePcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenSchemeDefaultScreenScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateFieldIssueTypeScreenSchemePcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateIssueType.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeSchemeDefaultIssueTypeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateIssueTypeIssueTypeSchemePcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateNotification.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateNotificationPcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplatePermissionScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplatePermissionSchemePcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProject.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectFieldLayoutSchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectIssueSecuritySchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectIssueTypeSchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectIssueTypeScreenSchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectNotificationSchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectPcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectPermissionSchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateProjectWorkflowSchemeId.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateRole.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateScope.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateSecurity.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateSecurityPcri.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateWorkflow.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowScheme.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowSchemeDefaultWorkflow.model_rebuild()
CreateProjectWithCustomTemplateBodyTemplateWorkflowWorkflowSchemePcri.model_rebuild()
CreateSchedulingRequest.model_rebuild()
CustomContextVariable.model_rebuild()
CustomFieldOptionCreate.model_rebuild()
CustomFieldOptionUpdate.model_rebuild()
CustomFieldPayload.model_rebuild()
CustomFieldReplacement.model_rebuild()
CustomFieldValueUpdate.model_rebuild()
Dashboard.model_rebuild()
DoTransitionBodyTransition.model_rebuild()
DoTransitionBodyTransitionTo.model_rebuild()
DoTransitionBodyTransitionToScope.model_rebuild()
DoTransitionBodyTransitionToScopeProject.model_rebuild()
DoTransitionBodyTransitionToScopeProjectAvatarUrls.model_rebuild()
DoTransitionBodyTransitionToScopeProjectProjectCategory.model_rebuild()
DoTransitionBodyTransitionToStatusCategory.model_rebuild()
EntityProperty.model_rebuild()
EvaluateJsisJiraExpressionBodyContext.model_rebuild()
EvaluateJsisJiraExpressionBodyContextIssue.model_rebuild()
EvaluateJsisJiraExpressionBodyContextIssues.model_rebuild()
EvaluateJsisJiraExpressionBodyContextIssuesJql.model_rebuild()
EvaluateJsisJiraExpressionBodyContextProject.model_rebuild()
ExpandPrioritySchemePage.model_rebuild()
FieldAssociationItemPayload.model_rebuild()
FieldLayoutConfiguration.model_rebuild()
FieldLayoutPayload.model_rebuild()
FieldMetadata.model_rebuild()
Fields.model_rebuild()
FieldUpdateOperation.model_rebuild()
FromLayoutPayload.model_rebuild()
Group.model_rebuild()
GroupName.model_rebuild()
Hierarchy.model_rebuild()
HistoryMetadata.model_rebuild()
HistoryMetadataParticipant.model_rebuild()
Icon.model_rebuild()
IssueContextVariable.model_rebuild()
IssueEntityPropertiesForMultiUpdate.model_rebuild()
IssueLayoutItemPayload.model_rebuild()
IssueLayoutPayload.model_rebuild()
IssueTransition.model_rebuild()
IssueTypeDetails.model_rebuild()
IssueTypeHierarchyPayload.model_rebuild()
IssueTypePayload.model_rebuild()
IssueUpdateDetails.model_rebuild()
JiraCascadingSelectField.model_rebuild()
JiraColorField.model_rebuild()
JiraColorInput.model_rebuild()
JiraComponentField.model_rebuild()
JiraDateField.model_rebuild()
JiraDateInput.model_rebuild()
JiraDateTimeField.model_rebuild()
JiraDateTimeInput.model_rebuild()
JiraGroupInput.model_rebuild()
JiraLabelPropertiesInputJackson1.model_rebuild()
JiraLabelsField.model_rebuild()
JiraLabelsInput.model_rebuild()
JiraMultipleGroupPickerField.model_rebuild()
JiraMultipleSelectField.model_rebuild()
JiraMultipleSelectUserPickerField.model_rebuild()
JiraMultipleVersionPickerField.model_rebuild()
JiraNumberField.model_rebuild()
JiraRichTextField.model_rebuild()
JiraRichTextInput.model_rebuild()
JiraSelectedOptionField.model_rebuild()
JiraSingleGroupPickerField.model_rebuild()
JiraSingleLineTextField.model_rebuild()
JiraSingleSelectField.model_rebuild()
JiraSingleSelectUserPickerField.model_rebuild()
JiraSingleVersionPickerField.model_rebuild()
JiraUrlField.model_rebuild()
JiraUserField.model_rebuild()
JiraVersionField.model_rebuild()
JsonContextVariable.model_rebuild()
JsonNode.model_rebuild()
JsonTypeBean.model_rebuild()
LinkIssuesBodyCommentVisibility.model_rebuild()
ListWrapperCallbackApplicationRole.model_rebuild()
ListWrapperCallbackGroupName.model_rebuild()
MandatoryFieldValue.model_rebuild()
MandatoryFieldValueForAdf.model_rebuild()
MultipartFile.model_rebuild()
MultipleCustomFieldValuesUpdate.model_rebuild()
NonWorkingDay.model_rebuild()
NotificationSchemeEventIdPayload.model_rebuild()
NotificationSchemeEventPayload.model_rebuild()
NotificationSchemeNotificationDetailsPayload.model_rebuild()
NotifyBodyRestrict.model_rebuild()
NotifyBodyTo.model_rebuild()
PagedListUserDetailsApplicationUser.model_rebuild()
PermissionGrantDto.model_rebuild()
Permissions.model_rebuild()
Priority.model_rebuild()
Project.model_rebuild()
ProjectCategory.model_rebuild()
ProjectComponent.model_rebuild()
ProjectCreateResourceIdentifier.model_rebuild()
ProjectDetails.model_rebuild()
ProjectInsight.model_rebuild()
ProjectLandingPageInfo.model_rebuild()
ProjectPermissions.model_rebuild()
ProjectRole.model_rebuild()
ProjectRoleGroup.model_rebuild()
ProjectRoleUser.model_rebuild()
PublishedWorkflowId.model_rebuild()
QuickFilterPayload.model_rebuild()
RedactionPosition.model_rebuild()
ResourceModel.model_rebuild()
RestrictedPermission.model_rebuild()
RoleActor.model_rebuild()
RolePayload.model_rebuild()
RulePayload.model_rebuild()
Scope.model_rebuild()
ScreenPayload.model_rebuild()
ScreenSchemePayload.model_rebuild()
SecurityLevelMemberPayload.model_rebuild()
SecurityLevelPayload.model_rebuild()
SharePermission.model_rebuild()
SimpleLink.model_rebuild()
SimpleListWrapperApplicationRole.model_rebuild()
SimpleListWrapperGroupName.model_rebuild()
SimplifiedHierarchyLevel.model_rebuild()
SingleRedactionRequest.model_rebuild()
Status.model_rebuild()
StatusCategory.model_rebuild()
StatusDetails.model_rebuild()
StatusPayload.model_rebuild()
SubmitBulkEditBodyEditedFieldsInput.model_rebuild()
SubmitBulkEditBodyEditedFieldsInputIssueType.model_rebuild()
SubmitBulkEditBodyEditedFieldsInputMultiselectComponents.model_rebuild()
SubmitBulkEditBodyEditedFieldsInputOriginalEstimateField.model_rebuild()
SubmitBulkEditBodyEditedFieldsInputPriority.model_rebuild()
SubmitBulkEditBodyEditedFieldsInputStatus.model_rebuild()
SubmitBulkEditBodyEditedFieldsInputTimeTrackingField.model_rebuild()
SwimlanePayload.model_rebuild()
SwimlanesPayload.model_rebuild()
TabPayload.model_rebuild()
TargetClassification.model_rebuild()
TargetMandatoryFields.model_rebuild()
TargetMandatoryFieldsFieldsValue.model_rebuild()
TargetStatus.model_rebuild()
TargetToSourcesMapping.model_rebuild()
TimeTrackingDetails.model_rebuild()
ToLayoutPayload.model_rebuild()
Transition.model_rebuild()
TransitionPayload.model_rebuild()
TransitionScreenDetails.model_rebuild()
UpdateCommentBodyVisibility.model_rebuild()
UpdatedProjectCategory.model_rebuild()
UpdateRemoteIssueLinkBodyApplication.model_rebuild()
UpdateRemoteIssueLinkBodyObject.model_rebuild()
UpdateRemoteIssueLinkBodyObjectIcon.model_rebuild()
UpdateRemoteIssueLinkBodyObjectStatus.model_rebuild()
UpdateRemoteIssueLinkBodyObjectStatusIcon.model_rebuild()
UpdateWorklogBodyVisibility.model_rebuild()
User.model_rebuild()
UserBean.model_rebuild()
UserBeanAvatarUrls.model_rebuild()
UserContextVariable.model_rebuild()
UserDetails.model_rebuild()
UserPermission.model_rebuild()
Version.model_rebuild()
VersionApprover.model_rebuild()
VersionIssuesStatus.model_rebuild()
Visibility.model_rebuild()
Workflow.model_rebuild()
WorkflowCompoundCondition.model_rebuild()
WorkflowOperations.model_rebuild()
WorkflowPayload.model_rebuild()
WorkflowRules.model_rebuild()
WorkflowSchemeIdName.model_rebuild()
WorkflowSimpleCondition.model_rebuild()
WorkflowStatus.model_rebuild()
WorkflowStatusLayoutPayload.model_rebuild()
WorkflowStatusPayload.model_rebuild()
WorkflowTransitionRule.model_rebuild()
WorkingDaysConfig.model_rebuild()

"""
Asana MCP Server - Pydantic Models

Generated: 2026-04-14 18:14:32 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AddCustomFieldSettingForGoalRequest",
    "AddCustomFieldSettingForPortfolioRequest",
    "AddCustomFieldSettingForProjectRequest",
    "AddDependenciesForTaskRequest",
    "AddDependentsForTaskRequest",
    "AddFollowersForProjectRequest",
    "AddFollowersForTaskRequest",
    "AddFollowersRequest",
    "AddItemForPortfolioRequest",
    "AddMembersForPortfolioRequest",
    "AddMembersForProjectRequest",
    "AddProjectForTaskRequest",
    "AddSupportingRelationshipRequest",
    "AddTagForTaskRequest",
    "AddTaskForSectionRequest",
    "AddUserForTeamRequest",
    "AddUserForWorkspaceRequest",
    "ApproveAccessRequest",
    "CreateAccessRequest",
    "CreateAllocationRequest",
    "CreateAttachmentForObjectRequest",
    "CreateBudgetRequest",
    "CreateCustomFieldRequest",
    "CreateEnumOptionForCustomFieldRequest",
    "CreateGoalMetricRequest",
    "CreateGoalRequest",
    "CreateGraphExportRequest",
    "CreateMembershipRequest",
    "CreateOrganizationExportRequest",
    "CreatePortfolioRequest",
    "CreateProjectBriefRequest",
    "CreateProjectForTeamRequest",
    "CreateProjectForWorkspaceRequest",
    "CreateProjectRequest",
    "CreateProjectStatusForProjectRequest",
    "CreateRateRequest",
    "CreateResourceExportRequest",
    "CreateSectionForProjectRequest",
    "CreateStatusForObjectRequest",
    "CreateStoryForTaskRequest",
    "CreateSubtaskForTaskRequest",
    "CreateTagForWorkspaceRequest",
    "CreateTagRequest",
    "CreateTaskRequest",
    "CreateTeamRequest",
    "CreateTimesheetApprovalStatusRequest",
    "CreateTimeTrackingEntryRequest",
    "DeleteAllocationRequest",
    "DeleteAttachmentRequest",
    "DeleteBudgetRequest",
    "DeleteCustomFieldRequest",
    "DeleteGoalRequest",
    "DeleteMembershipRequest",
    "DeletePortfolioRequest",
    "DeleteProjectBriefRequest",
    "DeleteProjectRequest",
    "DeleteProjectStatusRequest",
    "DeleteProjectTemplateRequest",
    "DeleteRateRequest",
    "DeleteSectionRequest",
    "DeleteStatusRequest",
    "DeleteStoryRequest",
    "DeleteTagRequest",
    "DeleteTaskRequest",
    "DeleteTaskTemplateRequest",
    "DeleteTimeTrackingEntryRequest",
    "DeleteWebhookRequest",
    "DuplicatePortfolioRequest",
    "DuplicateProjectRequest",
    "DuplicateTaskRequest",
    "GetAccessRequestsRequest",
    "GetAllocationRequest",
    "GetAllocationsRequest",
    "GetAttachmentRequest",
    "GetAttachmentsForObjectRequest",
    "GetAuditLogEventsRequest",
    "GetBudgetRequest",
    "GetBudgetsRequest",
    "GetCustomFieldRequest",
    "GetCustomFieldSettingsForGoalRequest",
    "GetCustomFieldSettingsForPortfolioRequest",
    "GetCustomFieldSettingsForProjectRequest",
    "GetCustomFieldSettingsForTeamRequest",
    "GetCustomFieldsForWorkspaceRequest",
    "GetCustomTypeRequest",
    "GetCustomTypesRequest",
    "GetDependenciesForTaskRequest",
    "GetDependentsForTaskRequest",
    "GetEventsRequest",
    "GetFavoritesForUserRequest",
    "GetGoalRelationshipRequest",
    "GetGoalRelationshipsRequest",
    "GetGoalRequest",
    "GetGoalsRequest",
    "GetItemsForPortfolioRequest",
    "GetJobRequest",
    "GetMembershipRequest",
    "GetMembershipsRequest",
    "GetOrganizationExportRequest",
    "GetParentGoalsForGoalRequest",
    "GetPortfolioMembershipRequest",
    "GetPortfolioMembershipsForPortfolioRequest",
    "GetPortfolioMembershipsRequest",
    "GetPortfolioRequest",
    "GetPortfoliosRequest",
    "GetProjectBriefRequest",
    "GetProjectMembershipRequest",
    "GetProjectMembershipsForProjectRequest",
    "GetProjectPortfolioSettingRequest",
    "GetProjectPortfolioSettingsForProjectRequest",
    "GetProjectRequest",
    "GetProjectsForTaskRequest",
    "GetProjectsForWorkspaceRequest",
    "GetProjectsRequest",
    "GetProjectStatusesForProjectRequest",
    "GetProjectStatusRequest",
    "GetProjectTemplateRequest",
    "GetProjectTemplatesForTeamRequest",
    "GetProjectTemplatesRequest",
    "GetRateRequest",
    "GetRatesRequest",
    "GetReactionsOnObjectRequest",
    "GetSectionRequest",
    "GetSectionsForProjectRequest",
    "GetStatusesForObjectRequest",
    "GetStatusRequest",
    "GetStoriesForTaskRequest",
    "GetStoryRequest",
    "GetSubtasksForTaskRequest",
    "GetTagRequest",
    "GetTagsForTaskRequest",
    "GetTagsForWorkspaceRequest",
    "GetTagsRequest",
    "GetTaskCountsForProjectRequest",
    "GetTaskForCustomIdRequest",
    "GetTaskRequest",
    "GetTasksForProjectRequest",
    "GetTasksForSectionRequest",
    "GetTasksForTagRequest",
    "GetTasksForUserTaskListRequest",
    "GetTasksRequest",
    "GetTaskTemplateRequest",
    "GetTaskTemplatesRequest",
    "GetTeamMembershipRequest",
    "GetTeamMembershipsForTeamRequest",
    "GetTeamMembershipsForUserRequest",
    "GetTeamMembershipsRequest",
    "GetTeamRequest",
    "GetTeamsForUserRequest",
    "GetTeamsForWorkspaceRequest",
    "GetTimePeriodRequest",
    "GetTimePeriodsRequest",
    "GetTimesheetApprovalStatusesRequest",
    "GetTimesheetApprovalStatusRequest",
    "GetTimeTrackingEntriesForTaskRequest",
    "GetTimeTrackingEntriesRequest",
    "GetTimeTrackingEntryRequest",
    "GetUserForWorkspaceRequest",
    "GetUserRequest",
    "GetUsersForTeamRequest",
    "GetUsersForWorkspaceRequest",
    "GetUsersRequest",
    "GetUserTaskListForUserRequest",
    "GetUserTaskListRequest",
    "GetWebhookRequest",
    "GetWorkspaceEventsRequest",
    "GetWorkspaceMembershipRequest",
    "GetWorkspaceMembershipsForUserRequest",
    "GetWorkspaceMembershipsForWorkspaceRequest",
    "GetWorkspaceRequest",
    "GetWorkspacesRequest",
    "InsertEnumOptionForCustomFieldRequest",
    "InsertSectionForProjectRequest",
    "InstantiateProjectRequest",
    "InstantiateTaskRequest",
    "ProjectSaveAsTemplateRequest",
    "RejectAccessRequest",
    "RemoveCustomFieldSettingForGoalRequest",
    "RemoveCustomFieldSettingForPortfolioRequest",
    "RemoveCustomFieldSettingForProjectRequest",
    "RemoveDependenciesForTaskRequest",
    "RemoveDependentsForTaskRequest",
    "RemoveFollowerForTaskRequest",
    "RemoveFollowersForProjectRequest",
    "RemoveFollowersRequest",
    "RemoveItemForPortfolioRequest",
    "RemoveMembersForPortfolioRequest",
    "RemoveMembersForProjectRequest",
    "RemoveProjectForTaskRequest",
    "RemoveSupportingRelationshipRequest",
    "RemoveTagForTaskRequest",
    "RemoveUserForTeamRequest",
    "RemoveUserForWorkspaceRequest",
    "SearchProjectsForWorkspaceRequest",
    "SearchTasksForWorkspaceRequest",
    "SetParentForTaskRequest",
    "TypeaheadForWorkspaceRequest",
    "UpdateAllocationRequest",
    "UpdateBudgetRequest",
    "UpdateCustomFieldRequest",
    "UpdateEnumOptionRequest",
    "UpdateGoalMetricRequest",
    "UpdateGoalRelationshipRequest",
    "UpdateGoalRequest",
    "UpdateMembershipRequest",
    "UpdatePortfolioRequest",
    "UpdateProjectBriefRequest",
    "UpdateProjectPortfolioSettingRequest",
    "UpdateProjectRequest",
    "UpdateRateRequest",
    "UpdateSectionRequest",
    "UpdateStoryRequest",
    "UpdateTagRequest",
    "UpdateTaskRequest",
    "UpdateTeamRequest",
    "UpdateTimesheetApprovalStatusRequest",
    "UpdateTimeTrackingEntryRequest",
    "UpdateUserForWorkspaceRequest",
    "UpdateUserRequest",
    "UpdateWorkspaceRequest",
    "AllocationRequest",
    "BudgetRequest",
    "CreateAllocationBodyData",
    "CreateMembershipRequest",
    "CustomFieldCreateRequest",
    "CustomFieldRequest",
    "DateVariableRequest",
    "EnumOptionRequest",
    "GoalRelationshipRequest",
    "GoalRequest",
    "GoalUpdateRequest",
    "PortfolioRequest",
    "PortfolioUpdateRequest",
    "ProjectBriefRequest",
    "ProjectRequest",
    "ProjectStatusBase",
    "ProjectUpdateRequest",
    "RequestedRoleRequest",
    "ResourceExportRequestParameter",
    "StatusUpdateRequest",
    "TagBase",
    "TagCreateRequest",
    "TagCreateTagForWorkspaceRequest",
    "TaskRequest",
    "TeamRequest",
    "UserUpdateRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_access_requests
class GetAccessRequestsRequestQuery(StrictModel):
    target: str = Field(default=..., description="The globally unique identifier of the target object for which to retrieve pending access requests.")
    user: str | None = Field(default=None, description="Filters results to access requests submitted by a specific user. Accepts the literal string 'me' for the authenticated user, a user's email address, or a user's globally unique identifier.")
class GetAccessRequestsRequest(StrictModel):
    """Retrieves pending access requests for a specified target object, optionally filtered to a specific user. Useful for reviewing who is awaiting permission to access a resource."""
    query: GetAccessRequestsRequestQuery

# Operation: request_access
class CreateAccessRequestBodyData(StrictModel):
    target: str = Field(default=..., validation_alias="target", serialization_alias="target", description="The unique global ID (gid) of the private object you are requesting access to. Supports projects and portfolios.")
    message: str | None = Field(default=None, validation_alias="message", serialization_alias="message", description="An optional message to accompany the access request, allowing the requester to provide context or justification for why access is needed.")
class CreateAccessRequestBody(StrictModel):
    data: CreateAccessRequestBodyData
class CreateAccessRequest(StrictModel):
    """Submits an access request for a private project or portfolio, notifying the owner so they can grant or deny access."""
    body: CreateAccessRequestBody

# Operation: approve_access_request
class ApproveAccessRequestPath(StrictModel):
    access_request_gid: str = Field(default=..., description="The globally unique identifier of the access request to approve.")
class ApproveAccessRequest(StrictModel):
    """Approves a pending access request, granting the requester access to the associated target object. Use this to fulfill access requests that have been reviewed and authorized."""
    path: ApproveAccessRequestPath

# Operation: reject_access_request
class RejectAccessRequestPath(StrictModel):
    access_request_gid: str = Field(default=..., description="The globally unique identifier of the access request to reject.")
class RejectAccessRequest(StrictModel):
    """Rejects a pending access request for a target object, denying the requester permission to access the resource. Use this to explicitly decline access requests that should not be granted."""
    path: RejectAccessRequestPath

# Operation: get_allocation
class GetAllocationRequestPath(StrictModel):
    allocation_gid: str = Field(default=..., description="The globally unique identifier for the allocation you want to retrieve.")
class GetAllocationRequest(StrictModel):
    """Retrieves the complete record for a single allocation, including all associated details and metadata. Use this to fetch full information about a specific allocation by its unique identifier."""
    path: GetAllocationRequestPath

# Operation: update_allocation
class UpdateAllocationRequestPath(StrictModel):
    allocation_gid: str = Field(default=..., description="The globally unique identifier of the allocation to update.")
class UpdateAllocationRequestBody(StrictModel):
    """The updated fields for the allocation."""
    data: AllocationRequest | None = Field(default=None, description="An object containing the allocation fields to update; only the fields included will be modified, all other fields will retain their current values.")
class UpdateAllocationRequest(StrictModel):
    """Updates an existing allocation by replacing only the fields provided in the request body, leaving all unspecified fields unchanged. Returns the complete updated allocation record."""
    path: UpdateAllocationRequestPath
    body: UpdateAllocationRequestBody | None = None

# Operation: delete_allocation
class DeleteAllocationRequestPath(StrictModel):
    allocation_gid: str = Field(default=..., description="The globally unique identifier of the allocation to delete.")
class DeleteAllocationRequest(StrictModel):
    """Permanently deletes an existing allocation by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteAllocationRequestPath

# Operation: list_allocations
class GetAllocationsRequestQuery(StrictModel):
    parent: str | None = Field(default=None, description="The unique identifier of the project to filter allocations by, returning only allocations associated with that project.")
    assignee: str | None = Field(default=None, description="The unique identifier of the user or placeholder to filter allocations by, returning only allocations assigned to that individual or placeholder resource.")
    workspace: str | None = Field(default=None, description="The unique identifier of the workspace to scope the allocation results to, limiting results to allocations within that workspace.")
class GetAllocationsRequest(StrictModel):
    """Retrieves a list of allocations, optionally filtered by project, assignee, or workspace. Useful for reviewing how resources are distributed across tasks and team members."""
    query: GetAllocationsRequestQuery | None = None

# Operation: create_allocation
class CreateAllocationRequestBody(StrictModel):
    """The allocation to create."""
    data: CreateAllocationBodyData | None = Field(default=None, description="The allocation data to create, including all relevant fields for the new allocation record.")
class CreateAllocationRequest(StrictModel):
    """Creates a new allocation and returns the full record of the newly created allocation."""
    body: CreateAllocationRequestBody | None = None

# Operation: get_attachment
class GetAttachmentRequestPath(StrictModel):
    attachment_gid: str = Field(default=..., description="The globally unique identifier of the attachment to retrieve.")
class GetAttachmentRequest(StrictModel):
    """Retrieves the full record for a single attachment, including its metadata and download URL. Requires the attachments:read scope."""
    path: GetAttachmentRequestPath

# Operation: delete_attachment
class DeleteAttachmentRequestPath(StrictModel):
    attachment_gid: str = Field(default=..., description="The globally unique identifier (GID) of the attachment to delete.")
class DeleteAttachmentRequest(StrictModel):
    """Permanently deletes a specific attachment by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteAttachmentRequestPath

# Operation: list_attachments
class GetAttachmentsForObjectRequestQuery(StrictModel):
    parent: str = Field(default=..., description="The globally unique identifier (GID) of the parent object whose attachments you want to retrieve. Must reference a project, project brief, or task.")
class GetAttachmentsForObjectRequest(StrictModel):
    """Retrieves all attachments associated with a specified project, project brief, or task. For projects, this returns files in the 'Key resources' section; for tasks, this includes all associated files including inline images."""
    query: GetAttachmentsForObjectRequestQuery

# Operation: upload_attachment
class CreateAttachmentForObjectRequestBody(StrictModel):
    """The file you want to upload.

*Note when using curl:*

Be sure to add an `‘@’` before the file path, and use the `--form`
option instead of the `-d` option.

When uploading PDFs with curl, force the content-type to be pdf by
appending the content type to the file path: `--form
"file=@file.pdf;type=application/pdf"`."""
    resource_subtype: Literal["asana", "external"] | None = Field(default=None, description="Specifies the attachment type. Use 'asana' for direct file uploads or 'external' for linking an external URL resource. When set to 'external', the 'parent', 'name', and 'url' fields are also required.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="The binary file content to upload. Required when 'resource_subtype' is 'asana' (direct file upload). Files from third-party services such as Dropbox, Box, Vimeo, or Google Drive cannot be attached via the API.", json_schema_extra={'format': 'binary'})
    parent: str | None = Field(default=None, description="The unique identifier (GID) of the parent object to attach to — must be a task, project, or project brief. Required for all attachment types.")
    url: str | None = Field(default=None, description="The publicly accessible URL of the external resource to attach. Required when 'resource_subtype' is 'external'.")
    name: str | None = Field(default=None, description="A display name for the external resource being attached. Required when 'resource_subtype' is 'external'.")
    connect_to_app: bool | None = Field(default=None, description="When true, associates the current OAuth app with this external attachment to enable an in-task app components widget. Only applicable to external attachments on a parent task, requires OAuth authentication, and the app must be installed on a project containing the parent task.")
class CreateAttachmentForObjectRequest(StrictModel):
    """Upload a file or link an external resource as an attachment to a task, project, or project brief in Asana. Supports direct file uploads (up to 100MB) or external URL attachments; multipart/form-data encoding is required for file uploads."""
    body: CreateAttachmentForObjectRequestBody | None = None

# Operation: list_audit_log_events
class GetAuditLogEventsRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier for the workspace or organization whose audit log events you want to retrieve.")
class GetAuditLogEventsRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, description="Restricts results to events created at or after this timestamp. Must be provided in ISO 8601 date-time format. Note that events before October 8th, 2021 are not available.", json_schema_extra={'format': 'date-time'})
    end_at: str | None = Field(default=None, description="Restricts results to events created strictly before this timestamp (exclusive upper bound). Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    event_type: str | None = Field(default=None, description="Restricts results to events of a specific type. Refer to the supported audit log events documentation for the full list of valid event type values.")
    actor_type: Literal["user", "asana", "asana_support", "anonymous", "external_administrator"] | None = Field(default=None, description="Restricts results to events performed by actors of a specific type. Use this only when filtering by actor type without a specific actor ID; omit this parameter if actor_gid is provided. Valid values are user, asana, asana_support, anonymous, or external_administrator.")
    actor_gid: str | None = Field(default=None, description="Restricts results to events triggered by the actor with this specific globally unique identifier. When provided, actor_type should be omitted.")
    resource_gid: str | None = Field(default=None, description="Restricts results to events associated with the resource that has this globally unique identifier.")
    limit: int | None = Field(default=None, description="The number of audit log events to return per page. Must be between 1 and 100 inclusive. Use the offset from the previous response to retrieve the next page of results.", ge=1, le=100)
class GetAuditLogEventsRequest(StrictModel):
    """Retrieve a paginated list of audit log events captured in a workspace or organization, sorted by creation time in ascending order. Supports filtering by time range, event type, actor, and resource, and can be polled continuously to stream new events as they are captured."""
    path: GetAuditLogEventsRequestPath
    query: GetAuditLogEventsRequestQuery | None = None

# Operation: list_budgets
class GetBudgetsRequestQuery(StrictModel):
    parent: str = Field(default=..., description="The globally unique identifier of the parent object whose budgets should be retrieved. Currently only project identifiers are supported as valid parents.")
class GetBudgetsRequest(StrictModel):
    """Retrieves all budgets associated with a given parent object. Returns at most one budget per parent, which must be a project."""
    query: GetBudgetsRequestQuery

# Operation: create_budget
class CreateBudgetRequestBody(StrictModel):
    """The budget to create."""
    data: BudgetRequest | None = Field(default=None, description="The budget object containing all required fields to define the new budget, such as name, amount, currency, and associated scope or time period.")
class CreateBudgetRequest(StrictModel):
    """Creates a new budget with the specified configuration. Use this to define spending limits and tracking parameters for a project, team, or time period."""
    body: CreateBudgetRequestBody | None = None

# Operation: get_budget
class GetBudgetRequestPath(StrictModel):
    budget_gid: str = Field(default=..., description="The globally unique identifier of the budget to retrieve.")
class GetBudgetRequest(StrictModel):
    """Retrieves the complete record for a single budget, including all associated details and metadata. Use this to inspect a specific budget by its unique identifier."""
    path: GetBudgetRequestPath

# Operation: update_budget
class UpdateBudgetRequestPath(StrictModel):
    budget_gid: str = Field(default=..., description="The globally unique identifier of the budget to update.")
class UpdateBudgetRequestBody(StrictModel):
    """The budget to update."""
    data: BudgetRequest | None = Field(default=None, description="An object containing the budget fields to update; only the fields included will be modified, all others will retain their current values.")
class UpdateBudgetRequest(StrictModel):
    """Updates an existing budget by replacing only the fields provided in the request body, leaving all unspecified fields unchanged."""
    path: UpdateBudgetRequestPath
    body: UpdateBudgetRequestBody | None = None

# Operation: delete_budget
class DeleteBudgetRequestPath(StrictModel):
    budget_gid: str = Field(default=..., description="The globally unique identifier of the budget to delete.")
class DeleteBudgetRequest(StrictModel):
    """Permanently deletes an existing budget by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteBudgetRequestPath

# Operation: list_project_custom_field_settings
class GetCustomFieldSettingsForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project whose custom field settings you want to retrieve.")
class GetCustomFieldSettingsForProjectRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of custom field settings to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetCustomFieldSettingsForProjectRequest(StrictModel):
    """Retrieves all custom field settings configured on a specific project, returned in compact form. Use opt_fields to request additional field data beyond the default compact representation."""
    path: GetCustomFieldSettingsForProjectRequestPath
    query: GetCustomFieldSettingsForProjectRequestQuery | None = None

# Operation: list_portfolio_custom_field_settings
class GetCustomFieldSettingsForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio whose custom field settings you want to retrieve.")
class GetCustomFieldSettingsForPortfolioRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of custom field setting objects to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetCustomFieldSettingsForPortfolioRequest(StrictModel):
    """Retrieves all custom field settings configured on a specific portfolio, returned in compact form. Requires the portfolios:read scope."""
    path: GetCustomFieldSettingsForPortfolioRequestPath
    query: GetCustomFieldSettingsForPortfolioRequestQuery | None = None

# Operation: list_goal_custom_field_settings
class GetCustomFieldSettingsForGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal whose custom field settings you want to retrieve.")
class GetCustomFieldSettingsForGoalRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of custom field settings to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetCustomFieldSettingsForGoalRequest(StrictModel):
    """Retrieves all custom field settings associated with a specific goal in compact form. Use opt_fields to request additional fields beyond the default compact representation."""
    path: GetCustomFieldSettingsForGoalRequestPath
    query: GetCustomFieldSettingsForGoalRequestQuery | None = None

# Operation: list_team_custom_field_settings
class GetCustomFieldSettingsForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier for the team whose custom field settings you want to retrieve.")
class GetCustomFieldSettingsForTeamRequest(StrictModel):
    """Retrieves all custom field settings associated with a specific team, returned in compact form. Use opt_fields to request additional field data beyond the default compact representation."""
    path: GetCustomFieldSettingsForTeamRequestPath

# Operation: create_custom_field
class CreateCustomFieldRequestBody(StrictModel):
    """The custom field object to create."""
    data: CustomFieldCreateRequest | None = Field(default=None, description="The request body containing the custom field definition, including required properties such as workspace, name, and type (one of: text, enum, multi_enum, number, date, or people).")
class CreateCustomFieldRequest(StrictModel):
    """Creates a new custom field within a specified workspace, supporting types such as text, enum, multi_enum, number, date, or people. The field name must be unique within the workspace and cannot conflict with existing task property names."""
    body: CreateCustomFieldRequestBody | None = None

# Operation: get_custom_field
class GetCustomFieldRequestPath(StrictModel):
    custom_field_gid: str = Field(default=..., description="The globally unique identifier of the custom field to retrieve.")
class GetCustomFieldRequest(StrictModel):
    """Retrieves the complete metadata definition for a specific custom field, including type-specific properties such as enum options, validation rules, and display settings."""
    path: GetCustomFieldRequestPath

# Operation: update_custom_field
class UpdateCustomFieldRequestPath(StrictModel):
    custom_field_gid: str = Field(default=..., description="The globally unique identifier of the custom field to update.")
class UpdateCustomFieldRequestBody(StrictModel):
    """The custom field object with all updated properties."""
    data: CustomFieldRequest | None = Field(default=None, description="An object containing only the custom field properties you wish to update; omitted fields retain their current values.")
class UpdateCustomFieldRequest(StrictModel):
    """Updates an existing custom field by its unique identifier, applying only the fields provided in the request body while leaving unspecified fields unchanged. Note that a custom field's type cannot be changed, enum options must be managed separately, and locked fields can only be updated by the user who locked them."""
    path: UpdateCustomFieldRequestPath
    body: UpdateCustomFieldRequestBody | None = None

# Operation: delete_custom_field
class DeleteCustomFieldRequestPath(StrictModel):
    custom_field_gid: str = Field(default=..., description="The globally unique identifier of the custom field to delete.")
class DeleteCustomFieldRequest(StrictModel):
    """Permanently deletes an existing custom field by its unique identifier. Note that locked custom fields can only be deleted by the user who originally locked the field."""
    path: DeleteCustomFieldRequestPath

# Operation: list_workspace_custom_fields
class GetCustomFieldsForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization whose custom fields you want to retrieve.")
class GetCustomFieldsForWorkspaceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of custom field records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetCustomFieldsForWorkspaceRequest(StrictModel):
    """Retrieves a list of all custom fields defined in a given workspace or organization. Returns compact representations suitable for discovery and reference."""
    path: GetCustomFieldsForWorkspaceRequestPath
    query: GetCustomFieldsForWorkspaceRequestQuery | None = None

# Operation: create_enum_option
class CreateEnumOptionForCustomFieldRequestPath(StrictModel):
    custom_field_gid: str = Field(default=..., description="The globally unique identifier of the custom field to which the new enum option will be added.")
class CreateEnumOptionForCustomFieldRequestBody(StrictModel):
    """The enum option object to create."""
    data: EnumOptionRequest | None = Field(default=None, description="The payload defining the new enum option's properties, such as its name, color, and enabled state.")
class CreateEnumOptionForCustomFieldRequest(StrictModel):
    """Creates a new enum option and appends it to the specified custom field's list of selectable values. A custom field supports up to 500 enum options (including disabled ones); locked fields can only be modified by the user who locked them."""
    path: CreateEnumOptionForCustomFieldRequestPath
    body: CreateEnumOptionForCustomFieldRequestBody | None = None

# Operation: reorder_enum_option
class InsertEnumOptionForCustomFieldRequestPath(StrictModel):
    custom_field_gid: str = Field(default=..., description="The globally unique identifier of the custom field whose enum options are being reordered.")
class InsertEnumOptionForCustomFieldRequestBodyData(StrictModel):
    enum_option: str | None = Field(default=None, validation_alias="enum_option", serialization_alias="enum_option", description="The unique identifier of the enum option to move to a new position within the custom field.")
    before_enum_option: str | None = Field(default=None, validation_alias="before_enum_option", serialization_alias="before_enum_option", description="The unique identifier of an existing enum option in this custom field; the target enum option will be inserted immediately before it. Mutually exclusive with after_enum_option.")
    after_enum_option: str | None = Field(default=None, validation_alias="after_enum_option", serialization_alias="after_enum_option", description="The unique identifier of an existing enum option in this custom field; the target enum option will be inserted immediately after it. Mutually exclusive with before_enum_option.")
class InsertEnumOptionForCustomFieldRequestBody(StrictModel):
    """The enum option object to create."""
    data: InsertEnumOptionForCustomFieldRequestBodyData | None = None
class InsertEnumOptionForCustomFieldRequest(StrictModel):
    """Repositions a specific enum option within a custom field's ordered list by placing it before or after another existing enum option. Locked custom fields can only be reordered by the user who locked the field."""
    path: InsertEnumOptionForCustomFieldRequestPath
    body: InsertEnumOptionForCustomFieldRequestBody | None = None

# Operation: update_enum_option
class UpdateEnumOptionRequestPath(StrictModel):
    enum_option_gid: str = Field(default=..., description="The globally unique identifier of the enum option to update.")
class UpdateEnumOptionRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name of the enum option as it appears in the custom field.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Controls whether this enum option is selectable by users on the custom field. At least one option must remain enabled on the field.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The color associated with the enum option for visual identification. Defaults to none if not specified.")
class UpdateEnumOptionRequestBody(StrictModel):
    """The enum option object to update"""
    data: UpdateEnumOptionRequestBodyData | None = None
class UpdateEnumOptionRequest(StrictModel):
    """Updates an existing enum option on a custom field, allowing changes to its name, color, or enabled state. Locked custom fields can only be modified by the user who locked them, and at least one enabled enum option must remain on the field."""
    path: UpdateEnumOptionRequestPath
    body: UpdateEnumOptionRequestBody | None = None

# Operation: list_custom_types
class GetCustomTypesRequestQuery(StrictModel):
    project: str = Field(default=..., description="The globally unique identifier of the project whose associated custom types you want to retrieve.")
    limit: int | None = Field(default=None, description="The number of custom types to return per page. Accepts values between 1 and 100 inclusive.", ge=1, le=100)
class GetCustomTypesRequest(StrictModel):
    """Retrieves all custom types associated with a specified project. Use `opt_fields` to request additional fields beyond the default compact representation."""
    query: GetCustomTypesRequestQuery

# Operation: get_custom_type
class GetCustomTypeRequestPath(StrictModel):
    custom_type_gid: str = Field(default=..., description="The globally unique identifier of the custom type to retrieve.")
class GetCustomTypeRequest(StrictModel):
    """Retrieves the complete record for a single custom type by its unique identifier. Use this to inspect the full definition and configuration of a specific custom type."""
    path: GetCustomTypeRequestPath

# Operation: list_resource_events
class GetEventsRequestQuery(StrictModel):
    resource: str = Field(default=..., description="The unique ID of the resource (task, project, or goal) whose events you want to retrieve.")
    sync: str | None = Field(default=None, description="A sync token from a previous response used to fetch only new events since that point in time. Omit on the first request to receive a fresh sync token; if the token has expired (HTTP 412), use the new token returned in that error response to resume.")
class GetEventsRequest(StrictModel):
    """Retrieves all events that have occurred on a resource (task, project, or goal) since a given sync token was created. Returns up to 100 events per request, with a new sync token to paginate forward through additional events."""
    query: GetEventsRequestQuery

# Operation: export_graph
class CreateGraphExportRequestBodyData(StrictModel):
    parent: str | None = Field(default=None, validation_alias="parent", serialization_alias="parent", description="The globally unique ID of the parent object (goal, project, portfolio, or team) whose graph data should be exported.")
class CreateGraphExportRequestBody(StrictModel):
    """A JSON payload specifying the parent object to export."""
    data: CreateGraphExportRequestBodyData | None = None
class CreateGraphExportRequest(StrictModel):
    """Initiates an asynchronous graph export job for a goal, team, portfolio, or project. Use the jobs endpoint to monitor progress; exports exceeding 1,000 tasks are cached for 4 hours, with subsequent requests returning the cached result."""
    body: CreateGraphExportRequestBody | None = None

# Operation: create_resource_export
class CreateResourceExportRequestBodyData(StrictModel):
    workspace: str | None = Field(default=None, validation_alias="workspace", serialization_alias="workspace", description="The GID of the workspace whose resources will be exported. Only one in-progress export is permitted per workspace at a time.")
    export_request_parameters: list[ResourceExportRequestParameter] | None = Field(default=None, validation_alias="export_request_parameters", serialization_alias="export_request_parameters", description="An array of export request parameter objects, where each object specifies a resource GID and its associated export options (such as filters and fields). Providing multiple entries for the same resource type achieves a disjunctive filter but may produce duplicate results. Order is not significant.")
class CreateResourceExportRequestBody(StrictModel):
    """A JSON payload specifying the resources to export, including filters to apply and fields to be exported."""
    data: CreateResourceExportRequestBodyData | None = None
class CreateResourceExportRequest(StrictModel):
    """Initiates an asynchronous bulk export of workspace resources (tasks, teams, or messages) in gzip-compressed JSON Lines format. Export progress can be monitored via the jobs endpoint, and the resulting file is accessible for 30 days after completion."""
    body: CreateResourceExportRequestBody | None = None

# Operation: get_goal_relationship
class GetGoalRelationshipRequestPath(StrictModel):
    goal_relationship_gid: str = Field(default=..., description="The unique identifier of the goal relationship to retrieve. This ID is returned when a goal relationship is created or listed.")
class GetGoalRelationshipRequest(StrictModel):
    """Retrieves the complete record for a single goal relationship, including details about how two goals are linked. Use this to inspect the nature and status of a specific goal-to-goal connection."""
    path: GetGoalRelationshipRequestPath

# Operation: update_goal_relationship
class UpdateGoalRelationshipRequestPath(StrictModel):
    goal_relationship_gid: str = Field(default=..., description="The globally unique identifier of the goal relationship to update.")
class UpdateGoalRelationshipRequestBody(StrictModel):
    """The updated fields for the goal relationship."""
    data: GoalRelationshipRequest | None = Field(default=None, description="The fields to update on the goal relationship; only provided fields will be modified, all others remain unchanged.")
class UpdateGoalRelationshipRequest(StrictModel):
    """Updates an existing goal relationship by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated goal relationship record."""
    path: UpdateGoalRelationshipRequestPath
    body: UpdateGoalRelationshipRequestBody | None = None

# Operation: list_goal_relationships
class GetGoalRelationshipsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of goal relationship records to return per page, between 1 and 100.", ge=1, le=100)
    supported_goal: str = Field(default=..., description="The globally unique identifier of the supported goal whose relationships you want to retrieve. This is a required field that scopes the results to a specific goal.")
    resource_subtype: str | None = Field(default=None, description="Filters the returned goal relationships to only those matching the specified resource subtype, such as a subgoal relationship.")
class GetGoalRelationshipsRequest(StrictModel):
    """Retrieves compact goal relationship records for a specified supported goal, allowing you to explore how goals are connected within your workspace."""
    query: GetGoalRelationshipsRequestQuery

# Operation: add_goal_supporting_relationship
class AddSupportingRelationshipRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The unique identifier of the parent goal to which the supporting resource will be linked.")
class AddSupportingRelationshipRequestBodyData(StrictModel):
    supporting_resource: str = Field(default=..., validation_alias="supporting_resource", serialization_alias="supporting_resource", description="The unique identifier of the resource to add as a supporting relationship to the parent goal. Must be the GID of a goal, project, task, or portfolio.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The GID of an existing subgoal of the parent goal; the new subgoal will be inserted immediately before it. Cannot be used together with `insert_after`. Only supported when adding a subgoal.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The GID of an existing subgoal of the parent goal; the new subgoal will be inserted immediately after it. Cannot be used together with `insert_before`. Only supported when adding a subgoal.")
    contribution_weight: float | None = Field(default=None, validation_alias="contribution_weight", serialization_alias="contribution_weight", description="A weight between 0 and 1 (inclusive) that determines how much the supporting resource's progress contributes to the parent goal's overall progress. Must be greater than 0 for the supporting resource to count toward automatically calculated parent goal metrics. Defaults to 0.")
class AddSupportingRelationshipRequestBody(StrictModel):
    """The supporting resource to be added to the goal"""
    data: AddSupportingRelationshipRequestBodyData
class AddSupportingRelationshipRequest(StrictModel):
    """Links a supporting resource (goal, project, task, or portfolio) to a parent goal, establishing a progress relationship between them. Returns the newly created goal relationship record."""
    path: AddSupportingRelationshipRequestPath
    body: AddSupportingRelationshipRequestBody

# Operation: remove_goal_supporting_relationship
class RemoveSupportingRelationshipRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The unique identifier of the parent goal from which the supporting relationship will be removed.")
class RemoveSupportingRelationshipRequestBodyData(StrictModel):
    supporting_resource: str = Field(default=..., validation_alias="supporting_resource", serialization_alias="supporting_resource", description="The unique identifier of the supporting resource to unlink from the parent goal; must be the identifier of a goal, project, task, or portfolio.")
class RemoveSupportingRelationshipRequestBody(StrictModel):
    """The supporting resource to be removed from the goal"""
    data: RemoveSupportingRelationshipRequestBodyData
class RemoveSupportingRelationshipRequest(StrictModel):
    """Removes a supporting relationship between a child resource and a parent goal, unlinking a goal, project, task, or portfolio that was previously set as a supporting resource."""
    path: RemoveSupportingRelationshipRequestPath
    body: RemoveSupportingRelationshipRequestBody

# Operation: get_goal
class GetGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal to retrieve.")
class GetGoalRequest(StrictModel):
    """Retrieves the complete record for a single goal, including all associated fields and metadata. Requires the goals:read scope, with additional time_periods:read scope needed to access the time_period field."""
    path: GetGoalRequestPath

# Operation: update_goal
class UpdateGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal to update.")
class UpdateGoalRequestBody(StrictModel):
    """The updated fields for the goal."""
    data: GoalUpdateRequest | None = Field(default=None, description="An object containing the goal fields to update; only the fields included will be modified, all unspecified fields retain their current values.")
class UpdateGoalRequest(StrictModel):
    """Updates an existing goal by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated goal record."""
    path: UpdateGoalRequestPath
    body: UpdateGoalRequestBody | None = None

# Operation: delete_goal
class DeleteGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal to delete.")
class DeleteGoalRequest(StrictModel):
    """Permanently deletes an existing goal by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteGoalRequestPath

# Operation: list_goals
class GetGoalsRequestQuery(StrictModel):
    portfolio: str | None = Field(default=None, description="The globally unique identifier of a portfolio to filter goals that support it.")
    project: str | None = Field(default=None, description="The globally unique identifier of a project to filter goals that support it.")
    task: str | None = Field(default=None, description="The globally unique identifier of a task to filter goals that support it.")
    is_workspace_level: bool | None = Field(default=None, description="When true, filters results to only workspace-level goals. Must be used together with the workspace parameter.")
    team: str | None = Field(default=None, description="The globally unique identifier of a team to filter goals belonging to that team.")
    workspace: str | None = Field(default=None, description="The globally unique identifier of a workspace to filter goals within that workspace.")
    time_periods: list[str] | None = Field(default=None, description="A comma-separated list of globally unique time period identifiers to filter goals associated with those periods. Order is not significant.")
class GetGoalsRequest(StrictModel):
    """Retrieves a list of compact goal records, optionally filtered by workspace, team, portfolio, project, task, or time period. Requires the goals:read scope."""
    query: GetGoalsRequestQuery | None = None

# Operation: create_goal
class CreateGoalRequestBody(StrictModel):
    """The goal to create."""
    data: GoalRequest | None = Field(default=None, description="The goal object containing the details for the new goal, such as name, owner, due date, and associated workspace or team.")
class CreateGoalRequest(StrictModel):
    """Creates a new goal within a specified workspace or team. Returns the full record of the newly created goal."""
    body: CreateGoalRequestBody | None = None

# Operation: set_goal_metric
class CreateGoalMetricRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal to which the metric will be attached.")
class CreateGoalMetricRequestBodyData(StrictModel):
    precision: int | None = Field(default=None, validation_alias="precision", serialization_alias="precision", description="Only applicable for metrics of type Number. Specifies the number of decimal places to display, where 0 means integer values, 1 rounds to the nearest tenth, and so on. Must be between 0 and 6 inclusive. Note: for percentage format, the precision applies to the raw decimal value before conversion to a percentage display.")
    unit: Literal["none", "currency", "percentage"] | None = Field(default=None, validation_alias="unit", serialization_alias="unit", description="The unit of measurement for the goal metric. Use 'currency' to enable currency formatting, 'percentage' for percentage-based progress, or 'none' for a unitless number.")
    currency_code: str | None = Field(default=None, validation_alias="currency_code", serialization_alias="currency_code", description="The ISO 4217 currency code used to format the metric value. Only applicable when the unit is set to 'currency'; otherwise this field is null.")
    initial_number_value: float | None = Field(default=None, validation_alias="initial_number_value", serialization_alias="initial_number_value", description="The starting value of the numeric goal metric, representing the baseline from which progress is measured.")
    target_number_value: float | None = Field(default=None, validation_alias="target_number_value", serialization_alias="target_number_value", description="The target value the numeric goal metric must reach to be considered complete. Must differ from the initial value.")
    current_number_value: float | None = Field(default=None, validation_alias="current_number_value", serialization_alias="current_number_value", description="The current value of the numeric goal metric, reflecting progress made so far between the initial and target values.")
    progress_source: Literal["manual", "subgoal_progress", "project_task_completion", "project_milestone_completion", "task_completion", "external"] | None = Field(default=None, validation_alias="progress_source", serialization_alias="progress_source", description="Defines how the goal's progress value is calculated. Choose 'manual' for user-entered progress, one of the automatic options to derive progress from subgoals, projects, or tasks, or 'external' for integration-managed progress from a source such as Salesforce.")
    is_custom_weight: bool | None = Field(default=None, validation_alias="is_custom_weight", serialization_alias="is_custom_weight", description="Only applicable when progress_source is 'subgoal_progress', 'project_task_completion', 'project_milestone_completion', or 'task_completion'. When true, each supporting object's custom weight is used in the progress calculation; when false, all supporting objects are treated as equally weighted.")
class CreateGoalMetricRequestBody(StrictModel):
    """The goal metric to create."""
    data: CreateGoalMetricRequestBodyData | None = None
class CreateGoalMetricRequest(StrictModel):
    """Creates and attaches a progress metric to a specified goal, defining how goal completion is measured and tracked. If a metric already exists on the goal, it will be replaced entirely."""
    path: CreateGoalMetricRequestPath
    body: CreateGoalMetricRequestBody | None = None

# Operation: update_goal_metric_value
class UpdateGoalMetricRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal whose metric value you want to update.")
class UpdateGoalMetricRequestBodyData(StrictModel):
    current_number_value: float | None = Field(default=None, validation_alias="current_number_value", serialization_alias="current_number_value", description="The new current value to record for the goal's numeric metric, reflecting the latest progress toward the goal's target.")
class UpdateGoalMetricRequestBody(StrictModel):
    """The updated fields for the goal metric."""
    data: UpdateGoalMetricRequestBodyData | None = None
class UpdateGoalMetricRequest(StrictModel):
    """Updates the current numeric value of an existing goal metric, allowing progress tracking against a defined target. Requires the goal to already have a numeric metric configured; returns the complete updated goal metric record."""
    path: UpdateGoalMetricRequestPath
    body: UpdateGoalMetricRequestBody | None = None

# Operation: add_goal_followers
class AddFollowersRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The unique identifier of the goal to which followers will be added.")
class AddFollowersRequestBodyData(StrictModel):
    followers: list[str] = Field(default=..., validation_alias="followers", serialization_alias="followers", description="A list of users to add as followers to the goal. Each item can be the string 'me' to reference the authenticated user, a user's email address, or a user's GID. Order is not significant.")
class AddFollowersRequestBody(StrictModel):
    """The followers to be added as collaborators"""
    data: AddFollowersRequestBodyData
class AddFollowersRequest(StrictModel):
    """Adds one or more followers (collaborators) to a specified goal. Returns the complete updated goal record reflecting the new followers."""
    path: AddFollowersRequestPath
    body: AddFollowersRequestBody

# Operation: remove_goal_followers
class RemoveFollowersRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal from which followers will be removed.")
class RemoveFollowersRequestBodyData(StrictModel):
    followers: list[str] = Field(default=..., validation_alias="followers", serialization_alias="followers", description="A list of users to remove as followers from the goal. Each item can be the string 'me' to reference the authenticated user, a user's email address, or a user's globally unique identifier (gid). Order is not significant.")
class RemoveFollowersRequestBody(StrictModel):
    """The followers to be removed as collaborators"""
    data: RemoveFollowersRequestBodyData
class RemoveFollowersRequest(StrictModel):
    """Removes one or more followers (collaborators) from a specified goal. Returns the complete updated goal record reflecting the removed followers."""
    path: RemoveFollowersRequestPath
    body: RemoveFollowersRequestBody

# Operation: list_parent_goals
class GetParentGoalsForGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal whose parent goals you want to retrieve.")
class GetParentGoalsForGoalRequest(StrictModel):
    """Retrieves a compact list of all parent goals associated with a specified goal. Useful for traversing goal hierarchies and understanding how a goal rolls up into broader objectives."""
    path: GetParentGoalsForGoalRequestPath

# Operation: add_custom_field_to_goal
class AddCustomFieldSettingForGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal to which the custom field setting will be added.")
class AddCustomFieldSettingForGoalRequestBodyData(StrictModel):
    custom_field: str | CustomFieldCreateRequest = Field(default=..., validation_alias="custom_field", serialization_alias="custom_field", description="The globally unique identifier of the custom field to associate with the goal.")
    is_important: bool | None = Field(default=None, validation_alias="is_important", serialization_alias="is_important", description="When set to true, marks this custom field as important for the goal, causing it to be prominently displayed in list views of the goal.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The GID of an existing custom field setting on this goal before which the new custom field setting will be inserted to control display order. Cannot be used together with insert_after.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The GID of an existing custom field setting on this goal after which the new custom field setting will be inserted to control display order. Cannot be used together with insert_before.")
class AddCustomFieldSettingForGoalRequestBody(StrictModel):
    """Information about the custom field setting."""
    data: AddCustomFieldSettingForGoalRequestBodyData
class AddCustomFieldSettingForGoalRequest(StrictModel):
    """Associates a custom field with a goal by creating a custom field setting, allowing the field to appear and be tracked on the specified goal."""
    path: AddCustomFieldSettingForGoalRequestPath
    body: AddCustomFieldSettingForGoalRequestBody

# Operation: remove_custom_field_from_goal
class RemoveCustomFieldSettingForGoalRequestPath(StrictModel):
    goal_gid: str = Field(default=..., description="The globally unique identifier of the goal from which the custom field setting will be removed.")
class RemoveCustomFieldSettingForGoalRequestBodyData(StrictModel):
    custom_field: str = Field(default=..., validation_alias="custom_field", serialization_alias="custom_field", description="The globally unique identifier of the custom field to remove from the goal.")
class RemoveCustomFieldSettingForGoalRequestBody(StrictModel):
    """Information about the custom field setting being removed."""
    data: RemoveCustomFieldSettingForGoalRequestBodyData
class RemoveCustomFieldSettingForGoalRequest(StrictModel):
    """Removes a custom field setting from a specified goal, detaching the custom field and its associated data from the goal. Requires the goals:write scope."""
    path: RemoveCustomFieldSettingForGoalRequestPath
    body: RemoveCustomFieldSettingForGoalRequestBody

# Operation: get_job
class GetJobRequestPath(StrictModel):
    job_gid: str = Field(default=..., description="The globally unique identifier of the job to retrieve.")
class GetJobRequest(StrictModel):
    """Retrieves the full record for a specific asynchronous job by its unique identifier. Useful for polling job status and accessing output resources such as new tasks, projects, portfolios, or templates created by the job."""
    path: GetJobRequestPath

# Operation: list_memberships
class GetMembershipsRequestQuery(StrictModel):
    parent: str | None = Field(default=None, description="The globally unique identifier of the parent resource to retrieve memberships for; accepted parent types are goal, project, portfolio, custom_type, or custom_field. Optional when both member and resource_subtype are provided together.")
    member: str | None = Field(default=None, description="The globally unique identifier of a user or team to filter memberships by; when combined with resource_subtype and no parent is specified, returns all memberships of that subtype for this member.")
    resource_subtype: Literal["project_membership"] | None = Field(default=None, description="Specifies the membership subtype to return; required when parent is absent, and must be paired with a member GID to retrieve all memberships of that type for the given member.")
class GetMembershipsRequest(StrictModel):
    """Retrieves compact membership records for a given parent resource (goal, project, portfolio, custom type, or custom field), optionally filtered by a specific member. Alternatively, when no parent is specified, returns all memberships of a given subtype for a specific member by combining the member and resource_subtype parameters."""
    query: GetMembershipsRequestQuery | None = None

# Operation: create_membership
class CreateMembershipRequestBody(StrictModel):
    """The updated fields for the membership."""
    data: CreateMembershipRequest | None = Field(default=None, description="The membership details including the resource to join (goal, project, portfolio, custom type, or custom field) and the member to add (Team or User).")
class CreateMembershipRequest(StrictModel):
    """Creates a new membership linking a Team or User to a goal, project, portfolio, custom type, or custom field. Returns the full record of the newly created membership."""
    body: CreateMembershipRequestBody | None = None

# Operation: get_membership
class GetMembershipRequestPath(StrictModel):
    membership_gid: str = Field(default=..., description="The globally unique identifier of the membership record to retrieve, applicable across all membership types (project, goal, portfolio, custom type, or custom field).")
class GetMembershipRequest(StrictModel):
    """Retrieves a single membership record by its unique identifier, returning details for any supported membership type including project, goal, portfolio, custom type, or custom field memberships."""
    path: GetMembershipRequestPath

# Operation: update_membership
class UpdateMembershipRequestPath(StrictModel):
    membership_gid: str = Field(default=..., description="The globally unique identifier of the membership to update.")
class UpdateMembershipRequestBodyData(StrictModel):
    access_level: str | None = Field(default=None, validation_alias="access_level", serialization_alias="access_level", description="The access level to assign to the member. Valid values vary by resource type: goals support 'viewer', 'commenter', 'editor', or 'admin'; projects support 'admin', 'editor', or 'commenter'; portfolios support 'admin', 'editor', or 'viewer'; custom fields support 'admin', 'editor', or 'user'.")
class UpdateMembershipRequestBody(StrictModel):
    """The membership to update."""
    data: UpdateMembershipRequestBodyData | None = None
class UpdateMembershipRequest(StrictModel):
    """Updates an existing membership by replacing only the fields provided in the request body, leaving all other fields unchanged. Supports memberships on goals, projects, portfolios, custom types, and custom fields."""
    path: UpdateMembershipRequestPath
    body: UpdateMembershipRequestBody | None = None

# Operation: delete_membership
class DeleteMembershipRequestPath(StrictModel):
    membership_gid: str = Field(default=..., description="The globally unique identifier of the membership to delete.")
class DeleteMembershipRequest(StrictModel):
    """Permanently removes an existing membership from a goal, project, portfolio, custom type, or custom field. Returns an empty data record upon successful deletion."""
    path: DeleteMembershipRequestPath

# Operation: create_organization_export
class CreateOrganizationExportRequestBodyData(StrictModel):
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="The globally unique identifier of the workspace or organization to export.")
class CreateOrganizationExportRequestBody(StrictModel):
    """The organization to export."""
    data: CreateOrganizationExportRequestBodyData | None = None
class CreateOrganizationExportRequest(StrictModel):
    """Initiates an export request for an entire Asana organization. Asana processes and completes the export asynchronously after the request is submitted."""
    body: CreateOrganizationExportRequestBody | None = None

# Operation: get_organization_export
class GetOrganizationExportRequestPath(StrictModel):
    organization_export_gid: str = Field(default=..., description="The globally unique identifier of the organization export request to retrieve.")
class GetOrganizationExportRequest(StrictModel):
    """Retrieves the current status and details of a previously requested organization export. Use this to check export progress or access the resulting download URL once complete."""
    path: GetOrganizationExportRequestPath

# Operation: list_portfolio_memberships
class GetPortfolioMembershipsRequestQuery(StrictModel):
    portfolio: str | None = Field(default=None, description="The unique identifier of the portfolio to filter memberships by. Required unless filtering by workspace and user.")
    workspace: str | None = Field(default=None, description="The unique identifier of the workspace to filter memberships by. Must be combined with a user identifier when specified.")
    user: str | None = Field(default=None, description="Identifies the user whose memberships to filter by. Accepts the string 'me' for the current user, a user's email address, or a user's global ID (gid).")
    limit: int | None = Field(default=None, description="The number of membership records to return per page. Accepts values between 1 and 100 inclusive.", ge=1, le=100)
class GetPortfolioMembershipsRequest(StrictModel):
    """Retrieves a list of portfolio memberships in compact representation. You must provide either a portfolio ID, a portfolio and user combination, or a workspace and user combination to filter results."""
    query: GetPortfolioMembershipsRequestQuery | None = None

# Operation: get_portfolio_membership
class GetPortfolioMembershipRequestPath(StrictModel):
    portfolio_membership_gid: str = Field(default=..., description="The unique identifier (GID) of the portfolio membership to retrieve.")
class GetPortfolioMembershipRequest(StrictModel):
    """Retrieves the complete details of a single portfolio membership record. Use this to inspect a specific user's membership relationship within a portfolio."""
    path: GetPortfolioMembershipRequestPath

# Operation: list_portfolio_memberships_for_portfolio
class GetPortfolioMembershipsForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio whose memberships you want to retrieve.")
class GetPortfolioMembershipsForPortfolioRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="Filters memberships to a specific user. Accepts the string 'me' for the authenticated user, a user's email address, or a user's globally unique identifier.")
    limit: int | None = Field(default=None, description="The number of membership records to return per page. Must be between 1 and 100 inclusive.", ge=1, le=100)
class GetPortfolioMembershipsForPortfolioRequest(StrictModel):
    """Retrieves all membership records for a specified portfolio, returning compact representations of each member. Optionally filter results by a specific user."""
    path: GetPortfolioMembershipsForPortfolioRequestPath
    query: GetPortfolioMembershipsForPortfolioRequestQuery | None = None

# Operation: list_portfolios
class GetPortfoliosRequestQuery(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier of the workspace or organization used to filter the returned portfolios.")
    owner: str | None = Field(default=None, description="The unique identifier of the user whose portfolios should be returned. Standard API users are limited to their own portfolios; Service Accounts may specify any user or omit this parameter to retrieve all portfolios in the workspace.")
class GetPortfoliosRequest(StrictModel):
    """Retrieves a compact list of portfolios owned by the current API user within a specified workspace. Service Accounts can optionally filter by owner or retrieve all portfolios across the workspace."""
    query: GetPortfoliosRequestQuery

# Operation: create_portfolio
class CreatePortfolioRequestBody(StrictModel):
    """The portfolio to create."""
    data: PortfolioRequest | None = Field(default=None, description="Request body containing the portfolio details, including the name and workspace to create the portfolio in.")
class CreatePortfolioRequest(StrictModel):
    """Creates a new portfolio in a specified workspace with a given name. Note that portfolios created via the API will not include default UI state (such as the 'Priority' custom field) to allow integrations to define their own initial configuration."""
    body: CreatePortfolioRequestBody | None = None

# Operation: get_portfolio
class GetPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to retrieve.")
class GetPortfolioRequest(StrictModel):
    """Retrieves the complete record for a single portfolio, including all associated metadata. Requires the portfolios:read scope."""
    path: GetPortfolioRequestPath

# Operation: update_portfolio
class UpdatePortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to update.")
class UpdatePortfolioRequestBody(StrictModel):
    """The updated fields for the portfolio."""
    data: PortfolioUpdateRequest | None = Field(default=None, description="An object containing the portfolio fields to update; only the fields included will be modified, all unspecified fields retain their current values.")
class UpdatePortfolioRequest(StrictModel):
    """Updates an existing portfolio by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated portfolio record."""
    path: UpdatePortfolioRequestPath
    body: UpdatePortfolioRequestBody | None = None

# Operation: delete_portfolio
class DeletePortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to delete.")
class DeletePortfolioRequest(StrictModel):
    """Permanently deletes an existing portfolio by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeletePortfolioRequestPath

# Operation: list_portfolio_items
class GetItemsForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio whose items you want to retrieve.")
class GetItemsForPortfolioRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of items to return per page, allowing pagination through large portfolios. Must be between 1 and 100.", ge=1, le=100)
class GetItemsForPortfolioRequest(StrictModel):
    """Retrieves a paginated list of items within a specified portfolio in compact form. Useful for inspecting the contents of a portfolio, such as projects or other resources it contains."""
    path: GetItemsForPortfolioRequestPath
    query: GetItemsForPortfolioRequestQuery | None = None

# Operation: add_portfolio_item
class AddItemForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to which the item will be added.")
class AddItemForPortfolioRequestBodyData(StrictModel):
    item: str = Field(default=..., validation_alias="item", serialization_alias="item", description="The globally unique identifier of the project or item to add to the portfolio.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The ID of an existing portfolio item before which the new item will be inserted. Cannot be used together with insert_after.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The ID of an existing portfolio item after which the new item will be inserted. Cannot be used together with insert_before.")
class AddItemForPortfolioRequestBody(StrictModel):
    """Information about the item being inserted."""
    data: AddItemForPortfolioRequestBodyData
class AddItemForPortfolioRequest(StrictModel):
    """Adds a project or item to a specified portfolio, optionally controlling its position relative to an existing item. Returns an empty data block on success."""
    path: AddItemForPortfolioRequestPath
    body: AddItemForPortfolioRequestBody

# Operation: remove_portfolio_item
class RemoveItemForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio from which the item will be removed.")
class RemoveItemForPortfolioRequestBodyData(StrictModel):
    item: str = Field(default=..., validation_alias="item", serialization_alias="item", description="The globally unique identifier of the item to remove from the portfolio.")
class RemoveItemForPortfolioRequestBody(StrictModel):
    """Information about the item being removed."""
    data: RemoveItemForPortfolioRequestBodyData
class RemoveItemForPortfolioRequest(StrictModel):
    """Removes a specific item from a portfolio, unlinking it from the portfolio's collection. Returns an empty data block upon success."""
    path: RemoveItemForPortfolioRequestPath
    body: RemoveItemForPortfolioRequestBody

# Operation: add_custom_field_to_portfolio
class AddCustomFieldSettingForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to which the custom field setting will be added.")
class AddCustomFieldSettingForPortfolioRequestBodyData(StrictModel):
    custom_field: str | CustomFieldCreateRequest = Field(default=..., validation_alias="custom_field", serialization_alias="custom_field", description="The globally unique identifier (GID) of the custom field to associate with the portfolio.")
    is_important: bool | None = Field(default=None, validation_alias="is_important", serialization_alias="is_important", description="When set to true, marks this custom field as important for the portfolio, causing it to be prominently displayed in list views of the portfolio's items.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The GID of an existing custom field setting on this portfolio before which the new custom field setting will be inserted to control ordering. Cannot be used together with insert_after.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The GID of an existing custom field setting on this portfolio after which the new custom field setting will be inserted to control ordering. Cannot be used together with insert_before.")
class AddCustomFieldSettingForPortfolioRequestBody(StrictModel):
    """Information about the custom field setting."""
    data: AddCustomFieldSettingForPortfolioRequestBodyData
class AddCustomFieldSettingForPortfolioRequest(StrictModel):
    """Associates a custom field with a portfolio by creating a custom field setting, allowing the field to appear and be tracked within the portfolio. Optionally controls the display prominence and ordering of the field relative to other custom field settings on the portfolio."""
    path: AddCustomFieldSettingForPortfolioRequestPath
    body: AddCustomFieldSettingForPortfolioRequestBody

# Operation: remove_portfolio_custom_field
class RemoveCustomFieldSettingForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio from which the custom field setting will be removed.")
class RemoveCustomFieldSettingForPortfolioRequestBodyData(StrictModel):
    custom_field: str = Field(default=..., validation_alias="custom_field", serialization_alias="custom_field", description="The globally unique identifier of the custom field to detach from the portfolio.")
class RemoveCustomFieldSettingForPortfolioRequestBody(StrictModel):
    """Information about the custom field setting being removed."""
    data: RemoveCustomFieldSettingForPortfolioRequestBodyData
class RemoveCustomFieldSettingForPortfolioRequest(StrictModel):
    """Removes a custom field setting from a portfolio, detaching it so the field no longer appears or collects data for that portfolio. Requires portfolios:write scope."""
    path: RemoveCustomFieldSettingForPortfolioRequestPath
    body: RemoveCustomFieldSettingForPortfolioRequestBody

# Operation: add_portfolio_members
class AddMembersForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to which members will be added.")
class AddMembersForPortfolioRequestBodyData(StrictModel):
    members: str = Field(default=..., validation_alias="members", serialization_alias="members", description="A comma-separated list of user identifiers to add as portfolio members; each identifier can be the string 'me', a user's email address, or a user's globally unique identifier (gid). Order is not significant.")
class AddMembersForPortfolioRequestBody(StrictModel):
    """Information about the members being added."""
    data: AddMembersForPortfolioRequestBodyData
class AddMembersForPortfolioRequest(StrictModel):
    """Adds one or more users as members of the specified portfolio, granting them access to view and collaborate on it. Returns the updated portfolio record."""
    path: AddMembersForPortfolioRequestPath
    body: AddMembersForPortfolioRequestBody

# Operation: remove_portfolio_members
class RemoveMembersForPortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio from which members will be removed.")
class RemoveMembersForPortfolioRequestBodyData(StrictModel):
    members: str = Field(default=..., validation_alias="members", serialization_alias="members", description="A comma-separated list of user identifiers to remove from the portfolio. Each identifier can be the string 'me' (current user), a user's email address, or a user's globally unique identifier (gid).")
class RemoveMembersForPortfolioRequestBody(StrictModel):
    """Information about the members being removed."""
    data: RemoveMembersForPortfolioRequestBodyData
class RemoveMembersForPortfolioRequest(StrictModel):
    """Removes one or more users from the membership list of a specified portfolio. Returns the updated portfolio record reflecting the changes."""
    path: RemoveMembersForPortfolioRequestPath
    body: RemoveMembersForPortfolioRequestBody

# Operation: duplicate_portfolio
class DuplicatePortfolioRequestPath(StrictModel):
    portfolio_gid: str = Field(default=..., description="The globally unique identifier of the portfolio to duplicate.")
class DuplicatePortfolioRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name to assign to the newly duplicated portfolio.")
    include: str | None = Field(default=None, validation_alias="include", serialization_alias="include", description="A comma-separated list of optional elements to copy into the duplicate portfolio. Custom field settings and views are always included automatically. Valid values are: description, members, permissions, templates, rules, child_projects, child_portfolios.")
class DuplicatePortfolioRequestBody(StrictModel):
    """Describes the duplicate's name and the elements that will be duplicated."""
    data: DuplicatePortfolioRequestBodyData | None = None
class DuplicatePortfolioRequest(StrictModel):
    """Creates a duplicate of an existing portfolio and returns an asynchronous job that handles the duplication process. Custom field settings and views are always copied; additional elements such as members, rules, and child projects can be optionally included."""
    path: DuplicatePortfolioRequestPath
    body: DuplicatePortfolioRequestBody | None = None

# Operation: get_project_brief
class GetProjectBriefRequestPath(StrictModel):
    project_brief_gid: str = Field(default=..., description="The globally unique identifier for the project brief to retrieve.")
class GetProjectBriefRequest(StrictModel):
    """Retrieves the full record for a specific project brief, including its title, description, and associated project details."""
    path: GetProjectBriefRequestPath

# Operation: update_project_brief
class UpdateProjectBriefRequestPath(StrictModel):
    project_brief_gid: str = Field(default=..., description="The globally unique identifier of the project brief to update.")
class UpdateProjectBriefRequestBody(StrictModel):
    """The updated fields for the project brief."""
    data: ProjectBriefRequest | None = Field(default=None, description="An object containing the project brief fields to update; only the fields included will be modified, all omitted fields retain their current values.")
class UpdateProjectBriefRequest(StrictModel):
    """Updates an existing project brief by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated project brief record."""
    path: UpdateProjectBriefRequestPath
    body: UpdateProjectBriefRequestBody | None = None

# Operation: delete_project_brief
class DeleteProjectBriefRequestPath(StrictModel):
    project_brief_gid: str = Field(default=..., description="The globally unique identifier of the project brief to delete.")
class DeleteProjectBriefRequest(StrictModel):
    """Permanently deletes an existing project brief by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteProjectBriefRequestPath

# Operation: create_project_brief
class CreateProjectBriefRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project for which the brief will be created.")
class CreateProjectBriefRequestBody(StrictModel):
    """The project brief to create."""
    data: ProjectBriefRequest | None = Field(default=None, description="The request body containing the fields and values for the new project brief to be created.")
class CreateProjectBriefRequest(StrictModel):
    """Creates a new project brief for the specified project, returning the full record of the newly created brief. Project briefs provide a structured summary of project goals, context, and key information."""
    path: CreateProjectBriefRequestPath
    body: CreateProjectBriefRequestBody | None = None

# Operation: get_project_membership
class GetProjectMembershipRequestPath(StrictModel):
    project_membership_gid: str = Field(default=..., description="The unique identifier (GID) of the project membership record to retrieve.")
class GetProjectMembershipRequest(StrictModel):
    """Retrieves the complete details of a single project membership record, including the member's role and access level within the project."""
    path: GetProjectMembershipRequestPath

# Operation: list_project_memberships
class GetProjectMembershipsForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project whose memberships you want to retrieve.")
class GetProjectMembershipsForProjectRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="Filter memberships to a specific user, identified by their GID, email address, or the keyword 'me' to refer to the authenticated user.")
    limit: int | None = Field(default=None, description="The number of membership records to return per page, between 1 and 100 inclusive.", ge=1, le=100)
class GetProjectMembershipsForProjectRequest(StrictModel):
    """Retrieves all membership records for a specified project, showing which users belong to it. Optionally filter results to a single user and control pagination with a per-page limit."""
    path: GetProjectMembershipsForProjectRequestPath
    query: GetProjectMembershipsForProjectRequestQuery | None = None

# Operation: get_project_portfolio_setting
class GetProjectPortfolioSettingRequestPath(StrictModel):
    project_portfolio_setting_gid: str = Field(default=..., description="The globally unique identifier of the project portfolio setting to retrieve.")
class GetProjectPortfolioSettingRequest(StrictModel):
    """Retrieves the complete record for a single project portfolio setting. Requires the `project_portfolio_settings:read` scope."""
    path: GetProjectPortfolioSettingRequestPath

# Operation: update_project_portfolio_setting
class UpdateProjectPortfolioSettingRequestPath(StrictModel):
    project_portfolio_setting_gid: str = Field(default=..., description="The globally unique identifier of the project portfolio setting to update.")
class UpdateProjectPortfolioSettingRequestBodyData(StrictModel):
    is_access_control_inherited: bool | None = Field(default=None, validation_alias="is_access_control_inherited", serialization_alias="is_access_control_inherited", description="Controls whether portfolio members automatically inherit access to the associated project; when true, portfolio membership grants project access.")
class UpdateProjectPortfolioSettingRequestBody(StrictModel):
    """The updated fields for the project portfolio setting."""
    data: UpdateProjectPortfolioSettingRequestBodyData | None = None
class UpdateProjectPortfolioSettingRequest(StrictModel):
    """Updates an existing project portfolio setting by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated project portfolio setting record."""
    path: UpdateProjectPortfolioSettingRequestPath
    body: UpdateProjectPortfolioSettingRequestBody | None = None

# Operation: list_project_portfolio_settings
class GetProjectPortfolioSettingsForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project whose portfolio settings you want to retrieve.")
class GetProjectPortfolioSettingsForProjectRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of portfolio settings to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetProjectPortfolioSettingsForProjectRequest(StrictModel):
    """Retrieves all project portfolio settings associated with a specific project, returned as a compact representation. Requires the project_portfolio_settings:read scope."""
    path: GetProjectPortfolioSettingsForProjectRequestPath
    query: GetProjectPortfolioSettingsForProjectRequestQuery | None = None

# Operation: get_project_status
class GetProjectStatusRequestPath(StrictModel):
    project_status_gid: str = Field(default=..., description="The unique global identifier of the project status update to retrieve.")
class GetProjectStatusRequest(StrictModel):
    """Retrieves the complete record for a single project status update by its unique identifier. Note: this endpoint is deprecated; new integrations should use the `/status_updates/{status_gid}` route instead."""
    path: GetProjectStatusRequestPath

# Operation: delete_project_status
class DeleteProjectStatusRequestPath(StrictModel):
    project_status_gid: str = Field(default=..., description="The unique identifier of the project status update to delete.")
class DeleteProjectStatusRequest(StrictModel):
    """Permanently deletes a specific project status update by its unique identifier. Note: this endpoint is deprecated; new integrations should use the status updates route instead."""
    path: DeleteProjectStatusRequestPath

# Operation: list_project_statuses
class GetProjectStatusesForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="Globally unique identifier for the project.")
class GetProjectStatusesForProjectRequest(StrictModel):
    """Retrieves all compact project status update records for a given project. Note: this endpoint is deprecated — new integrations should use the `/status_updates` route instead."""
    path: GetProjectStatusesForProjectRequestPath

# Operation: create_project_status
class CreateProjectStatusForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project on which to create the status update.")
class CreateProjectStatusForProjectRequestBody(StrictModel):
    """The project status to create."""
    data: ProjectStatusBase | None = Field(default=None, description="The request body containing the status update fields, such as title, text, color, and other relevant status details.")
class CreateProjectStatusForProjectRequest(StrictModel):
    """Creates a new status update on a specified project and returns the full record of the newly created status. Note: this endpoint is deprecated; new integrations should use the `/status_updates` route instead."""
    path: CreateProjectStatusForProjectRequestPath
    body: CreateProjectStatusForProjectRequestBody | None = None

# Operation: get_project_template
class GetProjectTemplateRequestPath(StrictModel):
    project_template_gid: str = Field(default=..., description="The globally unique identifier of the project template to retrieve.")
class GetProjectTemplateRequest(StrictModel):
    """Retrieves the complete record for a single project template, including all its configuration and metadata. Requires the project_templates:read scope."""
    path: GetProjectTemplateRequestPath

# Operation: delete_project_template
class DeleteProjectTemplateRequestPath(StrictModel):
    project_template_gid: str = Field(default=..., description="The globally unique identifier of the project template to delete.")
class DeleteProjectTemplateRequest(StrictModel):
    """Permanently deletes an existing project template by its unique identifier. This action is irreversible and returns an empty data record upon success."""
    path: DeleteProjectTemplateRequestPath

# Operation: list_project_templates
class GetProjectTemplatesRequestQuery(StrictModel):
    team: str | None = Field(default=None, description="The team to filter projects on.")
    workspace: str | None = Field(default=None, description="The workspace to filter results on.")
class GetProjectTemplatesRequest(StrictModel):
    """Retrieves compact records for all project templates available in a given team or workspace. Requires the project_templates:read scope."""
    query: GetProjectTemplatesRequestQuery | None = None

# Operation: list_team_project_templates
class GetProjectTemplatesForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="Globally unique identifier for the team.")
class GetProjectTemplatesForTeamRequest(StrictModel):
    """Retrieves all project templates belonging to a specified team, returning compact template records. Useful for discovering reusable project structures available within a team."""
    path: GetProjectTemplatesForTeamRequestPath

# Operation: create_project_from_template
class InstantiateProjectRequestPath(StrictModel):
    project_template_gid: str = Field(default=..., description="The globally unique identifier of the project template to instantiate. Retrieve this value from the get project template endpoint.")
class InstantiateProjectRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name to assign to the newly created project.")
    team: str | None = Field(default=None, validation_alias="team", serialization_alias="team", description="The unique identifier of the team to assign to the new project. Applicable only when the workspace is an organization; defaults to the same team as the source project template if omitted.")
    is_strict: bool | None = Field(default=None, validation_alias="is_strict", serialization_alias="is_strict", description="Controls how unfulfilled date variables are handled. When true, the request fails with an error if any date variable is missing a value; when false, missing date variables fall back to a default such as the current date.")
    requested_dates: list[DateVariableRequest] | None = Field(default=None, validation_alias="requested_dates", serialization_alias="requested_dates", description="An array of objects mapping each template date variable (identified by its GID from the template's requested_dates array) to a specific calendar date. Required when the project template contains date variables such as a task start date.")
    requested_roles: list[RequestedRoleRequest] | None = Field(default=None, validation_alias="requested_roles", serialization_alias="requested_roles", description="An array of objects mapping each template role to a specific user identifier, used to assign team members to predefined roles defined in the project template.")
class InstantiateProjectRequestBody(StrictModel):
    """Describes the inputs used for instantiating a project, such as the resulting project's name, which team it should be created in, and values for date variables."""
    data: InstantiateProjectRequestBodyData | None = None
class InstantiateProjectRequest(StrictModel):
    """Instantiates a new project from an existing project template, returning an asynchronous job that handles the creation process. Supports mapping template date variables and roles to specific calendar dates and users at instantiation time."""
    path: InstantiateProjectRequestPath
    body: InstantiateProjectRequestBody | None = None

# Operation: list_projects
class GetProjectsRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The GID of the workspace or organization used to filter the returned projects. Providing this filter is recommended to prevent request timeouts on large domains.")
    archived: bool | None = Field(default=None, description="When provided, filters results to only include projects whose archived status matches this value. Set to true to return only archived projects, or false to return only active projects.")
class GetProjectsRequest(StrictModel):
    """Retrieves a filtered list of compact project records accessible to the authenticated user. Use the available filters to narrow results — filtering by workspace is strongly recommended to avoid timeouts on large domains."""
    query: GetProjectsRequestQuery | None = None

# Operation: create_project
class CreateProjectRequestBody(StrictModel):
    """The project to create."""
    data: ProjectRequest | None = Field(default=None, description="The request body containing project details such as name, workspace, team, and privacy settings required to create the project.")
class CreateProjectRequest(StrictModel):
    """Creates a new project within a specified workspace or organization, optionally associating it with a team. Returns the full record of the newly created project."""
    body: CreateProjectRequestBody | None = None

# Operation: get_project
class GetProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier (GID) of the project to retrieve.")
class GetProjectRequest(StrictModel):
    """Retrieves the complete record for a single project, including all available fields and metadata. Requires the `projects:read` scope; accessing the `team` field additionally requires `teams:read`."""
    path: GetProjectRequestPath

# Operation: update_project
class UpdateProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier (GID) of the project to update.")
class UpdateProjectRequestBody(StrictModel):
    """The updated fields for the project."""
    data: ProjectUpdateRequest | None = Field(default=None, description="An object containing only the project fields you wish to update; omit any fields that should remain unchanged to avoid overwriting concurrent edits. Note: updating the `team` field is deprecated — use `POST /memberships` instead to share a project with a team.")
class UpdateProjectRequest(StrictModel):
    """Updates an existing project by its unique identifier, applying only the fields provided in the request body while leaving unspecified fields unchanged. Returns the complete updated project record."""
    path: UpdateProjectRequestPath
    body: UpdateProjectRequestBody | None = None

# Operation: delete_project
class DeleteProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier (GID) of the project to be deleted.")
class DeleteProjectRequest(StrictModel):
    """Permanently deletes an existing project by its unique identifier. This action is irreversible and returns an empty data record upon success."""
    path: DeleteProjectRequestPath

# Operation: duplicate_project
class DuplicateProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier (GID) of the source project to duplicate.")
class DuplicateProjectRequestBodyDataScheduleDates(StrictModel):
    should_skip_weekends: bool | None = Field(default=None, validation_alias="should_skip_weekends", serialization_alias="should_skip_weekends", description="Required when shifting task dates: determines whether auto-shifted due and start dates should skip Saturday and Sunday when recalculating offsets.")
    due_on: str | None = Field(default=None, validation_alias="due_on", serialization_alias="due_on", description="An ISO 8601 date (YYYY-MM-DD) to set as the last due date in the duplicated project; all other due dates are offset proportionally relative to this anchor date.")
    start_on: str | None = Field(default=None, validation_alias="start_on", serialization_alias="start_on", description="An ISO 8601 date (YYYY-MM-DD) to set as the first start date in the duplicated project; all other start dates are offset proportionally relative to this anchor date.")
class DuplicateProjectRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name to assign to the newly created duplicate project.")
    team: str | None = Field(default=None, validation_alias="team", serialization_alias="team", description="The GID of the team to assign the new project to. If omitted, the duplicate inherits the same team as the source project.")
    include: str | None = Field(default=None, validation_alias="include", serialization_alias="include", description="A comma-separated list of optional elements to copy into the duplicate project. Tasks, project views, and rules are always included automatically. Explicitly specify any combination of optional fields: allocations, forms, members, notes, permissions, task_assignee, task_attachments, task_dates, task_dependencies, task_followers, task_notes, task_projects, task_subtasks, task_tags, task_templates, task_type_default.")
    schedule_dates: DuplicateProjectRequestBodyDataScheduleDates | None = None
class DuplicateProjectRequestBody(StrictModel):
    """Describes the duplicate's name and the elements that will be duplicated."""
    data: DuplicateProjectRequestBodyData | None = None
class DuplicateProjectRequest(StrictModel):
    """Creates an asynchronous duplication job that copies an existing project into a new project, with configurable options for which elements (members, tasks, dates, etc.) to include. Returns a job object that can be polled to track duplication progress."""
    path: DuplicateProjectRequestPath
    body: DuplicateProjectRequestBody | None = None

# Operation: list_task_projects
class GetProjectsForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task whose associated projects you want to retrieve.")
class GetProjectsForTaskRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of project records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetProjectsForTaskRequest(StrictModel):
    """Retrieves all projects that contain a specified task. Returns a compact representation of each associated project."""
    path: GetProjectsForTaskRequestPath
    query: GetProjectsForTaskRequestQuery | None = None

# Operation: create_team_project
class CreateProjectForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier of the team with which the new project will be shared.")
class CreateProjectForTeamRequestBody(StrictModel):
    """The new project to create."""
    data: ProjectRequest | None = Field(default=None, description="The project details and configuration to use when creating the new team project.")
class CreateProjectForTeamRequest(StrictModel):
    """Creates a new project shared with the specified team. Returns the full record of the newly created project."""
    path: CreateProjectForTeamRequestPath
    body: CreateProjectForTeamRequestBody | None = None

# Operation: list_workspace_projects
class GetProjectsForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="Globally unique identifier for the workspace or organization.")
class GetProjectsForWorkspaceRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="Filters results to only include projects matching the specified archived status. When set to true, only archived projects are returned; when false, only active projects are returned.")
class GetProjectsForWorkspaceRequest(StrictModel):
    """Retrieves compact records for all projects within a specified workspace. Note: this endpoint may time out for large domains; use the memberships endpoint to fetch projects for a specific team."""
    path: GetProjectsForWorkspaceRequestPath
    query: GetProjectsForWorkspaceRequestQuery | None = None

# Operation: create_project_in_workspace
class CreateProjectForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization in which to create the project.")
class CreateProjectForWorkspaceRequestBody(StrictModel):
    """The new project to create."""
    data: ProjectRequest | None = Field(default=None, description="The project details to use when creating the new project, such as name, team, and other project attributes.")
class CreateProjectForWorkspaceRequest(StrictModel):
    """Creates a new project within the specified workspace or organization. If the workspace is an organization, a team must also be provided to share the project with."""
    path: CreateProjectForWorkspaceRequestPath
    body: CreateProjectForWorkspaceRequestBody | None = None

# Operation: search_projects
class SearchProjectsForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization to search within.")
class SearchProjectsForWorkspaceRequestQuery(StrictModel):
    text: str | None = Field(default=None, description="Full-text search string matched against project names to narrow results.")
    sort_by: Literal["due_date", "created_at", "completed_at", "modified_at"] | None = Field(default=None, description="Field by which to sort results; defaults to `modified_at` if not specified.")
    sort_ascending: bool | None = Field(default=None, description="When `true`, results are returned in ascending sort order; defaults to descending (`false`).")
    completed: bool | None = Field(default=None, description="Filter projects by completion status: `true` returns only completed projects, `false` returns only incomplete projects.")
    teams_any: str | None = Field(default=None, validation_alias="teams.any", serialization_alias="teams.any", description="Comma-separated list of team GIDs; returns projects belonging to any of the specified teams.")
    owner_any: str | None = Field(default=None, validation_alias="owner.any", serialization_alias="owner.any", description="Comma-separated list of user GIDs or the string `me`; returns projects owned by any of the specified users.")
    members_any: str | None = Field(default=None, validation_alias="members.any", serialization_alias="members.any", description="Comma-separated list of user GIDs or the string `me`; returns projects where any of the specified users are members.")
    members_not: str | None = Field(default=None, validation_alias="members.not", serialization_alias="members.not", description="Comma-separated list of user GIDs or the string `me`; excludes projects where any of the specified users are members.")
    portfolios_any: str | None = Field(default=None, validation_alias="portfolios.any", serialization_alias="portfolios.any", description="Comma-separated list of portfolio GIDs; returns projects that belong to any of the specified portfolios.")
    completed_on: str | None = Field(default=None, description="ISO 8601 date string to match projects completed on an exact date, or `null` to match projects with no completion date.", json_schema_extra={'format': 'date'})
    completed_on_before: str | None = Field(default=None, validation_alias="completed_on.before", serialization_alias="completed_on.before", description="ISO 8601 date string; returns projects completed strictly before this date.", json_schema_extra={'format': 'date'})
    completed_on_after: str | None = Field(default=None, validation_alias="completed_on.after", serialization_alias="completed_on.after", description="ISO 8601 date string; returns projects completed strictly after this date.", json_schema_extra={'format': 'date'})
    completed_at_before: str | None = Field(default=None, validation_alias="completed_at.before", serialization_alias="completed_at.before", description="ISO 8601 datetime string; returns projects whose completion timestamp is strictly before this datetime.", json_schema_extra={'format': 'date-time'})
    completed_at_after: str | None = Field(default=None, validation_alias="completed_at.after", serialization_alias="completed_at.after", description="ISO 8601 datetime string; returns projects whose completion timestamp is strictly after this datetime.", json_schema_extra={'format': 'date-time'})
    created_on: str | None = Field(default=None, description="ISO 8601 date string to match projects created on an exact date, or `null` to match projects with no creation date recorded.", json_schema_extra={'format': 'date'})
    created_on_before: str | None = Field(default=None, validation_alias="created_on.before", serialization_alias="created_on.before", description="ISO 8601 date string; returns projects created strictly before this date.", json_schema_extra={'format': 'date'})
    created_on_after: str | None = Field(default=None, validation_alias="created_on.after", serialization_alias="created_on.after", description="ISO 8601 date string; returns projects created strictly after this date.", json_schema_extra={'format': 'date'})
    created_at_before: str | None = Field(default=None, validation_alias="created_at.before", serialization_alias="created_at.before", description="ISO 8601 datetime string; returns projects whose creation timestamp is strictly before this datetime.", json_schema_extra={'format': 'date-time'})
    created_at_after: str | None = Field(default=None, validation_alias="created_at.after", serialization_alias="created_at.after", description="ISO 8601 datetime string; returns projects whose creation timestamp is strictly after this datetime.", json_schema_extra={'format': 'date-time'})
    due_on: str | None = Field(default=None, description="ISO 8601 date string to match projects with a due date on an exact date, or `null` to match projects with no due date.", json_schema_extra={'format': 'date'})
    due_on_before: str | None = Field(default=None, validation_alias="due_on.before", serialization_alias="due_on.before", description="ISO 8601 date string; returns projects with a due date strictly before this date.", json_schema_extra={'format': 'date'})
    due_on_after: str | None = Field(default=None, validation_alias="due_on.after", serialization_alias="due_on.after", description="ISO 8601 date string; returns projects with a due date strictly after this date.", json_schema_extra={'format': 'date'})
    due_at_before: str | None = Field(default=None, validation_alias="due_at.before", serialization_alias="due_at.before", description="ISO 8601 datetime string; returns projects whose due datetime is strictly before this datetime.", json_schema_extra={'format': 'date-time'})
    due_at_after: str | None = Field(default=None, validation_alias="due_at.after", serialization_alias="due_at.after", description="ISO 8601 datetime string; returns projects whose due datetime is strictly after this datetime.", json_schema_extra={'format': 'date-time'})
    start_on: str | None = Field(default=None, description="ISO 8601 date string to match projects with a start date on an exact date, or `null` to match projects with no start date.", json_schema_extra={'format': 'date'})
    start_on_before: str | None = Field(default=None, validation_alias="start_on.before", serialization_alias="start_on.before", description="ISO 8601 date string; returns projects with a start date strictly before this date.", json_schema_extra={'format': 'date'})
    start_on_after: str | None = Field(default=None, validation_alias="start_on.after", serialization_alias="start_on.after", description="ISO 8601 date string; returns projects with a start date strictly after this date.", json_schema_extra={'format': 'date'})
class SearchProjectsForWorkspaceRequest(StrictModel):
    """Search and filter projects within a workspace using advanced criteria including text, ownership, membership, portfolio, dates, and custom fields. Results are eventually consistent and require a premium Asana account; use list_projects instead when immediate consistency after writes is needed."""
    path: SearchProjectsForWorkspaceRequestPath
    query: SearchProjectsForWorkspaceRequestQuery | None = None

# Operation: add_custom_field_to_project
class AddCustomFieldSettingForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The unique identifier of the project to which the custom field will be added.")
class AddCustomFieldSettingForProjectRequestBodyData(StrictModel):
    custom_field: str | CustomFieldCreateRequest = Field(default=..., validation_alias="custom_field", serialization_alias="custom_field", description="The globally unique identifier (GID) of the custom field to associate with the project.")
    is_important: bool | None = Field(default=None, validation_alias="is_important", serialization_alias="is_important", description="When true, marks this custom field as important for the project, causing it to be prominently displayed in list views of the project's items.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The GID of an existing custom field setting on this project before which the new setting will be inserted to control ordering. Cannot be used together with insert_after.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The GID of an existing custom field setting on this project after which the new setting will be inserted to control ordering. Cannot be used together with insert_before.")
class AddCustomFieldSettingForProjectRequestBody(StrictModel):
    """Information about the custom field setting."""
    data: AddCustomFieldSettingForProjectRequestBodyData
class AddCustomFieldSettingForProjectRequest(StrictModel):
    """Associates a custom field with a project by creating a custom field setting, allowing the field to appear and be used within that project. Optionally controls the field's display prominence and its position relative to other custom field settings."""
    path: AddCustomFieldSettingForProjectRequestPath
    body: AddCustomFieldSettingForProjectRequestBody

# Operation: remove_custom_field_from_project
class RemoveCustomFieldSettingForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project from which the custom field setting will be removed.")
class RemoveCustomFieldSettingForProjectRequestBodyData(StrictModel):
    custom_field: str = Field(default=..., validation_alias="custom_field", serialization_alias="custom_field", description="The globally unique identifier of the custom field to detach from the project.")
class RemoveCustomFieldSettingForProjectRequestBody(StrictModel):
    """Information about the custom field setting being removed."""
    data: RemoveCustomFieldSettingForProjectRequestBodyData
class RemoveCustomFieldSettingForProjectRequest(StrictModel):
    """Removes a custom field setting from a project, detaching it so the field no longer appears or collects data for that project. Requires projects:write scope."""
    path: RemoveCustomFieldSettingForProjectRequestPath
    body: RemoveCustomFieldSettingForProjectRequestBody

# Operation: get_project_task_counts
class GetTaskCountsForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project whose task counts you want to retrieve.")
class GetTaskCountsForProjectRequest(StrictModel):
    """Retrieves task count statistics for a specific project, including total, incomplete, and completed task counts (milestones are included). All fields are excluded by default and must be explicitly requested using opt_fields."""
    path: GetTaskCountsForProjectRequestPath

# Operation: add_project_members
class AddMembersForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project to which members will be added.")
class AddMembersForProjectRequestBodyData(StrictModel):
    members: str = Field(default=..., validation_alias="members", serialization_alias="members", description="A comma-separated list of user identifiers to add as project members. Each identifier can be the string 'me', a user's email address, or a user's globally unique identifier (gid).")
class AddMembersForProjectRequestBody(StrictModel):
    """Information about the members being added."""
    data: AddMembersForProjectRequestBodyData
class AddMembersForProjectRequest(StrictModel):
    """Adds one or more users as members of the specified project. Note that added members may also become followers depending on their personal notification settings."""
    path: AddMembersForProjectRequestPath
    body: AddMembersForProjectRequestBody

# Operation: remove_project_members
class RemoveMembersForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project from which members will be removed.")
class RemoveMembersForProjectRequestBodyData(StrictModel):
    members: str = Field(default=..., validation_alias="members", serialization_alias="members", description="A comma-separated list of users to remove from the project, where each user can be identified by their GID, email address, or the literal string 'me' to reference the authenticated user.")
class RemoveMembersForProjectRequestBody(StrictModel):
    """Information about the members being removed."""
    data: RemoveMembersForProjectRequestBodyData
class RemoveMembersForProjectRequest(StrictModel):
    """Removes one or more users from the member list of a specified project. Returns the updated project record reflecting the new membership."""
    path: RemoveMembersForProjectRequestPath
    body: RemoveMembersForProjectRequestBody

# Operation: add_project_followers
class AddFollowersForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The unique identifier of the project to which followers will be added.")
class AddFollowersForProjectRequestBodyData(StrictModel):
    followers: str = Field(default=..., validation_alias="followers", serialization_alias="followers", description="A comma-separated list of user identifiers to add as followers; each identifier can be the string 'me', a user's email address, or a user's GID.")
class AddFollowersForProjectRequestBody(StrictModel):
    """Information about the followers being added."""
    data: AddFollowersForProjectRequestBodyData
class AddFollowersForProjectRequest(StrictModel):
    """Adds one or more users as followers to a project, automatically making them members if they are not already. Followers receive 'tasks added' notifications for the project."""
    path: AddFollowersForProjectRequestPath
    body: AddFollowersForProjectRequestBody

# Operation: remove_project_followers
class RemoveFollowersForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier of the project from which followers will be removed.")
class RemoveFollowersForProjectRequestBodyData(StrictModel):
    followers: str = Field(default=..., validation_alias="followers", serialization_alias="followers", description="A comma-separated list of users to remove as followers. Each user can be identified by their GID, email address, or the string 'me' to reference the authenticated user.")
class RemoveFollowersForProjectRequestBody(StrictModel):
    """Information about the followers being removed."""
    data: RemoveFollowersForProjectRequestBodyData
class RemoveFollowersForProjectRequest(StrictModel):
    """Removes one or more users from following a project without affecting their project membership status. Returns the updated project record."""
    path: RemoveFollowersForProjectRequestPath
    body: RemoveFollowersForProjectRequestBody

# Operation: save_project_as_template
class ProjectSaveAsTemplateRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The unique identifier of the project to convert into a template.")
class ProjectSaveAsTemplateRequestBodyData(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name to assign to the newly created project template.")
    team: str | None = Field(default=None, validation_alias="team", serialization_alias="team", description="The GID of the team to associate with the new project template. Required when the source project belongs to an organization; do not use alongside workspace.")
    workspace: str | None = Field(default=None, validation_alias="workspace", serialization_alias="workspace", description="The GID of the workspace to associate with the new project template. Only applicable when the source project exists in a workspace rather than an organization; do not use alongside team.")
    public: bool = Field(default=..., validation_alias="public", serialization_alias="public", description="Controls whether the project template is publicly visible to all members of its team. Set to false to restrict visibility.")
class ProjectSaveAsTemplateRequestBody(StrictModel):
    """Describes the inputs used for creating a project template, such as the resulting project template's name, which team it should be created in."""
    data: ProjectSaveAsTemplateRequestBodyData
class ProjectSaveAsTemplateRequest(StrictModel):
    """Converts an existing project into a reusable project template by initiating an asynchronous job. Returns a job object that can be monitored for completion status."""
    path: ProjectSaveAsTemplateRequestPath
    body: ProjectSaveAsTemplateRequestBody

# Operation: list_rates
class GetRatesRequestQuery(StrictModel):
    parent: str | None = Field(default=None, description="The globally unique identifier of the parent project whose rates should be retrieved.")
    resource: str | None = Field(default=None, description="The globally unique identifier of a user or placeholder to filter rates down to a single specific resource.")
class GetRatesRequest(StrictModel):
    """Retrieves a list of rate records associated with a parent project, optionally filtered to a specific user or placeholder resource. Modifying placeholder rates requires an Enterprise or Enterprise+ plan."""
    query: GetRatesRequestQuery | None = None

# Operation: create_rate
class CreateRateRequestBodyData(StrictModel):
    parent: str = Field(default=..., validation_alias="parent", serialization_alias="parent", description="The globally unique ID of the parent project to which this rate will be assigned.")
    resource: str = Field(default=..., validation_alias="resource", serialization_alias="resource", description="The globally unique ID of the resource (user or placeholder) for whom the rate is being set.")
    rate: float = Field(default=..., validation_alias="rate", serialization_alias="rate", description="The monetary value of the rate to assign to the resource, representing the billing amount per unit of time.")
class CreateRateRequestBody(StrictModel):
    """The rate to create."""
    data: CreateRateRequestBodyData
class CreateRateRequest(StrictModel):
    """Creates a billing rate for a specific resource (user or placeholder) within a parent project, defining the monetary value charged for that resource's time."""
    body: CreateRateRequestBody

# Operation: get_rate
class GetRateRequestPath(StrictModel):
    rate_gid: str = Field(default=..., description="The globally unique identifier for the rate to retrieve.")
class GetRateRequest(StrictModel):
    """Retrieves the complete record for a single rate, including all associated pricing details and metadata."""
    path: GetRateRequestPath

# Operation: update_rate
class UpdateRateRequestPath(StrictModel):
    rate_gid: str = Field(default=..., description="The globally unique identifier of the rate record to update.")
class UpdateRateRequestBodyData(StrictModel):
    rate: float | None = Field(default=None, validation_alias="rate", serialization_alias="rate", description="The new monetary value to assign to the rate. Must be a valid numeric amount.")
class UpdateRateRequestBody(StrictModel):
    """The updated fields for the rate."""
    data: UpdateRateRequestBodyData | None = None
class UpdateRateRequest(StrictModel):
    """Updates the monetary value of an existing rate record. Only the rate field can be modified; all other fields remain unchanged."""
    path: UpdateRateRequestPath
    body: UpdateRateRequestBody | None = None

# Operation: delete_rate
class DeleteRateRequestPath(StrictModel):
    rate_gid: str = Field(default=..., description="The globally unique identifier of the rate to delete.")
class DeleteRateRequest(StrictModel):
    """Permanently deletes a rate by its unique identifier. This action cannot be undone."""
    path: DeleteRateRequestPath

# Operation: list_reactions
class GetReactionsOnObjectRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of reactions to return per page. Must be between 1 and 100.", ge=1, le=100)
    target: str = Field(default=..., description="The globally unique identifier (GID) of the object to fetch reactions from. Must reference a valid status update or story.")
    emoji_base: str = Field(default=..., description="Filters results to only include reactions that use this emoji base character. Only reactions matching this exact emoji will be returned.")
class GetReactionsOnObjectRequest(StrictModel):
    """Retrieves all reactions matching a specific emoji on a given object, such as a status update or story. Returns a paginated list of reactions filtered by the specified emoji base character."""
    query: GetReactionsOnObjectRequestQuery

# Operation: get_section
class GetSectionRequestPath(StrictModel):
    section_gid: str = Field(default=..., description="The globally unique identifier (GID) of the section to retrieve.")
class GetSectionRequest(StrictModel):
    """Retrieves the complete details for a single section by its unique identifier. Useful for inspecting section metadata such as its name, project association, and ordering."""
    path: GetSectionRequestPath

# Operation: update_section
class UpdateSectionRequestPath(StrictModel):
    section_gid: str = Field(default=..., description="The globally unique identifier of the section to update.")
class UpdateSectionRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The new display name for the section. Must be a non-empty string.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The unique identifier of an existing section before which this section should be repositioned. Mutually exclusive with insert_after.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The unique identifier of an existing section after which this section should be repositioned. Mutually exclusive with insert_before.")
class UpdateSectionRequestBody(StrictModel):
    """The section to create."""
    data: UpdateSectionRequestBodyData | None = None
class UpdateSectionRequest(StrictModel):
    """Updates an existing section's name or position within its project. Only the fields provided will be modified; all other section properties remain unchanged."""
    path: UpdateSectionRequestPath
    body: UpdateSectionRequestBody | None = None

# Operation: delete_section
class DeleteSectionRequestPath(StrictModel):
    section_gid: str = Field(default=..., description="The globally unique identifier (GID) of the section to delete.")
class DeleteSectionRequest(StrictModel):
    """Permanently deletes an existing section by its unique identifier. The section must be empty and cannot be the last remaining section in the project."""
    path: DeleteSectionRequestPath

# Operation: list_project_sections
class GetSectionsForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="Globally unique identifier for the project.")
class GetSectionsForProjectRequest(StrictModel):
    """Retrieves all sections within a specified project, returning compact records for each. Useful for understanding a project's organizational structure before creating or moving tasks."""
    path: GetSectionsForProjectRequestPath

# Operation: create_section
class CreateSectionForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The unique identifier of the project in which the new section will be created.")
class CreateSectionForProjectRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the new section. Must be a non-empty string.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The GID of an existing section in this project before which the new section will be inserted. Mutually exclusive with insert_after; only one may be provided.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The GID of an existing section in this project after which the new section will be inserted. Mutually exclusive with insert_before; only one may be provided.")
class CreateSectionForProjectRequestBody(StrictModel):
    """The section to create."""
    data: CreateSectionForProjectRequestBodyData | None = None
class CreateSectionForProjectRequest(StrictModel):
    """Creates a new section within a specified project to help organize tasks. Returns the full record of the newly created section."""
    path: CreateSectionForProjectRequestPath
    body: CreateSectionForProjectRequestBody | None = None

# Operation: add_task_to_section
class AddTaskForSectionRequestPath(StrictModel):
    section_gid: str = Field(default=..., description="The unique identifier of the section to which the task will be added.")
class AddTaskForSectionRequestBodyData(StrictModel):
    task: str | None = Field(default=None, validation_alias="task", serialization_alias="task", description="The unique identifier of the task to add to the section. Note: tasks with a resource_subtype of 'section' (separators) are not supported.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The unique identifier of an existing task in this section before which the added task should be inserted. Mutually exclusive with insert_after.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The unique identifier of an existing task in this section after which the added task should be inserted. Mutually exclusive with insert_before.")
class AddTaskForSectionRequestBody(StrictModel):
    """The task and optionally the insert location."""
    data: AddTaskForSectionRequestBodyData | None = None
class AddTaskForSectionRequest(StrictModel):
    """Moves a task into a specific section within a project, removing it from any other sections. The task is placed at the top of the section by default, or at a specific position using insert_before or insert_after."""
    path: AddTaskForSectionRequestPath
    body: AddTaskForSectionRequestBody | None = None

# Operation: reorder_section
class InsertSectionForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The unique identifier of the project that contains the sections being reordered.")
class InsertSectionForProjectRequestBodyData(StrictModel):
    section: str | None = Field(default=None, validation_alias="section", serialization_alias="section", description="The unique identifier of the section you want to move to a new position within the project.")
    before_section: str | None = Field(default=None, validation_alias="before_section", serialization_alias="before_section", description="The unique identifier of the reference section that the moved section should be placed immediately before. Mutually exclusive with `after_section`.")
    after_section: str | None = Field(default=None, validation_alias="after_section", serialization_alias="after_section", description="The unique identifier of the reference section that the moved section should be placed immediately after. Mutually exclusive with `before_section`.")
class InsertSectionForProjectRequestBody(StrictModel):
    """The section's move action."""
    data: InsertSectionForProjectRequestBodyData | None = None
class InsertSectionForProjectRequest(StrictModel):
    """Move a section to a new position within a project by placing it before or after another section. Exactly one of `before_section` or `after_section` must be provided; sections cannot be moved across projects."""
    path: InsertSectionForProjectRequestPath
    body: InsertSectionForProjectRequestBody | None = None

# Operation: get_status_update
class GetStatusRequestPath(StrictModel):
    status_update_gid: str = Field(default=..., description="The unique identifier of the status update to retrieve.")
class GetStatusRequest(StrictModel):
    """Retrieves the complete record for a single status update by its unique identifier. Useful for fetching the full details of a specific project or task status update."""
    path: GetStatusRequestPath

# Operation: delete_status_update
class DeleteStatusRequestPath(StrictModel):
    status_update_gid: str = Field(default=..., description="The unique identifier of the status update to delete.")
class DeleteStatusRequest(StrictModel):
    """Permanently deletes a specific status update by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteStatusRequestPath

# Operation: list_status_updates
class GetStatusesForObjectRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of status update records to return per page, between 1 and 100.", ge=1, le=100)
    parent: str = Field(default=..., description="The globally unique identifier (GID) of the object whose status updates should be retrieved. Must reference a project, portfolio, or goal.")
    created_since: str | None = Field(default=None, description="Filters results to only include status updates created at or after this timestamp, specified in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
class GetStatusesForObjectRequest(StrictModel):
    """Retrieves a paginated list of status updates for a specified project, portfolio, or goal. Results can be filtered by creation date to surface only recent updates."""
    query: GetStatusesForObjectRequestQuery

# Operation: create_status_update
class CreateStatusForObjectRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of results to return per page, must be between 1 and 100.", ge=1, le=100)
class CreateStatusForObjectRequestBody(StrictModel):
    """The status update to create."""
    data: StatusUpdateRequest | None = Field(default=None, description="The payload containing the status update details to be created on the target object.")
class CreateStatusForObjectRequest(StrictModel):
    """Creates a new status update on a specified object, such as a project or task. Returns the full record of the newly created status update."""
    query: CreateStatusForObjectRequestQuery | None = None
    body: CreateStatusForObjectRequestBody | None = None

# Operation: get_story
class GetStoryRequestPath(StrictModel):
    story_gid: str = Field(default=..., description="The globally unique identifier (GID) of the story to retrieve.")
class GetStoryRequest(StrictModel):
    """Retrieves the full record for a single story by its unique identifier. Requires the stories:read scope, with additional attachments:read scope needed to access previews and attachments fields."""
    path: GetStoryRequestPath

# Operation: update_story
class UpdateStoryRequestPath(StrictModel):
    story_gid: str = Field(default=..., description="The globally unique identifier of the story to update.")
class UpdateStoryRequestBodyData(StrictModel):
    text: str | None = Field(default=None, validation_alias="text", serialization_alias="text", description="The plain text content of the comment story to set. Cannot be used together with html_text; only one may be specified per request.")
    is_pinned: bool | None = Field(default=None, validation_alias="is_pinned", serialization_alias="is_pinned", description="Whether the story should be pinned to its parent resource. Pinning is supported only for comment and attachment story types.")
    sticker_name: Literal["green_checkmark", "people_dancing", "dancing_unicorn", "heart", "party_popper", "people_waving_flags", "splashing_narwhal", "trophy", "yeti_riding_unicorn", "celebrating_people", "determined_climbers", "phoenix_spreading_love"] | None = Field(default=None, validation_alias="sticker_name", serialization_alias="sticker_name", description="The name of the sticker to display on the story. Set to null to remove an existing sticker. Must be one of the supported sticker identifiers.")
class UpdateStoryRequestBody(StrictModel):
    """The comment story to update."""
    data: UpdateStoryRequestBodyData | None = None
class UpdateStoryRequest(StrictModel):
    """Updates an existing story on a task, allowing edits to comment text, pin status, or sticker. Only comment stories support text updates, and only comment and attachment stories can be pinned."""
    path: UpdateStoryRequestPath
    body: UpdateStoryRequestBody | None = None

# Operation: delete_story
class DeleteStoryRequestPath(StrictModel):
    story_gid: str = Field(default=..., description="The globally unique identifier of the story to delete.")
class DeleteStoryRequest(StrictModel):
    """Permanently deletes a story by its unique identifier. Only the story's creator can delete it; returns an empty data record on success."""
    path: DeleteStoryRequestPath

# Operation: list_task_stories
class GetStoriesForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The task to operate on.")
class GetStoriesForTaskRequest(StrictModel):
    """Retrieves all stories (comments, activity, and system events) associated with a specific task. Returns compact story records in chronological order."""
    path: GetStoriesForTaskRequestPath

# Operation: add_task_comment
class CreateStoryForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task to which the story will be added.")
class CreateStoryForTaskRequestBodyData(StrictModel):
    text: str | None = Field(default=None, validation_alias="text", serialization_alias="text", description="The plain text content of the comment to post on the task. Cannot be used together with html_text.")
    is_pinned: bool | None = Field(default=None, validation_alias="is_pinned", serialization_alias="is_pinned", description="Whether the story should be pinned to the top of the task's story feed, making it prominently visible.")
    sticker_name: Literal["green_checkmark", "people_dancing", "dancing_unicorn", "heart", "party_popper", "people_waving_flags", "splashing_narwhal", "trophy", "yeti_riding_unicorn", "celebrating_people", "determined_climbers", "phoenix_spreading_love"] | None = Field(default=None, validation_alias="sticker_name", serialization_alias="sticker_name", description="The name of the sticker to attach to this story. Omit or set to null if no sticker is desired.")
class CreateStoryForTaskRequestBody(StrictModel):
    """The story to create."""
    data: CreateStoryForTaskRequestBodyData | None = None
class CreateStoryForTaskRequest(StrictModel):
    """Adds a comment story to a task, authored by the currently authenticated user and timestamped at the time of the request. Returns the full record of the newly created story."""
    path: CreateStoryForTaskRequestPath
    body: CreateStoryForTaskRequestBody | None = None

# Operation: list_tags
class GetTagsRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The unique identifier of the workspace used to filter the returned tags to only those belonging to that workspace.")
class GetTagsRequest(StrictModel):
    """Retrieves a list of compact tag records, optionally filtered by workspace. Requires the 'tags:read' scope."""
    query: GetTagsRequestQuery | None = None

# Operation: create_tag
class CreateTagRequestBody(StrictModel):
    """The tag to create."""
    data: TagCreateRequest | None = Field(default=None, description="The request body containing the tag details, including the required workspace or organization identifier and any additional tag properties such as name and color.")
class CreateTagRequest(StrictModel):
    """Creates a new tag within a specified workspace or organization, returning the full record of the newly created tag. Requires the tags:write scope, and the tag's workspace association is permanent once set."""
    body: CreateTagRequestBody | None = None

# Operation: get_tag
class GetTagRequestPath(StrictModel):
    tag_gid: str = Field(default=..., description="The globally unique identifier (GID) of the tag to retrieve.")
class GetTagRequest(StrictModel):
    """Retrieves the complete record for a single tag, including its name, color, and associated metadata. Requires the tags:read scope."""
    path: GetTagRequestPath

# Operation: update_tag
class UpdateTagRequestPath(StrictModel):
    tag_gid: str = Field(default=..., description="The globally unique identifier of the tag to update.")
class UpdateTagRequestBody(StrictModel):
    """The tag to update."""
    data: TagBase | None = Field(default=None, description="An object containing the tag fields to update. Only include fields you wish to change to avoid overwriting concurrent updates from other users.")
class UpdateTagRequest(StrictModel):
    """Updates the properties of an existing tag by its unique identifier. Only fields provided in the request body will be modified; unspecified fields remain unchanged."""
    path: UpdateTagRequestPath
    body: UpdateTagRequestBody | None = None

# Operation: delete_tag
class DeleteTagRequestPath(StrictModel):
    tag_gid: str = Field(default=..., description="The globally unique identifier of the tag to delete.")
class DeleteTagRequest(StrictModel):
    """Permanently deletes an existing tag by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteTagRequestPath

# Operation: list_task_tags
class GetTagsForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task whose tags you want to retrieve.")
class GetTagsForTaskRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of tag results to return per page, must be between 1 and 100.", ge=1, le=100)
class GetTagsForTaskRequest(StrictModel):
    """Retrieves all tags associated with a specific task, returned as compact tag representations. Requires the tags:read scope."""
    path: GetTagsForTaskRequestPath
    query: GetTagsForTaskRequestQuery | None = None

# Operation: list_workspace_tags
class GetTagsForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="Globally unique identifier for the workspace or organization.")
class GetTagsForWorkspaceRequest(StrictModel):
    """Retrieves compact tag records for all tags within a specified workspace. Useful for discovering and filtering available tags to organize and categorize work items."""
    path: GetTagsForWorkspaceRequestPath

# Operation: create_tag_in_workspace
class CreateTagForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization in which to create the tag.")
class CreateTagForWorkspaceRequestBody(StrictModel):
    """The tag to create."""
    data: TagCreateTagForWorkspaceRequest | None = Field(default=None, description="The tag details to create, including properties such as name, color, and any other supported tag fields.")
class CreateTagForWorkspaceRequest(StrictModel):
    """Creates a new tag within a specified workspace or organization. Returns the full record of the newly created tag."""
    path: CreateTagForWorkspaceRequestPath
    body: CreateTagForWorkspaceRequestBody | None = None

# Operation: list_task_templates
class GetTaskTemplatesRequestQuery(StrictModel):
    project: str | None = Field(default=None, description="The unique identifier of the project whose task templates should be returned. This filter is required to scope results to a specific project.")
class GetTaskTemplatesRequest(StrictModel):
    """Retrieves a list of compact task template records for a specified project. A project must be provided to filter and return the relevant task templates."""
    query: GetTaskTemplatesRequestQuery | None = None

# Operation: get_task_template
class GetTaskTemplateRequestPath(StrictModel):
    task_template_gid: str = Field(default=..., description="The globally unique identifier (GID) of the task template to retrieve.")
class GetTaskTemplateRequest(StrictModel):
    """Retrieves the complete record for a single task template, including all its fields and configuration. Requires the task_templates:read scope."""
    path: GetTaskTemplateRequestPath

# Operation: delete_task_template
class DeleteTaskTemplateRequestPath(StrictModel):
    task_template_gid: str = Field(default=..., description="The globally unique identifier of the task template to delete.")
class DeleteTaskTemplateRequest(StrictModel):
    """Permanently deletes an existing task template by its unique identifier. This action is irreversible and returns an empty data record upon success."""
    path: DeleteTaskTemplateRequestPath

# Operation: instantiate_task_from_template
class InstantiateTaskRequestPath(StrictModel):
    task_template_gid: str = Field(default=..., description="The globally unique identifier of the task template to instantiate a new task from.")
class InstantiateTaskRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the newly created task. If omitted, the task inherits the name defined in the source task template.")
class InstantiateTaskRequestBody(StrictModel):
    """Describes the inputs used for instantiating a task - the task's name."""
    data: InstantiateTaskRequestBodyData | None = None
class InstantiateTaskRequest(StrictModel):
    """Creates a new task by instantiating a task template, returning an asynchronous job that handles the task creation process. Use this to spin up pre-configured tasks from reusable templates."""
    path: InstantiateTaskRequestPath
    body: InstantiateTaskRequestBody | None = None

# Operation: list_tasks
class GetTasksRequestQuery(StrictModel):
    assignee: str | None = Field(default=None, description="Filter tasks by the GID of the assigned user. To find unassigned tasks, use assignee.any = null. Requires workspace to also be specified.")
    project: str | None = Field(default=None, description="Filter tasks belonging to the specified project GID.")
    section: str | None = Field(default=None, description="Filter tasks belonging to the specified section GID within a project.")
    workspace: str | None = Field(default=None, description="Filter tasks within the specified workspace GID. Requires assignee to also be specified.")
    completed_since: str | None = Field(default=None, description="Return only tasks that are incomplete or were completed on or after this timestamp, provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    modified_since: str | None = Field(default=None, description="Return only tasks modified on or after this timestamp in ISO 8601 date-time format. Modifications include property changes and association updates such as assigning, renaming, completing, or adding stories.", json_schema_extra={'format': 'date-time'})
class GetTasksRequest(StrictModel):
    """Retrieves a filtered list of compact task records based on assignee, project, section, workspace, or time-based criteria. At least one of project, tag, or both assignee and workspace must be specified."""
    query: GetTasksRequestQuery | None = None

# Operation: create_task
class CreateTaskRequestBody(StrictModel):
    """The task to create."""
    data: TaskRequest | None = Field(default=None, description="The task fields to set on the new task, such as name, workspace, projects, assignee, due date, and other task attributes. A workspace must be determinable either directly or via an associated project or parent task.")
class CreateTaskRequest(StrictModel):
    """Creates a new task in a specified workspace, project, or as a child of a parent task. Any fields not explicitly provided will be assigned their default values."""
    body: CreateTaskRequestBody | None = None

# Operation: get_task
class GetTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique global identifier (GID) of the task to retrieve.")
class GetTaskRequest(StrictModel):
    """Retrieves the complete record for a single task, including all fields and metadata. Note that accessing memberships requires projects:read and project_sections:read scopes, and actual_time_minutes requires time_tracking_entries:read scope."""
    path: GetTaskRequestPath

# Operation: update_task
class UpdateTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task to update.")
class UpdateTaskRequestBody(StrictModel):
    """The task to update."""
    data: TaskRequest | None = Field(default=None, description="An object containing only the task fields you wish to update; omitted fields will retain their current values.")
class UpdateTaskRequest(StrictModel):
    """Updates specific fields of an existing task by its unique identifier. Only the fields provided in the request body will be modified; all other fields remain unchanged."""
    path: UpdateTaskRequestPath
    body: UpdateTaskRequestBody | None = None

# Operation: delete_task
class DeleteTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique global identifier (GID) of the task to delete.")
class DeleteTaskRequest(StrictModel):
    """Permanently deletes a specific task by moving it to the requesting user's trash, where it can be recovered within 30 days before being completely removed from the system."""
    path: DeleteTaskRequestPath

# Operation: duplicate_task
class DuplicateTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task to duplicate.")
class DuplicateTaskRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name to assign to the newly duplicated task.")
    include: str | None = Field(default=None, validation_alias="include", serialization_alias="include", description="A comma-separated list of fields to copy from the original task to the duplicate. Supported fields include: assignee, attachments, dates, dependencies, followers, notes, parent, projects, subtasks, and tags.")
class DuplicateTaskRequestBody(StrictModel):
    """Describes the duplicate's name and the fields that will be duplicated."""
    data: DuplicateTaskRequestBodyData | None = None
class DuplicateTaskRequest(StrictModel):
    """Duplicates an existing task and returns an asynchronous job that handles the duplication process. You can specify a new name and choose which fields to carry over to the duplicated task."""
    path: DuplicateTaskRequestPath
    body: DuplicateTaskRequestBody | None = None

# Operation: list_project_tasks
class GetTasksForProjectRequestPath(StrictModel):
    project_gid: str = Field(default=..., description="The globally unique identifier (GID) of the project whose tasks you want to retrieve.")
class GetTasksForProjectRequestQuery(StrictModel):
    completed_since: str | None = Field(default=None, description="Filters results to include only incomplete tasks or tasks completed after this point in time. Accepts an ISO 8601 date-time string or the keyword 'now' to filter relative to the current moment.")
    limit: int | None = Field(default=None, description="The number of task records to return per page. Must be between 1 and 100 inclusive.", ge=1, le=100)
class GetTasksForProjectRequest(StrictModel):
    """Retrieves all tasks within a specified project, ordered by their priority within that project. Tasks may belong to multiple projects simultaneously."""
    path: GetTasksForProjectRequestPath
    query: GetTasksForProjectRequestQuery | None = None

# Operation: list_section_tasks
class GetTasksForSectionRequestPath(StrictModel):
    section_gid: str = Field(default=..., description="The globally unique identifier of the section whose tasks you want to retrieve.")
class GetTasksForSectionRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Number of task records to return per page. Must be between 1 and 100.", ge=1, le=100)
    completed_since: str | None = Field(default=None, description="Filters results to include only incomplete tasks or tasks completed after the specified time. Accepts an ISO 8601 date-time string or the keyword 'now'.")
class GetTasksForSectionRequest(StrictModel):
    """Retrieves all tasks within a specified board section, returning compact task records. Only applicable to board view sections."""
    path: GetTasksForSectionRequestPath
    query: GetTasksForSectionRequestQuery | None = None

# Operation: list_tasks_by_tag
class GetTasksForTagRequestPath(StrictModel):
    tag_gid: str = Field(default=..., description="The globally unique identifier of the tag whose associated tasks you want to retrieve.")
class GetTasksForTagRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of task records to return per page, must be between 1 and 100.", ge=1, le=100)
class GetTasksForTagRequest(StrictModel):
    """Retrieves all tasks associated with a specific tag, returning compact task records. A task may belong to multiple tags simultaneously."""
    path: GetTasksForTagRequestPath
    query: GetTasksForTagRequestQuery | None = None

# Operation: list_user_task_list_tasks
class GetTasksForUserTaskListRequestPath(StrictModel):
    user_task_list_gid: str = Field(default=..., description="The globally unique identifier for the user task list whose tasks you want to retrieve.")
class GetTasksForUserTaskListRequestQuery(StrictModel):
    completed_since: str | None = Field(default=None, description="Filters results to only include tasks that are incomplete or were completed on or after this point in time. Accepts an ISO 8601 date-time string or the keyword 'now' to return only currently incomplete tasks.")
    limit: int | None = Field(default=None, description="The number of task objects to return per page, between 1 and 100 inclusive.", ge=1, le=100)
class GetTasksForUserTaskListRequest(StrictModel):
    """Retrieves the compact list of tasks from a user's My Tasks list, including both complete and incomplete tasks by default. Use the completed_since filter to narrow results, such as returning only incomplete tasks by passing 'now'."""
    path: GetTasksForUserTaskListRequestPath
    query: GetTasksForUserTaskListRequestQuery | None = None

# Operation: list_subtasks
class GetSubtasksForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The task to operate on.")
class GetSubtasksForTaskRequest(StrictModel):
    """Retrieves a compact list of all subtasks belonging to a specified task. Useful for exploring task hierarchies and understanding nested work breakdowns."""
    path: GetSubtasksForTaskRequestPath

# Operation: create_subtask
class CreateSubtaskForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the parent task to which the new subtask will be added.")
class CreateSubtaskForTaskRequestBody(StrictModel):
    """The new subtask to create."""
    data: TaskRequest | None = Field(default=None, description="The subtask details to create, including fields such as name, assignee, due date, and notes.")
class CreateSubtaskForTaskRequest(StrictModel):
    """Creates a new subtask under the specified parent task and returns the full record of the newly created subtask."""
    path: CreateSubtaskForTaskRequestPath
    body: CreateSubtaskForTaskRequestBody | None = None

# Operation: set_task_parent
class SetParentForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier of the task whose parent relationship will be updated.")
class SetParentForTaskRequestBodyData(StrictModel):
    parent: str = Field(default=..., validation_alias="parent", serialization_alias="parent", description="The unique identifier of the task to set as the new parent, or null to remove the existing parent and make the task top-level.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The unique identifier of an existing subtask of the new parent after which this task should be inserted, or null to insert at the beginning of the subtask list. Cannot be used together with insert_before.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The unique identifier of an existing subtask of the new parent before which this task should be inserted, or null to insert at the end of the subtask list. Cannot be used together with insert_after.")
class SetParentForTaskRequestBody(StrictModel):
    """The new parent of the subtask."""
    data: SetParentForTaskRequestBodyData
class SetParentForTaskRequest(StrictModel):
    """Sets or removes the parent of a task, making it a subtask of another task or a top-level task when parent is null. Optionally controls the position of the task within the parent's subtask list."""
    path: SetParentForTaskRequestPath
    body: SetParentForTaskRequestBody

# Operation: list_task_dependencies
class GetDependenciesForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task whose dependencies you want to retrieve.")
class GetDependenciesForTaskRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of dependency records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetDependenciesForTaskRequest(StrictModel):
    """Retrieves all tasks that a given task depends on, returned as compact representations. Useful for understanding task prerequisites and dependency chains within a project."""
    path: GetDependenciesForTaskRequestPath
    query: GetDependenciesForTaskRequestQuery | None = None

# Operation: add_task_dependencies
class AddDependenciesForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task to which dependencies will be added.")
class AddDependenciesForTaskRequestBodyData(StrictModel):
    dependencies: list[str] | None = Field(default=None, validation_alias="dependencies", serialization_alias="dependencies", description="An array of task GIDs to mark as dependencies of the specified task; order is not significant and each item should be a valid task GID string.")
class AddDependenciesForTaskRequestBody(StrictModel):
    """The list of tasks to set as dependencies."""
    data: AddDependenciesForTaskRequestBodyData | None = None
class AddDependenciesForTaskRequest(StrictModel):
    """Marks one or more tasks as dependencies of a specified task, establishing that the target task depends on their completion. A task may have at most 30 dependents and dependencies combined."""
    path: AddDependenciesForTaskRequestPath
    body: AddDependenciesForTaskRequestBody | None = None

# Operation: remove_task_dependencies
class RemoveDependenciesForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task from which dependencies will be removed.")
class RemoveDependenciesForTaskRequestBodyData(StrictModel):
    dependencies: list[str] | None = Field(default=None, validation_alias="dependencies", serialization_alias="dependencies", description="An array of task GIDs representing the dependency tasks to unlink from the specified task. Order is not significant; each item should be a valid task GID string.")
class RemoveDependenciesForTaskRequestBody(StrictModel):
    """The list of tasks to unlink as dependencies."""
    data: RemoveDependenciesForTaskRequestBodyData | None = None
class RemoveDependenciesForTaskRequest(StrictModel):
    """Unlinks one or more dependency tasks from a specified task, removing the requirement that those tasks must be completed before this task can proceed."""
    path: RemoveDependenciesForTaskRequestPath
    body: RemoveDependenciesForTaskRequestBody | None = None

# Operation: list_task_dependents
class GetDependentsForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task whose dependents you want to retrieve.")
class GetDependentsForTaskRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of dependent task records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetDependentsForTaskRequest(StrictModel):
    """Retrieves compact representations of all tasks that depend on a specified task. Useful for understanding downstream impact when changes are made to a task."""
    path: GetDependentsForTaskRequestPath
    query: GetDependentsForTaskRequestQuery | None = None

# Operation: add_task_dependents
class AddDependentsForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier of the task that will become the dependency (i.e., the task that others will depend on).")
class AddDependentsForTaskRequestBodyData(StrictModel):
    dependents: list[str] | None = Field(default=None, validation_alias="dependents", serialization_alias="dependents", description="An array of task GIDs to mark as dependents of the specified task. Order is not significant; each item should be a valid task GID string.")
class AddDependentsForTaskRequestBody(StrictModel):
    """The list of tasks to add as dependents."""
    data: AddDependentsForTaskRequestBodyData | None = None
class AddDependentsForTaskRequest(StrictModel):
    """Marks one or more tasks as dependents of the specified task, meaning those tasks depend on this task being completed. A task can have at most 30 dependents and dependencies combined."""
    path: AddDependentsForTaskRequestPath
    body: AddDependentsForTaskRequestBody | None = None

# Operation: remove_task_dependents
class RemoveDependentsForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier of the task from which dependents will be unlinked.")
class RemoveDependentsForTaskRequestBodyData(StrictModel):
    dependents: list[str] | None = Field(default=None, validation_alias="dependents", serialization_alias="dependents", description="An array of task GIDs representing the dependent tasks to unlink from the specified task. Order is not significant.")
class RemoveDependentsForTaskRequestBody(StrictModel):
    """The list of tasks to remove as dependents."""
    data: RemoveDependentsForTaskRequestBodyData | None = None
class RemoveDependentsForTaskRequest(StrictModel):
    """Unlinks one or more dependent tasks from a specified task, removing the dependency relationship. Requires tasks:write scope."""
    path: RemoveDependentsForTaskRequestPath
    body: RemoveDependentsForTaskRequestBody | None = None

# Operation: add_task_to_project
class AddProjectForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier of the task to add to the project.")
class AddProjectForTaskRequestBodyData(StrictModel):
    project: str = Field(default=..., validation_alias="project", serialization_alias="project", description="The unique identifier of the project to add the task to.")
    insert_after: str | None = Field(default=None, validation_alias="insert_after", serialization_alias="insert_after", description="The GID of an existing task in the project after which this task should be inserted. Pass null to place the task at the beginning of the list or, when combined with `section`, at the beginning of that section. Cannot be used together with `insert_before`.")
    insert_before: str | None = Field(default=None, validation_alias="insert_before", serialization_alias="insert_before", description="The GID of an existing task in the project before which this task should be inserted. Pass null to place the task at the end of the list or, when combined with `section`, at the end of that section. Cannot be used together with `insert_after`.")
    section: str | None = Field(default=None, validation_alias="section", serialization_alias="section", description="The GID of a section within the project into which the task should be placed. By default the task is added to the end of the section; combine with `insert_after: null` to place at the beginning, `insert_before: null` to place at the end, or a non-null `insert_before`/`insert_after` task GID to position relative to a specific task within the section.")
class AddProjectForTaskRequestBody(StrictModel):
    """The project to add the task to."""
    data: AddProjectForTaskRequestBodyData
class AddProjectForTaskRequest(StrictModel):
    """Adds a task to a specified project, optionally positioning it relative to another task or within a section. Can also be used to reorder a task already in the project; a task may belong to at most 20 projects."""
    path: AddProjectForTaskRequestPath
    body: AddProjectForTaskRequestBody

# Operation: remove_task_from_project
class RemoveProjectForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier of the task to be removed from the project.")
class RemoveProjectForTaskRequestBodyData(StrictModel):
    project: str = Field(default=..., validation_alias="project", serialization_alias="project", description="The unique identifier of the project from which the task should be removed.")
class RemoveProjectForTaskRequestBody(StrictModel):
    """The project to remove the task from."""
    data: RemoveProjectForTaskRequestBodyData
class RemoveProjectForTaskRequest(StrictModel):
    """Removes a task from a specified project without deleting the task itself. The task remains in the system and can still belong to other projects."""
    path: RemoveProjectForTaskRequestPath
    body: RemoveProjectForTaskRequestBody

# Operation: add_task_tag
class AddTagForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique global identifier (GID) of the task to which the tag will be added.")
class AddTagForTaskRequestBodyData(StrictModel):
    tag: str = Field(default=..., validation_alias="tag", serialization_alias="tag", description="The unique global identifier (GID) of the tag to attach to the task.")
class AddTagForTaskRequestBody(StrictModel):
    """The tag to add to the task."""
    data: AddTagForTaskRequestBodyData
class AddTagForTaskRequest(StrictModel):
    """Adds an existing tag to a specified task, associating them for organization and filtering purposes. Returns an empty data block on success."""
    path: AddTagForTaskRequestPath
    body: AddTagForTaskRequestBody

# Operation: remove_task_tag
class RemoveTagForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique global identifier (GID) of the task from which the tag will be removed.")
class RemoveTagForTaskRequestBodyData(StrictModel):
    tag: str = Field(default=..., validation_alias="tag", serialization_alias="tag", description="The unique global identifier (GID) of the tag to remove from the task.")
class RemoveTagForTaskRequestBody(StrictModel):
    """The tag to remove from the task."""
    data: RemoveTagForTaskRequestBodyData
class RemoveTagForTaskRequest(StrictModel):
    """Removes a tag from a specified task, dissociating the tag without deleting it. Returns an empty data block on success."""
    path: RemoveTagForTaskRequestPath
    body: RemoveTagForTaskRequestBody

# Operation: add_task_followers
class AddFollowersForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task to which followers will be added.")
class AddFollowersForTaskRequestBodyData(StrictModel):
    followers: list[str] = Field(default=..., validation_alias="followers", serialization_alias="followers", description="A list of users to add as followers, where each entry can be the string 'me', a user's email address, or a user's GID. Order is not significant.")
class AddFollowersForTaskRequestBody(StrictModel):
    """The followers to add to the task."""
    data: AddFollowersForTaskRequestBodyData
class AddFollowersForTaskRequest(StrictModel):
    """Adds one or more followers to a specified task, associating them with it for updates and visibility. Returns the complete updated task record upon success."""
    path: AddFollowersForTaskRequestPath
    body: AddFollowersForTaskRequestBody

# Operation: remove_task_followers
class RemoveFollowerForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task from which followers will be removed.")
class RemoveFollowerForTaskRequestBodyData(StrictModel):
    followers: list[str] = Field(default=..., validation_alias="followers", serialization_alias="followers", description="A list of users to remove as followers from the task. Each item can be the string 'me', a user's email address, or a user's GID. Order is not significant.")
class RemoveFollowerForTaskRequestBody(StrictModel):
    """The followers to remove from the task."""
    data: RemoveFollowerForTaskRequestBodyData
class RemoveFollowerForTaskRequest(StrictModel):
    """Removes one or more specified followers from a task, leaving all other followers unaffected. Returns the complete, updated task record after the removal."""
    path: RemoveFollowerForTaskRequestPath
    body: RemoveFollowerForTaskRequestBody

# Operation: get_task_by_custom_id
class GetTaskForCustomIdRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier for the workspace or organization in which to search for the task.")
    custom_id: str = Field(default=..., description="The custom ID shortcode assigned to the task, typically formatted as a prefix followed by a number (e.g., a project code and sequence number).")
class GetTaskForCustomIdRequest(StrictModel):
    """Retrieves a task using its human-readable custom ID shortcode within a specified workspace. Useful when referencing tasks by their display identifiers rather than internal GIDs."""
    path: GetTaskForCustomIdRequestPath

# Operation: search_tasks
class SearchTasksForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization to search within.")
class SearchTasksForWorkspaceRequestQuery(StrictModel):
    text: str | None = Field(default=None, description="Full-text search string matched against both task name and description.")
    resource_subtype: Literal["default_task", "milestone", "approval", "custom"] | None = Field(default=None, description="Filters results to tasks of a specific subtype. Use 'default_task' for standard tasks, 'milestone' for milestones, 'approval' for approval tasks, or 'custom' for custom task types.")
    assignee_any: str | None = Field(default=None, validation_alias="assignee.any", serialization_alias="assignee.any", description="Returns tasks assigned to any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    assignee_not: str | None = Field(default=None, validation_alias="assignee.not", serialization_alias="assignee.not", description="Excludes tasks assigned to any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    portfolios_any: str | None = Field(default=None, validation_alias="portfolios.any", serialization_alias="portfolios.any", description="Returns tasks belonging to any of the specified portfolios. Accepts a comma-separated list of portfolio GIDs.")
    projects_any: str | None = Field(default=None, validation_alias="projects.any", serialization_alias="projects.any", description="Returns tasks belonging to any of the specified projects. Accepts a comma-separated list of project GIDs. Note: combining with sections.any returns tasks matching either filter, not just the section.")
    projects_not: str | None = Field(default=None, validation_alias="projects.not", serialization_alias="projects.not", description="Excludes tasks belonging to any of the specified projects. Accepts a comma-separated list of project GIDs.")
    projects_all: str | None = Field(default=None, validation_alias="projects.all", serialization_alias="projects.all", description="Returns tasks belonging to all of the specified projects. Accepts a comma-separated list of project GIDs.")
    sections_any: str | None = Field(default=None, validation_alias="sections.any", serialization_alias="sections.any", description="Returns tasks in any of the specified sections or columns. Accepts a comma-separated list of section GIDs. To retrieve only tasks in a section, omit projects.any.")
    sections_not: str | None = Field(default=None, validation_alias="sections.not", serialization_alias="sections.not", description="Excludes tasks in any of the specified sections or columns. Accepts a comma-separated list of section GIDs.")
    sections_all: str | None = Field(default=None, validation_alias="sections.all", serialization_alias="sections.all", description="Returns tasks in all of the specified sections or columns. Accepts a comma-separated list of section GIDs.")
    tags_any: str | None = Field(default=None, validation_alias="tags.any", serialization_alias="tags.any", description="Returns tasks with any of the specified tags. Accepts a comma-separated list of tag GIDs.")
    tags_not: str | None = Field(default=None, validation_alias="tags.not", serialization_alias="tags.not", description="Excludes tasks with any of the specified tags. Accepts a comma-separated list of tag GIDs.")
    tags_all: str | None = Field(default=None, validation_alias="tags.all", serialization_alias="tags.all", description="Returns tasks that have all of the specified tags. Accepts a comma-separated list of tag GIDs.")
    teams_any: str | None = Field(default=None, validation_alias="teams.any", serialization_alias="teams.any", description="Returns tasks belonging to any of the specified teams. Accepts a comma-separated list of team GIDs.")
    followers_any: str | None = Field(default=None, validation_alias="followers.any", serialization_alias="followers.any", description="Returns tasks followed by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    followers_not: str | None = Field(default=None, validation_alias="followers.not", serialization_alias="followers.not", description="Excludes tasks followed by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    created_by_any: str | None = Field(default=None, validation_alias="created_by.any", serialization_alias="created_by.any", description="Returns tasks created by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    created_by_not: str | None = Field(default=None, validation_alias="created_by.not", serialization_alias="created_by.not", description="Excludes tasks created by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    assigned_by_any: str | None = Field(default=None, validation_alias="assigned_by.any", serialization_alias="assigned_by.any", description="Returns tasks assigned by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    assigned_by_not: str | None = Field(default=None, validation_alias="assigned_by.not", serialization_alias="assigned_by.not", description="Excludes tasks assigned by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    liked_by_not: str | None = Field(default=None, validation_alias="liked_by.not", serialization_alias="liked_by.not", description="Excludes tasks liked by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    commented_on_by_not: str | None = Field(default=None, validation_alias="commented_on_by.not", serialization_alias="commented_on_by.not", description="Excludes tasks commented on by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'.")
    due_on_before: str | None = Field(default=None, validation_alias="due_on.before", serialization_alias="due_on.before", description="Returns tasks with a due date strictly before the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    due_on_after: str | None = Field(default=None, validation_alias="due_on.after", serialization_alias="due_on.after", description="Returns tasks with a due date strictly after the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    due_on: str | None = Field(default=None, description="Returns tasks with a due date exactly matching the specified date, or pass null to match tasks with no due date. Accepts an ISO 8601 date string or null.", json_schema_extra={'format': 'date'})
    due_at_before: str | None = Field(default=None, validation_alias="due_at.before", serialization_alias="due_at.before", description="Returns tasks with a due datetime strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    due_at_after: str | None = Field(default=None, validation_alias="due_at.after", serialization_alias="due_at.after", description="Returns tasks with a due datetime strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    start_on_before: str | None = Field(default=None, validation_alias="start_on.before", serialization_alias="start_on.before", description="Returns tasks with a start date strictly before the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    start_on_after: str | None = Field(default=None, validation_alias="start_on.after", serialization_alias="start_on.after", description="Returns tasks with a start date strictly after the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    start_on: str | None = Field(default=None, description="Returns tasks with a start date exactly matching the specified date, or pass null to match tasks with no start date. Accepts an ISO 8601 date string or null.", json_schema_extra={'format': 'date'})
    created_on_before: str | None = Field(default=None, validation_alias="created_on.before", serialization_alias="created_on.before", description="Returns tasks created strictly before the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    created_on_after: str | None = Field(default=None, validation_alias="created_on.after", serialization_alias="created_on.after", description="Returns tasks created strictly after the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    created_on: str | None = Field(default=None, description="Returns tasks created on exactly the specified date, or pass null to match tasks with no creation date recorded. Accepts an ISO 8601 date string or null.", json_schema_extra={'format': 'date'})
    created_at_before: str | None = Field(default=None, validation_alias="created_at.before", serialization_alias="created_at.before", description="Returns tasks created strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    created_at_after: str | None = Field(default=None, validation_alias="created_at.after", serialization_alias="created_at.after", description="Returns tasks created strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    completed_on_before: str | None = Field(default=None, validation_alias="completed_on.before", serialization_alias="completed_on.before", description="Returns tasks completed strictly before the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    completed_on_after: str | None = Field(default=None, validation_alias="completed_on.after", serialization_alias="completed_on.after", description="Returns tasks completed strictly after the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    completed_on: str | None = Field(default=None, description="Returns tasks completed on exactly the specified date, or pass null to match tasks with no completion date. Accepts an ISO 8601 date string or null.", json_schema_extra={'format': 'date'})
    completed_at_before: str | None = Field(default=None, validation_alias="completed_at.before", serialization_alias="completed_at.before", description="Returns tasks completed strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    completed_at_after: str | None = Field(default=None, validation_alias="completed_at.after", serialization_alias="completed_at.after", description="Returns tasks completed strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    modified_on_before: str | None = Field(default=None, validation_alias="modified_on.before", serialization_alias="modified_on.before", description="Returns tasks last modified strictly before the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    modified_on_after: str | None = Field(default=None, validation_alias="modified_on.after", serialization_alias="modified_on.after", description="Returns tasks last modified strictly after the specified date. Accepts an ISO 8601 date string.", json_schema_extra={'format': 'date'})
    modified_on: str | None = Field(default=None, description="Returns tasks last modified on exactly the specified date, or pass null to match tasks with no modification date. Accepts an ISO 8601 date string or null.", json_schema_extra={'format': 'date'})
    modified_at_before: str | None = Field(default=None, validation_alias="modified_at.before", serialization_alias="modified_at.before", description="Returns tasks last modified strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    modified_at_after: str | None = Field(default=None, validation_alias="modified_at.after", serialization_alias="modified_at.after", description="Returns tasks last modified strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone.", json_schema_extra={'format': 'date-time'})
    is_blocking: bool | None = Field(default=None, description="When true, filters to incomplete tasks that have at least one incomplete dependent task blocking them from being considered done.")
    is_blocked: bool | None = Field(default=None, description="When true, filters to tasks that have at least one incomplete dependency that must be resolved before the task can be completed.")
    has_attachment: bool | None = Field(default=None, description="When true, filters to tasks that have one or more file attachments.")
    completed: bool | None = Field(default=None, description="When true, returns only completed tasks; when false, returns only incomplete tasks. Omit to return both.")
    is_subtask: bool | None = Field(default=None, description="When true, filters results to subtasks only; when false, excludes subtasks from results.")
    sort_by: Literal["due_date", "created_at", "completed_at", "likes", "modified_at"] | None = Field(default=None, description="Field by which to sort the returned tasks. Defaults to 'modified_at'. Use in combination with sort_ascending to control order direction.")
    sort_ascending: bool | None = Field(default=None, description="When true, results are sorted in ascending order by the sort_by field; when false (default), results are sorted in descending order.")
class SearchTasksForWorkspaceRequest(StrictModel):
    """Search tasks within a workspace using advanced filters including text, assignees, projects, dates, custom fields, and more. Requires a premium Asana workspace or premium team membership; results are eventually consistent and support manual pagination via sort and limit."""
    path: SearchTasksForWorkspaceRequestPath
    query: SearchTasksForWorkspaceRequestQuery | None = None

# Operation: get_team_membership
class GetTeamMembershipRequestPath(StrictModel):
    team_membership_gid: str = Field(default=..., description="The unique identifier (GID) of the team membership record to retrieve.")
class GetTeamMembershipRequest(StrictModel):
    """Retrieves the complete membership record for a single team membership, including details about the member and their associated team. Requires the `team_memberships:read` scope, with additional `teams:read` scope needed to access team details."""
    path: GetTeamMembershipRequestPath

# Operation: list_team_memberships
class GetTeamMembershipsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of team membership records to return per page, between 1 and 100.", ge=1, le=100)
    team: str | None = Field(default=None, description="The globally unique identifier (GID) of the team whose memberships should be returned.")
    user: str | None = Field(default=None, description="Identifies the user whose team memberships to retrieve; accepts the string \"me\", a user email address, or a user GID. Must be used together with the workspace parameter.")
    workspace: str | None = Field(default=None, description="The globally unique identifier (GID) of the workspace to scope the results to. Must be used together with the user parameter.")
class GetTeamMembershipsRequest(StrictModel):
    """Retrieves a list of compact team membership records, optionally filtered by team, user, or workspace. Requires the team_memberships:read scope."""
    query: GetTeamMembershipsRequestQuery | None = None

# Operation: list_team_memberships_for_team
class GetTeamMembershipsForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier of the team whose memberships you want to retrieve.")
class GetTeamMembershipsForTeamRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of membership records to return per page, accepting values between 1 and 100.", ge=1, le=100)
class GetTeamMembershipsForTeamRequest(StrictModel):
    """Retrieves all team memberships for a specified team, returning compact membership records for each member. Requires the team_memberships:read scope."""
    path: GetTeamMembershipsForTeamRequestPath
    query: GetTeamMembershipsForTeamRequestQuery | None = None

# Operation: list_user_team_memberships
class GetTeamMembershipsForUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier for the user whose team memberships will be retrieved. Accepts the string 'me' for the authenticated user, a user's email address, or a user's global ID (gid).")
class GetTeamMembershipsForUserRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of team membership records to return per page, allowing pagination through large result sets. Must be an integer between 1 and 100.", ge=1, le=100)
    workspace: str = Field(default=..., description="The globally unique identifier (gid) of the workspace used to scope the team membership results to a specific organization or workspace.")
class GetTeamMembershipsForUserRequest(StrictModel):
    """Retrieves all team memberships for a specified user within a given workspace, returning compact membership records. Requires the team_memberships:read scope."""
    path: GetTeamMembershipsForUserRequestPath
    query: GetTeamMembershipsForUserRequestQuery

# Operation: create_team
class CreateTeamRequestBody(StrictModel):
    """The team to create."""
    data: TeamRequest | None = Field(default=None, description="The configuration details for the new team, such as name and settings.")
class CreateTeamRequest(StrictModel):
    """Creates a new team within the current workspace. Use this to organize members and resources under a named group."""
    body: CreateTeamRequestBody | None = None

# Operation: get_team
class GetTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier (GID) for the team to retrieve.")
class GetTeamRequest(StrictModel):
    """Retrieves the full details for a single team by its unique identifier. Requires the teams:read scope."""
    path: GetTeamRequestPath

# Operation: update_team
class UpdateTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier for the team to be updated.")
class UpdateTeamRequestBody(StrictModel):
    """The team to update."""
    data: TeamRequest | None = Field(default=None, description="The team fields to update, provided as a data object containing the properties and their new values.")
class UpdateTeamRequest(StrictModel):
    """Updates the properties of an existing team within the current workspace. Use this to modify team details such as name or description."""
    path: UpdateTeamRequestPath
    body: UpdateTeamRequestBody | None = None

# Operation: list_workspace_teams
class GetTeamsForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier for the workspace or organization whose teams you want to retrieve.")
class GetTeamsForWorkspaceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of team records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetTeamsForWorkspaceRequest(StrictModel):
    """Retrieves compact records for all teams within a specified workspace or organization that are visible to the authorized user. Requires the 'teams:read' scope."""
    path: GetTeamsForWorkspaceRequestPath
    query: GetTeamsForWorkspaceRequestQuery | None = None

# Operation: list_user_teams
class GetTeamsForUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier for the user whose teams you want to retrieve. Accepts the literal string 'me' for the authenticated user, a user's email address, or a numeric user GID.")
class GetTeamsForUserRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of team records to return per page. Must be an integer between 1 and 100 inclusive.", ge=1, le=100)
    organization: str = Field(default=..., description="The GID of the workspace or organization used to filter the returned teams, ensuring only teams within that context are included.")
class GetTeamsForUserRequest(StrictModel):
    """Retrieves all teams that a specified user belongs to, optionally filtered by a workspace or organization. Returns compact team records for the given user."""
    path: GetTeamsForUserRequestPath
    query: GetTeamsForUserRequestQuery

# Operation: add_team_member
class AddUserForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The unique identifier of the team to which the user will be added.")
class AddUserForTeamRequestBodyData(StrictModel):
    user: str | None = Field(default=None, validation_alias="user", serialization_alias="user", description="The identifier of the user to add to the team — accepts the literal string 'me' for the current user, a user's email address, or a user's globally unique identifier (GID).")
class AddUserForTeamRequestBody(StrictModel):
    """The user to add to the team."""
    data: AddUserForTeamRequestBodyData | None = None
class AddUserForTeamRequest(StrictModel):
    """Adds a user to the specified team, creating a new team membership record. The requesting user must already be a member of the team, and the user being added must belong to the same organization."""
    path: AddUserForTeamRequestPath
    body: AddUserForTeamRequestBody | None = None

# Operation: remove_team_member
class RemoveUserForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier of the team from which the user will be removed.")
class RemoveUserForTeamRequestBodyData(StrictModel):
    user: str | None = Field(default=None, validation_alias="user", serialization_alias="user", description="The identifier of the user to remove, accepted as the string 'me' (for the requesting user), an email address, or a user GID.")
class RemoveUserForTeamRequestBody(StrictModel):
    """The user to remove from the team."""
    data: RemoveUserForTeamRequestBodyData | None = None
class RemoveUserForTeamRequest(StrictModel):
    """Removes a specified user from a team. The user making this request must be a member of the team to remove themselves or others."""
    path: RemoveUserForTeamRequestPath
    body: RemoveUserForTeamRequestBody | None = None

# Operation: get_time_period
class GetTimePeriodRequestPath(StrictModel):
    time_period_gid: str = Field(default=..., description="The globally unique identifier of the time period to retrieve.")
class GetTimePeriodRequest(StrictModel):
    """Retrieves the full details of a specific time period by its unique identifier. Useful for accessing goal-tracking intervals such as fiscal quarters or annual periods."""
    path: GetTimePeriodRequestPath

# Operation: list_time_periods
class GetTimePeriodsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of time period records to return per page, between 1 and 100.", ge=1, le=100)
    start_on: str | None = Field(default=None, description="Filters results to time periods starting on or after this date, specified in ISO 8601 date format.", json_schema_extra={'format': 'date'})
    end_on: str | None = Field(default=None, description="Filters results to time periods ending on or before this date, specified in ISO 8601 date format.", json_schema_extra={'format': 'date'})
    workspace: str = Field(default=..., description="The globally unique identifier of the workspace whose time periods should be retrieved.")
class GetTimePeriodsRequest(StrictModel):
    """Retrieves a paginated list of compact time period records for a given workspace. Useful for browsing available time periods such as fiscal quarters or sprints."""
    query: GetTimePeriodsRequestQuery

# Operation: list_task_time_tracking_entries
class GetTimeTrackingEntriesForTaskRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The task to operate on.")
class GetTimeTrackingEntriesForTaskRequest(StrictModel):
    """Retrieves all time tracking entries logged against a specific task. Requires the time_tracking_entries:read scope."""
    path: GetTimeTrackingEntriesForTaskRequestPath

# Operation: create_time_entry
class CreateTimeTrackingEntryRequestPath(StrictModel):
    task_gid: str = Field(default=..., description="The unique identifier (GID) of the task on which the time tracking entry will be created.")
class CreateTimeTrackingEntryRequestBodyData(StrictModel):
    duration_minutes: int | None = Field(default=None, validation_alias="duration_minutes", serialization_alias="duration_minutes", description="The amount of time to log for this entry, expressed in whole minutes. Must be greater than 0.")
    entered_on: str | None = Field(default=None, validation_alias="entered_on", serialization_alias="entered_on", description="The calendar date this time entry is logged against, in ISO 8601 date format (YYYY-MM-DD). Defaults to today if omitted.", json_schema_extra={'format': 'date'})
    attributable_to: str | None = Field(default=None, validation_alias="attributable_to", serialization_alias="attributable_to", description="The GID of the project this time entry should be attributed to, allowing time to be associated with a specific project context.")
    billable_status: Literal["billable", "nonBillable", "notApplicable"] | None = Field(default=None, validation_alias="billable_status", serialization_alias="billable_status", description="The billable classification of this time entry: 'billable' for client-chargeable time, 'nonBillable' for internal time, or 'notApplicable' when billing status is not relevant.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A free-text note describing the work performed during this time entry, providing context for the logged time.")
class CreateTimeTrackingEntryRequestBody(StrictModel):
    """Information about the time tracking entry."""
    data: CreateTimeTrackingEntryRequestBodyData | None = None
class CreateTimeTrackingEntryRequest(StrictModel):
    """Logs a new time tracking entry on a specified task, recording duration, date, billable status, and optional project attribution. Returns the newly created time tracking entry record."""
    path: CreateTimeTrackingEntryRequestPath
    body: CreateTimeTrackingEntryRequestBody | None = None

# Operation: get_time_tracking_entry
class GetTimeTrackingEntryRequestPath(StrictModel):
    time_tracking_entry_gid: str = Field(default=..., description="The globally unique identifier (GID) of the time tracking entry to retrieve.")
class GetTimeTrackingEntryRequest(StrictModel):
    """Retrieves the complete record for a single time tracking entry. Requires the time_tracking_entries:read scope."""
    path: GetTimeTrackingEntryRequestPath

# Operation: update_time_tracking_entry
class UpdateTimeTrackingEntryRequestPath(StrictModel):
    time_tracking_entry_gid: str = Field(default=..., description="The globally unique identifier of the time tracking entry to update.")
class UpdateTimeTrackingEntryRequestBodyData(StrictModel):
    duration_minutes: int | None = Field(default=None, validation_alias="duration_minutes", serialization_alias="duration_minutes", description="The amount of time to log for this entry, expressed in whole minutes.")
    entered_on: str | None = Field(default=None, validation_alias="entered_on", serialization_alias="entered_on", description="The calendar date on which this time entry is logged, in ISO 8601 date format. Defaults to today if not specified.", json_schema_extra={'format': 'date'})
    attributable_to: str | None = Field(default=None, validation_alias="attributable_to", serialization_alias="attributable_to", description="The unique identifier (GID) of the project to which this time entry's effort is attributed.")
    billable_status: Literal["billable", "nonBillable", "notApplicable"] | None = Field(default=None, validation_alias="billable_status", serialization_alias="billable_status", description="The billable status of this time entry. Use 'billable' for client-chargeable work, 'nonBillable' for internal work, or 'notApplicable' when billing status is irrelevant.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A free-text description summarizing the work performed during this time entry.")
class UpdateTimeTrackingEntryRequestBody(StrictModel):
    """The updated fields for the time tracking entry."""
    data: UpdateTimeTrackingEntryRequestBodyData | None = None
class UpdateTimeTrackingEntryRequest(StrictModel):
    """Updates an existing time tracking entry by its unique identifier, modifying only the fields provided while leaving all other fields unchanged. Returns the complete updated time tracking entry record."""
    path: UpdateTimeTrackingEntryRequestPath
    body: UpdateTimeTrackingEntryRequestBody | None = None

# Operation: delete_time_tracking_entry
class DeleteTimeTrackingEntryRequestPath(StrictModel):
    time_tracking_entry_gid: str = Field(default=..., description="The globally unique identifier (GID) of the time tracking entry to delete.")
class DeleteTimeTrackingEntryRequest(StrictModel):
    """Permanently deletes a specific time tracking entry by its unique identifier. Returns an empty data record upon successful deletion."""
    path: DeleteTimeTrackingEntryRequestPath

# Operation: list_time_tracking_entries
class GetTimeTrackingEntriesRequestQuery(StrictModel):
    task: str | None = Field(default=None, description="The globally unique identifier of the task to scope results to only time tracking entries associated with that task.")
    attributable_to: str | None = Field(default=None, description="The globally unique identifier of the project to scope results to only time tracking entries attributed to that project.")
    portfolio: str | None = Field(default=None, description="The globally unique identifier of the portfolio to scope results to only time tracking entries belonging to tasks within that portfolio.")
    user: str | None = Field(default=None, description="The globally unique identifier of the user to scope results to only time tracking entries logged by that user.")
    workspace: str | None = Field(default=None, description="The globally unique identifier of the workspace to scope results to. When filtering by workspace, at least one of `entered_on_start_date` or `entered_on_end_date` must also be provided.")
    entered_on_start_date: str | None = Field(default=None, description="The inclusive start date for filtering entries by their entry date, in ISO 8601 date format (YYYY-MM-DD). Use together with `entered_on_end_date` to define a date range.", json_schema_extra={'format': 'date'})
    entered_on_end_date: str | None = Field(default=None, description="The inclusive end date for filtering entries by their entry date, in ISO 8601 date format (YYYY-MM-DD). Use together with `entered_on_start_date` to define a date range.", json_schema_extra={'format': 'date'})
    timesheet_approval_status: str | None = Field(default=None, description="The globally unique identifier of a timesheet approval status to scope results to only time tracking entries matching that approval state.")
class GetTimeTrackingEntriesRequest(StrictModel):
    """Retrieves a list of time tracking entries, optionally filtered by task, project, portfolio, user, workspace, date range, or timesheet approval status. Requires the `time_tracking_entries:read` scope."""
    query: GetTimeTrackingEntriesRequestQuery | None = None

# Operation: get_timesheet_approval_status
class GetTimesheetApprovalStatusRequestPath(StrictModel):
    timesheet_approval_status_gid: str = Field(default=..., description="The globally unique identifier (GID) of the timesheet approval status record to retrieve.")
class GetTimesheetApprovalStatusRequest(StrictModel):
    """Retrieves the complete record for a single timesheet approval status, including its current state and associated metadata. Requires the timesheet_approval_statuses:read scope."""
    path: GetTimesheetApprovalStatusRequestPath

# Operation: update_timesheet_approval_status
class UpdateTimesheetApprovalStatusRequestPath(StrictModel):
    timesheet_approval_status_gid: str = Field(default=..., description="The globally unique identifier of the timesheet approval status record to update.")
class UpdateTimesheetApprovalStatusRequestBodyData(StrictModel):
    approval_status: Literal["submitted", "draft", "approved", "rejected"] = Field(default=..., validation_alias="approval_status", serialization_alias="approval_status", description="The target approval state to transition to. Valid values are 'submitted' (submit for review), 'draft' (recall a submission), 'approved' (approve the timesheet), or 'rejected' (reject the timesheet). Allowed transitions depend on the current state of the record.")
    message: str | None = Field(default=None, validation_alias="message", serialization_alias="message", description="An optional message to accompany the status transition, such as a reason for approval or rejection.")
class UpdateTimesheetApprovalStatusRequestBody(StrictModel):
    """The fields to update on the timesheet approval status."""
    data: UpdateTimesheetApprovalStatusRequestBodyData
class UpdateTimesheetApprovalStatusRequest(StrictModel):
    """Transitions a timesheet approval status to a new state, such as submitting, recalling, approving, or rejecting. Only the provided fields are updated; invalid state transitions return a 400 error."""
    path: UpdateTimesheetApprovalStatusRequestPath
    body: UpdateTimesheetApprovalStatusRequestBody

# Operation: list_timesheet_approval_statuses
class GetTimesheetApprovalStatusesRequestQuery(StrictModel):
    workspace: str = Field(default=..., description="The globally unique identifier of the workspace whose timesheet approval statuses should be retrieved.")
    user: str | None = Field(default=None, description="The globally unique identifier of a specific user to narrow results to only their timesheet approval statuses.")
    from_date: str | None = Field(default=None, description="The inclusive start date for filtering timesheet approval statuses, in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    to_date: str | None = Field(default=None, description="The inclusive end date for filtering timesheet approval statuses, in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    approval_statuses: str | None = Field(default=None, description="One or more approval status values to filter by; accepted values are draft, submitted, approved, or rejected. Multiple values may be provided as a comma-separated list.")
class GetTimesheetApprovalStatusesRequest(StrictModel):
    """Retrieves a list of timesheet approval statuses for a given workspace, with optional filtering by user, date range, or approval status. Requires the timesheet_approval_statuses:read scope."""
    query: GetTimesheetApprovalStatusesRequestQuery

# Operation: create_timesheet_approval_status
class CreateTimesheetApprovalStatusRequestBodyData(StrictModel):
    user: str = Field(default=..., validation_alias="user", serialization_alias="user", description="The globally unique identifier of the user whose timesheet approval status is being created.")
    workspace: str = Field(default=..., validation_alias="workspace", serialization_alias="workspace", description="The globally unique identifier of the workspace in which the timesheet exists.")
    start_date: str = Field(default=..., validation_alias="start_date", serialization_alias="start_date", description="The start date of the timesheet week in ISO 8601 date format; must be a Monday.", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., validation_alias="end_date", serialization_alias="end_date", description="The end date of the timesheet week in ISO 8601 date format; must be the Sunday immediately following the start date.", json_schema_extra={'format': 'date'})
class CreateTimesheetApprovalStatusRequestBody(StrictModel):
    """The timesheet approval status to create."""
    data: CreateTimesheetApprovalStatusRequestBodyData
class CreateTimesheetApprovalStatusRequest(StrictModel):
    """Creates a new timesheet approval status for a specific user's weekly timesheet within a workspace. The week must span exactly Monday through the following Sunday."""
    body: CreateTimesheetApprovalStatusRequestBody

# Operation: search_workspace_typeahead
class TypeaheadForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier for the workspace or organization to search within.")
class TypeaheadForWorkspaceRequestQuery(StrictModel):
    resource_type: Literal["custom_field", "goal", "project", "project_template", "portfolio", "tag", "task", "team", "user"] = Field(default=..., description="The type of resource to search for. Accepts a single type from the supported set: custom_field, goal, project, project_template, portfolio, tag, task, team, or user. Multiple types are not supported.")
    query: str | None = Field(default=None, description="The search string used to match relevant objects by name or other identifying fields. Omitting or passing an empty string returns results ordered by relevance heuristics (e.g., recency or contact frequency) for the authenticated user.")
    count: int | None = Field(default=None, description="The maximum number of results to return, between 1 and 100. Defaults to 20 if omitted; if fewer matches exist than requested, all available results are returned.")
class TypeaheadForWorkspaceRequest(StrictModel):
    """Performs a fast typeahead/auto-completion search within a workspace, returning a compact list of matching objects (users, projects, tasks, etc.) ordered by relevance. Results are limited to a single page and are optimized for speed rather than exhaustive accuracy."""
    path: TypeaheadForWorkspaceRequestPath
    query: TypeaheadForWorkspaceRequestQuery

# Operation: get_user_task_list
class GetUserTaskListRequestPath(StrictModel):
    user_task_list_gid: str = Field(default=..., description="The globally unique identifier for the user task list to retrieve.")
class GetUserTaskListRequest(StrictModel):
    """Retrieves the full record for a specific user task list, including all associated metadata. Requires the tasks:read scope."""
    path: GetUserTaskListRequestPath

# Operation: get_user_task_list_by_user
class GetUserTaskListForUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier for the user whose task list you want to retrieve. Accepts the literal string 'me' for the authenticated user, a user's email address, or a user's global ID (gid).")
class GetUserTaskListForUserRequestQuery(StrictModel):
    workspace: str = Field(default=..., description="The global ID (gid) of the workspace in which to look up the user's task list. Each user has one task list per workspace.")
class GetUserTaskListForUserRequest(StrictModel):
    """Retrieves the full task list record for a specified user within a given workspace. Requires the tasks:read scope."""
    path: GetUserTaskListForUserRequestPath
    query: GetUserTaskListForUserRequestQuery

# Operation: list_users
class GetUsersRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The unique ID of a workspace or organization to restrict results to only users belonging to that workspace or organization.")
    team: str | None = Field(default=None, description="The unique ID of a team to restrict results to only users belonging to that team.")
    limit: int | None = Field(default=None, description="The number of user records to return per page. Must be an integer between 1 and 100 inclusive.", ge=1, le=100)
class GetUsersRequest(StrictModel):
    """Retrieves user records across all workspaces and organizations accessible to the authenticated user, with optional filtering by workspace or team. Requires the 'users:read' scope and returns results sorted by user ID."""
    query: GetUsersRequestQuery | None = None

# Operation: get_user
class GetUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier for the user to retrieve. Accepts a user GID, an email address, or the string 'me' to reference the currently authenticated user.")
class GetUserRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The GID of a workspace used to filter the user results, useful when a user belongs to multiple workspaces.")
class GetUserRequest(StrictModel):
    """Retrieves the full profile record for a single user, identified by their GID, email address, or the shorthand 'me' for the authenticated user. Optionally scoped to a specific workspace."""
    path: GetUserRequestPath
    query: GetUserRequestQuery | None = None

# Operation: update_user
class UpdateUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier for the target user, which can be the literal string 'me' to reference the authenticated user, a user's email address, or a numeric user GID.")
class UpdateUserRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="Filters the operation to a specific workspace by its GID, useful when a user belongs to multiple workspaces.")
class UpdateUserRequestBody(StrictModel):
    """The user to update."""
    data: UserUpdateRequest | None = Field(default=None, description="An object containing the user fields to update; only the fields included here will be modified, all omitted fields retain their current values.")
class UpdateUserRequest(StrictModel):
    """Updates an existing user's profile by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated user record."""
    path: UpdateUserRequestPath
    query: UpdateUserRequestQuery | None = None
    body: UpdateUserRequestBody | None = None

# Operation: list_user_favorites
class GetFavoritesForUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier of the user whose favorites to retrieve. Accepts the literal string 'me' to reference the authenticated user, a user's email address, or a user's GID.")
class GetFavoritesForUserRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of favorite items to return per page. Must be between 1 and 100 inclusive.", ge=1, le=100)
    resource_type: Literal["portfolio", "project", "tag", "task", "user", "project_template"] = Field(default=..., description="The type of Asana resource to filter favorites by. Must be one of the supported resource types: portfolio, project, tag, task, user, or project_template.")
    workspace: str = Field(default=..., description="The GID of the workspace in which to look up the user's favorites. All returned favorites will belong to this workspace.")
class GetFavoritesForUserRequest(StrictModel):
    """Retrieves all favorites for a specified user within a given workspace, filtered by resource type, ordered as they appear in the user's Asana sidebar. Note: currently only returns favorites for the authenticated user."""
    path: GetFavoritesForUserRequestPath
    query: GetFavoritesForUserRequestQuery

# Operation: list_team_members
class GetUsersForTeamRequestPath(StrictModel):
    team_gid: str = Field(default=..., description="The globally unique identifier of the team whose members you want to retrieve.")
class GetUsersForTeamRequest(StrictModel):
    """Retrieves all users who are members of a specified team, returned as compact records sorted alphabetically. Limited to 2000 results; use the users endpoint for larger result sets."""
    path: GetUsersForTeamRequestPath

# Operation: list_workspace_users
class GetUsersForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization whose users you want to retrieve.")
class GetUsersForWorkspaceRequest(StrictModel):
    """Retrieves a compact list of all users in the specified workspace or organization, sorted alphabetically. Results are capped at 2000 users; use the /users endpoint for larger result sets."""
    path: GetUsersForWorkspaceRequestPath

# Operation: get_workspace_user
class GetUserForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization in which to look up the user.")
    user_gid: str = Field(default=..., description="The identifier for the target user — accepts the literal string \"me\" (for the authenticated user), a user's email address, or a user's globally unique identifier (GID).")
class GetUserForWorkspaceRequest(StrictModel):
    """Retrieves the full profile record for a specific user within a given workspace or organization. Requires the `users:read` scope."""
    path: GetUserForWorkspaceRequestPath

# Operation: update_workspace_user
class UpdateUserForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization in which the user will be updated.")
    user_gid: str = Field(default=..., description="The identifier of the user to update, which can be the string 'me' to reference the authenticated user, a user's email address, or a user's globally unique identifier (GID).")
class UpdateUserForWorkspaceRequestBody(StrictModel):
    """The user to update."""
    data: UserUpdateRequest | None = Field(default=None, description="The user fields to update within the workspace. Only fields included here will be changed; omitted fields retain their current values.")
class UpdateUserForWorkspaceRequest(StrictModel):
    """Updates an existing user's information within a specified workspace or organization. Only the fields provided in the request body will be modified; all other fields remain unchanged."""
    path: UpdateUserForWorkspaceRequestPath
    body: UpdateUserForWorkspaceRequestBody | None = None

# Operation: get_webhook
class GetWebhookRequestPath(StrictModel):
    webhook_gid: str = Field(default=..., description="The globally unique identifier of the webhook to retrieve.")
class GetWebhookRequest(StrictModel):
    """Retrieves the full details of a specific webhook by its unique identifier. Requires the webhooks:read scope."""
    path: GetWebhookRequestPath

# Operation: delete_webhook
class DeleteWebhookRequestPath(StrictModel):
    webhook_gid: str = Field(default=..., description="The globally unique identifier of the webhook to permanently delete.")
class DeleteWebhookRequest(StrictModel):
    """Permanently deletes a webhook, stopping all future event deliveries to its target URL. Note that in-flight requests sent before deletion may still arrive, but no new requests will be issued."""
    path: DeleteWebhookRequestPath

# Operation: get_workspace_membership
class GetWorkspaceMembershipRequestPath(StrictModel):
    workspace_membership_gid: str = Field(default=..., description="The unique identifier (GID) of the workspace membership to retrieve.")
class GetWorkspaceMembershipRequest(StrictModel):
    """Retrieves the complete membership record for a single workspace membership, including details about the member and their role within the workspace."""
    path: GetWorkspaceMembershipRequestPath

# Operation: list_user_workspace_memberships
class GetWorkspaceMembershipsForUserRequestPath(StrictModel):
    user_gid: str = Field(default=..., description="The unique identifier for the user whose workspace memberships to retrieve. Accepts the literal string 'me' for the authenticated user, a registered email address, or a numeric user GID.")
class GetWorkspaceMembershipsForUserRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The number of membership records to return per page. Must be between 1 and 100 inclusive; use pagination to retrieve additional results beyond the first page.", ge=1, le=100)
class GetWorkspaceMembershipsForUserRequest(StrictModel):
    """Retrieves all workspace memberships for a specified user, returning compact membership records. Useful for discovering which workspaces a user belongs to."""
    path: GetWorkspaceMembershipsForUserRequestPath
    query: GetWorkspaceMembershipsForUserRequestQuery | None = None

# Operation: list_workspace_memberships
class GetWorkspaceMembershipsForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization whose memberships you want to retrieve.")
class GetWorkspaceMembershipsForWorkspaceRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="Filter memberships to a specific user, identified by the string 'me' (current user), an email address, or a user GID.")
    limit: int | None = Field(default=None, description="The number of membership records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetWorkspaceMembershipsForWorkspaceRequest(StrictModel):
    """Retrieves compact membership records for all members of a specified workspace or organization. Optionally filter results by a specific user."""
    path: GetWorkspaceMembershipsForWorkspaceRequestPath
    query: GetWorkspaceMembershipsForWorkspaceRequestQuery | None = None

# Operation: list_workspaces
class GetWorkspacesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Number of workspace records to return per page. Must be between 1 and 100.", ge=1, le=100)
class GetWorkspacesRequest(StrictModel):
    """Retrieves all workspaces visible to the authorized user. Returns compact records for each workspace, requiring the workspaces:read scope."""
    query: GetWorkspacesRequestQuery | None = None

# Operation: get_workspace
class GetWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier for the workspace or organization to retrieve.")
class GetWorkspaceRequest(StrictModel):
    """Retrieves the full details of a single workspace or organization. Requires the workspace's unique identifier to return its complete record."""
    path: GetWorkspaceRequestPath

# Operation: update_workspace
class UpdateWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier of the workspace or organization to update.")
class UpdateWorkspaceRequestBodyData(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The new display name to assign to the workspace.")
class UpdateWorkspaceRequestBody(StrictModel):
    """The workspace object with all updated properties."""
    data: UpdateWorkspaceRequestBodyData | None = None
class UpdateWorkspaceRequest(StrictModel):
    """Updates an existing workspace by modifying its properties, currently limited to renaming the workspace. Returns the complete updated workspace record."""
    path: UpdateWorkspaceRequestPath
    body: UpdateWorkspaceRequestBody | None = None

# Operation: add_workspace_user
class AddUserForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The unique identifier of the workspace or organization to which the user will be added.")
class AddUserForWorkspaceRequestBodyData(StrictModel):
    user: str | None = Field(default=None, validation_alias="user", serialization_alias="user", description="The identifier of the user to add, accepted as the literal string 'me' (current user), an email address, or a user GID.")
class AddUserForWorkspaceRequestBody(StrictModel):
    """The user to add to the workspace."""
    data: AddUserForWorkspaceRequestBodyData | None = None
class AddUserForWorkspaceRequest(StrictModel):
    """Adds a user to a workspace or organization by user ID or email address. Returns the full user record for the newly added user."""
    path: AddUserForWorkspaceRequestPath
    body: AddUserForWorkspaceRequestBody | None = None

# Operation: remove_workspace_user
class RemoveUserForWorkspaceRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The unique identifier of the workspace or organization from which the user will be removed.")
class RemoveUserForWorkspaceRequestBodyData(StrictModel):
    user: str | None = Field(default=None, validation_alias="user", serialization_alias="user", description="The identifier of the user to remove, which can be the literal string 'me', an email address, or a user's globally unique ID.")
class RemoveUserForWorkspaceRequestBody(StrictModel):
    """The user to remove from the workspace."""
    data: RemoveUserForWorkspaceRequestBodyData | None = None
class RemoveUserForWorkspaceRequest(StrictModel):
    """Removes a user from a workspace or organization, transferring ownership of their resources to the admin or PAT owner. The caller must be a workspace admin; the target user can be identified by their user ID or email address."""
    path: RemoveUserForWorkspaceRequestPath
    body: RemoveUserForWorkspaceRequestBody | None = None

# Operation: list_workspace_events
class GetWorkspaceEventsRequestPath(StrictModel):
    workspace_gid: str = Field(default=..., description="The globally unique identifier for the target workspace or organization whose events should be retrieved.")
class GetWorkspaceEventsRequestQuery(StrictModel):
    sync: str | None = Field(default=None, description="A sync token from a previous response used to fetch only events that occurred after that token was issued; omit this parameter on the first request to receive a fresh token. If the token has expired, the API returns a 412 error along with a new valid sync token to use going forward.")
class GetWorkspaceEventsRequest(StrictModel):
    """Retrieves all events that have occurred in a workspace since a given sync token was issued, enabling incremental polling for changes. Returns up to 1000 events per request; if more exist, the response includes a flag to continue paginating with a refreshed sync token."""
    path: GetWorkspaceEventsRequestPath
    query: GetWorkspaceEventsRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class AllocationBaseEffort(PermissiveModel):
    """The amount of time associated with the allocation, represented as a percentage or number of hours."""
    type_: Literal["hours", "percent"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The units used for tracking effort on an allocation, either \"hours\" or \"percent\".")
    value: float | None = Field(None, description="The numeric effort value on the allocation.")

class AllocationBase(PermissiveModel):
    """A generic Asana Resource, containing a globally unique identifier."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    start_date: str | None = Field(None, description="The localized day on which the allocation starts.", json_schema_extra={'format': 'date'})
    end_date: str | None = Field(None, description="The localized day on which the allocation ends.", json_schema_extra={'format': 'date'})
    effort: AllocationBaseEffort | None = Field(None, description="The amount of time associated with the allocation, represented as a percentage or number of hours.")

class AllocationRequestEffort(PermissiveModel):
    """The amount of time associated with the allocation, represented as a percentage or number of hours."""
    type_: Literal["hours", "percent"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The units used for tracking effort on an allocation, either \"hours\" or \"percent\".")
    value: float | None = Field(None, description="The numeric effort value on the allocation.")

class AllocationRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    start_date: str | None = Field(None, description="The localized day on which the allocation starts.", json_schema_extra={'format': 'date'})
    end_date: str | None = Field(None, description="The localized day on which the allocation ends.", json_schema_extra={'format': 'date'})
    effort: AllocationRequestEffort | None = Field(None, description="The amount of time associated with the allocation, represented as a percentage or number of hours.")
    assignee: str | None = Field(None, description="Globally unique identifier for the user or placeholder assigned to the allocation.")
    parent: str | None = Field(None, description="Globally unique identifier for the project the allocation is on.")

class AsanaNamedResource(PermissiveModel):
    """A generic Asana Resource, containing a globally unique identifier."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the object.")

class AsanaResource(PermissiveModel):
    """A generic Asana Resource, containing a globally unique identifier."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")

class BudgetActualRequest(PermissiveModel):
    """Defines the configuration of the actual portion of a budget. The actual value represents aggregated time tracking data attributed to the budget’s parent. This object controls which time entries are included based on their billable status. When no entries match the selected filter, the value will be 0."""
    billable_status_filter: Literal["billable", "non_billable", "any"] | None = Field(None, description="Billable status filter applied to time tracking entries contributing to the actual value. Determines which entries are included in aggregation. When not provided, defaults to `billable`.")

class BudgetCompact(PermissiveModel):
    """A *budget* object represents a budget for a given parent."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    budget_type: Literal["cost", "time"] | None = Field(None, description="The type of the budget, in \"cost\" or \"time\". The value of this property will dictate how the corresponding values for actual, estimate, and total are interpreted.")

class BudgetEstimateRequest(PermissiveModel):
    """Defines how the estimate portion of a budget is configured. This object controls whether the estimate is enabled, what data source it uses, and which tasks (by billable status) are included in calculating the estimate value. When disabled (enabled: false and source: none), the estimate is hidden and the API response will return `value: null` and `units: null` for this field."""
    billable_status_filter: Literal["billable", "non_billable", "any"] | None = Field(None, description="Billable status filter applied to the estimate when `source` is `tasks`. Ignored when `source` is `capacity_plans` or `none`. When not provided, defaults to `billable`.")
    source: Literal["none", "tasks", "capacity_plans"] | None = Field(None, description="The data source for the estimate. `tasks`: use task-level estimated time attributed to the parent. `capacity_plans`: use capacity plan estimates attributed to the parent. `none`: disables the estimate; only valid when `enabled` is `false`. When `enabled` is `true`, `source` must not be `none`.")
    enabled: bool | None = Field(None, description="Controls whether the estimate is displayed in the budget. This flag primarily affects UI presentation and the response payload. When `false` (and `source` is `none`), the estimate is hidden and the API response will return `value: null` and `units: null` for this field.")

class BudgetTotalRequest(PermissiveModel):
    """Defines how the total portion of a budget is configured. The total represents a user-defined target value, not an aggregated one. This object specifies whether the total is displayed and the current value for the selected budget_type."""
    enabled: bool | None = Field(None, description="Indicates whether the total value is active and should be displayed in the budget. This flag primarily affects UI presentation and the response payload.")
    value: float | None = Field(None, description="The user-set value for the total budget. When `budget_type` is `time`, represents minutes. When `budget_type` is `cost`, represents the monetary amount in the domain's currency. This value is stored separately for each `budget_type`, so switching between types preserves each value.")

class BudgetRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    budget_type: Literal["cost", "time"] | None = Field(None, description="The type of the budget, in \"cost\" or \"time\". The value of this property will dictate how the corresponding values for actual, estimate, and total are interpreted.")
    estimate: BudgetEstimateRequest | None = None
    actual: BudgetActualRequest | None = None
    total: BudgetTotalRequest | None = None
    parent: str | None = Field(None, description="Globally unique ID of the parent object: project. Can only be set on create, immutable thereafter.")

class CreateAllocationBodyDataEffort(PermissiveModel):
    """The amount of time associated with the allocation, represented as a percentage or number of hours."""
    type_: Literal["hours", "percent"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The units used for tracking effort on an allocation, either \"hours\" or \"percent\".")
    value: float | None = Field(None, description="The numeric effort value on the allocation.")

class CreateAllocationBodyData(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    start_date: str = Field(..., description="The localized day on which the allocation starts.", json_schema_extra={'format': 'date'})
    end_date: str = Field(..., description="The localized day on which the allocation ends.", json_schema_extra={'format': 'date'})
    effort: CreateAllocationBodyDataEffort | None = Field(None, description="The amount of time associated with the allocation, represented as a percentage or number of hours.")
    assignee: str = Field(..., description="Globally unique identifier for the user or placeholder assigned to the allocation.")
    parent: str = Field(..., description="Globally unique identifier for the project the allocation is on.")

class CustomFieldBaseDateValue(PermissiveModel):
    """*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`."""
    date: str | None = Field(None, description="A string representing the date in YYYY-MM-DD format.")
    date_time: str | None = Field(None, description="A string representing the date in ISO 8601 format. If no time value is selected, the value of `date-time` will be `null`.")

class CustomFieldCompactDateValue(PermissiveModel):
    """*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`."""
    date: str | None = Field(None, description="A string representing the date in YYYY-MM-DD format.")
    date_time: str | None = Field(None, description="A string representing the date in ISO 8601 format. If no time value is selected, the value of `date-time` will be `null`.")

class CustomFieldSettingCompact(PermissiveModel):
    """Custom Fields Settings objects represent the many-to-many join of the Custom Field and Project as well as stores information that is relevant to that particular pairing."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")

class DateVariableRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the date field in the project template. A value of `1` refers to the project start date, while `2` refers to the project due date.")
    value: str | None = Field(None, description="The date with which the date variable should be replaced when instantiating a project. This takes a date with `YYYY-MM-DD` format.", json_schema_extra={'format': 'date-time'})

class EnumOption(PermissiveModel):
    """Enum options are the possible values which an enum custom field can adopt. An enum custom field must contain at least 1 enum option but no more than 500.

You can add enum options to a custom field by using the `POST /custom_fields/custom_field_gid/enum_options` endpoint.

**It is not possible to remove or delete an enum option**. Instead, enum options can be disabled by updating the `enabled` field to false with the `PUT /enum_options/enum_option_gid` endpoint. Other attributes can be updated similarly.

On creation of an enum option, `enabled` is always set to `true`, meaning the enum option is a selectable value for the custom field. Setting `enabled=false` is equivalent to “trashing” the enum option in the Asana web app within the “Edit Fields” dialog. The enum option will no longer be selectable but, if the enum option value was previously set within a task, the task will retain the value.

Enum options are an ordered list and by default new enum options are inserted at the end. Ordering in relation to existing enum options can be specified on creation by using `insert_before` or `insert_after` to reference an existing enum option. Only one of `insert_before` and `insert_after` can be provided when creating a new enum option.

An enum options list can be reordered with the `POST /custom_fields/custom_field_gid/enum_options/insert` endpoint."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the enum option.")
    enabled: bool | None = Field(None, description="Whether or not the enum option is a selectable value for the custom field.")
    color: str | None = Field(None, description="The color of the enum option. Defaults to `none`.")

class CustomFieldCompact(PermissiveModel):
    """Custom Fields store the metadata that is used in order to add user-specified information to tasks in Asana. Be sure to reference the [custom fields](/reference/custom-fields) developer documentation for more information about how custom fields relate to various resources in Asana.

Users in Asana can [lock custom fields](https://asana.com/guide/help/premium/custom-fields#gl-lock-fields), which will make them read-only when accessed by other users. Attempting to edit a locked custom field will return HTTP error code `403 Forbidden`."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the custom field.")
    type_: Literal["text", "enum", "multi_enum", "number", "date", "people"] | None = Field(None, validation_alias="type", serialization_alias="type", description="*Deprecated: new integrations should prefer the resource_subtype field.* The type of the custom field. Must be one of the given values.\n")
    enum_options: list[EnumOption] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `enum` or `multi_enum`. This array specifies the possible values which an `enum` custom field can adopt. To modify the enum options, refer to [working with enum options](/reference/createenumoptionforcustomfield).")
    enabled: bool | None = Field(None, description="*Conditional*. This field applies only to [custom field values](/docs/custom-fields-guide#/accessing-custom-field-values-on-tasks-or-projects) and is not available for [custom field definitions](/docs/custom-fields-guide#/accessing-custom-field-definitions).\nDetermines if the custom field is enabled or not. For more details, see the [Custom Fields documentation](/docs/custom-fields-guide#/enabled-and-disabled-values).")
    representation_type: Literal["text", "enum", "multi_enum", "number", "date", "people", "formula", "custom_id"] | None = Field(None, description="This field tells the type of the custom field.")
    id_prefix: str | None = Field(None, description="This field is the unique custom ID string for the custom field.")
    input_restrictions: list[str] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of strings reflects the allowed types of objects that can be written to a `reference` custom field value.")
    is_formula_field: bool | None = Field(None, description="*Conditional*. This flag describes whether a custom field is a formula custom field.")
    date_value: CustomFieldCompactDateValue | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`.")
    enum_value: EnumOption | dict[str, Any] | None = None
    multi_enum_values: list[EnumOption] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `multi_enum`. This object is the chosen values of a `multi_enum` custom field.")
    number_value: float | None = Field(None, description="*Conditional*. This number is the value of a `number` custom field.")
    text_value: str | None = Field(None, description="*Conditional*. This string is the value of a `text` custom field.")
    display_value: str | None = Field(None, description="A string representation for the value of the custom field. Integrations that don't require the underlying type should use this field to read values. Using this field will future-proof an app against new custom field types.")

class CustomFieldBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the custom field.")
    type_: Literal["text", "enum", "multi_enum", "number", "date", "people"] | None = Field(None, validation_alias="type", serialization_alias="type", description="*Deprecated: new integrations should prefer the resource_subtype field.* The type of the custom field. Must be one of the given values.\n")
    enum_options: list[EnumOption] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `enum` or `multi_enum`. This array specifies the possible values which an `enum` custom field can adopt. To modify the enum options, refer to [working with enum options](/reference/createenumoptionforcustomfield).")
    enabled: bool | None = Field(None, description="*Conditional*. This field applies only to [custom field values](/docs/custom-fields-guide#/accessing-custom-field-values-on-tasks-or-projects) and is not available for [custom field definitions](/docs/custom-fields-guide#/accessing-custom-field-definitions).\nDetermines if the custom field is enabled or not. For more details, see the [Custom Fields documentation](/docs/custom-fields-guide#/enabled-and-disabled-values).")
    representation_type: Literal["text", "enum", "multi_enum", "number", "date", "people", "formula", "custom_id"] | None = Field(None, description="This field tells the type of the custom field.")
    id_prefix: str | None = Field(None, description="This field is the unique custom ID string for the custom field.")
    input_restrictions: list[str] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of strings reflects the allowed types of objects that can be written to a `reference` custom field value.")
    is_formula_field: bool | None = Field(None, description="*Conditional*. This flag describes whether a custom field is a formula custom field.")
    date_value: CustomFieldBaseDateValue | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `date`. This object reflects the chosen date (and optionally, time) value of a `date` custom field. If no date is selected, the value of `date_value` will be `null`.")
    enum_value: EnumOption | dict[str, Any] | None = None
    multi_enum_values: list[EnumOption] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `multi_enum`. This object is the chosen values of a `multi_enum` custom field.")
    number_value: float | None = Field(None, description="*Conditional*. This number is the value of a `number` custom field.")
    text_value: str | None = Field(None, description="*Conditional*. This string is the value of a `text` custom field.")
    display_value: str | None = Field(None, description="A string representation for the value of the custom field. Integrations that don't require the underlying type should use this field to read values. Using this field will future-proof an app against new custom field types.")
    description: str | None = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the custom field.")
    precision: int | None = Field(None, description="Only relevant for custom fields of type `Number`. This field dictates the number of places after the decimal to round to, i.e. 0 is integer values, 1 rounds to the nearest tenth, and so on. Must be between 0 and 6, inclusive.\nFor percentage format, this may be unintuitive, as a value of 0.25 has a precision of 0, while a value of 0.251 has a precision of 1. This is due to 0.25 being displayed as 25%.\nThe identifier format will always have a precision of 0.")
    format_: Literal["currency", "identifier", "percentage", "custom", "duration", "none"] | None = Field(None, validation_alias="format", serialization_alias="format", description="The format of this custom field.")
    currency_code: str | None = Field(None, description="ISO 4217 currency code to format this custom field. This will be null if the `format` is not `currency`.")
    custom_label: str | None = Field(None, description="This is the string that appears next to the custom field value. This will be null if the `format` is not `custom`.")
    custom_label_position: Literal["prefix", "suffix"] | None = Field(None, description="Only relevant for custom fields with `custom` format. This depicts where to place the custom label. This will be null if the `format` is not `custom`.")
    is_global_to_workspace: bool | None = Field(None, description="This flag describes whether this custom field is available to every container in the workspace. Before project-specific custom fields, this field was always true.")
    has_notifications_enabled: bool | None = Field(None, description="*Conditional*. This flag describes whether a follower of a task with this field should receive inbox notifications from changes to this field.")
    asana_created_field: Literal["a_v_requirements", "account_name", "actionable", "align_shipping_link", "align_status", "allotted_time", "appointment", "approval_stage", "approved", "article_series", "board_committee", "browser", "campaign_audience", "campaign_project_status", "campaign_regions", "channel_primary", "client_topic_type", "complete_by", "contact", "contact_email_address", "content_channels", "content_channels_needed", "content_stage", "content_type", "contract", "contract_status", "cost", "creation_stage", "creative_channel", "creative_needed", "creative_needs", "data_sensitivity", "deal_size", "delivery_appt", "delivery_appt_date", "department", "department_responsible", "design_request_needed", "design_request_type", "discussion_category", "do_this_task", "editorial_content_status", "editorial_content_tag", "editorial_content_type", "effort", "effort_level", "est_completion_date", "estimated_time", "estimated_value", "expected_cost", "external_steps_needed", "favorite_idea", "feedback_type", "financial", "funding_amount", "grant_application_process", "hiring_candidate_status", "idea_status", "ids_link", "ids_patient_link", "implementation_stage", "insurance", "interview_area", "interview_question_score", "itero_scan_link", "job_s_applied_to", "lab", "launch_status", "lead_status", "localization_language", "localization_market_team", "localization_status", "meeting_minutes", "meeting_needed", "minutes", "mrr", "must_localize", "name_of_foundation", "need_to_follow_up", "next_appointment", "next_steps_sales", "num_people", "number_of_user_reports", "office_location", "onboarding_activity", "owner", "participants_needed", "patient_date_of_birth", "patient_email", "patient_phone", "patient_status", "phone_number", "planning_category", "point_of_contact", "position", "post_format", "prescription", "priority", "priority_level", "product", "product_stage", "progress", "project_size", "project_status", "proposed_budget", "publish_status", "reason_for_scan", "referral", "request_type", "research_status", "responsible_department", "responsible_team", "risk_assessment_status", "room_name", "sales_counterpart", "sentiment", "shipping_link", "social_channels", "stage", "status", "status_design", "status_of_initiative", "system_setup", "task_progress", "team", "team_marketing", "team_responsible", "time_it_takes_to_complete_tasks", "timeframe", "treatment_type", "type_work_requests_it", "use_agency", "user_name", "vendor_category", "vendor_type", "word_count"] | None = Field(None, description="*Conditional*. A unique identifier to associate this field with the template source of truth.")

class CustomFieldRequest(PermissiveModel):
    workspace: str = Field(..., description="*Create-Only* The workspace to create a custom field in.")
    owned_by_app: bool | None = Field(None, description="*Allow-listed*. Instructs the API that this Custom Field is app-owned. This parameter is allow-listed to specific apps at this point in time. For apps that are not allow-listed, providing this parameter will result in a `403 Forbidden`.")
    people_value: list[str] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `people`. This array of user GIDs reflects the users to be written to a `people` custom field. Note that *write* operations will replace existing users (if any) in the custom field with the users specified in this array.")
    reference_value: list[str] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of GIDs reflects the objects to be written to a `reference` custom field. Note that *write* operations will replace existing objects (if any) in the custom field with the objects specified in this array.")

class CustomFieldCreateRequest(PermissiveModel):
    resource_subtype: Literal["text", "enum", "multi_enum", "number", "date", "people", "reference"] = Field(..., description="The type of the custom field. Must be one of the given values.")

class EnumOptionRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the enum option.")
    enabled: bool | None = Field(None, description="Whether or not the enum option is a selectable value for the custom field.")
    color: str | None = Field(None, description="The color of the enum option. Defaults to `none`.")
    insert_before: str | None = Field(None, description="An existing enum option within this custom field before which the new enum option should be inserted. Cannot be provided together with after_enum_option.")
    insert_after: str | None = Field(None, description="An existing enum option within this custom field after which the new enum option should be inserted. Cannot be provided together with before_enum_option.")

class GoalBase(PermissiveModel):
    """A generic Asana Resource, containing a globally unique identifier."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the goal.")
    html_notes: str | None = Field(None, description="The notes of the goal with formatting as HTML.")
    notes: str | None = Field(None, description="Free-form textual information associated with the goal (i.e. its description).")
    due_on: str | None = Field(None, description="The localized day on which this goal is due. This takes a date with format `YYYY-MM-DD`.")
    start_on: str | None = Field(None, description="The day on which work for this goal begins, or null if the goal has no start date. This takes a date with `YYYY-MM-DD` format, and cannot be set unless there is an accompanying due date.")
    is_workspace_level: bool | None = Field(None, description="*Conditional*. This property is only present when the `workspace` provided is an organization. Whether the goal belongs to the `workspace` (and is listed as part of the workspace’s goals) or not. If it isn’t a workspace-level goal, it is a team-level goal, and is associated with the goal’s team.")
    liked: bool | None = Field(None, description="True if the goal is liked by the authorized user, false if not.")

class GoalRequestBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the goal.")
    html_notes: str | None = Field(None, description="The notes of the goal with formatting as HTML.")
    notes: str | None = Field(None, description="Free-form textual information associated with the goal (i.e. its description).")
    due_on: str | None = Field(None, description="The localized day on which this goal is due. This takes a date with format `YYYY-MM-DD`.")
    start_on: str | None = Field(None, description="The day on which work for this goal begins, or null if the goal has no start date. This takes a date with `YYYY-MM-DD` format, and cannot be set unless there is an accompanying due date.")
    is_workspace_level: bool | None = Field(None, description="*Conditional*. This property is only present when the `workspace` provided is an organization. Whether the goal belongs to the `workspace` (and is listed as part of the workspace’s goals) or not. If it isn’t a workspace-level goal, it is a team-level goal, and is associated with the goal’s team.")
    liked: bool | None = Field(None, description="True if the goal is liked by the authorized user, false if not.")
    team: str | None = Field(None, description="*Conditional*. This property is only present when the `workspace` provided is an organization.")
    workspace: str | None = Field(None, description="The `gid` of a workspace.")
    time_period: str | None = Field(None, description="The `gid` of a time period.")
    owner: str | None = Field(None, description="The `gid` of a user.")

class GoalRequest(PermissiveModel):
    followers: list[str] | None = None

class GoalUpdateRequest(PermissiveModel):
    status: str | None = Field(None, description="The current status of this goal. When the goal is open, its status can be `green`, `yellow`, and `red` to reflect \"On Track\", \"At Risk\", and \"Off Track\", respectively. When the goal is closed, the value can be `missed`, `achieved`, `partial`, or `dropped`.\n*Note* you can only write to this property if `metric` is set.")
    custom_fields: dict[str, str] | None = Field(None, description="An object where each key is the GID of a custom field and its corresponding value is either an enum GID, string, number, or object (depending on the custom field type). See the [custom fields guide](/docs/custom-fields-guide) for details on creating and updating custom field values.")

class MembershipRequest(PermissiveModel):
    access_level: str | None = Field(None, description="Sets the access level for the member. Goals can have access levels `viewer`, `commenter`, `editor` or `admin`. Projects can have access levels `admin`, `editor` or `commenter`. Portfolios can have access levels `admin`, `editor` or `viewer`. Custom Fields can have access levels `admin`, `editor` or `user`.")

class PortfolioCompact(PermissiveModel):
    """A *portfolio* gives a high-level overview of the status of multiple initiatives in Asana. Portfolios provide a dashboard overview of the state of multiple projects, including a progress report and the most recent [project status](/reference/project-statuses) update.
Portfolios have some restrictions on size. Each portfolio has a max of 1500 items and, like projects, a max of 20 custom fields."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the portfolio.")

class PortfolioBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the portfolio.")
    archived: bool | None = Field(None, description="[Opt In](/docs/inputoutput-options). True if the portfolio is archived, false if not. Archived portfolios do not show in the UI by default and may be treated differently for queries.")
    color: Literal["dark-pink", "dark-green", "dark-blue", "dark-red", "dark-teal", "dark-brown", "dark-orange", "dark-purple", "dark-warm-gray", "light-pink", "light-green", "light-blue", "light-red", "light-teal", "light-brown", "light-orange", "light-purple", "light-warm-gray"] | None = Field(None, description="Color of the portfolio.")
    start_on: str | None = Field(None, description="The day on which work for this portfolio begins, or null if the portfolio has no start date. This takes a date with `YYYY-MM-DD` format. *Note: `due_on` must be present in the request when setting or unsetting the `start_on` parameter. Additionally, `start_on` and `due_on` cannot be the same date.*", json_schema_extra={'format': 'date'})
    due_on: str | None = Field(None, description="The day on which this portfolio is due. This takes a date with format YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    default_access_level: Literal["admin", "editor", "viewer"] | None = Field(None, description="The default access level when inviting new members to the portfolio")

class PortfolioRequest(PermissiveModel):
    workspace: str | None = Field(None, description="*Create-only*. The workspace or organization that the portfolio belongs to.")
    public: bool | None = Field(None, description="*Deprecated:* new integrations use `privacy_setting` instead.")

class PortfolioUpdateRequest(PermissiveModel):
    custom_fields: dict[str, str] | None = Field(None, description="An object where each key is the GID of a custom field and its corresponding value is either an enum GID, string, number, or object (depending on the custom field type). See the [custom fields guide](/docs/custom-fields-guide) for details on creating and updating custom field values.")

class ProjectBriefCompact(PermissiveModel):
    """A *Project Brief* allows you to explain the what and why of the project to your team."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")

class ProjectBriefBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    title: str | None = Field(None, description="The title of the project brief.")
    html_text: str | None = Field(None, description="HTML formatted text for the project brief.")

class ProjectBriefRequest(PermissiveModel):
    text: str | None = Field(None, description="The plain text of the project brief. When writing to a project brief, you can specify either `html_text` (preferred) or `text`, but not both.")

class ProjectCompact(PermissiveModel):
    """A *project* represents a prioritized list of tasks in Asana or a board with columns of tasks represented as cards. It exists in a single workspace or organization and is accessible to a subset of users in that workspace or organization, depending on its permissions."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="Name of the project. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")

class GoalRelationshipCompact(PermissiveModel):
    """A *goal relationship* is an object representing the relationship between a goal and another goal, a project, a task, or a portfolio."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    resource_subtype: Literal["subgoal", "supporting_work"] | None = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.")
    supporting_resource: ProjectCompact | dict[str, Any] | None = None
    contribution_weight: float | None = Field(None, description="The weight that the supporting resource's progress contributes to the supported goal's progress. This can be 0, 1, or any value in between.")

class ProjectStatusCompact(PermissiveModel):
    """*Deprecated: new integrations should prefer the `status_update` resource.*
A *project status* is an update on the progress of a particular project, and is sent out to all project followers when created. These updates include both text describing the update and a color code intended to represent the overall state of the project: "green" for projects that are on track, "yellow" for projects at risk, and "red" for projects that are behind."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    title: str | None = Field(None, description="The title of the project status update.")

class ProjectStatusBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    title: str | None = Field(None, description="The title of the project status update.")
    text: str | None = Field(None, description="The text content of the status update.")
    html_text: str | None = Field(None, description="[Opt In](/docs/inputoutput-options). The text content of the status update with formatting as HTML.")
    color: Literal["green", "yellow", "red", "blue", "complete"] | None = Field(None, description="The color associated with the status update.")

class RequestedRoleRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the template role in the project template.")
    value: str | None = Field(None, description="The user id that should be assigned to the template role.")

class ResourceExportFilters(PermissiveModel):
    """Filters to apply to a resource that will be exported. These filters can be used to narrow down the resources that are included in the export."""
    assigned_by_any: list[str] | None = Field(None, validation_alias="assigned_by.any", serialization_alias="assigned_by.any", description="Filter by the users who assigned the resource. This array accepts a list of user GIDs. This is only applicable to tasks.")
    assignee_any: list[str] | None = Field(None, validation_alias="assignee.any", serialization_alias="assignee.any", description="Filter by the users who are assigned to the resource. This array accepts a list of user GIDs. This is only applicable to tasks.")
    commented_on_by_any: list[str] | None = Field(None, validation_alias="commented_on_by.any", serialization_alias="commented_on_by.any", description="Filter by the users who commented on the resource. This array accepts a list of user GIDs.")
    created_at_after: str | None = Field(None, validation_alias="created_at.after", serialization_alias="created_at.after", description="Filter results to resources created after a specified date and time.", json_schema_extra={'format': 'date-time'})
    created_at_before: str | None = Field(None, validation_alias="created_at.before", serialization_alias="created_at.before", description="Filter results to resources created before a specified date and time.", json_schema_extra={'format': 'date-time'})
    created_by_any: list[str] | None = Field(None, validation_alias="created_by.any", serialization_alias="created_by.any", description="Filter by the users who created the resource. This array accepts a list of user GIDs.")
    followers_any: list[str] | None = Field(None, validation_alias="followers.any", serialization_alias="followers.any", description="Filter by the users who are following the resource. This array accepts a list of user GIDs.")
    liked_by_any: list[str] | None = Field(None, validation_alias="liked_by.any", serialization_alias="liked_by.any", description="Filter by the users who liked the resource. This array accepts a list of user GIDs.")
    modified_at_after: str | None = Field(None, validation_alias="modified_at.after", serialization_alias="modified_at.after", description="Filter results to resources modified after a specified date and time.", json_schema_extra={'format': 'date-time'})
    modified_at_before: str | None = Field(None, validation_alias="modified_at.before", serialization_alias="modified_at.before", description="Filter results to resources modified before a specified date and time.", json_schema_extra={'format': 'date-time'})

class ResourceExportRequestParameter(PermissiveModel):
    resource_type: str | None = Field(None, description="The type of the resource to be exported. This can be a task, team, or message.")
    filters: ResourceExportFilters | None = None
    fields: list[str] | None = Field(None, description="An array of fields to include for the resource type. If not provided, all non-optional fields for the resource type will be included. This conforms to the fields optional parameter available for all Asana endpoints which is documented [here](https://developers.asana.com/docs/inputoutput-options)")

class SectionCompact(PermissiveModel):
    """A *section* is a subdivision of a project that groups tasks together. It can either be a header above a list of tasks in a list view or a column in a board view of a project."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the section (i.e. the text displayed as the section header).")

class StatusUpdateCompact(PermissiveModel):
    """A *status update* is an update on the progress of a particular project, portfolio, or goal, and is sent out to all of its parent's followers when created. These updates include both text describing the update and a `status_type` intended to represent the overall state of the object."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    title: str | None = Field(None, description="The title of the status update.")
    resource_subtype: Literal["project_status_update", "portfolio_status_update", "goal_status_update"] | None = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.\nThe `resource_subtype`s for `status` objects represent the type of their parent.")

class StatusUpdateBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    title: str | None = Field(None, description="The title of the status update.")
    resource_subtype: Literal["project_status_update", "portfolio_status_update", "goal_status_update"] | None = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.\nThe `resource_subtype`s for `status` objects represent the type of their parent.")
    text: str = Field(..., description="The text content of the status update.")
    html_text: str | None = Field(None, description="[Opt In](/docs/inputoutput-options). The text content of the status update with formatting as HTML.")
    status_type: Literal["on_track", "at_risk", "off_track", "on_hold", "complete", "achieved", "partial", "missed", "dropped"] = Field(..., description="The type associated with the status update. This represents the current state of the object this object is on.\n\nThe valid values for `status_type` depend on the parent of the status update:\n- Projects: `on_track`, `at_risk`, `off_track`, `on_hold`, `complete`, `dropped`.\n- Portfolios: `on_track`, `at_risk`, `off_track`, `on_hold`, `complete`, `dropped`.\n- Goals: `on_track`, `at_risk`, `off_track`, `achieved`, `partial`, `missed`, `dropped`.")

class StatusUpdateRequest(PermissiveModel):
    parent: str

class TagCompact(PermissiveModel):
    """A *tag* is a label that can be attached to any task in Asana. It exists in a single workspace or organization."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="Name of the tag. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")

class TagBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="Name of the tag. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    color: Literal["dark-pink", "dark-green", "dark-blue", "dark-red", "dark-teal", "dark-brown", "dark-orange", "dark-purple", "dark-warm-gray", "light-pink", "light-green", "light-blue", "light-red", "light-teal", "light-brown", "light-orange", "light-purple", "light-warm-gray"] | None = Field(None, description="Color of the tag.")
    notes: str | None = Field(None, description="Free-form textual information associated with the tag (i.e. its description).")

class TagCreateRequest(PermissiveModel):
    followers: list[str] | None = Field(None, description="An array of strings identifying users. These can either be the string \"me\", an email, or the gid of a user.")
    workspace: str | None = Field(None, description="Gid of an object.")

class TagCreateTagForWorkspaceRequest(PermissiveModel):
    followers: list[str] | None = Field(None, description="An array of strings identifying users. These can either be the string \"me\", an email, or the gid of a user.")

class TaskBaseCreatedBy(PermissiveModel):
    """[Opt In](/docs/inputoutput-options). A *user* object represents an account in Asana that can be given access to various workspaces, projects, and tasks."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource.")
    resource_type: str | None = Field(None, description="The type of resource.")

class TaskBaseExternal(PermissiveModel):
    """*OAuth Required*. *Conditional*. This field is returned only if external values are set or included by using [Opt In] (/docs/inputoutput-options).
The external field allows you to store app-specific metadata on tasks, including a gid that can be used to retrieve tasks and a data blob that can store app-specific character strings. Note that you will need to authenticate with Oauth to access or modify this data. Once an external gid is set, you can use the notation `external:custom_gid` to reference your object anywhere in the API where you may use the original object gid. See the page on Custom External Data for more details."""
    gid: str | None = None
    data: str | None = None

class TaskBaseMembershipsItem(PermissiveModel):
    project: ProjectCompact | None = None
    section: SectionCompact | None = None

class TaskBaseV1External(PermissiveModel):
    """*OAuth Required*. *Conditional*. This field is returned only if external values are set or included by using [Opt In] (/docs/inputoutput-options).
The external field allows you to store app-specific metadata on tasks, including a gid that can be used to retrieve tasks and a data blob that can store app-specific character strings. Note that you will need to authenticate with Oauth to access or modify this data. Once an external gid is set, you can use the notation `external:custom_gid` to reference your object anywhere in the API where you may use the original object gid. See the page on Custom External Data for more details."""
    gid: str | None = None
    data: str | None = None

class TaskBaseV1MembershipsItem(PermissiveModel):
    project: ProjectCompact | None = None
    section: SectionCompact | None = None

class TaskCompactCreatedBy(PermissiveModel):
    """[Opt In](/docs/inputoutput-options). A *user* object represents an account in Asana that can be given access to various workspaces, projects, and tasks."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource.")
    resource_type: str | None = Field(None, description="The type of resource.")

class TaskCompact(PermissiveModel):
    """<p><strong style={{ color: "#4573D2" }}>Full object requires scope: </strong><code>tasks:read</code></p>

The *task* is the basic object around which many operations in Asana are centered."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the task.")
    resource_subtype: Literal["default_task", "milestone", "approval", "custom"] | None = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.\nThe resource_subtype `milestone` represent a single moment in time. This means tasks with this subtype cannot have a start_date.")
    created_by: TaskCompactCreatedBy | None = Field(None, description="[Opt In](/docs/inputoutput-options). A *user* object represents an account in Asana that can be given access to various workspaces, projects, and tasks.")

class TeamCompact(PermissiveModel):
    """<p><strong style={{ color: "#4573D2" }}>Full object requires scope: </strong><code>teams:read</code></p>

A *team* is used to group related projects and people together within an organization. Each project in an organization is associated with a team."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the team.")

class TeamRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the team.")
    description: str | None = Field(None, description="The description of the team.\n")
    html_description: str | None = Field(None, description="The description of the team with formatting as HTML.\n")
    organization: str | None = Field(None, description="The organization/workspace the team belongs to. This must be the same organization you are in and cannot be changed once set.\n")
    visibility: Literal["secret", "request_to_join", "public"] | None = Field(None, description="The visibility of the team to users in the same organization\n")
    edit_team_name_or_description_access_level: Literal["all_team_members", "only_team_admins"] | None = Field(None, description="Controls who can edit team name and description\n")
    edit_team_visibility_or_trash_team_access_level: Literal["all_team_members", "only_team_admins"] | None = Field(None, description="Controls who can edit team visibility and trash teams\n")
    member_invite_management_access_level: Literal["all_team_members", "only_team_admins"] | None = Field(None, description="Controls who can accept or deny member invites for a given team\n")
    guest_invite_management_access_level: Literal["all_team_members", "only_team_admins"] | None = Field(None, description="Controls who can accept or deny guest invites for a given team\n")
    join_request_management_access_level: Literal["all_team_members", "only_team_admins"] | None = Field(None, description="Controls who can accept or deny join team requests for a Membership by Request team. This field can only be updated when the team's `visibility` field is `request_to_join`.\n")
    team_member_removal_access_level: Literal["all_team_members", "only_team_admins"] | None = Field(None, description="Controls who can remove team members\n")
    team_content_management_access_level: Literal["no_restriction", "only_team_admins"] | None = Field(None, description="Controls who can create and share content with the team\n")
    endorsed: bool | None = Field(None, description="Whether the team has been endorsed\n")

class UserCompact(PermissiveModel):
    """A *user* object represents an account in Asana that can be given access to various workspaces, projects, and tasks."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="*Read-only except when same user as requester*. The user's name.")

class CustomFieldResponse(PermissiveModel):
    representation_type: Literal["text", "enum", "multi_enum", "number", "date", "people", "formula", "custom_id", "reference"] | None = Field(None, description="This field tells the type of the custom field.")
    id_prefix: str | None = Field(None, description="This field is the unique custom ID string for the custom field.")
    input_restrictions: list[str] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of strings reflects the allowed types of objects that can be written to a `reference` custom field value.")
    is_formula_field: bool | None = Field(None, description="*Conditional*. This flag describes whether a custom field is a formula custom field.")
    is_value_read_only: bool | None = Field(None, description="*Conditional*. This flag describes whether a custom field is read only.")
    created_by: UserCompact | Any | None = None
    people_value: list[UserCompact] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `people`. This array of [compact user](/reference/users) objects reflects the values of a `people` custom field.")
    reference_value: list[AsanaNamedResource] | None = Field(None, description="*Conditional*. Only relevant for custom fields of type `reference`. This array of objects reflects the values of a `reference` custom field.")
    privacy_setting: Literal["public_with_guests", "public", "private"] | None = Field(None, description="The privacy setting of the custom field. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*")
    default_access_level: Literal["admin", "editor", "user"] | None = Field(None, description="The default access level when inviting new members to the custom field. This isn't applied when the `privacy_setting` is `private`, or the user is a guest. For local fields in a project or portfolio, the user must additionally have permission to modify the container itself.")
    resource_subtype: Literal["text", "enum", "multi_enum", "number", "date", "people", "reference"] | None = Field(None, description="The type of the custom field. Must be one of the given values.\n")

class CustomFieldSettingResponse(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    project: ProjectCompact | dict[str, Any] | None = None
    is_important: bool | None = Field(None, description="`is_important` is used in the Asana web application to determine if this custom field is displayed in the list/grid view of a project or portfolio.")
    parent: ProjectCompact | dict[str, Any] | None = None
    custom_field: CustomFieldResponse | dict[str, Any] | None = None

class GoalCompact(PermissiveModel):
    """A generic Asana Resource, containing a globally unique identifier."""
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="The name of the goal.")
    owner: UserCompact | dict[str, Any] | None = None

class GoalRelationshipBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    resource_subtype: Literal["subgoal", "supporting_work"] | None = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.")
    supporting_resource: ProjectCompact | dict[str, Any] | None = None
    contribution_weight: float | None = Field(None, description="The weight that the supporting resource's progress contributes to the supported goal's progress. This can be 0, 1, or any value in between.")
    supported_goal: GoalCompact | dict[str, Any] | None = None

class GoalRelationshipRequest(PermissiveModel):
    pass

class Like(PermissiveModel):
    """An object to represent a user's like."""
    gid: str | None = Field(None, description="Globally unique identifier of the object, as a string.")
    user: UserCompact | None = None

class ProjectStatusResponse(PermissiveModel):
    author: UserCompact | None = None
    created_at: str | None = Field(None, description="The time at which this resource was created.", json_schema_extra={'format': 'date-time'})
    created_by: UserCompact | None = None
    modified_at: str | None = Field(None, description="The time at which this project status was last modified.\n*Note: This does not currently reflect any changes in associations such as comments that may have been added or removed from the project status.*", json_schema_extra={'format': 'date-time'})

class ProjectBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="Name of the project. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    archived: bool | None = Field(None, description="True if the project is archived, false if not. Archived projects do not show in the UI by default and may be treated differently for queries.")
    color: Literal["dark-pink", "dark-green", "dark-blue", "dark-red", "dark-teal", "dark-brown", "dark-orange", "dark-purple", "dark-warm-gray", "light-pink", "light-green", "light-blue", "light-red", "light-teal", "light-brown", "light-orange", "light-purple", "light-warm-gray", "none"] | None = Field(None, description="Color of the project.")
    icon: Literal["list", "board", "timeline", "calendar", "rocket", "people", "graph", "star", "bug", "light_bulb", "globe", "gear", "notebook", "computer", "check", "target", "html", "megaphone", "chat_bubbles", "briefcase", "page_layout", "mountain_flag", "puzzle", "presentation", "line_and_symbols", "speed_dial", "ribbon", "shoe", "shopping_basket", "map", "ticket", "coins"] | None = Field(None, description="The icon for a project.")
    created_at: str | None = Field(None, description="The time at which this resource was created.", json_schema_extra={'format': 'date-time'})
    current_status: ProjectStatusResponse | dict[str, Any] | None = None
    current_status_update: StatusUpdateCompact | dict[str, Any] | None = None
    custom_field_settings: list[CustomFieldSettingResponse] | None = Field(None, description="Array of custom field definitions that are enabled for the project. These represent which custom fields are available to be used on tasks within the project, but do not include any values.")
    default_view: Literal["list", "board", "calendar", "timeline"] | None = Field(None, description="The default view (list, board, calendar, or timeline) of a project.")
    due_date: str | None = Field(None, description="*Deprecated: new integrations should prefer the `due_on` field.*", json_schema_extra={'format': 'date'})
    due_on: str | None = Field(None, description="The day on which this project is due. This takes a date with format YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    html_notes: str | None = Field(None, description="[Opt In](/docs/inputoutput-options). The notes of the project with formatting as HTML.")
    members: list[UserCompact] | None = Field(None, description="Array of users who are members of this project.")
    modified_at: str | None = Field(None, description="The time at which this project was last modified.\n*Note: This does not currently reflect any changes in associations such as tasks or comments that may have been added or removed from the project.*", json_schema_extra={'format': 'date-time'})
    notes: str | None = Field(None, description="Free-form textual information associated with the project (ie., its description).")
    public: bool | None = Field(None, description="*Deprecated:* new integrations use `privacy_setting` instead.")
    privacy_setting: Literal["public_to_workspace", "private_to_team", "private"] | None = Field(None, description="The privacy setting of the project. *Note: Administrators in your organization may restrict the values of `privacy_setting`.* The value `private_to_team` is deprecated. Use `POST /memberships` to share a project with a team after creation.")
    start_on: str | None = Field(None, description="The day on which work for this project begins, or null if the project has no start date. This takes a date with `YYYY-MM-DD` format. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter. Additionally, `start_on` and `due_on` cannot be the same date.*", json_schema_extra={'format': 'date'})
    default_access_level: Literal["admin", "editor", "commenter", "viewer"] | None = Field(None, description="The default access for users or teams who join or are added as members to the project.")
    minimum_access_level_for_customization: Literal["admin", "editor"] | None = Field(None, description="The minimum access level needed for project members to modify this project's workflow and appearance.")
    minimum_access_level_for_sharing: Literal["admin", "editor"] | None = Field(None, description="The minimum access level needed for project members to share the project and manage project memberships.")

class ProjectRequest(PermissiveModel):
    custom_fields: dict[str, str] | None = Field(None, description="An object where each key is the GID of a custom field and its corresponding value is either an enum GID, string, number, or object (depending on the custom field type). See the [custom fields guide](/docs/custom-fields-guide) for details on creating and updating custom field values.")
    followers: str | None = Field(None, description="*Create-only*. Comma separated string of users. Followers are a subset of members who have opted in to receive \"tasks added\" notifications for a project.")
    owner: str | None = Field(None, description="The current owner of the project, may be null.")
    team: str | None = Field(None, description="*Deprecated:* The team to share this project with is deprecated. Use `POST /memberships` with `{ parent: project, member: team }` to share a project with a team after creation.")
    workspace: str | None = Field(None, description="The `gid` of a workspace.")

class ProjectUpdateRequest(PermissiveModel):
    custom_fields: dict[str, str] | None = Field(None, description="An object where each key is the GID of a custom field and its corresponding value is either an enum GID, string, number, or object (depending on the custom field type). See the [custom fields guide](/docs/custom-fields-guide) for details on creating and updating custom field values.")
    followers: str | None = Field(None, description="*Create-only*. Comma separated string of users. Followers are a subset of members who have opted in to receive \"tasks added\" notifications for a project.")
    owner: str | None = Field(None, description="The current owner of the project, may be null.")
    team: str | None = Field(None, description="*Deprecated:* Updating the team a project is shared with is deprecated. Use `POST /memberships` with `{ parent: project, member: team }` instead to manage team sharing.")

class TaskBase(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="Name of the task. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    resource_subtype: Literal["default_task", "milestone", "approval", "custom"] | None = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.\nThe resource_subtype `milestone` represent a single moment in time. This means tasks with this subtype cannot have a start_date.")
    created_by: TaskBaseCreatedBy | None = Field(None, description="[Opt In](/docs/inputoutput-options). A *user* object represents an account in Asana that can be given access to various workspaces, projects, and tasks.")
    approval_status: Literal["pending", "approved", "rejected", "changes_requested"] | None = Field(None, description="*Conditional* Reflects the approval status of this task. This field is kept in sync with `completed`, meaning `pending` translates to false while `approved`, `rejected`, and `changes_requested` translate to true. If you set completed to true, this field will be set to `approved`.")
    assignee_status: Literal["today", "upcoming", "later", "new", "inbox"] | None = Field(None, description="*Deprecated* Scheduling status of this task for the user it is assigned to. This field can only be set if the assignee is non-null. Setting this field to \"inbox\" or \"upcoming\" inserts it at the top of the section, while the other options will insert at the bottom.")
    assigned_by: UserCompact | Any | None = None
    completed: bool | None = Field(None, description="True if the task is currently marked complete, false if not.")
    completed_at: str | None = Field(None, description="The time at which this task was completed, or null if the task is incomplete.", json_schema_extra={'format': 'date-time'})
    completed_by: UserCompact | Any | None = None
    created_at: str | None = Field(None, description="The time at which this resource was created.", json_schema_extra={'format': 'date-time'})
    dependencies: list[AsanaResource] | None = Field(None, description="[Opt In](/docs/inputoutput-options). Array of resources referencing tasks that this task depends on. The objects contain only the gid of the dependency.")
    dependents: list[AsanaResource] | None = Field(None, description="[Opt In](/docs/inputoutput-options). Array of resources referencing tasks that depend on this task. The objects contain only the ID of the dependent.")
    due_at: str | None = Field(None, description="The UTC date and time on which this task is due, or null if the task has no due time. This takes an ISO 8601 date string in UTC and should not be used together with `due_on`.", json_schema_extra={'format': 'date-time'})
    due_on: str | None = Field(None, description="The localized date on which this task is due, or null if the task has no due date. This takes a date with `YYYY-MM-DD` format and should not be used together with `due_at`.", json_schema_extra={'format': 'date'})
    external: TaskBaseExternal | None = Field(None, description="*OAuth Required*. *Conditional*. This field is returned only if external values are set or included by using [Opt In] (/docs/inputoutput-options).\nThe external field allows you to store app-specific metadata on tasks, including a gid that can be used to retrieve tasks and a data blob that can store app-specific character strings. Note that you will need to authenticate with Oauth to access or modify this data. Once an external gid is set, you can use the notation `external:custom_gid` to reference your object anywhere in the API where you may use the original object gid. See the page on Custom External Data for more details.")
    html_notes: str | None = Field(None, description="[Opt In](/docs/inputoutput-options). The notes of the text with formatting as HTML.")
    hearted: bool | None = Field(None, description="*Deprecated - please use liked instead* True if the task is hearted by the authorized user, false if not.")
    hearts: list[Like] | None = Field(None, description="*Deprecated - please use likes instead* Array of likes for users who have hearted this task.")
    is_rendered_as_separator: bool | None = Field(None, description="[Opt In](/docs/inputoutput-options). In some contexts tasks can be rendered as a visual separator; for instance, subtasks can appear similar to [sections](/reference/sections) without being true `section` objects. If a `task` object is rendered this way in any context it will have the property `is_rendered_as_separator` set to `true`. This parameter only applies to regular tasks with `resource_subtype` of `default_task`. Tasks with `resource_subtype` of `milestone`, `approval`, or custom task types will not have this property and cannot be rendered as separators.")
    liked: bool | None = Field(None, description="True if the task is liked by the authorized user, false if not.")
    likes: list[Like] | None = Field(None, description="Array of likes for users who have liked this task.")
    memberships: list[TaskBaseMembershipsItem] | None = Field(None, description="<p><strong style={{ color: \"#4573D2\" }}>Full object requires scope: </strong><code>projects:read</code>, <code>project_sections:read</code></p>\n\n*Create-only*. Array of projects this task is associated with and the section it is in. At task creation time, this array can be used to add the task to specific sections. After task creation, these associations can be modified using the `addProject` and `removeProject` endpoints. Note that over time, more types of memberships may be added to this property.")
    modified_at: str | None = Field(None, description="The time at which this task was last modified.\n\nThe following conditions will change `modified_at`:\n\n- story is created on a task\n- story is trashed on a task\n- attachment is trashed on a task\n- task is assigned or unassigned\n- custom field value is changed\n- the task itself is trashed\n- Or if any of the following fields are updated:\n  - completed\n  - name\n  - due_date\n  - description\n  - attachments\n  - items\n  - schedule_status\n\nThe following conditions will _not_ change `modified_at`:\n\n- moving to a new container (project, portfolio, etc)\n- comments being added to the task (but the stories they generate\n  _will_ affect `modified_at`)", json_schema_extra={'format': 'date-time'})
    notes: str | None = Field(None, description="Free-form textual information associated with the task (i.e. its description).")
    num_hearts: int | None = Field(None, description="*Deprecated - please use likes instead* The number of users who have hearted this task.")
    num_likes: int | None = Field(None, description="The number of users who have liked this task.")
    num_subtasks: int | None = Field(None, description="[Opt In](/docs/inputoutput-options). The number of subtasks on this task.\n")
    start_at: str | None = Field(None, description="Date and time on which work begins for the task, or null if the task has no start time. This takes an ISO 8601 date string in UTC and should not be used together with `start_on`.\n*Note: `due_at` must be present in the request when setting or unsetting the `start_at` parameter.*", json_schema_extra={'format': 'date-time'})
    start_on: str | None = Field(None, description="The day on which work begins for the task , or null if the task has no start date. This takes a date with `YYYY-MM-DD` format and should not be used together with `start_at`.\n*Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter.*", json_schema_extra={'format': 'date'})
    actual_time_minutes: float | None = Field(None, description="<p><strong style={{ color: \"#4573D2\" }}>Full object requires scope: </strong><code>time_tracking_entries:read</code></p>\n\nThis value represents the sum of all the Time Tracking entries in the Actual Time field on a given Task. It is represented as a nullable long value.")

class TaskRequest(PermissiveModel):
    assignee: str | None = Field(None, description="Gid of a user.")
    assignee_section: str | None = Field(None, description="The *assignee section* is a subdivision of a project that groups tasks together in the assignee's \"My tasks\" list. It can either be a header above a list of tasks in a list view or a column in a board view of \"My tasks.\"\nThe `assignee_section` property will be returned in the response only if the request was sent by the user who is the assignee of the task. Note that you can only write to `assignee_section` with the gid of an existing section visible in the user's \"My tasks\" list.")
    custom_fields: dict[str, str] | None = Field(None, description="An object where each key is the GID of a custom field and its corresponding value is either an enum GID, string, number, object, or array (depending on the custom field type). See the [custom fields guide](/docs/custom-fields-guide) for details on creating and updating custom field values.")
    followers: list[str] | None = Field(None, description="*Create-Only* An array of strings identifying users. These can either be the string \"me\", an email, or the gid of a user. In order to change followers on an existing task use `addFollowers` and `removeFollowers`.")
    parent: str | None = Field(None, description="Gid of a task.")
    projects: list[str] | None = Field(None, description="*Create-Only* Array of project gids. In order to change projects on an existing task use `addProject` and `removeProject`.")
    tags: list[str] | None = Field(None, description="*Create-Only* Array of tag gids. In order to change tags on an existing task use `addTag` and `removeTag`.")
    workspace: str | None = Field(None, description="Gid of a workspace.")
    custom_type: str | None = Field(None, description="*Conditional:* You can only set custom_type if task `resource_subtype` is `custom`. GID or globally-unique identifier of a task's custom type.")
    custom_type_status_option: str | None = Field(None, description="*Conditional:* You can only set custom_type_status_option if task `resource_subtype` is `custom` GID or globally-unique identifier of a custom type's status option.")

class UserUpdateRequest(PermissiveModel):
    gid: str | None = Field(None, description="Globally unique identifier of the resource, as a string.")
    resource_type: str | None = Field(None, description="The base type of this resource.")
    name: str | None = Field(None, description="*Read-only except when same user as requester*. The user's name.")
    custom_fields: dict[str, str] | None = Field(None, description="An object where each key is the GID of a custom field and its corresponding value is either an enum GID, string, number, or object (depending on the custom field type). See the [custom fields guide](/docs/custom-fields-guide) for details on creating and updating custom field values.")


# Rebuild models to resolve forward references (required for circular refs)
AllocationBase.model_rebuild()
AllocationBaseEffort.model_rebuild()
AllocationRequest.model_rebuild()
AllocationRequestEffort.model_rebuild()
AsanaNamedResource.model_rebuild()
AsanaResource.model_rebuild()
BudgetActualRequest.model_rebuild()
BudgetCompact.model_rebuild()
BudgetEstimateRequest.model_rebuild()
BudgetRequest.model_rebuild()
BudgetTotalRequest.model_rebuild()
CreateAllocationBodyData.model_rebuild()
CreateAllocationBodyDataEffort.model_rebuild()
CustomFieldBase.model_rebuild()
CustomFieldBaseDateValue.model_rebuild()
CustomFieldCompact.model_rebuild()
CustomFieldCompactDateValue.model_rebuild()
CustomFieldCreateRequest.model_rebuild()
CustomFieldRequest.model_rebuild()
CustomFieldResponse.model_rebuild()
CustomFieldSettingCompact.model_rebuild()
CustomFieldSettingResponse.model_rebuild()
DateVariableRequest.model_rebuild()
EnumOption.model_rebuild()
EnumOptionRequest.model_rebuild()
GoalBase.model_rebuild()
GoalCompact.model_rebuild()
GoalRelationshipBase.model_rebuild()
GoalRelationshipCompact.model_rebuild()
GoalRelationshipRequest.model_rebuild()
GoalRequest.model_rebuild()
GoalRequestBase.model_rebuild()
GoalUpdateRequest.model_rebuild()
Like.model_rebuild()
MembershipRequest.model_rebuild()
PortfolioBase.model_rebuild()
PortfolioCompact.model_rebuild()
PortfolioRequest.model_rebuild()
PortfolioUpdateRequest.model_rebuild()
ProjectBase.model_rebuild()
ProjectBriefBase.model_rebuild()
ProjectBriefCompact.model_rebuild()
ProjectBriefRequest.model_rebuild()
ProjectCompact.model_rebuild()
ProjectRequest.model_rebuild()
ProjectStatusBase.model_rebuild()
ProjectStatusCompact.model_rebuild()
ProjectStatusResponse.model_rebuild()
ProjectUpdateRequest.model_rebuild()
RequestedRoleRequest.model_rebuild()
ResourceExportFilters.model_rebuild()
ResourceExportRequestParameter.model_rebuild()
SectionCompact.model_rebuild()
StatusUpdateBase.model_rebuild()
StatusUpdateCompact.model_rebuild()
StatusUpdateRequest.model_rebuild()
TagBase.model_rebuild()
TagCompact.model_rebuild()
TagCreateRequest.model_rebuild()
TagCreateTagForWorkspaceRequest.model_rebuild()
TaskBase.model_rebuild()
TaskBaseCreatedBy.model_rebuild()
TaskBaseExternal.model_rebuild()
TaskBaseMembershipsItem.model_rebuild()
TaskBaseV1External.model_rebuild()
TaskBaseV1MembershipsItem.model_rebuild()
TaskCompact.model_rebuild()
TaskCompactCreatedBy.model_rebuild()
TaskRequest.model_rebuild()
TeamCompact.model_rebuild()
TeamRequest.model_rebuild()
UserCompact.model_rebuild()
UserUpdateRequest.model_rebuild()

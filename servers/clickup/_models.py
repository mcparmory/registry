"""
Clickup MCP Server - Pydantic Models

Generated: 2026-05-11 19:39:54 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AddDependencyRequest",
    "AddGuestToFolderRequest",
    "AddGuestToListRequest",
    "AddGuestToTaskRequest",
    "AddtagsfromtimeentriesRequest",
    "AddTagToTaskRequest",
    "AddTaskLinkRequest",
    "AddTaskToListRequest",
    "ChangetagnamesfromtimeentriesRequest",
    "CreateatimeentryRequest",
    "CreateChatViewCommentRequest",
    "CreateChecklistItemRequest",
    "CreateChecklistRequest",
    "CreateFolderFromTemplateRequest",
    "CreateFolderlessListRequest",
    "CreateFolderListFromTemplateRequest",
    "CreateFolderRequest",
    "CreateFolderViewRequest",
    "CreateGoalRequest",
    "CreateKeyResultRequest",
    "CreateListCommentRequest",
    "CreateListRequest",
    "CreateListViewRequest",
    "CreateSpaceListFromTemplateRequest",
    "CreateSpaceRequest",
    "CreateSpaceTagRequest",
    "CreateSpaceViewRequest",
    "CreateTaskAttachmentRequest",
    "CreateTaskCommentRequest",
    "CreateTaskFromTemplateRequest",
    "CreateTaskRequest",
    "CreateTeamViewRequest",
    "CreateThreadedCommentRequest",
    "CreateUserGroupRequest",
    "DeleteatimeEntryRequest",
    "DeleteChecklistItemRequest",
    "DeleteChecklistRequest",
    "DeleteCommentRequest",
    "DeleteDependencyRequest",
    "DeleteFolderRequest",
    "DeleteGoalRequest",
    "DeleteKeyResultRequest",
    "DeleteListRequest",
    "DeleteSpaceRequest",
    "DeleteSpaceTagRequest",
    "DeleteTaskLinkRequest",
    "DeleteTaskRequest",
    "DeleteTeamRequest",
    "DeletetimetrackedRequest",
    "DeleteViewRequest",
    "DeleteWebhookRequest",
    "EditChecklistItemRequest",
    "EditChecklistRequest",
    "EditGuestOnWorkspaceRequest",
    "EditKeyResultRequest",
    "EditSpaceTagRequest",
    "EdittimetrackedRequest",
    "EditUserOnWorkspaceRequest",
    "GetAccessibleCustomFieldsRequest",
    "GetalltagsfromtimeentriesRequest",
    "GetBulkTasksTimeinStatusRequest",
    "GetChatViewCommentsRequest",
    "GetCustomItemsRequest",
    "GetCustomRolesRequest",
    "GetFilteredTeamTasksRequest",
    "GetFolderAvailableFieldsRequest",
    "GetFolderlessListsRequest",
    "GetFolderRequest",
    "GetFoldersRequest",
    "GetFolderTemplatesRequest",
    "GetFolderViewsRequest",
    "GetGoalRequest",
    "GetGoalsRequest",
    "GetGuestRequest",
    "GetListCommentsRequest",
    "GetListMembersRequest",
    "GetListRequest",
    "GetListsRequest",
    "GetListTemplatesRequest",
    "GetListViewsRequest",
    "GetrunningtimeentryRequest",
    "GetsingulartimeentryRequest",
    "GetSpaceAvailableFieldsRequest",
    "GetSpaceRequest",
    "GetSpacesRequest",
    "GetSpaceTagsRequest",
    "GetSpaceViewsRequest",
    "GetTaskCommentsRequest",
    "GetTaskMembersRequest",
    "GetTaskRequest",
    "GetTasksRequest",
    "GetTaskSTimeinStatusRequest",
    "GetTaskTemplatesRequest",
    "GetTeamAvailableFieldsRequest",
    "GetTeams1Request",
    "GetTeamViewsRequest",
    "GetThreadedCommentsRequest",
    "GettimeentrieswithinadaterangeRequest",
    "GettimeentryhistoryRequest",
    "GettrackedtimeRequest",
    "GetUserRequest",
    "GetViewRequest",
    "GetViewTasksRequest",
    "GetWebhooksRequest",
    "GetWorkspaceplanRequest",
    "GetWorkspaceseatsRequest",
    "InviteGuestToWorkspaceRequest",
    "InviteUserToWorkspaceRequest",
    "MergeTasksRequest",
    "RemoveCustomFieldValueRequest",
    "RemoveGuestFromFolderRequest",
    "RemoveGuestFromListRequest",
    "RemoveGuestFromTaskRequest",
    "RemoveGuestFromWorkspaceRequest",
    "RemoveTagFromTaskRequest",
    "RemovetagsfromtimeentriesRequest",
    "RemoveTaskFromListRequest",
    "RemoveUserFromWorkspaceRequest",
    "SetCustomFieldValueRequest",
    "SharedHierarchyRequest",
    "StartatimeEntryRequest",
    "StopatimeEntryRequest",
    "TracktimeRequest",
    "UpdateatimeEntryRequest",
    "UpdateCommentRequest",
    "UpdateFolderRequest",
    "UpdateGoalRequest",
    "UpdateListRequest",
    "UpdateSpaceRequest",
    "UpdateTaskRequest",
    "UpdateTeamRequest",
    "UpdateViewRequest",
    "AddtagsfromtimeentriesBodyTagsItem",
    "CreateatimeentryBodyTagsItem",
    "CreateTaskBodyCustomFieldsItemV0",
    "CreateTaskBodyCustomFieldsItemV1",
    "CreateTaskBodyCustomFieldsItemV10",
    "CreateTaskBodyCustomFieldsItemV11",
    "CreateTaskBodyCustomFieldsItemV12",
    "CreateTaskBodyCustomFieldsItemV13",
    "CreateTaskBodyCustomFieldsItemV14",
    "CreateTaskBodyCustomFieldsItemV2",
    "CreateTaskBodyCustomFieldsItemV3",
    "CreateTaskBodyCustomFieldsItemV4",
    "CreateTaskBodyCustomFieldsItemV5",
    "CreateTaskBodyCustomFieldsItemV6",
    "CreateTaskBodyCustomFieldsItemV7",
    "CreateTaskBodyCustomFieldsItemV8",
    "CreateTaskBodyCustomFieldsItemV9",
    "RemovetagsfromtimeentriesBodyTagsItem",
    "SetCustomFieldValueBodyV0",
    "SetCustomFieldValueBodyV1",
    "SetCustomFieldValueBodyV10",
    "SetCustomFieldValueBodyV11",
    "SetCustomFieldValueBodyV12",
    "SetCustomFieldValueBodyV13",
    "SetCustomFieldValueBodyV14",
    "SetCustomFieldValueBodyV15",
    "SetCustomFieldValueBodyV2",
    "SetCustomFieldValueBodyV3",
    "SetCustomFieldValueBodyV4",
    "SetCustomFieldValueBodyV5",
    "SetCustomFieldValueBodyV6",
    "SetCustomFieldValueBodyV7",
    "SetCustomFieldValueBodyV8",
    "SetCustomFieldValueBodyV9",
    "StartatimeEntryBodyTagsItem",
    "UpdateatimeEntryBodyTagsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: upload_task_attachment
class CreateTaskAttachmentRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to which the file will be attached.", examples=['9hv'])
class CreateTaskAttachmentRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the default system-generated task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when referencing a task by its custom task ID. Must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateTaskAttachmentRequestBody(StrictModel):
    attachment: list[Annotated[str, Field(json_schema_extra={'format': 'byte'})]] | None = Field(default=None, description="Base64-encoded file content for upload. The file content to upload as a multipart/form-data attachment. Each item represents a part of the multipart payload for the file being attached.")
class CreateTaskAttachmentRequest(StrictModel):
    """Upload a local file to a task as an attachment using multipart/form-data. Note that cloud-hosted files are not supported; only locally accessible files can be attached."""
    path: CreateTaskAttachmentRequestPath
    query: CreateTaskAttachmentRequestQuery | None = None
    body: CreateTaskAttachmentRequestBody | None = None

# Operation: create_checklist
class CreateChecklistRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to which the checklist will be added.", examples=['9hz'])
class CreateChecklistRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if referencing the task by its custom task ID instead of the default system-generated task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs; must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateChecklistRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new checklist.")
class CreateChecklistRequest(StrictModel):
    """Add a new named checklist to a specified task, allowing you to track subtasks or steps within that task."""
    path: CreateChecklistRequestPath
    query: CreateChecklistRequestQuery | None = None
    body: CreateChecklistRequestBody

# Operation: update_checklist
class EditChecklistRequestPath(StrictModel):
    checklist_id: str = Field(default=..., description="The unique identifier (UUID) of the checklist to update.", examples=['b955c4dc'])
class EditChecklistRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the checklist.")
    position: int | None = Field(default=None, description="The zero-based display order of the checklist among all checklists on the task, where 0 places it at the top.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class EditChecklistRequest(StrictModel):
    """Rename a checklist or change its display order relative to other checklists on a task. Provide a new name, a new position, or both."""
    path: EditChecklistRequestPath
    body: EditChecklistRequestBody | None = None

# Operation: delete_checklist
class DeleteChecklistRequestPath(StrictModel):
    checklist_id: str = Field(default=..., description="The unique identifier (UUID) of the checklist to delete.", examples=['b955c4dc'])
class DeleteChecklistRequest(StrictModel):
    """Permanently deletes a checklist from a task. This action is irreversible and removes the checklist along with all its items."""
    path: DeleteChecklistRequestPath

# Operation: create_checklist_item
class CreateChecklistItemRequestPath(StrictModel):
    checklist_id: str = Field(default=..., description="The unique identifier of the checklist to which the new item will be added.", examples=['b955c4dc'])
class CreateChecklistItemRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name or label for the checklist item.")
    assignee: int | None = Field(default=None, description="The numeric user ID of the team member to assign this checklist item to.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class CreateChecklistItemRequest(StrictModel):
    """Adds a new line item to an existing task checklist. Optionally assign the item to a specific user by their ID."""
    path: CreateChecklistItemRequestPath
    body: CreateChecklistItemRequestBody | None = None

# Operation: update_checklist_item
class EditChecklistItemRequestPath(StrictModel):
    checklist_id: str = Field(default=..., description="The unique identifier of the checklist that contains the item to be updated.", examples=['b955c4dc'])
    checklist_item_id: str = Field(default=..., description="The unique identifier of the specific checklist item to update.", examples=['21e08dc8'])
class EditChecklistItemRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The updated display name or label for the checklist item.")
    assignee: str | None = Field(default=None, description="The user ID of the team member to assign to this checklist item.")
    resolved: bool | None = Field(default=None, description="Whether the checklist item is marked as completed; set to true to resolve it or false to reopen it.")
    parent: str | None = Field(default=None, description="The checklist item ID of the parent item under which this item should be nested, enabling hierarchical checklist structures.")
class EditChecklistItemRequest(StrictModel):
    """Update an individual item within a task checklist, allowing you to rename it, reassign it, mark it as resolved or unresolved, or nest it under another checklist item as a child."""
    path: EditChecklistItemRequestPath
    body: EditChecklistItemRequestBody | None = None

# Operation: delete_checklist_item
class DeleteChecklistItemRequestPath(StrictModel):
    checklist_id: str = Field(default=..., description="The unique identifier (UUID) of the checklist from which the item will be deleted.", examples=['b955c4dc'])
    checklist_item_id: str = Field(default=..., description="The unique identifier (UUID) of the specific checklist item to be deleted.", examples=['21e08dc8'])
class DeleteChecklistItemRequest(StrictModel):
    """Permanently removes a specific line item from a task checklist. This action cannot be undone and will delete the item and its associated data."""
    path: DeleteChecklistItemRequestPath

# Operation: list_task_comments
class GetTaskCommentsRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task whose comments you want to retrieve.", examples=['9hz'])
class GetTaskCommentsRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to `true` if referencing the task by its custom task ID instead of the default ClickUp task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team ID) required when `custom_task_ids` is set to `true` to correctly resolve the custom task ID.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetTaskCommentsRequest(StrictModel):
    """Retrieve comments for a specific task, returned in reverse chronological order (newest to oldest). By default returns the 25 most recent comments; use the `start` and `start_id` parameters together with the last comment of the current response to paginate through older comments."""
    path: GetTaskCommentsRequestPath
    query: GetTaskCommentsRequestQuery | None = None

# Operation: add_task_comment
class CreateTaskCommentRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to which the comment will be added.", examples=['9hz'])
class CreateTaskCommentRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if referencing the task by its custom task ID instead of the default system-generated ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateTaskCommentRequestBody(StrictModel):
    comment_text: str = Field(default=..., description="The text content of the comment to be added to the task.")
    assignee: int | None = Field(default=None, description="The user ID of the individual to assign to this comment.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    group_assignee: str | None = Field(default=None, description="The ID of the group to assign to this comment.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    notify_all: bool = Field(default=..., description="When true, the comment creator is also notified in addition to task assignees and watchers, who are always notified regardless of this setting.")
class CreateTaskCommentRequest(StrictModel):
    """Add a new comment to a specified task, with options to assign the comment to a user or group and notify all relevant parties."""
    path: CreateTaskCommentRequestPath
    query: CreateTaskCommentRequestQuery | None = None
    body: CreateTaskCommentRequestBody

# Operation: list_chat_view_comments
class GetChatViewCommentsRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the Chat view whose comments you want to retrieve.", examples=['3c'])
class GetChatViewCommentsRequestQuery(StrictModel):
    start: int | None = Field(default=None, description="The timestamp of a Chat view comment to paginate from, expressed as Unix time in milliseconds. Use the date of the oldest comment from the previous response to retrieve the next page of comments.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    start_id: str | None = Field(default=None, description="The unique identifier of a Chat view comment to paginate from. Use the ID of the oldest comment from the previous response alongside the `start` parameter to retrieve the next page of comments.")
class GetChatViewCommentsRequest(StrictModel):
    """Retrieve comments from a Chat view, returning the most recent 25 comments by default. Use the date and ID of the oldest comment from a previous response to paginate and retrieve the next 25 comments."""
    path: GetChatViewCommentsRequestPath
    query: GetChatViewCommentsRequestQuery | None = None

# Operation: create_chat_view_comment
class CreateChatViewCommentRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the Chat view to which the comment will be added.", examples=['3c'])
class CreateChatViewCommentRequestBody(StrictModel):
    comment_text: str = Field(default=..., description="The text content of the comment to post on the Chat view.")
    notify_all: bool = Field(default=..., description="When set to true, the creator of the comment is also notified upon posting. Assignees and watchers on the view are always notified regardless of this setting.")
class CreateChatViewCommentRequest(StrictModel):
    """Adds a new comment to a specified Chat view. Optionally notifies the comment creator in addition to the assignees and watchers who are always notified."""
    path: CreateChatViewCommentRequestPath
    body: CreateChatViewCommentRequestBody

# Operation: list_comments
class GetListCommentsRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique identifier of the List whose comments you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[124])
class GetListCommentsRequestQuery(StrictModel):
    start: int | None = Field(default=None, description="The timestamp of the oldest comment from the previous page, used to paginate to the next set of 25 comments. Provide as Unix time in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    start_id: str | None = Field(default=None, description="The unique comment ID of the oldest comment from the previous page, used alongside the start timestamp to paginate to the next set of 25 comments.")
class GetListCommentsRequest(StrictModel):
    """Retrieve comments added to a specific List, returning the most recent 25 by default. Use the oldest comment's date and ID as pagination cursors to fetch earlier comments in batches of 25."""
    path: GetListCommentsRequestPath
    query: GetListCommentsRequestQuery | None = None

# Operation: add_list_comment
class CreateListCommentRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique identifier of the List to which the comment will be added.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[124])
class CreateListCommentRequestBody(StrictModel):
    comment_text: str = Field(default=..., description="The text content of the comment to be posted on the List.")
    assignee: int = Field(default=..., description="The user ID of the individual to assign to this comment.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    notify_all: bool = Field(default=..., description="When set to true, the creator of the comment will also receive a notification. Assignees and watchers on the List are always notified regardless of this setting.")
class CreateListCommentRequest(StrictModel):
    """Adds a comment to a specified List, optionally notifying the comment creator in addition to the standard assignees and watchers who are always notified."""
    path: CreateListCommentRequestPath
    body: CreateListCommentRequestBody

# Operation: update_comment
class UpdateCommentRequestPath(StrictModel):
    comment_id: float = Field(default=..., description="The unique identifier of the comment to update.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[456])
class UpdateCommentRequestBody(StrictModel):
    comment_text: str = Field(default=..., description="The updated text content to replace the existing comment body.")
    assignee: int = Field(default=..., description="The user ID of the individual to assign the comment to.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    group_assignee: int | None = Field(default=None, description="The group ID to assign the comment to, used when assigning to a team or group rather than an individual.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    resolved: bool = Field(default=..., description="Set to true to mark the comment as resolved, or false to mark it as unresolved.")
class UpdateCommentRequest(StrictModel):
    """Update an existing task comment by modifying its text, assigning it to a user or group, or marking it as resolved. All core fields must be provided in the request."""
    path: UpdateCommentRequestPath
    body: UpdateCommentRequestBody

# Operation: delete_comment
class DeleteCommentRequestPath(StrictModel):
    comment_id: float = Field(default=..., description="The unique numeric identifier of the comment to delete.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[456])
class DeleteCommentRequest(StrictModel):
    """Permanently deletes a specific task comment by its unique identifier. This action is irreversible and removes the comment from the task."""
    path: DeleteCommentRequestPath

# Operation: list_comment_replies
class GetThreadedCommentsRequestPath(StrictModel):
    comment_id: float = Field(default=..., description="The unique identifier of the parent comment whose threaded replies should be retrieved.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[456])
class GetThreadedCommentsRequest(StrictModel):
    """Retrieves all threaded reply comments nested under a specified parent comment. The parent comment itself is excluded from the returned results."""
    path: GetThreadedCommentsRequestPath

# Operation: reply_to_comment
class CreateThreadedCommentRequestPath(StrictModel):
    comment_id: float = Field(default=..., description="The unique identifier of the parent comment to reply to.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[456])
class CreateThreadedCommentRequestBody(StrictModel):
    comment_text: str = Field(default=..., description="The text content of the threaded reply comment.")
    assignee: int | None = Field(default=None, description="The user ID of the individual to assign this comment to.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    group_assignee: str | None = Field(default=None, description="The identifier of the group to assign this comment to.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    notify_all: bool = Field(default=..., description="When true, the original comment creator is also notified of this reply. Assignees and task watchers are always notified regardless of this setting.")
class CreateThreadedCommentRequest(StrictModel):
    """Create a threaded reply to an existing comment on a task. Supports assigning the reply to a user or group and controlling notification behavior."""
    path: CreateThreadedCommentRequestPath
    body: CreateThreadedCommentRequestBody

# Operation: list_custom_fields
class GetAccessibleCustomFieldsRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the List whose Custom Fields you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetAccessibleCustomFieldsRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type format for the request, indicating the content format expected by the API.", examples=['application/json'])
class GetAccessibleCustomFieldsRequest(StrictModel):
    """Retrieves all Custom Fields accessible to the authenticated user within a specific List. Use this to discover available field definitions before reading or writing custom field data."""
    path: GetAccessibleCustomFieldsRequestPath
    header: GetAccessibleCustomFieldsRequestHeader

# Operation: list_folder_custom_fields
class GetFolderAvailableFieldsRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique numeric identifier of the folder whose custom fields you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetFolderAvailableFieldsRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, used to indicate the format of the data being sent to the server.", examples=['application/json'])
class GetFolderAvailableFieldsRequest(StrictModel):
    """Retrieves all Custom Fields created at the Folder level for the specified folder. Note that Custom Fields created at the List level within the folder are not included in the results."""
    path: GetFolderAvailableFieldsRequestPath
    header: GetFolderAvailableFieldsRequestHeader

# Operation: list_space_custom_fields
class GetSpaceAvailableFieldsRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space whose Custom Fields you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetSpaceAvailableFieldsRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, used to indicate the format of the data being sent.", examples=['application/json'])
class GetSpaceAvailableFieldsRequest(StrictModel):
    """Retrieves all Custom Fields created at the Space level for a specific Space. Note that Custom Fields created at the Folder or List level are not included in the results."""
    path: GetSpaceAvailableFieldsRequestPath
    header: GetSpaceAvailableFieldsRequestHeader

# Operation: list_workspace_custom_fields
class GetTeamAvailableFieldsRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose Workspace-level Custom Fields you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetTeamAvailableFieldsRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, indicating the format of the request body sent to the API.", examples=['application/json'])
class GetTeamAvailableFieldsRequest(StrictModel):
    """Retrieves all Custom Fields created at the Workspace level for a specific Workspace. Note that Custom Fields created at the Space, Folder, or List level are not included in the results."""
    path: GetTeamAvailableFieldsRequestPath
    header: GetTeamAvailableFieldsRequestHeader

# Operation: set_task_custom_field_value
class SetCustomFieldValueRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task you want to update with a Custom Field value.", examples=['9hv'])
    field_id: str = Field(default=..., description="The universally unique identifier (UUID) of the Custom Field you want to set. Retrieve this from the Get Accessible Custom Fields or Get Task endpoints.", examples=['b955c4dc'])
class SetCustomFieldValueRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if you are referencing the task by its Custom Task ID instead of the standard task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when referencing a task by its Custom Task ID. Must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class SetCustomFieldValueRequestBody(StrictModel):
    body: SetCustomFieldValueBodyV0 | SetCustomFieldValueBodyV1 | SetCustomFieldValueBodyV2 | SetCustomFieldValueBodyV3 | SetCustomFieldValueBodyV4 | SetCustomFieldValueBodyV5 | SetCustomFieldValueBodyV6 | SetCustomFieldValueBodyV7 | SetCustomFieldValueBodyV8 | SetCustomFieldValueBodyV9 | SetCustomFieldValueBodyV10 | SetCustomFieldValueBodyV11 | SetCustomFieldValueBodyV12 | SetCustomFieldValueBodyV13 | SetCustomFieldValueBodyV14 | SetCustomFieldValueBodyV15 | None = Field(default=None, description="The request body containing the value to set for the Custom Field. The shape of the value varies by field type — supported types include URLs, UUIDs, email addresses, phone numbers, dates (millisecond timestamps), text, numbers, currency, user lists, label lists, dropdowns, progress, file lists, location objects, and booleans.", examples=[{'value': 'https://clickup.com/api'}, {'value': 'uuid1234'}, {'value': 'user@company.com'}, {'value': '+1 201 555 0123'}, {'value': 1667367645000, 'value_options': {'time': True}}, {'value': 'This is short or long text in a Custom Field.'}, {'value': -28}, {'value': 8000}, {'value': {'add': ['abcd1234', 'efghi5678'], 'rem': ['jklm9876', 'yuiop5678']}}, {'value': {'add': [123, 456], 'rem': [987, 765]}}, {'value': 4}, {'value': {'current': 20}}, {'value': ['uuid1234', 'uuid9876']}, {'value': {'location': {'lat': -28.016667, 'lng': 153.4}, 'formatted_address': 'Gold Coast QLD, Australia'}}, {'value': True}])
class SetCustomFieldValueRequest(StrictModel):
    """Set or update the value of a specific Custom Field on a task. Requires the task ID and the UUID of the Custom Field to update."""
    path: SetCustomFieldValueRequestPath
    query: SetCustomFieldValueRequestQuery | None = None
    body: SetCustomFieldValueRequestBody | None = None

# Operation: clear_task_custom_field_value
class RemoveCustomFieldValueRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task from which the Custom Field value will be cleared.", examples=['9hv'])
    field_id: str = Field(default=..., description="The UUID of the Custom Field whose value should be removed from the task.", examples=['b955c4dc'])
class RemoveCustomFieldValueRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team_id) required when using custom task IDs; must be paired with custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class RemoveCustomFieldValueRequest(StrictModel):
    """Clears the stored value of a specific Custom Field on a task without deleting the Custom Field definition or its available options."""
    path: RemoveCustomFieldValueRequestPath
    query: RemoveCustomFieldValueRequestQuery | None = None

# Operation: add_task_dependency
class AddDependencyRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The ID of the task for which the dependency relationship is being defined — either the task that is waiting on another task or the task that is blocking another task.", examples=['9hv'])
class AddDependencyRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference tasks by their custom task IDs instead of their default system-generated IDs. Requires `team_id` to also be provided.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when `custom_task_ids` is true, used to resolve custom task IDs within the correct Workspace scope.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class AddDependencyRequestBody(StrictModel):
    """Use the `depends_on` parameter in the request body to specify the task that must be completed before the task in the path parameter.\\
 \\
Use the `dependency_of` parameter in the request body to specify the task that's waiting for the task in the path parameter to be completed.\\
 \\
You can only use one per request."""
    depends_on: str | None = Field(default=None, description="The ID of the task that the specified task (`task_id`) is waiting on — i.e., the task that must be completed before `task_id` can proceed.")
    dependency_of: str | None = Field(default=None, description="The ID of the task that the specified task (`task_id`) is blocking — i.e., the task that cannot proceed until `task_id` is completed.")
class AddDependencyRequest(StrictModel):
    """Create a dependency relationship between two tasks, setting one task as waiting on or blocking another. Use `depends_on` to specify a task this task is waiting on, or `dependency_of` to specify a task this task is blocking."""
    path: AddDependencyRequestPath
    query: AddDependencyRequestQuery | None = None
    body: AddDependencyRequestBody | None = None

# Operation: delete_task_dependency
class DeleteDependencyRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the primary task whose dependency relationship is being removed.", examples=['9hv'])
class DeleteDependencyRequestQuery(StrictModel):
    depends_on: str = Field(default=..., description="The ID of the task that the primary task depends on — i.e., the prerequisite task to be unlinked.", examples=['9hz'])
    dependency_of: str = Field(default=..., description="The ID of the task that depends on the primary task — i.e., the downstream task to be unlinked.", examples=['9hz'])
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference tasks by their custom task IDs instead of their system-generated IDs. Requires the team_id parameter to also be provided.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team) required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve custom task references.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class DeleteDependencyRequest(StrictModel):
    """Remove a dependency relationship between two tasks, unlinking them so that one no longer depends on the other. Both the target task and the related dependent or prerequisite task must be specified."""
    path: DeleteDependencyRequestPath
    query: DeleteDependencyRequestQuery

# Operation: link_task
class AddTaskLinkRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The ID of the task initiating the link (the source task).", examples=['9hv'])
    links_to: str = Field(default=..., description="The ID of the task to link to (the target task).", examples=['9hz'])
class AddTaskLinkRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference tasks by their custom task IDs instead of their default system IDs. Requires team_id to also be provided when enabled.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team) required when custom_task_ids is set to true, used to resolve custom task IDs within the correct workspace scope.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class AddTaskLinkRequest(StrictModel):
    """Creates a directional link between two tasks, equivalent to using the Task Links feature in the task's right-hand sidebar. Only task-to-task links are supported; general or cross-object links are not."""
    path: AddTaskLinkRequestPath
    query: AddTaskLinkRequestQuery | None = None

# Operation: delete_task_link
class DeleteTaskLinkRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the source task from which the link will be removed.", examples=['9hv'])
    links_to: str = Field(default=..., description="The unique identifier of the target task that is currently linked to the source task.", examples=['9hz'])
class DeleteTaskLinkRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference tasks by their custom task IDs instead of their default system-generated IDs. Requires the team_id parameter to also be provided.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve tasks within the specified Workspace.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class DeleteTaskLinkRequest(StrictModel):
    """Removes the dependency or relationship link between two tasks. Both task IDs must be provided to identify the specific link to delete."""
    path: DeleteTaskLinkRequestPath
    query: DeleteTaskLinkRequestQuery | None = None

# Operation: list_folders
class GetFoldersRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space whose Folders you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[789])
class GetFoldersRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="When set to true, returns only archived Folders; when false or omitted, returns only active Folders.", examples=[False])
class GetFoldersRequest(StrictModel):
    """Retrieve all Folders within a specified Space. Optionally include archived Folders in the results."""
    path: GetFoldersRequestPath
    query: GetFoldersRequestQuery | None = None

# Operation: create_folder
class CreateFolderRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space in which the new folder will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[789])
class CreateFolderRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new folder, used to identify it within the Space.")
class CreateFolderRequest(StrictModel):
    """Creates a new folder within a specified Space to organize lists and tasks. Folders help structure your workspace hierarchy beneath a Space."""
    path: CreateFolderRequestPath
    body: CreateFolderRequestBody

# Operation: get_folder
class GetFolderRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique numeric identifier of the folder to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[457])
class GetFolderRequest(StrictModel):
    """Retrieves a folder and the Lists contained within it. Use this to inspect the structure and contents of a specific folder."""
    path: GetFolderRequestPath

# Operation: rename_folder
class UpdateFolderRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique numeric identifier of the folder to rename.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[457])
class UpdateFolderRequestBody(StrictModel):
    name: str = Field(default=..., description="The new name to assign to the folder.")
class UpdateFolderRequest(StrictModel):
    """Renames an existing folder by updating its display name. The folder's contents and structure remain unchanged."""
    path: UpdateFolderRequestPath
    body: UpdateFolderRequestBody

# Operation: delete_folder
class DeleteFolderRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique numeric identifier of the folder to be deleted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[457])
class DeleteFolderRequest(StrictModel):
    """Permanently deletes a folder from your Workspace. This action cannot be undone, so ensure the correct folder ID is specified before proceeding."""
    path: DeleteFolderRequestPath

# Operation: list_goals
class GetGoalsRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose Goals you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetGoalsRequestQuery(StrictModel):
    include_completed: bool | None = Field(default=None, description="When set to true, completed Goals are included in the response alongside active ones; omitting this parameter or setting it to false returns only active Goals.", examples=[True])
class GetGoalsRequest(StrictModel):
    """Retrieves all Goals available in a specified Workspace, with an option to include completed Goals in the results."""
    path: GetGoalsRequestPath
    query: GetGoalsRequestQuery | None = None

# Operation: create_goal
class CreateGoalRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace where the Goal will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateGoalRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name of the Goal.")
    due_date: int = Field(default=..., description="The deadline for the Goal expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    description: str = Field(default=..., description="A detailed description providing context or additional information about the Goal.")
    multiple_owners: bool = Field(default=..., description="Set to true to allow multiple users to own this Goal simultaneously, or false to restrict to a single owner.")
    owners: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., description="List of user IDs assigned as owners of the Goal. Order is not significant; each item should be a valid integer user ID.")
    color: str = Field(default=..., description="A color used to visually identify the Goal in the UI, specified as a hex color code.")
class CreateGoalRequest(StrictModel):
    """Creates a new Goal within a specified Workspace, allowing you to define objectives with ownership, due dates, and visual categorization."""
    path: CreateGoalRequestPath
    body: CreateGoalRequestBody

# Operation: get_goal
class GetGoalRequestPath(StrictModel):
    goal_id: str = Field(default=..., description="The unique UUID identifier of the goal to retrieve.", examples=['e53a033c'])
class GetGoalRequest(StrictModel):
    """Retrieves the full details of a specific goal, including its associated targets and current progress. Use this to inspect a goal's configuration and status by its unique identifier."""
    path: GetGoalRequestPath

# Operation: update_goal
class UpdateGoalRequestPath(StrictModel):
    goal_id: str = Field(default=..., description="The unique identifier (UUID) of the Goal to update.", examples=['e53a033c'])
class UpdateGoalRequestBody(StrictModel):
    name: str = Field(default=..., description="The new display name for the Goal.")
    due_date: int = Field(default=..., description="The due date for the Goal, represented as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    description: str = Field(default=..., description="The full replacement description for the Goal. This overwrites the existing description entirely.")
    rem_owners: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., description="List of user IDs to remove as owners of the Goal. Order is not significant; each item should be a valid user ID integer.")
    add_owners: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., description="List of user IDs to add as owners of the Goal. Order is not significant; each item should be a valid user ID integer.")
    color: str = Field(default=..., description="The color to assign to the Goal, used for visual categorization in the UI. Provide a valid hex color code.")
class UpdateGoalRequest(StrictModel):
    """Update an existing Goal's properties, including its name, due date, description, color, and ownership. Use this to rename a Goal, adjust its deadline, modify its description, or add and remove assigned owners."""
    path: UpdateGoalRequestPath
    body: UpdateGoalRequestBody

# Operation: delete_goal
class DeleteGoalRequestPath(StrictModel):
    goal_id: str = Field(default=..., description="The unique identifier (UUID) of the Goal to be deleted.", examples=['e53a033c'])
class DeleteGoalRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, used to indicate the format of the data being sent.", examples=['application/json'])
class DeleteGoalRequest(StrictModel):
    """Permanently removes a specified Goal from your Workspace. This action is irreversible and will delete all associated goal data."""
    path: DeleteGoalRequestPath
    header: DeleteGoalRequestHeader

# Operation: create_key_result
class CreateKeyResultRequestPath(StrictModel):
    goal_id: str = Field(default=..., description="The unique identifier of the goal to which this key result will be added.", examples=['e53a033c'])
class CreateKeyResultRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name of the key result that describes the measurable target.")
    owners: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., description="An array of user IDs representing the owners responsible for this key result. Order is not significant.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The measurement type for this key result. Valid values are: `number` (numeric count), `currency` (monetary value), `boolean` (true/false completion), `percentage` (0–100 scale), or `automatic` (derived from linked tasks or lists).")
    steps_start: int = Field(default=..., description="The starting value of the target range, representing the baseline or initial progress point.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    steps_end: int = Field(default=..., description="The ending value of the target range, representing the goal completion threshold.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    unit: str = Field(default=..., description="The unit label associated with the key result value (e.g., a currency code or custom unit name), applicable when the type is `number` or `currency`.")
    task_ids: list[str] = Field(default=..., description="An array of task IDs to link with this key result, allowing progress to be tracked automatically based on task completion. Order is not significant.")
    list_ids: list[str] = Field(default=..., description="An array of List IDs to link with this key result, allowing progress to be tracked automatically based on list task completion. Order is not significant.")
class CreateKeyResultRequest(StrictModel):
    """Create a new key result (target) within a specified goal to define measurable outcomes. Supports multiple target types including numeric, currency, boolean, percentage, and automatic tracking."""
    path: CreateKeyResultRequestPath
    body: CreateKeyResultRequestBody

# Operation: update_key_result
class EditKeyResultRequestPath(StrictModel):
    key_result_id: str = Field(default=..., description="The unique identifier of the key result to update.", examples=['947d46ed'])
class EditKeyResultRequestBody(StrictModel):
    """All properties available in the Create Key Result endpoint may also be used along with the additional properties below."""
    steps_current: int = Field(default=..., description="The current number of steps completed toward the key result target. Should reflect the latest progress value.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    note: str = Field(default=..., description="A note or comment describing the current status, blockers, or context for this progress update.")
class EditKeyResultRequest(StrictModel):
    """Update the progress and notes for an existing key result. Use this to record current step completion and add contextual notes to track advancement toward a goal."""
    path: EditKeyResultRequestPath
    body: EditKeyResultRequestBody

# Operation: delete_key_result
class DeleteKeyResultRequestPath(StrictModel):
    key_result_id: str = Field(default=..., description="The unique identifier (UUID) of the key result to delete.", examples=['947d46ed'])
class DeleteKeyResultRequest(StrictModel):
    """Permanently deletes a key result (target) from a Goal. This action is irreversible and removes the specified key result and its associated data."""
    path: DeleteKeyResultRequestPath

# Operation: invite_workspace_guest
class InviteGuestToWorkspaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace to which the guest will be invited.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class InviteGuestToWorkspaceRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the guest to invite to the Workspace.")
    can_edit_tags: bool | None = Field(default=None, description="Whether the guest is permitted to edit tags within the Workspace.")
    can_see_time_spent: bool | None = Field(default=None, description="Whether the guest can view time spent on tasks.")
    can_see_time_estimated: bool | None = Field(default=None, description="Whether the guest can view time estimates on tasks.")
    can_create_views: bool | None = Field(default=None, description="Whether the guest is allowed to create new views.")
    can_see_points_estimated: bool | None = Field(default=None, description="Whether the guest can view point estimates on tasks.")
    custom_role_id: int | None = Field(default=None, description="The ID of a custom role to assign to the guest upon invitation.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class InviteGuestToWorkspaceRequest(StrictModel):
    """Invites a guest user to a Workspace by email on an Enterprise Plan. After inviting, grant the guest access to specific Folders, Lists, or Tasks using the corresponding add-guest endpoints."""
    path: InviteGuestToWorkspaceRequestPath
    body: InviteGuestToWorkspaceRequestBody

# Operation: get_guest
class GetGuestRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace (team) containing the guest.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    guest_id: float = Field(default=..., description="The unique identifier of the guest user to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class GetGuestRequest(StrictModel):
    """Retrieves detailed information about a specific guest user within a Workspace. Available exclusively on the Enterprise Plan."""
    path: GetGuestRequestPath

# Operation: update_workspace_guest
class EditGuestOnWorkspaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace where the guest resides.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    guest_id: float = Field(default=..., description="The unique identifier of the guest whose settings are being updated.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class EditGuestOnWorkspaceRequestBody(StrictModel):
    can_see_points_estimated: bool | None = Field(default=None, description="Whether the guest is allowed to view point estimations on tasks.")
    can_edit_tags: bool | None = Field(default=None, description="Whether the guest is allowed to create, edit, and delete tags.")
    can_see_time_spent: bool | None = Field(default=None, description="Whether the guest is allowed to view time tracked (spent) on tasks.")
    can_see_time_estimated: bool | None = Field(default=None, description="Whether the guest is allowed to view time estimations on tasks.")
    can_create_views: bool | None = Field(default=None, description="Whether the guest is allowed to create new views within the Workspace.")
    custom_role_id: int | None = Field(default=None, description="The ID of a custom role to assign to the guest, controlling their permission level within the Workspace.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class EditGuestOnWorkspaceRequest(StrictModel):
    """Update permission settings and role assignment for a guest on a Workspace. This endpoint is only available on the Enterprise Plan."""
    path: EditGuestOnWorkspaceRequestPath
    body: EditGuestOnWorkspaceRequestBody | None = None

# Operation: remove_workspace_guest
class RemoveGuestFromWorkspaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace from which the guest will be removed.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    guest_id: float = Field(default=..., description="The unique identifier of the guest whose Workspace access will be revoked.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class RemoveGuestFromWorkspaceRequest(StrictModel):
    """Revokes a guest's access to the specified Workspace, removing all associated permissions. This endpoint is only available on the Enterprise Plan."""
    path: RemoveGuestFromWorkspaceRequestPath

# Operation: add_guest_to_task
class AddGuestToTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to share with the guest.", examples=['c04'])
    guest_id: float = Field(default=..., description="The unique numeric identifier of the guest user to add to the task.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class AddGuestToTaskRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="Whether to include details of items shared with the guest in the response. Set to false to exclude shared item details; defaults to true.", examples=[False])
class AddGuestToTaskRequestBody(StrictModel):
    permission_level: str = Field(default=..., description="The access level granted to the guest on this task. Accepted values are: read (view only), comment, edit, or create (full access).")
class AddGuestToTaskRequest(StrictModel):
    """Share a task with a guest user by granting them a specific permission level. This endpoint is only available to Workspaces on the Enterprise Plan."""
    path: AddGuestToTaskRequestPath
    query: AddGuestToTaskRequestQuery | None = None
    body: AddGuestToTaskRequestBody

# Operation: remove_task_guest
class RemoveGuestFromTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task from which the guest's access will be revoked.", examples=['c04'])
    guest_id: float = Field(default=..., description="The numeric identifier of the guest user whose access to the task will be removed.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class RemoveGuestFromTaskRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="Controls whether the response includes details of other items shared with the guest. Set to false to exclude shared item details; defaults to true.", examples=[False])
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the standard ClickUp task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the task.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class RemoveGuestFromTaskRequest(StrictModel):
    """Revoke a guest's access to a specific task, removing their ability to view or interact with it. This endpoint is only available on the Enterprise Plan."""
    path: RemoveGuestFromTaskRequestPath
    query: RemoveGuestFromTaskRequestQuery | None = None

# Operation: add_guest_to_list
class AddGuestToListRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique identifier of the List to share with the guest.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[1427])
    guest_id: float = Field(default=..., description="The unique identifier of the guest user to add to the List.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class AddGuestToListRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="Whether to include details of items already shared with the guest. Set to false to exclude shared item details; defaults to true.", examples=[False])
class AddGuestToListRequestBody(StrictModel):
    permission_level: str = Field(default=..., description="The access level granted to the guest on this List. Accepted values are: read (view only), comment, edit, or create (full access).")
class AddGuestToListRequest(StrictModel):
    """Share a List with a guest user by granting them a specific permission level. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""
    path: AddGuestToListRequestPath
    query: AddGuestToListRequestQuery | None = None
    body: AddGuestToListRequestBody

# Operation: remove_list_guest
class RemoveGuestFromListRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique identifier of the List from which the guest's access will be revoked.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[1427])
    guest_id: float = Field(default=..., description="The unique identifier of the guest whose access to the List will be removed.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class RemoveGuestFromListRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="Controls whether the response includes details of items shared with the guest. Set to false to exclude shared item details; defaults to true.", examples=[False])
class RemoveGuestFromListRequest(StrictModel):
    """Revokes a guest's access to a specific List, removing their ability to view or interact with it. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""
    path: RemoveGuestFromListRequestPath
    query: RemoveGuestFromListRequestQuery | None = None

# Operation: add_guest_to_folder
class AddGuestToFolderRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique identifier of the folder to share with the guest.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[1057])
    guest_id: float = Field(default=..., description="The unique identifier of the guest user to whom folder access will be granted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class AddGuestToFolderRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="Whether to include details of items already shared with the guest in the response. Set to false to exclude shared item details.", examples=[False])
class AddGuestToFolderRequestBody(StrictModel):
    permission_level: str = Field(default=..., description="The access level granted to the guest for this folder. Accepted values are: read (view only), comment, edit, or create (full access).")
class AddGuestToFolderRequest(StrictModel):
    """Share a folder with a guest user by granting them a specific permission level. This endpoint is only available on the Enterprise Plan."""
    path: AddGuestToFolderRequestPath
    query: AddGuestToFolderRequestQuery | None = None
    body: AddGuestToFolderRequestBody

# Operation: remove_folder_guest
class RemoveGuestFromFolderRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique numeric identifier of the Folder from which the guest's access will be revoked.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[1057])
    guest_id: float = Field(default=..., description="The unique numeric identifier of the guest whose access to the Folder will be removed.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class RemoveGuestFromFolderRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="When set to false, the response excludes details of items shared with the guest; defaults to true to include shared item details.", examples=[False])
class RemoveGuestFromFolderRequest(StrictModel):
    """Revoke a guest's access to a specific Folder, removing their ability to view or interact with its contents. This endpoint is only available on the Enterprise Plan."""
    path: RemoveGuestFromFolderRequestPath
    query: RemoveGuestFromFolderRequestQuery | None = None

# Operation: list_folder_lists
class GetListsRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique identifier of the Folder whose Lists you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[456])
class GetListsRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="When set to true, includes archived Lists in the response alongside active ones. Defaults to false, returning only active Lists.", examples=[False])
class GetListsRequest(StrictModel):
    """Retrieve all Lists contained within a specified Folder. Optionally include archived Lists in the results."""
    path: GetListsRequestPath
    query: GetListsRequestQuery | None = None

# Operation: create_list
class CreateListRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique identifier of the Folder in which the new List will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[456])
class CreateListRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new List.")
    markdown_content: str | None = Field(default=None, description="Optional description for the List, formatted using Markdown. Use this field instead of a plain-text content field to apply rich formatting.")
    due_date: int | None = Field(default=None, description="The due date for the List, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    due_date_time: bool | None = Field(default=None, description="When set to true, the due date includes a specific time component; when false, only the date is considered.")
    priority: int | None = Field(default=None, description="The priority level for the List, represented as an integer (e.g., 1 = urgent, 2 = high, 3 = normal, 4 = low).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    assignee: int | None = Field(default=None, description="The user ID of the member to assign as the owner of this List.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    status: str | None = Field(default=None, description="The color status of the List, which represents a visual label rather than task-level statuses defined within the List.")
class CreateListRequest(StrictModel):
    """Creates a new List inside a specified Folder, allowing you to organize tasks with optional metadata such as due dates, priority, assignee, and a color status."""
    path: CreateListRequestPath
    body: CreateListRequestBody

# Operation: create_folder_from_template
class CreateFolderFromTemplateRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Space where the new Folder will be created.")
    template_id: str = Field(default=..., description="The unique identifier of the Folder template to apply, always prefixed with `t-`. Retrieve available template IDs using the Get Folder Templates endpoint.", examples=['t-7162342'])
class CreateFolderFromTemplateRequestBodyOptions(StrictModel):
    return_immediately: bool | None = Field(default=None, validation_alias="return_immediately", serialization_alias="return_immediately", description="When true, returns the new Folder ID immediately after access checks without waiting for all nested assets to finish being created. When false, the request waits until the Folder and all its contents are fully created before responding.")
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="Optional description text to apply to the new Folder.")
    time_estimate: bool | None = Field(default=None, validation_alias="time_estimate", serialization_alias="time_estimate", description="When true, imports time estimate data (hours, minutes, and seconds) from the template tasks.")
    automation: bool | None = Field(default=None, validation_alias="automation", serialization_alias="automation", description="When true, imports automation rules defined in the template.")
    include_views: bool | None = Field(default=None, validation_alias="include_views", serialization_alias="include_views", description="When true, imports view configurations defined in the template.")
    old_due_date: bool | None = Field(default=None, validation_alias="old_due_date", serialization_alias="old_due_date", description="When true, imports the original due dates from template tasks.")
    old_start_date: bool | None = Field(default=None, validation_alias="old_start_date", serialization_alias="old_start_date", description="When true, imports the original start dates from template tasks.")
    old_followers: bool | None = Field(default=None, validation_alias="old_followers", serialization_alias="old_followers", description="When true, imports the watcher (follower) assignments from template tasks.")
    comment_attachments: bool | None = Field(default=None, validation_alias="comment_attachments", serialization_alias="comment_attachments", description="When true, imports file attachments from task comments in the template.")
    recur_settings: bool | None = Field(default=None, validation_alias="recur_settings", serialization_alias="recur_settings", description="When true, imports recurring task settings from the template.")
    old_tags: bool | None = Field(default=None, validation_alias="old_tags", serialization_alias="old_tags", description="When true, imports tags assigned to tasks in the template.")
    old_statuses: bool | None = Field(default=None, validation_alias="old_statuses", serialization_alias="old_statuses", description="When true, imports the status configuration (status types and workflow) from the template.")
    subtasks: bool | None = Field(default=None, validation_alias="subtasks", serialization_alias="subtasks", description="When true, imports subtask structures from the template tasks.")
    custom_type: bool | None = Field(default=None, validation_alias="custom_type", serialization_alias="custom_type", description="When true, imports custom task type definitions from the template.")
    old_assignees: bool | None = Field(default=None, validation_alias="old_assignees", serialization_alias="old_assignees", description="When true, imports assignee assignments from template tasks.")
    attachments: bool | None = Field(default=None, validation_alias="attachments", serialization_alias="attachments", description="When true, imports file attachments from template tasks.")
    comment: bool | None = Field(default=None, validation_alias="comment", serialization_alias="comment", description="When true, imports comments from template tasks.")
    old_status: bool | None = Field(default=None, validation_alias="old_status", serialization_alias="old_status", description="When true, imports the current status values of tasks from the template.")
    external_dependencies: bool | None = Field(default=None, validation_alias="external_dependencies", serialization_alias="external_dependencies", description="When true, imports external task dependency relationships from the template.")
    internal_dependencies: bool | None = Field(default=None, validation_alias="internal_dependencies", serialization_alias="internal_dependencies", description="When true, imports internal task dependency relationships from the template.")
    priority: bool | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="When true, imports priority levels assigned to tasks in the template.")
    custom_fields: bool | None = Field(default=None, validation_alias="custom_fields", serialization_alias="custom_fields", description="When true, imports Custom Field definitions and values from template tasks.")
    old_checklists: bool | None = Field(default=None, validation_alias="old_checklists", serialization_alias="old_checklists", description="When true, imports checklist items from template tasks.")
    relationships: bool | None = Field(default=None, validation_alias="relationships", serialization_alias="relationships", description="When true, imports task relationship links (e.g., linked tasks) from the template.")
    old_subtask_assignees: bool | None = Field(default=None, validation_alias="old_subtask_assignees", serialization_alias="old_subtask_assignees", description="When true, imports both subtask structures and their assignee assignments together from the template.")
    start_date: str | None = Field(default=None, validation_alias="start_date", serialization_alias="start_date", description="The project start date used as the anchor point for remapping task dates from the template. Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    due_date: str | None = Field(default=None, validation_alias="due_date", serialization_alias="due_date", description="The project due date used as the anchor point for remapping task dates from the template. Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    remap_start_date: bool | None = Field(default=None, validation_alias="remap_start_date", serialization_alias="remap_start_date", description="When true, recalculates and remaps task start dates relative to the provided project start or due date.")
    skip_weekends: bool | None = Field(default=None, validation_alias="skip_weekends", serialization_alias="skip_weekends", description="When true, excludes Saturday and Sunday when calculating remapped task dates.")
    archived: Literal[1, 2] | None = Field(default=None, validation_alias="archived", serialization_alias="archived", description="Controls whether archived tasks are included: 1 includes archived tasks, 2 includes only archived tasks, and null excludes archived tasks.")
class CreateFolderFromTemplateRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name to assign to the newly created Folder.")
    options: CreateFolderFromTemplateRequestBodyOptions | None = None
class CreateFolderFromTemplateRequest(StrictModel):
    """Create a new Folder within a Space using a predefined Folder template, optionally importing nested assets such as lists, tasks, subtasks, custom fields, and more. Supports both synchronous and asynchronous creation via the `return_immediately` parameter."""
    path: CreateFolderFromTemplateRequestPath
    body: CreateFolderFromTemplateRequestBody

# Operation: list_folderless_lists
class GetFolderlessListsRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space whose folderless Lists you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[789])
class GetFolderlessListsRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="When set to true, includes archived Lists in the response alongside active ones.", examples=[False])
class GetFolderlessListsRequest(StrictModel):
    """Retrieves all Lists within a Space that are not organized inside a Folder. Optionally includes archived Lists in the results."""
    path: GetFolderlessListsRequestPath
    query: GetFolderlessListsRequestQuery | None = None

# Operation: create_folderless_list
class CreateFolderlessListRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space in which the new List will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[789])
class CreateFolderlessListRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new List.")
    markdown_content: str | None = Field(default=None, description="Description body for the List, formatted in Markdown. Use this field instead of `content` when rich text formatting is needed.")
    due_date: int | None = Field(default=None, description="The due date for the List, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    due_date_time: bool | None = Field(default=None, description="When set to true, the due date includes a specific time component; when false, only the date is considered.")
    priority: int | None = Field(default=None, description="The priority level for the List, represented as an integer (e.g., 1 = Urgent, 2 = High, 3 = Normal, 4 = Low).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    assignee: int | None = Field(default=None, description="The user ID of the member to assign as the owner of this List.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    status: str | None = Field(default=None, description="Sets the color of the List, which is referred to as its status. This is distinct from the task-level statuses available within the List.")
class CreateFolderlessListRequest(StrictModel):
    """Creates a new List directly within a Space, without placing it inside a Folder. Use this when you want a top-level List organization within the Space."""
    path: CreateFolderlessListRequestPath
    body: CreateFolderlessListRequestBody

# Operation: get_list
class GetListRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the List to retrieve. To locate this ID, right-click the List in your Sidebar, select Copy link, and extract the last segment of the pasted URL.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[124])
class GetListRequest(StrictModel):
    """Retrieves detailed information about a specific List, including its settings, members, and configuration. Use this to inspect or reference a List's properties by its unique ID."""
    path: GetListRequestPath

# Operation: update_list
class UpdateListRequestPath(StrictModel):
    list_id: str = Field(default=..., description="The unique identifier of the List to update.", examples=['124'])
class UpdateListRequestBody(StrictModel):
    name: str = Field(default=..., description="The new display name for the List.")
    markdown_content: str | None = Field(default=None, description="The List's description body formatted in Markdown. Use this field instead of `content` to apply rich text formatting.")
    priority: int | None = Field(default=None, description="The priority level for the List, represented as an integer (e.g., 1 = urgent, 2 = high, 3 = normal, 4 = low).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    assignee: str | None = Field(default=None, description="The user ID of the member to assign as the List's default assignee.")
    status: str | None = Field(default=None, description="The color applied to the List, referred to as its status. This controls the List's color indicator, not the task statuses within the List.")
    unset_status: bool | None = Field(default=None, description="When set to true, removes the currently applied color from the List. Defaults to false, which preserves the existing color.")
    due_date: dict | None = Field(default=None, json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    due_date_time: bool | None = None
class UpdateListRequest(StrictModel):
    """Update a List's properties including its name, description, priority, assignee, due date, and color. Use this to rename a List or modify any of its metadata fields."""
    path: UpdateListRequestPath
    body: UpdateListRequestBody

# Operation: delete_list
class DeleteListRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the List to be deleted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[124])
class DeleteListRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, used to indicate the format of the data being sent.", examples=['application/json'])
class DeleteListRequest(StrictModel):
    """Permanently deletes a specified List from your Workspace. This action is irreversible and removes the List along with its associated data."""
    path: DeleteListRequestPath
    header: DeleteListRequestHeader

# Operation: add_task_to_list
class AddTaskToListRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the list to which the task will be added.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    task_id: str = Field(default=..., description="The unique string identifier of the task to add to the specified list.", examples=['9hz'])
class AddTaskToListRequest(StrictModel):
    """Adds an existing task to an additional list, enabling the task to appear in multiple lists simultaneously. Requires the Tasks in Multiple Lists ClickApp to be enabled in the workspace."""
    path: AddTaskToListRequestPath

# Operation: remove_task_from_list
class RemoveTaskFromListRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the List from which the task should be removed. Must not be the task's home List.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    task_id: str = Field(default=..., description="The unique string identifier of the task to remove from the specified List.", examples=['9hz'])
class RemoveTaskFromListRequest(StrictModel):
    """Removes a task from an additional (non-home) List it has been added to. Requires the Tasks in Multiple Lists ClickApp to be enabled; a task cannot be removed from its original home List."""
    path: RemoveTaskFromListRequestPath

# Operation: list_task_members
class GetTaskMembersRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task whose explicit members you want to retrieve.", examples=['9hz'])
class GetTaskMembersRequest(StrictModel):
    """Retrieves Workspace members who have been explicitly granted direct access to a specific task. Note: this does not include members with access via a Team, List, Folder, or Space."""
    path: GetTaskMembersRequestPath

# Operation: list_list_members
class GetListMembersRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the List whose explicit members you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetListMembersRequest(StrictModel):
    """Retrieves Workspace members who have been explicitly granted access to a specific List. Note: this does not include members with inherited access via a Team, Folder, or Space."""
    path: GetListMembersRequestPath

# Operation: list_custom_roles
class GetCustomRolesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose Custom Roles you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetCustomRolesRequestQuery(StrictModel):
    include_members: bool | None = Field(default=None, description="When set to true, the response will include the list of members assigned to each Custom Role.", examples=[True])
class GetCustomRolesRequest(StrictModel):
    """Retrieves all Custom Roles available in the specified Workspace, allowing you to review role definitions and optionally include their member assignments."""
    path: GetCustomRolesRequestPath
    query: GetCustomRolesRequestQuery | None = None

# Operation: list_shared_hierarchy
class SharedHierarchyRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace whose shared content you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class SharedHierarchyRequest(StrictModel):
    """Retrieves all tasks, Lists, and Folders that have been shared with the authenticated user within a specified workspace. Useful for discovering shared content accessible to the current user."""
    path: SharedHierarchyRequestPath

# Operation: list_spaces
class GetSpacesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose Spaces you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetSpacesRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="When set to true, returns only archived Spaces; when false or omitted, returns only active Spaces.", examples=[False])
class GetSpacesRequest(StrictModel):
    """Retrieves all Spaces available within a specified Workspace. Member details are only accessible for private Spaces the authenticated user belongs to."""
    path: GetSpacesRequestPath
    query: GetSpacesRequestQuery | None = None

# Operation: create_space
class CreateSpaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace (team) in which the new Space will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateSpaceRequestBodyFeaturesDueDates(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the due dates feature is enabled for tasks in this Space.")
    start_date: bool = Field(default=..., validation_alias="start_date", serialization_alias="start_date", description="Whether start dates are enabled for tasks in this Space.")
    remap_due_dates: bool = Field(default=..., validation_alias="remap_due_dates", serialization_alias="remap_due_dates", description="Whether due dates are automatically remapped for dependent tasks when a parent task's due date changes.")
    remap_closed_due_date: bool = Field(default=..., validation_alias="remap_closed_due_date", serialization_alias="remap_closed_due_date", description="Whether due dates on closed tasks are remapped when rescheduling dependent tasks in this Space.")
class CreateSpaceRequestBodyFeaturesTimeTracking(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether time tracking is enabled for tasks in this Space.")
class CreateSpaceRequestBodyFeaturesTags(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether tags are enabled for tasks in this Space.")
class CreateSpaceRequestBodyFeaturesTimeEstimates(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether time estimates are enabled for tasks in this Space.")
class CreateSpaceRequestBodyFeaturesChecklists(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether checklists are enabled for tasks in this Space.")
class CreateSpaceRequestBodyFeaturesCustomFields(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether custom fields are enabled for tasks in this Space.")
class CreateSpaceRequestBodyFeaturesRemapDependencies(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether dependency dates are automatically remapped when a dependent task's date changes in this Space.")
class CreateSpaceRequestBodyFeaturesDependencyWarning(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether a warning is shown when a task has unresolved dependencies in this Space.")
class CreateSpaceRequestBodyFeaturesPortfolios(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Portfolios feature is enabled for this Space.")
class CreateSpaceRequestBodyFeatures(StrictModel):
    due_dates: CreateSpaceRequestBodyFeaturesDueDates
    time_tracking: CreateSpaceRequestBodyFeaturesTimeTracking
    tags: CreateSpaceRequestBodyFeaturesTags
    time_estimates: CreateSpaceRequestBodyFeaturesTimeEstimates
    checklists: CreateSpaceRequestBodyFeaturesChecklists
    custom_fields: CreateSpaceRequestBodyFeaturesCustomFields
    remap_dependencies: CreateSpaceRequestBodyFeaturesRemapDependencies
    dependency_warning: CreateSpaceRequestBodyFeaturesDependencyWarning
    portfolios: CreateSpaceRequestBodyFeaturesPortfolios
class CreateSpaceRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new Space.")
    multiple_assignees: bool = Field(default=..., description="Whether tasks in this Space can be assigned to more than one user simultaneously.")
    features: CreateSpaceRequestBodyFeatures
class CreateSpaceRequest(StrictModel):
    """Creates a new Space within a specified Workspace, allowing configuration of its name, assignee settings, and feature toggles such as due dates, time tracking, tags, and dependencies."""
    path: CreateSpaceRequestPath
    body: CreateSpaceRequestBody

# Operation: get_space
class GetSpaceRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique numeric identifier of the Space to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[790])
class GetSpaceRequest(StrictModel):
    """Retrieves details for a specific Space within a Workspace, including its settings and configuration."""
    path: GetSpaceRequestPath

# Operation: update_space
class UpdateSpaceRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space to update.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[790])
class UpdateSpaceRequestBodyFeaturesDueDates(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Due Dates ClickApp is enabled for this Space, allowing tasks to have due date fields.")
    start_date: bool = Field(default=..., validation_alias="start_date", serialization_alias="start_date", description="Whether tasks in this Space support a start date field in addition to a due date.")
    remap_due_dates: bool = Field(default=..., validation_alias="remap_due_dates", serialization_alias="remap_due_dates", description="Whether due dates on dependent tasks are automatically remapped when a predecessor task's due date changes.")
    remap_closed_due_date: bool = Field(default=..., validation_alias="remap_closed_due_date", serialization_alias="remap_closed_due_date", description="Whether due dates on closed dependent tasks are also remapped when a predecessor task's due date changes.")
class UpdateSpaceRequestBodyFeaturesTimeTracking(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Time Tracking ClickApp is enabled for this Space, allowing members to log time on tasks.")
class UpdateSpaceRequestBodyFeaturesTags(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Tags ClickApp is enabled for this Space, allowing tasks to be labeled with tags.")
class UpdateSpaceRequestBodyFeaturesTimeEstimates(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Time Estimates ClickApp is enabled for this Space, allowing estimated time to be set on tasks.")
class UpdateSpaceRequestBodyFeaturesChecklists(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Checklists ClickApp is enabled for this Space, allowing checklist items to be added to tasks.")
class UpdateSpaceRequestBodyFeaturesCustomFields(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Custom Fields ClickApp is enabled for this Space, allowing custom data fields to be defined on tasks.")
class UpdateSpaceRequestBodyFeaturesRemapDependencies(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether dependency remapping is enabled, automatically adjusting dependent task dates when a predecessor's dates change.")
class UpdateSpaceRequestBodyFeaturesDependencyWarning(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether a warning is shown when a task with unresolved dependencies is marked complete.")
class UpdateSpaceRequestBodyFeaturesPortfolios(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Whether the Portfolios ClickApp is enabled for this Space, allowing tasks and lists to be tracked in portfolio views.")
class UpdateSpaceRequestBodyFeatures(StrictModel):
    due_dates: UpdateSpaceRequestBodyFeaturesDueDates
    time_tracking: UpdateSpaceRequestBodyFeaturesTimeTracking
    tags: UpdateSpaceRequestBodyFeaturesTags
    time_estimates: UpdateSpaceRequestBodyFeaturesTimeEstimates
    checklists: UpdateSpaceRequestBodyFeaturesChecklists
    custom_fields: UpdateSpaceRequestBodyFeaturesCustomFields
    remap_dependencies: UpdateSpaceRequestBodyFeaturesRemapDependencies
    dependency_warning: UpdateSpaceRequestBodyFeaturesDependencyWarning
    portfolios: UpdateSpaceRequestBodyFeaturesPortfolios
class UpdateSpaceRequestBody(StrictModel):
    name: str = Field(default=..., description="The new display name for the Space.")
    color: str = Field(default=..., description="The color associated with the Space, used for visual identification in the UI.")
    private: bool = Field(default=..., description="Whether the Space is private; private Spaces are only visible to invited members.")
    admin_can_manage: bool = Field(default=..., description="Whether workspace admins are permitted to manage this private Space. Enabling or restricting this setting is an Enterprise Plan feature.")
    multiple_assignees: bool = Field(default=..., description="Whether tasks in this Space can be assigned to multiple members simultaneously.")
    features: UpdateSpaceRequestBodyFeatures
class UpdateSpaceRequest(StrictModel):
    """Update a Space's settings including its name, color, privacy, and enabled ClickApps such as due dates, time tracking, tags, and custom fields."""
    path: UpdateSpaceRequestPath
    body: UpdateSpaceRequestBody

# Operation: delete_space
class DeleteSpaceRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique numeric identifier of the Space to be deleted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[790])
class DeleteSpaceRequest(StrictModel):
    """Permanently deletes a Space from your Workspace. This action is irreversible and removes the Space along with its associated data."""
    path: DeleteSpaceRequestPath

# Operation: list_space_tags
class GetSpaceTagsRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space whose tags you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[512])
class GetSpaceTagsRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type format for the request, indicating the content should be sent as JSON.", examples=['application/json'])
class GetSpaceTagsRequest(StrictModel):
    """Retrieve all task tags available in a specified Space. Use this to discover tags that can be applied to tasks within the Space."""
    path: GetSpaceTagsRequestPath
    header: GetSpaceTagsRequestHeader

# Operation: create_space_tag
class CreateSpaceTagRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space where the new tag will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[512])
class CreateSpaceTagRequestBodyTag(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the tag as it will appear throughout the Space.")
    tag_fg: str = Field(default=..., validation_alias="tag_fg", serialization_alias="tag_fg", description="The foreground (text) color of the tag, specified as a hex color code.")
    tag_bg: str = Field(default=..., validation_alias="tag_bg", serialization_alias="tag_bg", description="The background color of the tag, specified as a hex color code.")
class CreateSpaceTagRequestBody(StrictModel):
    tag: CreateSpaceTagRequestBodyTag
class CreateSpaceTagRequest(StrictModel):
    """Creates a new tag in the specified Space, allowing tasks within that Space to be categorized and labeled with custom colors."""
    path: CreateSpaceTagRequestPath
    body: CreateSpaceTagRequestBody

# Operation: update_space_tag
class EditSpaceTagRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the space that contains the tag to be updated.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[512])
    tag_name: str = Field(default=..., description="The current name of the tag to be edited, used to identify the tag within the space.", examples=['name'])
class EditSpaceTagRequestBodyTag(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The new display name to assign to the tag.")
    fg_color: str = Field(default=..., validation_alias="fg_color", serialization_alias="fg_color", description="The foreground (text) color for the tag, typically provided as a hex color code.")
    bg_color: str = Field(default=..., validation_alias="bg_color", serialization_alias="bg_color", description="The background color for the tag, typically provided as a hex color code.")
class EditSpaceTagRequestBody(StrictModel):
    tag: EditSpaceTagRequestBodyTag
class EditSpaceTagRequest(StrictModel):
    """Updates the name and color properties of an existing tag within a specified space. Use this to rename a tag or change its foreground and background display colors."""
    path: EditSpaceTagRequestPath
    body: EditSpaceTagRequestBody

# Operation: delete_space_tag
class DeleteSpaceTagRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique numeric identifier of the Space from which the tag will be deleted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[512])
    tag_name: str = Field(default=..., description="The URL path identifier of the tag to delete, typically matching the tag's display name.", examples=['name'])
class DeleteSpaceTagRequestBodyTag(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the tag being deleted, used to identify the tag in the request body.")
    tag_fg: str = Field(default=..., validation_alias="tag_fg", serialization_alias="tag_fg", description="The foreground (text) color of the tag, specified as a hex color code.")
    tag_bg: str = Field(default=..., validation_alias="tag_bg", serialization_alias="tag_bg", description="The background color of the tag, specified as a hex color code.")
class DeleteSpaceTagRequestBody(StrictModel):
    tag: DeleteSpaceTagRequestBodyTag
class DeleteSpaceTagRequest(StrictModel):
    """Permanently removes a task tag from a specified Space. The tag will no longer be available for tasks within that Space."""
    path: DeleteSpaceTagRequestPath
    body: DeleteSpaceTagRequestBody

# Operation: add_tag_to_task
class AddTagToTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to which the tag will be added.", examples=['abc'])
    tag_name: str = Field(default=..., description="The name of the tag to add to the task. Must match an existing tag name exactly.", examples=['name'])
class AddTagToTaskRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the default system-generated task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the task.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class AddTagToTaskRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, which must indicate JSON format.", examples=['application/json'])
class AddTagToTaskRequest(StrictModel):
    """Adds an existing tag to a specified task, associating it for organization and filtering purposes. Supports referencing tasks by custom task ID when the appropriate parameters are provided."""
    path: AddTagToTaskRequestPath
    query: AddTagToTaskRequestQuery | None = None
    header: AddTagToTaskRequestHeader

# Operation: remove_task_tag
class RemoveTagFromTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task from which the tag will be removed.", examples=['abc'])
    tag_name: str = Field(default=..., description="The name of the tag to remove from the task. Must match the tag name exactly as it exists in the Space.", examples=['name'])
class RemoveTagFromTaskRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if referencing the task by its custom task ID instead of the default ClickUp task ID. Must be used in conjunction with the team_id parameter.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team) required when custom_task_ids is set to true. Used to resolve the correct task when referencing by custom task ID.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class RemoveTagFromTaskRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, indicating the format of the payload being sent.", examples=['application/json'])
class RemoveTagFromTaskRequest(StrictModel):
    """Removes a specific tag from a task without deleting the tag from the Space. The tag remains available for use on other tasks within the Space."""
    path: RemoveTagFromTaskRequestPath
    query: RemoveTagFromTaskRequestQuery | None = None
    header: RemoveTagFromTaskRequestHeader

# Operation: list_tasks
class GetTasksRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric ID of the List whose tasks you want to retrieve. To find it, hover over the List in the Sidebar, click the ellipsis menu, select Copy link, and extract the number following '/li' in the URL.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetTasksRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="When true, includes archived tasks in the response. Archived tasks are excluded by default.", examples=[False])
    include_markdown_description: bool | None = Field(default=None, description="When true, task descriptions are returned in Markdown format instead of plain text.", examples=[True])
    page: int | None = Field(default=None, description="Zero-based page number for paginated results. Increment to retrieve subsequent pages of up to 100 tasks each.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    order_by: str | None = Field(default=None, description="Field by which to sort the returned tasks. Defaults to 'created' if not specified.")
    reverse: bool | None = Field(default=None, description="When true, reverses the sort order of the returned tasks.")
    subtasks: bool | None = Field(default=None, description="When true, subtasks are included in the response alongside top-level tasks. Subtasks are excluded by default.")
    statuses: list[str] | None = Field(default=None, description="Array of status names to filter tasks by. Only tasks matching one of the provided statuses are returned. To include closed tasks, also set include_closed to true.")
    include_closed: bool | None = Field(default=None, description="When true, closed tasks are included in the response. Closed tasks are excluded by default.")
    include_timl: bool | None = Field(default=None, description="When true, tasks that belong to multiple Lists (Tasks in Multiple Lists) are included in the response, even if their home List differs from the specified list_id. Excluded by default.")
    assignees: list[str] | None = Field(default=None, description="Array of assignee user IDs to filter tasks by. Only tasks assigned to at least one of the specified users are returned.")
    watchers: list[str] | None = Field(default=None, description="Array of watcher user IDs to filter tasks by. Only tasks watched by at least one of the specified users are returned.")
    tags: list[str] | None = Field(default=None, description="Array of tag names to filter tasks by. Only tasks that have at least one of the specified tags are returned.")
    due_date_gt: int | None = Field(default=None, description="Returns only tasks with a due date strictly after this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    due_date_lt: int | None = Field(default=None, description="Returns only tasks with a due date strictly before this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    date_created_gt: int | None = Field(default=None, description="Returns only tasks created strictly after this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    date_created_lt: int | None = Field(default=None, description="Returns only tasks created strictly before this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    date_updated_gt: int | None = Field(default=None, description="Returns only tasks last updated strictly after this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    date_updated_lt: int | None = Field(default=None, description="Returns only tasks last updated strictly before this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    date_done_gt: int | None = Field(default=None, description="Returns only tasks marked done strictly after this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    date_done_lt: int | None = Field(default=None, description="Returns only tasks marked done strictly before this Unix timestamp in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    custom_fields: list[str] | None = Field(default=None, description="Array of Custom Field filter objects for filtering tasks across multiple Custom Fields simultaneously. Each object must specify a field_id, an operator, and a value. Use custom_field instead when filtering on a single Custom Field.")
    custom_field: list[str] | None = Field(default=None, description="Array representing a single Custom Field filter, used when filtering tasks by exactly one Custom Field or Custom Relationship. Use custom_fields when filtering across multiple Custom Fields at once.")
    custom_items: list[float] | None = Field(default=None, description="Array of custom task type identifiers to filter by. Use 0 for standard tasks, 1 for Milestones, or any other workspace-defined custom task type ID.")
class GetTasksRequest(StrictModel):
    """Retrieve up to 100 tasks per page from a specified List, returning only tasks whose home List matches the given list_id by default. Use filtering, sorting, and pagination parameters to narrow results by status, assignee, tags, dates, custom fields, and more."""
    path: GetTasksRequestPath
    query: GetTasksRequestQuery | None = None

# Operation: create_task
class CreateTaskRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric ID of the list in which the task will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateTaskRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name of the task.")
    assignees: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] | None = Field(default=None, description="List of user IDs to assign to the task. Order is not significant.")
    archived: bool | None = Field(default=None, description="Whether the task should be created in an archived state.")
    group_assignees: list[str] | None = Field(default=None, description="List of user group IDs to assign to the task. Order is not significant.")
    tags: list[str] | None = Field(default=None, description="List of tag names to apply to the task. Order is not significant.")
    status: str | None = Field(default=None, description="The status to assign to the task. Must match an existing status name defined in the list.")
    priority: int | None = Field(default=None, description="The priority level for the task, where 1 is urgent, 2 is high, 3 is normal, and 4 is low.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    due_date: int | None = Field(default=None, description="The due date for the task as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    due_date_time: bool | None = Field(default=None, description="Set to true to include a specific time component with the due date, or false to treat it as a date-only value.")
    time_estimate: int | None = Field(default=None, description="The estimated time to complete the task, expressed in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    start_date: int | None = Field(default=None, description="The start date for the task as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    start_date_time: bool | None = Field(default=None, description="Set to true to include a specific time component with the start date, or false to treat it as a date-only value.")
    points: float | None = Field(default=None, description="The number of sprint points to assign to the task.")
    notify_all: bool | None = Field(default=None, description="When true, the task creator is also notified upon creation; all other assignees and watchers are always notified regardless of this setting.")
    parent: str | None = Field(default=None, description="The ID of an existing task to nest this new task under as a subtask. The parent task must reside in the same list specified in the path and may itself be a subtask.")
    markdown_content: str | None = Field(default=None, description="Markdown-formatted description for the task. Takes precedence over the plain-text description field if both are provided.")
    links_to: str | None = Field(default=None, description="The ID of an existing task to create a linked dependency relationship with the new task.")
    check_required_custom_fields: bool | None = Field(default=None, description="When true, enforces validation of any required Custom Fields on the task; by default required Custom Fields are ignored during API task creation.")
    custom_fields: list[CreateTaskBodyCustomFieldsItemV0 | CreateTaskBodyCustomFieldsItemV1 | CreateTaskBodyCustomFieldsItemV2 | CreateTaskBodyCustomFieldsItemV3 | CreateTaskBodyCustomFieldsItemV4 | CreateTaskBodyCustomFieldsItemV5 | CreateTaskBodyCustomFieldsItemV6 | CreateTaskBodyCustomFieldsItemV7 | CreateTaskBodyCustomFieldsItemV8 | CreateTaskBodyCustomFieldsItemV9 | CreateTaskBodyCustomFieldsItemV10 | CreateTaskBodyCustomFieldsItemV11 | CreateTaskBodyCustomFieldsItemV12 | CreateTaskBodyCustomFieldsItemV13 | CreateTaskBodyCustomFieldsItemV14] | None = Field(default=None, description="List of Custom Field objects to populate on the new task, each specifying a field ID and its value. Object and array type fields can be cleared by passing a null value.")
    custom_item_id: float | None = Field(default=None, description="The custom task type ID to apply to this task. Omit or pass null to create a standard task; retrieve available custom type IDs using the Get Custom Task Types endpoint.")
class CreateTaskRequest(StrictModel):
    """Creates a new task in the specified list, supporting full configuration including assignees, scheduling, custom fields, subtask relationships, and sprint points."""
    path: CreateTaskRequestPath
    body: CreateTaskRequestBody

# Operation: get_task
class GetTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to retrieve. When using custom task IDs, set custom_task_ids to true and provide the team_id.", examples=['9hz'])
class GetTaskRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID. Must be used together with the team_id parameter.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when custom_task_ids is set to true. Identifies which Workspace the custom task ID belongs to.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    include_subtasks: bool | None = Field(default=None, description="Set to true to include all subtasks nested under the task in the response. Defaults to false.")
    include_markdown_description: bool | None = Field(default=None, description="Set to true to return the task description formatted in Markdown instead of plain text.", examples=[True])
    custom_fields: list[str] | None = Field(default=None, description="Filter or include tasks matching specific Custom Field values using a JSON array of field conditions. Each condition specifies a field_id, a comparison operator, and a value. Supports Custom Relationships.")
class GetTaskRequest(StrictModel):
    """Retrieve detailed information about a specific task, including its fields, assignees, status, and attachments. Docs attached to the task are not returned."""
    path: GetTaskRequestPath
    query: GetTaskRequestQuery | None = None

# Operation: update_task
class UpdateTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to update.", examples=['9hx'])
class UpdateTaskRequestBodyAssignees(StrictModel):
    add: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., validation_alias="add", serialization_alias="add", description="List of user IDs to add as assignees to the task. Order is not significant.")
    rem: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., validation_alias="rem", serialization_alias="rem", description="List of user IDs to remove from the task's assignees. Order is not significant.")
class UpdateTaskRequestBodyGroupAssignees(StrictModel):
    add: list[str] | None = Field(default=None, validation_alias="add", serialization_alias="add", description="List of group (team) IDs to add as group assignees to the task. Order is not significant.")
    rem: list[str] | None = Field(default=None, validation_alias="rem", serialization_alias="rem", description="List of group (team) IDs to remove from the task's group assignees. Order is not significant.")
class UpdateTaskRequestBodyWatchers(StrictModel):
    add: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., validation_alias="add", serialization_alias="add", description="List of user IDs to add as watchers on the task. Order is not significant.")
    rem: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., validation_alias="rem", serialization_alias="rem", description="List of user IDs to remove from the task's watchers. Order is not significant.")
class UpdateTaskRequestBody(StrictModel):
    """***Note:** To update Custom Fields on a task, you must use the Set Custom Field endpoint.*"""
    custom_item_id: float | None = Field(default=None, description="The custom task type ID to assign to this task. Set to null to use the default 'Task' type. Retrieve available custom task type IDs using the Get Custom Task Types endpoint.")
    name: str | None = Field(default=None, description="The display name of the task.")
    markdown_content: str | None = Field(default=None, description="Markdown-formatted description for the task. Takes precedence over the plain-text description field if both are provided.")
    status: str | None = Field(default=None, description="The status of the task. Must match a valid status name defined in the task's list.")
    priority: int | None = Field(default=None, description="The priority level of the task, where 1 is urgent, 2 is high, 3 is normal, and 4 is low.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    due_date: int | None = Field(default=None, description="The due date for the task as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    due_date_time: bool | None = Field(default=None, description="Set to true if the due date includes a specific time component, or false if it is a date-only value.")
    parent: str | None = Field(default=None, description="The task ID of the parent task to move this subtask under. Cannot be used to convert a subtask back into a top-level task by passing null.")
    time_estimate: int | None = Field(default=None, description="The estimated time to complete the task, in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    start_date: int | None = Field(default=None, description="The start date for the task as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    start_date_time: bool | None = Field(default=None, description="Set to true if the start date includes a specific time component, or false if it is a date-only value.")
    points: float | None = Field(default=None, description="The number of Sprint Points to assign to this task.")
    archived: bool | None = Field(default=None, description="Set to true to archive the task, or false to unarchive it.")
    assignees: UpdateTaskRequestBodyAssignees
    group_assignees: UpdateTaskRequestBodyGroupAssignees | None = None
    watchers: UpdateTaskRequestBodyWatchers
class UpdateTaskRequest(StrictModel):
    """Update one or more fields on an existing task by its task ID. Supports updating metadata, assignments, dates, status, priority, and more."""
    path: UpdateTaskRequestPath
    body: UpdateTaskRequestBody

# Operation: delete_task
class DeleteTaskRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to delete. Use the task's custom ID instead if the custom_task_ids parameter is set to true.", examples=['9xh'])
class DeleteTaskRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task using its custom task ID rather than the default system-generated task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team ID) required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the task.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class DeleteTaskRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, which must be set to indicate JSON-formatted content.", examples=['application/json'])
class DeleteTaskRequest(StrictModel):
    """Permanently deletes a task from your Workspace by its task ID. This action is irreversible and removes the task and its associated data."""
    path: DeleteTaskRequestPath
    query: DeleteTaskRequestQuery | None = None
    header: DeleteTaskRequestHeader

# Operation: list_tasks_by_team
class GetFilteredTeamTasksRequestPath(StrictModel):
    team_id: float = Field(default=..., validation_alias="team_Id", serialization_alias="team_Id", description="The unique numeric ID of the Workspace (team) from which to retrieve tasks.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetFilteredTeamTasksRequestQuery(StrictModel):
    page: int | None = Field(default=None, description="Zero-based page number for paginated results; begin with 0 for the first page and increment to retrieve subsequent pages.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    order_by: str | None = Field(default=None, description="Field by which to sort the returned tasks. Defaults to `created` if not specified. Accepted values are `id`, `created`, `updated`, and `due_date`.")
    reverse: bool | None = Field(default=None, description="When set to true, reverses the sort order of the results so that the most recent or highest-value items appear first.")
    subtasks: bool | None = Field(default=None, description="When set to true, includes subtasks in the response. Subtasks are excluded by default.")
    space_ids: list[str] | None = Field(default=None, validation_alias="space_ids[]", serialization_alias="space_ids[]", description="Array of Space IDs used to filter tasks to only those belonging to the specified Spaces. Multiple values are supported.")
    project_ids: list[str] | None = Field(default=None, validation_alias="project_ids[]", serialization_alias="project_ids[]", description="Array of Folder IDs (referred to as `project_ids` in the API) used to filter tasks to only those within the specified Folders. Multiple values are supported.")
    list_ids: list[str] | None = Field(default=None, validation_alias="list_ids[]", serialization_alias="list_ids[]", description="Array of List IDs used to filter tasks to only those belonging to the specified Lists. Multiple values are supported.")
    statuses: list[str] | None = Field(default=None, validation_alias="statuses[]", serialization_alias="statuses[]", description="Array of status names used to filter tasks by their current status. Use URL encoding for status names that contain spaces (e.g., a space character is represented as `%20`).")
    include_closed: bool | None = Field(default=None, description="When set to true, includes closed tasks in the response alongside open tasks. Closed tasks are excluded by default.")
    assignees: list[str] | None = Field(default=None, validation_alias="assignees[]", serialization_alias="assignees[]", description="Array of ClickUp user IDs used to filter tasks by assignee. Multiple assignee IDs can be provided to match tasks assigned to any of the specified users.")
    tags: list[str] | None = Field(default=None, validation_alias="tags[]", serialization_alias="tags[]", description="Array of tag names used to filter tasks that have all specified tags applied. Use URL encoding for tag names containing spaces (e.g., a space character is represented as `%20`).")
    due_date_gt: int | None = Field(default=None, description="Returns only tasks with a due date strictly after this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    due_date_lt: int | None = Field(default=None, description="Returns only tasks with a due date strictly before this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    date_created_gt: int | None = Field(default=None, description="Returns only tasks created strictly after this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    date_created_lt: int | None = Field(default=None, description="Returns only tasks created strictly before this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    date_updated_gt: int | None = Field(default=None, description="Returns only tasks last updated strictly after this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    date_updated_lt: int | None = Field(default=None, description="Returns only tasks last updated strictly before this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    date_done_gt: int | None = Field(default=None, description="Returns only tasks marked as done strictly after this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    date_done_lt: int | None = Field(default=None, description="Returns only tasks marked as done strictly before this value, expressed as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    parent: str | None = Field(default=None, description="The ID of a parent task; when provided, the response returns the subtasks belonging to that parent task rather than top-level tasks.")
    include_markdown_description: bool | None = Field(default=None, description="When set to true, task description fields in the response are returned in Markdown format instead of plain text.", examples=[True])
    custom_items: list[float] | None = Field(default=None, validation_alias="custom_items[]", serialization_alias="custom_items[]", description="Array of custom task type identifiers used to filter results. Use `0` for standard tasks, `1` for Milestones, or any other numeric ID corresponding to a custom task type defined in the Workspace.")
    custom_fields: str | None = Field(default=None, description="Include tasks with specific values in one or more Custom Fields. Custom Relationships are included.\\\n \\\nFor example: `?custom_fields=[{\"field_id\":\"abcdefghi12345678\",\"operator\":\"=\",\"value\":\"1234\"}{\"field_id\":\"jklmnop123456\",\"operator\":\"<\",\"value\":\"5\"}]`\\\n \\\nOnly set Custom Field values display in the `value` property of the `custom_fields` parameter. The `=` operator isn't supported with Label Custom Fields.\\\n \\\nLearn more about [filtering using Custom Fields.](doc:taskfilters)")
class GetFilteredTeamTasksRequest(StrictModel):
    """Retrieve tasks from a Workspace that match specified filter criteria such as status, assignee, due date, tags, and location (Space, Folder, or List). Results are paginated at 100 tasks per page and limited to tasks the authenticated user can access."""
    path: GetFilteredTeamTasksRequestPath
    query: GetFilteredTeamTasksRequestQuery | None = None

# Operation: merge_tasks
class MergeTasksRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique ID of the target task that all source tasks will be merged into. Must be a valid internal task ID; Custom Task IDs are not supported.", examples=['9hv'])
class MergeTasksRequestBody(StrictModel):
    source_task_ids: list[str] = Field(default=..., description="An array of IDs representing the source tasks to merge into the target task. Order is not significant; all listed tasks will be merged. Custom Task IDs are not supported.", examples=[['abc123', 'def456']])
class MergeTasksRequest(StrictModel):
    """Merges one or more source tasks into a specified target task, consolidating their content and history. Source tasks are provided in the request body, and Custom Task IDs are not supported."""
    path: MergeTasksRequestPath
    body: MergeTasksRequestBody

# Operation: get_task_time_in_status
class GetTaskSTimeinStatusRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task for which to retrieve time-in-status data.", examples=['9hz'])
class GetTaskSTimeinStatusRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID (team_id) required when using custom task IDs. Must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetTaskSTimeinStatusRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, used to indicate the format of the request body sent to the API.", examples=['application/json'])
class GetTaskSTimeinStatusRequest(StrictModel):
    """Retrieves how long a task has spent in each status, providing a breakdown of time per status stage. Requires the Total Time in Status ClickApp to be enabled by a Workspace owner or admin."""
    path: GetTaskSTimeinStatusRequestPath
    query: GetTaskSTimeinStatusRequestQuery | None = None
    header: GetTaskSTimeinStatusRequestHeader

# Operation: get_bulk_tasks_time_in_status
class GetBulkTasksTimeinStatusRequestQuery(StrictModel):
    task_ids: str = Field(default=..., description="One or more task IDs to query; include this parameter once per task ID, with a maximum of 100 task IDs per request.")
    custom_task_ids: bool | None = Field(default=None, description="Set to true if referencing tasks by their custom task IDs instead of default system IDs.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when custom_task_ids is set to true; must be provided alongside that parameter.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetBulkTasksTimeinStatusRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload sent to the API.", examples=['application/json'])
class GetBulkTasksTimeinStatusRequest(StrictModel):
    """Retrieves how long two or more tasks have spent in each status. Requires the Total Time in Status ClickApp to be enabled by a Workspace owner or admin."""
    query: GetBulkTasksTimeinStatusRequestQuery
    header: GetBulkTasksTimeinStatusRequestHeader

# Operation: list_task_templates
class GetTaskTemplatesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose task templates you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetTaskTemplatesRequestQuery(StrictModel):
    page: int = Field(default=..., description="The zero-based page number for paginating through task template results, where 0 returns the first page.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'}, examples=[0])
class GetTaskTemplatesRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type format for the request body, which must be set to indicate JSON content.", examples=['application/json'])
class GetTaskTemplatesRequest(StrictModel):
    """Retrieves a paginated list of task templates available in the specified Workspace, which can be used to standardize task creation across teams."""
    path: GetTaskTemplatesRequestPath
    query: GetTaskTemplatesRequestQuery
    header: GetTaskTemplatesRequestHeader

# Operation: list_templates
class GetListTemplatesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose List templates you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetListTemplatesRequestQuery(StrictModel):
    page: int = Field(default=..., description="Zero-indexed page number for paginating through template results; start at 0 for the first page.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'}, examples=[0])
class GetListTemplatesRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="MIME type for the request body, indicating the format of the data being sent.", examples=['application/json'])
class GetListTemplatesRequest(StrictModel):
    """Retrieves all List templates available in a Workspace, returning their IDs and metadata. Use the returned template IDs (prefixed with `t-`) to create Lists from templates in a Folder or Space."""
    path: GetListTemplatesRequestPath
    query: GetListTemplatesRequestQuery
    header: GetListTemplatesRequestHeader

# Operation: list_folder_templates
class GetFolderTemplatesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose Folder templates you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetFolderTemplatesRequestQuery(StrictModel):
    page: int = Field(default=..., description="Zero-indexed page number for paginating through Folder template results; start at 0 for the first page.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'}, examples=[0])
class GetFolderTemplatesRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body sent to the API.", examples=['application/json'])
class GetFolderTemplatesRequest(StrictModel):
    """Retrieves all Folder templates available in a Workspace, including their template IDs. Use the returned template IDs (prefixed with `t-`) with the Create Folder From Template endpoint to instantiate new Folders."""
    path: GetFolderTemplatesRequestPath
    query: GetFolderTemplatesRequestQuery
    header: GetFolderTemplatesRequestHeader

# Operation: create_task_from_template
class CreateTaskFromTemplateRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique numeric identifier of the list where the new task will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[512])
    template_id: str = Field(default=..., description="The unique string identifier of the task template to use when creating the task.", examples=['9hz'])
class CreateTaskFromTemplateRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name to assign to the newly created task.")
class CreateTaskFromTemplateRequest(StrictModel):
    """Create a new task in a specified list using a pre-defined task template from your workspace. Publicly shared templates must be added to your workspace library before they can be used via the API."""
    path: CreateTaskFromTemplateRequestPath
    body: CreateTaskFromTemplateRequestBody

# Operation: create_list_from_template_in_folder
class CreateFolderListFromTemplateRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The ID of the Folder in which the new List will be created.")
    template_id: str = Field(default=..., description="The ID of the List template to apply. Template IDs include a 't-' prefix. Retrieve available template IDs using the Get List Templates endpoint.", examples=['t-15363293'])
class CreateFolderListFromTemplateRequestBodyOptions(StrictModel):
    return_immediately: bool | None = Field(default=None, validation_alias="return_immediately", serialization_alias="return_immediately", description="When true (default), the new List's ID is returned immediately before all nested template objects are fully created. When false, the request waits until the List and all sub-objects are fully applied before responding.")
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="Optional description or body text for the new List.")
    time_estimate: float | None = Field(default=None, validation_alias="time_estimate", serialization_alias="time_estimate", description="Whether to import time estimate values (hours, minutes, and seconds) from the template's tasks.")
    automation: bool | None = Field(default=None, validation_alias="automation", serialization_alias="automation", description="Whether to import automation rules defined in the template.")
    include_views: bool | None = Field(default=None, validation_alias="include_views", serialization_alias="include_views", description="Whether to import view configurations (e.g., Board, Calendar) from the template.")
    old_due_date: bool | None = Field(default=None, validation_alias="old_due_date", serialization_alias="old_due_date", description="Whether to import the original due dates from the template's tasks.")
    old_start_date: bool | None = Field(default=None, validation_alias="old_start_date", serialization_alias="old_start_date", description="Whether to import the original start dates from the template's tasks.")
    old_followers: bool | None = Field(default=None, validation_alias="old_followers", serialization_alias="old_followers", description="Whether to import the watcher (follower) assignments from the template's tasks.")
    comment_attachments: bool | None = Field(default=None, validation_alias="comment_attachments", serialization_alias="comment_attachments", description="Whether to import file attachments that are embedded in task comments from the template.")
    recur_settings: bool | None = Field(default=None, validation_alias="recur_settings", serialization_alias="recur_settings", description="Whether to import recurring task settings from the template's tasks.")
    old_tags: bool | None = Field(default=None, validation_alias="old_tags", serialization_alias="old_tags", description="Whether to import tags from the template's tasks.")
    old_statuses: bool | None = Field(default=None, validation_alias="old_statuses", serialization_alias="old_statuses", description="Whether to import the status configuration (status columns/workflow) from the template.")
    subtasks: bool | None = Field(default=None, validation_alias="subtasks", serialization_alias="subtasks", description="Whether to import subtasks from the template's tasks.")
    custom_type: bool | None = Field(default=None, validation_alias="custom_type", serialization_alias="custom_type", description="Whether to import custom task type definitions from the template's tasks.")
    old_assignees: bool | None = Field(default=None, validation_alias="old_assignees", serialization_alias="old_assignees", description="Whether to import assignee assignments from the template's tasks.")
    attachments: bool | None = Field(default=None, validation_alias="attachments", serialization_alias="attachments", description="Whether to import file attachments from the template's tasks.")
    comment: bool | None = Field(default=None, validation_alias="comment", serialization_alias="comment", description="Whether to import comments from the template's tasks.")
    old_status: bool | None = Field(default=None, validation_alias="old_status", serialization_alias="old_status", description="Whether to import the current status values set on the template's tasks.")
    external_dependencies: bool | None = Field(default=None, validation_alias="external_dependencies", serialization_alias="external_dependencies", description="Whether to import external dependency links from the template's tasks.")
    internal_dependencies: bool | None = Field(default=None, validation_alias="internal_dependencies", serialization_alias="internal_dependencies", description="Whether to import internal dependency links between tasks from the template.")
    priority: bool | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="Whether to import priority levels from the template's tasks.")
    custom_fields: bool | None = Field(default=None, validation_alias="custom_fields", serialization_alias="custom_fields", description="Whether to import Custom Field definitions and values from the template's tasks.")
    old_checklists: bool | None = Field(default=None, validation_alias="old_checklists", serialization_alias="old_checklists", description="Whether to import checklist items from the template's tasks.")
    relationships: bool | None = Field(default=None, validation_alias="relationships", serialization_alias="relationships", description="Whether to import task relationship links (e.g., blocked by, related to) from the template.")
    old_subtask_assignees: bool | None = Field(default=None, validation_alias="old_subtask_assignees", serialization_alias="old_subtask_assignees", description="Whether to import assignees on subtasks from the template's tasks.")
    start_date: str | None = Field(default=None, validation_alias="start_date", serialization_alias="start_date", description="The project start date used as the anchor when remapping task dates from the template. Must be an ISO 8601 date-time string.", json_schema_extra={'format': 'date-time'})
    due_date: str | None = Field(default=None, validation_alias="due_date", serialization_alias="due_date", description="The project due date used as the anchor when remapping task dates from the template. Must be an ISO 8601 date-time string.", json_schema_extra={'format': 'date-time'})
    remap_start_date: bool | None = Field(default=None, validation_alias="remap_start_date", serialization_alias="remap_start_date", description="Whether to remap task start dates relative to the new project start date provided in 'start_date'.")
    skip_weekends: bool | None = Field(default=None, validation_alias="skip_weekends", serialization_alias="skip_weekends", description="Whether to skip weekend days (Saturday and Sunday) when calculating remapped task dates.")
    archived: Literal[1, 2] | None = Field(default=None, validation_alias="archived", serialization_alias="archived", description="Controls inclusion of archived tasks from the template: 1 includes archived tasks, 2 excludes them. Omit to use the default behavior.")
class CreateFolderListFromTemplateRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name to assign to the newly created List.")
    options: CreateFolderListFromTemplateRequestBodyOptions | None = None
class CreateFolderListFromTemplateRequest(StrictModel):
    """Create a new List inside a specified Folder using an existing List template, optionally controlling which task properties (assignees, due dates, custom fields, etc.) are imported from the template. By default the request returns immediately with the future List ID, though the List and its nested objects may still be generating in the background."""
    path: CreateFolderListFromTemplateRequestPath
    body: CreateFolderListFromTemplateRequestBody

# Operation: create_list_from_template
class CreateSpaceListFromTemplateRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Space where the new List will be created.")
    template_id: str = Field(default=..., description="The unique identifier of the List template to apply, always prefixed with `t-`. Retrieve available template IDs using the Get List Templates endpoint.", examples=['t-15363293'])
class CreateSpaceListFromTemplateRequestBodyOptions(StrictModel):
    return_immediately: bool | None = Field(default=None, validation_alias="return_immediately", serialization_alias="return_immediately", description="When true, returns the new object ID immediately after access checks without waiting for all nested assets to finish being created. When false, the request waits until the List and all its contents are fully created before responding.")
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="Optional description or body text for the new List.")
    time_estimate: float | None = Field(default=None, validation_alias="time_estimate", serialization_alias="time_estimate", description="Whether to import time estimate values (hours, minutes, and seconds) from the template's tasks.")
    automation: bool | None = Field(default=None, validation_alias="automation", serialization_alias="automation", description="Whether to import automation rules defined in the template.")
    include_views: bool | None = Field(default=None, validation_alias="include_views", serialization_alias="include_views", description="Whether to import views configured in the template.")
    old_due_date: bool | None = Field(default=None, validation_alias="old_due_date", serialization_alias="old_due_date", description="Whether to import due dates from the template's tasks.")
    old_start_date: bool | None = Field(default=None, validation_alias="old_start_date", serialization_alias="old_start_date", description="Whether to import start dates from the template's tasks.")
    old_followers: bool | None = Field(default=None, validation_alias="old_followers", serialization_alias="old_followers", description="Whether to import watchers (followers) from the template's tasks.")
    comment_attachments: bool | None = Field(default=None, validation_alias="comment_attachments", serialization_alias="comment_attachments", description="Whether to import comment attachments from the template's tasks.")
    recur_settings: bool | None = Field(default=None, validation_alias="recur_settings", serialization_alias="recur_settings", description="Whether to import recurring task settings from the template's tasks.")
    old_tags: bool | None = Field(default=None, validation_alias="old_tags", serialization_alias="old_tags", description="Whether to import tags from the template's tasks.")
    old_statuses: bool | None = Field(default=None, validation_alias="old_statuses", serialization_alias="old_statuses", description="Whether to import status configuration settings from the template's tasks.")
    subtasks: bool | None = Field(default=None, validation_alias="subtasks", serialization_alias="subtasks", description="Whether to import subtasks from the template's tasks.")
    custom_type: bool | None = Field(default=None, validation_alias="custom_type", serialization_alias="custom_type", description="Whether to import custom task type definitions from the template's tasks.")
    old_assignees: bool | None = Field(default=None, validation_alias="old_assignees", serialization_alias="old_assignees", description="Whether to import assignees from the template's tasks.")
    attachments: bool | None = Field(default=None, validation_alias="attachments", serialization_alias="attachments", description="Whether to import file attachments from the template's tasks.")
    comment: bool | None = Field(default=None, validation_alias="comment", serialization_alias="comment", description="Whether to import comments from the template's tasks.")
    old_status: bool | None = Field(default=None, validation_alias="old_status", serialization_alias="old_status", description="Whether to import the current status values of the template's tasks.")
    external_dependencies: bool | None = Field(default=None, validation_alias="external_dependencies", serialization_alias="external_dependencies", description="Whether to import external task dependencies from the template's tasks.")
    internal_dependencies: bool | None = Field(default=None, validation_alias="internal_dependencies", serialization_alias="internal_dependencies", description="Whether to import internal task dependencies from the template's tasks.")
    priority: bool | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="Whether to import priority settings from the template's tasks.")
    custom_fields: bool | None = Field(default=None, validation_alias="custom_fields", serialization_alias="custom_fields", description="Whether to import Custom Field definitions and values from the template's tasks.")
    old_checklists: bool | None = Field(default=None, validation_alias="old_checklists", serialization_alias="old_checklists", description="Whether to import checklists from the template's tasks.")
    relationships: bool | None = Field(default=None, validation_alias="relationships", serialization_alias="relationships", description="Whether to import task relationship links from the template's tasks.")
    old_subtask_assignees: bool | None = Field(default=None, validation_alias="old_subtask_assignees", serialization_alias="old_subtask_assignees", description="Whether to import assignees on subtasks from the template's tasks.")
    start_date: str | None = Field(default=None, validation_alias="start_date", serialization_alias="start_date", description="The project start date used as the anchor point when remapping task dates, provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    due_date: str | None = Field(default=None, validation_alias="due_date", serialization_alias="due_date", description="The project due date used as the anchor point when remapping task dates, provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    remap_start_date: bool | None = Field(default=None, validation_alias="remap_start_date", serialization_alias="remap_start_date", description="Whether to remap task start dates relative to the new project start date.")
    skip_weekends: bool | None = Field(default=None, validation_alias="skip_weekends", serialization_alias="skip_weekends", description="Whether to skip weekend days when calculating remapped task dates.")
    archived: Literal[1, 2] | None = Field(default=None, validation_alias="archived", serialization_alias="archived", description="Controls inclusion of archived tasks: use 1 to include archived tasks, 2 to include only archived tasks, or omit for no archived tasks.")
class CreateSpaceListFromTemplateRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name to assign to the newly created List.")
    options: CreateSpaceListFromTemplateRequestBodyOptions | None = None
class CreateSpaceListFromTemplateRequest(StrictModel):
    """Create a new List within a Space using an existing List template, importing selected task properties such as assignees, due dates, custom fields, and more. Supports both synchronous and asynchronous creation via the `return_immediately` parameter."""
    path: CreateSpaceListFromTemplateRequestPath
    body: CreateSpaceListFromTemplateRequestBody

# Operation: get_workspace_seats
class GetWorkspaceseatsRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the Workspace whose seat information you want to retrieve.")
class GetWorkspaceseatsRequest(StrictModel):
    """Retrieves seat usage information for a Workspace, including the number of used, total, and available seats for both members and guests."""
    path: GetWorkspaceseatsRequestPath

# Operation: get_workspace_plan
class GetWorkspaceplanRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the Workspace whose plan information you want to retrieve.")
class GetWorkspaceplanRequest(StrictModel):
    """Retrieves the current subscription plan details for the specified Workspace, including plan tier and associated features."""
    path: GetWorkspaceplanRequestPath

# Operation: create_user_group
class CreateUserGroupRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace (referred to as team_id in the API) where the User Group will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateUserGroupRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new User Group, used to identify it within the Workspace.")
    handle: str | None = Field(default=None, description="An optional short identifier or alias for the User Group, typically used as a reference handle within the Workspace.")
    members: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., description="A list of user objects to include as members of the new User Group; order is not significant and each item should represent a user to be added.")
class CreateUserGroupRequest(StrictModel):
    """Creates a User Group within a Workspace to organize and manage users collectively. Note that adding a guest with view-only permissions automatically converts them to a paid guest, which may incur prorated charges if additional seats are needed."""
    path: CreateUserGroupRequestPath
    body: CreateUserGroupRequestBody

# Operation: list_custom_task_types
class GetCustomItemsRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose custom task types you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetCustomItemsRequest(StrictModel):
    """Retrieves all custom task types defined in a Workspace, allowing you to see available task type options for organizing and categorizing work."""
    path: GetCustomItemsRequestPath

# Operation: update_user_group
class UpdateTeamRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the User Group to update.", examples=['C9C58BE9'])
class UpdateTeamRequestBodyMembers(StrictModel):
    add: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., validation_alias="add", serialization_alias="add", description="List of user IDs to add to the User Group. Each item should be a valid user ID string.")
    rem: list[Annotated[int, Field(json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})]] = Field(default=..., validation_alias="rem", serialization_alias="rem", description="List of user IDs to remove from the User Group. Each item should be a valid user ID string.")
class UpdateTeamRequestBody(StrictModel):
    """The group handle can be updated, which is used to @mention a User Group within the Workspace.\\
 \\
Modify Group members by using the "add" and "rem" parameters with an array of user IDs to include or exclude members."""
    name: str | None = Field(default=None, description="The new display name for the User Group.")
    handle: str | None = Field(default=None, description="The new handle (short identifier or alias) for the User Group.")
    members: UpdateTeamRequestBodyMembers
class UpdateTeamRequest(StrictModel):
    """Updates a User Group's name, handle, or membership within a Workspace. Note that adding a guest with view-only permissions automatically converts them to a paid guest, which may incur prorated billing charges."""
    path: UpdateTeamRequestPath
    body: UpdateTeamRequestBody

# Operation: delete_user_group
class DeleteTeamRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the user group to delete from the Workspace.", examples=['C9C58BE9'])
class DeleteTeamRequest(StrictModel):
    """Permanently removes a user group from the Workspace. Note that in the API, 'group_id' refers to a user group, while 'team_id' refers to the Workspace."""
    path: DeleteTeamRequestPath

# Operation: list_user_groups
class GetTeams1RequestQuery(StrictModel):
    team_id: float = Field(default=..., description="The unique ID of the Workspace whose User Groups you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    group_ids: list[str] | None = Field(default=None, description="An optional list of User Group IDs to filter results to specific groups; omit to return all User Groups in the Workspace. Each item should be a valid User Group ID string. Order is not significant.", examples=['C9C58BE9-7C73-4002-A6A9-123456789123', 'F3B51AE4-6F25-1783-D2C1-987654321321'])
class GetTeams1Request(StrictModel):
    """Retrieves User Groups within a specified Workspace, optionally filtered to one or more specific groups. Note: in the API, 'team_id' refers to the Workspace ID and 'group_id' refers to a User Group ID."""
    query: GetTeams1RequestQuery

# Operation: get_task_tracked_time
class GettrackedtimeRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task whose tracked time entries you want to retrieve.", examples=['9hv'])
class GettrackedtimeRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if referencing the task by its custom task ID instead of the default ClickUp task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs; must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GettrackedtimeRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, indicating the format of the data being sent.", examples=['application/json'])
class GettrackedtimeRequest(StrictModel):
    """Retrieves all tracked time entries associated with a specific task. Note: This is a legacy endpoint; the Time Tracking API is recommended for managing time entries."""
    path: GettrackedtimeRequestPath
    query: GettrackedtimeRequestQuery | None = None
    header: GettrackedtimeRequestHeader

# Operation: track_task_time
class TracktimeRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to log time against.", examples=['9hv'])
class TracktimeRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if referencing the task by its custom task ID rather than the default system-generated ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class TracktimeRequestBody(StrictModel):
    """Include the total time or the start time and end time.\\
 \\
The total time is in milliseconds and `"start"` and `"end"` values are Unix time in milliseconds."""
    start: int = Field(default=..., description="The start time of the tracked time entry as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    end: int = Field(default=..., description="The end time of the tracked time entry as a Unix timestamp in milliseconds. Must be greater than the start value.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    time_: int = Field(default=..., validation_alias="time", serialization_alias="time", description="The total duration of the time entry in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class TracktimeRequest(StrictModel):
    """Records a time entry against a specific task using the legacy time tracking endpoint. For new integrations, the dedicated Time Tracking API endpoints are recommended instead."""
    path: TracktimeRequestPath
    query: TracktimeRequestQuery | None = None
    body: TracktimeRequestBody

# Operation: update_time_entry_legacy
class EdittimetrackedRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task containing the time interval to update.", examples=['9hv'])
    interval_id: str = Field(default=..., description="The unique identifier of the specific time interval to edit.", examples=['123'])
class EdittimetrackedRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of its default system ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class EdittimetrackedRequestBody(StrictModel):
    """Edit the start, end, or total time of a time tracked entry."""
    start: int = Field(default=..., description="The start time of the tracked interval as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    end: int = Field(default=..., description="The end time of the tracked interval as a Unix timestamp in milliseconds. Must be greater than the start value.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    time_: int = Field(default=..., validation_alias="time", serialization_alias="time", description="The total duration of the tracked time interval in milliseconds.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class EdittimetrackedRequest(StrictModel):
    """Updates an existing tracked time interval on a task by modifying its start time, end time, or duration. Note: This is a legacy endpoint; the Time Tracking API is recommended for managing time entries."""
    path: EdittimetrackedRequestPath
    query: EdittimetrackedRequestQuery | None = None
    body: EdittimetrackedRequestBody

# Operation: delete_tracked_time_interval
class DeletetimetrackedRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task from which the tracked time interval will be deleted.", examples=['9hv'])
    interval_id: str = Field(default=..., description="The unique identifier of the tracked time interval to delete.", examples=['123'])
class DeletetimetrackedRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the task by its custom task ID instead of the default ClickUp task ID.", examples=[True])
    team_id: float | None = Field(default=None, description="The Workspace ID required when referencing a task by its custom task ID; must be provided alongside custom_task_ids=true.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class DeletetimetrackedRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The MIME type of the request body, indicating the format of the data being sent.", examples=['application/json'])
class DeletetimetrackedRequest(StrictModel):
    """Deletes a specific tracked time interval from a task using its interval ID. Note: This is a legacy endpoint; the Time Tracking API is recommended for managing time entries."""
    path: DeletetimetrackedRequestPath
    query: DeletetimetrackedRequestQuery | None = None
    header: DeletetimetrackedRequestHeader

# Operation: list_time_entries
class GettimeentrieswithinadaterangeRequestPath(StrictModel):
    team_id: float = Field(default=..., validation_alias="team_Id", serialization_alias="team_Id", description="The unique identifier of the workspace from which to retrieve time entries.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GettimeentrieswithinadaterangeRequestQuery(StrictModel):
    start_date: float | None = Field(default=None, description="The beginning of the date range filter expressed as a Unix timestamp in milliseconds. Defaults to 30 days before the current time if omitted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
    end_date: float | None = Field(default=None, description="The end of the date range filter expressed as a Unix timestamp in milliseconds. Defaults to the current time if omitted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
    assignee: float | None = Field(default=None, description="Filter results to one or more specific users by their user IDs, supplied as a comma-separated list. Only Workspace Owners and Admins may retrieve entries for users other than themselves.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
    include_task_tags: bool | None = Field(default=None, description="When set to true, includes any tags associated with the task linked to each time entry in the response.")
    include_location_names: bool | None = Field(default=None, description="When set to true, enriches each time entry with the human-readable names of its associated List, Folder, and Space alongside their respective IDs.")
    include_approval_history: bool | None = Field(default=None, description="When set to true, includes the full approval history for each time entry, including status changes, reviewer notes, and approver details.")
    include_approval_details: bool | None = Field(default=None, description="When set to true, includes current approval details for each time entry such as the approver ID, approval timestamp, list of approvers, and current approval status.")
    space_id: float | None = Field(default=None, description="Restricts results to time entries linked to tasks within the specified Space. Cannot be combined with folder_id, list_id, or task_id.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
    folder_id: float | None = Field(default=None, description="Restricts results to time entries linked to tasks within the specified Folder. Cannot be combined with space_id, list_id, or task_id.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
    list_id: float | None = Field(default=None, description="Restricts results to time entries linked to tasks within the specified List. Cannot be combined with space_id, folder_id, or task_id.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
    task_id: str | None = Field(default=None, description="Restricts results to time entries linked to a single specific task. Cannot be combined with space_id, folder_id, or list_id.")
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the target task using its custom task ID instead of its standard ClickUp task ID. Must be used together with the team_id parameter.", examples=[True])
    team_id2: float | None = Field(default=None, description="The workspace ID required when custom_task_ids is set to true, used to resolve the custom task ID to the correct task within the workspace.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    is_billable: bool | None = Field(default=None, description="Filters results by billing status: set to true to return only billable time entries, or false to return only non-billable time entries. Omit to return all entries regardless of billing status.", examples=[True])
class GettimeentrieswithinadaterangeRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, which must be set to indicate JSON content.", examples=['application/json'])
class GettimeentrieswithinadaterangeRequest(StrictModel):
    """Retrieve time entries for a workspace filtered by a date range, location, assignee, and billing status. Defaults to the last 30 days for the authenticated user; only one location filter (space, folder, list, or task) may be applied at a time."""
    path: GettimeentrieswithinadaterangeRequestPath
    query: GettimeentrieswithinadaterangeRequestQuery | None = None
    header: GettimeentrieswithinadaterangeRequestHeader

# Operation: create_time_entry
class CreateatimeentryRequestPath(StrictModel):
    team_id: float = Field(default=..., validation_alias="team_Id", serialization_alias="team_Id", description="The unique identifier of the workspace where the time entry will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateatimeentryRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the associated task by its custom task ID instead of its standard ClickUp task ID.", examples=[True])
    team_id2: float | None = Field(default=None, description="The workspace ID required when using custom task IDs. Must be provided alongside custom_task_ids=true to correctly resolve the custom task reference.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateatimeentryRequestBody(StrictModel):
    """Associate a time entry with a task using the `tid` parameter."""
    description: str | None = Field(default=None, description="An optional text description or note to associate with the time entry.")
    tags: list[CreateatimeentryBodyTagsItem] | None = Field(default=None, description="A list of time tracking label objects to attach to the entry. Available to users on the Business Plan and above; each item should represent a valid time tracking tag.")
    start: int = Field(default=..., description="The start time of the time entry as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    stop: int | None = Field(default=None, description="The end time of the time entry as a Unix timestamp in milliseconds. Can be used instead of the duration parameter; if both stop and start are provided, duration is ignored.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    billable: bool | None = Field(default=None, description="Marks the time entry as billable when set to true.")
    duration: int = Field(default=..., description="The duration of the time entry in milliseconds. Used as an alternative to the stop parameter; ignored when both start and stop values are present. A negative value indicates a currently running timer.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    assignee: int | None = Field(default=None, description="The user ID to assign the time entry to. Workspace owners and admins may specify any user ID; members may only specify their own user ID.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    tid: str | None = Field(default=None, description="The ID of the task to associate with this time entry.")
class CreateatimeentryRequest(StrictModel):
    """Creates a time entry for a user in the specified workspace, supporting both completed entries (with start and stop/duration) and actively running timers. A negative duration indicates a timer is currently running for that user."""
    path: CreateatimeentryRequestPath
    query: CreateatimeentryRequestQuery | None = None
    body: CreateatimeentryRequestBody

# Operation: get_time_entry
class GetsingulartimeentryRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique numeric ID of the workspace containing the time entry.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    timer_id: str = Field(default=..., description="The unique ID of the time entry to retrieve. Time entry IDs can be obtained from the Get Time Entries Within a Date Range endpoint.", examples=['1963465985517105840'])
class GetsingulartimeentryRequestQuery(StrictModel):
    include_task_tags: bool | None = Field(default=None, description="When true, includes any task tags associated with the time entry in the response.")
    include_location_names: bool | None = Field(default=None, description="When true, includes the human-readable names of the List, Folder, and Space alongside their respective IDs in the response.")
    include_approval_history: bool | None = Field(default=None, description="When true, includes the full approval history for the time entry, showing past approval state changes.")
    include_approval_details: bool | None = Field(default=None, description="When true, includes detailed information about the current approval state and approver for the time entry.")
class GetsingulartimeentryRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, indicating the format of the payload being sent.", examples=['application/json'])
class GetsingulartimeentryRequest(StrictModel):
    """Retrieves a single time entry by its ID within a workspace. Note that a time entry with a negative duration indicates the timer is currently running for that user."""
    path: GetsingulartimeentryRequestPath
    query: GetsingulartimeentryRequestQuery | None = None
    header: GetsingulartimeentryRequestHeader

# Operation: update_time_entry
class UpdateatimeEntryRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace containing the time entry.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    timer_id: float = Field(default=..., description="The unique identifier of the time entry to update.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[2004673344540003600])
class UpdateatimeEntryRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true to reference the associated task by its custom task ID instead of its default ClickUp task ID.", examples=[True])
class UpdateatimeEntryRequestBody(StrictModel):
    """Accessible tag actions are `["replace", "add", "remove"]`"""
    description: str | None = Field(default=None, description="A text description or note to associate with the time entry.")
    tags: list[UpdateatimeEntryBodyTagsItem] = Field(default=..., description="A list of time tracking label objects to apply to the time entry. Available on Business Plan and above. Order is not significant; each item should be a valid tag object.")
    tag_action: str | None = Field(default=None, description="Specifies how the provided tags should be applied — for example, whether to replace existing tags or add to them.")
    start: int | None = Field(default=None, description="The start time of the time entry as a Unix timestamp in milliseconds. Must be provided together with the end parameter.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    end: int | None = Field(default=None, description="The end time of the time entry as a Unix timestamp in milliseconds. Must be provided together with the start parameter.", json_schema_extra={'format': 'int64', 'contentEncoding': 'int64'})
    tid: str = Field(default=..., description="The unique identifier of the task to associate with this time entry.")
    billable: bool | None = Field(default=None, description="Indicates whether the time entry should be marked as billable.")
    duration: int | None = Field(default=None, description="The duration of the time entry in milliseconds. Use this to set a fixed duration rather than deriving it from start and end times.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class UpdateatimeEntryRequest(StrictModel):
    """Update the details of an existing time entry in a workspace, including its description, tags, start/end times, duration, and billable status."""
    path: UpdateatimeEntryRequestPath
    query: UpdateatimeEntryRequestQuery | None = None
    body: UpdateatimeEntryRequestBody

# Operation: delete_time_entry
class DeleteatimeEntryRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace from which the time entries will be deleted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    timer_id: float = Field(default=..., description="The unique identifier of the time entry to delete. To delete multiple entries at once, provide a comma-separated list of timer IDs.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
class DeleteatimeEntryRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, indicating the format in which the data is being sent.", examples=['application/json'])
class DeleteatimeEntryRequest(StrictModel):
    """Permanently deletes one or more time entries from a specified Workspace. Multiple time entries can be removed in a single request by providing a comma-separated list of timer IDs."""
    path: DeleteatimeEntryRequestPath
    header: DeleteatimeEntryRequestHeader

# Operation: get_time_entry_history
class GettimeentryhistoryRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique numeric ID of the workspace containing the time entry.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    timer_id: str = Field(default=..., description="The unique ID of the time entry whose history you want to retrieve. Can be obtained from the Get Time Entries Within a Date Range endpoint.", examples=['1963465985517105840'])
class GettimeentryhistoryRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, indicating the format of the data being sent.", examples=['application/json'])
class GettimeentryhistoryRequest(StrictModel):
    """Retrieves the change history for a specific time entry, showing a chronological list of modifications made to it."""
    path: GettimeentryhistoryRequestPath
    header: GettimeentryhistoryRequestHeader

# Operation: get_running_time_entry
class GetrunningtimeentryRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace in which to look up the running time entry.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetrunningtimeentryRequestQuery(StrictModel):
    assignee: float | None = Field(default=None, description="The user ID of a specific team member whose running time entry should be retrieved; defaults to the authenticated user if omitted.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'})
class GetrunningtimeentryRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, indicating the format in which data is being sent to the API.", examples=['application/json'])
class GetrunningtimeentryRequest(StrictModel):
    """Retrieves the currently active (running) time entry for the authenticated user in the specified workspace. A time entry with a negative duration indicates the timer is actively tracking time."""
    path: GetrunningtimeentryRequestPath
    query: GetrunningtimeentryRequestQuery | None = None
    header: GetrunningtimeentryRequestHeader

# Operation: list_time_entry_tags
class GetalltagsfromtimeentriesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose time entry tags you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetalltagsfromtimeentriesRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request payload, indicating the format in which data is being sent to the server.", examples=['application/json'])
class GetalltagsfromtimeentriesRequest(StrictModel):
    """Retrieves all labels (tags) that have been applied to time entries within a specified Workspace. Useful for auditing or filtering time entry categorization across a team."""
    path: GetalltagsfromtimeentriesRequestPath
    header: GetalltagsfromtimeentriesRequestHeader

# Operation: add_tags_to_time_entries
class AddtagsfromtimeentriesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace containing the time entries.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class AddtagsfromtimeentriesRequestBody(StrictModel):
    time_entry_ids: list[str] = Field(default=..., description="List of time entry IDs to which the tags will be applied. Order is not significant; each ID should be a valid time entry identifier within the workspace.")
    tags: list[AddtagsfromtimeentriesBodyTagsItem] = Field(default=..., description="List of tag names to attach to the specified time entries. Order is not significant; each item should be a tag name string.")
class AddtagsfromtimeentriesRequest(StrictModel):
    """Add one or more tags to a set of time entries in a workspace. Useful for bulk-labeling time entries for categorization or reporting purposes."""
    path: AddtagsfromtimeentriesRequestPath
    body: AddtagsfromtimeentriesRequestBody

# Operation: rename_time_entry_tag
class ChangetagnamesfromtimeentriesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace containing the time entry tags to update.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class ChangetagnamesfromtimeentriesRequestBody(StrictModel):
    name: str = Field(default=..., description="The current name of the tag to be renamed.")
    new_name: str = Field(default=..., description="The new name to assign to the tag, replacing the current name across all associated time entries.")
    tag_bg: str = Field(default=..., description="The background color for the tag, specified as a hex color code.")
    tag_fg: str = Field(default=..., description="The foreground (text) color for the tag, specified as a hex color code.")
class ChangetagnamesfromtimeentriesRequest(StrictModel):
    """Rename an existing time entry tag within a workspace, updating its display name and color styling. All time entries using the old tag name will reflect the updated tag."""
    path: ChangetagnamesfromtimeentriesRequestPath
    body: ChangetagnamesfromtimeentriesRequestBody

# Operation: remove_tags_from_time_entries
class RemovetagsfromtimeentriesRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace containing the time entries.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class RemovetagsfromtimeentriesRequestBody(StrictModel):
    time_entry_ids: list[str] = Field(default=..., description="List of time entry IDs from which the specified tags will be removed. Order is not significant.")
    tags: list[RemovetagsfromtimeentriesBodyTagsItem] = Field(default=..., description="List of tag objects to remove from the specified time entries. Order is not significant; each item should represent a valid tag associated with the workspace.")
class RemovetagsfromtimeentriesRequest(StrictModel):
    """Remove one or more tags from specified time entries in a workspace. This disassociates the labels from the time entries without deleting the tags from the workspace."""
    path: RemovetagsfromtimeentriesRequestPath
    body: RemovetagsfromtimeentriesRequestBody

# Operation: start_time_entry
class StartatimeEntryRequestPath(StrictModel):
    team_id: float = Field(default=..., validation_alias="team_Id", serialization_alias="team_Id", description="The unique identifier of the workspace in which to start the time entry.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class StartatimeEntryRequestQuery(StrictModel):
    custom_task_ids: bool | None = Field(default=None, description="Set to true if the task is being referenced by its custom task ID rather than its default system-generated ID.", examples=[True])
class StartatimeEntryRequestBody(StrictModel):
    """For Workspaces on the Free Forever or Unlimited Plan, either the `timer_id` parameter or the `"tid"` field in the body of the request are required fields."""
    description: str | None = Field(default=None, description="A brief label or note describing what the time entry is tracking.")
    tags: list[StartatimeEntryBodyTagsItem] | None = Field(default=None, description="A list of time tracking label objects to associate with this entry; available to Business Plan users and above. Order is not significant.")
    tid: str | None = Field(default=None, description="The ID of the task to associate with this time entry.")
    billable: bool | None = Field(default=None, description="Indicates whether the time being tracked should be marked as billable.")
class StartatimeEntryRequest(StrictModel):
    """Starts a running timer for the authenticated user within the specified workspace. Optionally associates the entry with a task, tags, and billable status."""
    path: StartatimeEntryRequestPath
    query: StartatimeEntryRequestQuery | None = None
    body: StartatimeEntryRequestBody | None = None

# Operation: stop_time_entry
class StopatimeEntryRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the workspace in which to stop the active time entry.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class StopatimeEntryRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, which must be set to indicate JSON formatting.", examples=['application/json'])
class StopatimeEntryRequest(StrictModel):
    """Stops the currently running timer for the authenticated user in the specified workspace. Only one active timer can be running at a time, and this operation halts it immediately."""
    path: StopatimeEntryRequestPath
    header: StopatimeEntryRequestHeader

# Operation: invite_workspace_member
class InviteUserToWorkspaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace to which the user will be invited.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class InviteUserToWorkspaceRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the person to invite to the Workspace.")
    admin: bool = Field(default=..., description="Set to true to grant the invited user admin-level permissions in the Workspace, or false for standard member permissions.")
    custom_role_id: int | None = Field(default=None, description="The ID of a custom role to assign to the invited user upon joining, if your Workspace has custom roles configured. Omit to use the default member role.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class InviteUserToWorkspaceRequest(StrictModel):
    """Invites a user to join a Workspace as a full member via email. This endpoint is exclusive to Enterprise Plan Workspaces; use the Invite Guest endpoint to add guest-level users instead."""
    path: InviteUserToWorkspaceRequestPath
    body: InviteUserToWorkspaceRequestBody

# Operation: get_workspace_user
class GetUserRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique numeric ID of the Workspace (also referred to as a team) containing the user.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    user_id: float = Field(default=..., description="The unique numeric ID of the user to retrieve within the specified Workspace.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class GetUserRequestQuery(StrictModel):
    include_shared: bool | None = Field(default=None, description="When set to false, excludes details of items shared with the user as a guest; defaults to true to include all shared item details.", examples=[False])
class GetUserRequest(StrictModel):
    """Retrieves detailed profile and role information for a specific user within a Workspace. Available exclusively on the Enterprise Plan."""
    path: GetUserRequestPath
    query: GetUserRequestQuery | None = None

# Operation: update_workspace_user
class EditUserOnWorkspaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace (team) in which the user will be updated.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    user_id: float = Field(default=..., description="The unique identifier of the user to be updated within the specified Workspace.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class EditUserOnWorkspaceRequestBody(StrictModel):
    username: str = Field(default=..., description="The new display name to assign to the user within the Workspace.")
    admin: bool = Field(default=..., description="Whether the user should be granted admin-level privileges in the Workspace. Set to true to grant admin access, false to revoke it.")
    custom_role_id: int = Field(default=..., description="The identifier of the custom role to assign to the user, as defined in the Workspace's Enterprise role configuration.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
class EditUserOnWorkspaceRequest(StrictModel):
    """Update a workspace user's display name, admin status, and custom role assignment. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""
    path: EditUserOnWorkspaceRequestPath
    body: EditUserOnWorkspaceRequestBody

# Operation: remove_workspace_user
class RemoveUserFromWorkspaceRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace (team) from which the user will be removed.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
    user_id: float = Field(default=..., description="The unique identifier of the user to be deactivated and removed from the Workspace.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[403])
class RemoveUserFromWorkspaceRequest(StrictModel):
    """Deactivates and removes a user from the specified Workspace, revoking their access. This endpoint is exclusively available to Workspaces on the Enterprise Plan."""
    path: RemoveUserFromWorkspaceRequestPath

# Operation: list_workspace_views
class GetTeamViewsRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose Everything-level views you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetTeamViewsRequest(StrictModel):
    """Retrieves all task and page views available at the Everything level of a Workspace, providing a top-level overview of all views across the entire Workspace."""
    path: GetTeamViewsRequestPath

# Operation: create_workspace_view
class CreateTeamViewRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace in which to create the view.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class CreateTeamViewRequestBodyGrouping(StrictModel):
    field: str = Field(default=..., validation_alias="field", serialization_alias="field", description="The field by which tasks in the view are grouped. Use 'none' to disable grouping.")
    dir_: int = Field(default=..., validation_alias="dir", serialization_alias="dir", description="The sort direction for groups. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of group identifiers that should be rendered in a collapsed state by default. Order is not significant; each item is a group identifier string.")
    ignore: bool = Field(default=..., validation_alias="ignore", serialization_alias="ignore", description="When true, certain default behaviors or validations are bypassed during view creation.")
class CreateTeamViewRequestBodyDivide(StrictModel):
    field: None = Field(default=None, validation_alias="field", serialization_alias="field", description="The field used to divide tasks within groups. Set to null to disable division.")
    dir_: None = Field(default=None, validation_alias="dir", serialization_alias="dir", description="The sort direction for divided groups. Set to null to disable.")
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of division identifiers that should be rendered in a collapsed state by default. Order is not significant; each item is a division identifier string.")
class CreateTeamViewRequestBodySorting(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An ordered array of field objects specifying the sort fields and their directions. Supports the same fields available when filtering a view.")
class CreateTeamViewRequestBodyFilters(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of filter field objects defining which fields and conditions are used to filter tasks displayed in the view. Refer to the filter-views documentation for available fields.")
    op: str = Field(default=..., validation_alias="op", serialization_alias="op", description="The logical operator used to combine multiple filter conditions. Use 'AND' to require all conditions to match, or 'OR' to require any condition to match.")
    search: str = Field(default=..., validation_alias="search", serialization_alias="search", description="A search string used to filter tasks displayed in the view by matching task names or content.")
    show_closed: bool = Field(default=..., validation_alias="show_closed", serialization_alias="show_closed", description="When true, closed tasks are included in the view alongside open tasks.")
class CreateTeamViewRequestBodyColumns(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of column field objects controlling which columns are visible in the view. Custom Fields must use the 'cf_' prefix and be formatted as a JSON object with the Custom Field ID.")
class CreateTeamViewRequestBodyTeamSidebar(StrictModel):
    assignees: list[str] = Field(default=..., validation_alias="assignees", serialization_alias="assignees", description="An array of assignee identifiers used to filter tasks shown in the view to only those assigned to the specified users.")
    assigned_comments: bool = Field(default=..., validation_alias="assigned_comments", serialization_alias="assigned_comments", description="When true, the view displays comments that are assigned to users.")
    unassigned_tasks: bool = Field(default=..., validation_alias="unassigned_tasks", serialization_alias="unassigned_tasks", description="When true, tasks with no assignee are included in the view.")
class CreateTeamViewRequestBodySettings(StrictModel):
    show_task_locations: bool = Field(default=..., validation_alias="show_task_locations", serialization_alias="show_task_locations", description="When true, the location (List, Folder, Space) of each task is displayed within the view.")
    show_subtasks: int = Field(default=..., validation_alias="show_subtasks", serialization_alias="show_subtasks", description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    show_subtask_parent_names: bool = Field(default=..., validation_alias="show_subtask_parent_names", serialization_alias="show_subtask_parent_names", description="When true, the parent task name is shown alongside each subtask in the view.")
    show_closed_subtasks: bool = Field(default=..., validation_alias="show_closed_subtasks", serialization_alias="show_closed_subtasks", description="When true, closed subtasks are included in the view.")
    show_assignees: bool = Field(default=..., validation_alias="show_assignees", serialization_alias="show_assignees", description="When true, assignee avatars or names are displayed on task cards or rows within the view.")
    show_images: bool = Field(default=..., validation_alias="show_images", serialization_alias="show_images", description="When true, image attachments are displayed as previews on task cards or rows within the view.")
    collapse_empty_columns: str | None = Field(default=..., validation_alias="collapse_empty_columns", serialization_alias="collapse_empty_columns", description="Controls whether empty columns are collapsed in the view. Applicable primarily to Board-type views.")
    me_comments: bool = Field(default=..., validation_alias="me_comments", serialization_alias="me_comments", description="When true, the view is filtered to show only comments that mention or are assigned to the current user.")
    me_subtasks: bool = Field(default=..., validation_alias="me_subtasks", serialization_alias="me_subtasks", description="When true, the view is filtered to show only subtasks assigned to or created by the current user.")
    me_checklists: bool = Field(default=..., validation_alias="me_checklists", serialization_alias="me_checklists", description="When true, the view is filtered to show only checklists assigned to or created by the current user.")
class CreateTeamViewRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new view.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The view type to create. Determines the visual layout and available features for the view.")
    grouping: CreateTeamViewRequestBodyGrouping
    divide: CreateTeamViewRequestBodyDivide
    sorting: CreateTeamViewRequestBodySorting
    filters: CreateTeamViewRequestBodyFilters
    columns: CreateTeamViewRequestBodyColumns
    team_sidebar: CreateTeamViewRequestBodyTeamSidebar
    settings: CreateTeamViewRequestBodySettings
class CreateTeamViewRequest(StrictModel):
    """Create a new view at the Everything (Workspace) level, supporting view types such as List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt. Configure grouping, sorting, filtering, and display settings for the view."""
    path: CreateTeamViewRequestPath
    body: CreateTeamViewRequestBody

# Operation: list_space_views
class GetSpaceViewsRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space whose views you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[790])
class GetSpaceViewsRequest(StrictModel):
    """Retrieve all task and page views available within a specific Space. Useful for discovering how work is organized and displayed within a Space."""
    path: GetSpaceViewsRequestPath

# Operation: create_space_view
class CreateSpaceViewRequestPath(StrictModel):
    space_id: float = Field(default=..., description="The unique identifier of the Space where the new view will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[790])
class CreateSpaceViewRequestBodyGrouping(StrictModel):
    field: str = Field(default=..., validation_alias="field", serialization_alias="field", description="The field by which tasks in the view are grouped. Use 'none' to disable grouping.")
    dir_: int = Field(default=..., validation_alias="dir", serialization_alias="dir", description="Sort direction for groups. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of group identifiers that should be rendered in a collapsed state by default in this view.")
    ignore: bool = Field(default=..., validation_alias="ignore", serialization_alias="ignore", description="When true, certain default behaviors or validations are bypassed during view creation.")
class CreateSpaceViewRequestBodyDivide(StrictModel):
    field: None = Field(default=None, validation_alias="field", serialization_alias="field", description="The field used to divide tasks within groups. Set to null to disable division.")
    dir_: None = Field(default=None, validation_alias="dir", serialization_alias="dir", description="Sort direction for divided groups. Set to null to disable.")
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of division identifiers that should be rendered in a collapsed state by default in this view.")
class CreateSpaceViewRequestBodySorting(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An ordered array of field objects specifying the sort criteria for tasks in the view. Supports the same fields available when filtering a view.")
class CreateSpaceViewRequestBodyFilters(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of filter field objects that restrict which tasks appear in the view. Refer to the filter-views documentation for the full list of supported fields.")
    op: str = Field(default=..., validation_alias="op", serialization_alias="op", description="Logical operator applied to combine multiple filter conditions. Use 'AND' to require all conditions, or 'OR' to require any one condition.")
    search: str = Field(default=..., validation_alias="search", serialization_alias="search", description="A search string used to filter tasks displayed in the view by matching text content.")
    show_closed: bool = Field(default=..., validation_alias="show_closed", serialization_alias="show_closed", description="When true, closed tasks are included in the view alongside open tasks.")
class CreateSpaceViewRequestBodyColumns(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of column field objects controlling which columns are visible in the view. Custom Fields must use the 'cf_' prefix and be formatted as a JSON object with the Custom Field ID.")
class CreateSpaceViewRequestBodyTeamSidebar(StrictModel):
    assignees: list[str] = Field(default=..., validation_alias="assignees", serialization_alias="assignees", description="An array of assignee identifiers used to filter tasks shown in the view to only those assigned to the specified users.")
    assigned_comments: bool = Field(default=..., validation_alias="assigned_comments", serialization_alias="assigned_comments", description="When true, the view displays tasks that have comments assigned to specific users.")
    unassigned_tasks: bool = Field(default=..., validation_alias="unassigned_tasks", serialization_alias="unassigned_tasks", description="When true, tasks with no assignee are included in the view.")
class CreateSpaceViewRequestBodySettings(StrictModel):
    show_task_locations: bool = Field(default=..., validation_alias="show_task_locations", serialization_alias="show_task_locations", description="When true, the location (List, Folder, Space) of each task is displayed within the view.")
    show_subtasks: int = Field(default=..., validation_alias="show_subtasks", serialization_alias="show_subtasks", description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    show_subtask_parent_names: bool = Field(default=..., validation_alias="show_subtask_parent_names", serialization_alias="show_subtask_parent_names", description="When true, the parent task name is shown alongside each subtask in the view for additional context.")
    show_closed_subtasks: bool = Field(default=..., validation_alias="show_closed_subtasks", serialization_alias="show_closed_subtasks", description="When true, closed subtasks are included in the view.")
    show_assignees: bool = Field(default=..., validation_alias="show_assignees", serialization_alias="show_assignees", description="When true, assignee avatars or names are displayed on task cards within the view.")
    show_images: bool = Field(default=..., validation_alias="show_images", serialization_alias="show_images", description="When true, image attachments are previewed directly on task cards within the view.")
    collapse_empty_columns: str | None = Field(default=..., validation_alias="collapse_empty_columns", serialization_alias="collapse_empty_columns", description="Controls whether empty columns are collapsed in applicable view types such as Board.")
    me_comments: bool = Field(default=..., validation_alias="me_comments", serialization_alias="me_comments", description="When true, the view is filtered to show only tasks that have comments from the currently authenticated user.")
    me_subtasks: bool = Field(default=..., validation_alias="me_subtasks", serialization_alias="me_subtasks", description="When true, the view is filtered to show only tasks that have subtasks assigned to the currently authenticated user.")
    me_checklists: bool = Field(default=..., validation_alias="me_checklists", serialization_alias="me_checklists", description="When true, the view is filtered to show only tasks that have checklist items assigned to the currently authenticated user.")
class CreateSpaceViewRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new view.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The view type to create. Determines the layout and interaction model for tasks in this view.")
    grouping: CreateSpaceViewRequestBodyGrouping
    divide: CreateSpaceViewRequestBodyDivide
    sorting: CreateSpaceViewRequestBodySorting
    filters: CreateSpaceViewRequestBodyFilters
    columns: CreateSpaceViewRequestBodyColumns
    team_sidebar: CreateSpaceViewRequestBodyTeamSidebar
    settings: CreateSpaceViewRequestBodySettings
class CreateSpaceViewRequest(StrictModel):
    """Create a new view (List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt) within a specified Space, with full control over grouping, sorting, filtering, and display settings."""
    path: CreateSpaceViewRequestPath
    body: CreateSpaceViewRequestBody

# Operation: list_folder_views
class GetFolderViewsRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique identifier of the Folder whose views you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[457])
class GetFolderViewsRequest(StrictModel):
    """Retrieves all task and page views available within a specific Folder. Use this to discover the views configured for organizing and displaying folder content."""
    path: GetFolderViewsRequestPath

# Operation: create_folder_view
class CreateFolderViewRequestPath(StrictModel):
    folder_id: float = Field(default=..., description="The unique numeric identifier of the folder where the new view will be created.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[457])
class CreateFolderViewRequestBodyGrouping(StrictModel):
    field: str = Field(default=..., validation_alias="field", serialization_alias="field", description="The field by which tasks in the view are grouped. Accepted values are none, status, priority, assignee, tag, or dueDate.")
    dir_: int = Field(default=..., validation_alias="dir", serialization_alias="dir", description="Sort direction for the grouping field. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of group identifiers that should appear collapsed by default in the view. Order is not significant; each item represents a group to collapse.")
    ignore: bool = Field(default=..., validation_alias="ignore", serialization_alias="ignore", description="When true, certain default behaviors or notifications for this view are ignored. Consult ClickUp documentation for the specific behavior this flag suppresses.")
class CreateFolderViewRequestBodyDivide(StrictModel):
    field: None = Field(default=None, validation_alias="field", serialization_alias="field", description="The field used to divide tasks within the view. Set to null to disable division.")
    dir_: None = Field(default=None, validation_alias="dir", serialization_alias="dir", description="Sort direction for the divide field. Set to null to disable divide sorting.")
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of divide group identifiers that should appear collapsed by default. Order is not significant; each item represents a divide group to collapse.")
class CreateFolderViewRequestBodySorting(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An ordered array of field objects defining the sort sequence applied to tasks in the view. Supports the same fields available when filtering a view; earlier entries in the array take sort precedence.")
class CreateFolderViewRequestBodyFilters(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of filter field objects that restrict which tasks appear in the view. Refer to the ClickUp filter-views documentation for the full list of supported field identifiers.")
    op: str = Field(default=..., validation_alias="op", serialization_alias="op", description="Logical operator applied to combine multiple filter conditions. Use AND to require all filters to match, or OR to require at least one filter to match.")
    search: str = Field(default=..., validation_alias="search", serialization_alias="search", description="A search string used to filter tasks displayed in the view by matching against task names or content.")
    show_closed: bool = Field(default=..., validation_alias="show_closed", serialization_alias="show_closed", description="When true, closed tasks are included in the view alongside open tasks.")
class CreateFolderViewRequestBodyColumns(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of column field objects controlling which columns are visible in the view. Custom Fields must use the cf_ prefix and be formatted as a JSON object with the Custom Field ID.")
class CreateFolderViewRequestBodyTeamSidebar(StrictModel):
    assignees: list[str] = Field(default=..., validation_alias="assignees", serialization_alias="assignees", description="An array of assignee user IDs used to filter tasks shown in the view to only those assigned to the specified users.")
    assigned_comments: bool = Field(default=..., validation_alias="assigned_comments", serialization_alias="assigned_comments", description="When true, the view displays tasks that have comments assigned to users.")
    unassigned_tasks: bool = Field(default=..., validation_alias="unassigned_tasks", serialization_alias="unassigned_tasks", description="When true, tasks with no assignee are included in the view.")
class CreateFolderViewRequestBodySettings(StrictModel):
    show_task_locations: bool = Field(default=..., validation_alias="show_task_locations", serialization_alias="show_task_locations", description="When true, the location (Space, Folder, List) of each task is shown within the view.")
    show_subtasks: int = Field(default=..., validation_alias="show_subtasks", serialization_alias="show_subtasks", description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    show_subtask_parent_names: bool = Field(default=..., validation_alias="show_subtask_parent_names", serialization_alias="show_subtask_parent_names", description="When true, the parent task name is displayed alongside each subtask in the view for additional context.")
    show_closed_subtasks: bool = Field(default=..., validation_alias="show_closed_subtasks", serialization_alias="show_closed_subtasks", description="When true, closed subtasks are included in the view.")
    show_assignees: bool = Field(default=..., validation_alias="show_assignees", serialization_alias="show_assignees", description="When true, assignee avatars or names are shown on task cards within the view.")
    show_images: bool = Field(default=..., validation_alias="show_images", serialization_alias="show_images", description="When true, image attachments are displayed inline on task cards within the view.")
    collapse_empty_columns: str | None = Field(default=..., validation_alias="collapse_empty_columns", serialization_alias="collapse_empty_columns", description="Controls whether empty columns are collapsed in the view. Provide the desired collapse behavior as a string value.")
    me_comments: bool = Field(default=..., validation_alias="me_comments", serialization_alias="me_comments", description="When true, the view is filtered to show only tasks that have comments from the currently authenticated user.")
    me_subtasks: bool = Field(default=..., validation_alias="me_subtasks", serialization_alias="me_subtasks", description="When true, the view is filtered to show only subtasks assigned to or created by the currently authenticated user.")
    me_checklists: bool = Field(default=..., validation_alias="me_checklists", serialization_alias="me_checklists", description="When true, the view is filtered to show only tasks with checklists belonging to the currently authenticated user.")
class CreateFolderViewRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new view.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The view type to create. Must be one of the supported layout types: list, board, calendar, table, timeline, workload, activity, map, conversation, or gantt.")
    grouping: CreateFolderViewRequestBodyGrouping
    divide: CreateFolderViewRequestBodyDivide
    sorting: CreateFolderViewRequestBodySorting
    filters: CreateFolderViewRequestBodyFilters
    columns: CreateFolderViewRequestBodyColumns
    team_sidebar: CreateFolderViewRequestBodyTeamSidebar
    settings: CreateFolderViewRequestBodySettings
class CreateFolderViewRequest(StrictModel):
    """Create a new view (List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt) inside a specified Folder, with full control over grouping, sorting, filtering, and display settings."""
    path: CreateFolderViewRequestPath
    body: CreateFolderViewRequestBody

# Operation: list_views
class GetListViewsRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique identifier of the List whose views you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[124])
class GetListViewsRequest(StrictModel):
    """Retrieves all task and page views available for a specified List. Returns standard views and required views as separate response groups."""
    path: GetListViewsRequestPath

# Operation: create_list_view
class CreateListViewRequestPath(StrictModel):
    list_id: float = Field(default=..., description="The unique identifier of the List in which to create the new view.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[124])
class CreateListViewRequestBodyGrouping(StrictModel):
    field: str = Field(default=..., validation_alias="field", serialization_alias="field", description="The field by which tasks in the view are grouped. Use 'none' to disable grouping.")
    dir_: int = Field(default=..., validation_alias="dir", serialization_alias="dir", description="The sort direction for groups. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of group identifiers that should be rendered in a collapsed state by default in the view.")
    ignore: bool = Field(default=..., validation_alias="ignore", serialization_alias="ignore", description="When true, certain default behaviors or inherited settings are ignored when creating the view.")
class CreateListViewRequestBodyDivide(StrictModel):
    field: None = Field(default=None, validation_alias="field", serialization_alias="field", description="The field used to divide tasks within the view. Set to null to disable division.")
    dir_: None = Field(default=None, validation_alias="dir", serialization_alias="dir", description="The sort direction for the divide field. Set to null to disable.")
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of divide-group identifiers that should be rendered in a collapsed state by default in the view.")
class CreateListViewRequestBodySorting(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An ordered array of field definitions specifying which fields to sort by and in what direction. Supports the same fields available when filtering a view.")
class CreateListViewRequestBodyFilters(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of filter field definitions to apply to the view, limiting which tasks are displayed. Refer to the filter-views documentation for available fields.")
    op: str = Field(default=..., validation_alias="op", serialization_alias="op", description="The logical operator used to combine multiple filter conditions. Use 'AND' to require all conditions, or 'OR' to require any condition.")
    search: str = Field(default=..., validation_alias="search", serialization_alias="search", description="A search string used to filter tasks displayed in the view by matching text content.")
    show_closed: bool = Field(default=..., validation_alias="show_closed", serialization_alias="show_closed", description="When true, closed tasks are included in the view alongside open tasks.")
class CreateListViewRequestBodyColumns(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of column field definitions to display in the view. Custom Fields must use the 'cf_' prefix and be formatted as a JSON object with the Custom Field ID.")
class CreateListViewRequestBodyTeamSidebar(StrictModel):
    assignees: list[str] = Field(default=..., validation_alias="assignees", serialization_alias="assignees", description="An array of assignee identifiers used to filter the view to tasks assigned to specific users.")
    assigned_comments: bool = Field(default=..., validation_alias="assigned_comments", serialization_alias="assigned_comments", description="When true, the view displays comments that have been assigned to users.")
    unassigned_tasks: bool = Field(default=..., validation_alias="unassigned_tasks", serialization_alias="unassigned_tasks", description="When true, tasks with no assignee are included in the view.")
class CreateListViewRequestBodySettings(StrictModel):
    show_task_locations: bool = Field(default=..., validation_alias="show_task_locations", serialization_alias="show_task_locations", description="When true, the location (Space, Folder, List) of each task is shown within the view.")
    show_subtasks: int = Field(default=..., validation_alias="show_subtasks", serialization_alias="show_subtasks", description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    show_subtask_parent_names: bool = Field(default=..., validation_alias="show_subtask_parent_names", serialization_alias="show_subtask_parent_names", description="When true, the parent task name is displayed alongside each subtask in the view.")
    show_closed_subtasks: bool = Field(default=..., validation_alias="show_closed_subtasks", serialization_alias="show_closed_subtasks", description="When true, closed subtasks are included in the view.")
    show_assignees: bool = Field(default=..., validation_alias="show_assignees", serialization_alias="show_assignees", description="When true, assignee avatars or names are shown on task cards or rows within the view.")
    show_images: bool = Field(default=..., validation_alias="show_images", serialization_alias="show_images", description="When true, image attachments are previewed directly on task cards or rows within the view.")
    collapse_empty_columns: str | None = Field(default=..., validation_alias="collapse_empty_columns", serialization_alias="collapse_empty_columns", description="Controls whether empty columns are collapsed in the view, reducing visual clutter.")
    me_comments: bool = Field(default=..., validation_alias="me_comments", serialization_alias="me_comments", description="When true, the view is filtered to show only tasks that have comments from the current user.")
    me_subtasks: bool = Field(default=..., validation_alias="me_subtasks", serialization_alias="me_subtasks", description="When true, the view is filtered to show only tasks that have subtasks assigned to or created by the current user.")
    me_checklists: bool = Field(default=..., validation_alias="me_checklists", serialization_alias="me_checklists", description="When true, the view is filtered to show only tasks that have checklist items assigned to the current user.")
class CreateListViewRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new view.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The view type to create. Determines the visual layout and available features for the view.")
    grouping: CreateListViewRequestBodyGrouping
    divide: CreateListViewRequestBodyDivide
    sorting: CreateListViewRequestBodySorting
    filters: CreateListViewRequestBodyFilters
    columns: CreateListViewRequestBodyColumns
    team_sidebar: CreateListViewRequestBodyTeamSidebar
    settings: CreateListViewRequestBodySettings
class CreateListViewRequest(StrictModel):
    """Create a new view (List, Board, Calendar, Table, Timeline, Workload, Activity, Map, Chat, or Gantt) within a specified List, configuring grouping, sorting, filtering, and display options."""
    path: CreateListViewRequestPath
    body: CreateListViewRequestBody

# Operation: get_view
class GetViewRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view to retrieve. Corresponds to a specific task or page view within the workspace.", examples=['3c-105'])
class GetViewRequest(StrictModel):
    """Retrieves metadata and configuration details for a specific task or page view by its unique identifier. The fields returned vary depending on the view type."""
    path: GetViewRequestPath

# Operation: update_view
class UpdateViewRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view to update.", examples=['3c'])
class UpdateViewRequestBodyParent(StrictModel):
    type_: int = Field(default=..., validation_alias="type", serialization_alias="type", description="The hierarchy level of the parent location where the view resides. Use 7 for Workspace, 4 for Space, 5 for Folder, or 6 for List.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Workspace, Space, Folder, or List that contains this view.")
class UpdateViewRequestBodyGrouping(StrictModel):
    field: str = Field(default=..., validation_alias="field", serialization_alias="field", description="The field by which tasks in the view are grouped. Accepted values are none, status, priority, assignee, tag, or dueDate.")
    dir_: int = Field(default=..., validation_alias="dir", serialization_alias="dir", description="The sort direction for grouping. Use 1 for ascending order (e.g., urgent priority at top) or -1 for descending order (e.g., no priority at top).", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of group identifiers that should be rendered in a collapsed state within the view.")
    ignore: bool = Field(default=..., validation_alias="ignore", serialization_alias="ignore", description="When true, ignores the default view settings and applies only the explicitly provided configuration.")
class UpdateViewRequestBodyDivide(StrictModel):
    field: None = Field(default=None, validation_alias="field", serialization_alias="field", description="The field used to divide tasks within the view. Set to null to disable division.")
    dir_: None = Field(default=None, validation_alias="dir", serialization_alias="dir", description="The sort direction for the divide field. Set to null to disable.")
    collapsed: list[str] = Field(default=..., validation_alias="collapsed", serialization_alias="collapsed", description="An array of divide group identifiers that should be rendered in a collapsed state within the view.")
class UpdateViewRequestBodySorting(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An ordered array of field objects defining the sort criteria for the view. Each item specifies a field and sort direction; refer to the filter-views documentation for supported field names.")
class UpdateViewRequestBodyFilters(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of filter field objects applied to the view to restrict which tasks are displayed. Refer to the filter-views documentation for the full list of supported fields.")
    op: str = Field(default=..., validation_alias="op", serialization_alias="op", description="The logical operator used to combine multiple filter conditions. Use AND to require all conditions to match, or OR to require at least one condition to match.")
    search: str = Field(default=..., validation_alias="search", serialization_alias="search", description="A text search string used to filter tasks displayed in the view by keyword.")
    show_closed: bool = Field(default=..., validation_alias="show_closed", serialization_alias="show_closed", description="When true, closed tasks are included in the view alongside open tasks.")
class UpdateViewRequestBodyColumns(StrictModel):
    fields: list[str] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of column field objects defining which columns are visible in the view. Custom Fields must use the cf_ prefix and be formatted as a JSON object with the field's UUID.")
class UpdateViewRequestBodyTeamSidebar(StrictModel):
    assignees: list[str] = Field(default=..., validation_alias="assignees", serialization_alias="assignees", description="An array of assignee user IDs used to filter tasks shown in the view to only those assigned to the specified users.")
    assigned_comments: bool = Field(default=..., validation_alias="assigned_comments", serialization_alias="assigned_comments", description="When true, the view displays only tasks that have comments assigned to a user.")
    unassigned_tasks: bool = Field(default=..., validation_alias="unassigned_tasks", serialization_alias="unassigned_tasks", description="When true, tasks with no assignee are included in the view.")
class UpdateViewRequestBodySettings(StrictModel):
    show_task_locations: bool = Field(default=..., validation_alias="show_task_locations", serialization_alias="show_task_locations", description="When true, the location (Space, Folder, List) of each task is displayed within the view.")
    show_subtasks: int = Field(default=..., validation_alias="show_subtasks", serialization_alias="show_subtasks", description="Controls how subtasks are displayed. Use 1 to show subtasks separately, 2 to show them expanded inline, or 3 to show them collapsed inline.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'})
    show_subtask_parent_names: bool = Field(default=..., validation_alias="show_subtask_parent_names", serialization_alias="show_subtask_parent_names", description="When true, the parent task name is shown alongside each subtask in the view.")
    show_closed_subtasks: bool = Field(default=..., validation_alias="show_closed_subtasks", serialization_alias="show_closed_subtasks", description="When true, closed subtasks are included in the view.")
    show_assignees: bool = Field(default=..., validation_alias="show_assignees", serialization_alias="show_assignees", description="When true, assignee avatars or names are displayed on task cards within the view.")
    show_images: bool = Field(default=..., validation_alias="show_images", serialization_alias="show_images", description="When true, image attachments are previewed directly on task cards within the view.")
    collapse_empty_columns: str | None = Field(default=..., validation_alias="collapse_empty_columns", serialization_alias="collapse_empty_columns", description="Controls whether empty columns are collapsed in the view. Applicable primarily to Board views.")
    me_comments: bool = Field(default=..., validation_alias="me_comments", serialization_alias="me_comments", description="When true, the view filters to show only tasks that have comments from the currently authenticated user.")
    me_subtasks: bool = Field(default=..., validation_alias="me_subtasks", serialization_alias="me_subtasks", description="When true, the view filters to show only tasks that have subtasks assigned to the currently authenticated user.")
    me_checklists: bool = Field(default=..., validation_alias="me_checklists", serialization_alias="me_checklists", description="When true, the view filters to show only tasks that have checklist items assigned to the currently authenticated user.")
class UpdateViewRequestBody(StrictModel):
    name: str = Field(default=..., description="The new display name for the view.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of view being updated (e.g., list, board, calendar).")
    parent: UpdateViewRequestBodyParent
    grouping: UpdateViewRequestBodyGrouping
    divide: UpdateViewRequestBodyDivide
    sorting: UpdateViewRequestBodySorting
    filters: UpdateViewRequestBodyFilters
    columns: UpdateViewRequestBodyColumns
    team_sidebar: UpdateViewRequestBodyTeamSidebar
    settings: UpdateViewRequestBodySettings
class UpdateViewRequest(StrictModel):
    """Update an existing view by renaming it or modifying its grouping, sorting, filters, columns, and display settings. Supports all view types within a Workspace, Space, Folder, or List."""
    path: UpdateViewRequestPath
    body: UpdateViewRequestBody

# Operation: delete_view
class DeleteViewRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view to be deleted.", examples=['3c'])
class DeleteViewRequest(StrictModel):
    """Permanently deletes a specified view by its unique identifier. This action is irreversible and removes the view and its configuration from the system."""
    path: DeleteViewRequestPath

# Operation: list_view_tasks
class GetViewTasksRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view whose tasks you want to retrieve.", examples=['3c'])
class GetViewTasksRequestQuery(StrictModel):
    page: int = Field(default=..., description="The zero-based page number to retrieve for paginated results, where 0 returns the first page.", json_schema_extra={'format': 'int32', 'contentEncoding': 'int32'}, examples=[0])
class GetViewTasksRequest(StrictModel):
    """Retrieve all visible tasks within a specific ClickUp view, returned in paginated results."""
    path: GetViewTasksRequestPath
    query: GetViewTasksRequestQuery

# Operation: list_webhooks
class GetWebhooksRequestPath(StrictModel):
    team_id: float = Field(default=..., description="The unique identifier of the Workspace whose webhooks you want to retrieve.", json_schema_extra={'format': 'double', 'contentEncoding': 'double'}, examples=[123])
class GetWebhooksRequest(StrictModel):
    """Retrieves all webhooks created via the API for a specified Workspace. Only webhooks created by the authenticated user are returned."""
    path: GetWebhooksRequestPath

# Operation: delete_webhook
class DeleteWebhookRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier (UUID) of the webhook to delete.", examples=['4b67ac88'])
class DeleteWebhookRequest(StrictModel):
    """Permanently deletes a webhook, stopping all event monitoring and location tracking associated with it. This action cannot be undone."""
    path: DeleteWebhookRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AddtagsfromtimeentriesBodyTagsItem(PermissiveModel):
    name: str
    tag_fg: str
    tag_bg: str

class CreateTaskBodyCustomFieldsItemV0(PermissiveModel):
    """The `value` must be a string with a valid URL."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: str | None = Field(...)

class CreateTaskBodyCustomFieldsItemV1(PermissiveModel):
    """Enter the universal unique identifier (UUID) of the dropdown menu option you want to set. You can find the UUIDs available for each Dropdown Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields) New Dropdown Custom Field options cannot be created from this request."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: str | None = Field(...)

class CreateTaskBodyCustomFieldsItemV10(PermissiveModel):
    """Enter an integer that is greater than or equal to zero and where the `count` property is greater than or equal to the `value`. You can find the `count` property for each Emoji (Rating) Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields)"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: int | None = Field(..., json_schema_extra={'format': 'int32'})

class CreateTaskBodyCustomFieldsItemV11Value(PermissiveModel):
    current: float

class CreateTaskBodyCustomFieldsItemV11(PermissiveModel):
    """Enter a number between the `start` and `end` values of each Manual Progress Custom Field. For example, for a field with `start: 10` and `end: 30`, sending `current: 20` will be displayed as 50% complete in ClickUp. You can find the `start` and `end` values for each Manual Progress Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields) Manual Progress Custom Fields are nullable: `"value": null`."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: CreateTaskBodyCustomFieldsItemV11Value

class CreateTaskBodyCustomFieldsItemV12(PermissiveModel):
    """Enter an array of the universal unique identifiers (UUIDs) of the labels you want to apply. You can find the UUIDs available for each Label Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields) Label Custom Fields are nullable: `"value": null`."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: list[str]

class CreateTaskBodyCustomFieldsItemV13ValueLocation(PermissiveModel):
    lat: float | None = None
    lng: float | None = None

class CreateTaskBodyCustomFieldsItemV13Value(PermissiveModel):
    location: CreateTaskBodyCustomFieldsItemV13ValueLocation | None = None
    formatted_address: str | None = None

class CreateTaskBodyCustomFieldsItemV13(PermissiveModel):
    """Include the latitude, longitude, and formatted address as defined in the [Google Maps Geocoding API.](https://developers.google.com/maps/documentation/geocoding/overview)"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: CreateTaskBodyCustomFieldsItemV13Value

class CreateTaskBodyCustomFieldsItemV14(PermissiveModel):
    """Set a button Custom Field to `true` to "click" it. This will trigger the button's action as if it was clicked in the UI."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: bool | None = Field(...)

class CreateTaskBodyCustomFieldsItemV2(PermissiveModel):
    """The `value` must be a string with a valid email address."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: str | None = Field(...)

class CreateTaskBodyCustomFieldsItemV3(PermissiveModel):
    """The `value` must be a string with a valid country code."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: str | None = Field(...)

class CreateTaskBodyCustomFieldsItemV4ValueOptions(PermissiveModel):
    time_: bool | None = Field(None, validation_alias="time", serialization_alias="time")

class CreateTaskBodyCustomFieldsItemV4(PermissiveModel):
    """The `value` must be Unix time in milliseconds. To display the time in a Date Custom Field in ClickUp, you must include `time: true` in the `value_options` property."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: int | None = Field(..., json_schema_extra={'format': 'int64'})
    value_options: CreateTaskBodyCustomFieldsItemV4ValueOptions | None = None

class CreateTaskBodyCustomFieldsItemV5(PermissiveModel):
    """Enter a string of text."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: str | None = Field(...)

class CreateTaskBodyCustomFieldsItemV6(PermissiveModel):
    """Enter a number."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: float | None = Field(...)

class CreateTaskBodyCustomFieldsItemV7(PermissiveModel):
    """You can set an amount, but not the currency of a Money Custom Field via the API. You can check the currency of a Money Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields)"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: float | None = Field(...)

class CreateTaskBodyCustomFieldsItemV8Value(PermissiveModel):
    add: list[str] | None = None
    rem: list[str] | None = None

class CreateTaskBodyCustomFieldsItemV8(PermissiveModel):
    """Enter an array of task ids in the `add` property to add them to a Task Relationship Custom Field. Enter them into the `rem` property to remove tasks from the Relationship. Task Relationship Custom Fields are nullable: `"value": null`."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: CreateTaskBodyCustomFieldsItemV8Value

class CreateTaskBodyCustomFieldsItemV9Value(PermissiveModel):
    add: list[float] | None = None
    rem: list[float] | None = None

class CreateTaskBodyCustomFieldsItemV9(PermissiveModel):
    """Enter an array of user ids or a Team id in the `add` property to add them to a People Custom Field. Enter them into the `rem` property to remove users from a People Custom Field. You can get a list of people in the Workspace using [Get Authorized Teams (Workspaces).](ref:getauthorizedteams) People Custom Fields are nullable: `"value": null`."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: CreateTaskBodyCustomFieldsItemV9Value

class CreateatimeentryBodyTagsItem(PermissiveModel):
    name: str
    tag_fg: str
    tag_bg: str

class RemovetagsfromtimeentriesBodyTagsItem(PermissiveModel):
    name: str

class SetCustomFieldValueBodyV0(PermissiveModel):
    """The `value` must be a string with a valid URL."""
    value: str

class SetCustomFieldValueBodyV1(PermissiveModel):
    """Enter the universal unique identifier (UUID) of the dropdown menu option you want to set. You can find the UUIDs available for each Dropdown Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields) New Dropdown Custom Field options cannot be created from this request."""
    value: str

class SetCustomFieldValueBodyV10Value(PermissiveModel):
    add: list[str] | None = None
    rem: list[str] | None = None

class SetCustomFieldValueBodyV10(PermissiveModel):
    """Enter the ID of an attachment uploaded to a `custom_fields` entity using our [V3 Create Attachment](ref:postEntityAttachment) endpoint."""
    value: SetCustomFieldValueBodyV10Value

class SetCustomFieldValueBodyV11(PermissiveModel):
    """Enter an integer that is greater than or equal to zero and where the `count` property is greater than or equal to the `value`. You can find the `count` property for each Emoji (Rating) Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields)"""
    value: int = Field(..., json_schema_extra={'format': 'int32'})

class SetCustomFieldValueBodyV12Value(PermissiveModel):
    current: float

class SetCustomFieldValueBodyV12(PermissiveModel):
    """Enter a number between the `start` and `end` values of each Manual Progress Custom Field. For example, for a field with `start: 10` and `end: 30`, sending `current: 20` will be displayed as 50% complete in ClickUp. You can find the `start` and `end` values for each Manual Progress Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields)"""
    value: SetCustomFieldValueBodyV12Value

class SetCustomFieldValueBodyV13(PermissiveModel):
    """Enter an array of the universal unique identifiers (UUIDs) of the labels you want to apply. You can find the UUIDs available for each Label Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields)"""
    value: list[str]

class SetCustomFieldValueBodyV14ValueLocation(PermissiveModel):
    lat: float | None = None
    lng: float | None = None

class SetCustomFieldValueBodyV14Value(PermissiveModel):
    location: SetCustomFieldValueBodyV14ValueLocation | None = None
    formatted_address: str | None = None

class SetCustomFieldValueBodyV14(PermissiveModel):
    """Include the latitude, longitude, and formatted address as defined in the [Google Maps Geocoding API.](https://developers.google.com/maps/documentation/geocoding/overview)"""
    value: SetCustomFieldValueBodyV14Value

class SetCustomFieldValueBodyV15(PermissiveModel):
    """Set a button Custom Field to `true` to "click" it. This will trigger the button's action as if it was clicked in the UI."""
    value: bool

class SetCustomFieldValueBodyV2(PermissiveModel):
    """The `value` must be a string with a valid email address."""
    value: str

class SetCustomFieldValueBodyV3(PermissiveModel):
    """The `value` must be a string with a valid country code."""
    value: str

class SetCustomFieldValueBodyV4ValueOptions(PermissiveModel):
    time_: bool = Field(..., validation_alias="time", serialization_alias="time")

class SetCustomFieldValueBodyV4(PermissiveModel):
    """The `value` must be Unix time in milliseconds. To display the time in a Date Custom Field in ClickUp, you must include `time: true` in the `value_options` property."""
    value: int | None = Field(None, json_schema_extra={'format': 'int64'})
    value_options: SetCustomFieldValueBodyV4ValueOptions | None = None

class SetCustomFieldValueBodyV5(PermissiveModel):
    """Enter a string of text."""
    value: str

class SetCustomFieldValueBodyV6(PermissiveModel):
    """Enter a number."""
    value: float

class SetCustomFieldValueBodyV7(PermissiveModel):
    """You can set an amount, but not the currency of a Money Custom Field via the API. You can check the currency of a Money Custom Field using [Get Accessible Custom Fields.](ref:getaccessiblecustomfields)"""
    value: float

class SetCustomFieldValueBodyV8Value(PermissiveModel):
    add: list[str] | None = None
    rem: list[str] | None = None

class SetCustomFieldValueBodyV8(PermissiveModel):
    """Enter an array of task ids in the `add` property to add them to a Task Relationship Custom Field. Enter them into the `rem` property to remove tasks from the Relationship."""
    value: SetCustomFieldValueBodyV8Value

class SetCustomFieldValueBodyV9Value(PermissiveModel):
    add: list[float] | None = None
    rem: list[float] | None = None

class SetCustomFieldValueBodyV9(PermissiveModel):
    """Enter an array of user ids or a Team id in the `add` property to add them to a People Custom Field. Enter them into the `rem` property to remove users from a People Custom Field. You can get a list of people in the Workspace using [Get Authorized Teams (Workspaces).](ref:getauthorizedteams)"""
    value: SetCustomFieldValueBodyV9Value

class StartatimeEntryBodyTagsItem(PermissiveModel):
    name: str

class UpdateatimeEntryBodyTagsItem(PermissiveModel):
    name: str
    tag_fg: str
    tag_bg: str


# Rebuild models to resolve forward references (required for circular refs)
AddtagsfromtimeentriesBodyTagsItem.model_rebuild()
CreateatimeentryBodyTagsItem.model_rebuild()
CreateTaskBodyCustomFieldsItemV0.model_rebuild()
CreateTaskBodyCustomFieldsItemV1.model_rebuild()
CreateTaskBodyCustomFieldsItemV10.model_rebuild()
CreateTaskBodyCustomFieldsItemV11.model_rebuild()
CreateTaskBodyCustomFieldsItemV11Value.model_rebuild()
CreateTaskBodyCustomFieldsItemV12.model_rebuild()
CreateTaskBodyCustomFieldsItemV13.model_rebuild()
CreateTaskBodyCustomFieldsItemV13Value.model_rebuild()
CreateTaskBodyCustomFieldsItemV13ValueLocation.model_rebuild()
CreateTaskBodyCustomFieldsItemV14.model_rebuild()
CreateTaskBodyCustomFieldsItemV2.model_rebuild()
CreateTaskBodyCustomFieldsItemV3.model_rebuild()
CreateTaskBodyCustomFieldsItemV4.model_rebuild()
CreateTaskBodyCustomFieldsItemV4ValueOptions.model_rebuild()
CreateTaskBodyCustomFieldsItemV5.model_rebuild()
CreateTaskBodyCustomFieldsItemV6.model_rebuild()
CreateTaskBodyCustomFieldsItemV7.model_rebuild()
CreateTaskBodyCustomFieldsItemV8.model_rebuild()
CreateTaskBodyCustomFieldsItemV8Value.model_rebuild()
CreateTaskBodyCustomFieldsItemV9.model_rebuild()
CreateTaskBodyCustomFieldsItemV9Value.model_rebuild()
RemovetagsfromtimeentriesBodyTagsItem.model_rebuild()
SetCustomFieldValueBodyV0.model_rebuild()
SetCustomFieldValueBodyV1.model_rebuild()
SetCustomFieldValueBodyV10.model_rebuild()
SetCustomFieldValueBodyV10Value.model_rebuild()
SetCustomFieldValueBodyV11.model_rebuild()
SetCustomFieldValueBodyV12.model_rebuild()
SetCustomFieldValueBodyV12Value.model_rebuild()
SetCustomFieldValueBodyV13.model_rebuild()
SetCustomFieldValueBodyV14.model_rebuild()
SetCustomFieldValueBodyV14Value.model_rebuild()
SetCustomFieldValueBodyV14ValueLocation.model_rebuild()
SetCustomFieldValueBodyV15.model_rebuild()
SetCustomFieldValueBodyV2.model_rebuild()
SetCustomFieldValueBodyV3.model_rebuild()
SetCustomFieldValueBodyV4.model_rebuild()
SetCustomFieldValueBodyV4ValueOptions.model_rebuild()
SetCustomFieldValueBodyV5.model_rebuild()
SetCustomFieldValueBodyV6.model_rebuild()
SetCustomFieldValueBodyV7.model_rebuild()
SetCustomFieldValueBodyV8.model_rebuild()
SetCustomFieldValueBodyV8Value.model_rebuild()
SetCustomFieldValueBodyV9.model_rebuild()
SetCustomFieldValueBodyV9Value.model_rebuild()
StartatimeEntryBodyTagsItem.model_rebuild()
UpdateatimeEntryBodyTagsItem.model_rebuild()

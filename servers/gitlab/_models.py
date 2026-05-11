"""
Gitlab MCP Server - Pydantic Models

Generated: 2026-05-11 19:54:25 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "DeleteApiV4AdminCiVariablesKeyRequest",
    "DeleteApiV4AdminClustersClusterIdRequest",
    "DeleteApiV4ApplicationsIdRequest",
    "DeleteApiV4BroadcastMessagesIdRequest",
    "DeleteApiV4GroupsIdAccessRequestsUserIdRequest",
    "DeleteApiV4GroupsIdBadgesBadgeIdRequest",
    "DeleteApiV4ProjectsIdAccessRequestsUserIdRequest",
    "DeleteApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequest",
    "DeleteApiV4ProjectsIdBadgesBadgeIdRequest",
    "DeleteApiV4ProjectsIdRepositoryBranchesBranchRequest",
    "DeleteApiV4ProjectsIdRepositoryMergedBranchesRequest",
    "GetApiV4AdminCiVariablesKeyRequest",
    "GetApiV4AdminCiVariablesRequest",
    "GetApiV4AdminClustersClusterIdRequest",
    "GetApiV4AvatarRequest",
    "GetApiV4BroadcastMessagesIdRequest",
    "GetApiV4BulkImportsEntitiesRequest",
    "GetApiV4BulkImportsImportIdEntitiesEntityIdRequest",
    "GetApiV4BulkImportsImportIdEntitiesRequest",
    "GetApiV4BulkImportsImportIdRequest",
    "GetApiV4BulkImportsRequest",
    "GetApiV4GroupsIdAccessRequestsRequest",
    "GetApiV4GroupsIdBadgesBadgeIdRequest",
    "GetApiV4GroupsIdBadgesRequest",
    "GetApiV4ProjectsIdAccessRequestsRequest",
    "GetApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequest",
    "GetApiV4ProjectsIdBadgesBadgeIdRequest",
    "GetApiV4ProjectsIdBadgesRequest",
    "GetApiV4ProjectsIdRepositoryBranchesBranchRequest",
    "GetApiV4ProjectsIdRepositoryBranchesRequest",
    "GetSingleJobRequest",
    "HeadApiV4ProjectsIdRepositoryBranchesBranchRequest",
    "ListProjectJobsRequest",
    "PostApiV4AdminCiVariablesRequest",
    "PostApiV4AdminClustersAddRequest",
    "PostApiV4BulkImportsRequest",
    "PostApiV4GroupsIdAccessRequestsRequest",
    "PostApiV4GroupsIdBadgesRequest",
    "PostApiV4ProjectsIdAccessRequestsRequest",
    "PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequest",
    "PostApiV4ProjectsIdBadgesRequest",
    "PostApiV4ProjectsIdRepositoryBranchesRequest",
    "PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequest",
    "PutApiV4AdminClustersClusterIdRequest",
    "PutApiV4GroupsIdAccessRequestsUserIdApproveRequest",
    "PutApiV4GroupsIdBadgesBadgeIdRequest",
    "PutApiV4ProjectsIdAccessRequestsUserIdApproveRequest",
    "PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequest",
    "PutApiV4ProjectsIdBadgesBadgeIdRequest",
    "PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequest",
    "PutApiV4ProjectsIdRepositoryBranchesBranchUnprotectRequest",
    "TriggerManualJobRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_group_badge
class GetApiV4GroupsIdBadgesBadgeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. This identifies which group owns the badge you want to retrieve.")
    badge_id: int = Field(default=..., description="The unique identifier of the badge within the group.", json_schema_extra={'format': 'int32'})
class GetApiV4GroupsIdBadgesBadgeIdRequest(StrictModel):
    """Retrieves a specific badge belonging to a group. This allows you to fetch details about a badge that has been assigned to a group."""
    path: GetApiV4GroupsIdBadgesBadgeIdRequestPath

# Operation: update_group_badge
class PutApiV4GroupsIdBadgesBadgeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group owned by the authenticated user.")
    badge_id: int = Field(default=..., description="The unique identifier of the badge to update.", json_schema_extra={'format': 'int32'})
class PutApiV4GroupsIdBadgesBadgeIdRequestBody(StrictModel):
    link_url: str | None = Field(default=None, description="The URL where the badge link should direct users.")
    image_url: str | None = Field(default=None, description="The URL of the image to display as the badge.")
    name: str | None = Field(default=None, description="A descriptive name for the badge.")
class PutApiV4GroupsIdBadgesBadgeIdRequest(StrictModel):
    """Updates an existing badge for a group. Allows modification of the badge's name, image URL, and link URL."""
    path: PutApiV4GroupsIdBadgesBadgeIdRequestPath
    body: PutApiV4GroupsIdBadgesBadgeIdRequestBody | None = None

# Operation: remove_group_badge
class DeleteApiV4GroupsIdBadgesBadgeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. This identifies which group the badge should be removed from.")
    badge_id: int = Field(default=..., description="The unique identifier of the badge to remove from the group.", json_schema_extra={'format': 'int32'})
class DeleteApiV4GroupsIdBadgesBadgeIdRequest(StrictModel):
    """Removes a badge from a group. This allows administrators to delete badges that are no longer needed or relevant to the group."""
    path: DeleteApiV4GroupsIdBadgesBadgeIdRequestPath

# Operation: list_group_badges
class GetApiV4GroupsIdBadgesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. This identifies which group's badges to retrieve.")
class GetApiV4GroupsIdBadgesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of badges to return per page for pagination.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(default=None, description="Filter badges by name. Returns only badges matching the specified name.")
class GetApiV4GroupsIdBadgesRequest(StrictModel):
    """Retrieves a paginated list of badges for a group that are viewable by the authenticated user. Introduced in GitLab 10.6."""
    path: GetApiV4GroupsIdBadgesRequestPath
    query: GetApiV4GroupsIdBadgesRequestQuery | None = None

# Operation: add_group_badge
class PostApiV4GroupsIdBadgesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. You can use either the numeric group ID or the full URL-encoded group path (e.g., 'my-group' or 'parent-group%2Fchild-group').")
class PostApiV4GroupsIdBadgesRequestBody(StrictModel):
    link_url: str = Field(default=..., description="The URL where the badge image links to when clicked. This should be a valid HTTP or HTTPS URL.")
    image_url: str = Field(default=..., description="The URL of the badge image to display. This should be a valid HTTP or HTTPS URL pointing to an image file.")
    name: str | None = Field(default=None, description="A descriptive name for the badge to help identify its purpose. This is displayed as alt text and in the group's badge management interface.")
class PostApiV4GroupsIdBadgesRequest(StrictModel):
    """Adds a badge to a group to display custom branding or status indicators. The badge will be visible on the group's profile page."""
    path: PostApiV4GroupsIdBadgesRequestPath
    body: PostApiV4GroupsIdBadgesRequestBody

# Operation: deny_group_access_request
class DeleteApiV4GroupsIdAccessRequestsUserIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. This identifies which group's access request should be denied.")
    user_id: int = Field(default=..., description="The user ID of the person whose access request is being denied.", json_schema_extra={'format': 'int32'})
class DeleteApiV4GroupsIdAccessRequestsUserIdRequest(StrictModel):
    """Denies an access request from a user to join a group. The access request is removed and the user is not granted group membership."""
    path: DeleteApiV4GroupsIdAccessRequestsUserIdRequestPath

# Operation: approve_group_access_request
class PutApiV4GroupsIdAccessRequestsUserIdApproveRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. Use the numeric group ID or the full URL-encoded path (e.g., 'my-group' or 'parent-group%2Fmy-group').")
    user_id: int = Field(default=..., description="The numeric ID of the user whose access request is being approved.", json_schema_extra={'format': 'int32'})
class PutApiV4GroupsIdAccessRequestsUserIdApproveRequestBody(StrictModel):
    access_level: int | None = Field(default=None, description="The access level to grant the user upon approval. Specifies the user's role and permissions within the group (e.g., Developer, Maintainer).", json_schema_extra={'format': 'int32'})
class PutApiV4GroupsIdAccessRequestsUserIdApproveRequest(StrictModel):
    """Approves a pending access request for a user to join a group. The authenticated user must own the group to perform this action."""
    path: PutApiV4GroupsIdAccessRequestsUserIdApproveRequestPath
    body: PutApiV4GroupsIdAccessRequestsUserIdApproveRequestBody | None = None

# Operation: list_group_access_requests
class GetApiV4GroupsIdAccessRequestsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group. This identifies which group's access requests to retrieve.")
class GetApiV4GroupsIdAccessRequestsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of access requests to return per page for pagination.", json_schema_extra={'format': 'int32'})
class GetApiV4GroupsIdAccessRequestsRequest(StrictModel):
    """Retrieves a paginated list of pending access requests for a group. This allows group owners to review and manage user requests to join the group."""
    path: GetApiV4GroupsIdAccessRequestsRequestPath
    query: GetApiV4GroupsIdAccessRequestsRequestQuery | None = None

# Operation: request_group_access
class PostApiV4GroupsIdAccessRequestsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the group to request access for.")
class PostApiV4GroupsIdAccessRequestsRequest(StrictModel):
    """Submit an access request for the authenticated user to join a group. The group owner can then review and approve or deny the request."""
    path: PostApiV4GroupsIdAccessRequestsRequestPath

# Operation: delete_merged_branches
class DeleteApiV4ProjectsIdRepositoryMergedBranchesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path (e.g., group%2Fproject-name).")
class DeleteApiV4ProjectsIdRepositoryMergedBranchesRequest(StrictModel):
    """Delete all branches that have been merged into the project's default branch. This operation permanently removes merged branches to clean up the repository."""
    path: DeleteApiV4ProjectsIdRepositoryMergedBranchesRequestPath

# Operation: get_branch
class GetApiV4ProjectsIdRepositoryBranchesBranchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be a numeric ID or URL-encoded project path (e.g., group/subgroup/project).")
    branch: int = Field(default=..., description="The name of the branch to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiV4ProjectsIdRepositoryBranchesBranchRequest(StrictModel):
    """Retrieve details for a specific branch in a repository. Returns branch information including commit details and protection status."""
    path: GetApiV4ProjectsIdRepositoryBranchesBranchRequestPath

# Operation: delete_branch
class DeleteApiV4ProjectsIdRepositoryBranchesBranchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path.")
    branch: str = Field(default=..., description="The name of the branch to delete.")
class DeleteApiV4ProjectsIdRepositoryBranchesBranchRequest(StrictModel):
    """Delete a branch from a project repository. This operation permanently removes the specified branch."""
    path: DeleteApiV4ProjectsIdRepositoryBranchesBranchRequestPath

# Operation: check_branch_exists
class HeadApiV4ProjectsIdRepositoryBranchesBranchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded path of the project.")
    branch: str = Field(default=..., description="The name of the branch to check for existence in the repository.")
class HeadApiV4ProjectsIdRepositoryBranchesBranchRequest(StrictModel):
    """Verify whether a specific branch exists in a project repository. Returns a successful response if the branch is found, otherwise returns a 404 error."""
    path: HeadApiV4ProjectsIdRepositoryBranchesBranchRequestPath

# Operation: list_repository_branches
class GetApiV4ProjectsIdRepositoryBranchesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., 'group%2Fproject').")
class GetApiV4ProjectsIdRepositoryBranchesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of branches to return per page for pagination.", json_schema_extra={'format': 'int32'})
    sort: Literal["name_asc", "updated_asc", "updated_desc"] | None = Field(default=None, description="Sort the returned branches by name in ascending order, or by last update time in ascending or descending order.")
class GetApiV4ProjectsIdRepositoryBranchesRequest(StrictModel):
    """Retrieve a list of branches from a project's repository. Supports pagination and sorting by branch name or last update time."""
    path: GetApiV4ProjectsIdRepositoryBranchesRequestPath
    query: GetApiV4ProjectsIdRepositoryBranchesRequestQuery | None = None

# Operation: create_branch
class PostApiV4ProjectsIdRepositoryBranchesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project).")
class PostApiV4ProjectsIdRepositoryBranchesRequestQuery(StrictModel):
    branch: str = Field(default=..., description="The name for the new branch to be created.")
    ref: str = Field(default=..., description="The commit SHA or existing branch name from which to create the new branch.")
class PostApiV4ProjectsIdRepositoryBranchesRequest(StrictModel):
    """Create a new branch in a project from a specified commit SHA or existing branch. The new branch will be created with the given name and point to the specified reference."""
    path: PostApiV4ProjectsIdRepositoryBranchesRequestPath
    query: PostApiV4ProjectsIdRepositoryBranchesRequestQuery

# Operation: unprotect_branch
class PutApiV4ProjectsIdRepositoryBranchesBranchUnprotectRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path (e.g., group/subgroup/project).")
    branch: str = Field(default=..., description="The name of the branch to unprotect.")
class PutApiV4ProjectsIdRepositoryBranchesBranchUnprotectRequest(StrictModel):
    """Remove protection from a branch in a project, allowing it to be modified or deleted. This operation reverses any branch protection rules that were previously applied."""
    path: PutApiV4ProjectsIdRepositoryBranchesBranchUnprotectRequestPath

# Operation: protect_branch
class PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    branch: str = Field(default=..., description="The name of the branch to protect.")
class PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequestBody(StrictModel):
    developers_can_push: bool | None = Field(default=None, description="Allow developers to push commits to this branch.")
    developers_can_merge: bool | None = Field(default=None, description="Allow developers to merge pull requests into this branch.")
class PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequest(StrictModel):
    """Protect a branch by restricting push and merge permissions. Configure whether developers can push to or merge into the specified branch."""
    path: PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequestPath
    body: PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequestBody | None = None

# Operation: get_project_badge
class GetApiV4ProjectsIdBadgesBadgeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path (e.g., group/subgroup/project).")
    badge_id: int = Field(default=..., description="The unique identifier of the badge to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiV4ProjectsIdBadgesBadgeIdRequest(StrictModel):
    """Retrieve a specific badge associated with a project. This allows you to fetch details about a project badge by its ID."""
    path: GetApiV4ProjectsIdBadgesBadgeIdRequestPath

# Operation: update_project_badge
class PutApiV4ProjectsIdBadgesBadgeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    badge_id: int = Field(default=..., description="The unique identifier of the badge to update.", json_schema_extra={'format': 'int32'})
class PutApiV4ProjectsIdBadgesBadgeIdRequestBody(StrictModel):
    link_url: str | None = Field(default=None, description="The URL that the badge links to when clicked.")
    image_url: str | None = Field(default=None, description="The URL of the image to display as the badge.")
    name: str | None = Field(default=None, description="A descriptive name for the badge.")
class PutApiV4ProjectsIdBadgesBadgeIdRequest(StrictModel):
    """Updates an existing badge for a project. Allows modification of the badge's name, image URL, and link URL."""
    path: PutApiV4ProjectsIdBadgesBadgeIdRequestPath
    body: PutApiV4ProjectsIdBadgesBadgeIdRequestBody | None = None

# Operation: delete_badge
class DeleteApiV4ProjectsIdBadgesBadgeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project).")
    badge_id: int = Field(default=..., description="The unique identifier of the badge to remove from the project.", json_schema_extra={'format': 'int32'})
class DeleteApiV4ProjectsIdBadgesBadgeIdRequest(StrictModel):
    """Removes a badge from a project. This operation permanently deletes the specified badge and its association with the project."""
    path: DeleteApiV4ProjectsIdBadgesBadgeIdRequestPath

# Operation: list_project_badges
class GetApiV4ProjectsIdBadgesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project).")
class GetApiV4ProjectsIdBadgesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of badges to return per page for pagination.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(default=None, description="Filter badges by name. Returns only badges whose name matches the provided value.")
class GetApiV4ProjectsIdBadgesRequest(StrictModel):
    """Retrieves a paginated list of badges for a project that are visible to the authenticated user. This endpoint was introduced in GitLab 10.6."""
    path: GetApiV4ProjectsIdBadgesRequestPath
    query: GetApiV4ProjectsIdBadgesRequestQuery | None = None

# Operation: create_project_badge
class PostApiV4ProjectsIdBadgesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID or URL-encoded path of the project. Accepts both integer IDs and string paths.")
class PostApiV4ProjectsIdBadgesRequestBody(StrictModel):
    link_url: str = Field(default=..., description="The URL that the badge links to when clicked.")
    image_url: str = Field(default=..., description="The URL of the badge image to display.")
    name: str | None = Field(default=None, description="A descriptive name for the badge to identify its purpose.")
class PostApiV4ProjectsIdBadgesRequest(StrictModel):
    """Adds a new badge to a project. Badges are visual indicators that can link to external URLs and are displayed on the project page."""
    path: PostApiV4ProjectsIdBadgesRequestPath
    body: PostApiV4ProjectsIdBadgesRequestBody

# Operation: deny_access_request
class DeleteApiV4ProjectsIdAccessRequestsUserIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    user_id: int = Field(default=..., description="The numeric ID of the user whose access request should be denied.", json_schema_extra={'format': 'int32'})
class DeleteApiV4ProjectsIdAccessRequestsUserIdRequest(StrictModel):
    """Denies an access request from a user for the specified project. This removes the user's pending access request and prevents them from gaining project access through this request."""
    path: DeleteApiV4ProjectsIdAccessRequestsUserIdRequestPath

# Operation: approve_access_request
class PutApiV4ProjectsIdAccessRequestsUserIdApproveRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    user_id: int = Field(default=..., description="The user ID of the person whose access request is being approved.", json_schema_extra={'format': 'int32'})
class PutApiV4ProjectsIdAccessRequestsUserIdApproveRequestBody(StrictModel):
    access_level: int | None = Field(default=None, description="The access level to grant the user upon approval. Valid levels range from 10 (Guest) to 50 (Owner).", json_schema_extra={'format': 'int32'})
class PutApiV4ProjectsIdAccessRequestsUserIdApproveRequest(StrictModel):
    """Approves a pending access request for a user to join the project. Optionally specify the access level to grant; defaults to Developer role."""
    path: PutApiV4ProjectsIdAccessRequestsUserIdApproveRequestPath
    body: PutApiV4ProjectsIdAccessRequestsUserIdApproveRequestBody | None = None

# Operation: list_access_requests
class GetApiV4ProjectsIdAccessRequestsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject).")
class GetApiV4ProjectsIdAccessRequestsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of access requests to return per page for pagination.", json_schema_extra={'format': 'int32'})
class GetApiV4ProjectsIdAccessRequestsRequest(StrictModel):
    """Retrieves a list of access requests for a project. Access requests allow users to request membership in a project."""
    path: GetApiV4ProjectsIdAccessRequestsRequestPath
    query: GetApiV4ProjectsIdAccessRequestsRequestQuery | None = None

# Operation: request_project_access
class PostApiV4ProjectsIdAccessRequestsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project).")
class PostApiV4ProjectsIdAccessRequestsRequest(StrictModel):
    """Request access to a project as the authenticated user. This allows users to formally request membership or elevated permissions for a project they don't currently have access to."""
    path: PostApiV4ProjectsIdAccessRequestsRequestPath

# Operation: update_alert_metric_image
class PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    alert_iid: int = Field(default=..., description="The internal ID of the alert containing the metric image.", json_schema_extra={'format': 'int32'})
    metric_image_id: int = Field(default=..., description="The unique identifier of the metric image to update.", json_schema_extra={'format': 'int32'})
class PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The URL where the metric image or additional metric information can be viewed.")
    url_text: str | None = Field(default=None, description="A descriptive label or caption for the metric image or its associated URL.")
class PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequest(StrictModel):
    """Update the metric image associated with an alert, including its display URL and descriptive text for reference."""
    path: PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestPath
    body: PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestBody | None = None

# Operation: delete_alert_metric_image
class DeleteApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    alert_iid: int = Field(default=..., description="The internal ID (IID) of the alert from which to remove the metric image.", json_schema_extra={'format': 'int32'})
    metric_image_id: int = Field(default=..., description="The numeric ID of the metric image to delete.", json_schema_extra={'format': 'int32'})
class DeleteApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequest(StrictModel):
    """Remove a metric image associated with an alert in a project. This operation permanently deletes the specified metric image from the alert's collection."""
    path: DeleteApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestPath

# Operation: list_alert_metric_images
class GetApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    alert_iid: int = Field(default=..., description="The internal ID of the alert for which to retrieve associated metric images.", json_schema_extra={'format': 'int32'})
class GetApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequest(StrictModel):
    """Retrieve metric images associated with a specific alert in a project. Metric images provide visual context for alert conditions and their impact."""
    path: GetApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestPath

# Operation: upload_alert_metric_image
class PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path.")
    alert_iid: int = Field(default=..., description="The internal ID of the alert to attach the metric image to.", json_schema_extra={'format': 'int32'})
class PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The image file to upload. Supported formats are typically PNG, JPG, and GIF.", json_schema_extra={'format': 'byte'})
    url: str | None = Field(default=None, description="Optional URL to view additional metric information or the source of the metric data.")
    url_text: str | None = Field(default=None, description="Optional descriptive text explaining the metric image content or the linked URL.")
class PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequest(StrictModel):
    """Upload a metric image to an alert for visualization and documentation purposes. Optionally include a URL and description to provide context about the metric data."""
    path: PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestPath
    body: PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestBody

# Operation: pause_batched_background_migration
class PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the batched background migration to pause.", json_schema_extra={'format': 'int32'})
class PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequestBody(StrictModel):
    database: Literal["main", "ci", "embedding", "geo"] | None = Field(default=None, description="The database instance where the batched background migration is running. Defaults to 'main' if not specified.")
class PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequest(StrictModel):
    """Pause an active batched background migration by its ID. The migration can be resumed later from where it was paused."""
    path: PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequestPath
    body: PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequestBody | None = None

# Operation: get_admin_ci_variable
class GetApiV4AdminCiVariablesKeyRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier key of the instance-level CI/CD variable to retrieve.")
class GetApiV4AdminCiVariablesKeyRequest(StrictModel):
    """Retrieve the details of a specific instance-level CI/CD variable by its key. This operation returns the variable's configuration and metadata."""
    path: GetApiV4AdminCiVariablesKeyRequestPath

# Operation: delete_instance_variable
class DeleteApiV4AdminCiVariablesKeyRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier key of the instance-level variable to delete.")
class DeleteApiV4AdminCiVariablesKeyRequest(StrictModel):
    """Delete an instance-level CI/CD variable by its key. This removes the variable from the GitLab instance configuration."""
    path: DeleteApiV4AdminCiVariablesKeyRequestPath

# Operation: list_instance_variables
class GetApiV4AdminCiVariablesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of variables to return per page. Use this to control pagination when retrieving large result sets.", json_schema_extra={'format': 'int32'})
class GetApiV4AdminCiVariablesRequest(StrictModel):
    """Retrieve all instance-level CI/CD variables available across the GitLab instance. These variables are accessible to all projects and groups."""
    query: GetApiV4AdminCiVariablesRequestQuery | None = None

# Operation: create_instance_variable
class PostApiV4AdminCiVariablesRequestBody(StrictModel):
    key: str = Field(default=..., description="The unique identifier for the variable. Maximum 255 characters.")
    value: str = Field(default=..., description="The value assigned to the variable.")
    protected: bool | None = Field(default=None, description="When enabled, the variable is only available to protected branches and tags, preventing exposure in unprotected environments.")
    masked: bool | None = Field(default=None, description="When enabled, the variable value is masked in job logs and API responses to prevent accidental exposure of sensitive data.")
    raw: bool | None = Field(default=None, description="When enabled, the variable value is treated as a literal string and not expanded. When disabled, variable references are expanded during job execution.")
    variable_type: Literal["env_var", "file"] | None = Field(default=None, description="Specifies whether the variable stores an environment value or a file path.")
class PostApiV4AdminCiVariablesRequest(StrictModel):
    """Create a new instance-level CI/CD variable that is available to all projects. Instance variables are useful for storing secrets and configuration values needed across your entire GitLab instance."""
    body: PostApiV4AdminCiVariablesRequestBody

# Operation: get_cluster
class GetApiV4AdminClustersClusterIdRequestPath(StrictModel):
    cluster_id: int = Field(default=..., description="The unique identifier of the cluster to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiV4AdminClustersClusterIdRequest(StrictModel):
    """Retrieve details for a single instance cluster by its ID. This operation requires GitLab 13.2 or later."""
    path: GetApiV4AdminClustersClusterIdRequestPath

# Operation: update_cluster
class PutApiV4AdminClustersClusterIdRequestPath(StrictModel):
    cluster_id: int = Field(default=..., description="The unique identifier of the cluster to update.", json_schema_extra={'format': 'int32'})
class PutApiV4AdminClustersClusterIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the cluster.")
    enabled: bool | None = Field(default=None, description="Enable or disable GitLab's connection to the Kubernetes cluster.")
    environment_scope: str | None = Field(default=None, description="The environment associated with this cluster deployment.")
    namespace_per_environment: bool | None = Field(default=None, description="When enabled, each environment is deployed to a separate Kubernetes namespace for isolation.")
    domain: str | None = Field(default=None, description="The base domain for the cluster, used for generating application URLs.")
    management_project_id: int | None = Field(default=None, description="The ID of the GitLab project that manages this cluster's resources and configurations.", json_schema_extra={'format': 'int32'})
    managed: bool | None = Field(default=None, description="When enabled, GitLab automatically manages Kubernetes namespaces and service accounts for this cluster.")
class PutApiV4AdminClustersClusterIdRequest(StrictModel):
    """Update an existing instance cluster configuration. Modify cluster settings such as name, connectivity status, environment scope, and management preferences."""
    path: PutApiV4AdminClustersClusterIdRequestPath
    body: PutApiV4AdminClustersClusterIdRequestBody | None = None

# Operation: delete_cluster
class DeleteApiV4AdminClustersClusterIdRequestPath(StrictModel):
    cluster_id: int = Field(default=..., description="The unique identifier of the cluster to delete.", json_schema_extra={'format': 'int32'})
class DeleteApiV4AdminClustersClusterIdRequest(StrictModel):
    """Delete an instance cluster from GitLab. This removes the cluster configuration but does not delete any resources within the connected Kubernetes cluster itself."""
    path: DeleteApiV4AdminClustersClusterIdRequestPath

# Operation: add_kubernetes_cluster
class PostApiV4AdminClustersAddRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the Kubernetes cluster.")
    enabled: bool | None = Field(default=None, description="Whether the cluster is active and available for deployments.")
    environment_scope: str | None = Field(default=None, description="The environment scope this cluster is associated with, such as production or staging. Use * to match all environments.")
    namespace_per_environment: bool | None = Field(default=None, description="Whether to deploy each environment to its own isolated Kubernetes namespace for better resource separation and security.")
    domain: str | None = Field(default=None, description="The base domain for applications deployed to this cluster.")
    management_project_id: int | None = Field(default=None, description="The GitLab project ID that will manage this cluster's namespaces and service accounts.", json_schema_extra={'format': 'int32'})
    managed: bool | None = Field(default=None, description="Whether GitLab automatically manages Kubernetes namespaces and service accounts for this cluster.")
    platform_kubernetes_attributes_api_url: str = Field(default=..., validation_alias="platform_kubernetes_attributes[api_url]", serialization_alias="platform_kubernetes_attributes[api_url]", description="The URL endpoint to access the Kubernetes API server.")
    platform_kubernetes_attributes_token: str = Field(default=..., validation_alias="platform_kubernetes_attributes[token]", serialization_alias="platform_kubernetes_attributes[token]", description="The authentication token or bearer token used to authenticate requests to the Kubernetes API.")
    platform_kubernetes_attributes_authorization_type: Literal["unknown_authorization", "rbac", "abac"] | None = Field(default=None, validation_alias="platform_kubernetes_attributes[authorization_type]", serialization_alias="platform_kubernetes_attributes[authorization_type]", description="The authorization mechanism used by the Kubernetes cluster for access control.")
class PostApiV4AdminClustersAddRequest(StrictModel):
    """Register an existing Kubernetes cluster as an instance cluster in GitLab. This allows GitLab to deploy applications and manage resources on the cluster."""
    body: PostApiV4AdminClustersAddRequestBody

# Operation: delete_application
class DeleteApiV4ApplicationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the application to delete.", json_schema_extra={'format': 'int32'})
class DeleteApiV4ApplicationsIdRequest(StrictModel):
    """Permanently delete a specific application by its ID. This action cannot be undone."""
    path: DeleteApiV4ApplicationsIdRequestPath

# Operation: get_user_avatar
class GetApiV4AvatarRequestQuery(StrictModel):
    email: str = Field(default=..., description="The public email address of the user whose avatar should be retrieved.")
    size: int | None = Field(default=None, description="The width and height in pixels for the returned avatar image. Larger sizes provide higher resolution avatars.", json_schema_extra={'format': 'int32'})
class GetApiV4AvatarRequest(StrictModel):
    """Retrieve the avatar URL for a user based on their email address. Optionally specify a custom image size for the avatar."""
    query: GetApiV4AvatarRequestQuery

# Operation: get_broadcast_message
class GetApiV4BroadcastMessagesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the broadcast message to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiV4BroadcastMessagesIdRequest(StrictModel):
    """Retrieve a specific broadcast message by its ID. Broadcast messages are system-wide announcements visible to all users."""
    path: GetApiV4BroadcastMessagesIdRequestPath

# Operation: delete_broadcast_message
class DeleteApiV4BroadcastMessagesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the broadcast message to delete.", json_schema_extra={'format': 'int32'})
class DeleteApiV4BroadcastMessagesIdRequest(StrictModel):
    """Delete a broadcast message by its ID. This operation permanently removes the specified broadcast message from the system."""
    path: DeleteApiV4BroadcastMessagesIdRequestPath

# Operation: get_migration_entity
class GetApiV4BulkImportsImportIdEntitiesEntityIdRequestPath(StrictModel):
    import_id: int = Field(default=..., description="The unique identifier of the GitLab Migration batch containing the entity you want to retrieve.", json_schema_extra={'format': 'int32'})
    entity_id: int = Field(default=..., description="The unique identifier of the specific entity within the migration whose details you want to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiV4BulkImportsImportIdEntitiesEntityIdRequest(StrictModel):
    """Retrieve detailed information about a specific entity within a GitLab Migration. This allows you to inspect the status and properties of individual migrated items."""
    path: GetApiV4BulkImportsImportIdEntitiesEntityIdRequestPath

# Operation: list_migration_entities
class GetApiV4BulkImportsImportIdEntitiesRequestPath(StrictModel):
    import_id: int = Field(default=..., description="The unique identifier of the GitLab Migration import job to retrieve entities from.", json_schema_extra={'format': 'int32'})
class GetApiV4BulkImportsImportIdEntitiesRequestQuery(StrictModel):
    status: Literal["created", "started", "finished", "timeout", "failed"] | None = Field(default=None, description="Filter entities by their current processing status in the migration workflow.")
    per_page: int | None = Field(default=None, description="Number of entities to return per page for pagination. Defaults to 20 items per page.", json_schema_extra={'format': 'int32'})
class GetApiV4BulkImportsImportIdEntitiesRequest(StrictModel):
    """Retrieve a list of entities from a GitLab Migration import job. Filter by status and paginate through results to monitor migration progress."""
    path: GetApiV4BulkImportsImportIdEntitiesRequestPath
    query: GetApiV4BulkImportsImportIdEntitiesRequestQuery | None = None

# Operation: get_bulk_import
class GetApiV4BulkImportsImportIdRequestPath(StrictModel):
    import_id: int = Field(default=..., description="The unique identifier of the bulk import migration to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiV4BulkImportsImportIdRequest(StrictModel):
    """Retrieve details about a GitLab Migration bulk import job, including its status and progress information."""
    path: GetApiV4BulkImportsImportIdRequestPath

# Operation: list_migration_entities_all
class GetApiV4BulkImportsEntitiesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of entities to return per page for pagination purposes.", json_schema_extra={'format': 'int32'})
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Order in which to sort the returned entities by creation date.")
    status: Literal["created", "started", "finished", "timeout", "failed"] | None = Field(default=None, description="Filter entities by their current migration status to view only those in a specific state.")
class GetApiV4BulkImportsEntitiesRequest(StrictModel):
    """Retrieve a list of all entities from GitLab Migrations. This operation supports pagination, sorting, and filtering by migration status to help track the progress of bulk import operations."""
    query: GetApiV4BulkImportsEntitiesRequestQuery | None = None

# Operation: list_migrations
class GetApiV4BulkImportsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of migration records to return per page for pagination.", json_schema_extra={'format': 'int32'})
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Sort migrations by creation date in ascending or descending order.")
    status: Literal["created", "started", "finished", "timeout", "failed"] | None = Field(default=None, description="Filter migrations by their current status in the migration lifecycle.")
class GetApiV4BulkImportsRequest(StrictModel):
    """Retrieve a list of all GitLab Migrations with optional filtering and sorting. This feature was introduced in GitLab 14.1."""
    query: GetApiV4BulkImportsRequestQuery | None = None

# Operation: start_bulk_migration
class PostApiV4BulkImportsRequestBody(StrictModel):
    configuration_url: str = Field(default=..., validation_alias="configuration[url]", serialization_alias="configuration[url]", description="URL of the source GitLab instance to migrate from (e.g., https://source.gitlab.com)")
    configuration_access_token: str = Field(default=..., validation_alias="configuration[access_token]", serialization_alias="configuration[access_token]", description="Personal access token or project access token from the source GitLab instance with sufficient permissions to read the entities being migrated")
    entities_source_type: list[Literal["group_entity", "project_entity"]] = Field(default=..., validation_alias="entities[source_type]", serialization_alias="entities[source_type]", description="Array of entity types to migrate from the source instance. Each element specifies the type of resource (group or project) being imported")
    entities_source_full_path: list[str] = Field(default=..., validation_alias="entities[source_full_path]", serialization_alias="entities[source_full_path]", description="Array of relative paths for source entities to import. Each path corresponds to the entity at the same index in entities_source_type. Paths should be in the format of full project or group paths on the source instance")
    entities_destination_namespace: list[str] = Field(default=..., validation_alias="entities[destination_namespace]", serialization_alias="entities[destination_namespace]", description="Array of destination namespaces where entities will be imported. Each namespace corresponds to the entity at the same index. Specify the target group or namespace path on the destination instance")
    entities_destination_slug: list[str] | None = Field(default=None, validation_alias="entities[destination_slug]", serialization_alias="entities[destination_slug]", description="Array of optional destination slugs for imported entities. When provided, overrides the default slug derived from the source entity name. Each slug corresponds to the entity at the same index")
    entities_migrate_projects: list[bool] | None = Field(default=None, validation_alias="entities[migrate_projects]", serialization_alias="entities[migrate_projects]", description="Array of boolean flags indicating whether to include nested projects during group migration. Each flag corresponds to the group at the same index in entities_source_type")
class PostApiV4BulkImportsRequest(StrictModel):
    """Initiate a bulk migration of GitLab entities from a source instance to the destination. This operation supports migrating groups and projects with their nested resources between GitLab instances."""
    body: PostApiV4BulkImportsRequestBody

# Operation: list_jobs
class ListProjectJobsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded project path (e.g., group/subgroup/project).")
class ListProjectJobsRequestQuery(StrictModel):
    scope: list[str] | None = Field(default=None, description="Filter results to include only jobs with the specified statuses. Provide as an array of status values; order is not significant.")
class ListProjectJobsRequest(StrictModel):
    """Retrieve all jobs for a specified project, with optional filtering by job status. Use this to monitor job execution, track pipeline progress, or retrieve job details."""
    path: ListProjectJobsRequestPath
    query: ListProjectJobsRequestQuery | None = None

# Operation: get_job
class GetSingleJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, which can be a numeric ID or URL-encoded project path (e.g., group/subgroup/project).")
    job_id: int = Field(default=..., description="The numeric identifier of the job to retrieve.")
class GetSingleJobRequest(StrictModel):
    """Retrieve details for a specific job within a project. Returns comprehensive job information including status, logs, and execution details."""
    path: GetSingleJobRequestPath

# Operation: execute_manual_job
class TriggerManualJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project).")
    job_id: int = Field(default=..., description="The numeric ID of the manual job to execute.")
class TriggerManualJobRequestQuery(StrictModel):
    job_variables_attributes: list[str] | None = Field(default=None, description="Optional array of custom variables to make available to the job during execution. Variables are applied in the order provided.")
class TriggerManualJobRequest(StrictModel):
    """Execute a manual job for a project. Optionally provide custom variables to override job defaults during execution."""
    path: TriggerManualJobRequestPath
    query: TriggerManualJobRequestQuery | None = None

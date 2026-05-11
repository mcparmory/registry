"""
Bitbucket MCP Server - Pydantic Models

Generated: 2026-05-11 23:09:02 UTC
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
    "DeleteRepositoriesBranchRestrictionsRequest",
    "DeleteRepositoriesCommitApproveRequest",
    "DeleteRepositoriesCommitCommentsRequest",
    "DeleteRepositoriesCommitPropertiesRequest",
    "DeleteRepositoriesCommitReportsAnnotationsRequest",
    "DeleteRepositoriesCommitReportsRequest",
    "DeleteRepositoriesDefaultReviewersRequest",
    "DeleteRepositoriesDeployKeysRequest",
    "DeleteRepositoriesDeploymentsConfigEnvironmentsVariablesRequest",
    "DeleteRepositoriesDownloadsRequest",
    "DeleteRepositoriesEnvironmentsRequest",
    "DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesForCacheUuidRequest",
    "DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequest",
    "DeleteRepositoriesHooksRequest",
    "DeleteRepositoriesPermissionsConfigUsersRequest",
    "DeleteRepositoriesPipelinesConfigRunnersRequest",
    "DeleteRepositoriesPipelinesConfigSchedulesRequest",
    "DeleteRepositoriesPipelinesConfigSshKeyPairRequest",
    "DeleteRepositoriesPipelinesConfigSshKnownHostsRequest",
    "DeleteRepositoriesPipelinesConfigVariablesRequest",
    "DeleteRepositoriesPropertiesRequest",
    "DeleteRepositoriesPullrequestsApproveRequest",
    "DeleteRepositoriesPullrequestsCommentsRequest",
    "DeleteRepositoriesPullrequestsCommentsResolveRequest",
    "DeleteRepositoriesPullrequestsPropertiesRequest",
    "DeleteRepositoriesPullrequestsRequestChangesRequest",
    "DeleteRepositoriesPullrequestsTasksRequest",
    "DeleteRepositoriesRefsBranchesRequest",
    "DeleteRepositoriesRefsTagsRequest",
    "DeleteRepositoriesRequest",
    "DeleteSnippetsCommentsRequest",
    "DeleteSnippetsForWorkspaceForEncodedIdForNodeIdRequest",
    "DeleteSnippetsForWorkspaceForEncodedIdRequest",
    "DeleteSnippetsWatchRequest",
    "DeleteUsersGpgKeysRequest",
    "DeleteUsersPropertiesRequest",
    "DeleteUsersSshKeysRequest",
    "DeleteWorkspacesHooksRequest",
    "DeleteWorkspacesPipelinesConfigRunnersRequest",
    "DeleteWorkspacesPipelinesConfigVariablesRequest",
    "DeleteWorkspacesProjectsDefaultReviewersRequest",
    "DeleteWorkspacesProjectsDeployKeysRequest",
    "DeleteWorkspacesProjectsRequest",
    "GetHookEventsBySubjectTypeRequest",
    "GetRepositoriesBranchingModelRequest",
    "GetRepositoriesBranchingModelSettingsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsByIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsByCommentIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsByAnnotationIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitsByRevisionRequest",
    "GetRepositoriesByWorkspaceByRepoSlugCommitsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersByTargetUsernameRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDeployKeysByKeyIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDeployKeysRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDeploymentsByDeploymentUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDeploymentsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDownloadsByFilenameRequest",
    "GetRepositoriesByWorkspaceByRepoSlugDownloadsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugEnvironmentsByEnvironmentUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugEnvironmentsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugHooksByUidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugHooksRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsByGroupSlugRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersBySelectedUserIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsByStepUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersByRunnerUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesByScheduleUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsByKnownHostUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesByVariableUuidRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPipelinesRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsActivityRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdActivityRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsByCommentIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksByTaskIdRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequest",
    "GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugRefsBranchesByNameRequest",
    "GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequest",
    "GetRepositoriesByWorkspaceByRepoSlugRefsTagsByNameRequest",
    "GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequest",
    "GetRepositoriesByWorkspaceByRepoSlugRequest",
    "GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequest",
    "GetRepositoriesByWorkspaceByRepoSlugSrcRequest",
    "GetRepositoriesByWorkspaceRequest",
    "GetRepositoriesCommitPropertiesRequest",
    "GetRepositoriesCommitPullrequestsRequest",
    "GetRepositoriesCommitRequest",
    "GetRepositoriesCommitStatusesBuildRequest",
    "GetRepositoriesCommitStatusesRequest",
    "GetRepositoriesDeploymentsConfigEnvironmentsVariablesRequest",
    "GetRepositoriesDiffRequest",
    "GetRepositoriesDiffstatRequest",
    "GetRepositoriesEffectiveBranchingModelRequest",
    "GetRepositoriesEffectiveDefaultReviewersRequest",
    "GetRepositoriesFilehistoryRequest",
    "GetRepositoriesForksRequest",
    "GetRepositoriesMergeBaseRequest",
    "GetRepositoriesOverrideSettingsRequest",
    "GetRepositoriesPatchRequest",
    "GetRepositoriesPipelinesConfigCachesContentUriRequest",
    "GetRepositoriesPipelinesConfigCachesRequest",
    "GetRepositoriesPipelinesConfigRequest",
    "GetRepositoriesPipelinesConfigSchedulesExecutionsRequest",
    "GetRepositoriesPipelinesConfigSshKeyPairRequest",
    "GetRepositoriesPipelinesStepsLogRequest",
    "GetRepositoriesPipelinesStepsLogsRequest",
    "GetRepositoriesPipelinesStepsTestReportsRequest",
    "GetRepositoriesPipelinesStepsTestReportsTestCasesRequest",
    "GetRepositoriesPipelinesStepsTestReportsTestCasesTestCaseReasonsRequest",
    "GetRepositoriesPropertiesRequest",
    "GetRepositoriesPullrequestsCommitsRequest",
    "GetRepositoriesPullrequestsDiffRequest",
    "GetRepositoriesPullrequestsDiffstatRequest",
    "GetRepositoriesPullrequestsMergeTaskStatusRequest",
    "GetRepositoriesPullrequestsPatchRequest",
    "GetRepositoriesPullrequestsPropertiesRequest",
    "GetRepositoriesPullrequestsStatusesRequest",
    "GetRepositoriesRefsRequest",
    "GetRepositoriesWatchersRequest",
    "GetSnippetsByWorkspaceByEncodedIdByNodeIdFilesByPathRequest",
    "GetSnippetsByWorkspaceByEncodedIdByNodeIdRequest",
    "GetSnippetsByWorkspaceByEncodedIdCommentsByCommentIdRequest",
    "GetSnippetsByWorkspaceByEncodedIdCommentsRequest",
    "GetSnippetsByWorkspaceByEncodedIdCommitsByRevisionRequest",
    "GetSnippetsByWorkspaceByEncodedIdCommitsRequest",
    "GetSnippetsByWorkspaceByEncodedIdFilesByPathRequest",
    "GetSnippetsByWorkspaceByEncodedIdRequest",
    "GetSnippetsByWorkspaceRequest",
    "GetSnippetsDiffRequest",
    "GetSnippetsPatchRequest",
    "GetSnippetsWatchRequest",
    "GetTeamsSearchCodeRequest",
    "GetUserEmailsByEmailRequest",
    "GetUsersBySelectedUserGpgKeysByFingerprintRequest",
    "GetUsersBySelectedUserGpgKeysRequest",
    "GetUsersBySelectedUserSshKeysByKeyIdRequest",
    "GetUsersBySelectedUserSshKeysRequest",
    "GetUsersPropertiesRequest",
    "GetUsersRequest",
    "GetUsersSearchCodeRequest",
    "GetUserWorkspacesPermissionRequest",
    "GetUserWorkspacesPermissionsRepositoriesRequest",
    "GetUserWorkspacesRequest",
    "GetWorkspacesByWorkspaceHooksByUidRequest",
    "GetWorkspacesByWorkspaceHooksRequest",
    "GetWorkspacesByWorkspaceMembersByMemberRequest",
    "GetWorkspacesByWorkspaceMembersRequest",
    "GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequest",
    "GetWorkspacesByWorkspacePermissionsRepositoriesRequest",
    "GetWorkspacesByWorkspacePipelinesConfigRunnersByRunnerUuidRequest",
    "GetWorkspacesByWorkspacePipelinesConfigRunnersRequest",
    "GetWorkspacesByWorkspacePipelinesConfigVariablesByVariableUuidRequest",
    "GetWorkspacesByWorkspacePipelinesConfigVariablesRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersBySelectedUserRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysByKeyIdRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigGroupsRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigUsersRequest",
    "GetWorkspacesByWorkspaceProjectsByProjectKeyRequest",
    "GetWorkspacesByWorkspaceProjectsRequest",
    "GetWorkspacesByWorkspaceRequest",
    "GetWorkspacesPermissionsRequest",
    "GetWorkspacesProjectsBranchingModelRequest",
    "GetWorkspacesProjectsBranchingModelSettingsRequest",
    "GetWorkspacesPullrequestsRequest",
    "GetWorkspacesSearchCodeRequest",
    "PostRepositoriesBranchRestrictionsRequest",
    "PostRepositoriesCommitApproveRequest",
    "PostRepositoriesCommitCommentsRequest",
    "PostRepositoriesCommitReportsAnnotationsRequest",
    "PostRepositoriesCommitStatusesBuildRequest",
    "PostRepositoriesDeployKeysRequest",
    "PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequest",
    "PostRepositoriesDownloadsRequest",
    "PostRepositoriesEnvironmentsChangesRequest",
    "PostRepositoriesEnvironmentsRequest",
    "PostRepositoriesForksRequest",
    "PostRepositoriesForWorkspaceForRepoSlugCommitsForRevisionRequest",
    "PostRepositoriesForWorkspaceForRepoSlugCommitsRequest",
    "PostRepositoriesPipelinesConfigRunnersRequest",
    "PostRepositoriesPipelinesConfigSchedulesRequest",
    "PostRepositoriesPipelinesConfigSshKnownHostsRequest",
    "PostRepositoriesPipelinesConfigVariablesRequest",
    "PostRepositoriesPipelinesRequest",
    "PostRepositoriesPipelinesStopPipelineRequest",
    "PostRepositoriesPullrequestsApproveRequest",
    "PostRepositoriesPullrequestsCommentsRequest",
    "PostRepositoriesPullrequestsCommentsResolveRequest",
    "PostRepositoriesPullrequestsDeclineRequest",
    "PostRepositoriesPullrequestsMergeRequest",
    "PostRepositoriesPullrequestsRequest",
    "PostRepositoriesPullrequestsRequestChangesRequest",
    "PostRepositoriesPullrequestsTasksRequest",
    "PostRepositoriesRefsBranchesRequest",
    "PostRepositoriesRefsTagsRequest",
    "PostRepositoriesRequest",
    "PostRepositoriesSrcRequest",
    "PostSnippetsCommentsRequest",
    "PostSnippetsForWorkspaceRequest",
    "PostUsersGpgKeysRequest",
    "PostUsersSshKeysRequest",
    "PostWorkspacesPipelinesConfigRunnersRequest",
    "PostWorkspacesPipelinesConfigVariablesRequest",
    "PostWorkspacesProjectsDeployKeysRequest",
    "PostWorkspacesProjectsRequest",
    "PutRepositoriesBranchingModelSettingsRequest",
    "PutRepositoriesBranchRestrictionsRequest",
    "PutRepositoriesCommitCommentsRequest",
    "PutRepositoriesCommitPropertiesRequest",
    "PutRepositoriesCommitReportsAnnotationsRequest",
    "PutRepositoriesCommitReportsRequest",
    "PutRepositoriesCommitStatusesBuildRequest",
    "PutRepositoriesDefaultReviewersRequest",
    "PutRepositoriesDeployKeysRequest",
    "PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequest",
    "PutRepositoriesHooksRequest",
    "PutRepositoriesOverrideSettingsRequest",
    "PutRepositoriesPipelinesConfigBuildNumberRequest",
    "PutRepositoriesPipelinesConfigRunnersRequest",
    "PutRepositoriesPipelinesConfigSchedulesRequest",
    "PutRepositoriesPipelinesConfigSshKeyPairRequest",
    "PutRepositoriesPipelinesConfigSshKnownHostsRequest",
    "PutRepositoriesPipelinesConfigVariablesRequest",
    "PutRepositoriesPropertiesRequest",
    "PutRepositoriesPullrequestsCommentsRequest",
    "PutRepositoriesPullrequestsPropertiesRequest",
    "PutRepositoriesPullrequestsRequest",
    "PutRepositoriesPullrequestsTasksRequest",
    "PutRepositoriesRequest",
    "PutSnippetsCommentsRequest",
    "PutSnippetsForWorkspaceForEncodedIdForNodeIdRequest",
    "PutSnippetsForWorkspaceForEncodedIdRequest",
    "PutSnippetsWatchRequest",
    "PutUsersPropertiesRequest",
    "PutUsersSshKeysRequest",
    "PutWorkspacesHooksRequest",
    "PutWorkspacesPipelinesConfigRunnersRequest",
    "PutWorkspacesPipelinesConfigVariablesRequest",
    "PutWorkspacesProjectsDefaultReviewersRequest",
    "PutWorkspacesProjectsRequest",
    "Branchrestriction",
    "CommitComment",
    "Commitstatus",
    "GpgAccountKey",
    "PostRepositoriesDeploymentsConfigEnvironmentsVariablesBody",
    "PostRepositoriesEnvironmentsBody",
    "PostRepositoriesPipelinesBody",
    "PostRepositoriesPipelinesConfigSchedulesBody",
    "PostRepositoriesPipelinesConfigSshKnownHostsBody",
    "PostRepositoriesPipelinesConfigVariablesBody",
    "PostRepositoriesPullrequestsTasksBodyComment",
    "Pullrequest",
    "PullrequestComment",
    "PutRepositoriesCommitReportsAnnotationsBody",
    "PutRepositoriesCommitReportsBody",
    "PutRepositoriesDeploymentsConfigEnvironmentsVariablesBody",
    "PutRepositoriesPipelinesConfigBuildNumberBody",
    "PutRepositoriesPipelinesConfigSchedulesBody",
    "PutRepositoriesPipelinesConfigSshKeyPairBody",
    "PutRepositoriesPipelinesConfigSshKnownHostsBody",
    "PutRepositoriesPipelinesConfigVariablesBody",
    "ReportAnnotation",
    "Repository",
    "SnippetComment",
    "SshAccountKey",
    "Tag",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_webhook_event_types_by_subject
class GetHookEventsBySubjectTypeRequestPath(StrictModel):
    subject_type: Literal["repository", "workspace"] = Field(default=..., description="The entity type for which to retrieve subscribable webhook events. Note: team and user subject types are deprecated; use workspace instead.")
class GetHookEventsBySubjectTypeRequest(StrictModel):
    """Retrieves a paginated list of all valid webhook event types available for subscription on a given subject type (repository or workspace). This is public data requiring no authentication or scopes."""
    path: GetHookEventsBySubjectTypeRequestPath

# Operation: list_workspace_repositories
class GetRepositoriesByWorkspaceRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
class GetRepositoriesByWorkspaceRequestQuery(StrictModel):
    role: Literal["admin", "contributor", "member", "owner"] | None = Field(default=None, description="Filters repositories based on the authenticated user's access level: member (read access), contributor (write access), admin (administrator access), or owner (all repositories owned by the user).")
    q: str | None = Field(default=None, description="A query string to filter repositories using Bitbucket's filtering syntax, allowing you to narrow results by repository properties.")
    sort: str | None = Field(default=None, description="The field name by which to sort the returned repositories, following Bitbucket's sorting syntax for ordering results.")
class GetRepositoriesByWorkspaceRequest(StrictModel):
    """Retrieves a paginated list of all repositories within a specified workspace. Results can be filtered by the authenticated user's role and further narrowed using query and sort parameters."""
    path: GetRepositoriesByWorkspaceRequestPath
    query: GetRepositoriesByWorkspaceRequestQuery | None = None

# Operation: get_repository
class GetRepositoriesByWorkspaceByRepoSlugRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugRequest(StrictModel):
    """Retrieves detailed metadata for a specific repository within a workspace. Returns the full repository object including settings, links, and configuration."""
    path: GetRepositoriesByWorkspaceByRepoSlugRequestPath

# Operation: create_repository
class PostRepositoriesRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The slug or UUID of the repository to create. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID in which to create the repository. UUIDs must be surrounded by curly-braces.")
class PostRepositoriesRequestBody(StrictModel):
    """The repository that is to be created. Note that most object elements are optional. Elements "owner" and "full_name" are ignored as the URL implies them."""
    body: Repository | None = Field(default=None, description="Optional request body containing repository configuration such as SCM type and project assignment. If no project is specified, the repository is automatically assigned to the oldest project in the workspace.")
class PostRepositoriesRequest(StrictModel):
    """Creates a new repository in the specified workspace. Optionally assigns the repository to a project by providing a project key or UUID in the request body."""
    path: PostRepositoriesRequestPath
    body: PostRepositoriesRequestBody | None = None

# Operation: update_repository
class PutRepositoriesRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The slug or UUID of the repository to update. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID containing the repository. UUIDs must be surrounded by curly-braces.")
class PutRepositoriesRequestBody(StrictModel):
    """The repository that is to be updated.

Note that the elements "owner" and "full_name" are ignored since the
URL implies them.
"""
    body: Repository | None = Field(default=None, description="The repository fields to update, such as name, description, or visibility settings. Refer to the repository POST endpoint documentation for the full request body structure.")
class PutRepositoriesRequest(StrictModel):
    """Updates an existing repository's settings and metadata within a workspace, or creates one if it does not exist. Renaming the repository will change its URL slug and return the new location in the response's Location header if no slug conflict occurs."""
    path: PutRepositoriesRequestPath
    body: PutRepositoriesRequestBody | None = None

# Operation: delete_repository
class DeleteRepositoriesRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository to delete. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class DeleteRepositoriesRequestQuery(StrictModel):
    redirect_to: str | None = Field(default=None, description="An optional redirect path to display a friendly relocation message in the Bitbucket UI when a repository has moved. Note that GET requests to the original endpoint will still return a 404 regardless.")
class DeleteRepositoriesRequest(StrictModel):
    """Permanently deletes the specified repository from a workspace. This action is irreversible and does not affect any existing forks of the repository."""
    path: DeleteRepositoriesRequestPath
    query: DeleteRepositoriesRequestQuery | None = None

# Operation: list_branch_restrictions
class GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequestQuery(StrictModel):
    kind: str | None = Field(default=None, description="Filters results to only return branch restrictions of the specified type, such as push or merge restrictions.")
    pattern: str | None = Field(default=None, description="Filters results to only return branch restrictions that apply to branches matching the specified pattern.")
class GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequest(StrictModel):
    """Retrieves a paginated list of all branch restrictions configured for a repository. Optionally filter results by restriction kind or branch name pattern."""
    path: GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequestQuery | None = None

# Operation: create_branch_restriction
class PostRepositoriesBranchRestrictionsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesBranchRestrictionsRequestBody(StrictModel):
    """The new rule"""
    body: Branchrestriction | None = Field(default=None, description="The branch restriction rule definition, including the restriction kind, branch matching strategy (glob pattern or branching model type), and optionally the users and groups exempt from the restriction.")
class PostRepositoriesBranchRestrictionsRequest(StrictModel):
    """Creates a new branch restriction rule for a repository, controlling actions such as pushing, merging, or deleting branches based on matching patterns or branching model types."""
    path: PostRepositoriesBranchRestrictionsRequestPath
    body: PostRepositoriesBranchRestrictionsRequestBody | None = None

# Operation: get_branch_restriction
class GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the branch restriction rule to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsByIdRequest(StrictModel):
    """Retrieves a specific branch restriction rule for a repository by its unique ID. Use this to inspect the configuration of an individual branch protection or access control rule."""
    path: GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsByIdRequestPath

# Operation: update_branch_restriction
class PutRepositoriesBranchRestrictionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the branch restriction rule to update.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace. UUID values must be surrounded by curly-braces.")
class PutRepositoriesBranchRestrictionsRequestBody(StrictModel):
    """The new version of the existing rule"""
    body: Branchrestriction | None = Field(default=None, description="The request body containing the branch restriction rule fields to update. Only fields present in the body will be modified.")
class PutRepositoriesBranchRestrictionsRequest(StrictModel):
    """Updates an existing branch restriction rule for a repository. Only fields included in the request body are modified; omitted fields retain their current values."""
    path: PutRepositoriesBranchRestrictionsRequestPath
    body: PutRepositoriesBranchRestrictionsRequestBody | None = None

# Operation: delete_branch_restriction
class DeleteRepositoriesBranchRestrictionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the branch restriction rule to delete.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class DeleteRepositoriesBranchRestrictionsRequest(StrictModel):
    """Permanently deletes an existing branch restriction rule from a repository. This action cannot be undone and will immediately remove the associated access or push controls."""
    path: DeleteRepositoriesBranchRestrictionsRequestPath

# Operation: get_branching_model
class GetRepositoriesBranchingModelRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either the URL-friendly slug or the repository UUID enclosed in curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug or the workspace UUID enclosed in curly-braces.")
class GetRepositoriesBranchingModelRequest(StrictModel):
    """Retrieves the active branching model for a repository, including the development branch, optional production branch, and all enabled branch types. This is a read-only view; use the branching model settings endpoint to modify the configuration."""
    path: GetRepositoriesBranchingModelRequestPath

# Operation: get_branching_model_settings
class GetRepositoriesBranchingModelSettingsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository whose branching model settings are being retrieved. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesBranchingModelSettingsRequest(StrictModel):
    """Retrieves the raw branching model configuration for a repository, including development and production branch settings, branch type definitions, and default branch deletion behavior. Use the active branching model endpoint instead if you need to see the configuration resolved against actual current branches."""
    path: GetRepositoriesBranchingModelSettingsRequestPath

# Operation: update_branching_model_settings
class PutRepositoriesBranchingModelSettingsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class PutRepositoriesBranchingModelSettingsRequest(StrictModel):
    """Updates the branching model configuration for a repository, including development branch, production branch, branch type prefixes, and default branch deletion behavior. Only properties explicitly passed in the request body will be modified; omitted properties remain unchanged."""
    path: PutRepositoriesBranchingModelSettingsRequestPath

# Operation: get_commit
class GetRepositoriesCommitRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesCommitRequest(StrictModel):
    """Retrieves details for a specific commit in a repository using its SHA1 identifier. Returns commit metadata including author, timestamp, and associated changes."""
    path: GetRepositoriesCommitRequestPath

# Operation: approve_commit
class PostRepositoriesCommitApproveRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash identifying the specific commit to approve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository containing the commit. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class PostRepositoriesCommitApproveRequest(StrictModel):
    """Approves a specific commit as the authenticated user, recording their explicit approval. Requires the user to have direct access to the repository, as public visibility alone does not grant approval permissions."""
    path: PostRepositoriesCommitApproveRequestPath

# Operation: unapprove_commit
class DeleteRepositoriesCommitApproveRequestPath(StrictModel):
    commit: str = Field(default=..., description="The SHA1 hash uniquely identifying the commit to unapprove.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that contains the commit.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that owns the repository.")
class DeleteRepositoriesCommitApproveRequest(StrictModel):
    """Removes the authenticated user's approval from a specified commit in a repository. This action requires explicit access to the repository; public visibility alone does not grant approval or unapproval rights."""
    path: DeleteRepositoriesCommitApproveRequestPath

# Operation: list_commit_comments
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash identifying the specific commit whose comments should be retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID that uniquely identifies the repository within the workspace. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID that uniquely identifies the workspace containing the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A query string to filter the returned comments using Bitbucket's filtering and sorting syntax, allowing you to narrow results by specific field conditions.")
    sort: str | None = Field(default=None, description="The field name by which to sort the returned comments, following Bitbucket's filtering and sorting syntax. Overrides the default oldest-to-newest ordering.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequest(StrictModel):
    """Retrieves all comments (both global and inline) for a specific commit in a repository. Results are sorted oldest to newest by default and can be filtered or reordered using query parameters."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequestQuery | None = None

# Operation: create_commit_comment
class PostRepositoriesCommitCommentsRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit to comment on.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that identifies the repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that identifies the workspace containing the repository.")
class PostRepositoriesCommitCommentsRequestBody(StrictModel):
    """The specified comment."""
    body: CommitComment | None = Field(default=None, description="The comment payload, including the comment content and an optional parent comment ID to post a reply in an existing thread.")
class PostRepositoriesCommitCommentsRequest(StrictModel):
    """Posts a new comment on a specific commit in a repository. Supports threaded replies by referencing a parent comment ID in the request body."""
    path: PostRepositoriesCommitCommentsRequestPath
    body: PostRepositoriesCommitCommentsRequestBody | None = None

# Operation: get_commit_comment
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsByCommentIdRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the commit comment to retrieve.", json_schema_extra={'format': 'int64'})
    commit: str = Field(default=..., description="The full SHA1 hash of the commit whose comment is being retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug (URL-friendly identifier) or the workspace UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsByCommentIdRequest(StrictModel):
    """Retrieves a specific comment on a commit by its comment ID. Returns the full comment details including content, author, and timestamps."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsByCommentIdRequestPath

# Operation: update_commit_comment
class PutRepositoriesCommitCommentsRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to update.", json_schema_extra={'format': 'int64'})
    commit: str = Field(default=..., description="The full SHA1 hash of the commit that the comment belongs to.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that uniquely identifies the workspace containing the repository.")
class PutRepositoriesCommitCommentsRequestBody(StrictModel):
    """The updated comment."""
    body: CommitComment | None = Field(default=None, description="The request body containing the updated comment content, structured as a commit comment object with a raw text content field.")
class PutRepositoriesCommitCommentsRequest(StrictModel):
    """Updates the text content of an existing comment on a specific commit. Only the comment's content can be modified; other properties remain unchanged."""
    path: PutRepositoriesCommitCommentsRequestPath
    body: PutRepositoriesCommitCommentsRequestBody | None = None

# Operation: delete_commit_comment
class DeleteRepositoriesCommitCommentsRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the commit comment to delete.", json_schema_extra={'format': 'int64'})
    commit: str = Field(default=..., description="The full SHA1 hash of the commit whose comment is being deleted.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class DeleteRepositoriesCommitCommentsRequest(StrictModel):
    """Deletes a specific comment on a commit in a repository. If the comment has visible replies, it will be soft-deleted — its content is blanked and marked as deleted — to preserve the integrity of the comment thread."""
    path: DeleteRepositoriesCommitCommentsRequestPath

# Operation: get_commit_property
class GetRepositoriesCommitPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces).")
    repo_slug: str = Field(default=..., description="The slug of the repository where the commit resides.")
    commit: str = Field(default=..., description="The identifier of the commit whose application property is being retrieved.")
    app_key: str = Field(default=..., description="The unique key identifying the Connect app that owns the property.")
    property_name: str = Field(default=..., description="The name of the application property to retrieve from the specified commit.")
class GetRepositoriesCommitPropertiesRequest(StrictModel):
    """Retrieves a specific application property value stored against a commit in a Bitbucket repository. Useful for reading custom metadata attached to a commit by a Connect app."""
    path: GetRepositoriesCommitPropertiesRequestPath

# Operation: update_commit_property
class PutRepositoriesCommitPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace that contains the repository, identified by its slug or UUID (UUID must be wrapped in curly braces).")
    repo_slug: str = Field(default=..., description="The slug of the repository where the commit resides.")
    commit: str = Field(default=..., description="The commit identifier (hash) against which the application property is stored.")
    app_key: str = Field(default=..., description="The unique key identifying the Connect app that owns the property.")
    property_name: str = Field(default=..., description="The name of the application property to update, scoped to the specified Connect app.")
class PutRepositoriesCommitPropertiesRequest(StrictModel):
    """Update the value of an application property stored against a specific commit in a repository. Application properties allow Connect apps to associate custom metadata with Bitbucket resources."""
    path: PutRepositoriesCommitPropertiesRequestPath

# Operation: delete_commit_property
class DeleteRepositoriesCommitPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, specified as either the workspace slug or the workspace UUID wrapped in curly braces.")
    repo_slug: str = Field(default=..., description="The slug identifier of the repository from which the commit property will be deleted.")
    commit: str = Field(default=..., description="The commit identifier (hash) whose associated application property will be deleted.")
    app_key: str = Field(default=..., description="The unique key identifying the Bitbucket Connect app that owns the property being deleted.")
    property_name: str = Field(default=..., description="The name of the application property to delete from the specified commit.")
class DeleteRepositoriesCommitPropertiesRequest(StrictModel):
    """Deletes a specific application property value stored against a commit in a Bitbucket repository. This permanently removes the key-value metadata associated with the given Connect app and property name."""
    path: DeleteRepositoriesCommitPropertiesRequestPath

# Operation: list_commit_pull_requests
class GetRepositoriesCommitPullrequestsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug or the UUID enclosed in curly braces.")
    repo_slug: str = Field(default=..., description="The repository identifier, either the repository slug or the UUID enclosed in curly braces.")
    commit: str = Field(default=..., description="The full SHA1 hash of the commit whose associated pull requests should be retrieved.")
class GetRepositoriesCommitPullrequestsRequestQuery(StrictModel):
    pagelen: int | None = Field(default=None, description="The number of pull requests to return per page; controls pagination page size.", json_schema_extra={'format': 'int32'})
class GetRepositoriesCommitPullrequestsRequest(StrictModel):
    """Retrieves a paginated list of all pull requests that include a specific commit as part of their review. Requires the Pull Request Commit Links app to be installed on the repository."""
    path: GetRepositoriesCommitPullrequestsRequestPath
    query: GetRepositoriesCommitPullrequestsRequestQuery | None = None

# Operation: list_commit_reports
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    commit: str = Field(default=..., description="The full commit hash identifying the specific commit whose reports should be retrieved.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsRequest(StrictModel):
    """Retrieves a paginated list of code insight reports linked to a specific commit in a repository. Useful for reviewing quality, security, or test results associated with a given commit."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsRequestPath

# Operation: get_commit_report
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the commit and report.")
    commit: str = Field(default=..., description="The full commit hash identifying the specific commit the report is associated with.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the report, accepted as either a UUID or an external ID assigned by the reporting tool.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdRequest(StrictModel):
    """Retrieves a single code insight report for a specific commit in a repository. Returns the full report details matching the provided report ID."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdRequestPath

# Operation: create_or_update_commit_report
class PutRepositoriesCommitReportsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier — either the slug (short name) or the UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the target commit.")
    commit: str = Field(default=..., description="The full commit hash that this report is associated with.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="A unique identifier for the report scoped to this commit — either a UUID or an external ID. To avoid collisions with other systems, prefix external IDs with your system name (e.g., mySystem-001).")
class PutRepositoriesCommitReportsRequestBody(StrictModel):
    """The report to create or update"""
    body: PutRepositoriesCommitReportsBody | None = Field(default=None, description="The report payload containing metadata and result data. Supports fields: title, details, report_type (SECURITY, COVERAGE, TEST, BUG), reporter, link, result (PASSED, FAILED, PENDING), and a data array of typed metric entries. Each data entry specifies a title, type (BOOLEAN, DATE, DURATION, LINK, NUMBER, PERCENTAGE, TEXT), and a value whose format depends on the type — see the data field format table for type-specific value requirements.")
class PutRepositoriesCommitReportsRequest(StrictModel):
    """Creates or updates a Code Insights report for a specific commit in a repository. Use a unique report ID per commit, optionally prefixed with your system name to avoid collisions."""
    path: PutRepositoriesCommitReportsRequestPath
    body: PutRepositoriesCommitReportsRequestBody | None = None

# Operation: delete_commit_report
class DeleteRepositoriesCommitReportsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the commit and its associated report.")
    commit: str = Field(default=..., description="The full commit hash identifying the commit to which the report belongs.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the report to delete, accepted as either the report's UUID or its external ID.")
class DeleteRepositoriesCommitReportsRequest(StrictModel):
    """Deletes a single code insights report associated with a specific commit in a repository. The report is identified by its unique report ID."""
    path: DeleteRepositoriesCommitReportsRequestPath

# Operation: list_commit_report_annotations
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    commit: str = Field(default=..., description="The full commit hash identifying the specific commit whose report annotations should be retrieved.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the report, accepted as either a UUID or an external ID, for which annotations will be listed.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsRequest(StrictModel):
    """Retrieves a paginated list of annotations associated with a specific code insights report for a given commit in a repository."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsRequestPath

# Operation: bulk_create_annotations
class PostRepositoriesCommitReportsAnnotationsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g., my-team) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the workspace.")
    commit: str = Field(default=..., description="The full commit hash for which the report and its annotations are being uploaded.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The UUID or external ID of the report to which these annotations belong.")
class PostRepositoriesCommitReportsAnnotationsRequestBody(StrictModel):
    """The annotations to create or update"""
    body: list[ReportAnnotation] | None = Field(default=None, description="Array of annotation objects to create or update. Each annotation must include a unique external_id and may specify fields such as annotation_type (VULNERABILITY, CODE_SMELL, BUG), severity (CRITICAL, HIGH, MEDIUM, LOW), result (PASSED, FAILED, IGNORED, SKIPPED), and an optional file path and line number. Up to 100 annotations can be submitted per request.", min_length=1, max_length=100)
class PostRepositoriesCommitReportsAnnotationsRequest(StrictModel):
    """Bulk create or update up to 100 annotations for a specific commit report in a repository. Annotations represent individual findings (e.g., vulnerabilities, bugs, code smells) and can be optionally linked to a specific file and line number."""
    path: PostRepositoriesCommitReportsAnnotationsRequestPath
    body: PostRepositoriesCommitReportsAnnotationsRequestBody | None = None

# Operation: get_commit_report_annotation
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsByAnnotationIdRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The URL-friendly slug of the repository within the specified workspace.")
    commit: str = Field(default=..., description="The full commit hash identifying the commit to which the report belongs.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the report, accepted as either its UUID or its external ID string.")
    annotation_id: str = Field(default=..., validation_alias="annotationId", serialization_alias="annotationId", description="The unique identifier of the annotation to retrieve, accepted as either its UUID or its external ID string.")
class GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsByAnnotationIdRequest(StrictModel):
    """Retrieves a single annotation by its ID from a specific code insight report on a given commit. Useful for inspecting individual findings or diagnostics attached to a commit report."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsByAnnotationIdRequestPath

# Operation: upsert_commit_report_annotation
class PutRepositoriesCommitReportsAnnotationsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug or the UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the workspace.")
    commit: str = Field(default=..., description="The full commit hash that the report and annotation belong to.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the report to annotate, either its UUID or the external ID used when the report was created.")
    annotation_id: str = Field(default=..., validation_alias="annotationId", serialization_alias="annotationId", description="The unique identifier for this annotation, either its UUID or an external ID; prefix external IDs with your system name to avoid collisions.")
class PutRepositoriesCommitReportsAnnotationsRequestBody(StrictModel):
    """The annotation to create or update"""
    body: PutRepositoriesCommitReportsAnnotationsBody | None = Field(default=None, description="The annotation payload containing fields such as title, summary, annotation_type (VULNERABILITY, CODE_SMELL, BUG), severity (CRITICAL, HIGH, MEDIUM, LOW), result (PASSED, FAILED, IGNORED, SKIPPED), and optional file path and line number.")
class PutRepositoriesCommitReportsAnnotationsRequest(StrictModel):
    """Creates or updates a single annotation on a specific commit report, representing an individual finding such as a vulnerability, bug, or code smell, optionally linked to a file and line number."""
    path: PutRepositoriesCommitReportsAnnotationsRequestPath
    body: PutRepositoriesCommitReportsAnnotationsRequestBody | None = None

# Operation: delete_commit_annotation
class DeleteRepositoriesCommitReportsAnnotationsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the workspace.")
    commit: str = Field(default=..., description="The commit hash or identifier that the target annotation belongs to.")
    report_id: str = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the report containing the annotation, either its UUID or external ID.")
    annotation_id: str = Field(default=..., validation_alias="annotationId", serialization_alias="annotationId", description="The unique identifier of the annotation to delete, either its UUID or external ID.")
class DeleteRepositoriesCommitReportsAnnotationsRequest(StrictModel):
    """Deletes a single annotation from a specific commit report in a repository. The annotation is identified by its unique ID within the specified report."""
    path: DeleteRepositoriesCommitReportsAnnotationsRequestPath

# Operation: list_commit_statuses
class GetRepositoriesCommitStatusesRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit whose statuses you want to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesCommitStatusesRequestQuery(StrictModel):
    refname: str | None = Field(default=None, description="Filters results to only include commit statuses created with the specified ref name, or those created without any ref name.")
    q: str | None = Field(default=None, description="A query string to filter results using Bitbucket's filtering and sorting syntax, allowing you to narrow the returned statuses by field values.")
    sort: str | None = Field(default=None, description="The field by which to sort the returned statuses using Bitbucket's filtering and sorting syntax. Defaults to created_on if not specified.")
class GetRepositoriesCommitStatusesRequest(StrictModel):
    """Retrieves all statuses (such as CI/CD build results) associated with a specific commit in a Bitbucket repository. Supports filtering by ref name, query string, and custom sorting."""
    path: GetRepositoriesCommitStatusesRequestPath
    query: GetRepositoriesCommitStatusesRequestQuery | None = None

# Operation: create_commit_build_status
class PostRepositoriesCommitStatusesBuildRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit to attach the build status to.")
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (e.g. my-repo) or as a UUID surrounded by curly braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g. my-workspace) or as a UUID surrounded by curly braces.")
class PostRepositoriesCommitStatusesBuildRequestBody(StrictModel):
    """The new commit status object."""
    body: Commitstatus | None = Field(default=None, description="The build status payload containing fields such as key, state, description, url, and optionally refname. The key uniquely identifies the build status; if it already exists, the existing record will be overwritten. Set refname to the pull request source branch to associate the status with a pull request. The url field supports URI templates with context variables repository and commit.")
class PostRepositoriesCommitStatusesBuildRequest(StrictModel):
    """Creates or overwrites a build status for a specific commit in a repository, allowing CI/CD systems to report build results. Optionally associate the status with a pull request by specifying the source branch via the refname field."""
    path: PostRepositoriesCommitStatusesBuildRequestPath
    body: PostRepositoriesCommitStatusesBuildRequestBody | None = None

# Operation: get_commit_build_status
class GetRepositoriesCommitStatusesBuildRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit whose build status you want to retrieve.")
    key: str = Field(default=..., description="The unique key identifying the specific build status entry associated with the commit.")
    repo_slug: str = Field(default=..., description="The repository identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces.")
class GetRepositoriesCommitStatusesBuildRequest(StrictModel):
    """Retrieves a specific build status for a given commit using its unique key. Useful for checking the CI/CD pipeline result associated with a particular commit in a repository."""
    path: GetRepositoriesCommitStatusesBuildRequestPath

# Operation: update_commit_build_status
class PutRepositoriesCommitStatusesBuildRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit whose build status you want to update.")
    key: str = Field(default=..., description="The unique key identifying the build status entry to update. This value cannot be changed via this operation.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug (URL-friendly identifier) or the workspace UUID surrounded by curly-braces.")
class PutRepositoriesCommitStatusesBuildRequestBody(StrictModel):
    """The updated build status object"""
    body: Commitstatus | None = Field(default=None, description="The request body containing the build status fields to update, such as state, name, description, url, or refname.")
class PutRepositoriesCommitStatusesBuildRequest(StrictModel):
    """Updates an existing build status entry for a specific commit in a repository. Allows modification of state, name, description, URL, and ref name, while the unique key remains immutable."""
    path: PutRepositoriesCommitStatusesBuildRequestPath
    body: PutRepositoriesCommitStatusesBuildRequestBody | None = None

# Operation: list_commits
class GetRepositoriesByWorkspaceByRepoSlugCommitsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository.")
class GetRepositoriesByWorkspaceByRepoSlugCommitsRequest(StrictModel):
    """Retrieves all commits for a repository in reverse chronological (topological) order, similar to `git log --all`. Supports filtering by included/excluded refs and an optional file or directory path to scope results."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitsRequestPath

# Operation: list_commits_with_filters
class PostRepositoriesForWorkspaceForRepoSlugCommitsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesForWorkspaceForRepoSlugCommitsRequest(StrictModel):
    """Retrieves a list of commits for a repository, accepting include and exclude branch/commit parameters in the request body to avoid URL length limitations. This is functionally identical to the GET commits endpoint but does not support creating new commits."""
    path: PostRepositoriesForWorkspaceForRepoSlugCommitsRequestPath

# Operation: list_commits_by_revision
class GetRepositoriesByWorkspaceByRepoSlugCommitsByRevisionRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository within the workspace. UUID values must be surrounded by curly-braces.")
    revision: str = Field(default=..., description="The starting point for the commit log; accepts a full or abbreviated commit SHA1 or a ref name such as a branch or tag.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugCommitsByRevisionRequest(StrictModel):
    """Retrieves a paginated list of commits for a given branch, tag, or commit SHA in reverse chronological order, similar to `git log`. Supports filtering by additional include/exclude refs and an optional file or directory path to narrow results to commits affecting that path."""
    path: GetRepositoriesByWorkspaceByRepoSlugCommitsByRevisionRequestPath

# Operation: list_commits_by_revision_post
class PostRepositoriesForWorkspaceForRepoSlugCommitsForRevisionRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    revision: str = Field(default=..., description="The starting point for the commit history, specified as a full or abbreviated commit SHA1 hash or a ref name such as a branch or tag.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (workspace ID) or as a UUID surrounded by curly-braces.")
class PostRepositoriesForWorkspaceForRepoSlugCommitsForRevisionRequest(StrictModel):
    """Retrieves the commit history for a specific revision (SHA1 or branch/tag name) in a repository, using the request body to pass include and exclude filters instead of URL parameters to avoid length limitations."""
    path: PostRepositoriesForWorkspaceForRepoSlugCommitsForRevisionRequestPath

# Operation: list_default_reviewers
class GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (workspace short name) or as a UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersRequest(StrictModel):
    """Retrieves the list of users automatically added as reviewers on every new pull request for the specified repository. To include reviewers inherited from the parent project, use the effective-default-reviewers endpoint instead."""
    path: GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersRequestPath

# Operation: get_default_reviewer
class GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersByTargetUsernameRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    target_username: str = Field(default=..., description="The username or UUID of the default reviewer to look up. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersByTargetUsernameRequest(StrictModel):
    """Retrieves a specific default reviewer for a repository, confirming they are on the default reviewers list. A 404 response indicates the specified user is not a default reviewer for the repository."""
    path: GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersByTargetUsernameRequestPath

# Operation: add_default_reviewer
class PutRepositoriesDefaultReviewersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository within the workspace.")
    target_username: str = Field(default=..., description="The username or UUID of the user to add as a default reviewer for the repository.")
    workspace: str = Field(default=..., description="The workspace slug or UUID that owns the repository.")
class PutRepositoriesDefaultReviewersRequest(StrictModel):
    """Adds a specified user to the repository's list of default reviewers for pull requests. This operation is idempotent — adding a user who is already a default reviewer has no effect."""
    path: PutRepositoriesDefaultReviewersRequestPath

# Operation: remove_default_reviewer
class DeleteRepositoriesDefaultReviewersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository within the workspace.")
    target_username: str = Field(default=..., description="The username or UUID of the default reviewer to remove from the repository.")
    workspace: str = Field(default=..., description="The workspace slug or UUID that contains the repository.")
class DeleteRepositoriesDefaultReviewersRequest(StrictModel):
    """Removes a specified user from the default reviewers list for a repository. After removal, the user will no longer be automatically added as a reviewer on new pull requests."""
    path: DeleteRepositoriesDefaultReviewersRequestPath

# Operation: list_deploy_keys
class GetRepositoriesByWorkspaceByRepoSlugDeployKeysRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugDeployKeysRequest(StrictModel):
    """Retrieves all deploy keys associated with a specific repository in a workspace. Deploy keys provide read or read/write access to a repository without requiring user credentials."""
    path: GetRepositoriesByWorkspaceByRepoSlugDeployKeysRequestPath

# Operation: add_deploy_key
class PostRepositoriesDeployKeysRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesDeployKeysRequest(StrictModel):
    """Adds a new SSH deploy key to a repository, granting read or write access without requiring user credentials. Note that deploy keys authenticated via an OAuth consumer will be invalidated if that consumer is modified."""
    path: PostRepositoriesDeployKeysRequestPath

# Operation: get_deploy_key
class GetRepositoriesByWorkspaceByRepoSlugDeployKeysByKeyIdRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique numeric identifier of the deploy key to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID that owns the deploy key. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier (slug) or UUID in which the repository resides. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugDeployKeysByKeyIdRequest(StrictModel):
    """Retrieves a specific deploy key associated with a repository, identified by its unique key ID. Useful for inspecting deploy key details such as label, public key value, and permissions."""
    path: GetRepositoriesByWorkspaceByRepoSlugDeployKeysByKeyIdRequestPath

# Operation: update_deploy_key
class PutRepositoriesDeployKeysRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The numeric ID of the deploy key to update.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that contains the deploy key.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository.")
class PutRepositoriesDeployKeysRequest(StrictModel):
    """Updates an existing deploy key in a repository, allowing the label and comment to be changed while keeping the same public key value."""
    path: PutRepositoriesDeployKeysRequestPath

# Operation: delete_deploy_key
class DeleteRepositoriesDeployKeysRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique numeric identifier of the deploy key to delete.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID that owns the deploy key. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID where the repository resides. UUID values must be surrounded by curly-braces.")
class DeleteRepositoriesDeployKeysRequest(StrictModel):
    """Permanently removes a deploy key from a repository, revoking its access. This action cannot be undone."""
    path: DeleteRepositoriesDeployKeysRequestPath

# Operation: list_deployments
class GetRepositoriesByWorkspaceByRepoSlugDeploymentsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
class GetRepositoriesByWorkspaceByRepoSlugDeploymentsRequest(StrictModel):
    """Retrieves a list of all deployments for a specified repository. Returns deployment history and status information for the given workspace and repository."""
    path: GetRepositoriesByWorkspaceByRepoSlugDeploymentsRequestPath

# Operation: get_deployment
class GetRepositoriesByWorkspaceByRepoSlugDeploymentsByDeploymentUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the deployment.")
    deployment_uuid: str = Field(default=..., description="The unique identifier (UUID) of the deployment to retrieve.")
class GetRepositoriesByWorkspaceByRepoSlugDeploymentsByDeploymentUuidRequest(StrictModel):
    """Retrieves detailed information about a specific deployment in a repository. Use this to inspect the status, configuration, and metadata of a single deployment by its unique identifier."""
    path: GetRepositoriesByWorkspaceByRepoSlugDeploymentsByDeploymentUuidRequestPath

# Operation: list_environment_variables
class GetRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    environment_uuid: str = Field(default=..., description="The unique identifier of the deployment environment whose variables should be listed.")
class GetRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(StrictModel):
    """Retrieves all deployment variables configured for a specific environment in a repository. Returns environment-level variables used during deployments."""
    path: GetRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath

# Operation: create_environment_variable
class PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    environment_uuid: str = Field(default=..., description="The unique identifier of the deployment environment in which the variable will be created.")
class PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequestBody(StrictModel):
    """The variable to create"""
    body: PostRepositoriesDeploymentsConfigEnvironmentsVariablesBody | None = Field(default=None, description="The variable definition to create, including its key, value, and whether it should be treated as secured (masked).")
class PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(StrictModel):
    """Creates a new variable scoped to a specific deployment environment in a repository. Use this to define environment-level configuration or secrets for deployment pipelines."""
    path: PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath
    body: PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequestBody | None = None

# Operation: update_environment_variable
class PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the workspace that owns the deployment environment.")
    environment_uuid: str = Field(default=..., description="The UUID of the deployment environment whose variable is being updated.")
    variable_uuid: str = Field(default=..., description="The UUID of the specific variable to update within the deployment environment.")
class PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequestBody(StrictModel):
    """The updated deployment variable."""
    body: PutRepositoriesDeploymentsConfigEnvironmentsVariablesBody | None = Field(default=None, description="The request body containing the updated variable fields, such as key, value, or secured flag.")
class PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(StrictModel):
    """Updates an existing deployment environment level variable for a specific environment in a repository. Use this to modify the key, value, or secured status of a previously created variable."""
    path: PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath
    body: PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequestBody | None = None

# Operation: delete_environment_variable
class DeleteRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the workspace.")
    environment_uuid: str = Field(default=..., description="The unique identifier (UUID) of the deployment environment from which the variable will be deleted.")
    variable_uuid: str = Field(default=..., description="The unique identifier (UUID) of the variable to permanently delete from the environment.")
class DeleteRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(StrictModel):
    """Permanently deletes a specific variable from a deployment environment in a repository. This removes the variable and its value from the environment's configuration."""
    path: DeleteRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath

# Operation: get_repository_diff
class GetRepositoriesDiffRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository within the workspace.")
    spec: str = Field(default=..., description="A single commit SHA or a two-commit range using double-dot notation to define the diff scope. For two-commit ranges, the first commit contains the changes to preview and the second represents the comparison target (note: opposite order from git diff).")
    workspace: str = Field(default=..., description="The workspace slug or UUID that owns the repository.")
class GetRepositoriesDiffRequestQuery(StrictModel):
    context: int | None = Field(default=None, description="Number of context lines to include around each change in the diff, overriding the default of three lines.")
    path: str | None = Field(default=None, description="Restricts the diff output to a specific file path within the repository. This parameter may be repeated to filter on multiple paths.")
    ignore_whitespace: bool | None = Field(default=None, description="When true, whitespace differences are excluded from the diff output.")
    binary: bool | None = Field(default=None, description="When true, binary files are included in the diff output. Defaults to true if omitted.")
    renames: bool | None = Field(default=None, description="When true, rename detection is performed to identify moved or renamed files. Defaults to true if omitted.")
    topic: bool | None = Field(default=None, description="When true, returns a two-way three-dot diff showing changes between the source commit and the merge base of the source and destination commits. When false, returns a simple two-dot diff between source and destination. Defaults to true if omitted.")
class GetRepositoriesDiffRequest(StrictModel):
    """Retrieves a raw git-style diff for a repository, either for a single commit against its first parent or between two commits using dot notation. Supports three-dot topic diffs, file path filtering, and whitespace/rename/binary options."""
    path: GetRepositoriesDiffRequestPath
    query: GetRepositoriesDiffRequestQuery | None = None

# Operation: get_diffstat
class GetRepositoriesDiffstatRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository within the workspace.")
    spec: str = Field(default=..., description="A single commit SHA or a commit range using double-dot notation to compare two commits. For two-commit specs, the first commit represents the source (changes to preview) and the second represents the destination (state to compare against).")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository.")
class GetRepositoriesDiffstatRequestQuery(StrictModel):
    ignore_whitespace: bool | None = Field(default=None, description="When true, whitespace-only changes are excluded from the diffstat output.")
    path: str | None = Field(default=None, description="Restricts the diffstat to one or more specific file paths; repeat this parameter to include multiple paths.")
    renames: bool | None = Field(default=None, description="Controls whether file rename detection is performed; defaults to true when omitted.")
    topic: bool | None = Field(default=None, description="When true, returns a three-dot diff between the source commit and the merge base of the source and destination commits. When false, returns a simple two-dot diff between the two commits.")
class GetRepositoriesDiffstatRequest(StrictModel):
    """Retrieves file-level change statistics for a commit or commit range, returning a record per modified path with the type of change and lines added or removed. Supports single-commit diffs against the first parent, two-commit diffs, and three-dot topic branch diffs."""
    path: GetRepositoriesDiffstatRequestPath
    query: GetRepositoriesDiffstatRequestQuery | None = None

# Operation: list_download_artifacts
class GetRepositoriesByWorkspaceByRepoSlugDownloadsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugDownloadsRequest(StrictModel):
    """Retrieves all download artifacts associated with a specific repository in a workspace. Returns a list of available download links for the repository."""
    path: GetRepositoriesByWorkspaceByRepoSlugDownloadsRequestPath

# Operation: upload_download_artifact
class PostRepositoriesDownloadsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesDownloadsRequest(StrictModel):
    """Upload one or more download artifacts to a repository using a multipart/form-data POST request. If a file with the same name already exists, it will be replaced."""
    path: PostRepositoriesDownloadsRequestPath

# Operation: get_download_artifact
class GetRepositoriesByWorkspaceByRepoSlugDownloadsByFilenameRequestPath(StrictModel):
    filename: str = Field(default=..., description="The exact filename of the download artifact to retrieve from the repository's downloads section.")
    repo_slug: str = Field(default=..., description="The repository identifier, either as a URL-friendly slug or as a UUID enclosed in curly braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a URL-friendly slug or as a UUID enclosed in curly braces.")
class GetRepositoriesByWorkspaceByRepoSlugDownloadsByFilenameRequest(StrictModel):
    """Retrieves the actual file contents of a download artifact from a repository, redirecting to the file's direct download URL. Returns the raw file data rather than artifact metadata."""
    path: GetRepositoriesByWorkspaceByRepoSlugDownloadsByFilenameRequestPath

# Operation: delete_download_artifact
class DeleteRepositoriesDownloadsRequestPath(StrictModel):
    filename: str = Field(default=..., description="The exact name of the download artifact file to delete, including its file extension.")
    repo_slug: str = Field(default=..., description="The repository identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces.")
class DeleteRepositoriesDownloadsRequest(StrictModel):
    """Permanently deletes a specific download artifact file from a repository. This action cannot be undone and removes the file from the repository's public downloads section."""
    path: DeleteRepositoriesDownloadsRequestPath

# Operation: get_effective_branching_model
class GetRepositoriesEffectiveBranchingModelRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesEffectiveBranchingModelRequest(StrictModel):
    """Retrieves the effective (currently applied) branching model for a repository, reflecting any inherited workspace-level settings combined with repository-specific overrides."""
    path: GetRepositoriesEffectiveBranchingModelRequestPath

# Operation: list_effective_default_reviewers
class GetRepositoriesEffectiveDefaultReviewersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesEffectiveDefaultReviewersRequest(StrictModel):
    """Retrieves the effective default reviewers for a repository, combining reviewers defined at the repository level with those inherited from its parent project. These users are automatically added as reviewers on every new pull request created in the repository."""
    path: GetRepositoriesEffectiveDefaultReviewersRequestPath

# Operation: list_environments
class GetRepositoriesByWorkspaceByRepoSlugEnvironmentsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace whose environments will be listed.")
class GetRepositoriesByWorkspaceByRepoSlugEnvironmentsRequest(StrictModel):
    """Retrieves all deployment environments configured for a specified repository within a workspace. Useful for inspecting available environments such as production, staging, or test."""
    path: GetRepositoriesByWorkspaceByRepoSlugEnvironmentsRequestPath

# Operation: create_environment
class PostRepositoriesEnvironmentsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace where the environment will be created.")
class PostRepositoriesEnvironmentsRequestBody(StrictModel):
    """The environment to create."""
    body: PostRepositoriesEnvironmentsBody | None = Field(default=None, description="The request body containing the environment configuration details, such as name and environment type.")
class PostRepositoriesEnvironmentsRequest(StrictModel):
    """Creates a new deployment environment (e.g., production, staging, test) within a specified repository. Environments are used to manage deployment configurations and variables."""
    path: PostRepositoriesEnvironmentsRequestPath
    body: PostRepositoriesEnvironmentsRequestBody | None = None

# Operation: get_environment
class GetRepositoriesByWorkspaceByRepoSlugEnvironmentsByEnvironmentUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the target environment.")
    environment_uuid: str = Field(default=..., description="The unique UUID of the deployment environment to retrieve, surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugEnvironmentsByEnvironmentUuidRequest(StrictModel):
    """Retrieves the details of a specific deployment environment within a repository. Use this to inspect environment configuration, status, and metadata by its unique identifier."""
    path: GetRepositoriesByWorkspaceByRepoSlugEnvironmentsByEnvironmentUuidRequestPath

# Operation: delete_environment
class DeleteRepositoriesEnvironmentsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    environment_uuid: str = Field(default=..., description="The unique UUID of the deployment environment to delete, surrounded by curly braces.")
class DeleteRepositoriesEnvironmentsRequest(StrictModel):
    """Permanently deletes a deployment environment from a repository. This action cannot be undone and will remove all associated environment configuration."""
    path: DeleteRepositoriesEnvironmentsRequestPath

# Operation: update_environment
class PostRepositoriesEnvironmentsChangesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    environment_uuid: str = Field(default=..., description="The unique identifier (UUID) of the deployment environment to update.")
class PostRepositoriesEnvironmentsChangesRequest(StrictModel):
    """Apply configuration changes to a specific deployment environment in a repository. Use this to modify environment settings such as variables or deployment rules."""
    path: PostRepositoriesEnvironmentsChangesRequestPath

# Operation: list_file_history
class GetRepositoriesFilehistoryRequestPath(StrictModel):
    commit: str = Field(default=..., description="The SHA1 hash of the commit to start the file history from.")
    path: str = Field(default=..., description="The path to the file within the repository whose commit history you want to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace; UUIDs must be surrounded by curly braces.")
class GetRepositoriesFilehistoryRequestQuery(StrictModel):
    renames: str | None = Field(default=None, description="Controls whether Bitbucket follows the file across renames when traversing history; defaults to true, set to false to disable rename tracking.")
    q: str | None = Field(default=None, description="A filter expression to narrow down the returned commits using Bitbucket's filtering and sorting syntax.")
    sort: str | None = Field(default=None, description="The name of a response property to sort results by, using Bitbucket's filtering and sorting syntax.")
class GetRepositoriesFilehistoryRequest(StrictModel):
    """Retrieves a paginated list of commits that modified a specific file in a repository, returned in reverse chronological order. Supports rename tracking, filtering, and sorting to precisely scope the results."""
    path: GetRepositoriesFilehistoryRequestPath
    query: GetRepositoriesFilehistoryRequestQuery | None = None

# Operation: list_repository_forks
class GetRepositoriesForksRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository whose forks should be listed. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesForksRequestQuery(StrictModel):
    role: Literal["admin", "contributor", "member", "owner"] | None = Field(default=None, description="Filters returned forks based on the authenticated user's role: member (explicit read access), contributor (explicit write access), admin (explicit administrator access), or owner (repositories owned by the current user).")
    q: str | None = Field(default=None, description="A query string to filter and narrow down the list of returned forks using Bitbucket's filtering and sorting syntax.")
    sort: str | None = Field(default=None, description="The field name by which the returned fork results should be sorted, following Bitbucket's filtering and sorting syntax.")
class GetRepositoriesForksRequest(StrictModel):
    """Retrieves a paginated list of all forks for a specified repository in a given workspace. Results can be filtered by the authenticated user's role, a query string, and sorted by a specified field."""
    path: GetRepositoriesForksRequestPath
    query: GetRepositoriesForksRequestQuery | None = None

# Operation: fork_repository
class PostRepositoriesForksRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The slug or UUID of the repository to fork. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The slug or UUID of the workspace that owns the source repository. UUIDs must be surrounded by curly-braces.")
class PostRepositoriesForksRequestBody(StrictModel):
    """A repository object. This can be left blank."""
    body: Repository | None = Field(default=None, description="Optional request body following the repository JSON schema to configure the fork. Must include a workspace slug to specify the fork destination, and a name to distinguish it from the parent. Overridable fields include name, description, fork_policy, language, mainbranch, is_private, has_issues, has_wiki, and project. Fields scm, parent, and full_name cannot be overridden.")
class PostRepositoriesForksRequest(StrictModel):
    """Creates a new fork of the specified repository into a target workspace, optionally overriding properties such as name, description, visibility, and issue tracker settings. The fork inherits most parent properties by default, but scm, parent, and full_name cannot be changed."""
    path: PostRepositoriesForksRequestPath
    body: PostRepositoriesForksRequestBody | None = None

# Operation: list_repository_webhooks
class GetRepositoriesByWorkspaceByRepoSlugHooksRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or the repository UUID enclosed in curly-braces, uniquely identifying the target repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace slug (ID) or the workspace UUID enclosed in curly-braces, identifying the workspace that owns the repository.")
class GetRepositoriesByWorkspaceByRepoSlugHooksRequest(StrictModel):
    """Retrieves a paginated list of all webhooks installed on a specific repository. Useful for auditing or managing event-driven integrations configured for the repo."""
    path: GetRepositoriesByWorkspaceByRepoSlugHooksRequestPath

# Operation: get_repository_webhook
class GetRepositoriesByWorkspaceByRepoSlugHooksByUidRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces.")
    uid: str = Field(default=..., description="The unique identifier of the installed webhook to retrieve.")
    workspace: str = Field(default=..., description="The workspace slug (ID) or the workspace UUID surrounded by curly-braces that owns the repository.")
class GetRepositoriesByWorkspaceByRepoSlugHooksByUidRequest(StrictModel):
    """Retrieves the details of a specific webhook installed on a repository, identified by its unique ID. Use this to inspect webhook configuration, events, and status for a given repository."""
    path: GetRepositoriesByWorkspaceByRepoSlugHooksByUidRequestPath

# Operation: update_repository_webhook
class PutRepositoriesHooksRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either its slug (short name) or its UUID surrounded by curly-braces.")
    uid: str = Field(default=..., description="The unique identifier of the installed webhook subscription to update.")
    workspace: str = Field(default=..., description="The workspace identifier, either its slug or its UUID surrounded by curly-braces.")
class PutRepositoriesHooksRequest(StrictModel):
    """Updates an existing webhook subscription on a repository, allowing mutation of its description, URL, secret, active status, and events. The secret field controls HMAC signature generation for the X-Hub-Signature header; omit it to leave unchanged, or pass null to remove it."""
    path: PutRepositoriesHooksRequestPath

# Operation: delete_repository_webhook
class DeleteRepositoriesHooksRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    uid: str = Field(default=..., description="The unique identifier of the installed webhook subscription to delete.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class DeleteRepositoriesHooksRequest(StrictModel):
    """Permanently removes a specific webhook subscription from a repository, stopping all future event deliveries to the configured endpoint."""
    path: DeleteRepositoriesHooksRequestPath

# Operation: get_merge_base
class GetRepositoriesMergeBaseRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    revspec: str = Field(default=..., description="A range of exactly two commits specified using double-dot notation, identifying the two commits whose common ancestor should be found.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesMergeBaseRequest(StrictModel):
    """Finds the best common ancestor commit between two commits in a repository, useful for determining the divergence point of branches or commits. If multiple best common ancestors exist, one is returned arbitrarily."""
    path: GetRepositoriesMergeBaseRequestPath

# Operation: get_repository_override_settings
class GetRepositoriesOverrideSettingsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesOverrideSettingsRequest(StrictModel):
    """Retrieves the inheritance state for a repository's settings, indicating which settings are overridden at the repository level versus inherited from the workspace."""
    path: GetRepositoriesOverrideSettingsRequestPath

# Operation: set_repository_override_settings
class PutRepositoriesOverrideSettingsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUID values must be surrounded by curly-braces.")
class PutRepositoriesOverrideSettingsRequest(StrictModel):
    """Configures the inheritance state for a repository's settings, determining which settings are overridden at the repository level versus inherited from the workspace."""
    path: PutRepositoriesOverrideSettingsRequestPath

# Operation: get_repository_patch
class GetRepositoriesPatchRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    spec: str = Field(default=..., description="A single commit SHA or a two-commit range using double-dot notation to generate a patch series. For a range, the first commit is the source and the second is the destination.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesPatchRequest(StrictModel):
    """Retrieves a raw patch for a single commit (diffed against its first parent) or a patch series for a two-commit range, including commit headers such as author and message. Unlike diffs, patches carry full commit metadata and are returned as plain text in the repository's native encoding."""
    path: GetRepositoriesPatchRequestPath

# Operation: list_repository_group_permissions
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsRequest(StrictModel):
    """Retrieves a paginated list of explicit group permissions configured for a specific repository. Only explicitly set group permissions are returned; inherited or default permissions are not included."""
    path: GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsRequestPath

# Operation: get_repository_group_permission
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsByGroupSlugRequestPath(StrictModel):
    group_slug: str = Field(default=..., description="The slug identifier of the group whose repository permission is being retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that identifies the target repository.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that contains the repository.")
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsByGroupSlugRequest(StrictModel):
    """Retrieves the explicit permission level assigned to a specific group for a given repository. Requires admin permission on the repository; returns one of: admin, write, read, or none."""
    path: GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsByGroupSlugRequestPath

# Operation: list_repository_user_permissions
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersRequest(StrictModel):
    """Retrieves a paginated list of explicit user-level permissions configured for a specific repository. Only directly assigned user permissions are returned; inherited or group-based permissions are not included."""
    path: GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersRequestPath

# Operation: get_user_repository_permission
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersBySelectedUserIdRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUID format must be surrounded by curly-braces.")
    selected_user_id: str = Field(default=..., description="The unique identifier of the user whose permission is being retrieved. Accepts either an Atlassian Account ID or a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID that contains the repository. UUID format must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersBySelectedUserIdRequest(StrictModel):
    """Retrieves the explicit permission level assigned to a specific user for a given repository. Requires admin permission on the repository; returns one of: admin, write, read, or none."""
    path: GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersBySelectedUserIdRequestPath

# Operation: delete_user_repository_permission
class DeleteRepositoriesPermissionsConfigUsersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository within the workspace.")
    selected_user_id: str = Field(default=..., description="The account identifier for the user whose repository permission will be deleted, provided as either an Atlassian Account ID or a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, provided as either the workspace slug or a UUID surrounded by curly-braces.")
class DeleteRepositoriesPermissionsConfigUsersRequest(StrictModel):
    """Deletes an explicit user-level permission for a specific repository, removing any custom access grant assigned to that user. Requires admin permission on the repository and authentication via app passwords."""
    path: DeleteRepositoriesPermissionsConfigUsersRequestPath

# Operation: list_pipelines
class GetRepositoriesByWorkspaceByRepoSlugPipelinesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesRequestQuery(StrictModel):
    creator_uuid: str | None = Field(default=None, validation_alias="creator.uuid", serialization_alias="creator.uuid", description="Filter pipelines to only those created by the user with this UUID.", json_schema_extra={'format': 'uuid'})
    target_ref_type: Literal["BRANCH", "TAG", "ANNOTATED_TAG"] | None = Field(default=None, validation_alias="target.ref_type", serialization_alias="target.ref_type", description="Filter pipelines by the type of Git reference that triggered them. Must be one of BRANCH, TAG, or ANNOTATED_TAG.")
    target_ref_name: str | None = Field(default=None, validation_alias="target.ref_name", serialization_alias="target.ref_name", description="Filter pipelines by the exact name of the Git reference (branch name, tag name, etc.) that triggered them.")
    target_branch: str | None = Field(default=None, validation_alias="target.branch", serialization_alias="target.branch", description="Filter pipelines by the name of the branch that triggered them.")
    target_commit_hash: str | None = Field(default=None, validation_alias="target.commit.hash", serialization_alias="target.commit.hash", description="Filter pipelines by the commit hash (revision) that triggered them.")
    target_selector_pattern: str | None = Field(default=None, validation_alias="target.selector.pattern", serialization_alias="target.selector.pattern", description="Filter pipelines by the pipeline configuration pattern (e.g., a custom pipeline name pattern).")
    target_selector_type: Literal["BRANCH", "TAG", "CUSTOM", "PULLREQUESTS", "DEFAULT"] | None = Field(default=None, validation_alias="target.selector.type", serialization_alias="target.selector.type", description="Filter pipelines by their selector type, indicating the category of pipeline. Must be one of BRANCH, TAG, CUSTOM, PULLREQUESTS, or DEFAULT.")
    created_on: str | None = Field(default=None, description="Filter pipelines by their creation date and time, provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    trigger_type: Literal["PUSH", "MANUAL", "SCHEDULED", "PARENT_STEP"] | None = Field(default=None, description="Filter pipelines by what triggered them. Must be one of PUSH, MANUAL, SCHEDULED, or PARENT_STEP.")
    status: Literal["PARSING", "PENDING", "PAUSED", "HALTED", "BUILDING", "ERROR", "PASSED", "FAILED", "STOPPED", "UNKNOWN"] | None = Field(default=None, description="Filter pipelines by their current execution status. Must be one of PARSING, PENDING, PAUSED, HALTED, BUILDING, ERROR, PASSED, FAILED, STOPPED, or UNKNOWN.")
    sort: Literal["creator.uuid", "created_on", "run_creation_date"] | None = Field(default=None, description="The field by which to sort the returned pipelines. Must be one of creator.uuid, created_on, or run_creation_date.")
    page: int | None = Field(default=None, description="The page number to retrieve in the paginated result set, starting at 1.", json_schema_extra={'format': 'int32'})
    pagelen: int | None = Field(default=None, description="The maximum number of pipeline results to return per page, between 1 and 100.", json_schema_extra={'format': 'int32'})
class GetRepositoriesByWorkspaceByRepoSlugPipelinesRequest(StrictModel):
    """Retrieve a paginated list of pipelines for a specific repository, with support for filtering by branch, commit, status, trigger type, and more, as well as sorting of results."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugPipelinesRequestQuery | None = None

# Operation: trigger_pipeline
class PostRepositoriesPipelinesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier — either the slug (short name) or the UUID surrounded by curly braces — that owns the repository.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or identifier within the workspace where the pipeline will be triggered.")
class PostRepositoriesPipelinesRequestBody(StrictModel):
    """The pipeline to initiate."""
    body: PostRepositoriesPipelinesBody | None = Field(default=None, description="The pipeline trigger payload defining the target and optional variables. The target type determines the trigger mode: use 'pipeline_ref_target' for branch or tag triggers, 'pipeline_commit_target' for a specific commit with a custom selector, or 'pipeline_pullrequest_target' for pull request pipelines. Optionally include a 'variables' array of key-value pairs (with optional 'secured' flag) to inject build-time variables into custom pipelines.")
class PostRepositoriesPipelinesRequest(StrictModel):
    """Creates and initiates a pipeline run for a repository, supporting multiple trigger modes including branch-based, commit-specific, custom selector, pull request, and variable-injected pipelines as defined in the repository's bitbucket-pipelines.yml file."""
    path: PostRepositoriesPipelinesRequestPath
    body: PostRepositoriesPipelinesRequestBody | None = None

# Operation: list_pipeline_caches
class GetRepositoriesPipelinesConfigCachesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The slug or UUID of the workspace that owns the repository.")
    repo_slug: str = Field(default=..., description="The slug or UUID of the repository whose pipeline caches are being listed.")
class GetRepositoriesPipelinesConfigCachesRequest(StrictModel):
    """Retrieves all pipeline caches configured for a repository, providing visibility into cached dependencies and build artifacts used to speed up pipeline runs."""
    path: GetRepositoriesPipelinesConfigCachesRequestPath

# Operation: delete_pipeline_caches
class DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the account that owns the repository.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository whose pipeline caches will be deleted.")
class DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequestQuery(StrictModel):
    name: str = Field(default=..., description="The name of the pipeline cache to delete; all versions matching this name will be removed.")
class DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequest(StrictModel):
    """Delete all cached versions for a specific pipeline cache by name in a repository. This removes the named cache entries from the repository's pipelines configuration."""
    path: DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequestPath
    query: DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequestQuery

# Operation: delete_pipeline_cache
class DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesForCacheUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the account that owns the repository.")
    repo_slug: str = Field(default=..., description="The repository slug identifying the repository whose pipeline cache will be deleted.")
    cache_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline cache to delete.")
class DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesForCacheUuidRequest(StrictModel):
    """Deletes a specific pipeline cache from a repository, freeing up cached resources associated with the given cache UUID."""
    path: DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesForCacheUuidRequestPath

# Operation: get_pipeline_cache_content_uri
class GetRepositoriesPipelinesConfigCachesContentUriRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The slug or UUID of the Bitbucket workspace that owns the repository.")
    repo_slug: str = Field(default=..., description="The slug or UUID of the repository containing the pipeline cache.")
    cache_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline cache whose content URI you want to retrieve.")
class GetRepositoriesPipelinesConfigCachesContentUriRequest(StrictModel):
    """Retrieves the download URI for the content of a specific pipeline cache in a repository. Use this URI to access or download the cached build artifacts."""
    path: GetRepositoriesPipelinesConfigCachesContentUriRequestPath

# Operation: list_repository_runners
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersRequest(StrictModel):
    """Retrieve all pipeline runners configured for a specific repository. Runners are used to execute Bitbucket Pipelines builds within the given workspace and repository."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersRequestPath

# Operation: create_repository_runner
class PostRepositoriesPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace where the runner will be created.")
class PostRepositoriesPipelinesConfigRunnersRequest(StrictModel):
    """Creates a new runner for a specific repository in Bitbucket Pipelines, enabling custom build infrastructure to be registered and used for pipeline executions within that repository."""
    path: PostRepositoriesPipelinesConfigRunnersRequestPath

# Operation: get_repository_runner
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersByRunnerUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    runner_uuid: str = Field(default=..., description="The unique UUID of the runner to retrieve, used to identify a specific Pipelines runner within the repository.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersByRunnerUuidRequest(StrictModel):
    """Retrieves details of a specific Pipelines runner configured for a repository, identified by its UUID."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersByRunnerUuidRequestPath

# Operation: update_repository_runner
class PutRepositoriesPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    runner_uuid: str = Field(default=..., description="The unique identifier (UUID) of the runner to update, surrounded by curly-braces.")
class PutRepositoriesPipelinesConfigRunnersRequest(StrictModel):
    """Updates the configuration of a specific runner associated with a repository. Identifies the target runner by its UUID within the given workspace and repository."""
    path: PutRepositoriesPipelinesConfigRunnersRequestPath

# Operation: delete_repository_runner
class DeleteRepositoriesPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    runner_uuid: str = Field(default=..., description="The unique UUID of the runner to delete, used to precisely identify the target runner within the repository's Pipelines configuration.")
class DeleteRepositoriesPipelinesConfigRunnersRequest(StrictModel):
    """Permanently removes a specific runner from a repository's Pipelines configuration. The runner is identified by its UUID and will no longer be available for pipeline jobs in that repository."""
    path: DeleteRepositoriesPipelinesConfigRunnersRequestPath

# Operation: get_pipeline
class GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    pipeline_uuid: str = Field(default=..., description="The unique UUID of the pipeline run to retrieve.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidRequest(StrictModel):
    """Retrieves the details of a specific pipeline run within a repository, including its status, steps, and configuration."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidRequestPath

# Operation: list_pipeline_steps
class GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the pipeline.")
    pipeline_uuid: str = Field(default=..., description="The unique UUID of the pipeline whose steps are to be listed, formatted as a standard UUID string.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsRequest(StrictModel):
    """Retrieves all steps for a specified pipeline in a repository, providing visibility into each stage of the pipeline's execution."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsRequestPath

# Operation: get_pipeline_step
class GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsByStepUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug, which is the URL-friendly name of the repository within the specified workspace.")
    pipeline_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline whose step is being retrieved.")
    step_uuid: str = Field(default=..., description="The unique identifier (UUID) of the specific step within the pipeline to retrieve.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsByStepUuidRequest(StrictModel):
    """Retrieves the details of a specific step within a pipeline, including its status, timing, and configuration. Useful for monitoring or inspecting individual steps of a CI/CD pipeline run."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsByStepUuidRequestPath

# Operation: get_pipeline_step_log
class GetRepositoriesPipelinesStepsLogRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug, which is the URL-friendly name of the repository within the workspace.")
    pipeline_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline whose step log is being retrieved.")
    step_uuid: str = Field(default=..., description="The unique identifier (UUID) of the specific pipeline step whose log file should be returned.")
class GetRepositoriesPipelinesStepsLogRequest(StrictModel):
    """Retrieves the full log file for a specific step within a pipeline. Supports HTTP Range requests to efficiently stream or paginate potentially large log files."""
    path: GetRepositoriesPipelinesStepsLogRequestPath

# Operation: get_pipeline_step_log_container
class GetRepositoriesPipelinesStepsLogsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug identifying the target repository within the workspace.")
    pipeline_uuid: str = Field(default=..., description="The UUID of the pipeline whose step logs are being retrieved.")
    step_uuid: str = Field(default=..., description="The UUID of the step within the pipeline whose container logs are being retrieved.")
    log_uuid: str = Field(default=..., description="The UUID identifying which container log to retrieve — use the step UUID for the main build container, or the service container UUID for a service container.")
class GetRepositoriesPipelinesStepsLogsRequest(StrictModel):
    """Retrieves the log file for a build container or service container within a specific pipeline step. Supports HTTP Range requests to efficiently handle large log files."""
    path: GetRepositoriesPipelinesStepsLogsRequestPath

# Operation: get_pipeline_step_test_report
class GetRepositoriesPipelinesStepsTestReportsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID enclosed in curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    pipeline_uuid: str = Field(default=..., description="The UUID of the pipeline whose step test reports are being retrieved.")
    step_uuid: str = Field(default=..., description="The UUID of the specific pipeline step for which test reports are being retrieved.")
class GetRepositoriesPipelinesStepsTestReportsRequest(StrictModel):
    """Retrieves a summary of test reports for a specific step within a pipeline, providing an overview of test results such as pass/fail counts and coverage metrics."""
    path: GetRepositoriesPipelinesStepsTestReportsRequestPath

# Operation: list_pipeline_step_test_cases
class GetRepositoriesPipelinesStepsTestReportsTestCasesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    pipeline_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline whose step test cases are being retrieved.")
    step_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline step whose test cases are being retrieved.")
class GetRepositoriesPipelinesStepsTestReportsTestCasesRequest(StrictModel):
    """Retrieves all test cases from the test report for a specific step within a pipeline. Useful for inspecting individual test outcomes after a CI pipeline run."""
    path: GetRepositoriesPipelinesStepsTestReportsTestCasesRequestPath

# Operation: list_test_case_reasons
class GetRepositoriesPipelinesStepsTestReportsTestCasesTestCaseReasonsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug identifying the target repository within the workspace.")
    pipeline_uuid: str = Field(default=..., description="The UUID of the pipeline containing the step and test case.")
    step_uuid: str = Field(default=..., description="The UUID of the pipeline step that contains the test case.")
    test_case_uuid: str = Field(default=..., description="The UUID of the specific test case whose reasons are being retrieved.")
class GetRepositoriesPipelinesStepsTestReportsTestCasesTestCaseReasonsRequest(StrictModel):
    """Retrieves the reasons (output details) for a specific test case within a pipeline step, providing diagnostic information such as failure messages or stack traces."""
    path: GetRepositoriesPipelinesStepsTestReportsTestCasesTestCaseReasonsRequestPath

# Operation: stop_pipeline
class PostRepositoriesPipelinesStopPipelineRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug (short name) or the workspace UUID enclosed in curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the pipeline to stop.")
    pipeline_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline to stop, enclosed in curly braces.")
class PostRepositoriesPipelinesStopPipelineRequest(StrictModel):
    """Stops a running pipeline and all of its in-progress steps that have not yet completed. Use this to immediately halt pipeline execution within a specific repository."""
    path: PostRepositoriesPipelinesStopPipelineRequestPath

# Operation: get_pipelines_config
class GetRepositoriesPipelinesConfigRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The slug or UUID of the workspace that owns the repository.")
    repo_slug: str = Field(default=..., description="The slug or UUID of the repository whose Pipelines configuration is being retrieved.")
class GetRepositoriesPipelinesConfigRequest(StrictModel):
    """Retrieves the Pipelines configuration for a specific repository, including settings that control how pipelines are enabled and executed."""
    path: GetRepositoriesPipelinesConfigRequestPath

# Operation: set_pipeline_next_build_number
class PutRepositoriesPipelinesConfigBuildNumberRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug identifying which repository's pipeline build number sequence to update.")
class PutRepositoriesPipelinesConfigBuildNumberRequestBody(StrictModel):
    """The build number to update."""
    body: PutRepositoriesPipelinesConfigBuildNumberBody | None = Field(default=None, description="Request body containing the next build number to assign. Must be strictly higher than the current latest build number for this repository.")
class PutRepositoriesPipelinesConfigBuildNumberRequest(StrictModel):
    """Updates the next build number to be assigned to a pipeline in the specified repository. The configured value must be strictly greater than the current latest build number."""
    path: PutRepositoriesPipelinesConfigBuildNumberRequestPath
    body: PutRepositoriesPipelinesConfigBuildNumberRequestBody | None = None

# Operation: list_pipeline_schedules
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesRequest(StrictModel):
    """Retrieve all configured pipeline schedules for a given repository. Returns the list of schedules that define when pipelines are automatically triggered."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesRequestPath

# Operation: create_pipeline_schedule
class PostRepositoriesPipelinesConfigSchedulesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the workspace for which the pipeline schedule will be created.")
class PostRepositoriesPipelinesConfigSchedulesRequestBody(StrictModel):
    """The schedule to create."""
    body: PostRepositoriesPipelinesConfigSchedulesBody | None = Field(default=None, description="The schedule configuration payload defining the timing, target branch, and other schedule properties for the pipeline.")
class PostRepositoriesPipelinesConfigSchedulesRequest(StrictModel):
    """Creates a new pipeline schedule for the specified repository, allowing automated pipeline runs at defined intervals or times."""
    path: PostRepositoriesPipelinesConfigSchedulesRequestPath
    body: PostRepositoriesPipelinesConfigSchedulesRequestBody | None = None

# Operation: get_pipeline_schedule
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesByScheduleUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    schedule_uuid: str = Field(default=..., description="The UUID that uniquely identifies the pipeline schedule to retrieve.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesByScheduleUuidRequest(StrictModel):
    """Retrieves a specific pipeline schedule by its UUID for a given repository. Returns the full schedule configuration including timing and status details."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesByScheduleUuidRequestPath

# Operation: update_pipeline_schedule
class PutRepositoriesPipelinesConfigSchedulesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    schedule_uuid: str = Field(default=..., description="The unique identifier (UUID) of the pipeline schedule to update.")
class PutRepositoriesPipelinesConfigSchedulesRequestBody(StrictModel):
    """The schedule to update."""
    body: PutRepositoriesPipelinesConfigSchedulesBody | None = Field(default=None, description="The updated schedule configuration payload containing the fields to modify on the existing schedule.")
class PutRepositoriesPipelinesConfigSchedulesRequest(StrictModel):
    """Updates an existing pipeline schedule for a repository. Use this to modify the timing or configuration of a scheduled pipeline run."""
    path: PutRepositoriesPipelinesConfigSchedulesRequestPath
    body: PutRepositoriesPipelinesConfigSchedulesRequestBody | None = None

# Operation: delete_pipeline_schedule
class DeleteRepositoriesPipelinesConfigSchedulesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    schedule_uuid: str = Field(default=..., description="The unique UUID of the pipeline schedule to delete, used to identify the specific schedule within the repository.")
class DeleteRepositoriesPipelinesConfigSchedulesRequest(StrictModel):
    """Permanently deletes a specific pipeline schedule from a repository. This removes the scheduled trigger and prevents any future automated pipeline runs associated with it."""
    path: DeleteRepositoriesPipelinesConfigSchedulesRequestPath

# Operation: list_schedule_executions
class GetRepositoriesPipelinesConfigSchedulesExecutionsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    schedule_uuid: str = Field(default=..., description="The UUID of the pipeline schedule whose executions should be retrieved.")
class GetRepositoriesPipelinesConfigSchedulesExecutionsRequest(StrictModel):
    """Retrieve the execution history for a specific pipeline schedule in a repository. Returns a list of past executions triggered by the given schedule."""
    path: GetRepositoriesPipelinesConfigSchedulesExecutionsRequestPath

# Operation: get_repository_ssh_key_pair
class GetRepositoriesPipelinesConfigSshKeyPairRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class GetRepositoriesPipelinesConfigSshKeyPairRequest(StrictModel):
    """Retrieves the SSH key pair configured for a repository's pipeline, returning only the public key. The private key is write-only and is never exposed through the API or logs."""
    path: GetRepositoriesPipelinesConfigSshKeyPairRequestPath

# Operation: set_repository_ssh_key_pair
class PutRepositoriesPipelinesConfigSshKeyPairRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class PutRepositoriesPipelinesConfigSshKeyPairRequestBody(StrictModel):
    """The created or updated SSH key pair."""
    body: PutRepositoriesPipelinesConfigSshKeyPairBody | None = Field(default=None, description="The SSH key pair payload containing the public and private key to set for the repository's pipeline configuration.")
class PutRepositoriesPipelinesConfigSshKeyPairRequest(StrictModel):
    """Creates or updates the SSH key pair for a repository's pipeline configuration. The private key will be set as the default SSH identity in the build container."""
    path: PutRepositoriesPipelinesConfigSshKeyPairRequestPath
    body: PutRepositoriesPipelinesConfigSshKeyPairRequestBody | None = None

# Operation: delete_repository_ssh_key_pair
class DeleteRepositoriesPipelinesConfigSshKeyPairRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class DeleteRepositoriesPipelinesConfigSshKeyPairRequest(StrictModel):
    """Deletes the SSH key pair configured for a repository's pipelines. This removes both the public and private keys associated with the repository's pipeline SSH configuration."""
    path: DeleteRepositoriesPipelinesConfigSshKeyPairRequestPath

# Operation: list_pipeline_ssh_known_hosts
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsRequest(StrictModel):
    """Retrieves all SSH known hosts configured at the repository level for Pipelines. Known hosts are used to verify remote server identities during pipeline SSH connections."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsRequestPath

# Operation: create_ssh_known_host
class PostRepositoriesPipelinesConfigSshKnownHostsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class PostRepositoriesPipelinesConfigSshKnownHostsRequestBody(StrictModel):
    """The known host to create."""
    body: PostRepositoriesPipelinesConfigSshKnownHostsBody | None = Field(default=None, description="The known host object to create, containing the hostname and its associated public key details.")
class PostRepositoriesPipelinesConfigSshKnownHostsRequest(StrictModel):
    """Adds a known SSH host to a repository's Pipelines configuration, enabling trusted host verification during pipeline execution."""
    path: PostRepositoriesPipelinesConfigSshKnownHostsRequestPath
    body: PostRepositoriesPipelinesConfigSshKnownHostsRequestBody | None = None

# Operation: get_pipeline_ssh_known_host
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsByKnownHostUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID enclosed in curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    known_host_uuid: str = Field(default=..., description="The UUID of the SSH known host entry to retrieve, uniquely identifying it within the repository's Pipelines SSH configuration.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsByKnownHostUuidRequest(StrictModel):
    """Retrieves a specific SSH known host entry configured at the repository level for Pipelines, identified by its UUID."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsByKnownHostUuidRequestPath

# Operation: update_pipeline_known_host
class PutRepositoriesPipelinesConfigSshKnownHostsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    known_host_uuid: str = Field(default=..., description="The unique UUID of the SSH known host entry to update, used to identify the specific record within the repository's pipeline configuration.")
class PutRepositoriesPipelinesConfigSshKnownHostsRequestBody(StrictModel):
    """The updated known host."""
    body: PutRepositoriesPipelinesConfigSshKnownHostsBody | None = Field(default=None, description="The request body containing the updated SSH known host details, such as the hostname and public key fingerprint.")
class PutRepositoriesPipelinesConfigSshKnownHostsRequest(StrictModel):
    """Updates an existing SSH known host entry in a repository's pipeline configuration, allowing you to modify the host details for secure pipeline connections."""
    path: PutRepositoriesPipelinesConfigSshKnownHostsRequestPath
    body: PutRepositoriesPipelinesConfigSshKnownHostsRequestBody | None = None

# Operation: delete_known_host
class DeleteRepositoriesPipelinesConfigSshKnownHostsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    known_host_uuid: str = Field(default=..., description="The unique UUID of the known host entry to delete, used to identify the specific record within the repository's Pipelines SSH configuration.")
class DeleteRepositoriesPipelinesConfigSshKnownHostsRequest(StrictModel):
    """Deletes a specific SSH known host entry from a repository's Pipelines configuration. This removes the trusted host record identified by its UUID, preventing Pipelines from automatically trusting that host during SSH operations."""
    path: DeleteRepositoriesPipelinesConfigSshKnownHostsRequestPath

# Operation: list_repository_pipeline_variables
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesRequest(StrictModel):
    """Retrieves all pipeline variables configured at the repository level for a given workspace and repository. Useful for inspecting environment variables available to pipelines without exposing secured values."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesRequestPath

# Operation: create_repository_pipeline_variable
class PostRepositoriesPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
class PostRepositoriesPipelinesConfigVariablesRequestBody(StrictModel):
    """The variable to create."""
    body: PostRepositoriesPipelinesConfigVariablesBody | None = Field(default=None, description="The pipeline variable object to create, including its key, value, and whether it should be secured (masked in logs).")
class PostRepositoriesPipelinesConfigVariablesRequest(StrictModel):
    """Creates a new pipeline environment variable at the repository level, making it available to all pipelines within the specified repository."""
    path: PostRepositoriesPipelinesConfigVariablesRequestPath
    body: PostRepositoriesPipelinesConfigVariablesRequestBody | None = None

# Operation: get_pipeline_variable
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesByVariableUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace.")
    variable_uuid: str = Field(default=..., description="The UUID of the pipeline configuration variable to retrieve, uniquely identifying it within the repository.")
class GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesByVariableUuidRequest(StrictModel):
    """Retrieves a specific pipeline configuration variable for a repository by its UUID. Use this to inspect the details of a single repository-level pipeline variable."""
    path: GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesByVariableUuidRequestPath

# Operation: update_repository_pipeline_variable
class PutRepositoriesPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
    repo_slug: str = Field(default=..., description="The repository slug or identifier within the specified workspace.")
    variable_uuid: str = Field(default=..., description="The unique UUID of the pipeline variable to update, used to identify the exact variable to modify.")
class PutRepositoriesPipelinesConfigVariablesRequestBody(StrictModel):
    """The updated variable"""
    body: PutRepositoriesPipelinesConfigVariablesBody | None = Field(default=None, description="The updated variable object containing the new values or configuration to apply to the repository pipeline variable.")
class PutRepositoriesPipelinesConfigVariablesRequest(StrictModel):
    """Updates an existing pipeline variable at the repository level, allowing modification of its value or configuration. Targets a specific variable by its UUID within the given workspace and repository."""
    path: PutRepositoriesPipelinesConfigVariablesRequestPath
    body: PutRepositoriesPipelinesConfigVariablesRequestBody | None = None

# Operation: delete_repository_pipeline_variable
class DeleteRepositoriesPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly-braces.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) that contains the pipeline variable to delete.")
    variable_uuid: str = Field(default=..., description="The UUID of the pipeline variable to delete, uniquely identifying the variable within the repository.")
class DeleteRepositoriesPipelinesConfigVariablesRequest(StrictModel):
    """Permanently deletes a specific pipeline variable from a repository. This removes the variable and its value from the repository's pipeline configuration."""
    path: DeleteRepositoriesPipelinesConfigVariablesRequestPath

# Operation: get_repository_property
class GetRepositoriesPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, identified by its slug or UUID wrapped in curly braces.")
    repo_slug: str = Field(default=..., description="The slug of the repository from which the property value will be retrieved.")
    app_key: str = Field(default=..., description="The unique key identifying the Connect app that owns the property.")
    property_name: str = Field(default=..., description="The name of the application property to retrieve from the repository.")
class GetRepositoriesPropertiesRequest(StrictModel):
    """Retrieves a specific application property value stored against a repository for a given Connect app. Useful for reading custom metadata or configuration values associated with a repository."""
    path: GetRepositoriesPropertiesRequestPath

# Operation: update_repository_property
class PutRepositoriesPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The repository container, identified by either the workspace slug or the workspace UUID wrapped in curly braces.")
    repo_slug: str = Field(default=..., description="The slug identifier of the repository within the specified workspace.")
    app_key: str = Field(default=..., description="The unique key identifying the Connect app that owns this property.")
    property_name: str = Field(default=..., description="The name of the application property to update, scoped to the specified Connect app.")
class PutRepositoriesPropertiesRequest(StrictModel):
    """Updates the value of a named application property stored against a specific repository. Properties are scoped to a Connect app and allow apps to persist custom metadata on repositories."""
    path: PutRepositoriesPropertiesRequestPath

# Operation: delete_repository_property
class DeleteRepositoriesPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, specified as either the workspace slug or the workspace UUID wrapped in curly braces.")
    repo_slug: str = Field(default=..., description="The slug identifier of the repository from which the property will be deleted.")
    app_key: str = Field(default=..., description="The unique key identifying the Connect app that owns the property to be deleted.")
    property_name: str = Field(default=..., description="The name of the application property to delete from the repository.")
class DeleteRepositoriesPropertiesRequest(StrictModel):
    """Deletes a specific application property value stored against a repository. Removes the property identified by the app key and property name from the target repository."""
    path: DeleteRepositoriesPropertiesRequestPath

# Operation: list_pull_requests
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequestQuery(StrictModel):
    state: Literal["OPEN", "MERGED", "DECLINED", "SUPERSEDED"] | None = Field(default=None, description="Filters results to pull requests in the specified state. Repeat this parameter multiple times to include pull requests from more than one state simultaneously.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequest(StrictModel):
    """Retrieves all pull requests for a specified repository, defaulting to open pull requests. Supports filtering by one or more states, as well as additional filtering and sorting options."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequestQuery | None = None

# Operation: create_pull_request
class PostRepositoriesPullrequestsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) identifying the target repository where the pull request will be created.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository.")
class PostRepositoriesPullrequestsRequestBody(StrictModel):
    """The new pull request.

The request URL you POST to becomes the destination repository URL. For this reason, you must specify an explicit source repository in the request object if you want to pull from a different repository (fork).

Since not all elements are required or even mutable, you only need to include the elements you want to initialize, such as the source branch and the title."""
    body: Pullrequest | None = Field(default=None, description="The pull request payload including required fields such as title and source branch, plus optional fields like destination branch, reviewers list (array of user UUID objects), description, close_source_branch flag, and draft flag.")
class PostRepositoriesPullrequestsRequest(StrictModel):
    """Creates a new pull request in the specified repository, authored by the authenticated user, merging a source branch into a destination branch (defaults to the repository's main branch if not specified)."""
    path: PostRepositoriesPullrequestsRequestPath
    body: PostRepositoriesPullrequestsRequestBody | None = None

# Operation: list_pull_request_activity
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsActivityRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsActivityRequest(StrictModel):
    """Retrieves a paginated activity log for all pull requests in a repository, including comments, updates (state changes), approvals, and request changes. Inline comments on files or code lines include an additional inline property with location details."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsActivityRequestPath

# Operation: get_pull_request
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace; UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdRequest(StrictModel):
    """Retrieves the details of a specific pull request within a repository, including its status, reviewers, and associated commits."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdRequestPath

# Operation: update_pull_request
class PutRepositoriesPullrequestsRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request to update.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that contains the pull request.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository.")
class PutRepositoriesPullrequestsRequestBody(StrictModel):
    """The pull request that is to be updated."""
    body: Pullrequest | None = Field(default=None, description="The request body containing the pull request fields to update, such as title, description, source branch, or destination branch.")
class PutRepositoriesPullrequestsRequest(StrictModel):
    """Updates an open pull request's metadata, such as its title, description, or source and destination branches. Only pull requests in an open state can be modified."""
    path: PutRepositoriesPullrequestsRequestPath
    body: PutRepositoriesPullrequestsRequestBody | None = None

# Operation: list_pull_request_activity_by_id
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdActivityRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request whose activity log should be retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdActivityRequest(StrictModel):
    """Retrieves a paginated activity log for a specific pull request, including reviewer comments, updates, approvals, and change requests. Inline comments on files or code lines include an additional inline property with location details."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdActivityRequestPath

# Operation: approve_pull_request
class PostRepositoriesPullrequestsApproveRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request to approve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUID values must be surrounded by curly-braces.")
class PostRepositoriesPullrequestsApproveRequest(StrictModel):
    """Approves the specified pull request on behalf of the authenticated user. This records the user's approval and contributes to any required approval count for merging."""
    path: PostRepositoriesPullrequestsApproveRequestPath

# Operation: unapprove_pull_request
class DeleteRepositoriesPullrequestsApproveRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request to unapprove.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class DeleteRepositoriesPullrequestsApproveRequest(StrictModel):
    """Removes the authenticated user's approval from the specified pull request. Use this to retract a previously submitted approval on a pull request in the given repository."""
    path: DeleteRepositoriesPullrequestsApproveRequestPath

# Operation: list_pull_request_comments
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric ID of the pull request whose comments should be retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsRequest(StrictModel):
    """Retrieves a paginated list of all comments on a pull request, including global comments, inline comments, and replies. Results are sorted oldest to newest by default and support filtering and sorting via query parameters."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsRequestPath

# Operation: create_pull_request_comment
class PostRepositoriesPullrequestsCommentsRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request on which the comment will be created.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesPullrequestsCommentsRequestBody(StrictModel):
    """The comment object."""
    body: PullrequestComment | None = Field(default=None, description="The request body containing the comment content and any optional metadata such as inline positioning or parent comment reference.")
class PostRepositoriesPullrequestsCommentsRequest(StrictModel):
    """Creates a new comment on a specified pull request in a Bitbucket repository. Returns the newly created comment object upon success."""
    path: PostRepositoriesPullrequestsCommentsRequestPath
    body: PostRepositoriesPullrequestsCommentsRequestBody | None = None

# Operation: get_pull_request_comment
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsByCommentIdRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to retrieve.", json_schema_extra={'format': 'int64'})
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request containing the comment.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug (URL-friendly name) or the workspace UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsByCommentIdRequest(StrictModel):
    """Retrieves a specific comment from a pull request by its comment ID. Returns the full comment details including content, author, and timestamps."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsByCommentIdRequestPath

# Operation: update_pull_request_comment
class PutRepositoriesPullrequestsCommentsRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to update.", json_schema_extra={'format': 'int64'})
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request containing the comment.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class PutRepositoriesPullrequestsCommentsRequestBody(StrictModel):
    """The contents of the updated comment."""
    body: PullrequestComment | None = Field(default=None, description="The request body containing the updated comment content to replace the existing comment.")
class PutRepositoriesPullrequestsCommentsRequest(StrictModel):
    """Updates the content of an existing comment on a specific pull request. Only the comment body can be modified through this operation."""
    path: PutRepositoriesPullrequestsCommentsRequestPath
    body: PutRepositoriesPullrequestsCommentsRequestBody | None = None

# Operation: delete_pull_request_comment
class DeleteRepositoriesPullrequestsCommentsRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to delete.", json_schema_extra={'format': 'int64'})
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request containing the comment.")
    repo_slug: str = Field(default=..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug (URL-friendly name) or the workspace UUID surrounded by curly-braces.")
class DeleteRepositoriesPullrequestsCommentsRequest(StrictModel):
    """Permanently deletes a specific comment from a pull request. This action is irreversible and removes the comment from the pull request discussion thread."""
    path: DeleteRepositoriesPullrequestsCommentsRequestPath

# Operation: resolve_pull_request_comment
class PostRepositoriesPullrequestsCommentsResolveRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment thread to resolve.", json_schema_extra={'format': 'int64'})
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request containing the comment thread.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that uniquely identifies the workspace containing the repository.")
class PostRepositoriesPullrequestsCommentsResolveRequest(StrictModel):
    """Marks a pull request comment thread as resolved, collapsing the discussion and indicating the concern has been addressed."""
    path: PostRepositoriesPullrequestsCommentsResolveRequestPath

# Operation: reopen_pull_request_comment_thread
class DeleteRepositoriesPullrequestsCommentsResolveRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment whose resolved status should be removed.", json_schema_extra={'format': 'int64'})
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request containing the comment thread.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class DeleteRepositoriesPullrequestsCommentsResolveRequest(StrictModel):
    """Reopens a previously resolved comment thread on a pull request by removing its resolved status. This allows further discussion to continue on the specified comment."""
    path: DeleteRepositoriesPullrequestsCommentsResolveRequestPath

# Operation: list_pull_request_commits
class GetRepositoriesPullrequestsCommitsRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request whose commits are being retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository; UUIDs must be surrounded by curly-braces.")
class GetRepositoriesPullrequestsCommitsRequest(StrictModel):
    """Retrieves a paginated list of commits associated with a specific pull request. These are the commits that will be merged into the destination branch upon pull request acceptance."""
    path: GetRepositoriesPullrequestsCommitsRequestPath

# Operation: decline_pull_request
class PostRepositoriesPullrequestsDeclineRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric ID of the pull request to decline.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesPullrequestsDeclineRequest(StrictModel):
    """Declines an open pull request in the specified repository, rejecting the proposed changes. Use this to formally close a pull request without merging."""
    path: PostRepositoriesPullrequestsDeclineRequestPath

# Operation: get_pull_request_diff
class GetRepositoriesPullrequestsDiffRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request whose diff you want to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository containing the pull request. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class GetRepositoriesPullrequestsDiffRequest(StrictModel):
    """Retrieves the file diff for a specific pull request, showing all line-level changes between the source and destination branches. Redirects to the repository diff endpoint using the revspec corresponding to the pull request."""
    path: GetRepositoriesPullrequestsDiffRequestPath

# Operation: get_pull_request_diffstat
class GetRepositoriesPullrequestsDiffstatRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request whose diff stat you want to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesPullrequestsDiffstatRequest(StrictModel):
    """Retrieves the diff stat for a specific pull request, showing a summary of file changes (additions, deletions, modifications) by redirecting to the repository diffstat endpoint using the pull request's revision spec."""
    path: GetRepositoriesPullrequestsDiffstatRequestPath

# Operation: merge_pull_request
class PostRepositoriesPullrequestsMergeRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request to merge.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) identifying the target repository.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository.")
class PostRepositoriesPullrequestsMergeRequestQuery(StrictModel):
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="When true, the merge runs asynchronously and returns immediately with a 202 status and a polling link in the Location header; when false (default), the merge runs synchronously and returns 200 on success, or 202 with a polling link if the merge exceeds the timeout threshold.")
class PostRepositoriesPullrequestsMergeRequestBody(StrictModel):
    message: str | None = Field(default=None, description="Custom commit message to use on the resulting merge commit; limited to 128 KiB in size.")
    close_source_branch: bool | None = Field(default=None, description="Whether to delete the source branch after a successful merge; falls back to the value set when the pull request was created if not provided, which defaults to false.")
    merge_strategy: Literal["merge_commit", "squash", "fast_forward", "squash_fast_forward", "rebase_fast_forward", "rebase_merge"] | None = Field(default=None, description="The strategy used to merge the pull request into the target branch; controls how commits are combined or rewritten.")
class PostRepositoriesPullrequestsMergeRequest(StrictModel):
    """Merges a pull request in the specified repository, combining the source branch into the target branch using the chosen merge strategy. Supports synchronous and asynchronous execution modes."""
    path: PostRepositoriesPullrequestsMergeRequestPath
    query: PostRepositoriesPullrequestsMergeRequestQuery | None = None
    body: PostRepositoriesPullrequestsMergeRequestBody | None = None

# Operation: get_pull_request_merge_task_status
class GetRepositoriesPullrequestsMergeTaskStatusRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request whose merge task status is being checked.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) identifying the repository containing the pull request.")
    task_id: str = Field(default=..., description="The task ID returned by the merge endpoint when the merge operation was accepted asynchronously with a 202 response.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) identifying the workspace that owns the repository.")
class GetRepositoriesPullrequestsMergeTaskStatusRequest(StrictModel):
    """Checks the status of an asynchronous pull request merge task using a task ID returned from a long-running merge operation. Returns PENDING while in progress, SUCCESS with the merged pull request object on completion, or an error if the merge failed."""
    path: GetRepositoriesPullrequestsMergeTaskStatusRequestPath

# Operation: get_pull_request_patch
class GetRepositoriesPullrequestsPatchRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request within the repository.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace; UUIDs must be surrounded by curly-braces.")
class GetRepositoriesPullrequestsPatchRequest(StrictModel):
    """Retrieves the patch file for a specific pull request, redirecting to the repository patch endpoint using the pull request's revision specification."""
    path: GetRepositoriesPullrequestsPatchRequestPath

# Operation: request_pull_request_changes
class PostRepositoriesPullrequestsRequestChangesRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request on which changes are being requested.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository containing the pull request. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces.")
class PostRepositoriesPullrequestsRequestChangesRequest(StrictModel):
    """Request changes on a pull request in a Bitbucket repository, indicating that the pull request requires modifications before it can be approved or merged."""
    path: PostRepositoriesPullrequestsRequestChangesRequestPath

# Operation: remove_pull_request_change_request
class DeleteRepositoriesPullrequestsRequestChangesRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request from which the change request will be removed.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) identifying the repository containing the pull request.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) identifying the workspace that owns the repository.")
class DeleteRepositoriesPullrequestsRequestChangesRequest(StrictModel):
    """Removes the authenticated user's change request from a pull request, withdrawing their objection and allowing the PR to proceed toward merge."""
    path: DeleteRepositoriesPullrequestsRequestChangesRequestPath

# Operation: list_pull_request_statuses
class GetRepositoriesPullrequestsStatusesRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request whose statuses should be retrieved.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace. UUID values must be surrounded by curly-braces.")
class GetRepositoriesPullrequestsStatusesRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A query string to filter the returned statuses using Bitbucket's filtering and sorting syntax, allowing you to narrow down results by specific fields or conditions.")
    sort: str | None = Field(default=None, description="The field name by which to sort the returned statuses using Bitbucket's filtering and sorting syntax. Defaults to created_on if not specified.")
class GetRepositoriesPullrequestsStatusesRequest(StrictModel):
    """Retrieves all commit statuses (such as CI/CD build results) associated with a specific pull request in a Bitbucket repository. Supports filtering and sorting to narrow down results."""
    path: GetRepositoriesPullrequestsStatusesRequestPath
    query: GetRepositoriesPullrequestsStatusesRequestQuery | None = None

# Operation: list_pull_request_tasks
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The unique numeric identifier of the pull request whose tasks should be listed.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A query string to filter the returned tasks using Bitbucket's filtering and sorting syntax.")
    sort: str | None = Field(default=None, description="The field by which results should be sorted using Bitbucket's filtering and sorting syntax. Defaults to created_on if not specified.")
    pagelen: int | None = Field(default=None, description="The number of task objects to include per page of results. Accepts values between 1 and 100; defaults to 10.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequest(StrictModel):
    """Retrieves a paginated list of tasks associated with a specific pull request in a repository. Supports filtering and sorting results by the 'task' field."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequestQuery | None = None

# Operation: create_pull_request_task
class PostRepositoriesPullrequestsTasksRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request on which the task will be created.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that identifies the Bitbucket workspace containing the repository.")
class PostRepositoriesPullrequestsTasksRequestBodyContent(StrictModel):
    raw: str = Field(default=..., validation_alias="raw", serialization_alias="raw", description="The text content of the task to be created on the pull request.")
class PostRepositoriesPullrequestsTasksRequestBody(StrictModel):
    """The contents of the task"""
    comment: PostRepositoriesPullrequestsTasksBodyComment | None = Field(default=None, description="An optional reference to a pull request comment by its ID; when provided, the task will be displayed beneath that comment in the pull request view.")
    pending: bool | None = Field(default=None, description="Indicates whether the task should be created in a pending (incomplete) state; when omitted, the default state is applied.")
    content: PostRepositoriesPullrequestsTasksRequestBodyContent
class PostRepositoriesPullrequestsTasksRequest(StrictModel):
    """Creates a new task on a specified pull request in a Bitbucket repository. Tasks can optionally be linked to a specific comment, causing them to appear beneath that comment in the pull request view."""
    path: PostRepositoriesPullrequestsTasksRequestPath
    body: PostRepositoriesPullrequestsTasksRequestBody

# Operation: get_pull_request_task
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksByTaskIdRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request containing the task.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    task_id: int = Field(default=..., description="The unique numeric ID of the task to retrieve.", json_schema_extra={'format': 'int64'})
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksByTaskIdRequest(StrictModel):
    """Retrieves a specific task associated with a pull request in the given repository. Returns full task details for the specified task ID."""
    path: GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksByTaskIdRequestPath

# Operation: update_pull_request_task
class PutRepositoriesPullrequestsTasksRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request that contains the task to update.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) identifying the repository containing the pull request.")
    task_id: int = Field(default=..., description="The unique numeric ID of the task to update.", json_schema_extra={'format': 'int64'})
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) identifying the workspace that owns the repository.")
class PutRepositoriesPullrequestsTasksRequestBodyContent(StrictModel):
    raw: str = Field(default=..., validation_alias="raw", serialization_alias="raw", description="The updated text content of the task.")
class PutRepositoriesPullrequestsTasksRequestBody(StrictModel):
    """The updated state and content of the task."""
    state: Literal["RESOLVED", "UNRESOLVED"] | None = Field(default=None, description="The resolution state of the task, indicating whether it is open or completed.")
    content: PutRepositoriesPullrequestsTasksRequestBodyContent
class PutRepositoriesPullrequestsTasksRequest(StrictModel):
    """Updates an existing task on a specific pull request, allowing changes to the task content and resolution state."""
    path: PutRepositoriesPullrequestsTasksRequestPath
    body: PutRepositoriesPullrequestsTasksRequestBody

# Operation: delete_pull_request_task
class DeleteRepositoriesPullrequestsTasksRequestPath(StrictModel):
    pull_request_id: int = Field(default=..., description="The numeric ID of the pull request from which the task will be deleted.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    task_id: int = Field(default=..., description="The unique numeric ID of the task to delete.", json_schema_extra={'format': 'int64'})
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class DeleteRepositoriesPullrequestsTasksRequest(StrictModel):
    """Permanently deletes a specific task from a pull request. This action cannot be undone and removes the task from the pull request's task list."""
    path: DeleteRepositoriesPullrequestsTasksRequestPath

# Operation: get_pull_request_property
class GetRepositoriesPullrequestsPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces).")
    repo_slug: str = Field(default=..., description="The slug of the repository containing the pull request.")
    pullrequest_id: str = Field(default=..., description="The unique numeric identifier of the pull request within the repository.")
    app_key: str = Field(default=..., description="The key identifying the Connect app that owns the property, used to namespace properties and avoid conflicts between apps.")
    property_name: str = Field(default=..., description="The name of the application property to retrieve, scoped under the specified Connect app key.")
class GetRepositoriesPullrequestsPropertiesRequest(StrictModel):
    """Retrieves a specific application property value stored against a pull request in a Bitbucket repository. Useful for reading custom metadata attached to a pull request by a Connect app."""
    path: GetRepositoriesPullrequestsPropertiesRequestPath

# Operation: update_pull_request_property
class PutRepositoriesPullrequestsPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces).")
    repo_slug: str = Field(default=..., description="The slug of the repository that contains the pull request.")
    pullrequest_id: str = Field(default=..., description="The unique numeric identifier of the pull request whose property is being updated.")
    app_key: str = Field(default=..., description="The key identifying the Connect app that owns this property, used to namespace properties and prevent collisions between apps.")
    property_name: str = Field(default=..., description="The name of the application property to update, scoped under the specified app key.")
class PutRepositoriesPullrequestsPropertiesRequest(StrictModel):
    """Update the value of a named application property stored against a specific pull request. Application properties allow Connect apps to attach custom metadata to Bitbucket resources."""
    path: PutRepositoriesPullrequestsPropertiesRequestPath

# Operation: delete_pull_request_property
class DeleteRepositoriesPullrequestsPropertiesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces).")
    repo_slug: str = Field(default=..., description="The slug of the repository containing the pull request.")
    pullrequest_id: str = Field(default=..., description="The unique numeric identifier of the pull request whose property should be deleted.")
    app_key: str = Field(default=..., description="The key identifying the Connect app that owns the property being deleted.")
    property_name: str = Field(default=..., description="The name of the application property to delete from the pull request.")
class DeleteRepositoriesPullrequestsPropertiesRequest(StrictModel):
    """Deletes a specific application property value stored against a pull request. Use this to remove custom metadata associated with a pull request by a Connect app."""
    path: DeleteRepositoriesPullrequestsPropertiesRequestPath

# Operation: list_repository_refs
class GetRepositoriesRefsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either the URL-friendly slug or the repository UUID enclosed in curly braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug or the workspace UUID enclosed in curly braces.")
class GetRepositoriesRefsRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A query string to filter the returned refs using Bitbucket's filtering and sorting syntax, allowing you to narrow results by properties such as name or type.")
    sort: str | None = Field(default=None, description="The field by which to sort results using Bitbucket's filtering and sorting syntax; specifying 'name' applies natural sort order so numerical segments are ordered numerically rather than lexicographically.")
class GetRepositoriesRefsRequest(StrictModel):
    """Retrieves all branches and tags (refs) for a given repository in a Bitbucket workspace. Results default to lexical ordering but can be sorted naturally by name using the sort parameter."""
    path: GetRepositoriesRefsRequestPath
    query: GetRepositoriesRefsRequestQuery | None = None

# Operation: list_branches
class GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A filter expression to narrow down the list of branches returned, following Bitbucket's filtering and sorting syntax.")
    sort: str | None = Field(default=None, description="The field by which to sort the returned branches, following Bitbucket's filtering and sorting syntax. Sorting by name applies natural ordering so numerical segments are interpreted as numbers rather than strings.")
class GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequest(StrictModel):
    """Retrieves all open branches for the specified repository, returned in the order the source control manager provides them. Supports filtering and natural sorting by branch name via query parameters."""
    path: GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequestQuery | None = None

# Operation: create_branch
class PostRepositoriesRefsBranchesRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (workspace ID) or as a UUID surrounded by curly-braces.")
class PostRepositoriesRefsBranchesRequest(StrictModel):
    """Creates a new branch in the specified repository by providing a branch name and a target commit hash. Requires authentication with appropriate repository access."""
    path: PostRepositoriesRefsBranchesRequestPath

# Operation: get_branch
class GetRepositoriesByWorkspaceByRepoSlugRefsBranchesByNameRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the branch to retrieve. For Git repositories, omit any prefix such as 'refs/heads' and provide only the bare branch name.")
    repo_slug: str = Field(default=..., description="The repository identifier, either as a human-readable slug or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a human-readable slug or as a UUID surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugRefsBranchesByNameRequest(StrictModel):
    """Retrieves details for a specific branch within a repository by its name. Authentication is required, and private repositories require appropriate account authorization."""
    path: GetRepositoriesByWorkspaceByRepoSlugRefsBranchesByNameRequestPath

# Operation: delete_branch
class DeleteRepositoriesRefsBranchesRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the branch to delete, provided without any prefix such as refs/heads.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace; UUIDs must be surrounded by curly-braces.")
class DeleteRepositoriesRefsBranchesRequest(StrictModel):
    """Deletes a branch from the specified repository. The main branch cannot be deleted; branch names should be provided without any prefix such as refs/heads."""
    path: DeleteRepositoriesRefsBranchesRequestPath

# Operation: list_repository_tags
class GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A query string to filter the returned tags using Bitbucket's filtering and sorting syntax.")
    sort: str | None = Field(default=None, description="The field by which to sort results using Bitbucket's filtering and sorting syntax. Sorting by the name field applies natural ordering, treating numeric segments as numbers rather than strings.")
class GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequest(StrictModel):
    """Retrieves all tags for a given repository in a workspace. Supports filtering and sorting, including natural sort order for version-style tag names when sorting by name."""
    path: GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequestQuery | None = None

# Operation: create_tag
class PostRepositoriesRefsTagsRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either the repository slug or the repository UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug or the workspace UUID surrounded by curly-braces.")
class PostRepositoriesRefsTagsRequestBody(StrictModel):
    body: Tag | None = Field(default=None, description="JSON document containing the tag name, the target commit hash, and an optional annotation message. A full commit hash is preferred over a short prefix to avoid ambiguity.")
class PostRepositoriesRefsTagsRequest(StrictModel):
    """Creates a new annotated tag in the specified repository, associating it with a target commit hash. An optional message may be provided; if omitted, a default message is generated automatically."""
    path: PostRepositoriesRefsTagsRequestPath
    body: PostRepositoriesRefsTagsRequestBody | None = None

# Operation: get_repository_tag
class GetRepositoriesByWorkspaceByRepoSlugRefsTagsByNameRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the tag to retrieve.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace.")
    workspace: str = Field(default=..., description="The workspace slug or UUID (surrounded by curly-braces) that uniquely identifies the workspace containing the repository.")
class GetRepositoriesByWorkspaceByRepoSlugRefsTagsByNameRequest(StrictModel):
    """Retrieves details for a specific tag in a repository, including the tag's target commit, tagger information, date, and associated links."""
    path: GetRepositoriesByWorkspaceByRepoSlugRefsTagsByNameRequestPath

# Operation: delete_tag
class DeleteRepositoriesRefsTagsRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the tag to delete, without any ref prefixes.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class DeleteRepositoriesRefsTagsRequest(StrictModel):
    """Permanently deletes a tag from the specified repository. Provide only the tag name without any ref prefixes such as refs/tags."""
    path: DeleteRepositoriesRefsTagsRequestPath

# Operation: get_repository_root_src
class GetRepositoriesByWorkspaceByRepoSlugSrcRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces.")
class GetRepositoriesByWorkspaceByRepoSlugSrcRequest(StrictModel):
    """Retrieves the root directory listing of a repository's main branch, automatically resolving the branch name and latest commit. This is a convenience redirect equivalent to browsing the root path of the main branch directly."""
    path: GetRepositoriesByWorkspaceByRepoSlugSrcRequestPath

# Operation: create_commit_with_files
class PostRepositoriesSrcRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID (surrounded by curly-braces) identifying the target repository.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that owns the repository.")
class PostRepositoriesSrcRequestQuery(StrictModel):
    message: str | None = Field(default=None, description="The commit message to associate with the new commit. When omitted, Bitbucket uses a default canned message.")
    author: str | None = Field(default=None, description="The author identity for the new commit in 'Full Name <email>' format. When omitted, the authenticated user's display name and primary email are used; anonymous commits are not permitted.")
    files: str | None = Field(default=None, description="One or more repository-relative file paths that this request is manipulating. Listing a path here without a corresponding file field body causes that file to be deleted; paths not referenced in this field or as file fields are carried over unchanged from the parent commit.")
    branch: str | None = Field(default=None, description="The name of the branch on which to create the new commit. If omitted, the commit is placed on the repository's main branch. Providing a new branch name creates that branch; providing an existing branch name advances it, with optional parent SHA1 validation to guard against concurrent changes.")
class PostRepositoriesSrcRequest(StrictModel):
    """Creates a new commit in a repository by uploading, modifying, or deleting files via multipart/form-data or URL-encoded form data. Supports setting commit message, author, target branch, and file attributes such as executable or symlink."""
    path: PostRepositoriesSrcRequestPath
    query: PostRepositoriesSrcRequestQuery | None = None

# Operation: get_repository_src
class GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequestPath(StrictModel):
    commit: str = Field(default=..., description="The full SHA1 hash of the commit to retrieve file or directory contents from.")
    path: str = Field(default=..., description="The path to the target file or directory within the repository, relative to the repository root. Append a trailing slash when targeting the root directory.")
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly braces.")
    workspace: str = Field(default=..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly braces.")
class GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequestQuery(StrictModel):
    format_: Literal["meta", "rendered"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Controls the response format: 'meta' returns JSON metadata about the file or directory (size, attributes, links) instead of raw contents; 'rendered' returns HTML-rendered markup for supported plain-text file types (.md, .rst, .textile, etc.) instead of raw contents.")
    q: str | None = Field(default=None, description="A filter expression to narrow directory listing results using Bitbucket's filtering syntax, such as filtering by file size or attributes.")
    sort: str | None = Field(default=None, description="A sort expression to order directory listing results using Bitbucket's sorting syntax, such as sorting by size ascending or descending.")
    max_depth: int | None = Field(default=None, description="Maximum directory depth to recurse into when listing directory contents. Performs a breadth-first traversal; very large values may cause the request to time out with a 555 error. Defaults to 1 (non-recursive, direct children only).")
class GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequest(StrictModel):
    """Retrieve the raw contents of a file or a paginated directory listing at a specific commit in a Bitbucket repository. Supports metadata retrieval, rendered markup output, recursive directory traversal, and filtering/sorting for directory listings."""
    path: GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequestPath
    query: GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequestQuery | None = None

# Operation: list_repository_watchers
class GetRepositoriesWatchersRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces.")
class GetRepositoriesWatchersRequest(StrictModel):
    """Retrieves a paginated list of all users watching the specified repository. Useful for understanding a repository's audience and engagement."""
    path: GetRepositoriesWatchersRequestPath

# Operation: list_workspace_snippets
class GetSnippetsByWorkspaceRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetSnippetsByWorkspaceRequestQuery(StrictModel):
    role: Literal["owner", "contributor", "member"] | None = Field(default=None, description="Filters results to snippets where the authenticated user holds the specified role: owner (created the snippet), contributor (has edit access), or member (has view access).")
class GetSnippetsByWorkspaceRequest(StrictModel):
    """Retrieves all snippets owned by a specific workspace, optionally filtered by the authenticated user's role within that workspace."""
    path: GetSnippetsByWorkspaceRequestPath
    query: GetSnippetsByWorkspaceRequestQuery | None = None

# Operation: create_workspace_snippet
class PostSnippetsForWorkspaceRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace in which to create the snippet, identified by either its slug (human-readable ID) or its UUID surrounded by curly-braces.")
class PostSnippetsForWorkspaceRequest(StrictModel):
    """Creates a new snippet scoped to the specified workspace. Behaves identically to the global snippet creation endpoint, but associates the snippet with the given workspace."""
    path: PostSnippetsForWorkspaceRequestPath

# Operation: get_snippet
class GetSnippetsByWorkspaceByEncodedIdRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to retrieve.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g. a short name) or as a UUID surrounded by curly braces.")
class GetSnippetsByWorkspaceByEncodedIdRequest(StrictModel):
    """Retrieves a single snippet by its ID within a workspace. Supports multiple response content types: application/json (default, metadata and file links only), multipart/related (full snippet including file contents in one response), and multipart/form-data (flat structure with file contents)."""
    path: GetSnippetsByWorkspaceByEncodedIdRequestPath

# Operation: update_snippet
class PutSnippetsForWorkspaceForEncodedIdRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to update.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g. a short name) or as a UUID surrounded by curly braces.")
class PutSnippetsForWorkspaceForEncodedIdRequest(StrictModel):
    """Updates an existing snippet in the specified workspace, allowing changes to its title and files via differential payloads. Supports adding, updating, or deleting files atomically using JSON, multipart/related, or multipart/form-data content types."""
    path: PutSnippetsForWorkspaceForEncodedIdRequestPath

# Operation: delete_snippet
class DeleteSnippetsForWorkspaceForEncodedIdRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to delete.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g. my-team) or as a UUID surrounded by curly-braces.")
class DeleteSnippetsForWorkspaceForEncodedIdRequest(StrictModel):
    """Permanently deletes a specific snippet from the given workspace. Returns an empty response upon successful deletion."""
    path: DeleteSnippetsForWorkspaceForEncodedIdRequestPath

# Operation: list_snippet_comments
class GetSnippetsByWorkspaceByEncodedIdCommentsRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet whose comments are being retrieved.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetSnippetsByWorkspaceByEncodedIdCommentsRequest(StrictModel):
    """Retrieves a paginated list of all comments on a specific snippet within a workspace. Results are sorted oldest to newest by default and can be overridden with the sort query parameter."""
    path: GetSnippetsByWorkspaceByEncodedIdCommentsRequestPath

# Operation: create_snippet_comment
class PostSnippetsCommentsRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to comment on.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g. my-team) or as a UUID surrounded by curly-braces.")
class PostSnippetsCommentsRequestBody(StrictModel):
    """The contents of the new comment."""
    body: SnippetComment | None = Field(default=None, description="The comment payload. Must include the required field `content.raw` containing the comment text. Optionally include `parent.id` to post a threaded reply to an existing comment.")
class PostSnippetsCommentsRequest(StrictModel):
    """Creates a new comment on a specific snippet in a workspace. Supports threaded replies by including a parent comment ID in the request body."""
    path: PostSnippetsCommentsRequestPath
    body: PostSnippetsCommentsRequestBody | None = None

# Operation: get_snippet_comment
class GetSnippetsByWorkspaceByEncodedIdCommentsByCommentIdRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to retrieve.", json_schema_extra={'format': 'int64'})
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet, as assigned by Bitbucket.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetSnippetsByWorkspaceByEncodedIdCommentsByCommentIdRequest(StrictModel):
    """Retrieves a specific comment on a snippet within a workspace. Returns the full comment details for the given comment ID."""
    path: GetSnippetsByWorkspaceByEncodedIdCommentsByCommentIdRequestPath

# Operation: update_snippet_comment
class PutSnippetsCommentsRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to update.", json_schema_extra={'format': 'int64'})
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to which the comment belongs.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (e.g. a short name) or as a UUID surrounded by curly-braces.")
class PutSnippetsCommentsRequestBody(StrictModel):
    """The contents to update the comment to."""
    body: SnippetComment | None = Field(default=None, description="The request body containing the updated comment data. Must include `content.raw` with the new comment text in raw markup format.")
class PutSnippetsCommentsRequest(StrictModel):
    """Updates an existing comment on a snippet. Only the comment's author can make updates, and the request body must include the `content.raw` field."""
    path: PutSnippetsCommentsRequestPath
    body: PutSnippetsCommentsRequestBody | None = None

# Operation: delete_snippet_comment
class DeleteSnippetsCommentsRequestPath(StrictModel):
    comment_id: int = Field(default=..., description="The unique numeric identifier of the comment to delete.", json_schema_extra={'format': 'int64'})
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet, as assigned by Bitbucket.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
class DeleteSnippetsCommentsRequest(StrictModel):
    """Permanently deletes a specific comment from a snippet. This action is restricted to the comment author, snippet creator, or a workspace admin."""
    path: DeleteSnippetsCommentsRequestPath

# Operation: list_snippet_commits
class GetSnippetsByWorkspaceByEncodedIdCommitsRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet whose commit history is being retrieved.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
class GetSnippetsByWorkspaceByEncodedIdCommitsRequest(StrictModel):
    """Retrieves the commit history for a specific snippet, returning all changes made over time. Useful for auditing edits or tracking the evolution of a snippet's content."""
    path: GetSnippetsByWorkspaceByEncodedIdCommitsRequestPath

# Operation: get_snippet_commit_changes
class GetSnippetsByWorkspaceByEncodedIdCommitsByRevisionRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet whose commit changes you want to retrieve.")
    revision: str = Field(default=..., description="The SHA1 hash of the commit whose changes you want to inspect.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetSnippetsByWorkspaceByEncodedIdCommitsByRevisionRequest(StrictModel):
    """Retrieves the changes made to a specific snippet in a given commit. Use this to inspect what was modified in a snippet at a particular point in its history."""
    path: GetSnippetsByWorkspaceByEncodedIdCommitsByRevisionRequestPath

# Operation: get_snippet_file_content
class GetSnippetsByWorkspaceByEncodedIdFilesByPathRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to retrieve the file from.")
    path: str = Field(default=..., description="The relative path to the target file within the snippet.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
class GetSnippetsByWorkspaceByEncodedIdFilesByPathRequest(StrictModel):
    """Retrieves the raw content of a specific file within a snippet at its HEAD revision, bypassing the need to first fetch the snippet and extract versioned file links."""
    path: GetSnippetsByWorkspaceByEncodedIdFilesByPathRequestPath

# Operation: check_snippet_watch_status
class GetSnippetsWatchRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to check watch status for.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
class GetSnippetsWatchRequest(StrictModel):
    """Checks whether the currently authenticated user is watching a specific snippet. Returns 204 if watching, 404 if not watching or if the request is made anonymously."""
    path: GetSnippetsWatchRequestPath

# Operation: watch_snippet
class PutSnippetsWatchRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to watch.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class PutSnippetsWatchRequest(StrictModel):
    """Subscribes the authenticated user to watch a specific snippet, enabling notifications for changes. Returns 204 No Content on success."""
    path: PutSnippetsWatchRequestPath

# Operation: unwatch_snippet
class DeleteSnippetsWatchRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to stop watching.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces.")
class DeleteSnippetsWatchRequest(StrictModel):
    """Stops watching a specific snippet so the authenticated user no longer receives updates for it. Returns 204 No Content on success."""
    path: DeleteSnippetsWatchRequestPath

# Operation: get_snippet_revision
class GetSnippetsByWorkspaceByEncodedIdByNodeIdRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to retrieve.")
    node_id: str = Field(default=..., description="The commit revision SHA1 hash identifying the specific historical version of the snippet to retrieve.")
    workspace: str = Field(default=..., description="The workspace containing the snippet, specified as either the workspace slug or the workspace UUID surrounded by curly-braces.")
class GetSnippetsByWorkspaceByEncodedIdByNodeIdRequest(StrictModel):
    """Retrieves the file contents of a snippet at a specific historical revision identified by a commit SHA1. Unlike the standard snippet endpoint, this returns the snapshot of file contents at the given revision rather than the current version."""
    path: GetSnippetsByWorkspaceByEncodedIdByNodeIdRequestPath

# Operation: update_snippet_at_revision
class PutSnippetsForWorkspaceForEncodedIdForNodeIdRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to update.")
    node_id: str = Field(default=..., description="The SHA1 commit revision that must match the snippet's current HEAD; the update is rejected if this is not the most recent revision.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces.")
class PutSnippetsForWorkspaceForEncodedIdForNodeIdRequest(StrictModel):
    """Updates a snippet only if the specified commit revision matches the current HEAD, acting as a Compare-And-Swap (CAS) operation to prevent overwriting concurrent modifications. Fails with a 405 if the provided revision is not the latest."""
    path: PutSnippetsForWorkspaceForEncodedIdForNodeIdRequestPath

# Operation: delete_snippet_revision
class DeleteSnippetsForWorkspaceForEncodedIdForNodeIdRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to delete.")
    node_id: str = Field(default=..., description="The SHA1 commit hash identifying the specific revision of the snippet; must point to the latest commit or the request will fail.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
class DeleteSnippetsForWorkspaceForEncodedIdForNodeIdRequest(StrictModel):
    """Deletes a snippet at a specific versioned commit, but only if that commit is the latest revision. To delete a snippet unconditionally, use the base snippet delete endpoint instead."""
    path: DeleteSnippetsForWorkspaceForEncodedIdForNodeIdRequestPath

# Operation: get_snippet_file_contents
class GetSnippetsByWorkspaceByEncodedIdByNodeIdFilesByPathRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to retrieve the file from.")
    node_id: str = Field(default=..., description="The commit revision SHA1 hash identifying the specific version of the snippet to retrieve the file from.")
    path: str = Field(default=..., description="The path to the target file within the snippet, relative to the snippet's root.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly braces.")
class GetSnippetsByWorkspaceByEncodedIdByNodeIdFilesByPathRequest(StrictModel):
    """Retrieves the raw contents of a specific file within a snippet at a given commit revision. The response includes appropriate Content-Type and Content-Disposition headers based on the file's name and type."""
    path: GetSnippetsByWorkspaceByEncodedIdByNodeIdFilesByPathRequestPath

# Operation: get_snippet_diff
class GetSnippetsDiffRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet whose diff is being retrieved.")
    revision: str = Field(default=..., description="A revspec expression identifying the commit or range to diff, such as a commit SHA1, a branch/tag ref name, or a two-dot compare expression to diff between two refs.")
    workspace: str = Field(default=..., description="The workspace containing the snippet, specified as either the workspace slug or the workspace UUID surrounded by curly braces.")
class GetSnippetsDiffRequestQuery(StrictModel):
    path: str | None = Field(default=None, description="When provided, restricts the diff output to only the specified file path within the snippet, rather than showing all changed files.")
class GetSnippetsDiffRequest(StrictModel):
    """Retrieves the diff of a specific snippet commit against its first parent, showing what changed in that revision. Optionally filter the diff to a single file using the path parameter."""
    path: GetSnippetsDiffRequestPath
    query: GetSnippetsDiffRequestQuery | None = None

# Operation: get_snippet_patch
class GetSnippetsPatchRequestPath(StrictModel):
    encoded_id: str = Field(default=..., description="The unique identifier of the snippet to retrieve the patch for.")
    revision: str = Field(default=..., description="A revspec expression identifying the commit or range to patch against its first parent, such as a commit SHA1, a ref name, or a range expression using double-dot notation.")
    workspace: str = Field(default=..., description="The workspace containing the snippet, specified as either the workspace slug or the workspace UUID surrounded by curly braces.")
class GetSnippetsPatchRequest(StrictModel):
    """Retrieves the patch of a specific snippet commit against its first parent, including commit headers such as username and message. Unlike a diff, this returns separate patches for each commit on the second parent's ancestry up to the oldest common ancestor for merge commits."""
    path: GetSnippetsPatchRequestPath

# Operation: search_team_code
class GetTeamsSearchCodeRequestPath(StrictModel):
    username: str = Field(default=..., description="The team account to search within, specified as either the team's username or its UUID wrapped in curly braces.")
class GetTeamsSearchCodeRequestQuery(StrictModel):
    search_query: str = Field(default=..., description="The search query string used to find matching code; supports advanced syntax such as scoping to a specific repository using the `repo:` qualifier, and combining multiple terms.")
    page: int | None = Field(default=None, description="The page number of search results to retrieve, starting at 1 for the first page.", json_schema_extra={'format': 'int32'})
    pagelen: int | None = Field(default=None, description="The number of search results to return per page; controls pagination granularity.", json_schema_extra={'format': 'int32'})
class GetTeamsSearchCodeRequest(StrictModel):
    """Search across all repositories belonging to a team for code matching a given query, with results that can match file content, file paths, or both. Supports advanced query syntax for scoping searches to specific repositories and customizing returned fields."""
    path: GetTeamsSearchCodeRequestPath
    query: GetTeamsSearchCodeRequestQuery

# Operation: get_email
class GetUserEmailsByEmailRequestPath(StrictModel):
    email: str = Field(default=..., description="The full email address to look up among the authenticated user's registered email addresses.")
class GetUserEmailsByEmailRequest(StrictModel):
    """Retrieves details for a specific email address belonging to the authenticated user. The response includes whether the address has been confirmed and whether it is the user's primary email."""
    path: GetUserEmailsByEmailRequestPath

# Operation: list_workspaces
class GetUserWorkspacesRequestQuery(StrictModel):
    sort: str | None = Field(default=None, description="Property name to sort the returned workspaces by; only sorting by slug is supported.")
    administrator: bool | None = Field(default=None, description="When set to true, returns only workspaces where the caller has admin permissions; when set to false, returns only workspaces where the caller does not have admin permissions. Omit to return all accessible workspaces regardless of admin status.")
class GetUserWorkspacesRequest(StrictModel):
    """Retrieves all workspaces accessible to the authenticated user, including each workspace's details and the caller's admin permissions status. Supports filtering by admin role, sorting, and pagination."""
    query: GetUserWorkspacesRequestQuery | None = None

# Operation: get_workspace_permission
class GetUserWorkspacesPermissionRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
class GetUserWorkspacesPermissionRequest(StrictModel):
    """Retrieves the calling user's effective (highest) permission role for a specified workspace. If the user belongs to multiple groups with different roles, only the highest privilege level is returned."""
    path: GetUserWorkspacesPermissionRequestPath

# Operation: list_workspace_repository_permissions_for_user
class GetUserWorkspacesPermissionsRepositoriesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
class GetUserWorkspacesPermissionsRepositoriesRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A filter expression to narrow results by repository or permission level, using Bitbucket's filtering and sorting syntax. Values must be URL-encoded (e.g., encode `=` as `%3D`).")
    sort: str | None = Field(default=None, description="The response property name to sort results by, using Bitbucket's filtering and sorting syntax.")
class GetUserWorkspacesPermissionsRepositoriesRequest(StrictModel):
    """Retrieves each repository within the specified workspace where the authenticated user has been explicitly granted access, along with their highest effective permission level (admin, write, or read). Public repositories without explicit grants are excluded from results."""
    path: GetUserWorkspacesPermissionsRepositoriesRequestPath
    query: GetUserWorkspacesPermissionsRepositoriesRequestQuery | None = None

# Operation: get_user
class GetUsersRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The identifier of the user to retrieve, accepted as either an Atlassian Account ID or a UUID wrapped in curly braces.")
class GetUsersRequest(StrictModel):
    """Retrieves public profile information for a specified Bitbucket user account. Private profiles omit location, website, and account creation date fields."""
    path: GetUsersRequestPath

# Operation: list_user_gpg_keys
class GetUsersBySelectedUserGpgKeysRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The identifier of the user whose GPG keys will be listed, accepted as either an Atlassian Account ID or an account UUID wrapped in curly braces.")
class GetUsersBySelectedUserGpgKeysRequest(StrictModel):
    """Retrieves a paginated list of GPG public keys associated with a specified Bitbucket user. The key and subkeys fields can be included in the response using partial response syntax."""
    path: GetUsersBySelectedUserGpgKeysRequestPath

# Operation: add_gpg_key
class PostUsersGpgKeysRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The account identifier for the target user, accepted as either an Atlassian Account ID or a UUID surrounded by curly-braces.")
class PostUsersGpgKeysRequestBody(StrictModel):
    """The new GPG key object."""
    body: GpgAccountKey | None = Field(default=None, description="The request body containing the GPG public key to be added to the user account.")
class PostUsersGpgKeysRequest(StrictModel):
    """Adds a new GPG public key to the specified user account, enabling cryptographic verification of commits and other signed content. Returns the newly created GPG key object upon success."""
    path: PostUsersGpgKeysRequestPath
    body: PostUsersGpgKeysRequestBody | None = None

# Operation: get_user_gpg_key
class GetUsersBySelectedUserGpgKeysByFingerprintRequestPath(StrictModel):
    fingerprint: str = Field(default=..., description="The fingerprint uniquely identifying the GPG key to retrieve.")
    selected_user: str = Field(default=..., description="The user whose GPG key is being retrieved, specified as either an Atlassian Account ID or a UUID surrounded by curly-braces.")
class GetUsersBySelectedUserGpgKeysByFingerprintRequest(StrictModel):
    """Retrieves a specific GPG public key belonging to a user, identified by its fingerprint. Supports partial responses to include the full key and subkey fields."""
    path: GetUsersBySelectedUserGpgKeysByFingerprintRequestPath

# Operation: delete_user_gpg_key
class DeleteUsersGpgKeysRequestPath(StrictModel):
    fingerprint: str = Field(default=..., description="The unique fingerprint identifying the GPG key to delete, used to locate the specific key within the user's account.")
    selected_user: str = Field(default=..., description="The account identifier for the target user, accepted as either an Atlassian Account ID or a UUID surrounded by curly-braces.")
class DeleteUsersGpgKeysRequest(StrictModel):
    """Permanently removes a specific GPG public key from a user's account, identified by its fingerprint. This action cannot be undone."""
    path: DeleteUsersGpgKeysRequestPath

# Operation: get_user_app_property
class GetUsersPropertiesRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The identifier of the target user account, either as an Atlassian Account ID or a UUID wrapped in curly braces.")
    app_key: str = Field(default=..., description="The unique key identifying the Connect app whose property is being retrieved.")
    property_name: str = Field(default=..., description="The name of the application property to retrieve from the specified user and Connect app.")
class GetUsersPropertiesRequest(StrictModel):
    """Retrieves a specific application property value stored against a Bitbucket user account. Use this to read Connect app metadata associated with a particular user."""
    path: GetUsersPropertiesRequestPath

# Operation: update_user_app_property
class PutUsersPropertiesRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The unique identifier of the target user account, either as an Atlassian Account ID or a UUID wrapped in curly braces.")
    app_key: str = Field(default=..., description="The key identifying the Connect app whose property is being updated. This must correspond to a registered Connect app key.")
    property_name: str = Field(default=..., description="The name of the application property to update. This identifies which property value will be overwritten for the specified user and app.")
class PutUsersPropertiesRequest(StrictModel):
    """Updates the value of a named application property stored against a specific user for a given Connect app. Use this to persist or overwrite app-specific metadata associated with a Bitbucket user account."""
    path: PutUsersPropertiesRequestPath

# Operation: delete_user_app_property
class DeleteUsersPropertiesRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The identifier of the target user account, either as an Atlassian Account ID or a UUID wrapped in curly braces.")
    app_key: str = Field(default=..., description="The unique key identifying the Bitbucket Connect app whose property is being deleted.")
    property_name: str = Field(default=..., description="The name of the application property to delete from the user's account.")
class DeleteUsersPropertiesRequest(StrictModel):
    """Deletes a specific application property value stored against a Bitbucket user account. Targets a property by its Connect app key and property name."""
    path: DeleteUsersPropertiesRequestPath

# Operation: search_user_code
class GetUsersSearchCodeRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The unique identifier of the user whose repositories will be searched — either an Atlassian Account ID or a UUID wrapped in curly braces.")
class GetUsersSearchCodeRequestQuery(StrictModel):
    search_query: str = Field(default=..., description="The search query string used to find matching code; supports advanced syntax such as scoping results to a specific repository using the `repo:` qualifier and combining multiple terms.")
    page: int | None = Field(default=None, description="The page number of search results to retrieve, starting at 1 for the first page.", json_schema_extra={'format': 'int32'})
    pagelen: int | None = Field(default=None, description="The number of search results to return per page; controls pagination granularity.", json_schema_extra={'format': 'int32'})
class GetUsersSearchCodeRequest(StrictModel):
    """Search across all repositories belonging to a specified user, matching against file content and/or file paths. Supports advanced query syntax including repository-scoped searches and field expansion for richer results."""
    path: GetUsersSearchCodeRequestPath
    query: GetUsersSearchCodeRequestQuery

# Operation: list_user_ssh_keys
class GetUsersBySelectedUserSshKeysRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The identifier of the user whose SSH keys will be listed — either an Atlassian Account ID or an account UUID wrapped in curly braces.")
class GetUsersBySelectedUserSshKeysRequest(StrictModel):
    """Retrieves a paginated list of SSH public keys associated with the specified user account. Useful for auditing or managing a user's SSH authentication credentials."""
    path: GetUsersBySelectedUserSshKeysRequestPath

# Operation: add_ssh_key
class PostUsersSshKeysRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The account identifier for the target user, either as an Atlassian Account ID or as an account UUID surrounded by curly braces.")
class PostUsersSshKeysRequestBody(StrictModel):
    """The new SSH key object. Note that the username property has been deprecated due to [privacy changes](https://developer.atlassian.com/cloud/bitbucket/bitbucket-api-changes-gdpr/#removal-of-usernames-from-user-referencing-apis)."""
    body: SshAccountKey | None = Field(default=None, description="The SSH public key payload to add to the user account, including the key type, public key string, and optional label.")
class PostUsersSshKeysRequest(StrictModel):
    """Adds a new SSH public key to the specified user account. Returns the resulting SSH key object upon success."""
    path: PostUsersSshKeysRequestPath
    body: PostUsersSshKeysRequestBody | None = None

# Operation: get_user_ssh_key
class GetUsersBySelectedUserSshKeysByKeyIdRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique identifier (UUID) of the SSH key to retrieve.")
    selected_user: str = Field(default=..., description="The user account to retrieve the SSH key from, specified as either an Atlassian Account ID or an account UUID wrapped in curly braces.")
class GetUsersBySelectedUserSshKeysByKeyIdRequest(StrictModel):
    """Retrieves a specific SSH public key belonging to a user account. Useful for inspecting key details such as label, value, and creation date for a given user."""
    path: GetUsersBySelectedUserSshKeysByKeyIdRequestPath

# Operation: update_ssh_key
class PutUsersSshKeysRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique UUID identifier of the SSH key to update.")
    selected_user: str = Field(default=..., description="The account identifier for the target user, either as an Atlassian Account ID or as an account UUID surrounded by curly braces.")
class PutUsersSshKeysRequestBody(StrictModel):
    """The updated SSH key object"""
    body: SshAccountKey | None = Field(default=None, description="Request body containing the SSH key fields to update. Only the comment/label field is supported for updates.")
class PutUsersSshKeysRequest(StrictModel):
    """Updates the comment/label of a specific SSH public key on a user's account. Note that only the comment field can be modified; to change the key itself, delete and re-add it."""
    path: PutUsersSshKeysRequestPath
    body: PutUsersSshKeysRequestBody | None = None

# Operation: delete_user_ssh_key
class DeleteUsersSshKeysRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique UUID identifier of the SSH key to delete.")
    selected_user: str = Field(default=..., description="The account identifier for the target user, accepted as either an Atlassian Account ID or an account UUID wrapped in curly-braces.")
class DeleteUsersSshKeysRequest(StrictModel):
    """Permanently removes a specific SSH public key from a user's account, revoking any access associated with that key."""
    path: DeleteUsersSshKeysRequestPath

# Operation: get_workspace
class GetWorkspacesByWorkspaceRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier for the workspace, accepted as either a slug (short name) or a UUID wrapped in curly braces.")
class GetWorkspacesByWorkspaceRequest(StrictModel):
    """Retrieves details for a specific Bitbucket workspace. Returns workspace metadata including settings, links, and membership information."""
    path: GetWorkspacesByWorkspaceRequestPath

# Operation: list_workspace_webhooks
class GetWorkspacesByWorkspaceHooksRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier for the workspace, accepted as either a slug (short name) or a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceHooksRequest(StrictModel):
    """Retrieves a paginated list of all webhooks installed on the specified workspace. Useful for auditing or managing webhook integrations configured at the workspace level."""
    path: GetWorkspacesByWorkspaceHooksRequestPath

# Operation: get_workspace_webhook
class GetWorkspacesByWorkspaceHooksByUidRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the installed webhook to retrieve.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceHooksByUidRequest(StrictModel):
    """Retrieves the details of a specific webhook installed on a workspace, identified by its unique ID. Useful for inspecting webhook configuration, events, and status for a given workspace."""
    path: GetWorkspacesByWorkspaceHooksByUidRequestPath

# Operation: update_workspace_webhook
class PutWorkspacesHooksRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the installed webhook subscription to update.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
class PutWorkspacesHooksRequest(StrictModel):
    """Updates an existing webhook subscription for a workspace, allowing modification of its description, URL, secret, active status, and subscribed events. The webhook secret is used to generate an HMAC hex digest signature sent in the X-Hub-Signature header on delivery."""
    path: PutWorkspacesHooksRequestPath

# Operation: delete_workspace_webhook
class DeleteWorkspacesHooksRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the installed webhook subscription to delete.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class DeleteWorkspacesHooksRequest(StrictModel):
    """Permanently deletes a specific webhook subscription from a workspace, stopping all future event deliveries for that hook."""
    path: DeleteWorkspacesHooksRequestPath

# Operation: list_workspace_members
class GetWorkspacesByWorkspaceMembersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier of the workspace, either as a slug (e.g., a short name/alias) or as a UUID surrounded by curly braces.")
class GetWorkspacesByWorkspaceMembersRequest(StrictModel):
    """Retrieves all members belonging to the specified workspace. Supports filtering by email address (up to 90 at a time) when called by a workspace administrator, integration, or workspace access token."""
    path: GetWorkspacesByWorkspaceMembersRequestPath

# Operation: get_workspace_member
class GetWorkspacesByWorkspaceMembersByMemberRequestPath(StrictModel):
    member: str = Field(default=..., description="The unique identifier of the member to look up, either their UUID or Atlassian account ID.")
    workspace: str = Field(default=..., description="The unique identifier of the workspace, either its slug (human-readable ID) or its UUID wrapped in curly braces.")
class GetWorkspacesByWorkspaceMembersByMemberRequest(StrictModel):
    """Retrieves the membership details for a specific user in a given workspace, including the full User and Workspace objects associated with that membership."""
    path: GetWorkspacesByWorkspaceMembersByMemberRequestPath

# Operation: list_workspace_permissions
class GetWorkspacesPermissionsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug (short name) or the workspace UUID enclosed in curly braces.")
class GetWorkspacesPermissionsRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A filter expression to narrow results by permission level, using Bitbucket's filtering and sorting syntax.")
class GetWorkspacesPermissionsRequest(StrictModel):
    """Retrieves all members of a workspace along with their assigned permission levels (owner, collaborator, or member). Results can be filtered by permission level using the query parameter."""
    path: GetWorkspacesPermissionsRequestPath
    query: GetWorkspacesPermissionsRequestQuery | None = None

# Operation: list_workspace_repository_permissions
class GetWorkspacesByWorkspacePermissionsRepositoriesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug or the workspace UUID enclosed in curly braces.")
class GetWorkspacesByWorkspacePermissionsRepositoriesRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A query string to filter results by repository, user, or permission level using Bitbucket's filtering syntax; values must be URL-encoded.")
    sort: str | None = Field(default=None, description="The response property name to sort results by, using Bitbucket's sorting syntax to control the order of returned permissions.")
class GetWorkspacesByWorkspacePermissionsRepositoriesRequest(StrictModel):
    """Retrieves the effective repository permissions for all repositories in a workspace, returning the highest permission level each user holds. Accessible only to workspace admins; results can be filtered and sorted by repository, user, or permission level."""
    path: GetWorkspacesByWorkspacePermissionsRepositoriesRequestPath
    query: GetWorkspacesByWorkspacePermissionsRepositoriesRequestQuery | None = None

# Operation: list_repository_user_permissions_workspace
class GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequestPath(StrictModel):
    repo_slug: str = Field(default=..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces.")
class GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="A filter expression to narrow results by user or permission level, following Bitbucket's filtering and sorting syntax. Values must be URL-encoded.")
    sort: str | None = Field(default=None, description="A response property name to sort results by, following Bitbucket's sorting syntax, such as a user display name field.")
class GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequest(StrictModel):
    """Returns the effective permission level for each user in a specified repository within a workspace. Only users with admin permission on the repository can access this resource."""
    path: GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequestPath
    query: GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequestQuery | None = None

# Operation: list_workspace_runners
class GetWorkspacesByWorkspacePipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier for the workspace, accepted as either a slug (short name) or a UUID enclosed in curly braces.")
class GetWorkspacesByWorkspacePipelinesConfigRunnersRequest(StrictModel):
    """Retrieve all pipeline runners configured for a specific workspace. Runners are used to execute Bitbucket Pipelines builds within the workspace."""
    path: GetWorkspacesByWorkspacePipelinesConfigRunnersRequestPath

# Operation: create_workspace_runner
class PostWorkspacesPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug (human-readable short name) or the workspace UUID enclosed in curly braces.")
class PostWorkspacesPipelinesConfigRunnersRequest(StrictModel):
    """Creates a new runner for the specified workspace, enabling custom build infrastructure to execute Bitbucket Pipelines jobs."""
    path: PostWorkspacesPipelinesConfigRunnersRequestPath

# Operation: get_workspace_runner
class GetWorkspacesByWorkspacePipelinesConfigRunnersByRunnerUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
    runner_uuid: str = Field(default=..., description="The unique UUID identifying the runner to retrieve within the specified workspace.")
class GetWorkspacesByWorkspacePipelinesConfigRunnersByRunnerUuidRequest(StrictModel):
    """Retrieves details for a specific Pipelines runner configured in a workspace. Useful for inspecting runner status, configuration, and metadata by its unique identifier."""
    path: GetWorkspacesByWorkspacePipelinesConfigRunnersByRunnerUuidRequestPath

# Operation: update_workspace_runner
class PutWorkspacesPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
    runner_uuid: str = Field(default=..., description="The unique identifier (UUID) of the runner to update within the specified workspace.")
class PutWorkspacesPipelinesConfigRunnersRequest(StrictModel):
    """Updates the configuration or metadata of a specific runner within a workspace. Use this to modify runner settings such as labels, status, or other properties."""
    path: PutWorkspacesPipelinesConfigRunnersRequestPath

# Operation: delete_workspace_runner
class DeleteWorkspacesPipelinesConfigRunnersRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either the workspace slug (short name) or the workspace UUID enclosed in curly braces.")
    runner_uuid: str = Field(default=..., description="The unique identifier (UUID) of the runner to delete.")
class DeleteWorkspacesPipelinesConfigRunnersRequest(StrictModel):
    """Permanently deletes a specific Pipelines runner from a workspace using its UUID. This removes the runner's registration and it will no longer be available to execute pipeline steps."""
    path: DeleteWorkspacesPipelinesConfigRunnersRequestPath

# Operation: list_workspace_pipeline_variables
class GetWorkspacesByWorkspacePipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier for the workspace, accepted as either a slug (human-readable short name) or a UUID wrapped in curly braces.")
class GetWorkspacesByWorkspacePipelinesConfigVariablesRequest(StrictModel):
    """Retrieves all pipeline configuration variables defined at the workspace level. These variables are available across all pipelines within the specified workspace."""
    path: GetWorkspacesByWorkspacePipelinesConfigVariablesRequestPath

# Operation: create_pipeline_variable
class PostWorkspacesPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID enclosed in curly braces.")
class PostWorkspacesPipelinesConfigVariablesRequest(StrictModel):
    """Creates a new variable at the workspace level for use across Bitbucket Pipelines. Workspace-level variables are available to all pipelines within the specified workspace."""
    path: PostWorkspacesPipelinesConfigVariablesRequestPath

# Operation: get_workspace_pipeline_variable
class GetWorkspacesByWorkspacePipelinesConfigVariablesByVariableUuidRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
    variable_uuid: str = Field(default=..., description="The unique identifier (UUID) of the workspace pipeline configuration variable to retrieve.")
class GetWorkspacesByWorkspacePipelinesConfigVariablesByVariableUuidRequest(StrictModel):
    """Retrieves a specific pipeline configuration variable at the workspace level by its UUID. Use this to inspect the details of a single workspace-scoped pipeline variable."""
    path: GetWorkspacesByWorkspacePipelinesConfigVariablesByVariableUuidRequestPath

# Operation: update_workspace_pipeline_variable
class PutWorkspacesPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier for the workspace, accepted as either a slug (human-readable short name) or a UUID surrounded by curly-braces.")
    variable_uuid: str = Field(default=..., description="The UUID of the pipeline configuration variable to update, uniquely identifying the variable within the workspace.")
class PutWorkspacesPipelinesConfigVariablesRequest(StrictModel):
    """Updates an existing pipeline configuration variable at the workspace level. Changes apply to all pipelines within the specified workspace that reference this variable."""
    path: PutWorkspacesPipelinesConfigVariablesRequestPath

# Operation: delete_workspace_pipeline_variable
class DeleteWorkspacesPipelinesConfigVariablesRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The unique identifier for the workspace, accepted as either a slug (human-readable short name) or a UUID surrounded by curly-braces.")
    variable_uuid: str = Field(default=..., description="The UUID of the workspace pipeline variable to delete. This uniquely identifies the specific variable to be permanently removed.")
class DeleteWorkspacesPipelinesConfigVariablesRequest(StrictModel):
    """Permanently deletes a specific pipeline configuration variable at the workspace level. This action cannot be undone and will remove the variable from all pipelines that reference it within the workspace."""
    path: DeleteWorkspacesPipelinesConfigVariablesRequestPath

# Operation: list_workspace_projects
class GetWorkspacesByWorkspaceProjectsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")
class GetWorkspacesByWorkspaceProjectsRequest(StrictModel):
    """Retrieves all projects belonging to a specified workspace. Returns a list of project resources associated with the given workspace identifier."""
    path: GetWorkspacesByWorkspaceProjectsRequestPath

# Operation: create_project
class PostWorkspacesProjectsRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace in which to create the project, specified as either the workspace slug (human-readable ID) or the workspace UUID surrounded by curly braces.")
class PostWorkspacesProjectsRequest(StrictModel):
    """Creates a new project within the specified workspace, supporting optional avatar images via data-URL or external URL, privacy settings, and a unique project key."""
    path: PostWorkspacesProjectsRequestPath

# Operation: get_project
class GetWorkspacesByWorkspaceProjectsByProjectKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key assigned to the project, used to identify it within the workspace.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable ID) or a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyRequest(StrictModel):
    """Retrieves details for a specific project within a workspace. Returns project metadata including its key, name, and associated settings."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyRequestPath

# Operation: update_project
class PutWorkspacesProjectsRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key identifying the project within the workspace. This is the short alphanumeric identifier assigned to the project, not its name or UUID.")
    workspace: str = Field(default=..., description="The workspace in which the project resides, specified as either the workspace slug or the workspace UUID enclosed in curly braces.")
class PutWorkspacesProjectsRequest(StrictModel):
    """Creates or updates a project within a workspace using the specified project key. If the key is changed in the request body, the project is relocated and the new URL is returned in the Location response header."""
    path: PutWorkspacesProjectsRequestPath

# Operation: delete_project
class DeleteWorkspacesProjectsRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key assigned to the project, identifying which project to delete.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable ID) or a UUID surrounded by curly-braces.")
class DeleteWorkspacesProjectsRequest(StrictModel):
    """Permanently deletes a project from the specified workspace. The project must have no repositories; delete or transfer all repositories before attempting deletion."""
    path: DeleteWorkspacesProjectsRequestPath

# Operation: get_project_branching_model
class GetWorkspacesProjectsBranchingModelRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key assigned to the project within the workspace.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable ID) or as a UUID surrounded by curly-braces.")
class GetWorkspacesProjectsBranchingModelRequest(StrictModel):
    """Retrieves the read-only branching model configured at the project level, including development and production branch settings and all enabled branch types. To modify these settings, use the branching model settings endpoint."""
    path: GetWorkspacesProjectsBranchingModelRequestPath

# Operation: get_project_branching_model_settings
class GetWorkspacesProjectsBranchingModelSettingsRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key assigned to the project within the workspace, used to identify which project's branching model settings to retrieve.")
    workspace: str = Field(default=..., description="The workspace identifier, accepted as either the workspace slug or the workspace UUID enclosed in curly braces.")
class GetWorkspacesProjectsBranchingModelSettingsRequest(StrictModel):
    """Retrieves the raw branching model configuration for a project, including development and production branch settings, branch types, and default branch deletion behavior. Use the active branching model endpoint instead if you need to see the configuration resolved against actual current branches."""
    path: GetWorkspacesProjectsBranchingModelSettingsRequestPath

# Operation: list_project_default_reviewers
class GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key assigned to the project, used to identify the project within the workspace.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersRequest(StrictModel):
    """Retrieves all default reviewers configured for a project within a workspace. These users are automatically added as reviewers to pull requests in any repository belonging to the project."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersRequestPath

# Operation: get_project_default_reviewer
class GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersBySelectedUserRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique identifier of the project, either its short key or its UUID surrounded by curly-braces.")
    selected_user: str = Field(default=..., description="The unique identifier of the default reviewer to retrieve, either their username or their account UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The unique identifier of the workspace containing the project, either its slug or its UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersBySelectedUserRequest(StrictModel):
    """Retrieves a specific default reviewer for a project within a workspace. Returns reviewer details for the specified user if they are configured as a default reviewer on the project."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersBySelectedUserRequestPath

# Operation: add_project_default_reviewer
class PutWorkspacesProjectsDefaultReviewersRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique identifier for the project, either its short key or its UUID surrounded by curly-braces.")
    selected_user: str = Field(default=..., description="The unique identifier for the user to add as a default reviewer, either their username or their account UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The unique identifier for the workspace, either its slug (ID) or its UUID surrounded by curly-braces.")
class PutWorkspacesProjectsDefaultReviewersRequest(StrictModel):
    """Adds a specified user to the default reviewers list for a project in a workspace. This operation is idempotent, so adding an already-listed reviewer will not cause errors."""
    path: PutWorkspacesProjectsDefaultReviewersRequestPath

# Operation: remove_project_default_reviewer
class DeleteWorkspacesProjectsDefaultReviewersRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique identifier of the project, either its short key or its UUID surrounded by curly-braces.")
    selected_user: str = Field(default=..., description="The unique identifier of the user to remove as a default reviewer, either their username or their account UUID surrounded by curly-braces.")
    workspace: str = Field(default=..., description="The unique identifier of the workspace containing the project, either its slug or its UUID surrounded by curly-braces.")
class DeleteWorkspacesProjectsDefaultReviewersRequest(StrictModel):
    """Removes a specific user from a project's default reviewers list. Once removed, the user will no longer be automatically added as a reviewer on new pull requests in that project."""
    path: DeleteWorkspacesProjectsDefaultReviewersRequestPath

# Operation: list_project_deploy_keys
class GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key identifier assigned to the project, used to target the specific project whose deploy keys will be listed.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysRequest(StrictModel):
    """Retrieves all deploy keys associated with a specific project in a workspace. Deploy keys grant read or read/write access to a repository for CI/CD and automation purposes."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysRequestPath

# Operation: create_project_deploy_key
class PostWorkspacesProjectsDeployKeysRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key identifier assigned to the project (e.g., 'TEST_PROJECT'). This is the short key label, not the project name or UUID.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (human-readable ID) or as a UUID surrounded by curly-braces.")
class PostWorkspacesProjectsDeployKeysRequest(StrictModel):
    """Creates a new deploy key for a specified project within a workspace, enabling secure read or read/write access to the project's repositories."""
    path: PostWorkspacesProjectsDeployKeysRequestPath

# Operation: get_project_deploy_key
class GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysByKeyIdRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique numeric identifier of the deploy key to retrieve.")
    project_key: str = Field(default=..., description="The unique key assigned to the project, used to identify it within the workspace.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysByKeyIdRequest(StrictModel):
    """Retrieves a specific deploy key associated with a project, identified by its key ID. Returns the full deploy key details for the given workspace and project."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysByKeyIdRequestPath

# Operation: delete_project_deploy_key
class DeleteWorkspacesProjectsDeployKeysRequestPath(StrictModel):
    key_id: str = Field(default=..., description="The unique numeric identifier of the deploy key to be deleted from the project.")
    project_key: str = Field(default=..., description="The unique key identifier assigned to the project, used to reference the project within the workspace.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class DeleteWorkspacesProjectsDeployKeysRequest(StrictModel):
    """Permanently removes a specific deploy key from a project in the given workspace. This revokes any access granted to systems using that key."""
    path: DeleteWorkspacesProjectsDeployKeysRequestPath

# Operation: list_project_group_permissions
class GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigGroupsRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key identifying the project within the workspace, as assigned when the project was created.")
    workspace: str = Field(default=..., description="The workspace identifier, accepted as either the workspace slug or the workspace UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigGroupsRequest(StrictModel):
    """Retrieves a paginated list of explicit group-level permissions configured for a specific project within a workspace. Only explicitly assigned group permissions are returned; inherited or implicit permissions are not included."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigGroupsRequestPath

# Operation: list_project_user_permissions
class GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigUsersRequestPath(StrictModel):
    project_key: str = Field(default=..., description="The unique key identifying the project within the workspace, as assigned when the project was created.")
    workspace: str = Field(default=..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces.")
class GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigUsersRequest(StrictModel):
    """Retrieves a paginated list of explicit user-level permissions configured for a specific project within a workspace. Only directly assigned user permissions are returned; inherited or group-based permissions are not included."""
    path: GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigUsersRequestPath

# Operation: list_user_pull_requests_in_workspace
class GetWorkspacesPullrequestsRequestPath(StrictModel):
    selected_user: str = Field(default=..., description="The identifier of the pull request author — accepts a username, an Atlassian ID, or a UUID wrapped in curly braces.")
    workspace: str = Field(default=..., description="The identifier of the workspace — accepts a workspace slug or a UUID wrapped in curly braces.")
class GetWorkspacesPullrequestsRequestQuery(StrictModel):
    state: Literal["OPEN", "MERGED", "DECLINED", "SUPERSEDED"] | None = Field(default=None, description="Filters results to pull requests in the specified state. Repeat this parameter to include multiple states simultaneously; omitting it returns only open pull requests.")
class GetWorkspacesPullrequestsRequest(StrictModel):
    """Retrieves all pull requests authored by a specified user within a given workspace. Supports filtering by one or more states and allows sorting and filtering of results."""
    path: GetWorkspacesPullrequestsRequestPath
    query: GetWorkspacesPullrequestsRequestQuery | None = None

# Operation: search_workspace_code
class GetWorkspacesSearchCodeRequestPath(StrictModel):
    workspace: str = Field(default=..., description="The workspace to search within, specified as either the workspace slug or its UUID wrapped in curly braces.")
class GetWorkspacesSearchCodeRequestQuery(StrictModel):
    search_query: str = Field(default=..., description="The search query string used to match code content or file paths, supporting the same syntax as the Bitbucket UI including repository-scoped filters.")
    page: int | None = Field(default=None, description="The page number of search results to retrieve, starting at 1 for the first page.", json_schema_extra={'format': 'int32'})
    pagelen: int | None = Field(default=None, description="The number of search results to return per page; controls pagination granularity.", json_schema_extra={'format': 'int32'})
class GetWorkspacesSearchCodeRequest(StrictModel):
    """Search across all repositories in a workspace by code content, file path, or both. Supports scoped queries (e.g., limiting to a specific repository) and field expansion for richer response data."""
    path: GetWorkspacesSearchCodeRequestPath
    query: GetWorkspacesSearchCodeRequestQuery

# ============================================================================
# Component Models
# ============================================================================

class BaseCommitSummary(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class BaseCommitV1Summary(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class BranchLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class BranchLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class BranchLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class BranchLinks(StrictModel):
    self: BranchLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    commits: BranchLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    html: BranchLinksHtml | None = Field(None, description="A link to a resource related to this object.")

class BranchrestrictionLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class BranchrestrictionLinks(StrictModel):
    self: BranchrestrictionLinksSelf | None = Field(None, description="A link to a resource related to this object.")

class BranchrestrictionV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class BranchrestrictionV1Links(StrictModel):
    self: BranchrestrictionV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")

class CommentContent(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class CommentInline(StrictModel):
    from_: int | None = Field(None, validation_alias="from", serialization_alias="from", description="The comment's anchor line in the old version of the file. If the comment is a multi-line comment, this is the ending line number in the old version of the file.", ge=1)
    to: int | None = Field(None, description="The comment's anchor line in the new version of the file. If the comment is a multi-line comment, this is the ending line number in the new version of the file.", ge=1)
    start_from: int | None = Field(None, description="The starting line number in the old version of the file, if the comment is a multi-line comment. This is null otherwise.", ge=1)
    start_to: int | None = Field(None, description="The starting line number in the new version of the file, if the comment is a multi-line comment. This is null otherwise.", ge=1)
    path: str = Field(..., description="The path of the file this comment is anchored to.")

class CommentLinksCode(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommentLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommentLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommentLinks(StrictModel):
    self: CommentLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: CommentLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    code: CommentLinksCode | None = Field(None, description="A link to a resource related to this object.")

class CommentV1Content(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class CommentV1Inline(StrictModel):
    from_: int | None = Field(None, validation_alias="from", serialization_alias="from", description="The comment's anchor line in the old version of the file. If the comment is a multi-line comment, this is the ending line number in the old version of the file.", ge=1)
    to: int | None = Field(None, description="The comment's anchor line in the new version of the file. If the comment is a multi-line comment, this is the ending line number in the new version of the file.", ge=1)
    start_from: int | None = Field(None, description="The starting line number in the old version of the file, if the comment is a multi-line comment. This is null otherwise.", ge=1)
    start_to: int | None = Field(None, description="The starting line number in the new version of the file, if the comment is a multi-line comment. This is null otherwise.", ge=1)
    path: str = Field(..., description="The path of the file this comment is anchored to.")

class CommentV1LinksCode(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommentV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommentV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommentV1Links(StrictModel):
    self: CommentV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: CommentV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")
    code: CommentV1LinksCode | None = Field(None, description="A link to a resource related to this object.")

class CommitstatusLinksCommit(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommitstatusLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommitstatusLinks(StrictModel):
    self: CommitstatusLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    commit: CommitstatusLinksCommit | None = Field(None, description="A link to a resource related to this object.")

class CommitstatusV1LinksCommit(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommitstatusV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class CommitstatusV1Links(StrictModel):
    self: CommitstatusV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")
    commit: CommitstatusV1LinksCommit | None = Field(None, description="A link to a resource related to this object.")

class GpgAccountKeyLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class GpgAccountKeyLinks(StrictModel):
    self: GpgAccountKeyLinksSelf | None = Field(None, description="A link to a resource related to this object.")

class GpgAccountKeyV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class GpgAccountKeyV1Links(StrictModel):
    self: GpgAccountKeyV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")

class GroupLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class GroupLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class GroupLinks(StrictModel):
    self: GroupLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: GroupLinksHtml | None = Field(None, description="A link to a resource related to this object.")

class GroupV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class GroupV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class GroupV1Links(StrictModel):
    self: GroupV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: GroupV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")

class Link(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class AccountLinks(PermissiveModel):
    """Links related to an Account."""
    avatar: Link | None = None

class ObjectModel(PermissiveModel):
    """Base type for most resource objects. It defines the common `type` element that identifies an object's type. It also identifies the element as Swagger's `discriminator`."""
    type_: str = Field(..., validation_alias="type", serialization_alias="type")

class Account(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: AccountLinks | None = None
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class Author(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    raw: str | None = Field(None, description="The raw author value from the repository. This may be the only value available if the author does not match a user in Bitbucket.")
    user: Account | None = None

class CommentResolution(PermissiveModel):
    """The resolution object for a Comment."""
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    user: Account | None = None
    created_on: str | None = Field(None, description="The ISO8601 timestamp the resolution was created.", json_schema_extra={'format': 'date-time'})

class Commitstatus(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: CommitstatusLinks | None = None
    key: str = Field(..., description="An identifier for the status that's unique to\n        its type (current \"build\" is the only supported type) and the vendor,\n        e.g. BB-DEPLOY")
    refname: str | None = Field(None, description="\nThe name of the ref that pointed to this commit at the time the status\nobject was created. Note that this the ref may since have moved off of\nthe commit. This optional field can be useful for build systems whose\nbuild triggers and configuration are branch-dependent (e.g. a Pipeline\nbuild).\nIt is legitimate for this field to not be set, or even apply (e.g. a\nstatic linting job).")
    url: str | None = Field(None, description="A URL linking back to the vendor or build system, for providing more information about whatever process produced this status. Accepts context variables `repository` and `commit` that Bitbucket will evaluate at runtime whenever at runtime. For example, one could use https://foo.com/builds/{repository.full_name} which Bitbucket will turn into https://foo.com/builds/foo/bar at render time.")
    state: Literal["FAILED", "INPROGRESS", "STOPPED", "SUCCESSFUL"] = Field(..., description="Provides some indication of the status of this commit")
    name: str | None = Field(None, description="An identifier for the build itself, e.g. BB-DEPLOY-1")
    description: str | None = Field(None, description="A description of the build (e.g. \"Unit tests in Bamboo\")")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class Committer(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    raw: str | None = Field(None, description="The raw committer value from the repository. This may be the only value available if the committer does not match a user in Bitbucket.")
    user: Account | None = None

class Participant(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    user: Account | None = None
    role: Literal["PARTICIPANT", "REVIEWER"] | None = None
    approved: bool | None = None
    state: Literal["approved", "changes_requested"] | None = None
    participated_on: str | None = Field(None, description="The ISO8601 timestamp of the participant's action. For approvers, this is the time of their approval. For commenters and pull request reviewers who are not approvers, this is the time they last commented, or null if they have not commented.", json_schema_extra={'format': 'date-time'})

class PipelineConfigurationSource(PermissiveModel):
    """Information about the source of the pipeline configuration"""
    source: str = Field(..., description="Identifier of the configuration source")
    uri: str = Field(..., description="Link to the configuration source view or its immediate content", json_schema_extra={'format': 'uri'})

class PipelineVariable(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the variable.")
    key: str | None = Field(None, description="The unique name of the variable.")
    value: str | None = Field(None, description="The value of the variable. If the variable is secured, this will be empty.")
    secured: bool | None = Field(None, description="If true, this variable will be treated as secured. The value will never be exposed in the logs or the REST API.")

class PostRepositoriesDeploymentsConfigEnvironmentsVariablesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the variable.")
    key: str | None = Field(None, description="The unique name of the variable.")
    value: str | None = Field(None, description="The value of the variable. If the variable is secured, this will be empty.")
    secured: bool | None = Field(None, description="If true, this variable will be treated as secured. The value will never be exposed in the logs or the REST API.")

class PostRepositoriesEnvironmentsBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the environment.")
    name: str | None = Field(None, description="The name of the environment.")

class PostRepositoriesPipelinesBodyCreatorLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyCreatorLinks(PermissiveModel):
    """Links related to an Account."""
    avatar: PostRepositoriesPipelinesBodyCreatorLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyCreator(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyCreatorLinks | None = Field(None, description="Links related to an Account.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class PostRepositoriesPipelinesBodyLinksSelf(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    href: str | None = Field(None, description="A link", json_schema_extra={'format': 'uri'})

class PostRepositoriesPipelinesBodyLinksSteps(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    href: str | None = Field(None, description="A link", json_schema_extra={'format': 'uri'})

class PostRepositoriesPipelinesBodyLinks(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    self: PostRepositoriesPipelinesBodyLinksSelf | None = None
    steps: PostRepositoriesPipelinesBodyLinksSteps | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksCloneItem(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksDownloads(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksForks(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksHooks(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksPullrequests(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinksWatchers(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryLinks(StrictModel):
    self: PostRepositoriesPipelinesBodyRepositoryLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: PostRepositoriesPipelinesBodyRepositoryLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    avatar: PostRepositoriesPipelinesBodyRepositoryLinksAvatar | None = Field(None, description="A link to a resource related to this object.")
    pullrequests: PostRepositoriesPipelinesBodyRepositoryLinksPullrequests | None = Field(None, description="A link to a resource related to this object.")
    commits: PostRepositoriesPipelinesBodyRepositoryLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    forks: PostRepositoriesPipelinesBodyRepositoryLinksForks | None = Field(None, description="A link to a resource related to this object.")
    watchers: PostRepositoriesPipelinesBodyRepositoryLinksWatchers | None = Field(None, description="A link to a resource related to this object.")
    downloads: PostRepositoriesPipelinesBodyRepositoryLinksDownloads | None = Field(None, description="A link to a resource related to this object.")
    clone: list[PostRepositoriesPipelinesBodyRepositoryLinksCloneItem] | None = None
    hooks: PostRepositoriesPipelinesBodyRepositoryLinksHooks | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryMainbranchLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchLinks(StrictModel):
    self: PostRepositoriesPipelinesBodyRepositoryMainbranchLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    commits: PostRepositoriesPipelinesBodyRepositoryMainbranchLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    html: PostRepositoriesPipelinesBodyRepositoryMainbranchLinksHtml | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUserLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUserLinks(PermissiveModel):
    """Links related to an Account."""
    avatar: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUserLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUser(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUserLinks | None = Field(None, description="Links related to an Account.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthor(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    raw: str | None = Field(None, description="The raw author value from the repository. This may be the only value available if the author does not match a user in Bitbucket.")
    user: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUser | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUserLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUserLinks(PermissiveModel):
    """Links related to an Account."""
    avatar: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUserLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUser(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUserLinks | None = Field(None, description="Links related to an Account.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitter(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    raw: str | None = Field(None, description="The raw committer value from the repository. This may be the only value available if the committer does not match a user in Bitbucket.")
    user: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUser | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranchTargetSummary(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PostRepositoriesPipelinesBodyRepositoryOwnerLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryOwnerLinks(PermissiveModel):
    """Links related to an Account."""
    avatar: PostRepositoriesPipelinesBodyRepositoryOwnerLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryOwner(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryOwnerLinks | None = Field(None, description="Links related to an Account.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class PostRepositoriesPipelinesBodyRepositoryProjectLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectLinks(StrictModel):
    html: PostRepositoriesPipelinesBodyRepositoryProjectLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    avatar: PostRepositoriesPipelinesBodyRepositoryProjectLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksMembers(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksProjects(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksRepositories(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinks(PermissiveModel):
    avatar: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksAvatar | None = Field(None, description="A link to a resource related to this object.")
    self: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    members: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksMembers | None = Field(None, description="A link to a resource related to this object.")
    projects: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksProjects | None = Field(None, description="A link to a resource related to this object.")
    repositories: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksRepositories | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPipelinesBodyRepositoryProjectOwner(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinks | None = None
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class PostRepositoriesPipelinesBodyRepositoryProject(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryProjectLinks | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The project's immutable id.")
    key: str | None = Field(None, description="The project's key.")
    owner: PostRepositoriesPipelinesBodyRepositoryProjectOwner | None = None
    name: str | None = Field(None, description="The name of the project.")
    description: str | None = None
    is_private: bool | None = Field(None, description="\nIndicates whether the project is publicly accessible, or whether it is\nprivate to the team and consequently only visible to team members.\nNote that private projects cannot contain public repositories.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    has_publicly_visible_repos: bool | None = Field(None, description="\nIndicates whether the project contains publicly visible repositories.\nNote that private projects cannot contain public repositories.")

class PostRepositoriesPipelinesBodyState(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")

class PostRepositoriesPipelinesBodyTarget(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")

class PostRepositoriesPipelinesBodyTrigger(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")

class PostRepositoriesPipelinesConfigSchedulesBodyTargetSelector(PermissiveModel):
    type_: Literal["branches", "tags", "bookmarks", "default", "custom"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of selector.")
    pattern: str | None = Field(None, description="The name of the matching pipeline definition.")

class PostRepositoriesPipelinesConfigSchedulesBodyTarget(PermissiveModel):
    """The target on which the schedule will be executed."""
    selector: PostRepositoriesPipelinesConfigSchedulesBodyTargetSelector
    ref_name: str = Field(..., description="The name of the reference.")
    ref_type: Literal["branch"] = Field(..., description="The type of reference (branch only).")

class PostRepositoriesPipelinesConfigSchedulesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    target: PostRepositoriesPipelinesConfigSchedulesBodyTarget = Field(..., description="The target on which the schedule will be executed.")
    enabled: bool | None = Field(None, description="Whether the schedule is enabled.")
    cron_pattern: str = Field(..., description="The cron expression with second precision (7 fields) that the schedule applies. For example, for expression: 0 0 12 * * ? *, will execute at 12pm UTC every day.")

class PostRepositoriesPipelinesConfigSshKnownHostsBodyPublicKey(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    key_type: str | None = Field(None, description="The type of the public key.")
    key: str | None = Field(None, description="The base64 encoded public key.")
    md5_fingerprint: str | None = Field(None, description="The MD5 fingerprint of the public key.")
    sha256_fingerprint: str | None = Field(None, description="The SHA-256 fingerprint of the public key.")

class PostRepositoriesPipelinesConfigSshKnownHostsBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the known host.")
    hostname: str | None = Field(None, description="The hostname of the known host.")
    public_key: PostRepositoriesPipelinesConfigSshKnownHostsBodyPublicKey | None = None

class PostRepositoriesPipelinesConfigVariablesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the variable.")
    key: str | None = Field(None, description="The unique name of the variable.")
    value: str | None = Field(None, description="The value of the variable. If the variable is secured, this will be empty.")
    secured: bool | None = Field(None, description="If true, this variable will be treated as secured. The value will never be exposed in the logs or the REST API.")

class PostRepositoriesPullrequestsTasksBodyCommentContent(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PostRepositoriesPullrequestsTasksBodyCommentInline(StrictModel):
    from_: int | None = Field(None, validation_alias="from", serialization_alias="from", description="The comment's anchor line in the old version of the file. If the comment is a multi-line comment, this is the ending line number in the old version of the file.", ge=1)
    to: int | None = Field(None, description="The comment's anchor line in the new version of the file. If the comment is a multi-line comment, this is the ending line number in the new version of the file.", ge=1)
    start_from: int | None = Field(None, description="The starting line number in the old version of the file, if the comment is a multi-line comment. This is null otherwise.", ge=1)
    start_to: int | None = Field(None, description="The starting line number in the new version of the file, if the comment is a multi-line comment. This is null otherwise.", ge=1)
    path: str = Field(..., description="The path of the file this comment is anchored to.")

class PostRepositoriesPullrequestsTasksBodyCommentLinksCode(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPullrequestsTasksBodyCommentLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPullrequestsTasksBodyCommentLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPullrequestsTasksBodyCommentLinks(StrictModel):
    self: PostRepositoriesPullrequestsTasksBodyCommentLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: PostRepositoriesPullrequestsTasksBodyCommentLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    code: PostRepositoriesPullrequestsTasksBodyCommentLinksCode | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPullrequestsTasksBodyCommentUserLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PostRepositoriesPullrequestsTasksBodyCommentUserLinks(PermissiveModel):
    """Links related to an Account."""
    avatar: PostRepositoriesPullrequestsTasksBodyCommentUserLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PostRepositoriesPullrequestsTasksBodyCommentUser(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPullrequestsTasksBodyCommentUserLinks | None = Field(None, description="Links related to an Account.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    display_name: str | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid")

class ProjectLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class ProjectLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class ProjectLinks(StrictModel):
    html: ProjectLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    avatar: ProjectLinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class ProjectV1LinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class ProjectV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class ProjectV1Links(StrictModel):
    html: ProjectV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")
    avatar: ProjectV1LinksAvatar | None = Field(None, description="A link to a resource related to this object.")

class PullrequestEndpointBranch(StrictModel):
    name: str | None = None
    merge_strategies: list[Literal["merge_commit", "squash", "fast_forward", "squash_fast_forward", "rebase_fast_forward", "rebase_merge"]] | None = Field(None, description="Available merge strategies, when this endpoint is the destination of the pull request.")
    default_merge_strategy: str | None = Field(None, description="The default merge strategy, when this endpoint is the destination of the pull request.")

class PullrequestEndpointCommit(StrictModel):
    hash_: str | None = Field(None, validation_alias="hash", serialization_alias="hash", pattern="[0-9a-f]{7,}?")

class PullrequestLinksActivity(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksApprove(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksComments(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksDecline(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksDiff(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksDiffstat(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksMerge(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestLinks(StrictModel):
    self: PullrequestLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: PullrequestLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    commits: PullrequestLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    approve: PullrequestLinksApprove | None = Field(None, description="A link to a resource related to this object.")
    diff: PullrequestLinksDiff | None = Field(None, description="A link to a resource related to this object.")
    diffstat: PullrequestLinksDiffstat | None = Field(None, description="A link to a resource related to this object.")
    comments: PullrequestLinksComments | None = Field(None, description="A link to a resource related to this object.")
    activity: PullrequestLinksActivity | None = Field(None, description="A link to a resource related to this object.")
    merge: PullrequestLinksMerge | None = Field(None, description="A link to a resource related to this object.")
    decline: PullrequestLinksDecline | None = Field(None, description="A link to a resource related to this object.")

class PullrequestMergeCommit(StrictModel):
    hash_: str | None = Field(None, validation_alias="hash", serialization_alias="hash", pattern="[0-9a-f]{7,}?")

class PullrequestRenderedDescription(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestRenderedReason(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestRenderedTitle(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestRendered(StrictModel):
    """User provided pull request text, interpreted in a markup language and rendered in HTML"""
    title: PullrequestRenderedTitle | None = None
    description: PullrequestRenderedDescription | None = None
    reason: PullrequestRenderedReason | None = None

class PullrequestSummary(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestV1LinksActivity(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksApprove(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksComments(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksDecline(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksDiff(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksDiffstat(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksMerge(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class PullrequestV1Links(StrictModel):
    self: PullrequestV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: PullrequestV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")
    commits: PullrequestV1LinksCommits | None = Field(None, description="A link to a resource related to this object.")
    approve: PullrequestV1LinksApprove | None = Field(None, description="A link to a resource related to this object.")
    diff: PullrequestV1LinksDiff | None = Field(None, description="A link to a resource related to this object.")
    diffstat: PullrequestV1LinksDiffstat | None = Field(None, description="A link to a resource related to this object.")
    comments: PullrequestV1LinksComments | None = Field(None, description="A link to a resource related to this object.")
    activity: PullrequestV1LinksActivity | None = Field(None, description="A link to a resource related to this object.")
    merge: PullrequestV1LinksMerge | None = Field(None, description="A link to a resource related to this object.")
    decline: PullrequestV1LinksDecline | None = Field(None, description="A link to a resource related to this object.")

class PullrequestV1MergeCommit(StrictModel):
    hash_: str | None = Field(None, validation_alias="hash", serialization_alias="hash", pattern="[0-9a-f]{7,}?")

class PullrequestV1RenderedDescription(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestV1RenderedReason(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestV1RenderedTitle(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PullrequestV1Rendered(StrictModel):
    """User provided pull request text, interpreted in a markup language and rendered in HTML"""
    title: PullrequestV1RenderedTitle | None = None
    description: PullrequestV1RenderedDescription | None = None
    reason: PullrequestV1RenderedReason | None = None

class PullrequestV1Summary(StrictModel):
    raw: str | None = Field(None, description="The text as it was typed by a user.")
    markup: Literal["markdown", "creole", "plaintext"] | None = Field(None, description="The type of markup language the raw content is to be interpreted in.")
    html: str | None = Field(None, description="The user's content rendered as HTML.")

class PutRepositoriesCommitReportsAnnotationsBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    external_id: str | None = Field(None, description="ID of the annotation provided by the annotation creator. It can be used to identify the annotation as an alternative to it's generated uuid. It is not used by Bitbucket, but only by the annotation creator for updating or deleting this specific annotation. Needs to be unique.")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID that can be used to identify the annotation.")
    annotation_type: Literal["VULNERABILITY", "CODE_SMELL", "BUG"] | None = Field(None, description="The type of the report.")
    path: str | None = Field(None, description="The path of the file on which this annotation should be placed. This is the path of the file relative to the git repository. If no path is provided, then it will appear in the overview modal on all pull requests where the tip of the branch is the given commit, regardless of which files were modified.")
    line: int | None = Field(None, description="The line number that the annotation should belong to. If no line number is provided, then it will default to 0 and in a pull request it will appear at the top of the file specified by the path field.", ge=1)
    summary: str | None = Field(None, description="The message to display to users.")
    details: str | None = Field(None, description="The details to show to users when clicking on the annotation.")
    result: Literal["PASSED", "FAILED", "SKIPPED", "IGNORED"] | None = Field(None, description="The state of the report. May be set to PENDING and later updated.")
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] | None = Field(None, description="The severity of the annotation.")
    link: str | None = Field(None, description="A URL linking to the annotation in an external tool.", json_schema_extra={'format': 'uri'})
    created_on: str | None = Field(None, description="The timestamp when the report was created.", json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, description="The timestamp when the report was updated.", json_schema_extra={'format': 'date-time'})

class PutRepositoriesDeploymentsConfigEnvironmentsVariablesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the variable.")
    key: str | None = Field(None, description="The unique name of the variable.")
    value: str | None = Field(None, description="The value of the variable. If the variable is secured, this will be empty.")
    secured: bool | None = Field(None, description="If true, this variable will be treated as secured. The value will never be exposed in the logs or the REST API.")

class PutRepositoriesPipelinesConfigBuildNumberBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    next_: int | None = Field(None, validation_alias="next", serialization_alias="next", description="The next number that will be used as build number.")

class PutRepositoriesPipelinesConfigSchedulesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    enabled: bool | None = Field(None, description="Whether the schedule is enabled.")

class PutRepositoriesPipelinesConfigSshKeyPairBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    private_key: str | None = Field(None, description="The SSH private key. This value will be empty when retrieving the SSH key pair.")
    public_key: str | None = Field(None, description="The SSH public key.")

class PutRepositoriesPipelinesConfigSshKnownHostsBodyPublicKey(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    key_type: str | None = Field(None, description="The type of the public key.")
    key: str | None = Field(None, description="The base64 encoded public key.")
    md5_fingerprint: str | None = Field(None, description="The MD5 fingerprint of the public key.")
    sha256_fingerprint: str | None = Field(None, description="The SHA-256 fingerprint of the public key.")

class PutRepositoriesPipelinesConfigSshKnownHostsBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the known host.")
    hostname: str | None = Field(None, description="The hostname of the known host.")
    public_key: PutRepositoriesPipelinesConfigSshKnownHostsBodyPublicKey | None = None

class PutRepositoriesPipelinesConfigVariablesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the variable.")
    key: str | None = Field(None, description="The unique name of the variable.")
    value: str | None = Field(None, description="The value of the variable. If the variable is secured, this will be empty.")
    secured: bool | None = Field(None, description="If true, this variable will be treated as secured. The value will never be exposed in the logs or the REST API.")

class RefLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RefLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RefLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RefLinks(StrictModel):
    self: RefLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    commits: RefLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    html: RefLinksHtml | None = Field(None, description="A link to a resource related to this object.")

class ReportAnnotation(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    external_id: str | None = Field(None, description="ID of the annotation provided by the annotation creator. It can be used to identify the annotation as an alternative to it's generated uuid. It is not used by Bitbucket, but only by the annotation creator for updating or deleting this specific annotation. Needs to be unique.")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID that can be used to identify the annotation.")
    annotation_type: Literal["VULNERABILITY", "CODE_SMELL", "BUG"] | None = Field(None, description="The type of the report.")
    path: str | None = Field(None, description="The path of the file on which this annotation should be placed. This is the path of the file relative to the git repository. If no path is provided, then it will appear in the overview modal on all pull requests where the tip of the branch is the given commit, regardless of which files were modified.")
    line: int | None = Field(None, description="The line number that the annotation should belong to. If no line number is provided, then it will default to 0 and in a pull request it will appear at the top of the file specified by the path field.", ge=1)
    summary: str | None = Field(None, description="The message to display to users.")
    details: str | None = Field(None, description="The details to show to users when clicking on the annotation.")
    result: Literal["PASSED", "FAILED", "SKIPPED", "IGNORED"] | None = Field(None, description="The state of the report. May be set to PENDING and later updated.")
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] | None = Field(None, description="The severity of the annotation.")
    link: str | None = Field(None, description="A URL linking to the annotation in an external tool.", json_schema_extra={'format': 'uri'})
    created_on: str | None = Field(None, description="The timestamp when the report was created.", json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, description="The timestamp when the report was updated.", json_schema_extra={'format': 'date-time'})

class ReportData(PermissiveModel):
    """A key-value element that will be displayed along with the report."""
    type_: Literal["BOOLEAN", "DATE", "DURATION", "LINK", "NUMBER", "PERCENTAGE", "TEXT"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of data contained in the value field. If not provided, then the value will be detected as a boolean, number or string.")
    title: str | None = Field(None, description="A string describing what this data field represents.")
    value: dict[str, Any] | None = Field(None, description="The value of the data element.")

class PutRepositoriesCommitReportsBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID that can be used to identify the report.")
    title: str | None = Field(None, description="The title of the report.")
    details: str | None = Field(None, description="A string to describe the purpose of the report.")
    external_id: str | None = Field(None, description="ID of the report provided by the report creator. It can be used to identify the report as an alternative to it's generated uuid. It is not used by Bitbucket, but only by the report creator for updating or deleting this specific report. Needs to be unique.")
    reporter: str | None = Field(None, description="A string to describe the tool or company who created the report.")
    link: str | None = Field(None, description="A URL linking to the results of the report in an external tool.", json_schema_extra={'format': 'uri'})
    remote_link_enabled: bool | None = Field(None, description="If enabled, a remote link is created in Jira for the work item associated with the commit the report belongs to.")
    logo_url: str | None = Field(None, description="A URL to the report logo. If none is provided, the default insights logo will be used.", json_schema_extra={'format': 'uri'})
    report_type: Literal["SECURITY", "COVERAGE", "TEST", "BUG"] | None = Field(None, description="The type of the report.")
    result: Literal["PASSED", "FAILED", "PENDING"] | None = Field(None, description="The state of the report. May be set to PENDING and later updated.")
    data: list[ReportData] | None = Field(None, description="An array of data fields to display information on the report. Maximum 10.")
    created_on: str | None = Field(None, description="The timestamp when the report was created.", json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, description="The timestamp when the report was updated.", json_schema_extra={'format': 'date-time'})

class RepositoryLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksCloneItem(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksDownloads(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksForks(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksHooks(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksPullrequests(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinksWatchers(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryLinks(StrictModel):
    self: RepositoryLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: RepositoryLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    avatar: RepositoryLinksAvatar | None = Field(None, description="A link to a resource related to this object.")
    pullrequests: RepositoryLinksPullrequests | None = Field(None, description="A link to a resource related to this object.")
    commits: RepositoryLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    forks: RepositoryLinksForks | None = Field(None, description="A link to a resource related to this object.")
    watchers: RepositoryLinksWatchers | None = Field(None, description="A link to a resource related to this object.")
    downloads: RepositoryLinksDownloads | None = Field(None, description="A link to a resource related to this object.")
    clone: list[RepositoryLinksCloneItem] | None = None
    hooks: RepositoryLinksHooks | None = Field(None, description="A link to a resource related to this object.")

class RepositoryV1LinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksCloneItem(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksDownloads(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksForks(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksHooks(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksPullrequests(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1LinksWatchers(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class RepositoryV1Links(StrictModel):
    self: RepositoryV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: RepositoryV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")
    avatar: RepositoryV1LinksAvatar | None = Field(None, description="A link to a resource related to this object.")
    pullrequests: RepositoryV1LinksPullrequests | None = Field(None, description="A link to a resource related to this object.")
    commits: RepositoryV1LinksCommits | None = Field(None, description="A link to a resource related to this object.")
    forks: RepositoryV1LinksForks | None = Field(None, description="A link to a resource related to this object.")
    watchers: RepositoryV1LinksWatchers | None = Field(None, description="A link to a resource related to this object.")
    downloads: RepositoryV1LinksDownloads | None = Field(None, description="A link to a resource related to this object.")
    clone: list[RepositoryV1LinksCloneItem] | None = None
    hooks: RepositoryV1LinksHooks | None = Field(None, description="A link to a resource related to this object.")

class Snippet(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", ge=0)
    title: str | None = None
    scm: Literal["git"] | None = Field(None, description="The DVCS used to store the snippet.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    owner: Account | None = None
    creator: Account | None = None
    is_private: bool | None = None

class SnippetCommentLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class SnippetCommentLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class SnippetCommentLinks(StrictModel):
    self: SnippetCommentLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: SnippetCommentLinksHtml | None = Field(None, description="A link to a resource related to this object.")

class SnippetComment(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: SnippetCommentLinks | None = None
    snippet: Snippet | None = None

class SnippetCommentV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class SnippetCommentV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class SnippetCommentV1Links(StrictModel):
    self: SnippetCommentV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")
    html: SnippetCommentV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")

class SshKeyLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class SshKeyLinks(StrictModel):
    self: SshKeyLinksSelf | None = Field(None, description="A link to a resource related to this object.")

class SshKey(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The SSH key's immutable ID.")
    key: str | None = Field(None, description="The SSH public key value in OpenSSH format.")
    comment: str | None = Field(None, description="The comment parsed from the SSH key (if present)")
    label: str | None = Field(None, description="The user-defined label for the SSH key")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    last_used: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    links: SshKeyLinks | None = None

class SshAccountKey(PermissiveModel):
    owner: Account | None = None
    expires_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    fingerprint: str | None = Field(None, description="The SSH key fingerprint in SHA-256 format.")

class SshKeyV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class SshKeyV1Links(StrictModel):
    self: SshKeyV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")

class TagLinksCommits(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class TagLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class TagLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class TagLinks(StrictModel):
    self: TagLinksSelf | None = Field(None, description="A link to a resource related to this object.")
    commits: TagLinksCommits | None = Field(None, description="A link to a resource related to this object.")
    html: TagLinksHtml | None = Field(None, description="A link to a resource related to this object.")

class TeamLinks(PermissiveModel):
    avatar: Link | None = None
    self: Link | None = None
    html: Link | None = None
    members: Link | None = None
    projects: Link | None = None
    repositories: Link | None = None

class Team(PermissiveModel):
    links: TeamLinks | None = None

class Project(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: ProjectLinks | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The project's immutable id.")
    key: str | None = Field(None, description="The project's key.")
    owner: Team | None = None
    name: str | None = Field(None, description="The name of the project.")
    description: str | None = None
    is_private: bool | None = Field(None, description="\nIndicates whether the project is publicly accessible, or whether it is\nprivate to the team and consequently only visible to team members.\nNote that private projects cannot contain public repositories.")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    has_publicly_visible_repos: bool | None = Field(None, description="\nIndicates whether the project contains publicly visible repositories.\nNote that private projects cannot contain public repositories.")

class UserLinks(PermissiveModel):
    avatar: Link | None = None
    self: Link | None = None
    html: Link | None = None
    repositories: Link | None = None

class User(PermissiveModel):
    links: UserLinks | None = None
    account_id: str | None = Field(None, description="The user's Atlassian account ID.")
    account_status: str | None = Field(None, description="The status of the account. Currently the only possible value is \"active\", but more values may be added in the future.")
    has_2fa_enabled: bool | None = None
    nickname: str | None = Field(None, description="Account name defined by the owner. Should be used instead of the \"username\" field. Note that \"nickname\" cannot be used in place of \"username\" in URLs and queries, as \"nickname\" is not guaranteed to be unique.")
    is_staff: bool | None = None

class WorkspaceLinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksMembers(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksOwners(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksProjects(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksRepositories(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinksSnippets(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceLinks(StrictModel):
    avatar: WorkspaceLinksAvatar | None = Field(None, description="A link to a resource related to this object.")
    html: WorkspaceLinksHtml | None = Field(None, description="A link to a resource related to this object.")
    members: WorkspaceLinksMembers | None = Field(None, description="A link to a resource related to this object.")
    owners: WorkspaceLinksOwners | None = Field(None, description="A link to a resource related to this object.")
    projects: WorkspaceLinksProjects | None = Field(None, description="A link to a resource related to this object.")
    repositories: WorkspaceLinksRepositories | None = Field(None, description="A link to a resource related to this object.")
    snippets: WorkspaceLinksSnippets | None = Field(None, description="A link to a resource related to this object.")
    self: WorkspaceLinksSelf | None = Field(None, description="A link to a resource related to this object.")

class Workspace(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: WorkspaceLinks | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The workspace's immutable id.")
    name: str | None = Field(None, description="The name of the workspace.")
    slug: str | None = Field(None, description="The short label that identifies this workspace.")
    is_private: bool | None = Field(None, description="Indicates whether the workspace is publicly accessible, or whether it is\nprivate to the members and consequently only visible to members.")
    is_privacy_enforced: bool | None = Field(None, description="Indicates whether the workspace enforces private content, or whether it allows public content.")
    forking_mode: Literal["allow_forks", "internal_only"] | None = Field(None, description="Controls the rules for forking repositories within this workspace.\n\n* **allow_forks**: unrestricted forking\n* **internal_only**: prevents forking of private repositories outside the workspace or to public repositories\n")
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class Group(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: GroupLinks | None = None
    owner: Account | None = None
    workspace: Workspace | None = None
    name: str | None = None
    slug: str | None = Field(None, description="The \"sluggified\" version of the group's name. This contains only ASCII\ncharacters and can therefore be slightly different than the name")
    full_slug: str | None = Field(None, description="The concatenation of the workspace's slug and the group's slug,\nseparated with a colon (e.g. `acme:developers`)\n")

class Branchrestriction(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: BranchrestrictionLinks | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The branch restriction status' id.")
    kind: Literal["push", "delete", "force", "restrict_merges", "require_tasks_to_be_completed", "require_approvals_to_merge", "require_review_group_approvals_to_merge", "require_default_reviewer_approvals_to_merge", "require_no_changes_requested", "require_passing_builds_to_merge", "require_commits_behind", "reset_pullrequest_approvals_on_change", "smart_reset_pullrequest_approvals", "reset_pullrequest_changes_requested_on_change", "require_all_dependencies_merged", "enforce_merge_checks", "allow_auto_merge_when_builds_pass", "require_all_comments_resolved"] = Field(..., description="The type of restriction that is being applied.")
    branch_match_kind: Literal["branching_model", "glob"] = Field(..., description="Indicates how the restriction is matched against a branch. The default is `glob`.")
    branch_type: Literal["feature", "bugfix", "release", "hotfix", "development", "production"] | None = Field(None, description="Apply the restriction to branches of this type. Active when `branch_match_kind` is `branching_model`. The branch type will be calculated using the branching model configured for the repository.")
    pattern: str = Field(..., description="Apply the restriction to branches that match this pattern. Active when `branch_match_kind` is `glob`. Will be empty when `branch_match_kind` is `branching_model`.")
    value: int | None = Field(None, description="Value with kind-specific semantics:\n\n* `require_approvals_to_merge` uses it to require a minimum number of approvals on a PR.\n\n* `require_default_reviewer_approvals_to_merge` uses it to require a minimum number of approvals from default reviewers on a PR.\n\n* `require_passing_builds_to_merge` uses it to require a minimum number of passing builds.\n\n* `require_commits_behind` uses it to require the current branch is up to a maximum number of commits behind it destination.")
    users: list[Account] | None = Field(None, min_length=0)
    groups: list[Group] | None = Field(None, min_length=0)

class WorkspaceV1LinksAvatar(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksHtml(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksMembers(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksOwners(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksProjects(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksRepositories(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksSelf(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1LinksSnippets(StrictModel):
    """A link to a resource related to this object."""
    href: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None

class WorkspaceV1Links(StrictModel):
    avatar: WorkspaceV1LinksAvatar | None = Field(None, description="A link to a resource related to this object.")
    html: WorkspaceV1LinksHtml | None = Field(None, description="A link to a resource related to this object.")
    members: WorkspaceV1LinksMembers | None = Field(None, description="A link to a resource related to this object.")
    owners: WorkspaceV1LinksOwners | None = Field(None, description="A link to a resource related to this object.")
    projects: WorkspaceV1LinksProjects | None = Field(None, description="A link to a resource related to this object.")
    repositories: WorkspaceV1LinksRepositories | None = Field(None, description="A link to a resource related to this object.")
    snippets: WorkspaceV1LinksSnippets | None = Field(None, description="A link to a resource related to this object.")
    self: WorkspaceV1LinksSelf | None = Field(None, description="A link to a resource related to this object.")

class BaseCommit(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    hash_: str | None = Field(None, validation_alias="hash", serialization_alias="hash", pattern="[0-9a-f]{7,}?")
    date: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    author: Author | None = None
    committer: Committer | None = None
    message: str | None = None
    summary: BaseCommitSummary | None = None
    parents: list[BaseCommit] | None = Field(None, min_length=0)

class Branch(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: BranchLinks | None = None
    name: str | None = Field(None, description="The name of the ref.")
    target: Commit | None = None
    merge_strategies: list[Literal["merge_commit", "squash", "fast_forward", "squash_fast_forward", "rebase_fast_forward", "rebase_merge"]] | None = Field(None, description="Available merge strategies for pull requests targeting this branch.")
    default_merge_strategy: str | None = Field(None, description="The default merge strategy for pull requests targeting this branch.")

class Comment(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    content: CommentContent | None = None
    user: Account | None = None
    deleted: bool | None = None
    parent: Comment | None = None
    inline: CommentInline | None = None
    links: CommentLinks | None = None

class Commit(PermissiveModel):
    repository: Repository | None = None
    participants: list[Participant] | None = Field(None, min_length=0)

class CommitComment(PermissiveModel):
    commit: Commit | None = None

class GpgAccountKey(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    owner: Account | None = None
    key: str | None = Field(None, description="The GPG key value in X format.")
    key_id: str | None = Field(None, description="The unique identifier for the GPG key")
    fingerprint: str | None = Field(None, description="The GPG key fingerprint.")
    parent_fingerprint: str | None = Field(None, description="The fingerprint of the parent key. This value is null unless the current key is a subkey.")
    comment: str | None = Field(None, description="The comment parsed from the GPG key (if present)")
    name: str | None = Field(None, description="The user-defined label for the GPG key")
    expires_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    added_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    last_used: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    subkeys: Annotated[list[GpgAccountKey], AfterValidator(_check_unique_items)] | None = Field(None, min_length=0)
    links: GpgAccountKeyLinks | None = None

class PostRepositoriesPipelinesBody(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The UUID identifying the pipeline.")
    build_number: int | None = Field(None, description="The build number of the pipeline.")
    creator: PostRepositoriesPipelinesBodyCreator | None = None
    repository: PostRepositoriesPipelinesBodyRepository | None = None
    target: PostRepositoriesPipelinesBodyTarget | None = None
    trigger: PostRepositoriesPipelinesBodyTrigger | None = None
    state: PostRepositoriesPipelinesBodyState | None = None
    variables: list[PipelineVariable] | None = Field(None, description="The variables for the pipeline.", min_length=0)
    created_on: str | None = Field(None, description="The timestamp when the pipeline was created.", json_schema_extra={'format': 'date-time'})
    completed_on: str | None = Field(None, description="The timestamp when the Pipeline was completed. This is not set if the pipeline is still in progress.", json_schema_extra={'format': 'date-time'})
    build_seconds_used: int | None = Field(None, description="The number of build seconds used by this pipeline.")
    configuration_sources: list[PipelineConfigurationSource] | None = Field(None, description="An ordered list of sources of the pipeline configuration", min_length=0)
    links: PostRepositoriesPipelinesBodyLinks | None = None

class PostRepositoriesPipelinesBodyRepository(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryLinks | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The repository's immutable id. This can be used as a substitute for the slug segment in URLs. Doing this guarantees your URLs will survive renaming of the repository by its owner, or even transfer of the repository to a different user.")
    full_name: str | None = Field(None, description="The concatenation of the repository owner's username and the slugified name, e.g. \"evzijst/interruptingcow\". This is the same string used in Bitbucket URLs.")
    is_private: bool | None = None
    parent: Repository | None = None
    scm: Literal["git"] | None = None
    owner: PostRepositoriesPipelinesBodyRepositoryOwner | None = None
    name: str | None = None
    description: str | None = None
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    size: int | None = None
    language: str | None = None
    has_issues: bool | None = Field(None, description="\nThe issue tracker for this repository is enabled. Issue Tracker\nfeatures are not supported for repositories in workspaces\nadministered through admin.atlassian.com.\n")
    has_wiki: bool | None = Field(None, description="\nThe wiki for this repository is enabled. Wiki\nfeatures are not supported for repositories in workspaces\nadministered through admin.atlassian.com.\n")
    fork_policy: Literal["allow_forks", "no_public_forks", "no_forks"] | None = Field(None, description="\nControls the rules for forking this repository.\n\n* **allow_forks**: unrestricted forking\n* **no_public_forks**: restrict forking to private forks (forks cannot\n  be made public later)\n* **no_forks**: deny all forking\n")
    project: PostRepositoriesPipelinesBodyRepositoryProject | None = None
    mainbranch: PostRepositoriesPipelinesBodyRepositoryMainbranch | None = None

class PostRepositoriesPipelinesBodyRepositoryMainbranch(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PostRepositoriesPipelinesBodyRepositoryMainbranchLinks | None = None
    name: str | None = Field(None, description="The name of the ref.")
    target: PostRepositoriesPipelinesBodyRepositoryMainbranchTarget | None = None
    merge_strategies: list[Literal["merge_commit", "squash", "fast_forward", "squash_fast_forward", "rebase_fast_forward", "rebase_merge"]] | None = Field(None, description="Available merge strategies for pull requests targeting this branch.")
    default_merge_strategy: str | None = Field(None, description="The default merge strategy for pull requests targeting this branch.")

class PostRepositoriesPipelinesBodyRepositoryMainbranchTarget(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    hash_: str | None = Field(None, validation_alias="hash", serialization_alias="hash", pattern="[0-9a-f]{7,}?")
    date: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    author: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthor | None = None
    committer: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitter | None = None
    message: str | None = None
    summary: PostRepositoriesPipelinesBodyRepositoryMainbranchTargetSummary | None = None
    parents: list[BaseCommit] | None = Field(None, min_length=0)
    repository: Repository | None = None
    participants: list[Participant] | None = Field(None, min_length=0)

class PostRepositoriesPullrequestsTasksBodyComment(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    content: PostRepositoriesPullrequestsTasksBodyCommentContent | None = None
    user: PostRepositoriesPullrequestsTasksBodyCommentUser | None = None
    deleted: bool | None = None
    parent: Comment | None = None
    inline: PostRepositoriesPullrequestsTasksBodyCommentInline | None = None
    links: PostRepositoriesPullrequestsTasksBodyCommentLinks | None = None

class Pullrequest(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: PullrequestLinks | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The pull request's unique ID. Note that pull request IDs are only unique within their associated repository.")
    title: str | None = Field(None, description="Title of the pull request.")
    rendered: PullrequestRendered | None = Field(None, description="User provided pull request text, interpreted in a markup language and rendered in HTML")
    summary: PullrequestSummary | None = None
    state: Literal["OPEN", "DRAFT", "QUEUED", "MERGED", "DECLINED", "SUPERSEDED"] | None = Field(None, description="The pull request's current status.")
    author: Account | None = None
    source: PullrequestEndpoint | None = None
    destination: PullrequestEndpoint | None = None
    merge_commit: PullrequestMergeCommit | None = None
    comment_count: int | None = Field(None, description="The number of comments for a specific pull request.", ge=0)
    task_count: int | None = Field(None, description="The number of open tasks for a specific pull request.", ge=0)
    close_source_branch: bool | None = Field(None, description="A boolean flag indicating if merging the pull request closes the source branch.")
    closed_by: Account | None = None
    reason: str | None = Field(None, description="Explains why a pull request was declined. This field is only applicable to pull requests in rejected state.")
    created_on: str | None = Field(None, description="The ISO8601 timestamp the request was created.", json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, description="The ISO8601 timestamp the request was last updated.", json_schema_extra={'format': 'date-time'})
    reviewers: list[Account] | None = Field(None, description="The list of users that were added as reviewers on this pull request when it was created. For performance reasons, the API only includes this list on a pull request's `self` URL.")
    participants: list[Participant] | None = Field(None, description="        The list of users that are collaborating on this pull request.\n        Collaborators are user that:\n\n        * are added to the pull request as a reviewer (part of the reviewers\n          list)\n        * are not explicit reviewers, but have commented on the pull request\n        * are not explicit reviewers, but have approved the pull request\n\n        Each user is wrapped in an object that indicates the user's role and\n        whether they have approved the pull request. For performance reasons,\n        the API only returns this list when an API requests a pull request by\n        id.\n        ")
    draft: bool | None = Field(None, description="A boolean flag indicating whether the pull request is a draft.")
    queued: bool | None = Field(None, description="A boolean flag indicating whether the pull request is queued")

class PullrequestComment(PermissiveModel):
    pullrequest: Pullrequest | None = None
    resolution: CommentResolution | None = None
    pending: bool | None = None

class PullrequestEndpoint(StrictModel):
    repository: Repository | None = None
    branch: PullrequestEndpointBranch | None = None
    commit: PullrequestEndpointCommit | None = None

class Ref(PermissiveModel):
    """A ref object, representing a branch or tag in a repository."""
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: RefLinks | None = None
    name: str | None = Field(None, description="The name of the ref.")
    target: Commit | None = None

class Repository(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: RepositoryLinks | None = None
    uuid_: str | None = Field(None, validation_alias="uuid", serialization_alias="uuid", description="The repository's immutable id. This can be used as a substitute for the slug segment in URLs. Doing this guarantees your URLs will survive renaming of the repository by its owner, or even transfer of the repository to a different user.")
    full_name: str | None = Field(None, description="The concatenation of the repository owner's username and the slugified name, e.g. \"evzijst/interruptingcow\". This is the same string used in Bitbucket URLs.")
    is_private: bool | None = None
    parent: Repository | None = None
    scm: Literal["git"] | None = None
    owner: Account | None = None
    name: str | None = None
    description: str | None = None
    created_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_on: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    size: int | None = None
    language: str | None = None
    has_issues: bool | None = Field(None, description="\nThe issue tracker for this repository is enabled. Issue Tracker\nfeatures are not supported for repositories in workspaces\nadministered through admin.atlassian.com.\n")
    has_wiki: bool | None = Field(None, description="\nThe wiki for this repository is enabled. Wiki\nfeatures are not supported for repositories in workspaces\nadministered through admin.atlassian.com.\n")
    fork_policy: Literal["allow_forks", "no_public_forks", "no_forks"] | None = Field(None, description="\nControls the rules for forking this repository.\n\n* **allow_forks**: unrestricted forking\n* **no_public_forks**: restrict forking to private forks (forks cannot\n  be made public later)\n* **no_forks**: deny all forking\n")
    project: Project | None = None
    mainbranch: Branch | None = None

class Tag(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    links: TagLinks | None = None
    name: str | None = Field(None, description="The name of the ref.")
    target: Commit | None = None
    message: str | None = Field(None, description="The message associated with the tag, if available.")
    date: str | None = Field(None, description="The date that the tag was created, if available", json_schema_extra={'format': 'date-time'})
    tagger: Author | None = None


# Rebuild models to resolve forward references (required for circular refs)
Account.model_rebuild()
AccountLinks.model_rebuild()
Author.model_rebuild()
BaseCommit.model_rebuild()
BaseCommitSummary.model_rebuild()
BaseCommitV1Summary.model_rebuild()
Branch.model_rebuild()
BranchLinks.model_rebuild()
BranchLinksCommits.model_rebuild()
BranchLinksHtml.model_rebuild()
BranchLinksSelf.model_rebuild()
Branchrestriction.model_rebuild()
BranchrestrictionLinks.model_rebuild()
BranchrestrictionLinksSelf.model_rebuild()
BranchrestrictionV1Links.model_rebuild()
BranchrestrictionV1LinksSelf.model_rebuild()
Comment.model_rebuild()
CommentContent.model_rebuild()
CommentInline.model_rebuild()
CommentLinks.model_rebuild()
CommentLinksCode.model_rebuild()
CommentLinksHtml.model_rebuild()
CommentLinksSelf.model_rebuild()
CommentResolution.model_rebuild()
CommentV1Content.model_rebuild()
CommentV1Inline.model_rebuild()
CommentV1Links.model_rebuild()
CommentV1LinksCode.model_rebuild()
CommentV1LinksHtml.model_rebuild()
CommentV1LinksSelf.model_rebuild()
Commit.model_rebuild()
CommitComment.model_rebuild()
Commitstatus.model_rebuild()
CommitstatusLinks.model_rebuild()
CommitstatusLinksCommit.model_rebuild()
CommitstatusLinksSelf.model_rebuild()
CommitstatusV1Links.model_rebuild()
CommitstatusV1LinksCommit.model_rebuild()
CommitstatusV1LinksSelf.model_rebuild()
Committer.model_rebuild()
GpgAccountKey.model_rebuild()
GpgAccountKeyLinks.model_rebuild()
GpgAccountKeyLinksSelf.model_rebuild()
GpgAccountKeyV1Links.model_rebuild()
GpgAccountKeyV1LinksSelf.model_rebuild()
Group.model_rebuild()
GroupLinks.model_rebuild()
GroupLinksHtml.model_rebuild()
GroupLinksSelf.model_rebuild()
GroupV1Links.model_rebuild()
GroupV1LinksHtml.model_rebuild()
GroupV1LinksSelf.model_rebuild()
Link.model_rebuild()
ObjectModel.model_rebuild()
Participant.model_rebuild()
PipelineConfigurationSource.model_rebuild()
PipelineVariable.model_rebuild()
PostRepositoriesDeploymentsConfigEnvironmentsVariablesBody.model_rebuild()
PostRepositoriesEnvironmentsBody.model_rebuild()
PostRepositoriesPipelinesBody.model_rebuild()
PostRepositoriesPipelinesBodyCreator.model_rebuild()
PostRepositoriesPipelinesBodyCreatorLinks.model_rebuild()
PostRepositoriesPipelinesBodyCreatorLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyLinks.model_rebuild()
PostRepositoriesPipelinesBodyLinksSelf.model_rebuild()
PostRepositoriesPipelinesBodyLinksSteps.model_rebuild()
PostRepositoriesPipelinesBodyRepository.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksCloneItem.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksCommits.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksDownloads.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksForks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksHooks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksHtml.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksPullrequests.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksSelf.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryLinksWatchers.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranch.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchLinksCommits.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchLinksHtml.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchLinksSelf.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTarget.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthor.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUser.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUserLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetAuthorUserLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitter.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUser.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUserLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetCommitterUserLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryMainbranchTargetSummary.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryOwner.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryOwnerLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryOwnerLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProject.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectLinksHtml.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwner.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinks.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksAvatar.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksHtml.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksMembers.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksProjects.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksRepositories.model_rebuild()
PostRepositoriesPipelinesBodyRepositoryProjectOwnerLinksSelf.model_rebuild()
PostRepositoriesPipelinesBodyState.model_rebuild()
PostRepositoriesPipelinesBodyTarget.model_rebuild()
PostRepositoriesPipelinesBodyTrigger.model_rebuild()
PostRepositoriesPipelinesConfigSchedulesBody.model_rebuild()
PostRepositoriesPipelinesConfigSchedulesBodyTarget.model_rebuild()
PostRepositoriesPipelinesConfigSchedulesBodyTargetSelector.model_rebuild()
PostRepositoriesPipelinesConfigSshKnownHostsBody.model_rebuild()
PostRepositoriesPipelinesConfigSshKnownHostsBodyPublicKey.model_rebuild()
PostRepositoriesPipelinesConfigVariablesBody.model_rebuild()
PostRepositoriesPullrequestsTasksBodyComment.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentContent.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentInline.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentLinks.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentLinksCode.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentLinksHtml.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentLinksSelf.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentUser.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentUserLinks.model_rebuild()
PostRepositoriesPullrequestsTasksBodyCommentUserLinksAvatar.model_rebuild()
Project.model_rebuild()
ProjectLinks.model_rebuild()
ProjectLinksAvatar.model_rebuild()
ProjectLinksHtml.model_rebuild()
ProjectV1Links.model_rebuild()
ProjectV1LinksAvatar.model_rebuild()
ProjectV1LinksHtml.model_rebuild()
Pullrequest.model_rebuild()
PullrequestComment.model_rebuild()
PullrequestEndpoint.model_rebuild()
PullrequestEndpointBranch.model_rebuild()
PullrequestEndpointCommit.model_rebuild()
PullrequestLinks.model_rebuild()
PullrequestLinksActivity.model_rebuild()
PullrequestLinksApprove.model_rebuild()
PullrequestLinksComments.model_rebuild()
PullrequestLinksCommits.model_rebuild()
PullrequestLinksDecline.model_rebuild()
PullrequestLinksDiff.model_rebuild()
PullrequestLinksDiffstat.model_rebuild()
PullrequestLinksHtml.model_rebuild()
PullrequestLinksMerge.model_rebuild()
PullrequestLinksSelf.model_rebuild()
PullrequestMergeCommit.model_rebuild()
PullrequestRendered.model_rebuild()
PullrequestRenderedDescription.model_rebuild()
PullrequestRenderedReason.model_rebuild()
PullrequestRenderedTitle.model_rebuild()
PullrequestSummary.model_rebuild()
PullrequestV1Links.model_rebuild()
PullrequestV1LinksActivity.model_rebuild()
PullrequestV1LinksApprove.model_rebuild()
PullrequestV1LinksComments.model_rebuild()
PullrequestV1LinksCommits.model_rebuild()
PullrequestV1LinksDecline.model_rebuild()
PullrequestV1LinksDiff.model_rebuild()
PullrequestV1LinksDiffstat.model_rebuild()
PullrequestV1LinksHtml.model_rebuild()
PullrequestV1LinksMerge.model_rebuild()
PullrequestV1LinksSelf.model_rebuild()
PullrequestV1MergeCommit.model_rebuild()
PullrequestV1Rendered.model_rebuild()
PullrequestV1RenderedDescription.model_rebuild()
PullrequestV1RenderedReason.model_rebuild()
PullrequestV1RenderedTitle.model_rebuild()
PullrequestV1Summary.model_rebuild()
PutRepositoriesCommitReportsAnnotationsBody.model_rebuild()
PutRepositoriesCommitReportsBody.model_rebuild()
PutRepositoriesDeploymentsConfigEnvironmentsVariablesBody.model_rebuild()
PutRepositoriesPipelinesConfigBuildNumberBody.model_rebuild()
PutRepositoriesPipelinesConfigSchedulesBody.model_rebuild()
PutRepositoriesPipelinesConfigSshKeyPairBody.model_rebuild()
PutRepositoriesPipelinesConfigSshKnownHostsBody.model_rebuild()
PutRepositoriesPipelinesConfigSshKnownHostsBodyPublicKey.model_rebuild()
PutRepositoriesPipelinesConfigVariablesBody.model_rebuild()
Ref.model_rebuild()
RefLinks.model_rebuild()
RefLinksCommits.model_rebuild()
RefLinksHtml.model_rebuild()
RefLinksSelf.model_rebuild()
ReportAnnotation.model_rebuild()
ReportData.model_rebuild()
Repository.model_rebuild()
RepositoryLinks.model_rebuild()
RepositoryLinksAvatar.model_rebuild()
RepositoryLinksCloneItem.model_rebuild()
RepositoryLinksCommits.model_rebuild()
RepositoryLinksDownloads.model_rebuild()
RepositoryLinksForks.model_rebuild()
RepositoryLinksHooks.model_rebuild()
RepositoryLinksHtml.model_rebuild()
RepositoryLinksPullrequests.model_rebuild()
RepositoryLinksSelf.model_rebuild()
RepositoryLinksWatchers.model_rebuild()
RepositoryV1Links.model_rebuild()
RepositoryV1LinksAvatar.model_rebuild()
RepositoryV1LinksCloneItem.model_rebuild()
RepositoryV1LinksCommits.model_rebuild()
RepositoryV1LinksDownloads.model_rebuild()
RepositoryV1LinksForks.model_rebuild()
RepositoryV1LinksHooks.model_rebuild()
RepositoryV1LinksHtml.model_rebuild()
RepositoryV1LinksPullrequests.model_rebuild()
RepositoryV1LinksSelf.model_rebuild()
RepositoryV1LinksWatchers.model_rebuild()
Snippet.model_rebuild()
SnippetComment.model_rebuild()
SnippetCommentLinks.model_rebuild()
SnippetCommentLinksHtml.model_rebuild()
SnippetCommentLinksSelf.model_rebuild()
SnippetCommentV1Links.model_rebuild()
SnippetCommentV1LinksHtml.model_rebuild()
SnippetCommentV1LinksSelf.model_rebuild()
SshAccountKey.model_rebuild()
SshKey.model_rebuild()
SshKeyLinks.model_rebuild()
SshKeyLinksSelf.model_rebuild()
SshKeyV1Links.model_rebuild()
SshKeyV1LinksSelf.model_rebuild()
Tag.model_rebuild()
TagLinks.model_rebuild()
TagLinksCommits.model_rebuild()
TagLinksHtml.model_rebuild()
TagLinksSelf.model_rebuild()
Team.model_rebuild()
TeamLinks.model_rebuild()
User.model_rebuild()
UserLinks.model_rebuild()
Workspace.model_rebuild()
WorkspaceLinks.model_rebuild()
WorkspaceLinksAvatar.model_rebuild()
WorkspaceLinksHtml.model_rebuild()
WorkspaceLinksMembers.model_rebuild()
WorkspaceLinksOwners.model_rebuild()
WorkspaceLinksProjects.model_rebuild()
WorkspaceLinksRepositories.model_rebuild()
WorkspaceLinksSelf.model_rebuild()
WorkspaceLinksSnippets.model_rebuild()
WorkspaceV1Links.model_rebuild()
WorkspaceV1LinksAvatar.model_rebuild()
WorkspaceV1LinksHtml.model_rebuild()
WorkspaceV1LinksMembers.model_rebuild()
WorkspaceV1LinksOwners.model_rebuild()
WorkspaceV1LinksProjects.model_rebuild()
WorkspaceV1LinksRepositories.model_rebuild()
WorkspaceV1LinksSelf.model_rebuild()
WorkspaceV1LinksSnippets.model_rebuild()

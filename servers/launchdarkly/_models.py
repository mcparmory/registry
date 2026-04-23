"""
Launchdarkly MCP Server - Pydantic Models

Generated: 2026-04-23 21:25:48 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AssociateRepositoriesAndProjectsRequest",
    "CopyFeatureFlagRequest",
    "CreateAnnouncementPublicRequest",
    "CreateBigSegmentExportRequest",
    "CreateBigSegmentImportRequest",
    "CreateDeploymentEventRequest",
    "CreateExperimentRequest",
    "CreateInsightGroupRequest",
    "CreateLayerRequest",
    "CreateMetricGroupRequest",
    "CreateReleaseForFlagRequest",
    "CreateTriggerWorkflowRequest",
    "CreateViewRequest",
    "DeleteAgentGraphRequest",
    "DeleteAgentOptimizationRequest",
    "DeleteAiConfigRequest",
    "DeleteAiConfigVariationRequest",
    "DeleteAiToolRequest",
    "DeleteAnnouncementPublicRequest",
    "DeleteApplicationRequest",
    "DeleteApplicationVersionRequest",
    "DeleteApprovalRequest",
    "DeleteApprovalRequestForFlagRequest",
    "DeleteBranchesRequest",
    "DeleteContextInstancesRequest",
    "DeleteCustomRoleRequest",
    "DeleteDestinationRequest",
    "DeleteEnvironmentRequest",
    "DeleteFeatureFlagRequest",
    "DeleteFlagConfigScheduledChangesRequest",
    "DeleteFlagFollowerRequest",
    "DeleteInsightGroupRequest",
    "DeleteMemberRequest",
    "DeleteMetricGroupRequest",
    "DeleteMetricRequest",
    "DeleteModelConfigRequest",
    "DeleteOAuthClientRequest",
    "DeleteProjectRequest",
    "DeletePromptSnippetRequest",
    "DeleteRelayAutoConfigRequest",
    "DeleteReleaseByFlagKeyRequest",
    "DeleteReleasePipelineRequest",
    "DeleteReleasePolicyRequest",
    "DeleteRepositoryProjectRequest",
    "DeleteRepositoryRequest",
    "DeleteRestrictedModelsRequest",
    "DeleteSegmentRequest",
    "DeleteSubscriptionRequest",
    "DeleteTeamRequest",
    "DeleteTokenRequest",
    "DeleteTriggerWorkflowRequest",
    "DeleteViewRequest",
    "DeleteWebhookRequest",
    "DeleteWorkflowRequest",
    "GetAgentGraphRequest",
    "GetAgentOptimizationRequest",
    "GetAiConfigMetricsByVariationRequest",
    "GetAiConfigMetricsRequest",
    "GetAiConfigQuickStatsRequest",
    "GetAiConfigRequest",
    "GetAiConfigsRequest",
    "GetAiConfigTargetingRequest",
    "GetAiConfigVariationRequest",
    "GetAiToolRequest",
    "GetAllReleasePipelinesRequest",
    "GetAllReleaseProgressionsForReleasePipelineRequest",
    "GetAnnouncementsPublicRequest",
    "GetApplicationRequest",
    "GetApplicationVersionsRequest",
    "GetApprovalForFlagRequest",
    "GetApprovalRequest",
    "GetApprovalsForFlagRequest",
    "GetAuditLogEntriesRequest",
    "GetAuditLogEntryRequest",
    "GetBigSegmentExportRequest",
    "GetBigSegmentImportRequest",
    "GetBranchesRequest",
    "GetBranchRequest",
    "GetContextAttributeNamesRequest",
    "GetContextAttributeValuesRequest",
    "GetContextInstanceSegmentsMembershipByEnvRequest",
    "GetContextInstancesRequest",
    "GetContextKindsByProjectKeyRequest",
    "GetContextsRequest",
    "GetCustomRoleRequest",
    "GetCustomWorkflowRequest",
    "GetDeploymentFrequencyChartRequest",
    "GetDeploymentRequest",
    "GetDeploymentsRequest",
    "GetDestinationRequest",
    "GetEnvironmentRequest",
    "GetEnvironmentsByProjectRequest",
    "GetEventsUsageRequest",
    "GetExperimentationSettingsRequest",
    "GetExperimentRequest",
    "GetExperimentsAnyEnvRequest",
    "GetExperimentsRequest",
    "GetExpiringContextTargetsRequest",
    "GetExpiringTargetsForSegmentRequest",
    "GetExpiringUserTargetsForSegmentRequest",
    "GetExpiringUserTargetsRequest",
    "GetExtinctionsRequest",
    "GetFeatureFlagRequest",
    "GetFeatureFlagScheduledChangeRequest",
    "GetFeatureFlagsRequest",
    "GetFeatureFlagStatusAcrossEnvironmentsRequest",
    "GetFeatureFlagStatusesRequest",
    "GetFeatureFlagStatusRequest",
    "GetFlagConfigScheduledChangesRequest",
    "GetFlagDefaultsByProjectRequest",
    "GetFlagEventsRequest",
    "GetFlagFollowersRequest",
    "GetFlagStatusChartRequest",
    "GetFollowersByProjEnvRequest",
    "GetInsightGroupRequest",
    "GetInsightGroupsRequest",
    "GetInsightsScoresRequest",
    "GetLayersRequest",
    "GetLeadTimeChartRequest",
    "GetLinkedResourcesRequest",
    "GetLinkedViewsRequest",
    "GetMemberRequest",
    "GetMetricGroupRequest",
    "GetMetricGroupsRequest",
    "GetMetricRequest",
    "GetMetricsRequest",
    "GetModelConfigRequest",
    "GetOAuthClientByIdRequest",
    "GetProjectRequest",
    "GetPromptSnippetRequest",
    "GetPullRequestsRequest",
    "GetRelayProxyConfigRequest",
    "GetReleaseByFlagKeyRequest",
    "GetReleaseFrequencyChartRequest",
    "GetReleasePipelineByKeyRequest",
    "GetReleasePoliciesRequest",
    "GetReleasePolicyRequest",
    "GetRepositoriesRequest",
    "GetRepositoryRequest",
    "GetSegmentMembershipForContextRequest",
    "GetSegmentMembershipForUserRequest",
    "GetSegmentRequest",
    "GetSegmentsRequest",
    "GetStaleFlagsChartRequest",
    "GetStatisticsRequest",
    "GetSubscriptionByIdRequest",
    "GetSubscriptionsRequest",
    "GetTagsRequest",
    "GetTeamMaintainersRequest",
    "GetTeamRequest",
    "GetTeamRolesRequest",
    "GetTokenRequest",
    "GetTriggerWorkflowByIdRequest",
    "GetTriggerWorkflowsRequest",
    "GetViewRequest",
    "GetViewsRequest",
    "GetWebhookRequest",
    "GetWorkflowsRequest",
    "GetWorkflowTemplatesRequest",
    "LinkResourceRequest",
    "ListAgentGraphsRequest",
    "ListAgentOptimizationsRequest",
    "ListAiToolsRequest",
    "ListAiToolVersionsRequest",
    "ListModelConfigsRequest",
    "ListPromptSnippetReferencesRequest",
    "ListPromptSnippetsRequest",
    "PatchAgentGraphRequest",
    "PatchAgentOptimizationRequest",
    "PatchAiConfigRequest",
    "PatchAiConfigTargetingRequest",
    "PatchAiConfigVariationRequest",
    "PatchAiToolRequest",
    "PatchApplicationRequest",
    "PatchApplicationVersionRequest",
    "PatchApprovalRequest",
    "PatchApprovalRequestSettingsRequest",
    "PatchCustomRoleRequest",
    "PatchDestinationRequest",
    "PatchEnvironmentRequest",
    "PatchExperimentRequest",
    "PatchExpiringTargetsForSegmentRequest",
    "PatchExpiringTargetsRequest",
    "PatchExpiringUserTargetsForSegmentRequest",
    "PatchExpiringUserTargetsRequest",
    "PatchFeatureFlagRequest",
    "PatchFlagConfigScheduledChangeRequest",
    "PatchFlagDefaultsByProjectRequest",
    "PatchInsightGroupRequest",
    "PatchMemberRequest",
    "PatchMembersRequest",
    "PatchMetricGroupRequest",
    "PatchMetricRequest",
    "PatchOAuthClientRequest",
    "PatchProjectRequest",
    "PatchPromptSnippetRequest",
    "PatchRelayAutoConfigRequest",
    "PatchReleaseByFlagKeyRequest",
    "PatchRepositoryRequest",
    "PatchSegmentRequest",
    "PatchTeamRequest",
    "PatchTokenRequest",
    "PatchTriggerWorkflowRequest",
    "PatchWebhookRequest",
    "PostAgentGraphRequest",
    "PostAgentOptimizationRequest",
    "PostAiConfigRequest",
    "PostAiConfigVariationRequest",
    "PostAiToolRequest",
    "PostApprovalRequest",
    "PostApprovalRequestApplyForFlagRequest",
    "PostApprovalRequestApplyRequest",
    "PostApprovalRequestForFlagRequest",
    "PostApprovalRequestReviewForFlagRequest",
    "PostApprovalRequestReviewRequest",
    "PostAuditLogEntriesRequest",
    "PostDestinationRequest",
    "PostEnvironmentRequest",
    "PostExtinctionRequest",
    "PostFeatureFlagRequest",
    "PostFlagConfigScheduledChangesRequest",
    "PostFlagCopyConfigApprovalRequest",
    "PostGenerateProjectEnvWarehouseDestinationKeyPairRequest",
    "PostMembersRequest",
    "PostMemberTeamsRequest",
    "PostMetricRequest",
    "PostMigrationSafetyIssuesRequest",
    "PostModelConfigRequest",
    "PostProjectRequest",
    "PostPromptSnippetRequest",
    "PostRelayAutoConfigRequest",
    "PostReleasePipelineRequest",
    "PostReleasePoliciesOrderRequest",
    "PostRepositoryRequest",
    "PostRestrictedModelsRequest",
    "PostSegmentRequest",
    "PostTeamMembersRequest",
    "PostTeamRequest",
    "PutBranchRequest",
    "PutContextFlagSettingRequest",
    "PutContextKindRequest",
    "PutExperimentationSettingsRequest",
    "PutFlagDefaultsByProjectRequest",
    "PutFlagFollowerRequest",
    "PutReleasePipelineRequest",
    "PutReleasePolicyRequest",
    "ResetEnvironmentMobileKeyRequest",
    "ResetEnvironmentSdkKeyRequest",
    "ResetRelayAutoConfigRequest",
    "ResetTokenRequest",
    "SearchContextInstancesRequest",
    "SearchContextsRequest",
    "UnlinkResourceRequest",
    "UpdateAnnouncementPublicRequest",
    "UpdateBigSegmentContextTargetsRequest",
    "UpdateBigSegmentTargetsRequest",
    "UpdateDeploymentRequest",
    "UpdateLayerRequest",
    "UpdatePhaseStatusRequest",
    "UpdateSubscriptionRequest",
    "UpdateViewRequest",
    "AgentGraphEdge",
    "AgentGraphEdgePost",
    "AgentOptimizationAcceptanceStatement",
    "AgentOptimizationJudge",
    "AnnouncementPatchOperation",
    "CreatePhaseInput",
    "CustomProperty",
    "EnvironmentPost",
    "Extinction",
    "FlagInput",
    "FlagPrerequisitePost",
    "InsightsRepositoryProject",
    "Instruction",
    "JudgeAttachment",
    "Message",
    "MetricInMetricGroupInput",
    "MetricInput",
    "NewMemberForm",
    "PatchOperation",
    "PatchSegmentExpiringTargetInstruction",
    "PatchSegmentInstruction",
    "PermissionGrantInput",
    "RandomizationUnitInput",
    "ReferenceRep",
    "ReleasePolicyStage",
    "ReleaserAudienceConfigInput",
    "RoleAttributeValues",
    "Statement",
    "StatementPost",
    "TreatmentInput",
    "UrlPost",
    "Variation",
    "ViewLinkRequestFilter",
    "ViewLinkRequestKeys",
    "ViewLinkRequestSegmentIdentifiers",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_relay_proxy_config
class PostRelayAutoConfigRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for this Relay Proxy configuration. Used to identify and manage the configuration.")
    policy: list[Statement] = Field(default=..., description="An inline policy array that defines which environments and projects this Relay Proxy should include or exclude. Policy items are evaluated in order to determine scope. Refer to the inline policy documentation for syntax and structure.")
class PostRelayAutoConfigRequest(StrictModel):
    """Create a new Relay Proxy configuration that controls which environments and projects the Relay Proxy should include or exclude."""
    body: PostRelayAutoConfigRequestBody

# Operation: get_relay_proxy_config
class GetRelayProxyConfigRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the relay auto config to retrieve.", json_schema_extra={'format': 'string'})
class GetRelayProxyConfigRequest(StrictModel):
    """Retrieve a single Relay Proxy auto configuration by its unique identifier. Use this to fetch detailed settings for a specific relay proxy configuration."""
    path: GetRelayProxyConfigRequestPath

# Operation: update_relay_auto_config
class PatchRelayAutoConfigRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Relay Proxy configuration to update.", json_schema_extra={'format': 'string'})
class PatchRelayAutoConfigRequestBody(StrictModel):
    patch: list[PatchOperation] = Field(default=..., description="An array of JSON patch operations (RFC 6902) or JSON merge patch operations (RFC 7386) describing the changes to apply to the configuration.")
class PatchRelayAutoConfigRequest(StrictModel):
    """Update a Relay Proxy configuration using JSON patch or JSON merge patch operations. Changes are applied incrementally to the specified configuration."""
    path: PatchRelayAutoConfigRequestPath
    body: PatchRelayAutoConfigRequestBody

# Operation: delete_relay_auto_config
class DeleteRelayAutoConfigRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the relay auto config to delete. This is a string value that uniquely identifies the configuration within your account.", json_schema_extra={'format': 'string'})
class DeleteRelayAutoConfigRequest(StrictModel):
    """Delete a Relay Proxy auto-configuration by its unique identifier. This operation permanently removes the specified relay auto config from your account."""
    path: DeleteRelayAutoConfigRequestPath

# Operation: reset_relay_auto_config
class ResetRelayAutoConfigRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Relay Proxy configuration to reset.", json_schema_extra={'format': 'string'})
class ResetRelayAutoConfigRequestQuery(StrictModel):
    expiry: int | None = Field(default=None, description="Optional Unix epoch time in milliseconds when the old configuration key should expire. If not provided, the old key expires immediately upon reset.", json_schema_extra={'format': 'int64'})
class ResetRelayAutoConfigRequest(StrictModel):
    """Generate a new secret key for a Relay Proxy configuration, optionally setting an expiration time for the previous key before it becomes invalid."""
    path: ResetRelayAutoConfigRequestPath
    query: ResetRelayAutoConfigRequestQuery | None = None

# Operation: get_application
class GetApplicationRequestPath(StrictModel):
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The unique identifier for the application. This is a string value that uniquely identifies the application within your LaunchDarkly workspace.", json_schema_extra={'format': 'string'})
class GetApplicationRequest(StrictModel):
    """Retrieve a LaunchDarkly application by its unique application key. Optionally expand the response to include evaluated flags and other application details."""
    path: GetApplicationRequestPath

# Operation: update_application
class PatchApplicationRequestPath(StrictModel):
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The unique identifier for the application to update.", json_schema_extra={'format': 'string'})
class PatchApplicationRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type), 'path' (the field to modify), and 'value' (the new value for replace operations). Supported paths include '/description' and '/kind'.", examples=[[{'op': 'replace', 'path': '/description', 'value': 'Updated description'}]])
class PatchApplicationRequest(StrictModel):
    """Update an application's description and kind fields using JSON Patch format. Specify changes as an array of patch operations following RFC 6902 standard."""
    path: PatchApplicationRequestPath
    body: PatchApplicationRequestBody

# Operation: delete_application
class DeleteApplicationRequestPath(StrictModel):
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The unique identifier for the application to delete. This is a string value that uniquely identifies the application within the system.", json_schema_extra={'format': 'string'})
class DeleteApplicationRequest(StrictModel):
    """Permanently delete an application by its unique key. This action cannot be undone and will remove all associated data."""
    path: DeleteApplicationRequestPath

# Operation: list_application_versions
class GetApplicationVersionsRequestPath(StrictModel):
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The unique identifier for the application. This string key is used to look up and retrieve all versions belonging to that specific application.", json_schema_extra={'format': 'string'})
class GetApplicationVersionsRequest(StrictModel):
    """Retrieve all versions for a specific application identified by its application key. Returns a list of version records associated with the application in the account."""
    path: GetApplicationVersionsRequestPath

# Operation: update_application_version
class PatchApplicationVersionRequestPath(StrictModel):
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The unique identifier for the application being modified.", json_schema_extra={'format': 'string'})
    version_key: str = Field(default=..., validation_alias="versionKey", serialization_alias="versionKey", description="The unique identifier for the specific application version to update.", json_schema_extra={'format': 'string'})
class PatchApplicationVersionRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="A JSON Patch array describing the changes to apply. Each operation must specify an `op` (operation type like 'replace'), `path` (the field to modify), and `value` (the new value). Multiple operations can be included in a single request.", examples=[[{'op': 'replace', 'path': '/supported', 'value': 'false'}]])
class PatchApplicationVersionRequest(StrictModel):
    """Update an application version using JSON Patch operations. Currently supports updating the `supported` field to enable or disable the version."""
    path: PatchApplicationVersionRequestPath
    body: PatchApplicationVersionRequestBody

# Operation: delete_application_version
class DeleteApplicationVersionRequestPath(StrictModel):
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The unique identifier for the application containing the version to delete.", json_schema_extra={'format': 'string'})
    version_key: str = Field(default=..., validation_alias="versionKey", serialization_alias="versionKey", description="The unique identifier for the specific application version to delete.", json_schema_extra={'format': 'string'})
class DeleteApplicationVersionRequest(StrictModel):
    """Permanently delete a specific version of an application. This operation removes the version and all associated data."""
    path: DeleteApplicationVersionRequestPath

# Operation: create_approval_request
class PostApprovalRequestBody(StrictModel):
    resource_id: str = Field(default=..., validation_alias="resourceId", serialization_alias="resourceId", description="The resource identifier in the format proj/projKey:env/envKey:flag/flagKey (or equivalent for AI Configs and segments). Specifies which resource the approval request applies to.")
    description: str = Field(default=..., description="A brief summary of the requested changes. This helps reviewers understand the intent of the approval request.")
    instructions: list[Instruction] = Field(default=..., description="An ordered list of semantic patch instructions to apply when the approval is granted. Instructions vary by resource type: use addVariation, removeVariation, updateVariation, or updateDefaultVariation for flags; refer to AI Config or segment patch documentation for other resource types.")
    integration_config: dict[str, Any] | None = Field(default=None, validation_alias="integrationConfig", serialization_alias="integrationConfig", description="Optional object containing additional fields for third-party approval system integrations. Field requirements are defined in the manifest.json of the specific integration being used.")
class PostApprovalRequest(StrictModel):
    """Create an approval request for changes to a feature flag, AI Config, or segment. The request includes semantic patch instructions that will be applied upon approval."""
    body: PostApprovalRequestBody

# Operation: get_approval_request
class GetApprovalRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the approval request to retrieve.", json_schema_extra={'format': 'string'})
class GetApprovalRequest(StrictModel):
    """Retrieve a specific approval request by its ID. Optionally expand the response to include related resources such as environments, flags, projects, or resource details."""
    path: GetApprovalRequestPath

# Operation: update_approval_request
class PatchApprovalRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the approval request to update.", json_schema_extra={'format': 'string'})
class PatchApprovalRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instructions to apply. Each instruction specifies an operation (addReviewers or updateDescription) with its required parameters. At least one instruction must be provided.")
class PatchApprovalRequest(StrictModel):
    """Update an approval request using semantic patch instructions. Supports adding reviewers or updating the request description through a structured instruction format."""
    path: PatchApprovalRequestPath
    body: PatchApprovalRequestBody

# Operation: delete_approval_request
class DeleteApprovalRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the approval request to delete.", json_schema_extra={'format': 'string'})
class DeleteApprovalRequest(StrictModel):
    """Permanently delete an approval request by its ID. This action cannot be undone."""
    path: DeleteApprovalRequestPath

# Operation: apply_approval_request
class PostApprovalRequestApplyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the approval request to apply. This is a string value that identifies which approval request should be executed.", json_schema_extra={'format': 'string'})
class PostApprovalRequestApplyRequest(StrictModel):
    """Execute an approval request that has been approved. This operation finalizes the approval workflow for any approval request type."""
    path: PostApprovalRequestApplyRequestPath

# Operation: submit_approval_request_review
class PostApprovalRequestReviewRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the approval request being reviewed.", json_schema_extra={'format': 'string'})
class PostApprovalRequestReviewRequestBody(StrictModel):
    kind: Literal["approve", "comment", "decline"] | None = Field(default=None, description="The type of review action to perform: 'approve' to accept the changes, 'decline' to reject them, or 'comment' to provide feedback without making a final decision.")
class PostApprovalRequestReviewRequest(StrictModel):
    """Submit a review decision on an approval request by approving, declining, or adding a comment to the proposed changes."""
    path: PostApprovalRequestReviewRequestPath
    body: PostApprovalRequestReviewRequestBody | None = None

# Operation: list_audit_log_entries
class GetAuditLogEntriesRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="Full or partial resource name to search for in audit logs. Supports text-based matching across resource identifiers.", json_schema_extra={'format': 'string'})
    spec: str | None = Field(default=None, description="Resource specifier to filter results by specific resources or resource collections. Use LaunchDarkly resource specifier syntax to target particular resource types or instances.", json_schema_extra={'format': 'string'})
class GetAuditLogEntriesRequest(StrictModel):
    """Retrieve audit log entries with optional filtering by date ranges, resource specifiers, or full-text search. Use resource specifier syntax to target specific resources or collections."""
    query: GetAuditLogEntriesRequestQuery | None = None

# Operation: search_audit_log_entries
class PostAuditLogEntriesRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="Full-text search query to filter audit log entries by resource name or partial matches. Searches across resource names and related metadata.", json_schema_extra={'format': 'string'})
class PostAuditLogEntriesRequestBody(StrictModel):
    body: list[StatementPost] | None = Field(default=None, description="Array of resource specifiers to restrict results to specific resources or resource collections. Use LaunchDarkly resource specifier syntax to target particular entities (e.g., projects, environments, flags). Order is not significant.")
class PostAuditLogEntriesRequest(StrictModel):
    """Search audit log entries by full-text query and resource specifiers. Filter results by date ranges and resource types using query parameters and request body constraints."""
    query: PostAuditLogEntriesRequestQuery | None = None
    body: PostAuditLogEntriesRequestBody | None = None

# Operation: get_audit_log_entry
class GetAuditLogEntryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the audit log entry to retrieve.", json_schema_extra={'format': 'string'})
class GetAuditLogEntryRequest(StrictModel):
    """Retrieve a detailed audit log entry with full change history. Returns comprehensive metadata including the previous and current versions of the modified entity, plus the JSON patch or semantic patch that was applied."""
    path: GetAuditLogEntryRequestPath

# Operation: list_extinctions
class GetExtinctionsRequestQuery(StrictModel):
    repo_name: str | None = Field(default=None, validation_alias="repoName", serialization_alias="repoName", description="Filter results to extinctions in a specific repository by name.", json_schema_extra={'format': 'string'})
    branch_name: str | None = Field(default=None, validation_alias="branchName", serialization_alias="branchName", description="Filter results to extinctions in a specific branch. If not specified, only the default branch is queried.", json_schema_extra={'format': 'string'})
    proj_key: str | None = Field(default=None, validation_alias="projKey", serialization_alias="projKey", description="Filter results to extinctions in a specific project by project key.", json_schema_extra={'format': 'string'})
    from_: int | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Filter results to extinctions after a specific point in time, expressed as a Unix epoch timestamp in milliseconds. Must be used together with the `to` parameter.", json_schema_extra={'format': 'int64'})
    to: int | None = Field(default=None, description="Filter results to extinctions before a specific point in time, expressed as a Unix epoch timestamp in milliseconds. Must be used together with the `from` parameter.", json_schema_extra={'format': 'int64'})
class GetExtinctionsRequest(StrictModel):
    """Retrieve a list of all extinction events, which are created when all code references to a flag are removed. Filter results by repository, branch, project, or commit time window to find specific extinctions."""
    query: GetExtinctionsRequestQuery | None = None

# Operation: list_repositories
class GetRepositoriesRequestQuery(StrictModel):
    with_branches: str | None = Field(default=None, validation_alias="withBranches", serialization_alias="withBranches", description="Include branch metadata in the response. Set to any value to enable this option.", json_schema_extra={'format': 'string'})
    with_references_for_default_branch: str | None = Field(default=None, validation_alias="withReferencesForDefaultBranch", serialization_alias="withReferencesForDefaultBranch", description="Include branch metadata and code references for the default git branch in the response. Set to any value to enable this option.", json_schema_extra={'format': 'string'})
    proj_key: str | None = Field(default=None, validation_alias="projKey", serialization_alias="projKey", description="Filter code reference results to a specific LaunchDarkly project by providing its project key.", json_schema_extra={'format': 'string'})
class GetRepositoriesRequest(StrictModel):
    """Retrieve a list of connected repositories with optional branch metadata and code references. Filter results by project key to scope code references to a specific LaunchDarkly project."""
    query: GetRepositoriesRequestQuery | None = None

# Operation: create_repository
class PostRepositoryRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the repository (e.g., 'LaunchDarkly-Docs'). Used as the unique identifier for this repository.")
    source_link: str | None = Field(default=None, validation_alias="sourceLink", serialization_alias="sourceLink", description="A URL where the repository can be accessed (e.g., a GitHub repository URL). Provides a direct link to the repository source.")
    commit_url_template: str | None = Field(default=None, validation_alias="commitUrlTemplate", serialization_alias="commitUrlTemplate", description="A URL template for constructing links to specific commits. Use the placeholder ${sha} to represent the commit hash (e.g., 'https://github.com/launchdarkly/LaunchDarkly-Docs/commit/${sha}').")
    hunk_url_template: str | None = Field(default=None, validation_alias="hunkUrlTemplate", serialization_alias="hunkUrlTemplate", description="A URL template for constructing links to specific code hunks or lines. Use placeholders ${sha} for commit hash, ${filePath} for file path, and ${lineNumber} for line number (e.g., 'https://github.com/launchdarkly/LaunchDarkly-Docs/blob/${sha}/${filePath}#L${lineNumber}').")
    default_branch: str | None = Field(default=None, validation_alias="defaultBranch", serialization_alias="defaultBranch", description="The repository's default branch name. Defaults to 'main' if not specified (e.g., 'main', 'master', or 'develop').")
class PostRepositoryRequest(StrictModel):
    """Create a new code repository for tracking feature flag references. Optionally provide URLs for accessing the repository and constructing links to specific commits and code hunks."""
    body: PostRepositoryRequestBody

# Operation: get_repository
class GetRepositoryRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository to retrieve. This is a string identifier that uniquely identifies the repository within the system.", json_schema_extra={'format': 'string'})
class GetRepositoryRequest(StrictModel):
    """Retrieve a single repository by its name. Use this to fetch detailed information about a specific code repository tracked in the system."""
    path: GetRepositoryRequestPath

# Operation: update_repository
class PatchRepositoryRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository to update. This identifier is used to locate the specific repository in the system.", json_schema_extra={'format': 'string'})
class PatchRepositoryRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of patch operations describing the changes to apply. Each operation should specify an action (op), a JSON pointer path (path), and the new value (value) where applicable. Operations are processed in the order provided.", examples=[[{'op': 'replace', 'path': '/defaultBranch', 'value': 'main'}]])
class PatchRepositoryRequest(StrictModel):
    """Update a repository's settings using JSON patch or JSON merge patch operations. Changes are applied according to RFC 6902 or RFC 7386 standards."""
    path: PatchRepositoryRequestPath
    body: PatchRepositoryRequestBody

# Operation: delete_repository
class DeleteRepositoryRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository to delete. Must be a valid string identifier.", json_schema_extra={'format': 'string'})
class DeleteRepositoryRequest(StrictModel):
    """Permanently delete a repository and all associated code references. This action cannot be undone."""
    path: DeleteRepositoryRequestPath

# Operation: delete_branches
class DeleteBranchesRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository from which branches will be deleted.", json_schema_extra={'format': 'string'})
class DeleteBranchesRequestBody(StrictModel):
    body: list[str] = Field(default=..., description="An array of branch names to delete. Each item should be a string representing a branch name. Order is not significant.", examples=[['branch-to-be-deleted', 'another-branch-to-be-deleted']])
class DeleteBranchesRequest(StrictModel):
    """Asynchronously delete multiple branches from a repository. Returns a task that processes the branch deletions in the background."""
    path: DeleteBranchesRequestPath
    body: DeleteBranchesRequestBody

# Operation: list_branches
class GetBranchesRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository to list branches from. This is a required identifier that specifies which repository's branches to retrieve.", json_schema_extra={'format': 'string'})
class GetBranchesRequest(StrictModel):
    """Retrieve a list of all branches in the specified repository. Use this to discover available branches for code references and analysis."""
    path: GetBranchesRequestPath

# Operation: get_branch
class GetBranchRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository containing the branch.", json_schema_extra={'format': 'string'})
    branch: str = Field(default=..., description="The name of the branch to retrieve, URL-encoded to handle special characters in branch names.", json_schema_extra={'format': 'string'})
class GetBranchRequestQuery(StrictModel):
    proj_key: str | None = Field(default=None, validation_alias="projKey", serialization_alias="projKey", description="Optional project key to scope the branch lookup to a specific project within the repository.", json_schema_extra={'format': 'string'})
class GetBranchRequest(StrictModel):
    """Retrieve detailed information about a specific branch within a repository, optionally filtered to a particular project."""
    path: GetBranchRequestPath
    query: GetBranchRequestQuery | None = None

# Operation: upsert_branch
class PutBranchRequestPath(StrictModel):
    repo: str = Field(default=..., description="The name of the repository where the branch exists or will be created.", json_schema_extra={'format': 'string'})
    branch: str = Field(default=..., description="The branch name as it appears in the URL, URL-encoded if it contains special characters.", json_schema_extra={'format': 'string'})
class PutBranchRequestBody(StrictModel):
    name: str = Field(default=..., description="The human-readable branch name (e.g., 'main', 'develop'). This is the actual branch identifier.")
    head: str = Field(default=..., description="A commit identifier representing the current HEAD of the branch, typically a commit SHA hash.")
    sync_time: int = Field(default=..., validation_alias="syncTime", serialization_alias="syncTime", description="A Unix timestamp (in milliseconds or seconds as int64) indicating when this branch was last synchronized with the source.", json_schema_extra={'format': 'int64'})
    references: list[ReferenceRep] | None = Field(default=None, description="An optional array of flag references discovered on this branch. Order and format depend on the flag reference structure used by the system.")
class PutBranchRequest(StrictModel):
    """Create a new branch or update an existing branch in a repository. Use this to sync branch metadata including the current HEAD commit and last sync timestamp."""
    path: PutBranchRequestPath
    body: PutBranchRequestBody

# Operation: create_extinction_event
class PostExtinctionRequestPath(StrictModel):
    repo: str = Field(default=..., description="The repository name where the extinction event will be created.", json_schema_extra={'format': 'string'})
    branch: str = Field(default=..., description="The branch name, URL-encoded, where the extinction event applies.", json_schema_extra={'format': 'string'})
class PostExtinctionRequestBody(StrictModel):
    body: list[Extinction] = Field(default=..., description="Array of extinction event objects defining the code references and metadata for the extinction event.")
class PostExtinctionRequest(StrictModel):
    """Create a new extinction event for a specific branch in a repository. Extinction events track code reference removals or deprecations."""
    path: PostExtinctionRequestPath
    body: PostExtinctionRequestBody

# Operation: get_code_references_statistics
class GetStatisticsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Used to scope the statistics query to a specific project.", json_schema_extra={'format': 'string'})
class GetStatisticsRequest(StrictModel):
    """Retrieve code reference statistics for flags in a project, showing the number of references to flag keys across repositories in the default branch. Optionally filter results to a single flag using the flagKey query parameter."""
    path: GetStatisticsRequestPath

# Operation: generate_warehouse_destination_key_pair
class PostGenerateProjectEnvWarehouseDestinationKeyPairRequestPath(StrictModel):
    proj_key: str = Field(default=..., validation_alias="projKey", serialization_alias="projKey", description="The unique identifier for the project containing the destination configuration.", json_schema_extra={'format': 'string'})
    env_key: str = Field(default=..., validation_alias="envKey", serialization_alias="envKey", description="The unique identifier for the environment within the project where the warehouse destination is configured.", json_schema_extra={'format': 'string'})
class PostGenerateProjectEnvWarehouseDestinationKeyPairRequest(StrictModel):
    """Generate a public-private key pair for authenticating Data Export operations to a Snowflake warehouse destination. This enables secure credential-based access without storing passwords."""
    path: PostGenerateProjectEnvWarehouseDestinationKeyPairRequestPath

# Operation: create_data_export_destination
class PostDestinationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that uniquely identifies the LaunchDarkly project where the destination will be created.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that uniquely identifies the environment within the project where the destination will be created.", json_schema_extra={'format': 'string'})
class PostDestinationRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the Data Export destination. This name appears in the LaunchDarkly UI for easy identification.")
    kind: Literal["google-pubsub", "kinesis", "mparticle", "segment", "azure-event-hubs", "snowflake-v2", "databricks", "bigquery", "redshift"] | None = Field(default=None, description="The type of Data Export destination. Choose from: google-pubsub, kinesis, mparticle, segment, azure-event-hubs, snowflake-v2, databricks, bigquery, or redshift. Each type requires specific configuration fields.")
    config: Any | None = Field(default=None, description="An object containing the configuration parameters required for your chosen destination type. Required fields vary: Azure Event Hubs needs namespace, name, policyName, and policyKey; Google Pub/Sub needs project and topic; Kinesis needs region, roleArn, and streamName; mParticle needs apiKey, secret, userIdentity, and anonymousUserIdentity; Segment needs writeKey; Snowflake needs publicKey and snowflakeHostAddress.")
    on: bool | None = Field(default=None, description="Whether the Data Export destination is active and exporting events. When true, events are streamed to the destination; when false, the destination is paused. Displayed as the integration status in the LaunchDarkly UI.")
class PostDestinationRequest(StrictModel):
    """Create a new Data Export destination to stream LaunchDarkly events to external platforms. Configuration requirements vary by destination type (e.g., Azure Event Hubs, Google Pub/Sub, Kinesis, mParticle, Segment, Snowflake, Databricks, BigQuery, or Redshift)."""
    path: PostDestinationRequestPath
    body: PostDestinationRequestBody | None = None

# Operation: get_destination
class GetDestinationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the destination.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment within the project contains the destination.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Data Export destination to retrieve.", json_schema_extra={'format': 'string'})
class GetDestinationRequest(StrictModel):
    """Retrieve a single Data Export destination by its ID within a specific project and environment."""
    path: GetDestinationRequestPath

# Operation: update_destination
class PatchDestinationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the destination.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the destination is configured.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Data Export destination to update.", json_schema_extra={'format': 'string'})
class PatchDestinationRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of patch operations following RFC 6902 (JSON Patch) or RFC 7386 (JSON Merge Patch) format. Each operation specifies an action (op), target path (path), and new value (value) for the destination configuration.", examples=[[{'op': 'replace', 'path': '/config/topic', 'value': 'ld-pubsub-test-192302'}]])
class PatchDestinationRequest(StrictModel):
    """Update a Data Export destination using JSON patch or JSON merge patch operations. Specify the changes you want to apply to the destination configuration."""
    path: PatchDestinationRequestPath
    body: PatchDestinationRequestBody

# Operation: delete_destination
class DeleteDestinationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the destination to delete.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the destination exists.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Data Export destination to delete.", json_schema_extra={'format': 'string'})
class DeleteDestinationRequest(StrictModel):
    """Permanently delete a Data Export destination from a specific project and environment. This action cannot be undone."""
    path: DeleteDestinationRequestPath

# Operation: get_feature_flag_status_across_environments
class GetFeatureFlagStatusAcrossEnvironmentsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag. This is a required string key that identifies which project's flags to query.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the specific feature flag whose status you want to retrieve. This is a required string key that identifies the flag within the project.", json_schema_extra={'format': 'string'})
class GetFeatureFlagStatusAcrossEnvironmentsRequestQuery(StrictModel):
    env: str | None = Field(default=None, description="Optional filter to retrieve flag status for a specific environment only. If omitted, the response includes status across all environments in the project.", json_schema_extra={'format': 'string'})
class GetFeatureFlagStatusAcrossEnvironmentsRequest(StrictModel):
    """Retrieve the current status and configuration of a feature flag across all environments or a specific environment. Use this to check whether a flag is enabled, its targeting rules, and rollout percentages in your deployment pipeline."""
    path: GetFeatureFlagStatusAcrossEnvironmentsRequestPath
    query: GetFeatureFlagStatusAcrossEnvironmentsRequestQuery | None = None

# Operation: list_feature_flag_statuses
class GetFeatureFlagStatusesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flags.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project.", json_schema_extra={'format': 'string'})
class GetFeatureFlagStatusesRequest(StrictModel):
    """Retrieve the status of all feature flags in a specific project and environment, including their current state (new, active, inactive, or launched) and last request timestamp."""
    path: GetFeatureFlagStatusesRequestPath

# Operation: get_feature_flag_status
class GetFeatureFlagStatusRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which to check the feature flag status.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose status you want to retrieve.", json_schema_extra={'format': 'string'})
class GetFeatureFlagStatusRequest(StrictModel):
    """Retrieve the current status of a specific feature flag within a given project and environment. This includes whether the flag is enabled or disabled and any associated targeting rules."""
    path: GetFeatureFlagStatusRequestPath

# Operation: list_feature_flags
class GetFeatureFlagsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flags.", json_schema_extra={'format': 'string'})
class GetFeatureFlagsRequestQuery(StrictModel):
    env: str | None = Field(default=None, description="Filter flag configurations to a specific environment (e.g., 'production', 'staging'). Required when using environment-specific filters like `evaluated` or `targetingModifiedDate` sorting.", json_schema_extra={'format': 'string'})
    summary: bool | None = Field(default=None, description="Set to `0` to include detailed flag configuration including prerequisites, targets, and rules for each environment. By default, these details are excluded for performance.")
class GetFeatureFlagsRequest(StrictModel):
    """Retrieve all feature flags in a project with optional filtering by environment, tags, and other criteria. Supports pagination, sorting, and field expansion to optimize response payload and performance."""
    path: GetFeatureFlagsRequestPath
    query: GetFeatureFlagsRequestQuery | None = None

# Operation: create_feature_flag
class PostFeatureFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that uniquely identifies the project where the feature flag will be created.", json_schema_extra={'format': 'string'})
class PostFeatureFlagRequestQuery(StrictModel):
    clone: str | None = Field(default=None, description="Optional key of an existing feature flag to clone. Cloning copies the full targeting configuration across all environments, including on/off state, to the new flag.", json_schema_extra={'format': 'string'})
class PostFeatureFlagRequestBodyClientSideAvailability(StrictModel):
    using_environment_id: bool = Field(default=..., validation_alias="usingEnvironmentId", serialization_alias="usingEnvironmentId", description="Enable or disable availability for client-side SDKs. Defaults to false.")
    using_mobile_key: bool = Field(default=..., validation_alias="usingMobileKey", serialization_alias="usingMobileKey", description="Enable or disable availability for mobile SDKs. Defaults to true.")
class PostFeatureFlagRequestBodyDefaults(StrictModel):
    on_variation: int = Field(default=..., validation_alias="onVariation", serialization_alias="onVariation", description="The index of the variation to serve when targeting is enabled. Must correspond to a valid variation index.")
    off_variation: int = Field(default=..., validation_alias="offVariation", serialization_alias="offVariation", description="The index of the variation to serve when targeting is disabled. Must correspond to a valid variation index.")
class PostFeatureFlagRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the feature flag to display in the UI.")
    key: str = Field(default=..., description="A unique identifier for the flag used in your application code. Must be distinct within the project.")
    variations: list[Variation] | None = Field(default=None, description="Array of possible flag variations with unique values. If omitted, defaults to two boolean variations: true and false. Order matters as variations are referenced by index.")
    temporary: bool | None = Field(default=None, description="Mark the flag as temporary (intended for short-term use). Defaults to true.")
    tags: list[str] | None = Field(default=None, description="Array of tags to organize and categorize the feature flag. Defaults to an empty array.")
    custom_properties: dict[str, CustomProperty] | None = Field(default=None, validation_alias="customProperties", serialization_alias="customProperties", description="Custom metadata as key-value pairs where each key maps to a name and array of values. Typically used for integration-related data.")
    purpose: Literal["migration", "holdout"] | None = Field(default=None, description="The intended purpose of the flag. Use 'migration' for migration flags (which auto-generate variations based on stage count) or 'holdout' for holdout flags.")
    initial_prerequisites: list[FlagPrerequisitePost] | None = Field(default=None, validation_alias="initialPrerequisites", serialization_alias="initialPrerequisites", description="Array of prerequisite flags that must be satisfied before this flag is evaluated in all environments.")
    is_flag_on: bool | None = Field(default=None, validation_alias="isFlagOn", serialization_alias="isFlagOn", description="Automatically enable the flag across all environments upon creation. Defaults to false.")
    client_side_availability: PostFeatureFlagRequestBodyClientSideAvailability = Field(default=..., validation_alias="clientSideAvailability", serialization_alias="clientSideAvailability")
    defaults: PostFeatureFlagRequestBodyDefaults
class PostFeatureFlagRequest(StrictModel):
    """Create a feature flag in a project with customizable variations, targeting defaults, and optional migration settings. Supports cloning existing flags and configuring SDK availability."""
    path: PostFeatureFlagRequestPath
    query: PostFeatureFlagRequestQuery | None = None
    body: PostFeatureFlagRequestBody

# Operation: get_feature_flag
class GetFeatureFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag to retrieve.", json_schema_extra={'format': 'string'})
class GetFeatureFlagRequestQuery(StrictModel):
    env: str | None = Field(default=None, description="Optional environment filter to restrict returned configurations to a specific environment (e.g., 'production'). Omit to retrieve all environments.", json_schema_extra={'format': 'string'})
class GetFeatureFlagRequest(StrictModel):
    """Retrieve a single feature flag by its key, with configurations for all environments by default. Use the `env` parameter to filter results to specific environments for faster responses and smaller payloads."""
    path: GetFeatureFlagRequestPath
    query: GetFeatureFlagRequestQuery | None = None

# Operation: update_feature_flag
class PatchFeatureFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key used to identify the flag in your application code.", json_schema_extra={'format': 'string'})
class PatchFeatureFlagRequestQuery(StrictModel):
    ignore_conflicts: bool | None = Field(default=None, validation_alias="ignoreConflicts", serialization_alias="ignoreConflicts", description="If true, applies the patch even if it conflicts with pending scheduled changes or approval requests. Use to override validation checks.")
    dry_run: bool | None = Field(default=None, validation_alias="dryRun", serialization_alias="dryRun", description="If true, validates the patch and returns a preview of the flag after changes without persisting them. Useful for testing changes before applying.")
class PatchFeatureFlagRequestBody(StrictModel):
    patch: list[PatchOperation] = Field(default=..., description="Array of patch operations describing the changes to apply. Use semantic patch format (with Content-Type header domain-model=launchdarkly.semanticpatch), JSON patch (RFC 6902), or JSON merge patch (RFC 7386) format. Order of operations is significant.")
class PatchFeatureFlagRequest(StrictModel):
    """Perform a partial update to a feature flag using semantic patch, JSON patch, or JSON merge patch. Supports targeting rules, variations, prerequisites, flag settings, and lifecycle management across environments."""
    path: PatchFeatureFlagRequestPath
    query: PatchFeatureFlagRequestQuery | None = None
    body: PatchFeatureFlagRequestBody

# Operation: delete_feature_flag
class DeleteFeatureFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique key that identifies the feature flag in your codebase. This is the identifier you reference when evaluating the flag in your application.", json_schema_extra={'format': 'string'})
class DeleteFeatureFlagRequest(StrictModel):
    """Permanently delete a feature flag across all environments. This operation cannot be undone, so only use it for flags your application no longer references in code."""
    path: DeleteFeatureFlagRequestPath

# Operation: copy_feature_flag_between_environments
class CopyFeatureFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key that uniquely identifies the flag within the project.", json_schema_extra={'format': 'string'})
class CopyFeatureFlagRequestBodySource(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The environment key of the source environment to copy flag settings from.")
class CopyFeatureFlagRequestBodyTarget(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The environment key of the target environment to copy flag settings to.")
    current_version: int | None = Field(default=None, validation_alias="currentVersion", serialization_alias="currentVersion", description="Optional flag version number. When provided, the copy operation only succeeds if the target environment's current flag version matches this value, enabling optimistic locking to prevent concurrent modification conflicts.")
class CopyFeatureFlagRequestBody(StrictModel):
    included_actions: list[Literal["updateOn", "updateRules", "updateFallthrough", "updateOffVariation", "updatePrerequisites", "updateTargets", "updateFlagConfigMigrationSettings"]] | None = Field(default=None, validation_alias="includedActions", serialization_alias="includedActions", description="Optional list of specific flag changes to copy (e.g., 'updateOn'). Use this to copy only selected changes rather than the entire flag configuration. Cannot be combined with excludedActions; if neither is provided, all flag changes are copied.")
    source: CopyFeatureFlagRequestBodySource
    target: CopyFeatureFlagRequestBodyTarget
class CopyFeatureFlagRequest(StrictModel):
    """Copy feature flag configuration from a source environment to a target environment. This Enterprise-only operation supports selective copying of flag changes and optimistic locking via version matching."""
    path: CopyFeatureFlagRequestPath
    body: CopyFeatureFlagRequestBody

# Operation: list_expiring_context_targets
class GetExpiringContextTargetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the feature flag is configured.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose expiring context targets should be retrieved.", json_schema_extra={'format': 'string'})
class GetExpiringContextTargetsRequest(StrictModel):
    """Retrieve a list of context targets scheduled for removal from a feature flag. This helps identify and manage temporary targeting rules that are approaching their expiration date."""
    path: GetExpiringContextTargetsRequestPath

# Operation: update_expiring_context_targets
class PatchExpiringTargetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag. A string identifier for the LaunchDarkly project.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the feature flag targeting applies. A string identifier for the specific environment.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key to update expiring targets for. A string identifier for the feature flag.", json_schema_extra={'format': 'string'})
class PatchExpiringTargetsRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instructions to execute. Each instruction must specify a `kind` (addExpiringTarget, updateExpiringTarget, or removeExpiringTarget), the target context via `contextKey` and `contextKind`, the `variationId` to target, and for add/update operations, a `value` representing the Unix millisecond timestamp for removal. Instructions are processed in order.")
class PatchExpiringTargetsRequest(StrictModel):
    """Schedule, update, or remove the date when a context will be automatically removed from individual targeting on a feature flag. Use semantic patch instructions to add expiration dates, modify existing ones, or cancel scheduled removals."""
    path: PatchExpiringTargetsRequestPath
    body: PatchExpiringTargetsRequestBody

# Operation: list_expiring_user_targets_for_feature_flag
class GetExpiringUserTargetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that specifies which environment's feature flag targeting data to retrieve.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key that identifies which flag's expiring user targets to list.", json_schema_extra={'format': 'string'})
class GetExpiringUserTargetsRequest(StrictModel):
    """Retrieve a list of user targets scheduled for removal from a feature flag in a specific environment. Note: This endpoint is deprecated; use list_expiring_context_targets_for_feature_flag instead after upgrading to context-based SDKs."""
    path: GetExpiringUserTargetsRequestPath

# Operation: schedule_user_target_removal_on_flag
class PatchExpiringUserTargetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the feature flag is configured.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key to update expiring user targets for.", json_schema_extra={'format': 'string'})
class PatchExpiringUserTargetsRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="Array of semantic patch instructions to add, update, or remove user target removal dates. Each instruction must specify a kind (addExpireUserTargetDate, updateExpireUserTargetDate, or removeExpireUserTargetDate), the userKey to target, and the variationId. For add and update operations, include value as a Unix timestamp in milliseconds. The update operation supports an optional version parameter to ensure consistency.")
class PatchExpiringUserTargetsRequest(StrictModel):
    """Schedule, update, or remove a removal date for a user from a feature flag's individual targeting. Use semantic patch instructions to manage when LaunchDarkly will stop serving a specific variation to targeted users."""
    path: PatchExpiringUserTargetsRequestPath
    body: PatchExpiringUserTargetsRequestBody

# Operation: list_flag_triggers
class GetTriggerWorkflowsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the flag triggers are configured.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose triggers you want to retrieve.", json_schema_extra={'format': 'string'})
class GetTriggerWorkflowsRequest(StrictModel):
    """Retrieve all triggers configured for a feature flag in a specific environment. Triggers define automated workflows that respond to flag changes."""
    path: GetTriggerWorkflowsRequestPath

# Operation: create_flag_trigger
class CreateTriggerWorkflowRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier of the environment where the trigger will be active.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier of the feature flag that will be triggered.", json_schema_extra={'format': 'string'})
class CreateTriggerWorkflowRequestBody(StrictModel):
    instructions: list[Instruction] | None = Field(default=None, description="An array containing a single object that specifies the action to perform when the trigger is activated. The object must have a 'kind' field set to either 'turnFlagOn' or 'turnFlagOff' to control the flag's state.")
    integration_key: str = Field(default=..., validation_alias="integrationKey", serialization_alias="integrationKey", description="The unique identifier of the integration that will activate this trigger. Use 'generic-trigger' for integrations that are not explicitly supported by the system.")
class CreateTriggerWorkflowRequest(StrictModel):
    """Create a new trigger for a feature flag that automatically performs an action (such as turning the flag on or off) when activated by an integrated system."""
    path: CreateTriggerWorkflowRequestPath
    body: CreateTriggerWorkflowRequestBody

# Operation: get_trigger_workflow_by_id
class GetTriggerWorkflowByIdRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag and trigger.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag that contains the trigger.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which the trigger operates.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the specific flag trigger to retrieve.", json_schema_extra={'format': 'string'})
class GetTriggerWorkflowByIdRequest(StrictModel):
    """Retrieve a specific flag trigger by its ID within a feature flag, project, and environment context. Use this to fetch detailed configuration and status of an individual trigger workflow."""
    path: GetTriggerWorkflowByIdRequestPath

# Operation: update_flag_trigger
class PatchTriggerWorkflowRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the trigger is configured.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key associated with this trigger.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flag trigger to update.", json_schema_extra={'format': 'string'})
class PatchTriggerWorkflowRequestBody(StrictModel):
    instructions: list[Instruction] | None = Field(default=None, description="An array of semantic patch instructions to apply. Each instruction is an object with a `kind` field specifying the operation: `replaceTriggerActionInstructions` (with `value` array of actions like `turnFlagOn` or `turnFlagOff`), `cycleTriggerUrl`, `disableTrigger`, or `enableTrigger`. Instructions are applied in order.")
class PatchTriggerWorkflowRequest(StrictModel):
    """Update a flag trigger's configuration using semantic patch instructions. Supports actions like enabling/disabling the trigger, replacing trigger actions, or cycling the trigger URL."""
    path: PatchTriggerWorkflowRequestPath
    body: PatchTriggerWorkflowRequestBody | None = None

# Operation: delete_trigger_for_flag
class DeleteTriggerWorkflowRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the flag trigger is configured.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag associated with this trigger.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flag trigger to delete.", json_schema_extra={'format': 'string'})
class DeleteTriggerWorkflowRequest(StrictModel):
    """Delete a specific flag trigger by its ID. This removes the trigger configuration that automates flag state changes based on defined conditions."""
    path: DeleteTriggerWorkflowRequestPath

# Operation: get_release_by_flag_key
class GetReleaseByFlagKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the flag.", json_schema_extra={'format': 'string'})
    flag_key: str = Field(default=..., validation_alias="flagKey", serialization_alias="flagKey", description="The unique identifier for the feature flag within the project.", json_schema_extra={'format': 'string'})
class GetReleaseByFlagKeyRequest(StrictModel):
    """Retrieve the currently active release associated with a specific feature flag. Returns release metadata if an active release exists for the flag."""
    path: GetReleaseByFlagKeyRequestPath

# Operation: update_release_phase_status_by_flag_key
class PatchReleaseByFlagKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the flag. A string identifier for the project.", json_schema_extra={'format': 'string'})
    flag_key: str = Field(default=..., validation_alias="flagKey", serialization_alias="flagKey", description="The flag key identifying which flag's release to update. A string identifier for the flag.", json_schema_extra={'format': 'string'})
class PatchReleaseByFlagKeyRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="A JSON patch array specifying the phase status changes. Each patch object must contain an 'op' field set to 'replace', a 'path' field pointing to a phase's complete status (e.g., '/phases/0/complete'), and a 'value' field set to true or false. Array order matters—use the index to target specific phases.", examples=[[{'op': 'replace', 'path': '/phases/0/complete', 'value': True}]])
class PatchReleaseByFlagKeyRequest(StrictModel):
    """Update the completion status of a release phase for a flag in a legacy release pipeline. Use JSON patch format to mark specific phases as complete or incomplete by their array index."""
    path: PatchReleaseByFlagKeyRequestPath
    body: PatchReleaseByFlagKeyRequestBody

# Operation: delete_release_for_flag
class DeleteReleaseByFlagKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the flag. Used to scope the operation to the correct project context.", json_schema_extra={'format': 'string'})
    flag_key: str = Field(default=..., validation_alias="flagKey", serialization_alias="flagKey", description="The unique identifier for the feature flag from which the release will be deleted. Must correspond to an existing flag within the specified project.", json_schema_extra={'format': 'string'})
class DeleteReleaseByFlagKeyRequest(StrictModel):
    """Removes a release associated with a feature flag. This operation permanently deletes the release record from the specified flag within a project."""
    path: DeleteReleaseByFlagKeyRequestPath

# Operation: list_audit_subscriptions_by_integration
class GetSubscriptionsRequestPath(StrictModel):
    integration_key: str = Field(default=..., validation_alias="integrationKey", serialization_alias="integrationKey", description="The unique identifier for the integration whose audit log subscriptions you want to retrieve.", json_schema_extra={'format': 'string'})
class GetSubscriptionsRequest(StrictModel):
    """Retrieve all audit log subscriptions associated with a specific integration. Use this to view which audit events are being monitored for a given integration."""
    path: GetSubscriptionsRequestPath

# Operation: get_audit_log_subscription
class GetSubscriptionByIdRequestPath(StrictModel):
    integration_key: str = Field(default=..., validation_alias="integrationKey", serialization_alias="integrationKey", description="The unique identifier for the integration. This key determines which integration context the subscription belongs to.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the audit log subscription to retrieve.", json_schema_extra={'format': 'string'})
class GetSubscriptionByIdRequest(StrictModel):
    """Retrieve a specific audit log subscription by its ID within a given integration. Use this to fetch details about an existing subscription configuration."""
    path: GetSubscriptionByIdRequestPath

# Operation: update_audit_log_subscription
class UpdateSubscriptionRequestPath(StrictModel):
    integration_key: str = Field(default=..., validation_alias="integrationKey", serialization_alias="integrationKey", description="The unique identifier for the integration containing the audit log subscription.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the audit log subscription to update.", json_schema_extra={'format': 'string'})
class UpdateSubscriptionRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type), 'path' (the JSON pointer to the target field), and 'value' (the new value for replace/add operations).", examples=[[{'op': 'replace', 'path': '/on', 'value': False}]])
class UpdateSubscriptionRequest(StrictModel):
    """Update an audit log subscription configuration using JSON Patch operations. Specify the changes you want to apply to the subscription settings."""
    path: UpdateSubscriptionRequestPath
    body: UpdateSubscriptionRequestBody

# Operation: delete_audit_log_subscription
class DeleteSubscriptionRequestPath(StrictModel):
    integration_key: str = Field(default=..., validation_alias="integrationKey", serialization_alias="integrationKey", description="The unique identifier for the integration from which the subscription will be deleted.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the audit log subscription to delete.", json_schema_extra={'format': 'string'})
class DeleteSubscriptionRequest(StrictModel):
    """Remove an audit log subscription from an integration. This permanently deletes the subscription and stops audit log collection for the specified integration."""
    path: DeleteSubscriptionRequestPath

# Operation: invite_members
class PostMembersRequestBody(StrictModel):
    body: list[NewMemberForm] = Field(default=..., description="Array of member objects to invite. Each object must include an email field and either a role field (base role name) or customRoles field (custom or preset role key). Some roles may require roleAttributes for scope specification. Maximum 50 members per request. The request fails entirely if any member data is invalid or if email addresses conflict with existing members in this account or others, or if duplicates exist within the request itself.")
class PostMembersRequest(StrictModel):
    """Invite one or more new members to join an account via email. Each member receives an invitation and must have a valid email address with either a base role (reader, writer, admin, owner/admin, no_access) or a custom role key. Up to 50 members can be invited per request; the entire request fails if any member's data is invalid or conflicts with existing members."""
    body: PostMembersRequestBody

# Operation: update_members_bulk
class PatchMembersRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="Array of semantic patch instructions defining the bulk update operations. Each instruction object must include a `kind` field specifying the operation type (replaceMembersRoles, replaceAllMembersRoles, replaceMembersCustomRoles, replaceAllMembersCustomRoles, or replaceMembersRoleAttributes) along with required parameters for that operation type. Instructions are processed sequentially.")
class PatchMembersRequest(StrictModel):
    """Perform bulk updates to member roles and custom roles using semantic patch instructions. Supports targeted updates to specific members or filtered bulk updates across all members (Enterprise feature)."""
    body: PatchMembersRequestBody

# Operation: get_member
class GetMemberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The member ID as a string. Use the reserved value `me` to retrieve the caller's own member information instead of specifying a numeric ID.", json_schema_extra={'format': 'string'})
class GetMemberRequest(StrictModel):
    """Retrieve a single account member by ID. Use the reserved value `me` to get the caller's own member information. Optionally expand the response to include custom role details and role attributes."""
    path: GetMemberRequestPath

# Operation: update_member
class PatchMemberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the member to update.", json_schema_extra={'format': 'string'})
class PatchMemberRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="A JSON Patch array describing the changes to apply. Each patch object must contain an operation (add, remove, replace, etc.), a path (e.g., '/role' or '/customRoles/0'), and a value. Use array index notation to modify role arrays: use '/0' to prepend, '/-' to append, or a specific index to modify an existing position.", examples=[[{'op': 'add', 'path': '/role', 'value': 'writer'}]])
class PatchMemberRequest(StrictModel):
    """Update an account member's role or custom roles using JSON Patch format. Changes are applied to the member object, though IdP-managed accounts may be overridden by the Identity Provider shortly after."""
    path: PatchMemberRequestPath
    body: PatchMemberRequestBody

# Operation: delete_member
class DeleteMemberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the member to delete", json_schema_extra={'format': 'string'})
class DeleteMemberRequest(StrictModel):
    """Remove an account member by their ID. This operation will fail if SCIM provisioning is enabled for the account."""
    path: DeleteMemberRequestPath

# Operation: add_member_to_teams
class PostMemberTeamsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the member to add to teams.", json_schema_extra={'format': 'string'})
class PostMemberTeamsRequestBody(StrictModel):
    team_keys: list[str] = Field(default=..., validation_alias="teamKeys", serialization_alias="teamKeys", description="An array of team keys identifying which teams the member should be added to. Provide one or more team keys as strings in the array.")
class PostMemberTeamsRequest(StrictModel):
    """Add a single member to one or more teams. The member will be granted access to all specified teams."""
    path: PostMemberTeamsRequestPath
    body: PostMemberTeamsRequestBody

# Operation: list_metrics
class GetMetricsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Used to scope the metrics query to a specific project.", json_schema_extra={'format': 'string'})
class GetMetricsRequest(StrictModel):
    """Retrieve all metrics for a specified project with support for filtering by various criteria (data sources, event types, tags, usage context) and optional expansion of related experiment counts."""
    path: GetMetricsRequestPath

# Operation: create_metric
class PostMetricRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project where the metric will be created.", json_schema_extra={'format': 'string'})
class PostMetricRequestBodyDataSource(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The unique identifier for the data source that will provide events for this metric.")
    name: str | None = Field(default=None, validation_alias="_name", serialization_alias="_name", description="The human-readable name of the data source providing events for this metric.")
    environment_key: str | None = Field(default=None, validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key associated with this metric (e.g., 'production', 'staging').")
    integration_key: str | None = Field(default=None, validation_alias="_integrationKey", serialization_alias="_integrationKey", description="The integration key for connecting this metric to an external data source or service.")
class PostMetricRequestBodyEventDefault(StrictModel):
    disabled: bool | None = Field(default=None, validation_alias="disabled", serialization_alias="disabled", description="Set to true to disable automatic default values for missing unit events during result calculation. Defaults to false.")
    value: float | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The default numeric value applied to missing unit events when disabled is false. Currently only 0 is supported.")
class PostMetricRequestBodyFilters(StrictModel):
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The filter type: 'contextAttribute' to filter on user context attributes, 'eventProperty' to filter on event properties, or 'group' to filter on group membership.")
    attribute: str | None = Field(default=None, validation_alias="attribute", serialization_alias="attribute", description="The name of the context attribute or event property to filter on (e.g., 'country'). Not applicable for group-type filters.")
    op: str = Field(default=..., validation_alias="op", serialization_alias="op", description="The comparison operator to apply (e.g., 'in', 'equals', 'contains'). Determines how values are matched against the filter.")
    values: list[Any] = Field(default=..., validation_alias="values", serialization_alias="values", description="An array of values to match against the filter. For numeric values, do not exceed 14 decimal places (e.g., ['JP'] for country filtering).")
    negate: bool = Field(default=..., validation_alias="negate", serialization_alias="negate", description="Set to true to invert the filter logic (e.g., 'in' becomes 'not in'). Defaults to false.")
class PostMetricRequestBody(StrictModel):
    key: str = Field(default=..., description="A unique identifier for the metric, used as a reference key in your codebase (e.g., 'metric-key-123abc').")
    name: str | None = Field(default=None, description="A human-readable name for the metric to display in the UI (e.g., 'Example metric').")
    kind: Literal["pageview", "click", "custom"] = Field(default=..., description="The type of event this metric tracks: 'pageview' for page views, 'click' for user clicks, or 'custom' for application-defined events.")
    selector: str | None = Field(default=None, description="One or more CSS selectors identifying the elements to track. Required only for click metrics (e.g., '.dropdown-toggle').")
    urls: list[UrlPost] | None = Field(default=None, description="One or more target URLs to track. Required for click and pageview metrics. Specify as an array of URL strings.")
    is_numeric: bool | None = Field(default=None, validation_alias="isNumeric", serialization_alias="isNumeric", description="For custom metrics only: set to true to track numeric value changes against a baseline, or false to track conversions when users take an action.")
    unit: str | None = Field(default=None, description="The unit of measurement for numeric custom metrics (e.g., 'orders', 'revenue'). Only applicable when tracking numeric values.")
    event_key: str | None = Field(default=None, validation_alias="eventKey", serialization_alias="eventKey", description="The event key identifier used in your application code to trigger this metric. Required for custom conversion and numeric metrics (e.g., 'Order placed').")
    success_criteria: Literal["HigherThanBaseline", "LowerThanBaseline"] | None = Field(default=None, validation_alias="successCriteria", serialization_alias="successCriteria", description="Success criteria for numeric custom metrics: 'HigherThanBaseline' if increases are favorable, 'LowerThanBaseline' if decreases are favorable. Optional for conversion metrics.")
    tags: list[str] | None = Field(default=None, description="An array of tags to organize and categorize the metric (e.g., ['example-tag']).")
    randomization_units: list[str] | None = Field(default=None, validation_alias="randomizationUnits", serialization_alias="randomizationUnits", description="An array of randomization units allowed for this metric (e.g., ['user']). Determines how experiment variations are assigned.")
    trace_query: str | None = Field(default=None, validation_alias="traceQuery", serialization_alias="traceQuery", description="A trace query to identify relevant traces for this metric (e.g., 'service.name = \"checkout\"'). Required only for trace metrics.")
    trace_value_location: str | None = Field(default=None, validation_alias="traceValueLocation", serialization_alias="traceValueLocation", description="The location within a trace to extract numeric values from (e.g., 'duration'). Required only for numeric trace metrics.")
    data_source: PostMetricRequestBodyDataSource = Field(default=..., validation_alias="dataSource", serialization_alias="dataSource")
    event_default: PostMetricRequestBodyEventDefault | None = Field(default=None, validation_alias="eventDefault", serialization_alias="eventDefault")
    filters: PostMetricRequestBodyFilters
class PostMetricRequest(StrictModel):
    """Create a new metric in a specified project to track user interactions or custom events. The metric structure varies based on the kind (pageview, click, or custom) and whether it measures conversions or numeric values."""
    path: PostMetricRequestPath
    body: PostMetricRequestBody

# Operation: get_metric
class GetMetricRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the metric.", json_schema_extra={'format': 'string'})
    metric_key: str = Field(default=..., validation_alias="metricKey", serialization_alias="metricKey", description="The unique identifier for the metric to retrieve.", json_schema_extra={'format': 'string'})
class GetMetricRequestQuery(StrictModel):
    version_id: str | None = Field(default=None, validation_alias="versionId", serialization_alias="versionId", description="The specific version ID of the metric to retrieve. If omitted, returns the current version. Use comma-separated values in the expand query parameter to include experiments, experimentCount, metricGroups, or metricGroupCount in the response.", json_schema_extra={'format': 'string'})
class GetMetricRequest(StrictModel):
    """Retrieve detailed information about a specific metric in a LaunchDarkly project. Optionally expand the response to include related experiments and metric groups."""
    path: GetMetricRequestPath
    query: GetMetricRequestQuery | None = None

# Operation: update_metric
class PatchMetricRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the metric.", json_schema_extra={'format': 'string'})
    metric_key: str = Field(default=..., validation_alias="metricKey", serialization_alias="metricKey", description="The unique identifier for the metric to update.", json_schema_extra={'format': 'string'})
class PatchMetricRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type such as 'replace', 'add', or 'remove'), 'path' (the JSON pointer to the target property), and 'value' (the new value, required for 'replace' and 'add' operations).", examples=[[{'op': 'replace', 'path': '/name', 'value': 'my-updated-metric'}]])
class PatchMetricRequest(StrictModel):
    """Update a metric using JSON Patch operations. Specify the changes you want to make to the metric's properties such as name, description, or other attributes."""
    path: PatchMetricRequestPath
    body: PatchMetricRequestBody

# Operation: delete_metric
class DeleteMetricRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the metric to delete.", json_schema_extra={'format': 'string'})
    metric_key: str = Field(default=..., validation_alias="metricKey", serialization_alias="metricKey", description="The unique identifier for the metric to delete.", json_schema_extra={'format': 'string'})
class DeleteMetricRequest(StrictModel):
    """Permanently delete a metric from a project by its key. This operation removes the metric and all associated data."""
    path: DeleteMetricRequestPath

# Operation: get_oauth_client_by_id
class GetOAuthClientByIdRequestPath(StrictModel):
    client_id: str = Field(default=..., validation_alias="clientId", serialization_alias="clientId", description="The unique identifier of the OAuth 2.0 client to retrieve.", json_schema_extra={'format': 'string'})
class GetOAuthClientByIdRequest(StrictModel):
    """Retrieve a registered OAuth 2.0 client by its unique client ID. Use this to fetch detailed configuration and metadata for a specific OAuth client application."""
    path: GetOAuthClientByIdRequestPath

# Operation: update_oauth_client
class PatchOAuthClientRequestPath(StrictModel):
    client_id: str = Field(default=..., validation_alias="clientId", serialization_alias="clientId", description="The unique identifier of the OAuth 2.0 client to update.", json_schema_extra={'format': 'string'})
class PatchOAuthClientRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="A JSON Patch array describing the changes to apply. Each operation must specify an operation type (op), a JSON pointer path, and a value. Supported paths are /name, /description, and /redirectUri.", examples=[[{'op': 'replace', 'path': '/name', 'value': 'Example Client V2'}]])
class PatchOAuthClientRequest(StrictModel):
    """Update an OAuth 2.0 client's configuration using JSON Patch operations. Only the client name, description, and redirect URI can be modified."""
    path: PatchOAuthClientRequestPath
    body: PatchOAuthClientRequestBody

# Operation: delete_oauth_client
class DeleteOAuthClientRequestPath(StrictModel):
    client_id: str = Field(default=..., validation_alias="clientId", serialization_alias="clientId", description="The unique identifier of the OAuth 2.0 client to delete.", json_schema_extra={'format': 'string'})
class DeleteOAuthClientRequest(StrictModel):
    """Permanently delete an OAuth 2.0 client application by its unique identifier. This action cannot be undone and will invalidate all tokens issued to this client."""
    path: DeleteOAuthClientRequestPath

# Operation: create_project
class PostProjectRequestBodyDefaultClientSideAvailability(StrictModel):
    using_environment_id: bool = Field(default=..., validation_alias="usingEnvironmentId", serialization_alias="usingEnvironmentId", description="Enable or disable availability of this project for client-side SDKs.")
    using_mobile_key: bool = Field(default=..., validation_alias="usingMobileKey", serialization_alias="usingMobileKey", description="Enable or disable availability of this project for mobile SDKs.")
class PostProjectRequestBodyNamingConvention(StrictModel):
    case: Literal["camelCase", "upperCamelCase", "snakeCase", "kebabCase", "constantCase"] | None = Field(default=None, validation_alias="case", serialization_alias="case", description="Optional casing convention to enforce for new flag keys in this project. Choose from: camelCase, upperCamelCase, snakeCase, kebabCase, or constantCase.")
    prefix: str | None = Field(default=None, validation_alias="prefix", serialization_alias="prefix", description="Optional prefix to enforce for all new flag keys in this project (e.g., 'enable-').")
class PostProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-friendly display name for the project (e.g., 'My Project').")
    key: str = Field(default=..., description="A unique identifier for the project used in code references (e.g., 'project-key-123abc'). Must be unique within your account.")
    tags: list[str] | None = Field(default=None, description="Optional list of tags to organize and categorize the project (e.g., ['ops']).")
    environments: list[EnvironmentPost] | None = Field(default=None, description="Optional list of environments to create for this project. If omitted, default environments will be created automatically.")
    default_client_side_availability: PostProjectRequestBodyDefaultClientSideAvailability = Field(default=..., validation_alias="defaultClientSideAvailability", serialization_alias="defaultClientSideAvailability")
    naming_convention: PostProjectRequestBodyNamingConvention | None = Field(default=None, validation_alias="namingConvention", serialization_alias="namingConvention")
class PostProjectRequest(StrictModel):
    """Create a new project with a unique key and name. Configure SDK availability, naming conventions, and initial environments for the project."""
    body: PostProjectRequestBody

# Operation: get_project
class GetProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Used to specify which project to retrieve.", json_schema_extra={'format': 'string'})
class GetProjectRequest(StrictModel):
    """Retrieve a single project by its key. Optionally expand the response to include related resources such as environments."""
    path: GetProjectRequestPath

# Operation: update_project
class PatchProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project to update.", json_schema_extra={'format': 'string'})
class PatchProjectRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations describing the changes to apply. Each operation must specify an operation type (add, remove, replace, etc.), a JSON Pointer path to the target field, and a value where applicable. For array fields, use numeric indices or `/-` to append to the end.", examples=[[{'op': 'add', 'path': '/tags/0', 'value': 'another-tag'}]])
class PatchProjectRequest(StrictModel):
    """Update a project using JSON Patch operations. Supports modifying project fields including adding, removing, or replacing values. Array fields like tags are automatically deduplicated and sorted alphabetically."""
    path: PatchProjectRequestPath
    body: PatchProjectRequestBody

# Operation: delete_project
class DeleteProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project to delete. This is a string value that uniquely identifies the project within your account.", json_schema_extra={'format': 'string'})
class DeleteProjectRequest(StrictModel):
    """Permanently delete a project and all its associated environments and feature flags. This operation cannot be undone and will fail if the project is the last one in the account."""
    path: DeleteProjectRequestPath

# Operation: list_context_kinds_by_project
class GetContextKindsByProjectKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. This is a string-based key that distinguishes the project within your LaunchDarkly workspace.", json_schema_extra={'format': 'string'})
class GetContextKindsByProjectKeyRequest(StrictModel):
    """Retrieve all context kinds configured for a specific project. Context kinds define the types of contextual information that can be associated with feature flags and experiments in the project."""
    path: GetContextKindsByProjectKeyRequestPath

# Operation: update_context_kind
class PutContextKindRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the context kind.", json_schema_extra={'format': 'string'})
    key: str = Field(default=..., description="The unique identifier for the context kind to create or update.", json_schema_extra={'format': 'string'})
class PutContextKindRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the context kind (e.g., 'organization'). This is the human-readable label used to identify the context kind.")
    archived: bool | None = Field(default=None, description="Whether the context kind is archived. Archived context kinds cannot be used for targeting. Defaults to false if not specified.")
class PutContextKindRequest(StrictModel):
    """Create or update a context kind within a project. If the context kind exists, only the provided fields will be updated; otherwise, a new context kind will be created."""
    path: PutContextKindRequestPath
    body: PutContextKindRequestBody

# Operation: list_environments_by_project
class GetEnvironmentsByProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Used to scope the environment list to a specific project.", json_schema_extra={'format': 'string'})
class GetEnvironmentsByProjectRequest(StrictModel):
    """Retrieve a paginated list of environments for a specified project, with support for filtering by name/key and tags, and sorting by creation date, criticality, or name."""
    path: GetEnvironmentsByProjectRequestPath

# Operation: create_environment
class PostEnvironmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project where the environment will be created.", json_schema_extra={'format': 'string'})
class PostEnvironmentRequestBodySource(StrictModel):
    key: str | None = Field(default=None, validation_alias="key", serialization_alias="key", description="Optional: The key of an existing environment to clone configuration from, including flags and segments.")
class PostEnvironmentRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the environment (e.g., 'Production', 'Staging', 'Development').")
    key: str = Field(default=..., description="A project-unique identifier for the environment, used in API calls and SDKs (e.g., 'prod', 'staging', 'dev').")
    color: str = Field(default=..., description="A hex color code (without '#') to visually distinguish this environment in the LaunchDarkly UI (e.g., 'F5A623' for orange).")
    default_ttl: int | None = Field(default=None, validation_alias="defaultTtl", serialization_alias="defaultTtl", description="Optional: The default cache duration in minutes for the PHP SDK to store feature flag rules locally. Reduces API calls but may delay flag updates.")
    secure_mode: bool | None = Field(default=None, validation_alias="secureMode", serialization_alias="secureMode", description="Optional: When enabled, prevents client-side SDK users from viewing flag variations assigned to other users, enhancing security for sensitive environments.")
    default_track_events: bool | None = Field(default=None, validation_alias="defaultTrackEvents", serialization_alias="defaultTrackEvents", description="Optional: When enabled, automatically tracks detailed event data for newly created feature flags in this environment.")
    confirm_changes: bool | None = Field(default=None, validation_alias="confirmChanges", serialization_alias="confirmChanges", description="Optional: When enabled, requires explicit confirmation in the UI before applying any flag or segment changes in this environment.")
    require_comments: bool | None = Field(default=None, validation_alias="requireComments", serialization_alias="requireComments", description="Optional: When enabled, requires users to provide comments explaining the reason for any flag or segment changes made via the UI.")
    tags: list[str] | None = Field(default=None, description="Optional: An array of tags to categorize and organize the environment (e.g., ['ops', 'production'], ['team:backend']).")
    critical: bool | None = Field(default=None, description="Optional: Marks this environment as critical, which may trigger additional safeguards or notifications for changes.")
    source: PostEnvironmentRequestBodySource | None = None
class PostEnvironmentRequest(StrictModel):
    """Create a new environment within a project. Specify the environment name, unique key, UI color, and optional settings like caching TTL, secure mode, and change approval requirements. Note: approval settings cannot be configured during creation and must be updated separately."""
    path: PostEnvironmentRequestPath
    body: PostEnvironmentRequestBody

# Operation: get_environment
class GetEnvironmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the environment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment to retrieve.", json_schema_extra={'format': 'string'})
class GetEnvironmentRequest(StrictModel):
    """Retrieve a specific environment within a project. Returns environment configuration including approval settings when the approvals feature is enabled."""
    path: GetEnvironmentRequestPath

# Operation: update_environment
class PatchEnvironmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the environment to update.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment within the project to update.", json_schema_extra={'format': 'string'})
class PatchEnvironmentRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="A JSON Patch array describing the changes to apply. Each operation specifies an action (op), target path, and value. For array fields, append the index to the path (e.g., `/fieldName/0` to prepend). Only `canReviewOwnRequest`, `canApplyDeclinedChanges`, `minNumApprovals`, `required`, and `requiredApprovalTags` approval settings are editable; do not set both `required` and `requiredApprovalTags` simultaneously.", examples=[[{'op': 'replace', 'path': '/requireComments', 'value': True}]])
class PatchEnvironmentRequest(StrictModel):
    """Update an environment's configuration using JSON Patch operations. Supports modifying fields including approval settings, comments requirements, and array-based properties."""
    path: PatchEnvironmentRequestPath
    body: PatchEnvironmentRequestBody

# Operation: delete_environment
class DeleteEnvironmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the environment to delete.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment to delete.", json_schema_extra={'format': 'string'})
class DeleteEnvironmentRequest(StrictModel):
    """Permanently delete an environment from a project by its key. This action cannot be undone."""
    path: DeleteEnvironmentRequestPath

# Operation: reset_environment_sdk_key
class ResetEnvironmentSdkKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the environment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment whose SDK key should be reset.", json_schema_extra={'format': 'string'})
class ResetEnvironmentSdkKeyRequestQuery(StrictModel):
    expiry: int | None = Field(default=None, description="Optional grace period for the old SDK key expiration, specified in UNIX milliseconds. If not provided, the old key expires immediately. This allows clients using the old key to transition to the new key without service interruption.", json_schema_extra={'format': 'int64'})
class ResetEnvironmentSdkKeyRequest(StrictModel):
    """Reset an environment's SDK key and optionally specify when the old key should expire. During the expiry grace period, both the old and new SDK keys remain valid, allowing for seamless client migration."""
    path: ResetEnvironmentSdkKeyRequestPath
    query: ResetEnvironmentSdkKeyRequestQuery | None = None

# Operation: list_context_attribute_names
class GetContextAttributeNamesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the environment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project.", json_schema_extra={'format': 'string'})
class GetContextAttributeNamesRequest(StrictModel):
    """Retrieve all available context attribute names for a specific environment within a project. This returns the list of attributes that can be used to define user context in feature flag evaluations."""
    path: GetContextAttributeNamesRequestPath

# Operation: get_context_attribute_values
class GetContextAttributeValuesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the context attribute.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the context attribute values are stored.", json_schema_extra={'format': 'string'})
    attribute_name: str = Field(default=..., validation_alias="attributeName", serialization_alias="attributeName", description="The name of the context attribute for which to retrieve values.", json_schema_extra={'format': 'string'})
class GetContextAttributeValuesRequest(StrictModel):
    """Retrieve all values associated with a specific context attribute within a project environment. Use this to discover what values have been recorded or are available for a given attribute name."""
    path: GetContextAttributeValuesRequestPath

# Operation: search_context_instances
class SearchContextInstancesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the context instances to search.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment within the project to search.", json_schema_extra={'format': 'string'})
class SearchContextInstancesRequestQuery(StrictModel):
    continuation_token: str | None = Field(default=None, validation_alias="continuationToken", serialization_alias="continuationToken", description="Pagination token for retrieving subsequent result pages. Use the `next` link from previous responses when available, or provide a continuation token to fetch results after a specific sort value.", json_schema_extra={'format': 'string'})
    include_total_count: bool | None = Field(default=None, validation_alias="includeTotalCount", serialization_alias="includeTotalCount", description="Whether to include the total count of all matching context instances in the response (defaults to true).")
class SearchContextInstancesRequestBody(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of context instances to return in a single response, between 1 and 50 items (defaults to 20).")
    sort: str | None = Field(default=None, description="Field to sort results by. Use `ts` for ascending timestamp order or `-ts` for descending timestamp order.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter expression to narrow results by context attributes. Supports nested filter syntax for querying kindKeys, timestamps, and other context properties. See LaunchDarkly filtering documentation for syntax details.")
class SearchContextInstancesRequest(StrictModel):
    """Search for context instances within a specific project and environment using filters, sorting, and pagination. Supports advanced filtering syntax for querying context data across your application."""
    path: SearchContextInstancesRequestPath
    query: SearchContextInstancesRequestQuery | None = None
    body: SearchContextInstancesRequestBody | None = None

# Operation: get_context_instance
class GetContextInstancesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the context instance.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the context instance to retrieve.", json_schema_extra={'format': 'string'})
class GetContextInstancesRequestQuery(StrictModel):
    include_total_count: bool | None = Field(default=None, validation_alias="includeTotalCount", serialization_alias="includeTotalCount", description="Whether to include the total count of matching context instances in the response. Defaults to true if not specified.")
class GetContextInstancesRequest(StrictModel):
    """Retrieve a specific context instance by its ID within a project and environment. Returns detailed information about the context instance configuration."""
    path: GetContextInstancesRequestPath
    query: GetContextInstancesRequestQuery | None = None

# Operation: delete_context_instance
class DeleteContextInstancesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the context instance to delete.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the context instance is located.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the context instance to delete.", json_schema_extra={'format': 'string'})
class DeleteContextInstancesRequest(StrictModel):
    """Delete a specific context instance by its ID within a project environment. This operation permanently removes the context instance and cannot be undone."""
    path: DeleteContextInstancesRequestPath

# Operation: search_contexts
class SearchContextsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the environment to search.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies the specific environment within the project where contexts will be searched.", json_schema_extra={'format': 'string'})
class SearchContextsRequestQuery(StrictModel):
    include_total_count: bool | None = Field(default=None, validation_alias="includeTotalCount", serialization_alias="includeTotalCount", description="Whether to include the total count of all matching contexts in the response. Defaults to true if not specified.")
class SearchContextsRequestBody(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of contexts to return in the response. Accepts values up to 50, with a default of 20 if not specified.")
    sort: str | None = Field(default=None, description="Field to sort results by. Use 'ts' for ascending chronological order or '-ts' for descending order by timestamp.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter expression to narrow results by context attributes and kinds. Supports multiple conditions using operators like 'startsWith' and 'anyOf', separated by commas.")
class SearchContextsRequest(StrictModel):
    """Search for contexts in a LaunchDarkly environment using filters, sorting, and pagination. Supports advanced filtering by context attributes and kinds to find specific contexts matching your criteria."""
    path: SearchContextsRequestPath
    query: SearchContextsRequestQuery | None = None
    body: SearchContextsRequestBody | None = None

# Operation: update_flag_setting_for_context
class PutContextFlagSettingRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the flag setting applies.", json_schema_extra={'format': 'string'})
    context_kind: str = Field(default=..., validation_alias="contextKind", serialization_alias="contextKind", description="The context kind (e.g., 'user', 'organization') that categorizes the context.", json_schema_extra={'format': 'string'})
    context_key: str = Field(default=..., validation_alias="contextKey", serialization_alias="contextKey", description="The unique identifier for the context within its kind.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The key of the feature flag to update.", json_schema_extra={'format': 'string'})
class PutContextFlagSettingRequestBody(StrictModel):
    setting: Any | None = Field(default=None, description="The variation value to assign to this context. Must match the flag's variation type (e.g., true/false for boolean flags, a string value for string flags). Omit or set to null to remove the context's flag setting.")
class PutContextFlagSettingRequest(StrictModel):
    """Set or clear a feature flag's variation value for a specific context. Omit or set `setting` to null to erase the current setting; otherwise, provide a variation value matching the flag's type (e.g., boolean, string)."""
    path: PutContextFlagSettingRequestPath
    body: PutContextFlagSettingRequestBody | None = None

# Operation: get_context
class GetContextsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the context.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project.", json_schema_extra={'format': 'string'})
    kind: str = Field(default=..., description="The category or type of context (e.g., 'user', 'organization', 'device').", json_schema_extra={'format': 'string'})
    key: str = Field(default=..., description="The unique identifier for the specific context instance within its kind.", json_schema_extra={'format': 'string'})
class GetContextsRequestQuery(StrictModel):
    include_total_count: bool | None = Field(default=None, validation_alias="includeTotalCount", serialization_alias="includeTotalCount", description="Whether to include the total count of matching contexts in the response. Defaults to true if not specified.")
class GetContextsRequest(StrictModel):
    """Retrieve a specific context by its kind and key within a project environment. Contexts are used to segment user data and targeting rules."""
    path: GetContextsRequestPath
    query: GetContextsRequestQuery | None = None

# Operation: list_experiments
class GetExperimentsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the experiments.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies the specific environment within the project where experiments are located.", json_schema_extra={'format': 'string'})
class GetExperimentsRequestQuery(StrictModel):
    lifecycle_state: str | None = Field(default=None, validation_alias="lifecycleState", serialization_alias="lifecycleState", description="A comma-separated list specifying which experiment states to include in results. Valid values are `archived`, `active`, or both. Defaults to returning only active experiments if not specified.", json_schema_extra={'format': 'string'})
class GetExperimentsRequest(StrictModel):
    """Retrieve all experiments in an environment with optional filtering by flag, metric, or iteration status, and optional expansion of related data such as iterations, metrics, treatments, and analysis configuration."""
    path: GetExperimentsRequestPath
    query: GetExperimentsRequestQuery | None = None

# Operation: create_experiment
class CreateExperimentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project where the experiment will be created.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the experiment will run.", json_schema_extra={'format': 'string'})
class CreateExperimentRequestBodyIteration(StrictModel):
    hypothesis: str = Field(default=..., validation_alias="hypothesis", serialization_alias="hypothesis", description="A clear statement of the expected outcome or business hypothesis being tested by this experiment.")
    can_reshuffle_traffic: bool | None = Field(default=None, validation_alias="canReshuffleTraffic", serialization_alias="canReshuffleTraffic", description="Whether traffic can be reassigned to different variations when audience size changes. Defaults to true, allowing dynamic reallocation.")
    metrics: list[MetricInput] = Field(default=..., validation_alias="metrics", serialization_alias="metrics", description="Array of metric objects defining which metrics will be measured and analyzed for this experiment. Each metric specifies how success is measured.")
    primary_single_metric_key: str | None = Field(default=None, validation_alias="primarySingleMetricKey", serialization_alias="primarySingleMetricKey", description="The key of the primary metric to analyze. Either this or `primaryFunnelKey` must be specified, but not both.")
    primary_funnel_key: str | None = Field(default=None, validation_alias="primaryFunnelKey", serialization_alias="primaryFunnelKey", description="The key of the primary funnel group (multi-step metric) to analyze. Either this or `primarySingleMetricKey` must be specified, but not both.")
    treatments: list[TreatmentInput] = Field(default=..., validation_alias="treatments", serialization_alias="treatments", description="Array of treatment objects defining the variations being tested. Each treatment corresponds to a feature flag variation.")
    flags: dict[str, FlagInput] = Field(default=..., validation_alias="flags", serialization_alias="flags", description="Object containing the feature flag key and targeting rules that determine which users see which variations in this iteration.")
    randomization_unit: str | None = Field(default=None, validation_alias="randomizationUnit", serialization_alias="randomizationUnit", description="The unit used to consistently assign users to variations (e.g., 'user', 'account', 'organization'). Defaults to 'user'.")
    reallocation_frequency_millis: int | None = Field(default=None, validation_alias="reallocationFrequencyMillis", serialization_alias="reallocationFrequencyMillis", description="For multi-armed bandit experiments, the frequency in milliseconds at which traffic allocation is automatically rebalanced across variations based on performance.")
    covariate_id: str | None = Field(default=None, validation_alias="covariateId", serialization_alias="covariateId", description="The identifier of an uploaded covariate CSV file used to adjust analysis for known variables that may affect results.")
    attributes: list[str] | None = Field(default=None, validation_alias="attributes", serialization_alias="attributes", description="Array of attribute names (e.g., 'country', 'device', 'os') that can be used to segment and analyze experiment results by user characteristics.")
class CreateExperimentRequestBodyAnalysisConfig(StrictModel):
    bayesian_threshold: str | None = Field(default=None, validation_alias="bayesianThreshold", serialization_alias="bayesianThreshold", description="For Bayesian analysis, the probability threshold (as a percentage) for determining if a variation is likely better than the baseline. Higher values require stronger evidence.")
    significance_threshold: str | None = Field(default=None, validation_alias="significanceThreshold", serialization_alias="significanceThreshold", description="For Frequentist analysis, the significance threshold (as a percentage) for statistical significance. Typical values are 5 for 95% confidence.")
    test_direction: str | None = Field(default=None, validation_alias="testDirection", serialization_alias="testDirection", description="For Frequentist analysis, whether the test is one-sided (directional) or two-sided (non-directional) when comparing variations to baseline.")
    multiple_comparison_correction_method: Literal["bonferroni", "benjamini-hochberg"] | None = Field(default=None, validation_alias="multipleComparisonCorrectionMethod", serialization_alias="multipleComparisonCorrectionMethod", description="Method to correct for multiple comparisons in Frequentist analysis: 'bonferroni' is conservative, 'benjamini-hochberg' is less conservative.")
    multiple_comparison_correction_scope: Literal["variations", "variations-and-metrics", "metrics"] | None = Field(default=None, validation_alias="multipleComparisonCorrectionScope", serialization_alias="multipleComparisonCorrectionScope", description="Scope of multiple comparison correction: 'variations' corrects across variations only, 'metrics' corrects across metrics only, or 'variations-and-metrics' corrects across both.")
    sequential_testing_enabled: bool | None = Field(default=None, validation_alias="sequentialTestingEnabled", serialization_alias="sequentialTestingEnabled", description="Whether to enable sequential testing for Frequentist analysis, allowing results to be checked at interim points rather than only at the end.")
class CreateExperimentRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the experiment that describes its purpose.")
    key: str = Field(default=..., description="A unique identifier for the experiment, used in API calls and references. Must be URL-safe.")
    holdout_id: str | None = Field(default=None, validation_alias="holdoutId", serialization_alias="holdoutId", description="The identifier of a holdout group to exclude from the experiment while measuring their metrics separately for comparison.")
    tags: list[str] | None = Field(default=None, description="Array of tags for organizing and categorizing the experiment for easier discovery and management.")
    methodology: Literal["bayesian", "frequentist", "export_only"] | None = Field(default=None, description="The statistical methodology for analyzing results: 'bayesian' (default) uses probability-based analysis, 'frequentist' uses traditional hypothesis testing, or 'export_only' for external analysis.")
    data_source: Literal["launchdarkly", "snowflake"] | None = Field(default=None, validation_alias="dataSource", serialization_alias="dataSource", description="The source system for metric data analysis: 'launchdarkly' (default) uses LaunchDarkly's event data, 'snowflake' or 'databricks' connect to external data warehouses.")
    iteration: CreateExperimentRequestBodyIteration
    analysis_config: CreateExperimentRequestBodyAnalysisConfig | None = Field(default=None, validation_alias="analysisConfig", serialization_alias="analysisConfig")
class CreateExperimentRequest(StrictModel):
    """Create a new experiment in a LaunchDarkly project environment. After creation, you must create an iteration and update the experiment with the `startIteration` instruction to run it."""
    path: CreateExperimentRequestPath
    body: CreateExperimentRequestBody

# Operation: get_experiment
class GetExperimentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the experiment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the experiment is running.", json_schema_extra={'format': 'string'})
    experiment_key: str = Field(default=..., validation_alias="experimentKey", serialization_alias="experimentKey", description="The unique identifier for the experiment to retrieve. Use the optional `expand` query parameter to include additional fields such as previousIterations, draftIteration, secondaryMetrics, treatments, or analysisConfig in the response.", json_schema_extra={'format': 'string'})
class GetExperimentRequest(StrictModel):
    """Retrieve detailed information about a specific experiment in a LaunchDarkly project environment. Optionally expand the response to include iterations, metrics, treatments, and analysis configuration."""
    path: GetExperimentRequestPath

# Operation: update_experiment
class PatchExperimentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the experiment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the experiment exists.", json_schema_extra={'format': 'string'})
    experiment_key: str = Field(default=..., validation_alias="experimentKey", serialization_alias="experimentKey", description="The unique identifier for the experiment to update.", json_schema_extra={'format': 'string'})
class PatchExperimentRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instructions to apply to the experiment. Each instruction is an object with a `kind` field specifying the operation (updateName, updateDescription, startIteration, stopIteration, archiveExperiment, or restoreExperiment) and optional parameters like `value`, `changeJustification`, `winningTreatmentId`, or `winningReason` depending on the instruction type.")
class PatchExperimentRequest(StrictModel):
    """Update an experiment using semantic patch instructions. Supports operations like renaming, updating descriptions, managing iterations, and archiving experiments."""
    path: PatchExperimentRequestPath
    body: PatchExperimentRequestBody

# Operation: list_flag_followers_by_project_environment
class GetFollowersByProjEnvRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the flags and environment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where you want to retrieve flag followers.", json_schema_extra={'format': 'string'})
class GetFollowersByProjEnvRequest(StrictModel):
    """Retrieve all followers across feature flags within a specific project and environment. This returns the list of users or teams monitoring flag changes in that environment."""
    path: GetFollowersByProjEnvRequestPath

# Operation: reset_mobile_key_for_environment
class ResetEnvironmentMobileKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the environment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment whose mobile SDK key should be reset.", json_schema_extra={'format': 'string'})
class ResetEnvironmentMobileKeyRequest(StrictModel):
    """Reset an environment's mobile SDK key, immediately expiring the previous key. This operation generates a new mobile key for the specified environment within a project."""
    path: ResetEnvironmentMobileKeyRequestPath

# Operation: evaluate_context_instance_segment_memberships
class GetContextInstanceSegmentsMembershipByEnvRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the LaunchDarkly project. This is a string identifier used to scope the operation within your workspace.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies the specific environment within the project. This determines which segment definitions and rules are evaluated.", json_schema_extra={'format': 'string'})
class GetContextInstanceSegmentsMembershipByEnvRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The context instance to evaluate. Must include a unique key identifier, a kind (e.g., 'user', 'organization'), and any custom attributes relevant to segment rules (e.g., name, jobFunction, address). The structure supports nested objects for complex attributes.", examples=[{'address': {'city': 'Springfield', 'street': '123 Main Street'}, 'jobFunction': 'doctor', 'key': 'context-key-123abc', 'kind': 'user', 'name': 'Sandy'}])
class GetContextInstanceSegmentsMembershipByEnvRequest(StrictModel):
    """Evaluate which segments a context instance belongs to based on its attributes. Provide a context instance with its key, kind, and custom attributes to retrieve membership status across all segments in the environment."""
    path: GetContextInstanceSegmentsMembershipByEnvRequestPath
    body: GetContextInstanceSegmentsMembershipByEnvRequestBody

# Operation: get_experimentation_settings
class GetExperimentationSettingsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project whose experimentation settings you want to retrieve.", json_schema_extra={'format': 'string'})
class GetExperimentationSettingsRequest(StrictModel):
    """Retrieve the current experimentation settings configured for a specific project. This includes all active experimentation policies and configurations."""
    path: GetExperimentationSettingsRequestPath

# Operation: update_experimentation_settings
class PutExperimentationSettingsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project whose experimentation settings should be updated.", json_schema_extra={'format': 'string'})
class PutExperimentationSettingsRequestBody(StrictModel):
    randomization_units: list[RandomizationUnitInput] = Field(default=..., validation_alias="randomizationUnits", serialization_alias="randomizationUnits", description="An array of randomization units that are permitted for experiments in this project. Each unit defines how experiment subjects are randomly assigned to variations.")
class PutExperimentationSettingsRequest(StrictModel):
    """Update the experimentation settings for a project, including the randomization units that are allowed for running experiments."""
    path: PutExperimentationSettingsRequestPath
    body: PutExperimentationSettingsRequestBody

# Operation: list_experiments_project
class GetExperimentsAnyEnvRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project from which to retrieve experiments.", json_schema_extra={'format': 'string'})
class GetExperimentsAnyEnvRequestQuery(StrictModel):
    lifecycle_state: str | None = Field(default=None, validation_alias="lifecycleState", serialization_alias="lifecycleState", description="Filter experiments by lifecycle state using a comma-separated list. Valid values are `active`, `archived`, or both. Defaults to `active` experiments only if not specified.", json_schema_extra={'format': 'string'})
class GetExperimentsAnyEnvRequest(StrictModel):
    """Retrieve a list of experiments across all environments in a project, optionally filtered by lifecycle state (active, archived, or both)."""
    path: GetExperimentsAnyEnvRequestPath
    query: GetExperimentsAnyEnvRequestQuery | None = None

# Operation: get_flag_defaults_for_project
class GetFlagDefaultsByProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Used to scope the flag defaults to a specific project.", json_schema_extra={'format': 'string'})
class GetFlagDefaultsByProjectRequest(StrictModel):
    """Retrieve the default flag settings configured for a specific project. These defaults apply to feature flags within the project unless overridden at a more granular level."""
    path: GetFlagDefaultsByProjectRequestPath

# Operation: update_flag_defaults_for_project
class PutFlagDefaultsByProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project where flag defaults will be applied.", json_schema_extra={'format': 'string'})
class PutFlagDefaultsByProjectRequestBodyBooleanDefaults(StrictModel):
    true_display_name: str = Field(default=..., validation_alias="trueDisplayName", serialization_alias="trueDisplayName", description="The display name shown in the LaunchDarkly UI for the true variation of flags (e.g., 'On', 'Enabled', 'True').")
    false_display_name: str = Field(default=..., validation_alias="falseDisplayName", serialization_alias="falseDisplayName", description="The display name shown in the LaunchDarkly UI for the false variation of flags (e.g., 'Off', 'Disabled', 'False').")
    true_description: str = Field(default=..., validation_alias="trueDescription", serialization_alias="trueDescription", description="A description explaining the purpose or behavior of the true variation, displayed in the LaunchDarkly UI.")
    false_description: str = Field(default=..., validation_alias="falseDescription", serialization_alias="falseDescription", description="A description explaining the purpose or behavior of the false variation, displayed in the LaunchDarkly UI.")
    on_variation: int = Field(default=..., validation_alias="onVariation", serialization_alias="onVariation", description="The index (0 or 1) of the variation to serve when flag targeting is enabled and no rules match the target.")
    off_variation: int = Field(default=..., validation_alias="offVariation", serialization_alias="offVariation", description="The index (0 or 1) of the variation to serve when flag targeting is disabled.")
class PutFlagDefaultsByProjectRequestBodyDefaultClientSideAvailability(StrictModel):
    using_mobile_key: bool = Field(default=..., validation_alias="usingMobileKey", serialization_alias="usingMobileKey", description="Whether flags should be available to mobile SDKs by default.")
    using_environment_id: bool = Field(default=..., validation_alias="usingEnvironmentId", serialization_alias="usingEnvironmentId", description="Whether flags should be available to client-side SDKs by default.")
class PutFlagDefaultsByProjectRequestBody(StrictModel):
    tags: list[str] = Field(default=..., description="A list of default tag labels to automatically assign to each new flag created in this project. Tags help organize and categorize flags.")
    temporary: bool = Field(default=..., description="Whether newly created flags should be marked as temporary by default, indicating they are intended for short-term use.")
    boolean_defaults: PutFlagDefaultsByProjectRequestBodyBooleanDefaults = Field(default=..., validation_alias="booleanDefaults", serialization_alias="booleanDefaults")
    default_client_side_availability: PutFlagDefaultsByProjectRequestBodyDefaultClientSideAvailability = Field(default=..., validation_alias="defaultClientSideAvailability", serialization_alias="defaultClientSideAvailability")
class PutFlagDefaultsByProjectRequest(StrictModel):
    """Set default configuration values for all feature flags created in a project, including naming conventions, targeting behavior, and SDK availability."""
    path: PutFlagDefaultsByProjectRequestPath
    body: PutFlagDefaultsByProjectRequestBody

# Operation: update_flag_defaults_for_project_partial
class PatchFlagDefaultsByProjectRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that uniquely identifies the project containing the flag defaults to update.", json_schema_extra={'format': 'string'})
class PatchFlagDefaultsByProjectRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of patch operations following RFC 6902 (JSON Patch) or RFC 7386 (JSON Merge Patch) format, specifying the changes to apply to the flag defaults.")
class PatchFlagDefaultsByProjectRequest(StrictModel):
    """Update flag defaults for a project using JSON patch or JSON merge patch operations. This allows you to modify default flag configurations applied across the project."""
    path: PatchFlagDefaultsByProjectRequestPath
    body: PatchFlagDefaultsByProjectRequestBody

# Operation: list_approval_requests_for_flag
class GetApprovalsForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag to retrieve approval requests for.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which to list approval requests.", json_schema_extra={'format': 'string'})
class GetApprovalsForFlagRequest(StrictModel):
    """Retrieve all pending approval requests for a feature flag in a specific environment. Use this to review changes awaiting approval before they can be deployed."""
    path: GetApprovalsForFlagRequestPath

# Operation: create_approval_request_for_feature_flag
class PostApprovalRequestForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag that requires approval for changes.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the flag changes will be applied.", json_schema_extra={'format': 'string'})
class PostApprovalRequestForFlagRequestBody(StrictModel):
    description: str = Field(default=..., description="A concise summary of the requested changes to the feature flag, helping reviewers understand the intent of the approval request.")
    instructions: list[Instruction] = Field(default=..., description="An ordered list of semantic patch instructions that define the exact changes to apply to the feature flag. Instructions must follow the semantic patch format documented in the feature flag update API.")
    execution_date: int | None = Field(default=None, validation_alias="executionDate", serialization_alias="executionDate", description="Optional Unix timestamp (in milliseconds) specifying when the approval request instructions should be automatically executed. If omitted, execution occurs immediately upon approval.", json_schema_extra={'format': 'int64'})
    operating_on_id: str | None = Field(default=None, validation_alias="operatingOnId", serialization_alias="operatingOnId", description="The ID of an existing scheduled change, required only if your instructions modify or delete a previously scheduled change to the flag.")
    integration_config: dict[str, Any] | None = Field(default=None, validation_alias="integrationConfig", serialization_alias="integrationConfig", description="Optional custom fields for third-party approval system integrations. Field definitions are provided in the integration's manifest.json file in the LaunchDarkly integration framework repository.")
class PostApprovalRequestForFlagRequest(StrictModel):
    """Submit an approval request to modify a feature flag in a specific environment. The request includes semantic patch instructions that will be applied upon approval, with optional scheduling and third-party integration metadata."""
    path: PostApprovalRequestForFlagRequestPath
    body: PostApprovalRequestForFlagRequestBody

# Operation: create_flag_copy_approval_request
class PostFlagCopyConfigApprovalRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose configuration will be copied.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the target environment where the flag configuration will be copied to.", json_schema_extra={'format': 'string'})
class PostFlagCopyConfigApprovalRequestBodySource(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The unique identifier for the source environment from which the flag configuration will be copied.")
class PostFlagCopyConfigApprovalRequestBody(StrictModel):
    description: str = Field(default=..., description="A brief summary explaining the purpose of this configuration copy request (e.g., 'copy flag settings to another environment').")
    included_actions: list[Literal["updateOn", "updateFallthrough", "updateOffVariation", "updateRules", "updateTargets", "updatePrerequisites"]] | None = Field(default=None, validation_alias="includedActions", serialization_alias="includedActions", description="Optional list of specific flag changes to copy from source to target environment (e.g., 'updateOn'). You may specify either included or excluded actions, but not both. If omitted, all flag changes will be copied.")
    source: PostFlagCopyConfigApprovalRequestBodySource
class PostFlagCopyConfigApprovalRequest(StrictModel):
    """Create an approval request to copy a feature flag's configuration from a source environment to a target environment. This allows controlled promotion of flag settings across your deployment environments."""
    path: PostFlagCopyConfigApprovalRequestPath
    body: PostFlagCopyConfigApprovalRequestBody

# Operation: get_approval_request_for_flag
class GetApprovalForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag associated with this approval request.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the approval request applies.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the specific approval request to retrieve.", json_schema_extra={'format': 'string'})
class GetApprovalForFlagRequest(StrictModel):
    """Retrieve a specific approval request for a feature flag in a given environment. Use this to check the status and details of a pending or completed approval workflow."""
    path: GetApprovalForFlagRequestPath

# Operation: delete_approval_request_for_flag
class DeleteApprovalRequestForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag associated with the approval request.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the approval request applies.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the approval request to delete.", json_schema_extra={'format': 'string'})
class DeleteApprovalRequestForFlagRequest(StrictModel):
    """Delete a pending approval request for a feature flag in a specific environment. This removes the approval workflow, preventing further review or approval actions on the request."""
    path: DeleteApprovalRequestForFlagRequestPath

# Operation: apply_approval_request_for_flag
class PostApprovalRequestApplyForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag associated with the approval request.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the approval request will be applied.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the approval request to apply. The request must have been previously approved before it can be applied.", json_schema_extra={'format': 'string'})
class PostApprovalRequestApplyForFlagRequest(StrictModel):
    """Apply an approval request that has been approved for a feature flag in a specific environment. This executes the changes specified in the approval request."""
    path: PostApprovalRequestApplyForFlagRequestPath

# Operation: review_approval_request_for_flag
class PostApprovalRequestReviewForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag being reviewed.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the approval request applies.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the approval request being reviewed.", json_schema_extra={'format': 'string'})
class PostApprovalRequestReviewForFlagRequestBody(StrictModel):
    kind: Literal["approve", "comment", "decline"] | None = Field(default=None, description="The type of review action: approve to accept the changes, decline to reject them, or comment to provide feedback without a final decision.")
class PostApprovalRequestReviewForFlagRequest(StrictModel):
    """Submit a review decision on a pending approval request for a feature flag, either approving, declining, or commenting on the proposed changes."""
    path: PostApprovalRequestReviewForFlagRequestPath
    body: PostApprovalRequestReviewForFlagRequestBody | None = None

# Operation: list_flag_followers
class GetFlagFollowersRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose followers you want to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which to retrieve flag followers.", json_schema_extra={'format': 'string'})
class GetFlagFollowersRequest(StrictModel):
    """Retrieve a list of team members who are following a specific feature flag within a project and environment. This helps identify who is monitoring changes to the flag."""
    path: GetFlagFollowersRequestPath

# Operation: add_flag_follower
class PutFlagFollowerRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag to follow.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the flag follower relationship applies.", json_schema_extra={'format': 'string'})
    member_id: str = Field(default=..., validation_alias="memberId", serialization_alias="memberId", description="The unique identifier of the team member to add as a follower. Members with reader-level permissions can only add themselves, while higher-privileged members can add any team member.", json_schema_extra={'format': 'string'})
class PutFlagFollowerRequest(StrictModel):
    """Subscribe a team member to receive updates about a feature flag's changes in a specific project and environment. Members with reader roles can only add themselves as followers."""
    path: PutFlagFollowerRequestPath

# Operation: remove_flag_follower
class DeleteFlagFollowerRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag from which to remove the follower.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the flag follower relationship exists.", json_schema_extra={'format': 'string'})
    member_id: str = Field(default=..., validation_alias="memberId", serialization_alias="memberId", description="The unique identifier of the member to remove as a follower. Members with reader roles can only remove themselves; other roles can remove any member.", json_schema_extra={'format': 'string'})
class DeleteFlagFollowerRequest(StrictModel):
    """Remove a member as a follower of a feature flag in a specific project and environment. Members with reader roles can only remove themselves as followers."""
    path: DeleteFlagFollowerRequestPath

# Operation: list_scheduled_changes_for_flag
class GetFlagConfigScheduledChangesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose scheduled changes you want to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which to list scheduled changes for the feature flag.", json_schema_extra={'format': 'string'})
class GetFlagConfigScheduledChangesRequest(StrictModel):
    """Retrieve all scheduled changes pending application to a feature flag in a specific environment. This shows future modifications that will be automatically applied at their scheduled times."""
    path: GetFlagConfigScheduledChangesRequestPath

# Operation: create_scheduled_changes_for_flag
class PostFlagConfigScheduledChangesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key to schedule changes for.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the scheduled changes will be applied.", json_schema_extra={'format': 'string'})
class PostFlagConfigScheduledChangesRequestQuery(StrictModel):
    ignore_conflicts: bool | None = Field(default=None, validation_alias="ignoreConflicts", serialization_alias="ignoreConflicts", description="If true, the operation succeeds even when these instructions conflict with existing scheduled changes. If false (default), the operation fails on conflicts.")
class PostFlagConfigScheduledChangesRequestBody(StrictModel):
    execution_date: int = Field(default=..., validation_alias="executionDate", serialization_alias="executionDate", description="Unix timestamp (milliseconds) indicating when the scheduled changes should be executed.", json_schema_extra={'format': 'int64'})
    instructions: list[Instruction] = Field(default=..., description="Array containing a single object with `kind: \"scheduled_action\"` and semantic patch instructions. Supported instructions are the same as those available when updating a feature flag directly.")
class PostFlagConfigScheduledChangesRequest(StrictModel):
    """Schedule semantic patch instructions to be applied to a feature flag at a specified future date. Optionally allow the operation to succeed even if scheduled changes conflict with existing ones."""
    path: PostFlagConfigScheduledChangesRequestPath
    query: PostFlagConfigScheduledChangesRequestQuery | None = None
    body: PostFlagConfigScheduledChangesRequestBody

# Operation: get_scheduled_change_for_feature_flag
class GetFeatureFlagScheduledChangeRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag associated with the scheduled change.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the scheduled change will be applied.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the scheduled change to retrieve.", json_schema_extra={'format': 'string'})
class GetFeatureFlagScheduledChangeRequest(StrictModel):
    """Retrieve a specific scheduled change that will be applied to a feature flag in a given environment. Use this to inspect the details of a pending flag modification by its ID."""
    path: GetFeatureFlagScheduledChangeRequestPath

# Operation: update_scheduled_flag_change
class PatchFlagConfigScheduledChangeRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key for which the scheduled change applies.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the scheduled change is configured.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduled change to update.", json_schema_extra={'format': 'string'})
class PatchFlagConfigScheduledChangeRequestQuery(StrictModel):
    ignore_conflicts: bool | None = Field(default=None, validation_alias="ignoreConflicts", serialization_alias="ignoreConflicts", description="Set to `true` to allow the update even if new instructions conflict with existing scheduled changes, or `false` to reject conflicting updates. Defaults to `false`.")
class PatchFlagConfigScheduledChangeRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instructions to apply. Each instruction is an object with a `kind` field specifying the operation (deleteScheduledChange, replaceScheduledChangesInstructions, or updateScheduledChangesExecutionDate). Some instructions require a `value` field with the new data.")
class PatchFlagConfigScheduledChangeRequest(StrictModel):
    """Update a scheduled flag change by replacing its instructions or execution date using semantic patch operations. Supports deleting the scheduled change, modifying its execution time, or changing the flag actions to be performed."""
    path: PatchFlagConfigScheduledChangeRequestPath
    query: PatchFlagConfigScheduledChangeRequestQuery | None = None
    body: PatchFlagConfigScheduledChangeRequestBody

# Operation: delete_scheduled_flag_changes
class DeleteFlagConfigScheduledChangesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the feature flag. Used to scope the operation to a specific project.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The feature flag key identifying which flag's scheduled changes should be deleted.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key specifying which environment's scheduled changes workflow should be removed.", json_schema_extra={'format': 'string'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduled changes workflow to delete.", json_schema_extra={'format': 'string'})
class DeleteFlagConfigScheduledChangesRequest(StrictModel):
    """Delete a scheduled changes workflow for a feature flag in a specific environment. This removes the pending scheduled changes and cancels any automation associated with the workflow."""
    path: DeleteFlagConfigScheduledChangesRequestPath

# Operation: list_workflows_for_feature_flag
class GetWorkflowsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag whose workflows you want to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which to retrieve workflows.", json_schema_extra={'format': 'string'})
class GetWorkflowsRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Filter workflows by their current status. Supported values are `active` (ongoing workflows), `completed` (finished workflows), and `failed` (workflows that encountered errors). Omit to retrieve workflows of all statuses.", json_schema_extra={'format': 'string'})
class GetWorkflowsRequest(StrictModel):
    """Retrieve all workflows associated with a feature flag in a specific environment. Optionally filter results by workflow status to view active, completed, or failed workflows."""
    path: GetWorkflowsRequestPath
    query: GetWorkflowsRequestQuery | None = None

# Operation: get_custom_workflow
class GetCustomWorkflowRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag and workflow.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag that contains the workflow.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which the workflow operates.", json_schema_extra={'format': 'string'})
    workflow_id: str = Field(default=..., validation_alias="workflowId", serialization_alias="workflowId", description="The unique identifier of the specific workflow to retrieve.", json_schema_extra={'format': 'string'})
class GetCustomWorkflowRequest(StrictModel):
    """Retrieve a specific custom workflow by its ID within a feature flag's environment. Use this to inspect workflow configuration, status, and details."""
    path: GetCustomWorkflowRequestPath

# Operation: delete_workflow
class DeleteWorkflowRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    feature_flag_key: str = Field(default=..., validation_alias="featureFlagKey", serialization_alias="featureFlagKey", description="The unique identifier for the feature flag that contains the workflow to delete.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the workflow is configured.", json_schema_extra={'format': 'string'})
    workflow_id: str = Field(default=..., validation_alias="workflowId", serialization_alias="workflowId", description="The unique identifier for the workflow to delete.", json_schema_extra={'format': 'string'})
class DeleteWorkflowRequest(StrictModel):
    """Remove a workflow from a feature flag in a specific environment. This permanently deletes the workflow and its associated configuration."""
    path: DeleteWorkflowRequestPath

# Operation: get_migration_safety_issues
class PostMigrationSafetyIssuesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag.", json_schema_extra={'format': 'string'})
    flag_key: str = Field(default=..., validation_alias="flagKey", serialization_alias="flagKey", description="The unique identifier for the feature flag being evaluated for migration safety.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment in which the flag changes would be applied.", json_schema_extra={'format': 'string'})
class PostMigrationSafetyIssuesRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instructions that describe the flag modifications to evaluate. Use the same instruction format as standard flag update operations. Order matters—instructions are applied sequentially.")
class PostMigrationSafetyIssuesRequest(StrictModel):
    """Analyzes a feature flag patch and returns any migration safety issues that would result from applying those changes. Use this to validate flag modifications before deployment."""
    path: PostMigrationSafetyIssuesRequestPath
    body: PostMigrationSafetyIssuesRequestBody

# Operation: add_flag_to_release_pipeline
class CreateReleaseForFlagRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the flag.", json_schema_extra={'format': 'string'})
    flag_key: str = Field(default=..., validation_alias="flagKey", serialization_alias="flagKey", description="The unique identifier for the flag to be added to the release pipeline.", json_schema_extra={'format': 'string'})
class CreateReleaseForFlagRequestBody(StrictModel):
    release_variation_id: str | None = Field(default=None, validation_alias="releaseVariationId", serialization_alias="releaseVariationId", description="The variation to release across all phases of the pipeline. If not specified, the default variation will be used.")
    release_pipeline_key: str = Field(default=..., validation_alias="releasePipelineKey", serialization_alias="releasePipelineKey", description="The unique identifier of the release pipeline to attach the flag to.")
class CreateReleaseForFlagRequest(StrictModel):
    """Adds a flag to a release pipeline, optionally specifying which variation to release across all phases. This initiates the flag's progression through the release pipeline's defined stages."""
    path: CreateReleaseForFlagRequestPath
    body: CreateReleaseForFlagRequestBody

# Operation: update_release_phase_status
class UpdatePhaseStatusRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the feature flag release.", json_schema_extra={'format': 'string'})
    flag_key: str = Field(default=..., validation_alias="flagKey", serialization_alias="flagKey", description="The unique identifier for the feature flag whose release phase should be updated.", json_schema_extra={'format': 'string'})
    phase_id: str = Field(default=..., validation_alias="phaseId", serialization_alias="phaseId", description="The unique identifier for the specific phase within the release whose status should be updated.", json_schema_extra={'format': 'string'})
class UpdatePhaseStatusRequestBody(StrictModel):
    status: str | None = Field(default=None, description="The new execution status to assign to the phase, controlling its progression through the release lifecycle.")
    audiences: list[ReleaserAudienceConfigInput] | None = Field(default=None, description="An ordered list of audience configurations to apply when initializing the phase. Each item specifies targeting rules and rollout parameters for that audience segment.")
class UpdatePhaseStatusRequest(StrictModel):
    """Update the execution status of a specific phase within a feature flag release. Use this to advance phases through their lifecycle and configure audience targeting for phase initialization."""
    path: UpdatePhaseStatusRequestPath
    body: UpdatePhaseStatusRequestBody | None = None

# Operation: list_layers
class GetLayersRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. This string value is used to scope the layer collection to a specific project.", json_schema_extra={'format': 'string'})
class GetLayersRequest(StrictModel):
    """Retrieve all layers for a specified project. Returns a collection of layer resources associated with the given project."""
    path: GetLayersRequestPath

# Operation: create_layer
class CreateLayerRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project where the layer will be created.", json_schema_extra={'format': 'string'})
class CreateLayerRequestBody(StrictModel):
    key: str = Field(default=..., description="A unique identifier for the layer, typically in kebab-case format (e.g., 'checkout-flow'). This key is used to reference the layer in API calls and must be distinct within the project.")
    name: str = Field(default=..., description="A human-readable name for the layer that describes its purpose (e.g., 'Checkout Flow'). This is displayed in the UI and should be clear and descriptive.")
    description: str = Field(default=..., description="A detailed description explaining the layer's purpose and scope within the application. This helps team members understand what experiments belong in this layer.")
class CreateLayerRequest(StrictModel):
    """Create a new layer within a project to enable mutually-exclusive traffic allocation across experiments. Experiments running in the same layer will have their traffic split exclusively among them."""
    path: CreateLayerRequestPath
    body: CreateLayerRequestBody

# Operation: update_layer
class UpdateLayerRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the layer.", json_schema_extra={'format': 'string'})
    layer_key: str = Field(default=..., validation_alias="layerKey", serialization_alias="layerKey", description="The unique identifier for the layer to update.", json_schema_extra={'format': 'string'})
class UpdateLayerRequestBody(StrictModel):
    environment_key: str | None = Field(default=None, validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key for environment-specific updates, such as modifying experiment traffic reservations. Required when updating experiment reservations.")
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instructions defining the updates to apply. Each instruction object must include a `kind` field specifying the operation type (updateName, updateDescription, updateExperimentReservation, or removeExperiment), along with any required parameters for that instruction type.")
class UpdateLayerRequest(StrictModel):
    """Modify a layer's properties or experiment traffic reservations using semantic patch instructions. Supports updating layer name/description or managing traffic reservations for experiments within the layer."""
    path: UpdateLayerRequestPath
    body: UpdateLayerRequestBody

# Operation: list_metric_groups
class GetMetricGroupsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Used to scope the metric groups to a specific project.", json_schema_extra={'format': 'string'})
class GetMetricGroupsRequest(StrictModel):
    """Retrieve all metric groups for a project. Supports filtering by experiment status, connections, kind, maintainers, and fuzzy search; results can be sorted by name, creation date, or connection count."""
    path: GetMetricGroupsRequestPath

# Operation: create_metric_group
class CreateMetricGroupRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project where the metric group will be created.", json_schema_extra={'format': 'string'})
class CreateMetricGroupRequestBody(StrictModel):
    key: str | None = Field(default=None, description="A unique identifier for the metric group used in API references and integrations. If not provided, one will be auto-generated.")
    name: str = Field(default=..., description="A human-readable name for the metric group that appears in the UI and reports.")
    kind: Literal["funnel", "standard"] = Field(default=..., description="The classification type for the metric group: 'standard' for a regular collection of metrics, or 'funnel' for a sequential progression of steps.")
    maintainer_id: str = Field(default=..., validation_alias="maintainerId", serialization_alias="maintainerId", description="The ID of the team member responsible for maintaining and managing this metric group.")
    tags: list[str] = Field(default=..., description="One or more tags to categorize and organize the metric group for easier discovery and filtering.")
    metrics: list[MetricInMetricGroupInput] = Field(default=..., description="An ordered list of metrics to include in the group. The order is significant and determines the sequence in which metrics are displayed and processed.")
class CreateMetricGroupRequest(StrictModel):
    """Create a new metric group within a project to organize and track related metrics. Metric groups can be configured as standard collections or funnel-type progressions."""
    path: CreateMetricGroupRequestPath
    body: CreateMetricGroupRequestBody

# Operation: get_metric_group
class GetMetricGroupRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the metric group.", json_schema_extra={'format': 'string'})
    metric_group_key: str = Field(default=..., validation_alias="metricGroupKey", serialization_alias="metricGroupKey", description="The unique identifier for the metric group to retrieve.", json_schema_extra={'format': 'string'})
class GetMetricGroupRequest(StrictModel):
    """Retrieve detailed information about a specific metric group within a project. Optionally expand the response to include associated experiments or experiment counts."""
    path: GetMetricGroupRequestPath

# Operation: update_metric_group
class PatchMetricGroupRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the metric group.", json_schema_extra={'format': 'string'})
    metric_group_key: str = Field(default=..., validation_alias="metricGroupKey", serialization_alias="metricGroupKey", description="The unique identifier for the metric group to be updated.", json_schema_extra={'format': 'string'})
class PatchMetricGroupRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations (RFC 6902) specifying the changes to apply. Each operation must include 'op' (the operation type such as 'replace', 'add', or 'remove'), 'path' (the JSON pointer to the target property), and 'value' (the new value, required for 'replace' and 'add' operations).", examples=[[{'op': 'replace', 'path': '/name', 'value': 'my-updated-metric-group'}]])
class PatchMetricGroupRequest(StrictModel):
    """Update a metric group using JSON Patch operations. Apply one or more changes to a metric group's properties by specifying the operation type, target path, and new value."""
    path: PatchMetricGroupRequestPath
    body: PatchMetricGroupRequestBody

# Operation: delete_metric_group
class DeleteMetricGroupRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the metric group to delete.", json_schema_extra={'format': 'string'})
    metric_group_key: str = Field(default=..., validation_alias="metricGroupKey", serialization_alias="metricGroupKey", description="The unique identifier for the metric group to delete.", json_schema_extra={'format': 'string'})
class DeleteMetricGroupRequest(StrictModel):
    """Permanently delete a metric group from a project by its key. This action cannot be undone."""
    path: DeleteMetricGroupRequestPath

# Operation: list_release_pipelines
class GetAllReleasePipelinesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project's release pipelines to retrieve.", json_schema_extra={'format': 'string'})
class GetAllReleasePipelinesRequest(StrictModel):
    """Retrieve all release pipelines for a project. Supports filtering by pipeline attributes (key, name, description) and environment."""
    path: GetAllReleasePipelinesRequestPath

# Operation: create_release_pipeline
class PostReleasePipelineRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that uniquely identifies the project where the release pipeline will be created.", json_schema_extra={'format': 'string'})
class PostReleasePipelineRequestBody(StrictModel):
    key: str = Field(default=..., description="A unique identifier for this release pipeline within the project (e.g., 'standard-pipeline'). Used to reference the pipeline in API calls and configurations.")
    name: str = Field(default=..., description="A human-readable name for the release pipeline (e.g., 'Standard Pipeline'). Displayed in the UI and used for identification.")
    phases: list[CreatePhaseInput] = Field(default=..., description="An ordered array of phase objects that define logical groupings of environments. Each phase shares attributes for coordinating feature rollouts across its environments.")
    tags: list[str] | None = Field(default=None, description="An optional list of tags to categorize and organize the release pipeline (e.g., ['example-tag']). Useful for filtering and searching pipelines.")
    is_project_default: bool | None = Field(default=None, validation_alias="isProjectDefault", serialization_alias="isProjectDefault", description="Optional boolean flag. When true, sets this pipeline as the default for the project. If not specified, only the first pipeline created becomes the default.")
    is_legacy: bool | None = Field(default=None, validation_alias="isLegacy", serialization_alias="isLegacy", description="Optional boolean flag. When true, enables this pipeline for Release Automation features. Controls whether the pipeline participates in automated release workflows.")
class PostReleasePipelineRequest(StrictModel):
    """Create a new release pipeline for a project. The first pipeline created automatically becomes the default; subsequent pipelines can be set as default via the project update API. Projects support up to 20 release pipelines."""
    path: PostReleasePipelineRequestPath
    body: PostReleasePipelineRequestBody

# Operation: get_release_pipeline_by_key
class GetReleasePipelineByKeyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the release pipeline.", json_schema_extra={'format': 'string'})
    pipeline_key: str = Field(default=..., validation_alias="pipelineKey", serialization_alias="pipelineKey", description="The unique identifier for the release pipeline to retrieve.", json_schema_extra={'format': 'string'})
class GetReleasePipelineByKeyRequest(StrictModel):
    """Retrieve a specific release pipeline within a project using its unique key identifier. This operation returns the complete pipeline configuration and metadata."""
    path: GetReleasePipelineByKeyRequestPath

# Operation: update_release_pipeline
class PutReleasePipelineRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the release pipeline.", json_schema_extra={'format': 'string'})
    pipeline_key: str = Field(default=..., validation_alias="pipelineKey", serialization_alias="pipelineKey", description="The unique identifier for the release pipeline to be updated.", json_schema_extra={'format': 'string'})
class PutReleasePipelineRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the release pipeline (e.g., 'Standard Pipeline'). Used to identify the pipeline in the UI and reports.")
    phases: list[CreatePhaseInput] = Field(default=..., description="An ordered array of deployment phases, where each phase represents a logical grouping of one or more environments that share attributes for rolling out changes. Phase order determines the sequence of deployments.")
    tags: list[str] | None = Field(default=None, description="An optional array of tags for categorizing and filtering the release pipeline (e.g., ['example-tag']). Tags help organize pipelines by team, environment type, or other attributes.")
class PutReleasePipelineRequest(StrictModel):
    """Updates an existing release pipeline with new configuration, including its name, deployment phases, and optional tags for organization and filtering."""
    path: PutReleasePipelineRequestPath
    body: PutReleasePipelineRequestBody

# Operation: delete_release_pipeline
class DeleteReleasePipelineRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the release pipeline.", json_schema_extra={'format': 'string'})
    pipeline_key: str = Field(default=..., validation_alias="pipelineKey", serialization_alias="pipelineKey", description="The unique identifier for the release pipeline to delete.", json_schema_extra={'format': 'string'})
class DeleteReleasePipelineRequest(StrictModel):
    """Deletes a release pipeline from a project. Note that the default release pipeline cannot be deleted; if you need to remove it, first create and set a different pipeline as default."""
    path: DeleteReleasePipelineRequestPath

# Operation: list_release_progressions_for_pipeline
class GetAllReleaseProgressionsForReleasePipelineRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the release pipeline.", json_schema_extra={'format': 'string'})
    pipeline_key: str = Field(default=..., validation_alias="pipelineKey", serialization_alias="pipelineKey", description="The unique identifier for the release pipeline whose release progressions you want to retrieve.", json_schema_extra={'format': 'string'})
class GetAllReleaseProgressionsForReleasePipelineRequest(StrictModel):
    """Retrieve the progression status of all releases across all feature flags within a specified release pipeline. This provides a comprehensive view of how releases are advancing through the pipeline."""
    path: GetAllReleaseProgressionsForReleasePipelineRequestPath

# Operation: get_custom_role
class GetCustomRoleRequestPath(StrictModel):
    custom_role_key: str = Field(default=..., validation_alias="customRoleKey", serialization_alias="customRoleKey", description="The unique identifier for the custom role, specified as either the custom role key or its ID.", json_schema_extra={'format': 'string'})
class GetCustomRoleRequest(StrictModel):
    """Retrieve a single custom role by its unique key or ID. Use this to fetch detailed information about a specific custom role in your organization."""
    path: GetCustomRoleRequestPath

# Operation: update_custom_role
class PatchCustomRoleRequestPath(StrictModel):
    custom_role_key: str = Field(default=..., validation_alias="customRoleKey", serialization_alias="customRoleKey", description="The unique identifier key for the custom role to update.", json_schema_extra={'format': 'string'})
class PatchCustomRoleRequestBody(StrictModel):
    patch: list[PatchOperation] = Field(default=..., description="An array of JSON patch operations (RFC 6902) or JSON merge patch (RFC 7386) representing the changes to apply. To modify the policy array, use path `/policy` followed by an array index (`/0` for beginning, `/-` for end), or specify other role properties to update.")
class PatchCustomRoleRequest(StrictModel):
    """Update a custom role using JSON patch or JSON merge patch operations. Supports modifying role policies by specifying the desired changes as a patch document."""
    path: PatchCustomRoleRequestPath
    body: PatchCustomRoleRequestBody

# Operation: delete_custom_role
class DeleteCustomRoleRequestPath(StrictModel):
    custom_role_key: str = Field(default=..., validation_alias="customRoleKey", serialization_alias="customRoleKey", description="The unique identifier for the custom role to delete. This is a string value that uniquely identifies the role within the system.", json_schema_extra={'format': 'string'})
class DeleteCustomRoleRequest(StrictModel):
    """Permanently delete a custom role by its unique key. This action removes the role and any associated permissions from the system."""
    path: DeleteCustomRoleRequestPath

# Operation: list_segments
class GetSegmentsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segments.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project from which to retrieve segments.", json_schema_extra={'format': 'string'})
class GetSegmentsRequest(StrictModel):
    """Retrieve all segments in a project environment, including rule-based, list-based, and synced segments. Supports filtering by tags, keys, segment type, external sync status, and fuzzy search across segment metadata."""
    path: GetSegmentsRequestPath

# Operation: create_segment
class PostSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project where the segment will be created.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the segment will be created.", json_schema_extra={'format': 'string'})
class PostSegmentRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the segment that describes its purpose or audience.")
    key: str = Field(default=..., description="A unique identifier for the segment used in code and API references. Must be distinct within the project.")
    tags: list[str] | None = Field(default=None, description="Optional labels to organize and categorize the segment for easier management and filtering.")
    unbounded: bool | None = Field(default=None, description="Set to true to create a big segment for handling more than 15,000 individual targets; false for standard segments with rule-based or smaller list-based criteria.")
    unbounded_context_kind: str | None = Field(default=None, validation_alias="unboundedContextKind", serialization_alias="unboundedContextKind", description="For big segments, specifies the context kind (e.g., 'device', 'user') that the segment targets. Required when creating a big segment.")
class PostSegmentRequest(StrictModel):
    """Create a new segment in a LaunchDarkly project environment. Segments can be standard (rule-based or small list-based) or big segments (large list-based or synced) for targeting contexts."""
    path: PostSegmentRequestPath
    body: PostSegmentRequestBody

# Operation: get_segment
class GetSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the segment to retrieve.", json_schema_extra={'format': 'string'})
class GetSegmentRequest(StrictModel):
    """Retrieve a single segment by its key. Segments can be rule-based, list-based, or synced; big segments include larger list-based and synced segments with additional metadata fields."""
    path: GetSegmentRequestPath

# Operation: update_segment
class PatchSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the segment to update.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the segment exists.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key identifying which segment to update.", json_schema_extra={'format': 'string'})
class PatchSegmentRequestQuery(StrictModel):
    dry_run: bool | None = Field(default=None, validation_alias="dryRun", serialization_alias="dryRun", description="When true, validates the patch and returns a preview of the updated segment without persisting changes.")
class PatchSegmentRequestBody(StrictModel):
    patch: list[PatchOperation] = Field(default=..., description="The patch instructions as a JSON array. Use semantic patch (with `domain-model=launchdarkly.semanticpatch` header) for segment-specific operations like managing targets and rules, or standard JSON patch/merge patch for direct field modifications. Semantic patch requires `environmentKey` and `instructions` properties; JSON patch uses standard RFC 6902 operations.")
class PatchSegmentRequest(StrictModel):
    """Update a segment using semantic patch, JSON patch, or JSON merge patch. Supports modifications to segment metadata, targeting rules, individual targets, and big segment operations."""
    path: PatchSegmentRequestPath
    query: PatchSegmentRequestQuery | None = None
    body: PatchSegmentRequestBody

# Operation: delete_segment
class DeleteSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the segment to delete.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the segment exists.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the segment to delete.", json_schema_extra={'format': 'string'})
class DeleteSegmentRequest(StrictModel):
    """Permanently delete a segment from a specific project and environment. This action cannot be undone."""
    path: DeleteSegmentRequestPath

# Operation: update_big_segment_context_targets
class UpdateBigSegmentContextTargetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the LaunchDarkly project containing the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies the specific environment within the project.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key that uniquely identifies the big segment to update.", json_schema_extra={'format': 'string'})
class UpdateBigSegmentContextTargetsRequestBodyIncluded(StrictModel):
    add: list[str] | None = Field(default=None, validation_alias="add", serialization_alias="add", description="Array of context identifiers to add to the segment's included list. Order is not significant.")
    remove: list[str] | None = Field(default=None, validation_alias="remove", serialization_alias="remove", description="Array of context identifiers to remove from the segment's included list. Order is not significant.")
class UpdateBigSegmentContextTargetsRequestBodyExcluded(StrictModel):
    add: list[str] | None = Field(default=None, validation_alias="add", serialization_alias="add", description="Array of context identifiers to add to the segment's excluded list. Order is not significant.")
    remove: list[str] | None = Field(default=None, validation_alias="remove", serialization_alias="remove", description="Array of context identifiers to remove from the segment's excluded list. Order is not significant.")
class UpdateBigSegmentContextTargetsRequestBody(StrictModel):
    included: UpdateBigSegmentContextTargetsRequestBodyIncluded | None = None
    excluded: UpdateBigSegmentContextTargetsRequestBodyExcluded | None = None
class UpdateBigSegmentContextTargetsRequest(StrictModel):
    """Update which contexts are included in or excluded from a big segment. Big segments support larger list-based and synced segments, unlike standard segments which are not supported by this operation."""
    path: UpdateBigSegmentContextTargetsRequestPath
    body: UpdateBigSegmentContextTargetsRequestBody | None = None

# Operation: get_segment_membership_for_context
class GetSegmentMembershipForContextRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment to query for segment membership.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key that identifies the big segment to check membership against.", json_schema_extra={'format': 'string'})
    context_key: str = Field(default=..., validation_alias="contextKey", serialization_alias="contextKey", description="The context key that identifies the specific context whose membership status you want to retrieve.", json_schema_extra={'format': 'string'})
class GetSegmentMembershipForContextRequest(StrictModel):
    """Check whether a specific context is included or excluded from a big segment. Big segments support larger list-based and synced segments, but not standard segments."""
    path: GetSegmentMembershipForContextRequestPath

# Operation: create_big_segment_export
class CreateBigSegmentExportRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segment to export.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the segment exists.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the big segment to export.", json_schema_extra={'format': 'string'})
class CreateBigSegmentExportRequest(StrictModel):
    """Initiates an export process for a large segment (synced or list-based) containing more than 15,000 entries. The export runs asynchronously and can be monitored for completion status."""
    path: CreateBigSegmentExportRequestPath

# Operation: get_big_segment_export
class GetBigSegmentExportRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the segment is defined.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the segment being exported.", json_schema_extra={'format': 'string'})
    export_id: str = Field(default=..., validation_alias="exportID", serialization_alias="exportID", description="The unique identifier for the specific export process to retrieve information about.", json_schema_extra={'format': 'string'})
class GetBigSegmentExportRequest(StrictModel):
    """Retrieve the status and details of a big segment export process for a synced or list-based segment containing more than 15,000 entries."""
    path: GetBigSegmentExportRequestPath

# Operation: create_big_segment_import
class CreateBigSegmentImportRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the big segment to import data into.", json_schema_extra={'format': 'string'})
class CreateBigSegmentImportRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="A CSV file containing the segment keys to import. Each row should contain one key entry.", json_schema_extra={'format': 'binary'})
    mode: str | None = Field(default=None, description="The import strategy: use `merge` to add new entries while preserving existing ones, or `replace` to overwrite all existing entries with the imported data.", json_schema_extra={'format': 'string'})
    wait_on_approvals: bool | None = Field(default=None, validation_alias="waitOnApprovals", serialization_alias="waitOnApprovals", description="If true, the import process will pause and wait for any required approvals before processing the data.")
class CreateBigSegmentImportRequest(StrictModel):
    """Initiate an import process for a big segment to add or replace list-based segment entries. This operation supports importing large datasets with more than 15,000 entries from a CSV file."""
    path: CreateBigSegmentImportRequestPath
    body: CreateBigSegmentImportRequestBody | None = None

# Operation: get_big_segment_import
class GetBigSegmentImportRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the segment being imported.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment contains the segment being imported.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key that identifies the specific big segment associated with this import.", json_schema_extra={'format': 'string'})
    import_id: str = Field(default=..., validation_alias="importID", serialization_alias="importID", description="The import ID that uniquely identifies the specific import process to retrieve status and details for.", json_schema_extra={'format': 'string'})
class GetBigSegmentImportRequest(StrictModel):
    """Retrieve detailed information about an in-progress or completed big segment import process. Big segments support list-based imports with more than 15,000 entries."""
    path: GetBigSegmentImportRequestPath

# Operation: update_big_segment_user_targets
class UpdateBigSegmentTargetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project contains the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment the segment belongs to.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key that uniquely identifies the big segment to update.", json_schema_extra={'format': 'string'})
class UpdateBigSegmentTargetsRequestBodyIncluded(StrictModel):
    add: list[str] | None = Field(default=None, validation_alias="add", serialization_alias="add", description="Array of user context identifiers to add to the segment's included targets. Order is not significant.")
    remove: list[str] | None = Field(default=None, validation_alias="remove", serialization_alias="remove", description="Array of user context identifiers to remove from the segment's included targets. Order is not significant.")
class UpdateBigSegmentTargetsRequestBodyExcluded(StrictModel):
    add: list[str] | None = Field(default=None, validation_alias="add", serialization_alias="add", description="Array of user context identifiers to add to the segment's excluded targets. Order is not significant.")
    remove: list[str] | None = Field(default=None, validation_alias="remove", serialization_alias="remove", description="Array of user context identifiers to remove from the segment's excluded targets. Order is not significant.")
class UpdateBigSegmentTargetsRequestBody(StrictModel):
    included: UpdateBigSegmentTargetsRequestBodyIncluded | None = None
    excluded: UpdateBigSegmentTargetsRequestBodyExcluded | None = None
class UpdateBigSegmentTargetsRequest(StrictModel):
    """Modify user context targets included or excluded in a big segment. Use this operation to add or remove users from list-based or synced segments, which support larger audiences than standard segments."""
    path: UpdateBigSegmentTargetsRequestPath
    body: UpdateBigSegmentTargetsRequestBody | None = None

# Operation: get_user_segment_membership
class GetSegmentMembershipForUserRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the segment membership is evaluated.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The big segment key to check membership for.", json_schema_extra={'format': 'string'})
    user_key: str = Field(default=..., validation_alias="userKey", serialization_alias="userKey", description="The user key to check for membership in the segment.", json_schema_extra={'format': 'string'})
class GetSegmentMembershipForUserRequest(StrictModel):
    """Check whether a user is included or excluded from a big segment. This operation only works with big segments, not standard segments."""
    path: GetSegmentMembershipForUserRequestPath

# Operation: list_expiring_targets_for_segment
class GetExpiringTargetsForSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment where the segment's expiring targets are managed.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the segment whose expiring context targets you want to retrieve.", json_schema_extra={'format': 'string'})
class GetExpiringTargetsForSegmentRequest(StrictModel):
    """Retrieve a list of context targets within a segment that are scheduled for removal. This helps identify which targets will be automatically deleted from the segment."""
    path: GetExpiringTargetsForSegmentRequestPath

# Operation: update_segment_expiring_targets
class PatchExpiringTargetsForSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the segment. Used to identify which project's segment configuration to modify.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the segment targeting applies. Specifies which environment's segment expiration rules to update.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key identifying which segment's expiring targets to modify.", json_schema_extra={'format': 'string'})
class PatchExpiringTargetsForSegmentRequestBody(StrictModel):
    instructions: list[PatchSegmentExpiringTargetInstruction] = Field(default=..., description="Array of semantic patch instructions defining the changes to apply. Each instruction must specify a kind (addExpiringTarget, updateExpiringTarget, or removeExpiringTarget), the target type (included or excluded), context key, context kind, and for add/update operations, an expiration timestamp in Unix milliseconds. Instructions are processed sequentially and partial failures return status 200 with errors listed in the response.")
class PatchExpiringTargetsForSegmentRequest(StrictModel):
    """Schedule or modify expiration dates for context targets within a segment using semantic patch instructions. Supports adding, updating, or removing scheduled expirations for included or excluded contexts."""
    path: PatchExpiringTargetsForSegmentRequestPath
    body: PatchExpiringTargetsForSegmentRequestBody

# Operation: list_expiring_user_targets_for_segment
class GetExpiringUserTargetsForSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the segment.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project where the segment is defined.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique identifier for the segment whose expiring user targets should be retrieved.", json_schema_extra={'format': 'string'})
class GetExpiringUserTargetsForSegmentRequest(StrictModel):
    """Retrieve a list of user targets scheduled for removal from a specific segment. Note: This endpoint is deprecated; use list_expiring_targets_for_segment instead after upgrading to context-based SDKs."""
    path: GetExpiringUserTargetsForSegmentRequestPath

# Operation: update_expiring_user_targets_for_segment
class PatchExpiringUserTargetsForSegmentRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the segment. Used to identify which project's segment to update.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key where the segment targeting applies. Specifies which environment's user targets should be modified.", json_schema_extra={'format': 'string'})
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key identifying which segment's user target expirations to update.", json_schema_extra={'format': 'string'})
class PatchExpiringUserTargetsForSegmentRequestBody(StrictModel):
    instructions: list[PatchSegmentInstruction] = Field(default=..., description="Array of semantic patch instructions defining the changes to apply. Each instruction must specify a kind (addExpireUserTargetDate, updateExpireUserTargetDate, or removeExpireUserTargetDate), targetType (included or excluded), userKey, and optionally a value (Unix milliseconds for expiration date) or version number. Instructions are processed in order.")
class PatchExpiringUserTargetsForSegmentRequest(StrictModel):
    """Update expiration dates for users targeted in a segment using semantic patch instructions. This endpoint manages when LaunchDarkly will automatically remove users from segment targeting."""
    path: PatchExpiringUserTargetsForSegmentRequestPath
    body: PatchExpiringUserTargetsForSegmentRequestBody

# Operation: create_team
class PostTeamRequestBody(StrictModel):
    custom_role_keys: list[str] | None = Field(default=None, validation_alias="customRoleKeys", serialization_alias="customRoleKeys", description="List of custom role keys to assign to the team, granting access to those roles. Provide as an array of role key strings.")
    key: str = Field(default=..., description="Unique identifier for the team. Used to reference the team in API calls and must be URL-safe.")
    member_i_ds: list[str] | None = Field(default=None, validation_alias="memberIDs", serialization_alias="memberIDs", description="Array of member IDs to add to the team upon creation. Each ID should be a valid LaunchDarkly member identifier.")
    name: str = Field(default=..., description="Human-readable name for the team. This is displayed in the LaunchDarkly UI and should be descriptive.")
    permission_grants: list[PermissionGrantInput] | None = Field(default=None, validation_alias="permissionGrants", serialization_alias="permissionGrants", description="Array of permission grants that define specific actions the team can perform without requiring a custom role. Each grant specifies an action and resource scope.")
    role_attributes: dict[str, RoleAttributeValues] | None = Field(default=None, validation_alias="roleAttributes", serialization_alias="roleAttributes", description="Object containing role attributes as key-value pairs. Attributes provide additional context or metadata for the team's roles.")
class PostTeamRequest(StrictModel):
    """Create a new team in LaunchDarkly with optional members, custom roles, and permission grants. Supports expanding the response to include members, roles, projects, and maintainers."""
    body: PostTeamRequestBody

# Operation: get_team
class GetTeamRequestPath(StrictModel):
    team_key: str = Field(default=..., validation_alias="teamKey", serialization_alias="teamKey", description="The unique identifier for the team. Use this key to fetch the specific team's details.", json_schema_extra={'format': 'string'})
class GetTeamRequest(StrictModel):
    """Retrieve a team by its unique key. Optionally expand the response to include members, roles, role attributes, projects, or maintainers."""
    path: GetTeamRequestPath

# Operation: update_team
class PatchTeamRequestPath(StrictModel):
    team_key: str = Field(default=..., validation_alias="teamKey", serialization_alias="teamKey", description="The unique identifier for the team to update. Use the team key value returned from team listing operations.", json_schema_extra={'format': 'string'})
class PatchTeamRequestBody(StrictModel):
    instructions: list[Instruction] = Field(default=..., description="An array of semantic patch instruction objects that specify the updates to apply. Each instruction object must include a `kind` field indicating the operation type (e.g., addMembers, updateName, removeCustomRoles) and any required parameters for that operation. Multiple instructions are processed sequentially.")
class PatchTeamRequest(StrictModel):
    """Perform a partial update to a team using semantic patch instructions. Supports operations like adding/removing members, updating team metadata, managing custom roles, and configuring permission grants."""
    path: PatchTeamRequestPath
    body: PatchTeamRequestBody

# Operation: delete_team
class DeleteTeamRequestPath(StrictModel):
    team_key: str = Field(default=..., validation_alias="teamKey", serialization_alias="teamKey", description="The unique identifier for the team to delete. This is a string value that uniquely identifies the team within your LaunchDarkly organization.", json_schema_extra={'format': 'string'})
class DeleteTeamRequest(StrictModel):
    """Permanently delete a team by its key. This action cannot be undone and will remove the team from your LaunchDarkly account."""
    path: DeleteTeamRequestPath

# Operation: list_team_maintainers
class GetTeamMaintainersRequestPath(StrictModel):
    team_key: str = Field(default=..., validation_alias="teamKey", serialization_alias="teamKey", description="The unique identifier for the team whose maintainers you want to retrieve.", json_schema_extra={'format': 'string'})
class GetTeamMaintainersRequest(StrictModel):
    """Retrieve the list of maintainers assigned to a specific team. Maintainers have elevated permissions to manage team settings and members."""
    path: GetTeamMaintainersRequestPath

# Operation: add_members_to_team
class PostTeamMembersRequestPath(StrictModel):
    team_key: str = Field(default=..., validation_alias="teamKey", serialization_alias="teamKey", description="The unique identifier for the team. Used to route the request to the correct team.", json_schema_extra={'format': 'string'})
class PostTeamMembersRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="A CSV file containing email addresses in the first column (headers optional). LaunchDarkly ignores additional columns. File must not exceed 25MB and must contain at least one valid email address belonging to a LaunchDarkly organization member.", json_schema_extra={'format': 'binary'})
class PostTeamMembersRequest(StrictModel):
    """Add multiple team members to an existing team by uploading a CSV file containing email addresses. The operation validates all entries before adding any members—a single invalid entry prevents all additions."""
    path: PostTeamMembersRequestPath
    body: PostTeamMembersRequestBody | None = None

# Operation: list_team_roles
class GetTeamRolesRequestPath(StrictModel):
    team_key: str = Field(default=..., validation_alias="teamKey", serialization_alias="teamKey", description="The unique identifier for the team whose roles you want to retrieve.", json_schema_extra={'format': 'string'})
class GetTeamRolesRequest(StrictModel):
    """Retrieve all custom roles assigned to a specific team. Custom roles define granular permissions for team members within LaunchDarkly."""
    path: GetTeamRolesRequestPath

# Operation: list_workflow_templates
class GetWorkflowTemplatesRequestQuery(StrictModel):
    summary: bool | None = Field(default=None, description="Return lightweight template summaries instead of full template objects. When true, returns only essential metadata; when false or omitted, returns complete template details.")
    search: str | None = Field(default=None, description="Filter templates by searching for a substring within template names or descriptions. The search is case-sensitive and matches partial strings.", json_schema_extra={'format': 'string'})
class GetWorkflowTemplatesRequest(StrictModel):
    """Retrieve workflow templates for your account with optional filtering and summary mode. Use the summary parameter to get lightweight template metadata or the search parameter to filter templates by name or description."""
    query: GetWorkflowTemplatesRequestQuery | None = None

# Operation: get_token
class GetTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the access token to retrieve.", json_schema_extra={'format': 'string'})
class GetTokenRequest(StrictModel):
    """Retrieve a single access token by its unique identifier. Use this to fetch details about a specific token for inspection or validation purposes."""
    path: GetTokenRequestPath

# Operation: update_token
class PatchTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the access token to update.", json_schema_extra={'format': 'string'})
class PatchTokenRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include 'op' (the operation type), 'path' (the token property to modify), and 'value' (the new value for replace operations). Operations are applied in order.", examples=[[{'op': 'replace', 'path': '/role', 'value': 'writer'}]])
class PatchTokenRequest(StrictModel):
    """Update an access token's settings using JSON Patch operations. Specify the changes you want to make (such as modifying the role) in RFC 6902 patch format."""
    path: PatchTokenRequestPath
    body: PatchTokenRequestBody

# Operation: delete_token
class DeleteTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the access token to delete. This is a string value that uniquely identifies the token in the system.", json_schema_extra={'format': 'string'})
class DeleteTokenRequest(StrictModel):
    """Permanently delete an access token by its ID. This operation removes the token immediately, invalidating any authentication attempts using it."""
    path: DeleteTokenRequestPath

# Operation: reset_token
class ResetTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the access token to reset.", json_schema_extra={'format': 'string'})
class ResetTokenRequestQuery(StrictModel):
    expiry: int | None = Field(default=None, description="Optional Unix epoch time in milliseconds when the old token key should expire. If not provided, the old key expires immediately upon reset.", json_schema_extra={'format': 'int64'})
class ResetTokenRequest(StrictModel):
    """Generate a new secret key for an access token, optionally setting an expiration time for the old key. Use this to rotate credentials while maintaining token validity."""
    path: ResetTokenRequestPath
    query: ResetTokenRequestQuery | None = None

# Operation: get_events_usage_by_type
class GetEventsUsageRequestPath(StrictModel):
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The event category to retrieve usage data for. Must be either 'received' (events received by the system) or 'published' (events published by the system).", json_schema_extra={'format': 'string'})
class GetEventsUsageRequestQuery(StrictModel):
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="ISO 8601 timestamp marking the start of the requested data range. If not provided, defaults to 24 hours before the 'to' timestamp.", json_schema_extra={'format': 'string'})
    to: str | None = Field(default=None, description="ISO 8601 timestamp marking the end of the requested data range. If not provided, defaults to the current time.", json_schema_extra={'format': 'string'})
class GetEventsUsageRequest(StrictModel):
    """Retrieve time-series data showing how many times a flag was evaluated and which variation resulted from each evaluation. Data granularity automatically adjusts based on age: minutely for the past 2 hours, hourly for the past 2 days, and daily for older data."""
    path: GetEventsUsageRequestPath
    query: GetEventsUsageRequestQuery | None = None

# Operation: get_webhook
class GetWebhookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook to retrieve.", json_schema_extra={'format': 'string'})
class GetWebhookRequest(StrictModel):
    """Retrieve a single webhook by its unique identifier. Use this to fetch detailed information about a specific webhook configuration."""
    path: GetWebhookRequestPath

# Operation: update_webhook
class PatchWebhookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook to update.", json_schema_extra={'format': 'string'})
class PatchWebhookRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations describing the changes to apply. Each operation must include an 'op' field (e.g., 'replace'), a 'path' field indicating which property to modify, and a 'value' field with the new value.", examples=[[{'op': 'replace', 'path': '/on', 'value': False}]])
class PatchWebhookRequest(StrictModel):
    """Update a webhook's configuration using JSON Patch operations. Specify the changes you want to make (such as enabling/disabling the webhook) as an array of patch operations."""
    path: PatchWebhookRequestPath
    body: PatchWebhookRequestBody

# Operation: delete_webhook
class DeleteWebhookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook to delete. This is a string value that uniquely identifies the webhook in the system.", json_schema_extra={'format': 'string'})
class DeleteWebhookRequest(StrictModel):
    """Permanently delete a webhook by its ID. This action cannot be undone and will stop all event notifications from being sent to the webhook's configured endpoint."""
    path: DeleteWebhookRequestPath

# Operation: list_tags
class GetTagsRequestQuery(StrictModel):
    kind: list[str] | None = Field(default=None, description="Filter tags by resource type. Accepts multiple types including flag, project, environment, segment, metric, metric-data-source, aiconfig, and view. If not specified, returns tags of all types.")
    pre: str | None = Field(default=None, description="Return only tags that begin with the specified prefix string.")
    archived: bool | None = Field(default=None, description="Include or exclude archived tags in the results. When true, returns archived tags; when false or omitted, returns only active tags.")
    as_of: str | None = Field(default=None, validation_alias="asOf", serialization_alias="asOf", description="Retrieve tags as they existed at a specific point in time, specified in ISO 8601 format. Defaults to the current time if not provided.")
class GetTagsRequest(StrictModel):
    """Retrieve a list of tags, optionally filtered by resource type, prefix, or archived status, and as of a specific point in time."""
    query: GetTagsRequestQuery | None = None

# Operation: get_ai_config_targeting
class GetAiConfigTargetingRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config whose targeting configuration should be retrieved.")
class GetAiConfigTargetingRequest(StrictModel):
    """Retrieve the targeting configuration for a specific AI Config. Returns the targeting rules and criteria that determine which users or contexts this AI Config applies to."""
    path: GetAiConfigTargetingRequestPath

# Operation: update_ai_config_targeting
class PatchAiConfigTargetingRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the LaunchDarkly project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config to update.")
class PatchAiConfigTargetingRequestBody(StrictModel):
    """AI Config targeting semantic patch instructions"""
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the LaunchDarkly environment where the AI Config targeting applies.")
    instructions: list[dict[str, Any]] = Field(default=..., description="An array of semantic patch instructions that define the targeting changes to apply. Each instruction must include a `kind` property specifying the operation type (e.g., addRule, addClauses, removeTargets) and relevant parameters for that operation. Instructions are processed in order.")
class PatchAiConfigTargetingRequest(StrictModel):
    """Update an AI Config's targeting rules, variations, and rollouts using semantic patch instructions. Supports adding/removing rules and clauses, managing individual context targets, and configuring percentage-based rollouts."""
    path: PatchAiConfigTargetingRequestPath
    body: PatchAiConfigTargetingRequestBody

# Operation: list_ai_configs
class GetAiConfigsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project. Use the project key (e.g., 'default') to specify which project's AI Configs to retrieve.")
class GetAiConfigsRequest(StrictModel):
    """Retrieve all AI Configs available in a specified project. Returns a list of AI configuration objects that define AI behavior and settings for the project."""
    path: GetAiConfigsRequestPath

# Operation: create_ai_config
class PostAiConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project where the AI Config will be created.")
class PostAiConfigRequestBodyDefaultVariationJudgeConfiguration(StrictModel):
    judges: list[JudgeAttachment] | None = Field(default=None, validation_alias="judges", serialization_alias="judges", description="Optional array of judges attached to this variation for evaluation purposes. When provided, this replaces all existing judge attachments; an empty array removes all judges.")
class PostAiConfigRequestBodyDefaultVariation(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="A unique identifier for the default variation of this AI Config.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the default variation.")
    instructions: str | None = Field(default=None, validation_alias="instructions", serialization_alias="instructions", description="Instructions for agent behavior. Only applicable and returned when the mode is set to 'agent'.")
    messages: list[Message] | None = Field(default=None, validation_alias="messages", serialization_alias="messages", description="Optional array of messages that define the conversation context or system prompts for the AI Config.")
    model_config_key: str | None = Field(default=None, validation_alias="modelConfigKey", serialization_alias="modelConfigKey", description="Optional reference to a model configuration key that specifies the underlying model settings and parameters.")
    judge_configuration: PostAiConfigRequestBodyDefaultVariationJudgeConfiguration | None = Field(default=None, validation_alias="judgeConfiguration", serialization_alias="judgeConfiguration")
class PostAiConfigRequestBody(StrictModel):
    """AI Config object to create"""
    description: str | None = Field(default=None, description="Optional description of the AI Config to provide context about its purpose and usage.")
    key: str = Field(default=..., description="A unique identifier for the AI Config within the project, used for referencing and management.")
    mode: Literal["agent", "completion", "judge"] | None = Field(default=None, description="The operational mode of the AI Config. Choose 'completion' for standard text generation, 'agent' for agentic behavior with instructions, or 'judge' for evaluation purposes. Defaults to 'completion'.")
    name: str = Field(default=..., description="The display name of the AI Config.")
    tags: list[str] | None = Field(default=None, description="Optional array of tags for categorizing and organizing the AI Config.")
    evaluation_metric_key: str | None = Field(default=None, validation_alias="evaluationMetricKey", serialization_alias="evaluationMetricKey", description="Optional key referencing an evaluation metric to assess the performance of this AI Config.")
    is_inverted: bool | None = Field(default=None, validation_alias="isInverted", serialization_alias="isInverted", description="Optional boolean flag indicating whether the evaluation metric is inverted, meaning lower values indicate better performance when set to true.")
    default_variation: PostAiConfigRequestBodyDefaultVariation = Field(default=..., validation_alias="defaultVariation", serialization_alias="defaultVariation")
class PostAiConfigRequest(StrictModel):
    """Create a new AI Config within a project to define AI model behavior, variations, and evaluation criteria. Supports multiple modes (completion, agent, or judge) with customizable instructions, messages, and evaluation metrics."""
    path: PostAiConfigRequestPath
    body: PostAiConfigRequestBody

# Operation: get_ai_config
class GetAiConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI configuration.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the specific AI configuration to retrieve.")
class GetAiConfigRequest(StrictModel):
    """Retrieve a specific AI configuration by its project and configuration keys. Use this to fetch detailed settings and properties for a particular AI config within a project."""
    path: GetAiConfigRequestPath

# Operation: update_ai_config
class PatchAiConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config to update.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config to update.")
class PatchAiConfigRequestBody(StrictModel):
    """AI Config object to update"""
    name: str | None = Field(default=None, description="The new name for the AI Config.")
    tags: list[str] | None = Field(default=None, description="A list of tags to associate with the AI Config. Tags are used for organization and filtering.")
    evaluation_metric_key: str | None = Field(default=None, validation_alias="evaluationMetricKey", serialization_alias="evaluationMetricKey", description="The unique identifier of the evaluation metric to use for assessing this AI Config's performance.")
    is_inverted: bool | None = Field(default=None, validation_alias="isInverted", serialization_alias="isInverted", description="Set to true if the evaluation metric is inverted, meaning lower values indicate better performance. Set to false if higher values are better.")
class PatchAiConfigRequest(StrictModel):
    """Update an existing AI Config by modifying specific fields. Only the fields included in the request body will be updated; other fields remain unchanged."""
    path: PatchAiConfigRequestPath
    body: PatchAiConfigRequestBody | None = None

# Operation: delete_ai_config
class DeleteAiConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the AI Config. Use 'default' for the default project or specify a custom project key.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier of the AI Config to delete.")
class DeleteAiConfigRequest(StrictModel):
    """Permanently delete an AI Config from a project. This operation removes the configuration and cannot be undone."""
    path: DeleteAiConfigRequestPath

# Operation: create_ai_config_variation
class PostAiConfigVariationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier of the AI Config for which to create a variation.")
class PostAiConfigVariationRequestBodyJudgeConfiguration(StrictModel):
    judges: list[JudgeAttachment] | None = Field(default=None, validation_alias="judges", serialization_alias="judges", description="List of judge configurations for evaluating this variation. When provided, replaces all existing judges; an empty array removes all judge attachments.")
class PostAiConfigVariationRequestBody(StrictModel):
    """AI Config variation object to create"""
    instructions: str | None = Field(default=None, description="Instructions for the agent behavior. Only applicable and returned for agent-type variations.")
    key: str = Field(default=..., description="The unique identifier for this variation within the AI Config.")
    messages: list[Message] | None = Field(default=None, description="Array of message objects defining the conversation or prompt structure for this variation. Order and format depend on the model type.")
    name: str = Field(default=..., description="A human-readable name for this variation to distinguish it from other variations of the same AI Config.")
    model_config_key: str | None = Field(default=None, validation_alias="modelConfigKey", serialization_alias="modelConfigKey", description="Optional reference to a model configuration key. If provided, uses a predefined model configuration; otherwise, model details must be specified in the request body.")
    judge_configuration: PostAiConfigVariationRequestBodyJudgeConfiguration | None = Field(default=None, validation_alias="judgeConfiguration", serialization_alias="judgeConfiguration")
class PostAiConfigVariationRequest(StrictModel):
    """Create a new variation for an AI Config, specifying model configuration, instructions, and optional judges for evaluation."""
    path: PostAiConfigVariationRequestPath
    body: PostAiConfigVariationRequestBody

# Operation: get_ai_config_variation
class GetAiConfigVariationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config. Use 'default' for the default project.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config within the project. Use 'default' for the default configuration.")
    variation_key: str = Field(default=..., validation_alias="variationKey", serialization_alias="variationKey", description="The unique identifier for the specific variation within the AI Config. Use 'default' for the default variation.")
class GetAiConfigVariationRequest(StrictModel):
    """Retrieve a specific AI Config variation by its key, including all versions associated with that variation."""
    path: GetAiConfigVariationRequestPath

# Operation: update_ai_config_variation
class PatchAiConfigVariationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config containing the variation to update.")
    variation_key: str = Field(default=..., validation_alias="variationKey", serialization_alias="variationKey", description="The unique identifier for the variation to update.")
class PatchAiConfigVariationRequestBodyJudgeConfiguration(StrictModel):
    judges: list[JudgeAttachment] | None = Field(default=None, validation_alias="judges", serialization_alias="judges", description="Array of judge objects that evaluate this variation's performance. Replaces all existing judges; provide an empty array to remove all judge attachments.")
class PatchAiConfigVariationRequestBody(StrictModel):
    """AI Config variation object to update"""
    instructions: str | None = Field(default=None, description="Instructions that guide the agent's behavior when this AI Config operates in agent mode.")
    messages: list[Message] | None = Field(default=None, description="Array of message objects defining the conversation structure. Each message has a role (e.g., 'system', 'user', 'assistant') and content text. Order matters and represents the conversation sequence.")
    model_config_key: str | None = Field(default=None, validation_alias="modelConfigKey", serialization_alias="modelConfigKey", description="The unique identifier for the model configuration to use with this variation.")
    name: str | None = Field(default=None, description="A human-readable name for this variation.")
    state: str | None = Field(default=None, description="The lifecycle state of the variation. Must be either 'archived' to hide the variation or 'published' to make it active.")
    judge_configuration: PatchAiConfigVariationRequestBodyJudgeConfiguration | None = Field(default=None, validation_alias="judgeConfiguration", serialization_alias="judgeConfiguration")
class PatchAiConfigVariationRequest(StrictModel):
    """Update an existing AI Config variation by modifying its properties. Changes create a new version of the variation while preserving the original."""
    path: PatchAiConfigVariationRequestPath
    body: PatchAiConfigVariationRequestBody | None = None

# Operation: delete_ai_config_variation
class DeleteAiConfigVariationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config whose variation should be deleted.")
    variation_key: str = Field(default=..., validation_alias="variationKey", serialization_alias="variationKey", description="The unique identifier for the specific variation to delete.")
class DeleteAiConfigVariationRequest(StrictModel):
    """Permanently delete a specific variation of an AI Config. This removes the variation and all its associated data from the project."""
    path: DeleteAiConfigVariationRequestPath

# Operation: get_ai_config_quick_stats
class GetAiConfigQuickStatsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Configs. This key determines which project's statistics will be retrieved.")
class GetAiConfigQuickStatsRequestQuery(StrictModel):
    env: str = Field(default=..., description="The environment key that filters which metrics are included in the results. Only statistics from this specific environment will be returned.")
class GetAiConfigQuickStatsRequest(StrictModel):
    """Retrieve aggregate quick statistics for AI Configs within a specific project and environment. Returns metrics summarizing AI Config usage and performance for the specified environment."""
    path: GetAiConfigQuickStatsRequestPath
    query: GetAiConfigQuickStatsRequestQuery

# Operation: get_ai_config_metrics
class GetAiConfigMetricsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config whose metrics should be retrieved.")
class GetAiConfigMetricsRequestQuery(StrictModel):
    from_: int = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the metrics time range as milliseconds since epoch (inclusive). Use this to define the beginning of your analysis period.")
    to: int = Field(default=..., description="The end of the metrics time range as milliseconds since epoch (exclusive). The time range between `from` and `to` cannot exceed 100 days.")
    env: str = Field(default=..., description="The environment key to filter metrics by. Only metrics collected in this specific environment will be included in the results.")
class GetAiConfigMetricsRequest(StrictModel):
    """Retrieve usage and performance metrics for a specific AI Config within a defined time range and environment. Metrics are aggregated for the specified period to help monitor AI Config performance and usage patterns."""
    path: GetAiConfigMetricsRequestPath
    query: GetAiConfigMetricsRequestQuery

# Operation: get_ai_config_metrics_by_variation
class GetAiConfigMetricsByVariationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI Config.")
    config_key: str = Field(default=..., validation_alias="configKey", serialization_alias="configKey", description="The unique identifier for the AI Config whose metrics you want to retrieve.")
class GetAiConfigMetricsByVariationRequestQuery(StrictModel):
    from_: int = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the time range for metrics, specified as milliseconds since epoch (inclusive).")
    to: int = Field(default=..., description="The end of the time range for metrics, specified as milliseconds since epoch (exclusive). The time range cannot span more than 100 days.")
    env: str = Field(default=..., description="The environment key to filter metrics. Only metrics from this specific environment will be included in the results.")
class GetAiConfigMetricsByVariationRequest(StrictModel):
    """Retrieve usage and performance metrics for an AI Config segmented by variation. Results are filtered to a specific time range and environment."""
    path: GetAiConfigMetricsByVariationRequestPath
    query: GetAiConfigMetricsByVariationRequestQuery

# Operation: add_restricted_models
class PostRestrictedModelsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project's restricted model list to update. Use the project key from your LaunchDarkly workspace (e.g., 'default').")
class PostRestrictedModelsRequestBody(StrictModel):
    """List of AI model keys to add to the restricted list."""
    keys: list[str] = Field(default=..., description="An array of AI model keys to add to the restricted list. Each key must be a valid model key returned by the List AI model configs endpoint. Duplicate keys in the array will be deduplicated.")
class PostRestrictedModelsRequest(StrictModel):
    """Add one or more AI models to the restricted list for a project. Restricted models cannot be used in AI configurations for that project. Model keys are obtained from the List AI model configs endpoint."""
    path: PostRestrictedModelsRequestPath
    body: PostRestrictedModelsRequestBody

# Operation: remove_restricted_models
class DeleteRestrictedModelsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project identifier (e.g., 'default') that contains the restricted model list to modify.")
class DeleteRestrictedModelsRequestBody(StrictModel):
    """List of AI model keys to remove from the restricted list"""
    keys: list[str] = Field(default=..., description="An array of model keys to remove from the restricted list. Each key identifies a specific model to unrestrict.")
class DeleteRestrictedModelsRequest(StrictModel):
    """Remove one or more AI models from the project's restricted list by their keys. This allows previously restricted models to be used again in the project."""
    path: DeleteRestrictedModelsRequestPath
    body: DeleteRestrictedModelsRequestBody

# Operation: list_model_configs
class ListModelConfigsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project (e.g., 'default'). This determines which project's model configurations are returned.")
class ListModelConfigsRequestQuery(StrictModel):
    restricted: bool | None = Field(default=None, description="When set to true, returns only model configurations that are restricted. Omit or set to false to return all configurations.")
class ListModelConfigsRequest(StrictModel):
    """Retrieve all AI model configurations for a specified project. Optionally filter to show only restricted models."""
    path: ListModelConfigsRequestPath
    query: ListModelConfigsRequestQuery | None = None

# Operation: create_model_config
class PostModelConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project identifier where this model configuration will be created (e.g., 'default').")
class PostModelConfigRequestBody(StrictModel):
    """AI model config object to create"""
    name: str = Field(default=..., description="A human-readable display name for the model that will appear in the UI.")
    key: str = Field(default=..., description="A unique identifier key for this model configuration within the project, used for internal references and API calls.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The model identifier recognized by the third-party provider (e.g., 'gpt-4', 'claude-3-opus'). This is the identifier sent to the provider's API.")
    icon: str | None = Field(default=None, description="An optional icon identifier or URL to visually represent this model in the UI.")
    provider: str | None = Field(default=None, description="The AI service provider for this model (e.g., 'openai', 'anthropic', 'google'). Determines how requests are routed and authenticated.")
    params: dict[str, Any] | None = Field(default=None, description="Optional object containing provider-specific parameters and configuration settings for this model.")
    custom_params: dict[str, Any] | None = Field(default=None, validation_alias="customParams", serialization_alias="customParams", description="Optional object for custom parameters specific to your implementation or use case.")
    tags: list[str] | None = Field(default=None, description="Optional array of tags for categorizing and organizing this model configuration.")
    cost_per_input_token: float | None = Field(default=None, validation_alias="costPerInputToken", serialization_alias="costPerInputToken", description="The cost in USD per input token for this model, used for tracking and billing calculations.", json_schema_extra={'format': 'double'})
    cost_per_output_token: float | None = Field(default=None, validation_alias="costPerOutputToken", serialization_alias="costPerOutputToken", description="The cost in USD per output token for this model, used for tracking and billing calculations.", json_schema_extra={'format': 'double'})
class PostModelConfigRequest(StrictModel):
    """Create a new AI model configuration for your project. This configuration defines model identity, provider details, and cost metrics for use across AI features in your project."""
    path: PostModelConfigRequestPath
    body: PostModelConfigRequestBody

# Operation: get_model_config
class GetModelConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the model configuration. Typically 'default' for standard projects.")
    model_config_key: str = Field(default=..., validation_alias="modelConfigKey", serialization_alias="modelConfigKey", description="The unique identifier for the AI model configuration to retrieve. Typically 'default' for the standard model configuration.")
class GetModelConfigRequest(StrictModel):
    """Retrieve a specific AI model configuration by its unique key within a project. Use this to fetch detailed settings and parameters for a configured AI model."""
    path: GetModelConfigRequestPath

# Operation: delete_model_config
class DeleteModelConfigRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the model config. Use 'default' for the default project or specify a custom project key.")
    model_config_key: str = Field(default=..., validation_alias="modelConfigKey", serialization_alias="modelConfigKey", description="The unique identifier of the AI model configuration to delete.")
class DeleteModelConfigRequest(StrictModel):
    """Permanently delete an AI model configuration from a project. This operation removes the specified model config and cannot be undone."""
    path: DeleteModelConfigRequestPath

# Operation: list_ai_tools
class ListAiToolsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the AI tools to retrieve.")
class ListAiToolsRequest(StrictModel):
    """Retrieve all AI tools available in a specific project. Returns a complete list of configured AI tools that can be used within the project."""
    path: ListAiToolsRequestPath

# Operation: create_ai_tool
class PostAiToolRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project where the AI tool will be created.")
class PostAiToolRequestBody(StrictModel):
    """AI tool object to create"""
    key: str = Field(default=..., description="The unique identifier for the AI tool within the project. Used to reference this tool in subsequent operations.")
    schema_: dict[str, Any] = Field(default=..., validation_alias="schema", serialization_alias="schema", description="A JSON Schema object that defines the tool's input parameters and their constraints. This schema is sent to the LLM to describe what inputs the tool accepts and how to invoke it.")
    custom_parameters: dict[str, Any] | None = Field(default=None, validation_alias="customParameters", serialization_alias="customParameters", description="Optional object containing custom metadata and configuration settings for application-level use. These values are not exposed to the LLM and are used only by your application logic.")
class PostAiToolRequest(StrictModel):
    """Create a new AI tool within a project that defines custom functionality for LLM consumption. The tool's parameters are specified via JSON Schema, with optional custom metadata for application-level configuration."""
    path: PostAiToolRequestPath
    body: PostAiToolRequestBody

# Operation: list_ai_tool_versions
class ListAiToolVersionsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the AI tool.")
    tool_key: str = Field(default=..., validation_alias="toolKey", serialization_alias="toolKey", description="The unique identifier of the AI tool for which to retrieve versions.")
class ListAiToolVersionsRequest(StrictModel):
    """Retrieve all versions of a specific AI tool within a project. Returns a list of version records for the identified tool."""
    path: ListAiToolVersionsRequestPath

# Operation: get_ai_tool
class GetAiToolRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI tool.")
    tool_key: str = Field(default=..., validation_alias="toolKey", serialization_alias="toolKey", description="The unique identifier for the AI tool to retrieve.")
class GetAiToolRequest(StrictModel):
    """Retrieve a specific AI tool by its project and tool identifiers. Use this operation to fetch detailed information about a configured AI tool within a project."""
    path: GetAiToolRequestPath

# Operation: update_ai_tool
class PatchAiToolRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the AI tool.")
    tool_key: str = Field(default=..., validation_alias="toolKey", serialization_alias="toolKey", description="The unique identifier for the AI tool to be updated.")
class PatchAiToolRequestBody(StrictModel):
    """AI tool object to update"""
    schema_: dict[str, Any] | None = Field(default=None, validation_alias="schema", serialization_alias="schema", description="A JSON Schema object that defines the tool's input parameters and their constraints for LLM consumption. This schema is used by language models to understand how to invoke the tool correctly.")
    custom_parameters: dict[str, Any] | None = Field(default=None, validation_alias="customParameters", serialization_alias="customParameters", description="Custom metadata and configuration settings for application-level use. These parameters are not exposed to or used by the LLM, allowing you to store tool-specific application logic and settings.")
class PatchAiToolRequest(StrictModel):
    """Update an existing AI tool's configuration, including its parameter schema for LLM consumption and custom application-level settings."""
    path: PatchAiToolRequestPath
    body: PatchAiToolRequestBody | None = None

# Operation: delete_ai_tool
class DeleteAiToolRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the AI tool to delete.")
    tool_key: str = Field(default=..., validation_alias="toolKey", serialization_alias="toolKey", description="The unique identifier of the AI tool to delete.")
class DeleteAiToolRequest(StrictModel):
    """Permanently delete an AI tool from a project. This action cannot be undone and will remove the tool and all associated configurations."""
    path: DeleteAiToolRequestPath

# Operation: list_prompt_snippets
class ListPromptSnippetsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the prompt snippets to retrieve.")
class ListPromptSnippetsRequest(StrictModel):
    """Retrieve all prompt snippets available in a specific project. Prompt snippets are reusable text templates used to configure AI behavior and responses."""
    path: ListPromptSnippetsRequestPath

# Operation: create_prompt_snippet
class PostPromptSnippetRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project where the prompt snippet will be created.")
class PostPromptSnippetRequestBody(StrictModel):
    """Prompt snippet object to create"""
    key: str = Field(default=..., description="A unique key identifier for the prompt snippet within the project, used for referencing the snippet in configurations.")
    name: str = Field(default=..., description="A human-readable name for the prompt snippet to help identify its purpose.")
    text: str = Field(default=..., description="The text content of the prompt snippet that will be stored and reused in AI configurations.")
class PostPromptSnippetRequest(StrictModel):
    """Create a new prompt snippet within a project to store reusable AI prompt text for use in AI configurations."""
    path: PostPromptSnippetRequestPath
    body: PostPromptSnippetRequestBody

# Operation: get_prompt_snippet
class GetPromptSnippetRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the prompt snippet.")
    snippet_key: str = Field(default=..., validation_alias="snippetKey", serialization_alias="snippetKey", description="The unique identifier for the prompt snippet to retrieve.")
class GetPromptSnippetRequest(StrictModel):
    """Retrieve a specific prompt snippet by its unique key within a project. Use this to fetch the full details of a saved prompt snippet for use in AI configurations."""
    path: GetPromptSnippetRequestPath

# Operation: update_prompt_snippet
class PatchPromptSnippetRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the prompt snippet.")
    snippet_key: str = Field(default=..., validation_alias="snippetKey", serialization_alias="snippetKey", description="The unique identifier of the prompt snippet to update.")
class PatchPromptSnippetRequestBody(StrictModel):
    """Prompt snippet fields to update"""
    name: str | None = Field(default=None, description="The display name for the prompt snippet. If provided, updates the snippet's name.")
    text: str | None = Field(default=None, description="The text content of the prompt snippet. If provided, updates the snippet's template text.")
class PatchPromptSnippetRequest(StrictModel):
    """Update an existing prompt snippet in a project, creating a new version with the modified content or metadata."""
    path: PatchPromptSnippetRequestPath
    body: PatchPromptSnippetRequestBody | None = None

# Operation: delete_prompt_snippet
class DeletePromptSnippetRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the prompt snippet to delete.")
    snippet_key: str = Field(default=..., validation_alias="snippetKey", serialization_alias="snippetKey", description="The unique identifier of the prompt snippet to delete.")
class DeletePromptSnippetRequest(StrictModel):
    """Delete an existing prompt snippet from a project's AI configuration. This operation permanently removes the specified prompt snippet and cannot be undone."""
    path: DeletePromptSnippetRequestPath

# Operation: list_prompt_snippet_references
class ListPromptSnippetReferencesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the prompt snippet.")
    snippet_key: str = Field(default=..., validation_alias="snippetKey", serialization_alias="snippetKey", description="The unique identifier for the prompt snippet whose references you want to list.")
class ListPromptSnippetReferencesRequest(StrictModel):
    """Retrieve all AI Config variations that currently reference a specific prompt snippet, helping you understand where a snippet is being used across your project."""
    path: ListPromptSnippetReferencesRequestPath

# Operation: list_agent_graphs
class ListAgentGraphsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the agent graphs to list.")
class ListAgentGraphsRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'.")
class ListAgentGraphsRequest(StrictModel):
    """Retrieve all agent graphs in a project with their metadata. Returns graph information without edge data for efficient listing."""
    path: ListAgentGraphsRequestPath
    header: ListAgentGraphsRequestHeader

# Operation: create_agent_graph
class PostAgentGraphRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project where the agent graph will be created.")
class PostAgentGraphRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Currently only 'beta' is supported.")
class PostAgentGraphRequestBody(StrictModel):
    """Agent graph object to create"""
    key: str = Field(default=..., description="A unique identifier for the agent graph within the project. Must be distinct from other graphs in the same project.")
    name: str = Field(default=..., description="A human-readable display name for the agent graph.")
    root_config_key: str | None = Field(default=None, validation_alias="rootConfigKey", serialization_alias="rootConfigKey", description="The AI Config key that serves as the root node of the graph. Required if edges are provided; omit both this and edges to create a metadata-only graph.")
    edges: list[AgentGraphEdgePost] | None = Field(default=None, description="An array of edges defining connections between nodes in the graph. Each edge specifies the relationship between two nodes. Required if rootConfigKey is provided; both must be present together or both omitted.")
class PostAgentGraphRequest(StrictModel):
    """Create a new agent graph within a project. The graph can be initialized with a root configuration node and edges, or created as metadata-only if neither is provided."""
    path: PostAgentGraphRequestPath
    header: PostAgentGraphRequestHeader
    body: PostAgentGraphRequestBody

# Operation: get_agent_graph
class GetAgentGraphRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the agent graph.")
    graph_key: str = Field(default=..., validation_alias="graphKey", serialization_alias="graphKey", description="The unique identifier for the agent graph to retrieve.")
class GetAgentGraphRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Currently only the beta version is supported.")
class GetAgentGraphRequest(StrictModel):
    """Retrieve a specific agent graph by its key, including all its edges and configuration details."""
    path: GetAgentGraphRequestPath
    header: GetAgentGraphRequestHeader

# Operation: update_agent_graph
class PatchAgentGraphRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the agent graph.")
    graph_key: str = Field(default=..., validation_alias="graphKey", serialization_alias="graphKey", description="The unique identifier for the agent graph to update.")
class PatchAgentGraphRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'.")
class PatchAgentGraphRequestBody(StrictModel):
    """Agent graph object to update"""
    name: str | None = Field(default=None, description="A human-readable name for the agent graph. Use this to provide a descriptive label for the graph.")
    root_config_key: str | None = Field(default=None, validation_alias="rootConfigKey", serialization_alias="rootConfigKey", description="The AI Config key designating the root node of the graph. When provided, edges must also be included in the same request, and both will completely replace existing values.")
    edges: list[AgentGraphEdge] | None = Field(default=None, description="An ordered array of edges defining the graph structure and connections between nodes. When provided, rootConfigKey must also be included in the same request, and both will completely replace all existing edges.")
class PatchAgentGraphRequest(StrictModel):
    """Update an existing agent graph by modifying its configuration. Provide only the fields you want to change; unspecified fields retain their current values. If updating the root node or graph structure, both rootConfigKey and edges must be provided together as they are treated as a complete replacement."""
    path: PatchAgentGraphRequestPath
    header: PatchAgentGraphRequestHeader
    body: PatchAgentGraphRequestBody | None = None

# Operation: delete_agent_graph
class DeleteAgentGraphRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the agent graph to delete.")
    graph_key: str = Field(default=..., validation_alias="graphKey", serialization_alias="graphKey", description="The unique identifier for the agent graph to delete.")
class DeleteAgentGraphRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'.")
class DeleteAgentGraphRequest(StrictModel):
    """Permanently delete an agent graph and all of its associated edges from a project. This operation cannot be undone."""
    path: DeleteAgentGraphRequestPath
    header: DeleteAgentGraphRequestHeader

# Operation: list_agent_optimizations
class ListAgentOptimizationsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the agent optimizations to retrieve.")
class ListAgentOptimizationsRequest(StrictModel):
    """Retrieve all agent optimizations configured for a specific project. Returns a list of optimization settings and configurations applied to agents within the project."""
    path: ListAgentOptimizationsRequestPath

# Operation: create_agent_optimization
class PostAgentOptimizationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project where the agent optimization will be created.")
class PostAgentOptimizationRequestBody(StrictModel):
    """Agent optimization object to create"""
    key: str = Field(default=..., description="A unique key to identify this agent optimization configuration within the project.")
    ai_config_key: str = Field(default=..., validation_alias="aiConfigKey", serialization_alias="aiConfigKey", description="The key of the AI configuration that this optimization applies to.")
    max_attempts: int = Field(default=..., validation_alias="maxAttempts", serialization_alias="maxAttempts", description="The maximum number of attempts the agent should make when trying to meet acceptance criteria. Must be a positive integer.")
    model_choices: list[str] | None = Field(default=None, validation_alias="modelChoices", serialization_alias="modelChoices", description="An optional list of AI model identifiers to evaluate and compare during optimization. Order may indicate priority or evaluation sequence.")
    judge_model: str = Field(default=..., validation_alias="judgeModel", serialization_alias="judgeModel", description="The key of the model to use as the judge for evaluating agent performance against acceptance criteria.")
    variable_choices: list[dict[str, Any]] | None = Field(default=None, validation_alias="variableChoices", serialization_alias="variableChoices", description="An optional list of variable configurations that the agent can choose from or adjust during optimization. Order may indicate priority or evaluation sequence.")
    acceptance_statements: list[AgentOptimizationAcceptanceStatement] | None = Field(default=None, validation_alias="acceptanceStatements", serialization_alias="acceptanceStatements", description="An optional list of acceptance criteria statements that define successful agent behavior. The agent must satisfy these conditions within the maximum attempts.")
    judges: list[AgentOptimizationJudge] | None = Field(default=None, description="An optional list of judge configurations or identifiers used to evaluate agent responses. Multiple judges can provide consensus evaluation.")
    user_input_options: list[str] | None = Field(default=None, validation_alias="userInputOptions", serialization_alias="userInputOptions", description="An optional list of user input options or scenarios that the agent should handle during optimization testing.")
    ground_truth_responses: list[str] | None = Field(default=None, validation_alias="groundTruthResponses", serialization_alias="groundTruthResponses", description="An optional list of expected or reference responses used to measure agent accuracy and performance against ground truth.")
    metric_key: str | None = Field(default=None, validation_alias="metricKey", serialization_alias="metricKey", description="An optional key referencing a specific metric to track and optimize for during the agent optimization process.")
class PostAgentOptimizationRequest(StrictModel):
    """Create a new agent optimization configuration within a project to define how an AI agent should be evaluated and optimized using specified models, judges, and acceptance criteria."""
    path: PostAgentOptimizationRequestPath
    body: PostAgentOptimizationRequestBody

# Operation: get_agent_optimization
class GetAgentOptimizationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the agent optimization.")
    optimization_key: str = Field(default=..., validation_alias="optimizationKey", serialization_alias="optimizationKey", description="The unique identifier for the specific agent optimization to retrieve.")
class GetAgentOptimizationRequest(StrictModel):
    """Retrieve a specific agent optimization configuration by its unique key within a project. Use this to inspect the details and settings of an existing optimization."""
    path: GetAgentOptimizationRequestPath

# Operation: update_agent_optimization
class PatchAgentOptimizationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the agent optimization.")
    optimization_key: str = Field(default=..., validation_alias="optimizationKey", serialization_alias="optimizationKey", description="The unique identifier of the agent optimization to update.")
class PatchAgentOptimizationRequestBody(StrictModel):
    """Agent optimization fields to update"""
    max_attempts: int | None = Field(default=None, validation_alias="maxAttempts", serialization_alias="maxAttempts", description="The maximum number of attempts allowed for the agent during optimization execution.")
    model_choices: list[str] | None = Field(default=None, validation_alias="modelChoices", serialization_alias="modelChoices", description="An ordered list of model identifiers to evaluate during optimization. Order may affect evaluation priority.")
    judge_model: str | None = Field(default=None, validation_alias="judgeModel", serialization_alias="judgeModel", description="The model identifier to use as a judge for evaluating agent performance against acceptance criteria.")
    variable_choices: list[dict[str, Any]] | None = Field(default=None, validation_alias="variableChoices", serialization_alias="variableChoices", description="An ordered list of variable configurations to test during optimization. Order may affect evaluation sequence.")
    acceptance_statements: list[AgentOptimizationAcceptanceStatement] | None = Field(default=None, validation_alias="acceptanceStatements", serialization_alias="acceptanceStatements", description="A list of acceptance criteria statements that define successful agent behavior. Each statement should clearly specify expected outcomes.")
    judges: list[AgentOptimizationJudge] | None = Field(default=None, description="A list of judge configurations or identifiers used to evaluate agent responses. Multiple judges can be specified for consensus-based evaluation.")
    user_input_options: list[str] | None = Field(default=None, validation_alias="userInputOptions", serialization_alias="userInputOptions", description="A list of user input options or scenarios to test during optimization. Defines the range of inputs the agent should handle.")
    ground_truth_responses: list[str] | None = Field(default=None, validation_alias="groundTruthResponses", serialization_alias="groundTruthResponses", description="A list of ground truth responses corresponding to test inputs. Used as reference standards for evaluating agent accuracy.")
    metric_key: str | None = Field(default=None, validation_alias="metricKey", serialization_alias="metricKey", description="The identifier of the metric to optimize against. Specifies which performance metric should be the primary optimization target.")
class PatchAgentOptimizationRequest(StrictModel):
    """Update an existing agent optimization configuration for a project. This operation creates a new version of the optimization with the provided changes."""
    path: PatchAgentOptimizationRequestPath
    body: PatchAgentOptimizationRequestBody | None = None

# Operation: delete_agent_optimization
class DeleteAgentOptimizationRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the agent optimization to delete.")
    optimization_key: str = Field(default=..., validation_alias="optimizationKey", serialization_alias="optimizationKey", description="The unique identifier of the agent optimization to delete.")
class DeleteAgentOptimizationRequest(StrictModel):
    """Permanently delete an agent optimization configuration from a project. This action cannot be undone."""
    path: DeleteAgentOptimizationRequestPath

# Operation: list_announcements
class GetAnnouncementsPublicRequestQuery(StrictModel):
    status: Literal["active", "inactive", "scheduled"] | None = Field(default=None, description="Filter announcements by their current status: active (published and visible), inactive (unpublished), or scheduled (queued for future publication).")
class GetAnnouncementsPublicRequest(StrictModel):
    """Retrieve a list of announcements filtered by their publication status. Use this to fetch active, inactive, or scheduled announcements for display or management purposes."""
    query: GetAnnouncementsPublicRequestQuery | None = None

# Operation: create_announcement
class CreateAnnouncementPublicRequestBody(StrictModel):
    """Announcement request body"""
    is_dismissible: bool = Field(default=..., validation_alias="isDismissible", serialization_alias="isDismissible", description="Whether users can dismiss this announcement from their view. Set to true to allow users to close the announcement, or false to make it persistent.")
    title: str = Field(default=..., description="A concise headline for the announcement (e.g., 'System Maintenance Notice'). This is the primary text users see first.")
    message: str = Field(default=..., description="The full announcement message body. Supports markdown formatting for emphasis, links, and structure. Use this to provide detailed information about the announcement.")
    start_time: int = Field(default=..., validation_alias="startTime", serialization_alias="startTime", description="The Unix timestamp in milliseconds when the announcement becomes visible to users. This marks the start of the announcement's active period.", json_schema_extra={'format': 'int64'})
    end_time: int | None = Field(default=None, validation_alias="endTime", serialization_alias="endTime", description="The Unix timestamp in milliseconds when the announcement stops being displayed to users. If omitted, the announcement remains active indefinitely after the start time.", json_schema_extra={'format': 'int64'})
    severity: Literal["info", "warning", "critical"] = Field(default=..., description="The urgency level of the announcement. Use 'info' for general notices, 'warning' for important alerts, or 'critical' for urgent system issues requiring immediate attention.")
class CreateAnnouncementPublicRequest(StrictModel):
    """Create a new announcement to notify users about system events, maintenance, or important updates. The announcement will be displayed to users during the specified time window."""
    body: CreateAnnouncementPublicRequestBody

# Operation: update_announcement
class UpdateAnnouncementPublicRequestPath(StrictModel):
    announcement_id: str = Field(default=..., validation_alias="announcementId", serialization_alias="announcementId", description="The unique identifier of the announcement to update, provided as a numeric string (e.g., '1234567890').")
class UpdateAnnouncementPublicRequestBody(StrictModel):
    """Update announcement request body"""
    body: list[AnnouncementPatchOperation] = Field(default=..., description="An array of patch operations to apply to the announcement. Each operation specifies how to modify the announcement's properties.")
class UpdateAnnouncementPublicRequest(StrictModel):
    """Update an existing announcement by applying a series of changes. Specify the announcement to modify using its ID and provide the updates as an array of patch operations."""
    path: UpdateAnnouncementPublicRequestPath
    body: UpdateAnnouncementPublicRequestBody

# Operation: delete_announcement
class DeleteAnnouncementPublicRequestPath(StrictModel):
    announcement_id: str = Field(default=..., validation_alias="announcementId", serialization_alias="announcementId", description="The unique identifier of the announcement to delete, provided as a numeric string (e.g., '1234567890').")
class DeleteAnnouncementPublicRequest(StrictModel):
    """Permanently delete an announcement by its ID. This action cannot be undone."""
    path: DeleteAnnouncementPublicRequestPath

# Operation: update_approval_request_settings_for_project_environment
class PatchApprovalRequestSettingsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that uniquely identifies the project containing the approval settings.")
class PatchApprovalRequestSettingsRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="API version identifier. Must be set to 'beta' for this endpoint.")
class PatchApprovalRequestSettingsRequestBody(StrictModel):
    """Approval request settings to update"""
    auto_apply_approved_changes: bool | None = Field(default=None, validation_alias="autoApplyApprovedChanges", serialization_alias="autoApplyApprovedChanges", description="Enable automatic application of changes once all required reviewers have approved them. Only applicable when using third-party approval services.")
    bypass_approvals_for_pending_changes: bool | None = Field(default=None, validation_alias="bypassApprovalsForPendingChanges", serialization_alias="bypassApprovalsForPendingChanges", description="Skip the approval process for changes that are currently pending review.")
    can_apply_declined_changes: bool | None = Field(default=None, validation_alias="canApplyDeclinedChanges", serialization_alias="canApplyDeclinedChanges", description="Allow applying changes if at least one reviewer has approved, regardless of other reviewers' decisions.")
    can_review_own_request: bool | None = Field(default=None, validation_alias="canReviewOwnRequest", serialization_alias="canReviewOwnRequest", description="Permit the person who created an approval request to also approve and apply their own change.")
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment these approval settings apply to.")
    min_num_approvals: int | None = Field(default=None, validation_alias="minNumApprovals", serialization_alias="minNumApprovals", description="The number of approvals required before a change can be applied. Must be between 1 and 5 inclusive.", json_schema_extra={'format': 'int'})
    required: bool | None = Field(default=None, description="Whether approval is mandatory for changes in this environment.")
    required_approval_tags: list[str] | None = Field(default=None, validation_alias="requiredApprovalTags", serialization_alias="requiredApprovalTags", description="List of flag tags that trigger approval requirements. When specified, only flags with these tags require approval; otherwise all flags require approval.")
    resource_kind: str = Field(default=..., validation_alias="resourceKind", serialization_alias="resourceKind", description="The type of resource these approval settings apply to.")
    service_config: dict[str, Any] | None = Field(default=None, validation_alias="serviceConfig", serialization_alias="serviceConfig", description="Custom configuration object specific to the approval service being used.")
    service_kind: str | None = Field(default=None, validation_alias="serviceKind", serialization_alias="serviceKind", description="The approval service provider to use for managing approvals (e.g., 'launchdarkly' for native approvals).")
    service_kind_configuration_id: str | None = Field(default=None, validation_alias="serviceKindConfigurationId", serialization_alias="serviceKindConfigurationId", description="Integration configuration ID for a custom approval service. This is an Enterprise-only feature and identifies which custom integration to use.")
class PatchApprovalRequestSettingsRequest(StrictModel):
    """Update approval request settings for a specific environment within a project. Configure approval requirements, reviewer permissions, and integration settings for flag change approvals."""
    path: PatchApprovalRequestSettingsRequestPath
    header: PatchApprovalRequestSettingsRequestHeader
    body: PatchApprovalRequestSettingsRequestBody

# Operation: list_views
class GetViewsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Use 'default' for the default project or specify a custom project key.")
class GetViewsRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="API version specification. Must be set to 'beta' to access this endpoint.")
class GetViewsRequest(StrictModel):
    """Retrieve all views available in a specified project. Views are saved configurations or perspectives for organizing and displaying project data."""
    path: GetViewsRequestPath
    header: GetViewsRequestHeader

# Operation: create_view
class CreateViewRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that uniquely identifies the project where the view will be created (e.g., 'default').")
class CreateViewRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Currently only 'beta' is supported.")
class CreateViewRequestBody(StrictModel):
    """View object to create"""
    key: str = Field(default=..., description="A unique identifier for the view within the project. This key is used to reference the view in API calls and must be distinct from other views in the same project.")
    name: str = Field(default=..., description="A human-readable display name for the view that appears in the user interface.")
    generate_sdk_keys: bool | None = Field(default=None, validation_alias="generateSdkKeys", serialization_alias="generateSdkKeys", description="Whether to automatically generate SDK keys associated with this view. Defaults to false if not specified.")
    tags: list[str] | None = Field(default=None, description="An optional list of tags to categorize and organize the view. Tags help with filtering and searching views.")
class CreateViewRequest(StrictModel):
    """Create a new view within a specified project. Views are used to organize and filter feature flags and other resources within your LaunchDarkly project."""
    path: CreateViewRequestPath
    header: CreateViewRequestHeader
    body: CreateViewRequestBody

# Operation: get_view
class GetViewRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the view (e.g., 'default').")
    view_key: str = Field(default=..., validation_alias="viewKey", serialization_alias="viewKey", description="The unique identifier for the view to retrieve (e.g., 'my-view').")
class GetViewRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta'.")
class GetViewRequest(StrictModel):
    """Retrieve a specific view by its project and view keys. Returns the view configuration and metadata for the specified view."""
    path: GetViewRequestPath
    header: GetViewRequestHeader

# Operation: update_view
class UpdateViewRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the view. Use the project identifier (e.g., 'default').")
    view_key: str = Field(default=..., validation_alias="viewKey", serialization_alias="viewKey", description="The view key that identifies which view to update (e.g., 'my-view').")
class UpdateViewRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="API version specification. Must be set to 'beta' for this endpoint.")
class UpdateViewRequestBody(StrictModel):
    """A JSON representation of the view including only the fields to update."""
    name: str | None = Field(default=None, description="A human-readable name for the view. This is the display name users will see.")
    generate_sdk_keys: bool | None = Field(default=None, validation_alias="generateSdkKeys", serialization_alias="generateSdkKeys", description="Whether to automatically generate SDK keys for this view. Set to true to enable SDK key generation.")
    tags: list[str] | None = Field(default=None, description="Tags to associate with this view for organization and filtering. Provide as an array of tag strings.")
    archived: bool | None = Field(default=None, description="Whether the view is archived. Set to true to archive the view, or false to unarchive it.")
class UpdateViewRequest(StrictModel):
    """Update an existing view by replacing specified fields. Provide a JSON object containing only the fields you want to modify; unchanged fields retain their current values."""
    path: UpdateViewRequestPath
    header: UpdateViewRequestHeader
    body: UpdateViewRequestBody | None = None

# Operation: delete_view
class DeleteViewRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier of the project containing the view. Use the project key (e.g., 'default') to specify which project to access.")
    view_key: str = Field(default=..., validation_alias="viewKey", serialization_alias="viewKey", description="The unique identifier of the view to delete. Specify the view key (e.g., 'my-view') to target the exact view for deletion.")
class DeleteViewRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta' for this endpoint.")
class DeleteViewRequest(StrictModel):
    """Permanently delete a specific view from a project by its key. This operation removes the view and cannot be undone."""
    path: DeleteViewRequestPath
    header: DeleteViewRequestHeader

# Operation: link_resources_to_view
class LinkResourceRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the view. Use the project identifier (e.g., 'default').")
    view_key: str = Field(default=..., validation_alias="viewKey", serialization_alias="viewKey", description="The view key where resources will be linked. Use the view identifier (e.g., 'my-view').")
    resource_type: Literal["flags", "segments"] = Field(default=..., validation_alias="resourceType", serialization_alias="resourceType", description="The type of resource to link. Must be either 'flags' or 'segments'.")
class LinkResourceRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version for this endpoint. Must be 'beta'.")
class LinkResourceRequestBody(StrictModel):
    """Resources to link to the view. You can provide explicit keys/IDs, filters, or both.
- Flags: identified by key or filtered by maintainerId, maintainerTeamKey, tags, state, query
- Segments: identified by segment ID or filtered by tags, query, unbounded
"""
    body: ViewLinkRequestKeys | ViewLinkRequestSegmentIdentifiers | ViewLinkRequestFilter = Field(default=..., description="Request body containing resource keys and/or filters to link. For flags, you can filter by maintainerId, maintainerTeamKey, tags, state, or query. For segments, you can filter by tags, query, or unbounded status.")
class LinkResourceRequest(StrictModel):
    """Link one or multiple resources (flags or segments) to a view using resource keys, filters, or both. When both keys and filters are provided, resources matching either condition are linked."""
    path: LinkResourceRequestPath
    header: LinkResourceRequestHeader
    body: LinkResourceRequestBody

# Operation: delete_view_resource_links
class UnlinkResourceRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the view. Use the project identifier (e.g., 'default').")
    view_key: str = Field(default=..., validation_alias="viewKey", serialization_alias="viewKey", description="The view key from which to unlink resources. Use the view identifier (e.g., 'my-view').")
    resource_type: Literal["flags", "segments"] = Field(default=..., validation_alias="resourceType", serialization_alias="resourceType", description="The type of resource to unlink: either 'flags' for feature flags or 'segments' for audience segments.")
class UnlinkResourceRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="API version identifier. Must be set to 'beta' for this endpoint.")
class UnlinkResourceRequestBody(StrictModel):
    """The resource to link to the view. Flags are identified by key. Segments are identified by segment ID."""
    body: ViewLinkRequestKeys | ViewLinkRequestSegmentIdentifiers | ViewLinkRequestFilter = Field(default=..., description="Request body containing the resource identifiers to unlink. For flags, provide flag keys; for segments, provide segment IDs.")
class UnlinkResourceRequest(StrictModel):
    """Remove one or multiple linked resources (feature flags or segments) from a view. Specify the resource type and provide the identifiers to unlink."""
    path: UnlinkResourceRequestPath
    header: UnlinkResourceRequestHeader
    body: UnlinkResourceRequestBody

# Operation: list_linked_resources_for_view
class GetLinkedResourcesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies the project containing the view. Use the project's unique identifier (e.g., 'default').")
    view_key: str = Field(default=..., validation_alias="viewKey", serialization_alias="viewKey", description="The view key that identifies the specific view within the project. Use the view's unique identifier (e.g., 'my-view').")
    resource_type: Literal["flags", "segments"] = Field(default=..., validation_alias="resourceType", serialization_alias="resourceType", description="The type of linked resource to retrieve. Must be either 'flags' for feature flags or 'segments' for user segments.")
class GetLinkedResourcesRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional case-insensitive search filter that matches against the resource key and resource name. Leave empty to retrieve all linked resources without filtering.")
class GetLinkedResourcesRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version for this endpoint. Must be set to 'beta' to access this operation.")
class GetLinkedResourcesRequest(StrictModel):
    """Retrieve all linked resources of a specified type (flags or segments) associated with a given view within a project. Optionally filter results using a case-insensitive search query."""
    path: GetLinkedResourcesRequestPath
    query: GetLinkedResourcesRequestQuery | None = None
    header: GetLinkedResourcesRequestHeader

# Operation: list_linked_views_for_resource
class GetLinkedViewsRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that contains the resource. Typically 'default' for standard projects.")
    resource_type: Literal["flags", "segments"] = Field(default=..., validation_alias="resourceType", serialization_alias="resourceType", description="The type of resource to retrieve linked views for. Must be either 'flags' or 'segments'.")
    resource_key: str = Field(default=..., validation_alias="resourceKey", serialization_alias="resourceKey", description="The unique identifier for the resource. For flags, use the flag key. For segments, use the segment ID.")
class GetLinkedViewsRequestQuery(StrictModel):
    environment_id: str | None = Field(default=None, validation_alias="environmentId", serialization_alias="environmentId", description="The environment ID where the resource exists. Required when resourceType is 'segments'; optional for flags.")
class GetLinkedViewsRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Currently supports 'beta' version.")
class GetLinkedViewsRequest(StrictModel):
    """Retrieve all views linked to a specific resource (flag or segment). Use the resource key for flags and segment ID for segments to identify the target resource."""
    path: GetLinkedViewsRequestPath
    query: GetLinkedViewsRequestQuery | None = None
    header: GetLinkedViewsRequestHeader

# Operation: list_release_policies
class GetReleasePoliciesRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project (e.g., 'default').")
class GetReleasePoliciesRequestQuery(StrictModel):
    exclude_default: bool | None = Field(default=None, validation_alias="excludeDefault", serialization_alias="excludeDefault", description="Set to true to exclude the default release policy from the results; when false or omitted, the default policy is included if an environment filter is present.")
class GetReleasePoliciesRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this endpoint; must be set to 'beta'.")
class GetReleasePoliciesRequest(StrictModel):
    """Retrieve a list of release policies for a specified project with optional filtering to exclude the default policy."""
    path: GetReleasePoliciesRequestPath
    query: GetReleasePoliciesRequestQuery | None = None
    header: GetReleasePoliciesRequestHeader

# Operation: reorder_release_policies
class PostReleasePoliciesOrderRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project whose release policies should be reordered. Use the project key assigned during project creation (e.g., 'default').")
class PostReleasePoliciesOrderRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this operation. Currently only the beta version is available.")
class PostReleasePoliciesOrderRequestBody(StrictModel):
    """Array of release policy keys in the desired rank order (scoped policies only). These keys must include _all_ of the scoped release policies for the project."""
    body: list[str] = Field(default=..., description="An ordered array of release policy keys that defines the new execution sequence. The order of keys in this array determines the order in which policies are evaluated and applied.")
class PostReleasePoliciesOrderRequest(StrictModel):
    """Reorder the release policies for a project by specifying their desired sequence. This operation updates the policy execution order without modifying individual policy configurations."""
    path: PostReleasePoliciesOrderRequestPath
    header: PostReleasePoliciesOrderRequestHeader
    body: PostReleasePoliciesOrderRequestBody

# Operation: get_release_policy
class GetReleasePolicyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project (e.g., 'default'). This scopes the release policy lookup to a specific project.")
    policy_key: str = Field(default=..., validation_alias="policyKey", serialization_alias="policyKey", description="The unique identifier for the release policy within the project (e.g., 'production-release'). This specifies which policy to retrieve.")
class GetReleasePolicyRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this request. Must be set to 'beta' to access this endpoint.")
class GetReleasePolicyRequest(StrictModel):
    """Retrieve a specific release policy by its key within a project. Use this to fetch detailed configuration and settings for a named release policy."""
    path: GetReleasePolicyRequestPath
    header: GetReleasePolicyRequestHeader

# Operation: update_release_policy
class PutReleasePolicyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the release policy.")
    policy_key: str = Field(default=..., validation_alias="policyKey", serialization_alias="policyKey", description="The unique human-readable identifier for the release policy to update.")
class PutReleasePolicyRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="API version specification; must be set to 'beta' for this endpoint.")
class PutReleasePolicyRequestBodyScope(StrictModel):
    environment_keys: list[str] | None = Field(default=None, validation_alias="environmentKeys", serialization_alias="environmentKeys", description="Optional list of environment keys where this policy applies (e.g., production, staging). If specified, the policy is scoped to these environments only.")
    flag_tag_keys: list[str] | None = Field(default=None, validation_alias="flagTagKeys", serialization_alias="flagTagKeys", description="Optional list of flag tag keys to which this policy applies. If specified, the policy only affects flags with these tags.")
class PutReleasePolicyRequestBodyGuardedReleaseConfig(StrictModel):
    min_sample_size: int | None = Field(default=None, validation_alias="minSampleSize", serialization_alias="minSampleSize", description="Optional minimum number of samples (observations) required before the system can make a release decision. Helps ensure statistical significance.")
    rollback_on_regression: bool | None = Field(default=None, validation_alias="rollbackOnRegression", serialization_alias="rollbackOnRegression", description="Optional flag to automatically roll back the release if a regression is detected in monitored metrics.")
    metric_keys: list[str] | None = Field(default=None, validation_alias="metricKeys", serialization_alias="metricKeys", description="Optional list of metric keys to monitor during release (e.g., http-errors, latency). These metrics inform release decisions and rollback triggers.")
    metric_group_keys: list[str] | None = Field(default=None, validation_alias="metricGroupKeys", serialization_alias="metricGroupKeys", description="Optional list of metric group keys to monitor during release. Groups allow monitoring multiple related metrics together.")
    stages: list[ReleasePolicyStage] | None = Field(default=None, validation_alias="stages", serialization_alias="stages", description="Optional array of release stages for guarded-release policies, defining sequential validation gates and approval requirements.")
class PutReleasePolicyRequestBodyProgressiveReleaseConfig(StrictModel):
    stages: list[ReleasePolicyStage] | None = Field(default=None, validation_alias="stages", serialization_alias="stages", description="Optional array of release stages for progressive-release policies, defining percentage-based rollout increments and timing.")
class PutReleasePolicyRequestBody(StrictModel):
    """Release policy data to update"""
    release_method: Literal["guarded-release", "progressive-release"] = Field(default=..., validation_alias="releaseMethod", serialization_alias="releaseMethod", description="The release strategy for this policy: 'guarded-release' for controlled rollouts with validation gates, or 'progressive-release' for gradual percentage-based rollouts.")
    name: str = Field(default=..., description="A human-readable name for the release policy, up to 256 characters. Used for display and identification in the UI.", max_length=256)
    scope: PutReleasePolicyRequestBodyScope | None = None
    guarded_release_config: PutReleasePolicyRequestBodyGuardedReleaseConfig | None = Field(default=None, validation_alias="guardedReleaseConfig", serialization_alias="guardedReleaseConfig")
    progressive_release_config: PutReleasePolicyRequestBodyProgressiveReleaseConfig | None = Field(default=None, validation_alias="progressiveReleaseConfig", serialization_alias="progressiveReleaseConfig")
class PutReleasePolicyRequest(StrictModel):
    """Update an existing release policy for a project, configuring how feature flags are released across environments with optional metrics-based validation and rollback controls."""
    path: PutReleasePolicyRequestPath
    header: PutReleasePolicyRequestHeader
    body: PutReleasePolicyRequestBody

# Operation: delete_release_policy
class DeleteReleasePolicyRequestPath(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project containing the release policy (e.g., 'default').")
    policy_key: str = Field(default=..., validation_alias="policyKey", serialization_alias="policyKey", description="The human-readable identifier for the release policy to delete (e.g., 'production-release').")
class DeleteReleasePolicyRequestHeader(StrictModel):
    ld_api_version: Literal["beta"] = Field(default=..., validation_alias="LD-API-Version", serialization_alias="LD-API-Version", description="The API version to use for this operation. Must be set to 'beta'.")
class DeleteReleasePolicyRequest(StrictModel):
    """Permanently delete a release policy from a project. This action cannot be undone and will remove all associated policy configurations."""
    path: DeleteReleasePolicyRequestPath
    header: DeleteReleasePolicyRequestHeader

# Operation: get_deployment_frequency_chart
class GetDeploymentFrequencyChartRequestQuery(StrictModel):
    project_key: str | None = Field(default=None, validation_alias="projectKey", serialization_alias="projectKey", description="The project key to filter deployment frequency data for a specific project.", json_schema_extra={'format': 'string'})
    environment_key: str | None = Field(default=None, validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key to filter deployment frequency data for a specific environment.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Comma-separated list of application keys to filter deployment frequency data across multiple applications.", json_schema_extra={'format': 'string'})
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the time range as a Unix timestamp in milliseconds. Defaults to 7 days ago if not specified.", json_schema_extra={'format': 'date-time'})
    to: str | None = Field(default=None, description="End of the time range as a Unix timestamp in milliseconds. Defaults to the current time if not specified.", json_schema_extra={'format': 'date-time'})
    bucket_type: str | None = Field(default=None, validation_alias="bucketType", serialization_alias="bucketType", description="Type of time bucket for aggregating data: `rolling` (continuous window), `hour` (hourly intervals), or `day` (daily intervals). Defaults to `rolling`.", json_schema_extra={'format': 'string'})
    bucket_ms: int | None = Field(default=None, validation_alias="bucketMs", serialization_alias="bucketMs", description="Duration of intervals for the x-axis in milliseconds. Defaults to one day (86400000 milliseconds). Adjust to control granularity of the chart data.", json_schema_extra={'format': 'int64'})
    group_by: str | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="Dimension to group deployment frequency data by: `application` (per application) or `kind` (by deployment type).", json_schema_extra={'format': 'string'})
class GetDeploymentFrequencyChartRequest(StrictModel):
    """Retrieve deployment frequency chart data for engineering insights, showing how often deployments occur across your infrastructure. Optionally expand the response to include detailed metrics related to deployment frequency."""
    query: GetDeploymentFrequencyChartRequestQuery | None = None

# Operation: get_stale_flags_chart
class GetStaleFlagsChartRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project to retrieve stale flags data for.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment within the project to retrieve stale flags data for.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Optional comma-separated list of application keys to filter stale flags data to specific applications.", json_schema_extra={'format': 'string'})
    group_by: str | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="Optional property to group the stale flags results by. Currently supports grouping by maintainer to organize flags by their responsible team members.", json_schema_extra={'format': 'string'})
class GetStaleFlagsChartRequest(StrictModel):
    """Retrieve stale flags chart data for engineering insights, showing flag health metrics across a project and environment. Optionally expand the response to include detailed metrics and group results by maintainer."""
    query: GetStaleFlagsChartRequestQuery

# Operation: get_flag_status_chart
class GetFlagStatusChartRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project's flag data to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that specifies which environment's flag statuses to chart.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Optional comma-separated list of application keys to filter the flag status data to specific applications.", json_schema_extra={'format': 'string'})
class GetFlagStatusChartRequest(StrictModel):
    """Retrieve flag status chart data for a specific project and environment, optionally filtered by applications. This provides observability into flag health and status distribution across your infrastructure."""
    query: GetFlagStatusChartRequestQuery

# Operation: get_lead_time_chart
class GetLeadTimeChartRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project's lead time data to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str | None = Field(default=None, validation_alias="environmentKey", serialization_alias="environmentKey", description="Optional environment key to filter lead time data to a specific environment within the project.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Optional comma-separated list of application keys to filter the chart data to specific applications.", json_schema_extra={'format': 'string'})
    from_: int | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Optional Unix timestamp in milliseconds marking the start of the time range. Defaults to 7 days before the end time if not specified.", json_schema_extra={'format': 'int64'})
    to: int | None = Field(default=None, description="Optional Unix timestamp in milliseconds marking the end of the time range. Defaults to the current time if not specified.", json_schema_extra={'format': 'int64'})
    bucket_type: str | None = Field(default=None, validation_alias="bucketType", serialization_alias="bucketType", description="Optional bucket type for aggregating data points. Choose from: `rolling` (continuous window), `hour` (hourly intervals), or `day` (daily intervals). Defaults to `rolling`.", json_schema_extra={'format': 'string'})
    bucket_ms: int | None = Field(default=None, validation_alias="bucketMs", serialization_alias="bucketMs", description="Optional duration in milliseconds for each interval on the x-axis. Defaults to one day (86400000 milliseconds). Only applies when bucketType is `hour` or `day`.", json_schema_extra={'format': 'int64'})
    group_by: str | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="Optional dimension for grouping chart data. Choose from: `application` (group by application) or `stage` (group by deployment stage). Defaults to `stage`.", json_schema_extra={'format': 'string'})
class GetLeadTimeChartRequest(StrictModel):
    """Retrieve lead time chart data for engineering insights, showing deployment frequency metrics across specified time periods and grouping dimensions."""
    query: GetLeadTimeChartRequestQuery

# Operation: get_release_frequency_chart
class GetReleaseFrequencyChartRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project's release data to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment's release data to retrieve.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Comma-separated list of application keys to filter results to specific applications. Omit to include all applications.", json_schema_extra={'format': 'string'})
    has_experiments: bool | None = Field(default=None, validation_alias="hasExperiments", serialization_alias="hasExperiments", description="Filter results to releases associated with experiments (true) or releases without experiments (false). Omit to include all releases regardless of experiment association.", json_schema_extra={'format': 'boolean'})
    global_: str | None = Field(default=None, validation_alias="global", serialization_alias="global", description="Filter to include or exclude global events. Use 'include' to show global events or 'exclude' to hide them. Defaults to 'include'.", json_schema_extra={'format': 'string'})
    group_by: str | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="Group results by a property such as 'impact' to organize the chart data. Omit for ungrouped results.", json_schema_extra={'format': 'string'})
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the time range as a Unix timestamp in milliseconds. Defaults to 7 days before the 'to' timestamp if not specified.", json_schema_extra={'format': 'date-time'})
    to: str | None = Field(default=None, description="End of the time range as a Unix timestamp in milliseconds. Defaults to the current time if not specified.", json_schema_extra={'format': 'date-time'})
    bucket_type: str | None = Field(default=None, validation_alias="bucketType", serialization_alias="bucketType", description="Time interval bucketing strategy: 'rolling' for continuous aggregation, 'hour' for hourly buckets, or 'day' for daily buckets. Defaults to 'rolling'.", json_schema_extra={'format': 'string'})
    bucket_ms: int | None = Field(default=None, validation_alias="bucketMs", serialization_alias="bucketMs", description="Duration of each time interval bucket in milliseconds. Defaults to one day (86400000 milliseconds). Only applies when bucketType is not 'rolling'.", json_schema_extra={'format': 'int64'})
class GetReleaseFrequencyChartRequest(StrictModel):
    """Retrieve release frequency chart data for a project and environment, with optional filtering by application, experiment association, and time range. Results can be grouped by impact and bucketed into time intervals for visualization."""
    query: GetReleaseFrequencyChartRequestQuery

# Operation: create_deployment_event
class CreateDeploymentEventRequestBody(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which LaunchDarkly project this deployment belongs to.")
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key (e.g., production, staging) where the deployment occurred.")
    application_key: str = Field(default=..., validation_alias="applicationKey", serialization_alias="applicationKey", description="The application key that identifies the service or component being deployed. LaunchDarkly automatically creates a new application record for each unique key. Typically matches your GitHub repository name.")
    application_kind: Literal["server", "browser", "mobile"] | None = Field(default=None, validation_alias="applicationKind", serialization_alias="applicationKind", description="The type of application being deployed. Defaults to 'server' if not specified. Choose from: server, browser, or mobile.")
    version: str = Field(default=..., description="The version identifier for this deployment. Use at least the first seven characters of the commit SHA or a git tag. Only alphanumeric characters, periods, hyphens, and underscores are allowed.")
    event_type: Literal["started", "failed", "finished", "custom"] = Field(default=..., validation_alias="eventType", serialization_alias="eventType", description="The type of deployment event being recorded. Choose from: 'started' (deployment beginning), 'finished' (deployment completed successfully), 'failed' (deployment failed), or 'custom' (for other event types).")
    event_metadata: dict[str, Any] | None = Field(default=None, validation_alias="eventMetadata", serialization_alias="eventMetadata", description="Optional JSON object with event-specific metadata such as build system version or other contextual information about this particular event.")
    deployment_metadata: dict[str, Any] | None = Field(default=None, validation_alias="deploymentMetadata", serialization_alias="deploymentMetadata", description="Optional JSON object with deployment-wide metadata such as build number or other information relevant to the entire deployment.")
class CreateDeploymentEventRequest(StrictModel):
    """Record a deployment event for an application to track deployment lifecycle and metrics in engineering insights. Events can mark deployment start, completion, failure, or custom milestones."""
    body: CreateDeploymentEventRequestBody

# Operation: list_deployments
class GetDeploymentsRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project to query deployments for.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment to query deployments for.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Comma-separated list of application keys to filter deployments by specific applications. Omit to include all applications.", json_schema_extra={'format': 'string'})
    from_: int | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Unix timestamp in milliseconds marking the start of the time range. Defaults to 7 days before the current time if not specified.", json_schema_extra={'format': 'int64'})
    to: int | None = Field(default=None, description="Unix timestamp in milliseconds marking the end of the time range. Defaults to the current time if not specified.", json_schema_extra={'format': 'int64'})
    kind: str | None = Field(default=None, description="Filter deployments by deployment kind (e.g., 'blue-green', 'canary'). Omit to include all kinds.", json_schema_extra={'format': 'string'})
    status: str | None = Field(default=None, description="Filter deployments by deployment status (e.g., 'active', 'completed'). Omit to include all statuses.", json_schema_extra={'format': 'string'})
class GetDeploymentsRequest(StrictModel):
    """Retrieve a list of deployments for a specific project and environment, with optional filtering by application, time range, kind, and status. Supports expansion to include associated pull requests and flag references."""
    query: GetDeploymentsRequestQuery

# Operation: get_deployment
class GetDeploymentRequestPath(StrictModel):
    deployment_id: str = Field(default=..., validation_alias="deploymentID", serialization_alias="deploymentID", description="The unique identifier of the deployment to retrieve. This ID is provided in the `id` field when listing deployments.", json_schema_extra={'format': 'string'})
class GetDeploymentRequest(StrictModel):
    """Retrieve a specific deployment by its ID. Optionally expand the response to include associated pull requests and flag references."""
    path: GetDeploymentRequestPath

# Operation: update_deployment
class UpdateDeploymentRequestPath(StrictModel):
    deployment_id: str = Field(default=..., validation_alias="deploymentID", serialization_alias="deploymentID", description="The unique identifier of the deployment to update. This ID is returned in the `id` field when listing deployments.", json_schema_extra={'format': 'string'})
class UpdateDeploymentRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="An array of JSON Patch operations (RFC 6902) describing the changes to apply. Each operation must include `op` (the operation type), `path` (the property to modify), and `value` (the new value for replace operations). Operations are applied in order.", examples=[[{'op': 'replace', 'path': '/status', 'value': 'finished'}]])
class UpdateDeploymentRequest(StrictModel):
    """Update a deployment's properties using JSON Patch operations. Specify the deployment by ID and provide an array of patch operations to modify its state."""
    path: UpdateDeploymentRequestPath
    body: UpdateDeploymentRequestBody

# Operation: list_flag_events
class GetFlagEventsRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project to query for flag events.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key that identifies which environment within the project to query for flag events.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Comma-separated list of application keys to filter events by specific applications.", json_schema_extra={'format': 'string'})
    query: str | None = Field(default=None, description="Filter events by flag key using a search query string.", json_schema_extra={'format': 'string'})
    impact_size: str | None = Field(default=None, validation_alias="impactSize", serialization_alias="impactSize", description="Filter events by the magnitude of user impact: `none` (no change), `small` (less than 20% change), `medium` (20-80% change), or `large` (more than 80% change).", json_schema_extra={'format': 'string'})
    has_experiments: bool | None = Field(default=None, validation_alias="hasExperiments", serialization_alias="hasExperiments", description="Filter to show only events associated with experiments (`true`) or events without experiments (`false`).", json_schema_extra={'format': 'boolean'})
    global_: str | None = Field(default=None, validation_alias="global", serialization_alias="global", description="Include or exclude global events from results. Defaults to `include`. Valid options are `include` or `exclude`.", json_schema_extra={'format': 'string'})
    from_: int | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Unix timestamp in milliseconds marking the start of the time range. Defaults to 7 days ago if not specified.", json_schema_extra={'format': 'int64'})
    to: int | None = Field(default=None, description="Unix timestamp in milliseconds marking the end of the time range. Defaults to the current time if not specified.", json_schema_extra={'format': 'int64'})
class GetFlagEventsRequest(StrictModel):
    """Retrieve a list of flag events for a specific project and environment, with optional filtering by application, flag key, impact size, and experiment association. Supports expanding the response to include experiment details."""
    query: GetFlagEventsRequestQuery

# Operation: create_insight_group
class CreateInsightGroupRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the insight group (e.g., 'Production - All Apps'). Used for display and identification in the UI.")
    key: str = Field(default=..., description="A unique identifier key for the insight group in kebab-case format (e.g., 'default-production-all-apps'). Used for API references and internal lookups.")
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that this insight group belongs to. Determines which project's data and configuration the group operates within.")
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key (e.g., 'production', 'staging') that this insight group monitors. Scopes insights to a specific deployment environment.")
    application_keys: list[str] | None = Field(default=None, validation_alias="applicationKeys", serialization_alias="applicationKeys", description="Optional list of application keys to include in this insight group (e.g., ['billing-service', 'inventory-service']). If omitted, the group will automatically include data from all applications in the specified project and environment.")
class CreateInsightGroupRequest(StrictModel):
    """Create a new insight group to organize and monitor engineering insights across a specific project and environment. Optionally scope the group to specific applications."""
    body: CreateInsightGroupRequestBody

# Operation: list_insight_groups
class GetInsightGroupsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Filter the insight groups list by group name. Supports partial string matching to find groups by name.", json_schema_extra={'format': 'string'})
class GetInsightGroupsRequest(StrictModel):
    """Retrieve a list of insight groups for which you are collecting engineering insights. Optionally filter by group name and expand the response to include scores, environment details, or metadata indicators."""
    query: GetInsightGroupsRequestQuery | None = None

# Operation: get_insight_group
class GetInsightGroupRequestPath(StrictModel):
    insight_group_key: str = Field(default=..., validation_alias="insightGroupKey", serialization_alias="insightGroupKey", description="The unique identifier for the insight group to retrieve.", json_schema_extra={'format': 'string'})
class GetInsightGroupRequest(StrictModel):
    """Retrieve a specific insight group by its key, with optional expansion to include scoring details and environment associations used in engineering insights metrics."""
    path: GetInsightGroupRequestPath

# Operation: update_insight_group
class PatchInsightGroupRequestPath(StrictModel):
    insight_group_key: str = Field(default=..., validation_alias="insightGroupKey", serialization_alias="insightGroupKey", description="The unique identifier for the insight group to update.", json_schema_extra={'format': 'string'})
class PatchInsightGroupRequestBody(StrictModel):
    body: list[PatchOperation] = Field(default=..., description="A JSON Patch document (RFC 6902) describing the updates to apply. Each operation must include 'op' (the operation type), 'path' (the JSON pointer to the field), and 'value' (the new value for replace operations). Common operations include 'replace' to change field values.", examples=[[{'op': 'replace', 'path': '/name', 'value': 'Prod group'}]])
class PatchInsightGroupRequest(StrictModel):
    """Update an insight group using JSON Patch operations. Specify the changes you want to make (such as renaming the group) via a JSON Patch document following RFC 6902 standards."""
    path: PatchInsightGroupRequestPath
    body: PatchInsightGroupRequestBody

# Operation: delete_insight_group
class DeleteInsightGroupRequestPath(StrictModel):
    insight_group_key: str = Field(default=..., validation_alias="insightGroupKey", serialization_alias="insightGroupKey", description="The unique identifier for the insight group to delete. This is a string value that uniquely identifies the insight group within the system.", json_schema_extra={'format': 'string'})
class DeleteInsightGroupRequest(StrictModel):
    """Permanently delete an insight group by its unique key. This operation removes the insight group and all associated data."""
    path: DeleteInsightGroupRequestPath

# Operation: get_insights_scores
class GetInsightsScoresRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project. Required to scope the insights scores to a specific project.", json_schema_extra={'format': 'string'})
    environment_key: str = Field(default=..., validation_alias="environmentKey", serialization_alias="environmentKey", description="The unique identifier for the environment within the project. Required to retrieve environment-specific insight metrics.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Optional comma-separated list of application identifiers to filter insights scores to specific applications. When omitted, scores for all applications in the environment are returned.", json_schema_extra={'format': 'string'})
class GetInsightsScoresRequest(StrictModel):
    """Retrieve engineering insights scores for a specified project and environment, optionally filtered by one or more applications. This data powers engineering insights metrics dashboards and performance analysis views."""
    query: GetInsightsScoresRequestQuery

# Operation: list_pull_requests
class GetPullRequestsRequestQuery(StrictModel):
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key that identifies which project's pull requests to retrieve.", json_schema_extra={'format': 'string'})
    environment_key: str | None = Field(default=None, validation_alias="environmentKey", serialization_alias="environmentKey", description="The environment key, required only when sorting results by lead time metrics.", json_schema_extra={'format': 'string'})
    application_key: str | None = Field(default=None, validation_alias="applicationKey", serialization_alias="applicationKey", description="Filter results to pull requests deployed to specific applications. Provide as a comma-separated list of application keys.", json_schema_extra={'format': 'string'})
    status: str | None = Field(default=None, description="Filter results by pull request status. Valid options are: open, merged, closed, or deployed.", json_schema_extra={'format': 'string'})
    query: str | None = Field(default=None, description="Search pull requests by title or author name. Performs a text match against these fields.", json_schema_extra={'format': 'string'})
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range as a Unix timestamp in milliseconds. Defaults to 7 days before the end date if not specified.", json_schema_extra={'format': 'date-time'})
    to: str | None = Field(default=None, description="End of the date range as a Unix timestamp in milliseconds. Defaults to the current time if not specified.", json_schema_extra={'format': 'date-time'})
class GetPullRequestsRequest(StrictModel):
    """Retrieve a list of pull requests for a project with optional filtering by status, application, date range, and search terms. Supports expanding the response to include deployment details, flag references, and lead time metrics."""
    query: GetPullRequestsRequestQuery

# Operation: associate_repositories_with_projects
class AssociateRepositoriesAndProjectsRequestBody(StrictModel):
    mappings: list[InsightsRepositoryProject] = Field(default=..., description="Array of repository-to-project mappings. Each mapping object should specify which repository associates with which project. Order is preserved and processed sequentially.")
class AssociateRepositoriesAndProjectsRequest(StrictModel):
    """Create or update associations between repositories and projects. Use this operation to map one or more repositories to their corresponding projects for engineering insights tracking."""
    body: AssociateRepositoriesAndProjectsRequestBody

# Operation: remove_repository_project_association
class DeleteRepositoryProjectRequestPath(StrictModel):
    repository_key: str = Field(default=..., validation_alias="repositoryKey", serialization_alias="repositoryKey", description="The unique identifier for the repository from which the project association will be removed.", json_schema_extra={'format': 'string'})
    project_key: str = Field(default=..., validation_alias="projectKey", serialization_alias="projectKey", description="The unique identifier for the project to be disassociated from the repository.", json_schema_extra={'format': 'string'})
class DeleteRepositoryProjectRequest(StrictModel):
    """Remove the association between a repository and a project in engineering insights. This operation disassociates the specified project from the given repository."""
    path: DeleteRepositoryProjectRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AccessAllowedReason(PermissiveModel):
    resources: list[str] | None = Field(None, description="Resource specifier strings")
    not_resources: list[str] | None = Field(None, validation_alias="notResources", serialization_alias="notResources", description="Targeted resources are the resources NOT in this list. The <code>resources</code> and <code>notActions</code> fields must be empty to use this field.")
    actions: list[str] | None = Field(None, description="Actions to perform on a resource")
    not_actions: list[str] | None = Field(None, validation_alias="notActions", serialization_alias="notActions", description="Targeted actions are the actions NOT in this list. The <code>actions</code> and <code>notResources</code> fields must be empty to use this field.")
    effect: Literal["allow", "deny"] = Field(..., description="Whether this statement should allow or deny actions on the resources.")
    role_name: str | None = None

class AccessAllowedRep(PermissiveModel):
    action: str
    reason: AccessAllowedReason

class AccessDeniedReason(PermissiveModel):
    resources: list[str] | None = Field(None, description="Resource specifier strings")
    not_resources: list[str] | None = Field(None, validation_alias="notResources", serialization_alias="notResources", description="Targeted resources are the resources NOT in this list. The <code>resources</code> and <code>notActions</code> fields must be empty to use this field.")
    actions: list[str] | None = Field(None, description="Actions to perform on a resource")
    not_actions: list[str] | None = Field(None, validation_alias="notActions", serialization_alias="notActions", description="Targeted actions are the actions NOT in this list. The <code>actions</code> and <code>notResources</code> fields must be empty to use this field.")
    effect: Literal["allow", "deny"] = Field(..., description="Whether this statement should allow or deny actions on the resources.")
    role_name: str | None = None

class AccessDenied(PermissiveModel):
    action: str
    reason: AccessDeniedReason

class Access(PermissiveModel):
    denied: list[AccessDenied]
    allowed: list[AccessAllowedRep]

class AgentGraphEdge(PermissiveModel):
    """An edge in an agent graph connecting two AI Configs"""
    key: str = Field(..., description="A unique key for this edge within the graph")
    source_config: str = Field(..., validation_alias="sourceConfig", serialization_alias="sourceConfig", description="The AI Config key that is the source of this edge")
    target_config: str = Field(..., validation_alias="targetConfig", serialization_alias="targetConfig", description="The AI Config key that is the target of this edge")
    handoff: dict[str, Any] | None = Field(None, description="The handoff options from the source AI Config to the target AI Config")

class AgentGraphEdgePost(PermissiveModel):
    """An edge in an agent graph connecting two AI Configs"""
    key: str = Field(..., description="A unique key for this edge within the graph")
    source_config: str = Field(..., validation_alias="sourceConfig", serialization_alias="sourceConfig", description="The AI Config key that is the source of this edge")
    target_config: str = Field(..., validation_alias="targetConfig", serialization_alias="targetConfig", description="The AI Config key that is the target of this edge")
    handoff: dict[str, Any] | None = Field(None, description="The handoff options from the source AI Config to the target AI Config")

class AgentOptimizationAcceptanceStatement(PermissiveModel):
    statement: str
    threshold: float = Field(..., json_schema_extra={'format': 'double'})

class AgentOptimizationJudge(PermissiveModel):
    key: str
    threshold: float = Field(..., json_schema_extra={'format': 'double'})

class AiConfigsSummary(PermissiveModel):
    count: int

class AnnouncementPatchOperation(PermissiveModel):
    op: str = Field(..., description="The type of operation to perform")
    path: str = Field(..., description="A JSON Pointer string specifying the part of the document to operate on")
    value: Any | None = Field(None, description="A JSON value used in \"add\", \"replace\", and \"test\" operations")

class ApprovalSettings(PermissiveModel):
    required: bool = Field(..., description="If approvals are required for this environment")
    bypass_approvals_for_pending_changes: bool = Field(..., validation_alias="bypassApprovalsForPendingChanges", serialization_alias="bypassApprovalsForPendingChanges", description="Whether to skip approvals for pending changes")
    min_num_approvals: int = Field(..., validation_alias="minNumApprovals", serialization_alias="minNumApprovals", description="Sets the amount of approvals required before a member can apply a change. The minimum is one and the maximum is five.")
    can_review_own_request: bool = Field(..., validation_alias="canReviewOwnRequest", serialization_alias="canReviewOwnRequest", description="Allow someone who makes an approval request to apply their own change")
    can_apply_declined_changes: bool = Field(..., validation_alias="canApplyDeclinedChanges", serialization_alias="canApplyDeclinedChanges", description="Allow applying the change as long as at least one person has approved")
    auto_apply_approved_changes: bool | None = Field(None, validation_alias="autoApplyApprovedChanges", serialization_alias="autoApplyApprovedChanges", description="Automatically apply changes that have been approved by all reviewers. This field is only applicable for approval services other than LaunchDarkly.")
    service_kind: str = Field(..., validation_alias="serviceKind", serialization_alias="serviceKind", description="Which service to use for managing approvals")
    service_config: dict[str, Any] = Field(..., validation_alias="serviceConfig", serialization_alias="serviceConfig")
    required_approval_tags: list[str] = Field(..., validation_alias="requiredApprovalTags", serialization_alias="requiredApprovalTags", description="Require approval only on flags with the provided tags. Otherwise all flags will require approval.")
    service_kind_configuration_id: str | None = Field(None, validation_alias="serviceKindConfigurationId", serialization_alias="serviceKindConfigurationId", description="Optional field for integration configuration ID of a custom approval integration. This is an Enterprise-only feature.")

class ClientSideAvailability(PermissiveModel):
    using_mobile_key: bool | None = Field(None, validation_alias="usingMobileKey", serialization_alias="usingMobileKey")
    using_environment_id: bool | None = Field(None, validation_alias="usingEnvironmentId", serialization_alias="usingEnvironmentId")

class CoreLink(PermissiveModel):
    href: str
    type_: str = Field(..., validation_alias="type", serialization_alias="type")

class CustomProperty(PermissiveModel):
    name: str = Field(..., description="The name of the custom property of this type.")
    value: list[str] = Field(..., description="An array of values for the custom property data to associate with this flag.")

class Defaults(PermissiveModel):
    on_variation: int = Field(..., validation_alias="onVariation", serialization_alias="onVariation", description="The index, from the array of variations for this flag, of the variation to serve by default when targeting is on.")
    off_variation: int = Field(..., validation_alias="offVariation", serialization_alias="offVariation", description="The index, from the array of variations for this flag, of the variation to serve by default when targeting is off.")

class Extinction(PermissiveModel):
    revision: str = Field(..., description="The identifier for the revision where flag became extinct. For example, a commit SHA.")
    message: str = Field(..., description="Description of the extinction. For example, the commit message for the revision.")
    time_: int = Field(..., validation_alias="time", serialization_alias="time", description="Time of extinction")
    flag_key: str = Field(..., validation_alias="flagKey", serialization_alias="flagKey", description="The feature flag key")
    proj_key: str = Field(..., validation_alias="projKey", serialization_alias="projKey", description="The project key")

class FlagInput(PermissiveModel):
    rule_id: str = Field(..., validation_alias="ruleId", serialization_alias="ruleId", description="The ID of the variation or rollout of the flag to use. Use \"fallthrough\" for the default targeting behavior when the flag is on.")
    flag_config_version: int = Field(..., validation_alias="flagConfigVersion", serialization_alias="flagConfigVersion", description="The flag version")
    not_in_experiment_variation_id: str | None = Field(None, validation_alias="notInExperimentVariationId", serialization_alias="notInExperimentVariationId", description="The ID of the variation to route traffic not part of the experiment analysis to. Defaults to variation ID of baseline treatment, if set.")

class FlagPrerequisitePost(PermissiveModel):
    key: str = Field(..., description="Flag key of the prerequisite flag")
    variation_id: str = Field(..., validation_alias="variationId", serialization_alias="variationId", description="ID of a variation of the prerequisite flag")

class HunkRep(PermissiveModel):
    starting_line_number: int = Field(..., validation_alias="startingLineNumber", serialization_alias="startingLineNumber", description="Line number of beginning of code reference hunk")
    lines: str | None = Field(None, description="Contextual lines of code that include the referenced feature flag")
    proj_key: str | None = Field(None, validation_alias="projKey", serialization_alias="projKey", description="The project key")
    flag_key: str | None = Field(None, validation_alias="flagKey", serialization_alias="flagKey", description="The feature flag key")
    aliases: list[str] | None = Field(None, description="An array of flag key aliases")

class InitiatorRep(PermissiveModel):
    name: str | None = Field(None, description="The name of the member who initiated the export")
    email: str | None = Field(None, description="The email address of the member who initiated the export")

class InsightsRepositoryProject(PermissiveModel):
    repository_key: str = Field(..., validation_alias="repositoryKey", serialization_alias="repositoryKey", description="The repository key")
    project_key: str = Field(..., validation_alias="projectKey", serialization_alias="projectKey", description="The project key")

class Instruction(RootModel[dict[str, Any]]):
    pass

class Instructions(RootModel[list[Instruction]]):
    pass

class IntegrationStatus(PermissiveModel):
    display: str
    value: str

class IntegrationMetadata(PermissiveModel):
    external_id: str = Field(..., validation_alias="externalId", serialization_alias="externalId")
    external_status: IntegrationStatus = Field(..., validation_alias="externalStatus", serialization_alias="externalStatus")
    external_url: str = Field(..., validation_alias="externalUrl", serialization_alias="externalUrl")
    last_checked: int = Field(..., validation_alias="lastChecked", serialization_alias="lastChecked")

class IntegrationStatusRep(PermissiveModel):
    status_code: int | None = Field(None, validation_alias="statusCode", serialization_alias="statusCode")
    response_body: str | None = Field(None, validation_alias="responseBody", serialization_alias="responseBody")
    timestamp: int | None = None

class IntegrationSubscriptionStatusRep(PermissiveModel):
    success_count: int | None = Field(None, validation_alias="successCount", serialization_alias="successCount")
    last_success: int | None = Field(None, validation_alias="lastSuccess", serialization_alias="lastSuccess")
    last_error: int | None = Field(None, validation_alias="lastError", serialization_alias="lastError")
    error_count: int | None = Field(None, validation_alias="errorCount", serialization_alias="errorCount")
    errors: list[IntegrationStatusRep] | None = None

class JudgeAttachment(PermissiveModel):
    judge_config_key: str = Field(..., validation_alias="judgeConfigKey", serialization_alias="judgeConfigKey", description="Key of the judge AI Config")
    sampling_rate: float = Field(..., validation_alias="samplingRate", serialization_alias="samplingRate", description="Sampling rate for this judge attachment (0.0 to 1.0)", ge=0, le=1, json_schema_extra={'format': 'float'})

class LastSeenMetadata(PermissiveModel):
    token_id: str | None = Field(None, validation_alias="tokenId", serialization_alias="tokenId", description="The ID of the token used in the member's last session")

class Link(PermissiveModel):
    href: str | None = None
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class Client(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    name: str = Field(..., description="Client name")
    description: str | None = Field(None, description="Client description")
    account_id: str = Field(..., validation_alias="_accountId", serialization_alias="_accountId", description="The account ID the client is registered under")
    client_id: str = Field(..., validation_alias="_clientId", serialization_alias="_clientId", description="The client's unique ID")
    client_secret: str | None = Field(None, validation_alias="_clientSecret", serialization_alias="_clientSecret", description="The client secret. This will only be shown upon creation.")
    redirect_uri: str = Field(..., validation_alias="redirectUri", serialization_alias="redirectUri", description="The client's redirect URI")
    creation_date: int = Field(..., validation_alias="_creationDate", serialization_alias="_creationDate", description="Timestamp of client creation date")

class ContextRecord(PermissiveModel):
    last_seen: str | None = Field(None, validation_alias="lastSeen", serialization_alias="lastSeen", description="Timestamp of the last time an evaluation occurred for this context", json_schema_extra={'format': 'date-time'})
    application_id: str | None = Field(None, validation_alias="applicationId", serialization_alias="applicationId", description="An identifier representing the application where the LaunchDarkly SDK is running")
    context: Any = Field(..., description="The context, including its kind and attributes")
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    access: Access | None = Field(None, validation_alias="_access", serialization_alias="_access", description="Details on the allowed and denied actions for this context instance")
    associated_contexts: int | None = Field(None, validation_alias="associatedContexts", serialization_alias="associatedContexts", description="The total number of associated contexts. Associated contexts are contexts that have appeared in the same context instance, that is, they were part of the same flag evaluation.")

class Contexts(PermissiveModel):
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    total_count: int | None = Field(None, validation_alias="totalCount", serialization_alias="totalCount", description="The number of contexts")
    environment_id: str = Field(..., validation_alias="_environmentId", serialization_alias="_environmentId", description="The environment ID where the context was evaluated")
    continuation_token: str | None = Field(None, validation_alias="continuationToken", serialization_alias="continuationToken", description="An obfuscated string that references the last context instance on the previous page of results. You can use this for pagination, however, we recommend using the <code>next</code> link instead.")
    items: list[ContextRecord] = Field(..., description="A collection of contexts. Can include multiple versions of contexts that have the same <code>kind</code> and <code>key</code>, but different <code>applicationId</code>s.")

class Environment(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The ID for the environment. Use this as the client-side ID for authorization in some client-side SDKs, and to associate LaunchDarkly environments with CDN integrations in edge SDKs.")
    key: str = Field(..., description="A project-unique key for the new environment")
    name: str = Field(..., description="A human-friendly name for the new environment")
    api_key: str = Field(..., validation_alias="apiKey", serialization_alias="apiKey", description="The SDK key for the environment. Use this for authorization in server-side SDKs.")
    mobile_key: str = Field(..., validation_alias="mobileKey", serialization_alias="mobileKey", description="The mobile key for the environment. Use this for authorization in mobile SDKs.")
    color: str = Field(..., description="The color used to indicate this environment in the UI")
    default_ttl: int = Field(..., validation_alias="defaultTtl", serialization_alias="defaultTtl", description="The default time (in minutes) that the PHP SDK can cache feature flag rules locally")
    secure_mode: bool = Field(..., validation_alias="secureMode", serialization_alias="secureMode", description="Ensures that one end user of the client-side SDK cannot inspect the variations for another end user")
    access: Access | None = Field(None, validation_alias="_access", serialization_alias="_access")
    default_track_events: bool = Field(..., validation_alias="defaultTrackEvents", serialization_alias="defaultTrackEvents", description="Enables tracking detailed information for new flags by default")
    require_comments: bool = Field(..., validation_alias="requireComments", serialization_alias="requireComments", description="Whether members who modify flags and segments through the LaunchDarkly user interface are required to add a comment")
    confirm_changes: bool = Field(..., validation_alias="confirmChanges", serialization_alias="confirmChanges", description="Whether members who modify flags and segments through the LaunchDarkly user interface are required to confirm those changes")
    tags: list[str] = Field(..., description="A list of tags for this environment")
    approval_settings: ApprovalSettings | None = Field(None, validation_alias="approvalSettings", serialization_alias="approvalSettings", description="Details about the approval settings for flags in this environment")
    resource_approval_settings: dict[str, ApprovalSettings] | None = Field(None, validation_alias="resourceApprovalSettings", serialization_alias="resourceApprovalSettings", description="Details about the approval settings for other resources in this environment, organized by resource kind (for example, \"aiconfig\" and \"segment\")")
    critical: bool = Field(..., description="Whether the environment is critical")

class EnvironmentSummary(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    key: str = Field(..., description="A project-unique key for the environment")
    name: str = Field(..., description="A human-friendly name for the environment")
    color: str = Field(..., description="The color used to indicate this environment in the UI")

class Environments(PermissiveModel):
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    total_count: int | None = Field(None, validation_alias="totalCount", serialization_alias="totalCount", description="The number of environments returned")
    items: list[Environment] = Field(..., description="An array of environments")

class Export(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The export ID")
    segment_key: str = Field(..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The segment key")
    creation_time: int = Field(..., validation_alias="creationTime", serialization_alias="creationTime", description="Timestamp of when this export was created")
    status: str = Field(..., description="The export status")
    size_bytes: int = Field(..., validation_alias="sizeBytes", serialization_alias="sizeBytes", description="The export size, in bytes", json_schema_extra={'format': 'int64'})
    size: str = Field(..., description="The export size, with units")
    initiator: InitiatorRep = Field(..., description="Details on the member who initiated the export")
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources, including the location of the exported file")

class MemberPermissionGrantSummaryRep(PermissiveModel):
    action_set: str | None = Field(None, validation_alias="actionSet", serialization_alias="actionSet", description="The name of the group of related actions to allow. A permission grant may have either an <code>actionSet</code> or a list of <code>actions</code> but not both at the same time.")
    actions: list[str] | None = Field(None, description="A list of actions to allow. A permission grant may have either an <code>actionSet</code> or a list of <code>actions</code> but not both at the same time.")
    resource: str = Field(..., description="The resource for which the actions are allowed")

class MemberSummary(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The member's ID")
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName", description="The member's first name")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName", description="The member's last name")
    role: str = Field(..., description="The member's base role. If the member has no additional roles, this role will be in effect.")
    email: str = Field(..., description="The member's email address")

class MemberTeamSummaryRep(PermissiveModel):
    custom_role_keys: list[str] = Field(..., validation_alias="customRoleKeys", serialization_alias="customRoleKeys", description="A list of keys of the custom roles this team has access to")
    key: str = Field(..., description="The team key")
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links")
    name: str = Field(..., description="The team name")

class Message(PermissiveModel):
    content: str
    role: str

class MetricInMetricGroupInput(PermissiveModel):
    key: str = Field(..., description="The metric key")
    name_in_group: str = Field(..., validation_alias="nameInGroup", serialization_alias="nameInGroup", description="Name of the metric when used within the associated metric group. Can be different from the original name of the metric")

class MetricInput(PermissiveModel):
    key: str = Field(..., description="The metric key")
    is_group: bool | None = Field(None, validation_alias="isGroup", serialization_alias="isGroup", description="Whether this is a metric group (true) or a metric (false). Defaults to false")
    primary: bool | None = Field(None, description="Deprecated, use <code>primarySingleMetricKey</code> and <code>primaryFunnelKey</code>. Whether this is a primary metric (true) or a secondary metric (false)")

class Metrics(PermissiveModel):
    input_tokens: int | None = Field(None, validation_alias="inputTokens", serialization_alias="inputTokens")
    output_tokens: int | None = Field(None, validation_alias="outputTokens", serialization_alias="outputTokens")
    total_tokens: int | None = Field(None, validation_alias="totalTokens", serialization_alias="totalTokens")
    generation_count: int | None = Field(None, validation_alias="generationCount", serialization_alias="generationCount", description="Number of attempted generations")
    generation_success_count: int | None = Field(None, validation_alias="generationSuccessCount", serialization_alias="generationSuccessCount", description="Number of successful generations")
    generation_error_count: int | None = Field(None, validation_alias="generationErrorCount", serialization_alias="generationErrorCount", description="Number of generations with errors")
    thumbs_up: int | None = Field(None, validation_alias="thumbsUp", serialization_alias="thumbsUp")
    thumbs_down: int | None = Field(None, validation_alias="thumbsDown", serialization_alias="thumbsDown")
    duration_ms: int | None = Field(None, validation_alias="durationMs", serialization_alias="durationMs")
    time_to_first_token_ms: int | None = Field(None, validation_alias="timeToFirstTokenMs", serialization_alias="timeToFirstTokenMs")
    satisfaction_rating: float | None = Field(None, validation_alias="satisfactionRating", serialization_alias="satisfactionRating", description="A value between 0 and 1 representing satisfaction rating", ge=0, le=1, json_schema_extra={'format': 'float'})
    input_cost: float | None = Field(None, validation_alias="inputCost", serialization_alias="inputCost", description="Cost of input tokens in USD", json_schema_extra={'format': 'double'})
    output_cost: float | None = Field(None, validation_alias="outputCost", serialization_alias="outputCost", description="Cost of output tokens in USD", json_schema_extra={'format': 'double'})
    judge_accuracy: float | None = Field(None, validation_alias="judgeAccuracy", serialization_alias="judgeAccuracy", description="Average accuracy judge score (0.0-1.0)", ge=0, le=1, json_schema_extra={'format': 'float'})
    judge_relevance: float | None = Field(None, validation_alias="judgeRelevance", serialization_alias="judgeRelevance", description="Average relevance judge score (0.0-1.0)", ge=0, le=1, json_schema_extra={'format': 'float'})
    judge_toxicity: float | None = Field(None, validation_alias="judgeToxicity", serialization_alias="judgeToxicity", description="Average toxicity judge score (0.0-1.0)", ge=0, le=1, json_schema_extra={'format': 'float'})

class MetricsSummary(PermissiveModel):
    count: int

class ParentAndSelfLinks(PermissiveModel):
    """The location and content type of related resources"""
    self: CoreLink
    parent: CoreLink

class ExpandedAiConfig(PermissiveModel):
    """AI Config representation for Views API - contains only fields actually used by the Views service"""
    key: str | None = Field(None, description="A unique key used to reference the AI config")
    name: str | None = Field(None, description="A human-friendly name for the AI config")
    tags: list[str] | None = Field(None, description="Tags for the AI config")
    description: str | None = Field(None, description="Description of the AI config")
    version: int | None = Field(None, description="Version of the AI config")
    created_at: int | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt", description="Creation date in milliseconds", json_schema_extra={'format': 'int64'})
    updated_at: int | None = Field(None, validation_alias="updatedAt", serialization_alias="updatedAt", description="Last modification date in milliseconds", json_schema_extra={'format': 'int64'})
    flag_key: str | None = Field(None, validation_alias="flagKey", serialization_alias="flagKey", description="Key of the flag that this AI config is attached to")
    links: ParentAndSelfLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ExpandedLinkedAiConfigs(PermissiveModel):
    items: list[ExpandedAiConfig]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ExpandedMetric(PermissiveModel):
    """Metric representation for Views API - contains only fields actually used by the Views service"""
    key: str | None = Field(None, description="A unique key used to reference the metric")
    name: str | None = Field(None, description="A human-friendly name for the metric")
    creation_date: int | None = Field(None, validation_alias="creationDate", serialization_alias="creationDate", description="Creation date in milliseconds", json_schema_extra={'format': 'int64'})
    last_modified: int | None = Field(None, validation_alias="lastModified", serialization_alias="lastModified", description="Last modification date in milliseconds", json_schema_extra={'format': 'int64'})
    is_active: bool | None = Field(None, validation_alias="isActive", serialization_alias="isActive", description="Whether the metric is active")
    event_key: str | None = Field(None, validation_alias="eventKey", serialization_alias="eventKey", description="Event key for the metric")
    id_: str | None = Field(None, validation_alias="_id", serialization_alias="_id", description="ID of the metric")
    version_id: str | None = Field(None, validation_alias="_versionId", serialization_alias="_versionId", description="Version ID of the metric")
    kind: str | None = Field(None, description="Kind of the Metric")
    category: str | None = Field(None, description="Category of the Metric")
    description: str | None = Field(None, description="Description of the Metric")
    is_numeric: bool | None = Field(None, validation_alias="isNumeric", serialization_alias="isNumeric")
    last_seen: int | None = Field(None, validation_alias="lastSeen", serialization_alias="lastSeen", description="Last seen date in milliseconds", json_schema_extra={'format': 'int64'})
    links: ParentAndSelfLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ExpandedLinkedMetrics(PermissiveModel):
    items: list[ExpandedMetric]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ExpandedSegment(PermissiveModel):
    """Segment representation for Views API - contains only fields actually used by the Views service"""
    key: str = Field(..., description="A unique key used to reference the segment")
    name: str = Field(..., description="A human-friendly name for the segment")
    environment_id: str | None = Field(None, validation_alias="environmentId", serialization_alias="environmentId", description="Environment ID of the segment")
    environment_key: str | None = Field(None, validation_alias="environmentKey", serialization_alias="environmentKey", description="Environment key of the segment")
    description: str | None = Field(None, description="Description of the segment")
    creation_date: int | None = Field(None, validation_alias="creationDate", serialization_alias="creationDate", description="Creation date in milliseconds", json_schema_extra={'format': 'int64'})
    last_modified_date: int | None = Field(None, validation_alias="lastModifiedDate", serialization_alias="lastModifiedDate", description="Last modification date in milliseconds", json_schema_extra={'format': 'int64'})
    deleted: bool | None = Field(None, description="Whether the segment is deleted")
    tags: list[str] | None = Field(None, description="Tags for the segment")
    unbounded: bool | None = Field(None, description="Whether the segment is unbounded")
    version: int | None = Field(None, description="Version of the segment")
    generation: int | None = Field(None, description="Generation of the segment")
    links: ParentAndSelfLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ExpandedLinkedResourcesSegments(PermissiveModel):
    items: list[ExpandedSegment]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ExpandedLinkedSegments(PermissiveModel):
    """Details on linked segments for a view - requires passing the 'allSegments' expand field"""
    items: list[ExpandedSegment]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class PatchOperation(PermissiveModel):
    op: str = Field(..., description="The type of operation to perform")
    path: str = Field(..., description="A JSON Pointer string specifying the part of the document to operate on")
    value: Any | None = Field(None, description="A JSON value used in \"add\", \"replace\", and \"test\" operations")

class PatchSegmentExpiringTargetInstruction(PermissiveModel):
    kind: Literal["addExpiringTarget", "updateExpiringTarget", "removeExpiringTarget"] = Field(..., description="The type of change to make to the context's removal date from this segment")
    context_key: str = Field(..., validation_alias="contextKey", serialization_alias="contextKey", description="A unique key used to represent the context")
    context_kind: str = Field(..., validation_alias="contextKind", serialization_alias="contextKind", description="The kind of context")
    target_type: Literal["included", "excluded"] = Field(..., validation_alias="targetType", serialization_alias="targetType", description="The segment's target type")
    value: int | None = Field(None, description="The time, in Unix milliseconds, when the context should be removed from this segment. Required if <code>kind</code> is <code>addExpiringTarget</code> or <code>updateExpiringTarget</code>.", json_schema_extra={'format': 'int64'})
    version: int | None = Field(None, description="The version of the expiring target to update. Optional and only used if <code>kind</code> is <code>updateExpiringTarget</code>. If included, update will fail if version doesn't match current version of the expiring target.")

class PatchSegmentInstruction(PermissiveModel):
    kind: Literal["addExpireUserTargetDate", "updateExpireUserTargetDate", "removeExpireUserTargetDate"] = Field(..., description="The type of change to make to the user's removal date from this segment")
    user_key: str = Field(..., validation_alias="userKey", serialization_alias="userKey", description="A unique key used to represent the user")
    target_type: Literal["included", "excluded"] = Field(..., validation_alias="targetType", serialization_alias="targetType", description="The segment's target type")
    value: int | None = Field(None, description="The time, in Unix milliseconds, when the user should be removed from this segment. Required if <code>kind</code> is <code>addExpireUserTargetDate</code> or <code>updateExpireUserTargetDate</code>.")
    version: int | None = Field(None, description="The version of the segment to update. Required if <code>kind</code> is <code>updateExpireUserTargetDate</code>.")

class PermissionGrantInput(PermissiveModel):
    action_set: Literal["maintainTeam"] | None = Field(None, validation_alias="actionSet", serialization_alias="actionSet", description="A group of related actions to allow. Specify either <code>actionSet</code> or <code>actions</code>. Use <code>maintainTeam</code> to add team maintainers.")
    actions: list[str] | None = Field(None, description="A list of actions to allow. Specify either <code>actionSet</code> or <code>actions</code>. To learn more, read [Role actions](https://launchdarkly.com/docs/ld-docs/home/account/role-actions).")
    member_i_ds: list[str] | None = Field(None, validation_alias="memberIDs", serialization_alias="memberIDs", description="A list of member IDs who receive the permission grant.")

class PhaseConfiguration(RootModel[dict[str, Any]]):
    pass

class Project(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The ID of this project")
    key: str = Field(..., description="The key of this project")
    include_in_snippet_by_default: bool = Field(..., validation_alias="includeInSnippetByDefault", serialization_alias="includeInSnippetByDefault", description="Whether or not flags created in this project are made available to the client-side JavaScript SDK by default")
    default_client_side_availability: ClientSideAvailability | None = Field(None, validation_alias="defaultClientSideAvailability", serialization_alias="defaultClientSideAvailability", description="Describes which client-side SDKs can use new flags by default")
    name: str = Field(..., description="A human-friendly name for the project")
    access: Access | None = Field(None, validation_alias="_access", serialization_alias="_access", description="Details on the allowed and denied actions for this project")
    tags: list[str] = Field(..., description="A list of tags for the project")
    default_release_pipeline_key: str | None = Field(None, validation_alias="defaultReleasePipelineKey", serialization_alias="defaultReleasePipelineKey", description="The key of the default release pipeline for this project")
    environments: Environments | None = Field(None, description="A paginated list of environments for the project. By default this field is omitted unless expanded by the client.")

class Projects(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="A link to this resource.")
    items: list[Project] = Field(..., description="List of projects.")
    total_count: int | None = Field(None, validation_alias="totalCount", serialization_alias="totalCount")

class RandomizationUnitInput(PermissiveModel):
    randomization_unit: str = Field(..., validation_alias="randomizationUnit", serialization_alias="randomizationUnit", description="The unit of randomization. Must match the key of an existing context kind in this project.")
    default: bool | None = Field(None, description="If true, any experiment iterations created within this project will default to using this randomization unit. A project can only have one default randomization unit.")
    standard_randomization_unit: str | None = Field(None, validation_alias="standardRandomizationUnit", serialization_alias="standardRandomizationUnit", description="(deprecated) This field is deprecated and will be removed. Use randomizationUnit instead.")

class ReferenceRep(PermissiveModel):
    path: str = Field(..., description="File path of the reference")
    hint: str | None = Field(None, description="Programming language used in the file")
    hunks: list[HunkRep]

class ReleaseGuardianConfiguration(PermissiveModel):
    monitoring_window_milliseconds: int = Field(..., validation_alias="monitoringWindowMilliseconds", serialization_alias="monitoringWindowMilliseconds", description="The monitoring window in milliseconds", json_schema_extra={'format': 'int64'})
    rollout_weight: int = Field(..., validation_alias="rolloutWeight", serialization_alias="rolloutWeight", description="The rollout weight percentage")
    rollback_on_regression: bool = Field(..., validation_alias="rollbackOnRegression", serialization_alias="rollbackOnRegression", description="Whether or not to roll back on regression")
    randomization_unit: str | None = Field(None, validation_alias="randomizationUnit", serialization_alias="randomizationUnit", description="The randomization unit for the measured rollout")

class AudienceConfiguration(PermissiveModel):
    release_strategy: str = Field(..., validation_alias="releaseStrategy", serialization_alias="releaseStrategy", description="The release strategy")
    require_approval: bool = Field(..., validation_alias="requireApproval", serialization_alias="requireApproval", description="Whether or not the audience requires approval")
    notify_member_ids: list[str] | None = Field(None, validation_alias="notifyMemberIds", serialization_alias="notifyMemberIds", description="An array of member IDs. These members are notified to review the approval request.")
    notify_team_keys: list[str] | None = Field(None, validation_alias="notifyTeamKeys", serialization_alias="notifyTeamKeys", description="An array of team keys. The members of these teams are notified to review the approval request.")
    release_guardian_configuration: ReleaseGuardianConfiguration | None = Field(None, validation_alias="releaseGuardianConfiguration", serialization_alias="releaseGuardianConfiguration", description="The configuration for the release guardian.")

class Audience(PermissiveModel):
    environment: EnvironmentSummary | None = Field(None, description="Details about the environment. When the environment has been deleted, this field is omitted.")
    name: str = Field(..., description="The release phase name")
    configuration: AudienceConfiguration | None = Field(None, description="The configuration for the audience's rollout.")
    segment_keys: list[str] | None = Field(None, validation_alias="segmentKeys", serialization_alias="segmentKeys", description="A list of segment keys")

class AudiencePost(PermissiveModel):
    environment_key: str = Field(..., validation_alias="environmentKey", serialization_alias="environmentKey", description="A project-unique key for the environment.")
    name: str = Field(..., description="The audience name")
    segment_keys: list[str] | None = Field(None, validation_alias="segmentKeys", serialization_alias="segmentKeys", description="Segments targeted by this audience.")
    configuration: AudienceConfiguration | None = Field(None, description="The configuration for the audience's rollout.")

class Audiences(RootModel[list[Audience]]):
    pass

class CreatePhaseInput(PermissiveModel):
    audiences: list[AudiencePost] = Field(..., description="An ordered list of the audiences for this release phase. Each audience corresponds to a LaunchDarkly environment.")
    name: str = Field(..., description="The release phase name")
    configuration: PhaseConfiguration | None = Field(None, description="The configuration for the phase's rollout.")

class Phase(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The phase ID")
    audiences: Audiences = Field(..., description="An ordered list of the audiences for this release phase. Each audience corresponds to a LaunchDarkly environment.")
    name: str = Field(..., description="The release phase name")
    configuration: PhaseConfiguration | None = Field(None, description="The configuration for the phase's rollout.")

class ReleaseAudience(PermissiveModel):
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The audience ID")
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    environment: EnvironmentSummary | None = Field(None, description="Details about the environment. If the environment is deleted, this field will be omitted.")
    name: str = Field(..., description="The release phase name")
    configuration: AudienceConfiguration | None = Field(None, description="The audience configuration")
    segment_keys: list[str] | None = Field(None, validation_alias="segmentKeys", serialization_alias="segmentKeys", description="A list of segment keys")
    status: str | None = Field(None, description="The audience status")
    rule_ids: list[str] | None = Field(None, validation_alias="_ruleIds", serialization_alias="_ruleIds", description="The rules IDs added or updated by this audience")

class ReleaseGuardianConfigurationInput(PermissiveModel):
    monitoring_window_milliseconds: int | None = Field(None, validation_alias="monitoringWindowMilliseconds", serialization_alias="monitoringWindowMilliseconds", description="The monitoring window in milliseconds", json_schema_extra={'format': 'int64'})
    rollout_weight: int | None = Field(None, validation_alias="rolloutWeight", serialization_alias="rolloutWeight", description="The rollout weight")
    rollback_on_regression: bool | None = Field(None, validation_alias="rollbackOnRegression", serialization_alias="rollbackOnRegression", description="Whether or not to rollback on regression")
    randomization_unit: str | None = Field(None, validation_alias="randomizationUnit", serialization_alias="randomizationUnit", description="The randomization unit for the measured rollout")

class ReleasePolicyScope(PermissiveModel):
    environment_keys: list[str] | None = Field(None, validation_alias="environmentKeys", serialization_alias="environmentKeys", description="List of environment keys this policy applies to")
    flag_tag_keys: list[str] | None = Field(None, validation_alias="flagTagKeys", serialization_alias="flagTagKeys", description="List of flag tag keys this policy applies to")

class ReleasePolicyStage(PermissiveModel):
    allocation: int
    duration_millis: int = Field(..., validation_alias="durationMillis", serialization_alias="durationMillis", json_schema_extra={'format': 'int64'})

class GuardedReleaseConfig(PermissiveModel):
    """Configuration for guarded releases"""
    rollout_context_kind_key: str | None = Field(None, validation_alias="rolloutContextKindKey", serialization_alias="rolloutContextKindKey", description="Context kind key to use as the randomization unit for the rollout")
    min_sample_size: int | None = Field(None, validation_alias="minSampleSize", serialization_alias="minSampleSize", description="The minimum number of samples required to make a decision")
    rollback_on_regression: bool | None = Field(None, validation_alias="rollbackOnRegression", serialization_alias="rollbackOnRegression", description="Whether to roll back on regression")
    metric_keys: list[str] | None = Field(None, validation_alias="metricKeys", serialization_alias="metricKeys", description="List of metric keys")
    metric_group_keys: list[str] | None = Field(None, validation_alias="metricGroupKeys", serialization_alias="metricGroupKeys", description="List of metric group keys")
    stages: list[ReleasePolicyStage] | None = Field(None, description="List of stages")

class ProgressiveReleaseConfig(PermissiveModel):
    """Configuration for progressive releases"""
    rollout_context_kind_key: str | None = Field(None, validation_alias="rolloutContextKindKey", serialization_alias="rolloutContextKindKey", description="Context kind key to use as the randomization unit for the rollout")
    stages: list[ReleasePolicyStage] | None = Field(None, description="List of stages")

class ReleaserAudienceConfigInput(PermissiveModel):
    audience_id: str | None = Field(None, validation_alias="audienceId", serialization_alias="audienceId", description="UUID of the audience.")
    release_guardian_configuration: ReleaseGuardianConfigurationInput | None = Field(None, validation_alias="releaseGuardianConfiguration", serialization_alias="releaseGuardianConfiguration", description="Optional configuration details for the specified audience. Will default to the release pipeline's audience configuration if omitted.")
    notify_member_ids: list[str] | None = Field(None, validation_alias="notifyMemberIds", serialization_alias="notifyMemberIds", description="An array of member IDs. These members are notified to review the approval request.")
    notify_team_keys: list[str] | None = Field(None, validation_alias="notifyTeamKeys", serialization_alias="notifyTeamKeys", description="An array of team keys. The members of these teams are notified to review the approval request.")

class ResourceSummary(PermissiveModel):
    flag_count: int = Field(..., validation_alias="flagCount", serialization_alias="flagCount")
    segment_count: int | None = Field(None, validation_alias="segmentCount", serialization_alias="segmentCount")
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class RoleAttributeValues(RootModel[list[str]]):
    pass

class RoleAttributeMap(RootModel[dict[str, RoleAttributeValues]]):
    pass

class Member(PermissiveModel):
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The member's ID")
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName", description="The member's first name")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName", description="The member's last name")
    role: str = Field(..., description="The member's base role. If the member has no additional roles, this role will be in effect.")
    email: str = Field(..., description="The member's email address")
    pending_invite: bool = Field(..., validation_alias="_pendingInvite", serialization_alias="_pendingInvite", description="Whether the member has a pending invitation")
    verified: bool = Field(..., validation_alias="_verified", serialization_alias="_verified", description="Whether the member's email address has been verified")
    pending_email: str | None = Field(None, validation_alias="_pendingEmail", serialization_alias="_pendingEmail", description="The member's email address before it has been verified, for accounts where email verification is required")
    custom_roles: list[str] = Field(..., validation_alias="customRoles", serialization_alias="customRoles", description="The set of additional roles, besides the base role, assigned to the member")
    mfa: str = Field(..., description="Whether multi-factor authentication is enabled for this member")
    excluded_dashboards: list[str] | None = Field(None, validation_alias="excludedDashboards", serialization_alias="excludedDashboards", description="Default dashboards that the member has chosen to ignore")
    last_seen: int = Field(..., validation_alias="_lastSeen", serialization_alias="_lastSeen", description="The member's last session date (as Unix milliseconds since epoch)")
    last_seen_metadata: LastSeenMetadata | None = Field(None, validation_alias="_lastSeenMetadata", serialization_alias="_lastSeenMetadata", description="Additional metadata associated with the member's last session, for example, whether a token was used")
    integration_metadata: IntegrationMetadata | None = Field(None, validation_alias="_integrationMetadata", serialization_alias="_integrationMetadata", description="Details on the member account in an external source, if this member is provisioned externally")
    teams: list[MemberTeamSummaryRep] | None = Field(None, description="Details on the teams this member is assigned to")
    permission_grants: list[MemberPermissionGrantSummaryRep] | None = Field(None, validation_alias="permissionGrants", serialization_alias="permissionGrants", description="A list of permission grants. Permission grants allow a member to have access to a specific action, without having to create or update a custom role.")
    creation_date: int = Field(..., validation_alias="creationDate", serialization_alias="creationDate", description="Timestamp of when the member was created")
    oauth_providers: list[str] | None = Field(None, validation_alias="oauthProviders", serialization_alias="oauthProviders", description="A list of OAuth providers")
    version: int | None = Field(None, description="Version of the current configuration")
    role_attributes: RoleAttributeMap | None = Field(None, validation_alias="roleAttributes", serialization_alias="roleAttributes", description="The role attributes for the member")

class Members(PermissiveModel):
    items: list[Member] = Field(..., description="An array of members")
    links: dict[str, Link] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    total_count: int | None = Field(None, validation_alias="totalCount", serialization_alias="totalCount", description="The number of members returned")

class NewMemberForm(PermissiveModel):
    email: str = Field(..., description="The member's email")
    password: str | None = Field(None, description="The member's password")
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName", description="The member's first name")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName", description="The member's last name")
    role: Literal["reader", "writer", "admin", "no_access"] | None = Field(None, description="The member's initial role, if you are using a base role for the initial role")
    custom_roles: list[str] | None = Field(None, validation_alias="customRoles", serialization_alias="customRoles", description="An array of the member's initial roles, if you are using custom roles or preset roles provided by LaunchDarkly")
    team_keys: list[str] | None = Field(None, validation_alias="teamKeys", serialization_alias="teamKeys", description="An array of the member's teams")
    role_attributes: RoleAttributeMap | None = Field(None, validation_alias="roleAttributes", serialization_alias="roleAttributes", description="An object of role attributes for the member")

class SourceEnv(PermissiveModel):
    key: str | None = Field(None, description="The key of the source environment to clone from")
    version: int | None = Field(None, description="(Optional) The version number of the source environment to clone from. Used for optimistic locking")

class EnvironmentPost(PermissiveModel):
    name: str = Field(..., description="A human-friendly name for the new environment")
    key: str = Field(..., description="A project-unique key for the new environment")
    color: str = Field(..., description="A color to indicate this environment in the UI")
    default_ttl: int | None = Field(None, validation_alias="defaultTtl", serialization_alias="defaultTtl", description="The default time (in minutes) that the PHP SDK can cache feature flag rules locally")
    secure_mode: bool | None = Field(None, validation_alias="secureMode", serialization_alias="secureMode", description="Ensures that one end user of the client-side SDK cannot inspect the variations for another end user")
    default_track_events: bool | None = Field(None, validation_alias="defaultTrackEvents", serialization_alias="defaultTrackEvents", description="Enables tracking detailed information for new flags by default")
    confirm_changes: bool | None = Field(None, validation_alias="confirmChanges", serialization_alias="confirmChanges", description="Requires confirmation for all flag and segment changes via the UI in this environment")
    require_comments: bool | None = Field(None, validation_alias="requireComments", serialization_alias="requireComments", description="Requires comments for all flag and segment changes via the UI in this environment")
    tags: list[str] | None = Field(None, description="Tags to apply to the new environment")
    source: SourceEnv | None = Field(None, description="Indicates that the new environment created will be cloned from the provided source environment")
    critical: bool | None = Field(None, description="Whether the environment is critical")

class Statement(PermissiveModel):
    resources: list[str] | None = Field(None, description="Resource specifier strings")
    not_resources: list[str] | None = Field(None, validation_alias="notResources", serialization_alias="notResources", description="Targeted resources are the resources NOT in this list. The <code>resources</code> and <code>notActions</code> fields must be empty to use this field.")
    actions: list[str] | None = Field(None, description="Actions to perform on a resource")
    not_actions: list[str] | None = Field(None, validation_alias="notActions", serialization_alias="notActions", description="Targeted actions are the actions NOT in this list. The <code>actions</code> and <code>notResources</code> fields must be empty to use this field.")
    effect: Literal["allow", "deny"] = Field(..., description="Whether this statement should allow or deny actions on the resources.")

class Integration(PermissiveModel):
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    id_: str | None = Field(None, validation_alias="_id", serialization_alias="_id", description="The ID for this integration audit log subscription")
    kind: str | None = Field(None, description="The type of integration")
    name: str | None = Field(None, description="A human-friendly name for the integration")
    config: dict[str, Any] | None = Field(None, description="Details on configuration for an integration of this type. Refer to the <code>formVariables</code> field in the corresponding <code>manifest.json</code> for a full list of fields for each integration.")
    statements: list[Statement] | None = Field(None, description="Represents a Custom role policy, defining a resource kinds filter the integration audit log subscription responds to.")
    on: bool | None = Field(None, description="Whether the integration is currently active")
    tags: list[str] | None = Field(None, description="An array of tags for this integration")
    access: Access | None = Field(None, validation_alias="_access", serialization_alias="_access", description="Details on the allowed and denied actions for this subscription")
    status: IntegrationSubscriptionStatusRep | None = Field(None, validation_alias="_status", serialization_alias="_status", description="Details on the most recent successes and errors for this integration")
    url: str | None = Field(None, description="Slack webhook receiver URL. Only used for legacy Slack webhook integrations.")
    api_key: str | None = Field(None, validation_alias="apiKey", serialization_alias="apiKey", description="Datadog API key. Only used for legacy Datadog webhook integrations.")

class StatementPost(PermissiveModel):
    resources: list[str] | None = Field(None, description="Resource specifier strings")
    not_resources: list[str] | None = Field(None, validation_alias="notResources", serialization_alias="notResources", description="Targeted resources are the resources NOT in this list. The <code>resources</code> field must be empty to use this field.")
    actions: list[str] | None = Field(None, description="Actions to perform on a resource")
    not_actions: list[str] | None = Field(None, validation_alias="notActions", serialization_alias="notActions", description="Targeted actions are the actions NOT in this list. The <code>actions</code> field must be empty to use this field.")
    effect: Literal["allow", "deny"] = Field(..., description="Whether this statement should allow or deny actions on the resources.")

class TokenSummary(PermissiveModel):
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links")
    id_: str | None = Field(None, validation_alias="_id", serialization_alias="_id")
    name: str | None = Field(None, description="The name of the token")
    ending: str | None = Field(None, description="The last few characters of the token")
    service_token: bool | None = Field(None, validation_alias="serviceToken", serialization_alias="serviceToken", description="Whether this is a service token")

class CompletedBy(PermissiveModel):
    member: MemberSummary | None = Field(None, description="The LaunchDarkly member who marked this phase as complete")
    token: TokenSummary | None = Field(None, description="The service token used to mark this phase as complete")

class ReleasePhase(PermissiveModel):
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The phase ID")
    name: str = Field(..., validation_alias="_name", serialization_alias="_name", description="The release phase name")
    complete: bool = Field(..., description="Whether this phase is complete")
    creation_date: int = Field(..., validation_alias="_creationDate", serialization_alias="_creationDate", description="Timestamp of when the release phase was created")
    completion_date: int | None = Field(None, validation_alias="_completionDate", serialization_alias="_completionDate", description="Timestamp of when the release phase was completed")
    completed_by: CompletedBy | None = Field(None, validation_alias="_completedBy", serialization_alias="_completedBy", description="Details about how this phase was marked as complete")
    audiences: list[ReleaseAudience] = Field(..., validation_alias="_audiences", serialization_alias="_audiences", description="A logical grouping of one or more environments that share attributes for rolling out changes")
    status: str | None = Field(None, description="Status of the phase")
    started: bool | None = Field(None, description="Whether or not this phase has started")
    started_date: int | None = Field(None, validation_alias="_startedDate", serialization_alias="_startedDate", description="Timestamp of when the release phase was started")
    configuration: PhaseConfiguration | None = Field(None, description="The phase configuration")

class Release(PermissiveModel):
    links: dict[str, Link] | None = Field(None, validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    name: str = Field(..., description="The release pipeline name")
    release_pipeline_key: str = Field(..., validation_alias="releasePipelineKey", serialization_alias="releasePipelineKey", description="The release pipeline key")
    release_pipeline_description: str = Field(..., validation_alias="releasePipelineDescription", serialization_alias="releasePipelineDescription", description="The release pipeline description")
    phases: list[ReleasePhase] = Field(..., description="An ordered list of the release pipeline phases")
    version: int = Field(..., validation_alias="_version", serialization_alias="_version", description="The release version")
    release_variation_id: str | None = Field(None, validation_alias="_releaseVariationId", serialization_alias="_releaseVariationId", description="The chosen release variation ID to use across all phases of a release")
    canceled_at: int | None = Field(None, validation_alias="_canceledAt", serialization_alias="_canceledAt", description="Timestamp of when the release was canceled")

class TreatmentParameterInput(PermissiveModel):
    flag_key: str = Field(..., validation_alias="flagKey", serialization_alias="flagKey", description="The flag key")
    variation_id: str = Field(..., validation_alias="variationId", serialization_alias="variationId", description="The ID of the flag variation")

class TreatmentInput(PermissiveModel):
    name: str = Field(..., description="The treatment name")
    baseline: bool = Field(..., description="Whether this treatment is the baseline to compare other treatments against")
    allocation_percent: str = Field(..., validation_alias="allocationPercent", serialization_alias="allocationPercent", description="The percentage of traffic allocated to this treatment during the iteration")
    parameters: list[TreatmentParameterInput] = Field(..., description="Details on the flag and variation to use for this treatment")

class UrlPost(PermissiveModel):
    kind: Literal["exact", "canonical", "substring", "regex"] | None = None
    url: str | None = None
    substring: str | None = None
    pattern: str | None = None

class Variation(PermissiveModel):
    id_: str | None = Field(None, validation_alias="_id", serialization_alias="_id", description="The ID of the variation. Leave empty when you are creating a flag.")
    value: Any = Field(..., description="The value of the variation. For boolean flags, this must be <code>true</code> or <code>false</code>. For multivariate flags, this may be a string, number, or JSON object.")
    description: str | None = Field(None, description="Description of the variation. Defaults to an empty string, but is omitted from the response if not set.")
    name: str | None = Field(None, description="A human-friendly name for the variation. Defaults to an empty string, but is omitted from the response if not set.")

class ViewLinkRequestFilter(StrictModel):
    filter_: str = Field(..., validation_alias="filter", serialization_alias="filter", description="Filter string to match resources for linking. Uses the same syntax as list endpoints: flags use comma-separated field:value filters, segments use queryfilter syntax.\n\nSupported filters by resource type:\n- flags: query, tags, maintainerId, maintainerTeamKey, type, status, state, staleState, sdkAvailability, targeting, hasExperiment, hasDataExport, evaluated, creationDate, contextKindTargeted, contextKindsEvaluated, filterEnv, segmentTargeted, codeReferences.min, codeReferences.max, excludeSettings, releasePipeline, applicationEvaluated, purpose, guardedRollout, view, key, name, archived, followerId\n- segments (queryfilter): query, tags, keys, excludedKeys, unbounded, external, view, type\nSome filters are only available when the corresponding feature is enabled on your account.\n")
    environment_id: str | None = Field(None, validation_alias="environmentId", serialization_alias="environmentId", description="Required when using filter for segment resources. Specifies which environment to query for segments matching the filter.\nIgnored for flag resources (flags are global across environments).\n")
    comment: str | None = Field('', description="Optional comment for the link/unlink operation")

class ViewLinkRequestKeys(StrictModel):
    keys: list[str] = Field(..., description="Keys of the resources (flags, segments) to link/unlink")
    filter_: str | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter string to determine which resources should be linked. Resources only need to match either the filter or explicitly-listed keys to be linked (union).\nUses the same syntax as list endpoints: flags use comma-separated field:value filters, segments use queryfilter syntax.\n\nSupported filters by resource type:\n- flags: query, tags, maintainerId, maintainerTeamKey, type, status, state, staleState, sdkAvailability, targeting, hasExperiment, hasDataExport, evaluated, creationDate, contextKindTargeted, contextKindsEvaluated, filterEnv, segmentTargeted, codeReferences.min, codeReferences.max, excludeSettings, releasePipeline, applicationEvaluated, purpose, guardedRollout, view, key, name, archived, followerId\n- segments (queryfilter): query, tags, keys, excludedKeys, unbounded, external, view, type\nSome filters are only available when the corresponding feature is enabled on your account.\n")
    comment: str | None = Field('', description="Optional comment for the link/unlink operation")

class ViewLinkRequestSegmentIdentifier(PermissiveModel):
    environment_id: str = Field(..., validation_alias="environmentId", serialization_alias="environmentId")
    segment_key: str = Field(..., validation_alias="segmentKey", serialization_alias="segmentKey")

class ViewLinkRequestSegmentIdentifiers(StrictModel):
    segment_identifiers: list[ViewLinkRequestSegmentIdentifier] = Field(..., validation_alias="segmentIdentifiers", serialization_alias="segmentIdentifiers", description="Identifiers of the segments to link/unlink (environmentId and segmentKey)")
    filter_: str | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter string to determine which resources should be linked. Resources only need to match either the filter or explicitly-listed keys to be linked (union).\nUses the same queryfilter syntax as the segments list endpoint.\n\nSupported filters for segments: query, tags, keys, excludedKeys, unbounded, external, view, type\n")
    environment_id: str | None = Field(None, validation_alias="environmentId", serialization_alias="environmentId", description="Required when using filter for segment resources. Specifies which environment to query for segments matching the filter.\nIgnored when only using explicit segmentIdentifiers (since each identifier contains its own environmentId).\n")
    comment: str | None = Field('', description="Optional comment for the link/unlink operation")

class ViewsAccessAllowedReason(PermissiveModel):
    resources: list[str] | None = Field(None, description="Resource specifier strings")
    not_resources: list[str] | None = Field(None, validation_alias="notResources", serialization_alias="notResources", description="Targeted resources are the resources NOT in this list. The <code>resources</code> and <code>notActions</code> fields must be empty to use this field.")
    actions: list[str] | None = Field(None, description="Actions to perform on a resource")
    not_actions: list[str] | None = Field(None, validation_alias="notActions", serialization_alias="notActions", description="Targeted actions are the actions NOT in this list. The <code>actions</code> and <code>notResources</code> fields must be empty to use this field.")
    effect: Literal["allow", "deny"] = Field(..., description="Whether this statement should allow or deny actions on the resources.")
    role_name: str | None = None

class ViewsAccessAllowedRep(PermissiveModel):
    action: str
    reason: ViewsAccessAllowedReason

class ViewsAccessDeniedReason(PermissiveModel):
    resources: list[str] | None = Field(None, description="Resource specifier strings")
    not_resources: list[str] | None = Field(None, validation_alias="notResources", serialization_alias="notResources", description="Targeted resources are the resources NOT in this list. The <code>resources</code> and <code>notActions</code> fields must be empty to use this field.")
    actions: list[str] | None = Field(None, description="Actions to perform on a resource")
    not_actions: list[str] | None = Field(None, validation_alias="notActions", serialization_alias="notActions", description="Targeted actions are the actions NOT in this list. The <code>actions</code> and <code>notResources</code> fields must be empty to use this field.")
    effect: Literal["allow", "deny"] = Field(..., description="Whether this statement should allow or deny actions on the resources.")
    role_name: str | None = None

class ViewsAccessDenied(PermissiveModel):
    action: str
    reason: ViewsAccessDeniedReason

class ViewsAccess(PermissiveModel):
    denied: list[ViewsAccessDenied]
    allowed: list[ViewsAccessAllowedRep]

class ViewsAccessRep(PermissiveModel):
    denied: list[ViewsAccessDenied]
    allowed: list[ViewsAccessAllowedRep]

class ViewsLink(PermissiveModel):
    href: str | None = None
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class ViewsMaintainerMember(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    email: str
    role: str
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName")

class ViewsMaintainerTeam(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    key: str
    name: str

class Maintainer(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    kind: str
    maintainer_member: ViewsMaintainerMember | None = Field(None, validation_alias="maintainerMember", serialization_alias="maintainerMember")
    maintainer_team: ViewsMaintainerTeam | None = Field(None, validation_alias="maintainerTeam", serialization_alias="maintainerTeam")

class ViewsMemberSummary(PermissiveModel):
    links: dict[str, ViewsLink] = Field(..., validation_alias="_links", serialization_alias="_links", description="The location and content type of related resources")
    id_: str = Field(..., validation_alias="_id", serialization_alias="_id", description="The member's ID")
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName", description="The member's first name")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName", description="The member's last name")
    role: str = Field(..., description="The member's base role. If the member has no additional roles, this role will be in effect.")
    email: str = Field(..., description="The member's email address")

class ViewsMemberTeamSummaryRep(PermissiveModel):
    custom_role_keys: list[str] = Field(..., validation_alias="customRoleKeys", serialization_alias="customRoleKeys", description="A list of keys of the custom roles this team has access to")
    key: str = Field(..., description="The team key")
    links: dict[str, ViewsLink] | None = Field(None, validation_alias="_links", serialization_alias="_links")
    name: str = Field(..., description="The team name")

class ExpandedFlagMaintainer(PermissiveModel):
    key: str = Field(..., description="The ID of the maintainer member, or the key of the maintainer team")
    kind: Literal["member", "team"] = Field(..., description="The type of the maintainer")
    member: ViewsMemberSummary | None = Field(None, validation_alias="_member", serialization_alias="_member")
    team: ViewsMemberTeamSummaryRep | None = Field(None, validation_alias="_team", serialization_alias="_team")

class ExpandedFlag(PermissiveModel):
    """Flag representation for Views API - contains only fields actually used by the Views service"""
    key: str = Field(..., description="A unique key used to reference the flag")
    name: str = Field(..., description="A human-friendly name for the flag")
    description: str | None = Field(None, description="Description of the flag")
    creation_date: int | None = Field(None, validation_alias="creationDate", serialization_alias="creationDate", description="Creation date in milliseconds", json_schema_extra={'format': 'int64'})
    version: int | None = Field(None, validation_alias="_version", serialization_alias="_version", description="Version of the flag")
    archived: bool | None = Field(None, description="Whether the flag is archived")
    tags: list[str] | None = Field(None, description="Tags for the flag")
    temporary: bool | None = Field(None, description="Whether the flag is temporary")
    include_in_snippet: bool | None = Field(None, validation_alias="includeInSnippet", serialization_alias="includeInSnippet", description="Whether to include in snippet")
    maintainer: ExpandedFlagMaintainer | None = None
    links: ParentAndSelfLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ExpandedLinkedFlags(PermissiveModel):
    """Details on linked flags for a view - requires passing the 'allFlags' expand field"""
    items: list[ExpandedFlag]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ExpandedLinkedResourcesFlags(PermissiveModel):
    items: list[ExpandedFlag]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ExpandedLinkedResourcesItems(PermissiveModel):
    flags: ExpandedLinkedResourcesFlags
    segments: ExpandedLinkedResourcesSegments | None = None

class ExpandedLinkedResources(PermissiveModel):
    """Details on linked resources for a view - requires passing the 'allResources' expand field"""
    items: ExpandedLinkedResourcesItems
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ViewsPaginatedLinks(PermissiveModel):
    first: ViewsLink | None = None
    last: ViewsLink | None = None
    next_: ViewsLink | None = Field(None, validation_alias="next", serialization_alias="next")
    prev: ViewsLink | None = None
    self: ViewsLink

class ViewsSelfLink(PermissiveModel):
    self: CoreLink

class ExpandedDirectlyLinkedFlag(PermissiveModel):
    key: str
    name: str
    links: ViewsSelfLink

class ExpandedDirectlyLinkedFlags(PermissiveModel):
    items: list[ExpandedDirectlyLinkedFlag]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class ExpandedDirectlyLinkedSegment(PermissiveModel):
    key: str
    name: str
    environment_id: str = Field(..., validation_alias="environmentId", serialization_alias="environmentId")
    links: ViewsSelfLink

class ExpandedDirectlyLinkedSegments(PermissiveModel):
    items: list[ExpandedDirectlyLinkedSegment]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")

class FlagsSummary(PermissiveModel):
    count: int
    linked_flags: ExpandedDirectlyLinkedFlags | None = Field(None, validation_alias="linkedFlags", serialization_alias="linkedFlags")

class SegmentsSummary(PermissiveModel):
    count: int
    linked_segments: ExpandedDirectlyLinkedSegments | None = Field(None, validation_alias="linkedSegments", serialization_alias="linkedSegments")

class View(PermissiveModel):
    access: ViewsAccessRep | None = Field(None, validation_alias="_access", serialization_alias="_access")
    links: ParentAndSelfLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of this view", json_schema_extra={'format': 'string'})
    account_id: str = Field(..., validation_alias="accountId", serialization_alias="accountId", description="ID of the account that owns this view")
    project_id: str = Field(..., validation_alias="projectId", serialization_alias="projectId", description="ID of the project this view belongs to")
    project_key: str = Field(..., validation_alias="projectKey", serialization_alias="projectKey", description="Key of the project this view belongs to")
    key: str = Field(..., description="Unique key for the view within the account/project")
    name: str = Field(..., description="Human-readable name for the view")
    description: str = Field(..., description="Optional detailed description of the view")
    generate_sdk_keys: bool = Field(..., validation_alias="generateSdkKeys", serialization_alias="generateSdkKeys", description="Whether to generate SDK keys for this view. Defaults to false.")
    version: int = Field(..., description="Version number for tracking changes")
    tags: list[str] = Field(..., description="Tags associated with this view")
    created_at: int = Field(..., validation_alias="createdAt", serialization_alias="createdAt", json_schema_extra={'format': 'int64'})
    updated_at: int = Field(..., validation_alias="updatedAt", serialization_alias="updatedAt", json_schema_extra={'format': 'int64'})
    archived: bool = Field(..., description="Whether this view is archived")
    archived_at: int | None = Field(None, validation_alias="archivedAt", serialization_alias="archivedAt", json_schema_extra={'format': 'int64'})
    deleted_at: int | None = Field(None, validation_alias="deletedAt", serialization_alias="deletedAt", json_schema_extra={'format': 'int64'})
    deleted: bool = Field(..., description="Whether this view is deleted")
    maintainer: Maintainer | None = None
    flags_summary: FlagsSummary | None = Field(None, validation_alias="flagsSummary", serialization_alias="flagsSummary")
    segments_summary: SegmentsSummary | None = Field(None, validation_alias="segmentsSummary", serialization_alias="segmentsSummary")
    metrics_summary: MetricsSummary | None = Field(None, validation_alias="metricsSummary", serialization_alias="metricsSummary")
    ai_configs_summary: AiConfigsSummary | None = Field(None, validation_alias="aiConfigsSummary", serialization_alias="aiConfigsSummary")
    resource_summary: ResourceSummary | None = Field(None, validation_alias="resourceSummary", serialization_alias="resourceSummary")
    flags_expanded: ExpandedLinkedFlags | None = Field(None, validation_alias="flagsExpanded", serialization_alias="flagsExpanded")
    segments_expanded: ExpandedLinkedSegments | None = Field(None, validation_alias="segmentsExpanded", serialization_alias="segmentsExpanded")
    metrics_expanded: ExpandedLinkedMetrics | None = Field(None, validation_alias="metricsExpanded", serialization_alias="metricsExpanded")
    ai_configs_expanded: ExpandedLinkedAiConfigs | None = Field(None, validation_alias="aiConfigsExpanded", serialization_alias="aiConfigsExpanded")
    resources_expanded: ExpandedLinkedResources | None = Field(None, validation_alias="resourcesExpanded", serialization_alias="resourcesExpanded")

class Views(PermissiveModel):
    links: ViewsPaginatedLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")
    items: list[View]
    total_count: int = Field(..., validation_alias="totalCount", serialization_alias="totalCount")


# Rebuild models to resolve forward references (required for circular refs)
Access.model_rebuild()
AccessAllowedReason.model_rebuild()
AccessAllowedRep.model_rebuild()
AccessDenied.model_rebuild()
AccessDeniedReason.model_rebuild()
AgentGraphEdge.model_rebuild()
AgentGraphEdgePost.model_rebuild()
AgentOptimizationAcceptanceStatement.model_rebuild()
AgentOptimizationJudge.model_rebuild()
AiConfigsSummary.model_rebuild()
AnnouncementPatchOperation.model_rebuild()
ApprovalSettings.model_rebuild()
Audience.model_rebuild()
AudienceConfiguration.model_rebuild()
AudiencePost.model_rebuild()
Audiences.model_rebuild()
Client.model_rebuild()
ClientSideAvailability.model_rebuild()
CompletedBy.model_rebuild()
ContextRecord.model_rebuild()
Contexts.model_rebuild()
CoreLink.model_rebuild()
CreatePhaseInput.model_rebuild()
CustomProperty.model_rebuild()
Defaults.model_rebuild()
Environment.model_rebuild()
EnvironmentPost.model_rebuild()
Environments.model_rebuild()
EnvironmentSummary.model_rebuild()
ExpandedAiConfig.model_rebuild()
ExpandedDirectlyLinkedFlag.model_rebuild()
ExpandedDirectlyLinkedFlags.model_rebuild()
ExpandedDirectlyLinkedSegment.model_rebuild()
ExpandedDirectlyLinkedSegments.model_rebuild()
ExpandedFlag.model_rebuild()
ExpandedFlagMaintainer.model_rebuild()
ExpandedLinkedAiConfigs.model_rebuild()
ExpandedLinkedFlags.model_rebuild()
ExpandedLinkedMetrics.model_rebuild()
ExpandedLinkedResources.model_rebuild()
ExpandedLinkedResourcesFlags.model_rebuild()
ExpandedLinkedResourcesItems.model_rebuild()
ExpandedLinkedResourcesSegments.model_rebuild()
ExpandedLinkedSegments.model_rebuild()
ExpandedMetric.model_rebuild()
ExpandedSegment.model_rebuild()
Export.model_rebuild()
Extinction.model_rebuild()
FlagInput.model_rebuild()
FlagPrerequisitePost.model_rebuild()
FlagsSummary.model_rebuild()
GuardedReleaseConfig.model_rebuild()
HunkRep.model_rebuild()
InitiatorRep.model_rebuild()
InsightsRepositoryProject.model_rebuild()
Instruction.model_rebuild()
Instructions.model_rebuild()
Integration.model_rebuild()
IntegrationMetadata.model_rebuild()
IntegrationStatus.model_rebuild()
IntegrationStatusRep.model_rebuild()
IntegrationSubscriptionStatusRep.model_rebuild()
JudgeAttachment.model_rebuild()
LastSeenMetadata.model_rebuild()
Link.model_rebuild()
Maintainer.model_rebuild()
Member.model_rebuild()
MemberPermissionGrantSummaryRep.model_rebuild()
Members.model_rebuild()
MemberSummary.model_rebuild()
MemberTeamSummaryRep.model_rebuild()
Message.model_rebuild()
MetricInMetricGroupInput.model_rebuild()
MetricInput.model_rebuild()
Metrics.model_rebuild()
MetricsSummary.model_rebuild()
NewMemberForm.model_rebuild()
ParentAndSelfLinks.model_rebuild()
PatchOperation.model_rebuild()
PatchSegmentExpiringTargetInstruction.model_rebuild()
PatchSegmentInstruction.model_rebuild()
PermissionGrantInput.model_rebuild()
Phase.model_rebuild()
PhaseConfiguration.model_rebuild()
ProgressiveReleaseConfig.model_rebuild()
Project.model_rebuild()
Projects.model_rebuild()
RandomizationUnitInput.model_rebuild()
ReferenceRep.model_rebuild()
Release.model_rebuild()
ReleaseAudience.model_rebuild()
ReleaseGuardianConfiguration.model_rebuild()
ReleaseGuardianConfigurationInput.model_rebuild()
ReleasePhase.model_rebuild()
ReleasePolicyScope.model_rebuild()
ReleasePolicyStage.model_rebuild()
ReleaserAudienceConfigInput.model_rebuild()
ResourceSummary.model_rebuild()
RoleAttributeMap.model_rebuild()
RoleAttributeValues.model_rebuild()
SegmentsSummary.model_rebuild()
SourceEnv.model_rebuild()
Statement.model_rebuild()
StatementPost.model_rebuild()
TokenSummary.model_rebuild()
TreatmentInput.model_rebuild()
TreatmentParameterInput.model_rebuild()
UrlPost.model_rebuild()
Variation.model_rebuild()
View.model_rebuild()
ViewLinkRequestFilter.model_rebuild()
ViewLinkRequestKeys.model_rebuild()
ViewLinkRequestSegmentIdentifier.model_rebuild()
ViewLinkRequestSegmentIdentifiers.model_rebuild()
Views.model_rebuild()
ViewsAccess.model_rebuild()
ViewsAccessAllowedReason.model_rebuild()
ViewsAccessAllowedRep.model_rebuild()
ViewsAccessDenied.model_rebuild()
ViewsAccessDeniedReason.model_rebuild()
ViewsAccessRep.model_rebuild()
ViewsLink.model_rebuild()
ViewsMaintainerMember.model_rebuild()
ViewsMaintainerTeam.model_rebuild()
ViewsMemberSummary.model_rebuild()
ViewsMemberTeamSummaryRep.model_rebuild()
ViewsPaginatedLinks.model_rebuild()
ViewsSelfLink.model_rebuild()

"""
E2b MCP Server - Pydantic Models

Generated: 2026-04-14 18:20:03 UTC
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
    "DeleteAccessTokensRequest",
    "DeleteApiKeysRequest",
    "DeleteSandboxesRequest",
    "DeleteTemplatesRequest",
    "DeleteTemplatesTagsRequest",
    "DeleteVolumesRequest",
    "GetNodesByNodeIdRequest",
    "GetSandboxesBySandboxIdMetricsRequest",
    "GetSandboxesBySandboxIdRequest",
    "GetSandboxesMetricsRequest",
    "GetSnapshotsRequest",
    "GetTeamsMetricsMaxRequest",
    "GetTeamsMetricsRequest",
    "GetTemplatesAliasesRequest",
    "GetTemplatesBuildsLogsRequest",
    "GetTemplatesBuildsStatusRequest",
    "GetTemplatesByTemplateIdRequest",
    "GetTemplatesFilesRequest",
    "GetTemplatesRequest",
    "GetTemplatesTagsRequest",
    "GetV2SandboxesLogsRequest",
    "GetV2SandboxesRequest",
    "GetVolumesByVolumeIdRequest",
    "PatchApiKeysRequest",
    "PatchV2TemplatesRequest",
    "PostAccessTokensRequest",
    "PostAdminTeamsSandboxesKillRequest",
    "PostApiKeysRequest",
    "PostNodesRequest",
    "PostSandboxesConnectRequest",
    "PostSandboxesPauseRequest",
    "PostSandboxesRefreshesRequest",
    "PostSandboxesRequest",
    "PostSandboxesSnapshotsRequest",
    "PostSandboxesTimeoutRequest",
    "PostTemplatesTagsRequest",
    "PostV2TemplatesBuildsRequest",
    "PostV3TemplatesRequest",
    "PostVolumesRequest",
    "AwsRegistry",
    "GcpRegistry",
    "GeneralRegistry",
    "SandboxVolumeMount",
    "TemplateStep",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_team_metrics
class GetTeamsMetricsRequestPath(StrictModel):
    team_id: str = Field(default=..., validation_alias="teamID", serialization_alias="teamID", description="The unique identifier of the team for which to retrieve metrics.")
class GetTeamsMetricsRequestQuery(StrictModel):
    start: int | None = Field(default=None, description="Unix timestamp in seconds marking the start of the metrics interval. If omitted, defaults to the beginning of the current period.", json_schema_extra={'format': 'int64'})
    end: int | None = Field(default=None, description="Unix timestamp in seconds marking the end of the metrics interval. If omitted, defaults to the current time.", json_schema_extra={'format': 'int64'})
class GetTeamsMetricsRequest(StrictModel):
    """Retrieve performance and activity metrics for a specific team over an optional time interval. If no time range is specified, returns metrics for the current period."""
    path: GetTeamsMetricsRequestPath
    query: GetTeamsMetricsRequestQuery | None = None

# Operation: get_team_metrics_maximum
class GetTeamsMetricsMaxRequestPath(StrictModel):
    team_id: str = Field(default=..., validation_alias="teamID", serialization_alias="teamID", description="The unique identifier of the team for which to retrieve metrics.")
class GetTeamsMetricsMaxRequestQuery(StrictModel):
    start: int | None = Field(default=None, description="Unix timestamp in seconds marking the start of the interval. If omitted, metrics from the earliest available data are included.", json_schema_extra={'format': 'int64'})
    end: int | None = Field(default=None, description="Unix timestamp in seconds marking the end of the interval. If omitted, metrics up to the current time are included.", json_schema_extra={'format': 'int64'})
    metric: Literal["concurrent_sandboxes", "sandbox_start_rate"] = Field(default=..., description="The specific metric to retrieve the maximum value for during the interval.")
class GetTeamsMetricsMaxRequest(StrictModel):
    """Retrieve the maximum value for a specified metric within a given time interval for a team. Useful for understanding peak performance or resource utilization."""
    path: GetTeamsMetricsMaxRequestPath
    query: GetTeamsMetricsMaxRequestQuery

# Operation: create_sandbox
class PostSandboxesRequestBodyAutoResume(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Enable automatic resumption of the sandbox when it enters a paused state.")
class PostSandboxesRequestBodyNetwork(StrictModel):
    allow_public_traffic: bool | None = Field(default=None, validation_alias="allowPublicTraffic", serialization_alias="allowPublicTraffic", description="Control whether sandbox URLs are publicly accessible or require authentication to access.")
    allow_out: list[str] | None = Field(default=None, validation_alias="allowOut", serialization_alias="allowOut", description="List of CIDR blocks or IP addresses permitted for outbound traffic. Allowed addresses take precedence over denied addresses when both are specified.")
    deny_out: list[str] | None = Field(default=None, validation_alias="denyOut", serialization_alias="denyOut", description="List of CIDR blocks or IP addresses blocked from outbound traffic.")
class PostSandboxesRequestBody(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template to use for creating the sandbox.")
    metadata: Any | None = Field(default=None, description="Custom metadata to attach to the sandbox for tracking and organization purposes.")
    env_vars: Any | None = Field(default=None, validation_alias="envVars", serialization_alias="envVars", description="Environment variables to inject into the sandbox runtime environment.")
    mcp: dict[str, Any] | None = Field(default=None, description="Model Context Protocol (MCP) configuration settings for the sandbox.")
    volume_mounts: list[SandboxVolumeMount] | None = Field(default=None, validation_alias="volumeMounts", serialization_alias="volumeMounts", description="Volume mounts to attach to the sandbox, enabling access to external storage or data sources.")
    auto_resume: PostSandboxesRequestBodyAutoResume = Field(default=..., validation_alias="autoResume", serialization_alias="autoResume")
    network: PostSandboxesRequestBodyNetwork | None = None
class PostSandboxesRequest(StrictModel):
    """Create a new sandbox instance from a specified template. The sandbox can be configured with network policies, environment variables, and storage mounts."""
    body: PostSandboxesRequestBody

# Operation: list_sandboxes
class GetV2SandboxesRequestQuery(StrictModel):
    metadata: str | None = Field(default=None, description="Filter sandboxes by metadata key-value pairs. Use URL encoding for both keys and values (e.g., user=abc&app=prod).")
    state: list[Literal["running", "paused"]] | None = Field(default=None, description="Filter sandboxes by one or more states. Provide as an array of state values.")
    limit: int | None = Field(default=None, description="Maximum number of sandboxes to return per page. Must be between 1 and 100.", json_schema_extra={'format': 'int32'})
class GetV2SandboxesRequest(StrictModel):
    """Retrieve a list of all sandboxes with optional filtering by metadata and state. Results are paginated with a configurable limit."""
    query: GetV2SandboxesRequestQuery | None = None

# Operation: list_sandbox_metrics
class GetSandboxesMetricsRequestQuery(StrictModel):
    sandbox_ids: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(default=..., description="One or more sandbox IDs to retrieve metrics for. Provide as a comma-separated list of sandbox identifiers.", max_length=100)
class GetSandboxesMetricsRequest(StrictModel):
    """Retrieve performance and usage metrics for specified sandboxes. Supports querying multiple sandboxes in a single request."""
    query: GetSandboxesMetricsRequestQuery

# Operation: list_sandbox_logs
class GetV2SandboxesLogsRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox for which to retrieve logs.")
class GetV2SandboxesLogsRequestQuery(StrictModel):
    cursor: int | None = Field(default=None, description="Starting timestamp in milliseconds from which logs should be returned. Use this to paginate through results or retrieve logs after a specific point in time.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="Maximum number of log entries to return in a single response.", json_schema_extra={'format': 'int32'})
    direction: Literal["forward", "backward"] | None = Field(default=None, description="Order in which logs should be returned relative to the cursor timestamp.")
class GetV2SandboxesLogsRequest(StrictModel):
    """Retrieve logs from a specific sandbox with optional filtering by time range and result limit. Logs can be returned in forward or backward chronological order."""
    path: GetV2SandboxesLogsRequestPath
    query: GetV2SandboxesLogsRequestQuery | None = None

# Operation: get_sandbox
class GetSandboxesBySandboxIdRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox to retrieve.")
class GetSandboxesBySandboxIdRequest(StrictModel):
    """Retrieve a specific sandbox by its unique identifier. Use this operation to fetch detailed information about a sandbox environment."""
    path: GetSandboxesBySandboxIdRequestPath

# Operation: terminate_sandbox
class DeleteSandboxesRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox to terminate.")
class DeleteSandboxesRequest(StrictModel):
    """Terminate and remove a sandbox environment by its ID. This operation permanently deletes the sandbox and all associated resources."""
    path: DeleteSandboxesRequestPath

# Operation: get_sandbox_metrics
class GetSandboxesBySandboxIdMetricsRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox for which to retrieve metrics.")
class GetSandboxesBySandboxIdMetricsRequestQuery(StrictModel):
    start: int | None = Field(default=None, description="Unix timestamp in seconds marking the beginning of the metrics collection interval. If omitted, metrics are retrieved from the earliest available data.", json_schema_extra={'format': 'int64'})
    end: int | None = Field(default=None, description="Unix timestamp in seconds marking the end of the metrics collection interval. If omitted, metrics are retrieved up to the current time.", json_schema_extra={'format': 'int64'})
class GetSandboxesBySandboxIdMetricsRequest(StrictModel):
    """Retrieve performance and resource metrics for a specific sandbox over an optional time interval. Metrics are aggregated between the specified start and end timestamps."""
    path: GetSandboxesBySandboxIdMetricsRequestPath
    query: GetSandboxesBySandboxIdMetricsRequestQuery | None = None

# Operation: pause_sandbox
class PostSandboxesPauseRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox to pause.")
class PostSandboxesPauseRequest(StrictModel):
    """Pause an active sandbox to temporarily suspend its execution and resource consumption. The sandbox can be resumed later without losing its state."""
    path: PostSandboxesPauseRequestPath

# Operation: connect_sandbox
class PostSandboxesConnectRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox to connect to.")
class PostSandboxesConnectRequestBody(StrictModel):
    timeout: int = Field(default=..., description="The number of seconds from the current time until the sandbox should automatically expire. Must be a non-negative value.", json_schema_extra={'format': 'int32'})
class PostSandboxesConnectRequest(StrictModel):
    """Establish a connection to a sandbox and extend its time-to-live. If the sandbox is paused, it will be automatically resumed."""
    path: PostSandboxesConnectRequestPath
    body: PostSandboxesConnectRequestBody

# Operation: set_sandbox_timeout
class PostSandboxesTimeoutRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox to configure.")
class PostSandboxesTimeoutRequestBody(StrictModel):
    timeout: int = Field(default=..., description="The number of seconds from the current time until the sandbox should automatically expire. Must be a non-negative integer.", json_schema_extra={'format': 'int32'})
class PostSandboxesTimeoutRequest(StrictModel):
    """Set the expiration time for a sandbox by specifying a timeout duration in seconds from the current request time. Calling this operation multiple times resets the sandbox's time-to-live (TTL), with each call using the current timestamp as the new starting point."""
    path: PostSandboxesTimeoutRequestPath
    body: PostSandboxesTimeoutRequestBody

# Operation: refresh_sandbox
class PostSandboxesRefreshesRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox to refresh.")
class PostSandboxesRefreshesRequestBody(StrictModel):
    duration: int | None = Field(default=None, description="The duration in seconds to extend the sandbox's time to live. If not specified, a default duration will be applied.", ge=0, le=3600)
class PostSandboxesRefreshesRequest(StrictModel):
    """Extend the time to live of an active sandbox by refreshing it. Optionally specify a custom duration to keep the sandbox alive."""
    path: PostSandboxesRefreshesRequestPath
    body: PostSandboxesRefreshesRequestBody | None = None

# Operation: create_sandbox_snapshot
class PostSandboxesSnapshotsRequestPath(StrictModel):
    sandbox_id: str = Field(default=..., validation_alias="sandboxID", serialization_alias="sandboxID", description="The unique identifier of the sandbox from which to create the snapshot.")
class PostSandboxesSnapshotsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Optional name for the snapshot. If a snapshot with this name already exists, a new build will be assigned to the existing snapshot instead of creating a new one.")
class PostSandboxesSnapshotsRequest(StrictModel):
    """Create a persistent snapshot of the sandbox's current state that can be used to create new sandboxes and persists beyond the original sandbox's lifetime."""
    path: PostSandboxesSnapshotsRequestPath
    body: PostSandboxesSnapshotsRequestBody | None = None

# Operation: list_snapshots
class GetSnapshotsRequestQuery(StrictModel):
    sandbox_id: str | None = Field(default=None, validation_alias="sandboxID", serialization_alias="sandboxID", description="Filter results to snapshots created from a specific sandbox ID.")
    limit: int | None = Field(default=None, description="Number of snapshots to return per page. Useful for paginating through large result sets.", json_schema_extra={'format': 'int32'})
class GetSnapshotsRequest(StrictModel):
    """Retrieve all snapshots for your team, with optional filtering by source sandbox and pagination support."""
    query: GetSnapshotsRequestQuery | None = None

# Operation: create_template
class PostV3TemplatesRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Name of the template. Optionally include a version tag using colon separator (e.g., 'my-template:v1'). If a tag is provided in the name, it will be added to the tags array automatically.")
    tags: list[str] | None = Field(default=None, description="Tags to assign to the template for organization and categorization. Tags help identify and group related templates.")
    cpu_count: int | None = Field(default=None, validation_alias="cpuCount", serialization_alias="cpuCount", description="Number of CPU cores to allocate to the sandbox. Must be at least 1 core.", json_schema_extra={'format': 'int32'})
    memory_mb: int | None = Field(default=None, validation_alias="memoryMB", serialization_alias="memoryMB", description="Memory to allocate to the sandbox in mebibytes (MiB). Must be at least 128 MiB.", json_schema_extra={'format': 'int32'})
class PostV3TemplatesRequest(StrictModel):
    """Create a new template with optional resource specifications and organizational tags. Templates define sandbox configurations for reproducible environments."""
    body: PostV3TemplatesRequestBody | None = None

# Operation: get_template_files_upload_link
class GetTemplatesFilesRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template for which to retrieve the files upload link.")
    hash_: str = Field(default=..., validation_alias="hash", serialization_alias="hash", description="The cryptographic hash that identifies the specific version or snapshot of the template files to retrieve.")
class GetTemplatesFilesRequest(StrictModel):
    """Retrieve a download link for a tar archive containing the build layer files associated with a specific template. The link is generated based on the template ID and file hash."""
    path: GetTemplatesFilesRequestPath

# Operation: list_templates
class GetTemplatesRequestQuery(StrictModel):
    team_id: str | None = Field(default=None, validation_alias="teamID", serialization_alias="teamID", description="Filter templates to a specific team. If omitted, returns templates accessible to all teams or the default scope.")
class GetTemplatesRequest(StrictModel):
    """Retrieve all templates available in the system, optionally filtered by a specific team. Use this to discover and display template options for users."""
    query: GetTemplatesRequestQuery | None = None

# Operation: list_template_builds
class GetTemplatesByTemplateIdRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template for which to retrieve builds.")
class GetTemplatesByTemplateIdRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of builds to return in a single page of results. Defaults to 100 if not specified.", json_schema_extra={'format': 'int32'})
class GetTemplatesByTemplateIdRequest(StrictModel):
    """Retrieve all builds associated with a specific template. Use pagination to control the number of results returned per page."""
    path: GetTemplatesByTemplateIdRequestPath
    query: GetTemplatesByTemplateIdRequestQuery | None = None

# Operation: delete_template
class DeleteTemplatesRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template to delete.")
class DeleteTemplatesRequest(StrictModel):
    """Permanently delete a template by its ID. This action cannot be undone."""
    path: DeleteTemplatesRequestPath

# Operation: start_template_build
class PostV2TemplatesBuildsRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template to build.")
    build_id: str = Field(default=..., validation_alias="buildID", serialization_alias="buildID", description="The unique identifier for this specific build execution.")
class PostV2TemplatesBuildsRequestBody(StrictModel):
    from_template: str | None = Field(default=None, validation_alias="fromTemplate", serialization_alias="fromTemplate", description="Optional template ID to use as a base for this template build, allowing inheritance of template configuration.")
    from_image_registry: Annotated[AwsRegistry | GcpRegistry | GeneralRegistry, Field(discriminator="type_")] | None = Field(default=None, validation_alias="fromImageRegistry", serialization_alias="fromImageRegistry", description="Optional image registry configuration for sourcing or pushing build artifacts.")
    force: bool | None = Field(default=None, description="Whether to bypass cache and force the entire build to execute from scratch.")
    steps: list[TemplateStep] | None = Field(default=None, description="Ordered list of build steps to execute. Each step represents a discrete build operation performed sequentially.")
    start_cmd: str | None = Field(default=None, validation_alias="startCmd", serialization_alias="startCmd", description="Command to execute within the template after the build completes, typically used to start services or initialize the environment.")
    ready_cmd: str | None = Field(default=None, validation_alias="readyCmd", serialization_alias="readyCmd", description="Command to execute after the build to verify the template is ready and operational, used for health checks or readiness validation.")
class PostV2TemplatesBuildsRequest(StrictModel):
    """Initiate a build process for a specific template. This operation executes the build with optional customization including base template selection, build steps, and post-build commands."""
    path: PostV2TemplatesBuildsRequestPath
    body: PostV2TemplatesBuildsRequestBody | None = None

# Operation: update_template
class PatchV2TemplatesRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template to update.")
class PatchV2TemplatesRequestBody(StrictModel):
    public: bool | None = Field(default=None, description="Controls template visibility. When true, the template is accessible to anyone; when false, it is restricted to team members only.")
class PatchV2TemplatesRequest(StrictModel):
    """Update an existing template's properties, such as its visibility settings. Modify template accessibility to be public or restricted to team members only."""
    path: PatchV2TemplatesRequestPath
    body: PatchV2TemplatesRequestBody | None = None

# Operation: get_template_build_status
class GetTemplatesBuildsStatusRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template containing the build.")
    build_id: str = Field(default=..., validation_alias="buildID", serialization_alias="buildID", description="The unique identifier of the build whose status should be retrieved.")
class GetTemplatesBuildsStatusRequestQuery(StrictModel):
    logs_offset: int | None = Field(default=None, validation_alias="logsOffset", serialization_alias="logsOffset", description="The starting index for build logs to return. Use this to paginate through large log sets.", json_schema_extra={'format': 'int32'})
    limit: int | None = Field(default=None, description="The maximum number of build logs to return in the response. Useful for controlling response size and pagination.", json_schema_extra={'format': 'int32'})
    level: Literal["debug", "info", "warn", "error"] | None = Field(default=None, description="Filter logs by severity level. Returns only logs matching the specified level or higher priority.")
class GetTemplatesBuildsStatusRequest(StrictModel):
    """Retrieve the current status and build logs for a specific template build. Returns build information with optional log filtering by offset, limit, and severity level."""
    path: GetTemplatesBuildsStatusRequestPath
    query: GetTemplatesBuildsStatusRequestQuery | None = None

# Operation: list_template_build_logs
class GetTemplatesBuildsLogsRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template containing the build.")
    build_id: str = Field(default=..., validation_alias="buildID", serialization_alias="buildID", description="The unique identifier of the build whose logs should be retrieved.")
class GetTemplatesBuildsLogsRequestQuery(StrictModel):
    cursor: int | None = Field(default=None, description="Starting point for log retrieval specified as a Unix timestamp in milliseconds. Logs returned will be from this timestamp onward (or backward, depending on direction).", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="Maximum number of log entries to return in a single response.", json_schema_extra={'format': 'int32'})
    direction: Literal["forward", "backward"] | None = Field(default=None, description="Order in which log entries should be returned relative to the cursor timestamp.")
    level: Literal["debug", "info", "warn", "error"] | None = Field(default=None, description="Filter logs by severity level. Only entries matching the specified level will be returned.")
    source: Literal["temporary", "persistent"] | None = Field(default=None, description="Filter logs by their storage source. Temporary logs are transient, while persistent logs are retained long-term.")
class GetTemplatesBuildsLogsRequest(StrictModel):
    """Retrieve logs from a template build execution. Supports filtering by log level and source, with pagination and directional traversal of log entries."""
    path: GetTemplatesBuildsLogsRequestPath
    query: GetTemplatesBuildsLogsRequestQuery | None = None

# Operation: assign_template_tags
class PostTemplatesTagsRequestBody(StrictModel):
    target: str = Field(default=..., description="The target template specified in 'name:tag' format, where name is the template identifier and tag is the specific build version.")
    tags: list[str] = Field(default=..., description="Array of tags to assign to the template. Tags are applied in the order provided and can be used for categorization and filtering.")
class PostTemplatesTagsRequest(StrictModel):
    """Assign one or more tags to a specific template build. Tags help organize and categorize templates for easier discovery and management."""
    body: PostTemplatesTagsRequestBody

# Operation: remove_template_tags
class DeleteTemplatesTagsRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the template from which tags will be removed.")
    tags: list[str] = Field(default=..., description="An array of tag names to remove from the template. Order is not significant.")
class DeleteTemplatesTagsRequest(StrictModel):
    """Remove one or more tags from a specific template. This operation allows bulk deletion of tags associated with a template."""
    body: DeleteTemplatesTagsRequestBody

# Operation: list_template_tags
class GetTemplatesTagsRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateID", serialization_alias="templateID", description="The unique identifier of the template for which to retrieve tags.")
class GetTemplatesTagsRequest(StrictModel):
    """Retrieve all tags associated with a specific template. Tags are used to categorize and organize templates for easier discovery and management."""
    path: GetTemplatesTagsRequestPath

# Operation: check_template_alias
class GetTemplatesAliasesRequestPath(StrictModel):
    alias: str = Field(default=..., description="The unique identifier or name of the template to check for existence.")
class GetTemplatesAliasesRequest(StrictModel):
    """Verify whether a template with the specified alias exists in the system."""
    path: GetTemplatesAliasesRequestPath

# Operation: get_node
class GetNodesByNodeIdRequestPath(StrictModel):
    node_id: str = Field(default=..., validation_alias="nodeID", serialization_alias="nodeID", description="The unique identifier of the node to retrieve.")
class GetNodesByNodeIdRequestQuery(StrictModel):
    cluster_id: str | None = Field(default=None, validation_alias="clusterID", serialization_alias="clusterID", description="The cluster to which the node belongs. Use this to scope the node lookup to a specific cluster.", json_schema_extra={'format': 'uuid'})
class GetNodesByNodeIdRequest(StrictModel):
    """Retrieve detailed information about a specific node, optionally filtered by cluster membership."""
    path: GetNodesByNodeIdRequestPath
    query: GetNodesByNodeIdRequestQuery | None = None

# Operation: update_node_status
class PostNodesRequestPath(StrictModel):
    node_id: str = Field(default=..., validation_alias="nodeID", serialization_alias="nodeID", description="The unique identifier of the node to update.")
class PostNodesRequestBody(StrictModel):
    cluster_id: str | None = Field(default=None, validation_alias="clusterID", serialization_alias="clusterID", description="The unique identifier of the cluster containing the node. Required to scope the node operation within the correct cluster context.", json_schema_extra={'format': 'uuid'})
    status: Literal["ready", "draining", "connecting", "unhealthy"] = Field(default=..., description="The desired operational status for the node. Determines how the node handles workloads and cluster participation.")
class PostNodesRequest(StrictModel):
    """Update the operational status of a node within a cluster. This operation allows you to transition a node between different states such as ready, draining, connecting, or unhealthy."""
    path: PostNodesRequestPath
    body: PostNodesRequestBody

# Operation: terminate_team_sandboxes
class PostAdminTeamsSandboxesKillRequestPath(StrictModel):
    team_id: str = Field(default=..., validation_alias="teamID", serialization_alias="teamID", description="The unique identifier of the team whose sandboxes should be terminated.", json_schema_extra={'format': 'uuid'})
class PostAdminTeamsSandboxesKillRequest(StrictModel):
    """Terminates all active sandboxes for a specified team. This operation will immediately stop and remove all sandbox instances associated with the team."""
    path: PostAdminTeamsSandboxesKillRequestPath

# Operation: create_access_token
class PostAccessTokensRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the access token to help identify its purpose or associated application.")
class PostAccessTokensRequest(StrictModel):
    """Create a new access token for API authentication. The token can be used to authorize requests to protected endpoints."""
    body: PostAccessTokensRequestBody

# Operation: revoke_access_token
class DeleteAccessTokensRequestPath(StrictModel):
    access_token_id: str = Field(default=..., validation_alias="accessTokenID", serialization_alias="accessTokenID", description="The unique identifier of the access token to revoke and delete.")
class DeleteAccessTokensRequest(StrictModel):
    """Revoke and delete an access token, immediately invalidating it for future API requests."""
    path: DeleteAccessTokensRequestPath

# Operation: create_api_key
class PostApiKeysRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the API key to help identify its purpose or associated application.")
class PostApiKeysRequest(StrictModel):
    """Create a new API key for your team to authenticate API requests. The key can be used to access team resources and data."""
    body: PostApiKeysRequestBody

# Operation: update_api_key
class PatchApiKeysRequestPath(StrictModel):
    api_key_id: str = Field(default=..., validation_alias="apiKeyID", serialization_alias="apiKeyID", description="The unique identifier of the API key to update.")
class PatchApiKeysRequestBody(StrictModel):
    name: str = Field(default=..., description="The new name for the API key. Use a descriptive name to identify the key's purpose or associated application.")
class PatchApiKeysRequest(StrictModel):
    """Update the name of a team API key. Allows you to rename an existing API key for better organization and identification."""
    path: PatchApiKeysRequestPath
    body: PatchApiKeysRequestBody

# Operation: delete_api_key
class DeleteApiKeysRequestPath(StrictModel):
    api_key_id: str = Field(default=..., validation_alias="apiKeyID", serialization_alias="apiKeyID", description="The unique identifier of the API key to delete.")
class DeleteApiKeysRequest(StrictModel):
    """Permanently delete a team API key. This action cannot be undone and will invalidate any requests using this key."""
    path: DeleteApiKeysRequestPath

# Operation: create_volume
class PostVolumesRequestBody(StrictModel):
    name: str = Field(default=..., description="The name identifier for the volume. Must contain only letters, numbers, hyphens, and underscores.", pattern='^[a-zA-Z0-9_-]+$')
class PostVolumesRequest(StrictModel):
    """Create a new team volume for storing and organizing data. The volume name must be unique within the team and follow alphanumeric naming conventions."""
    body: PostVolumesRequestBody

# Operation: get_volume
class GetVolumesByVolumeIdRequestPath(StrictModel):
    volume_id: str = Field(default=..., validation_alias="volumeID", serialization_alias="volumeID", description="The unique identifier of the volume to retrieve.")
class GetVolumesByVolumeIdRequest(StrictModel):
    """Retrieve detailed information about a specific team volume by its unique identifier."""
    path: GetVolumesByVolumeIdRequestPath

# Operation: delete_volume
class DeleteVolumesRequestPath(StrictModel):
    volume_id: str = Field(default=..., validation_alias="volumeID", serialization_alias="volumeID", description="The unique identifier of the volume to delete.")
class DeleteVolumesRequest(StrictModel):
    """Permanently delete a team volume by its ID. This action cannot be undone."""
    path: DeleteVolumesRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AwsRegistry(PermissiveModel):
    type_: Literal["aws"] = Field(..., validation_alias="type", serialization_alias="type", description="Type of registry authentication")
    aws_access_key_id: str = Field(..., validation_alias="awsAccessKeyId", serialization_alias="awsAccessKeyId", description="AWS Access Key ID for ECR authentication")
    aws_secret_access_key: str = Field(..., validation_alias="awsSecretAccessKey", serialization_alias="awsSecretAccessKey", description="AWS Secret Access Key for ECR authentication")
    aws_region: str = Field(..., validation_alias="awsRegion", serialization_alias="awsRegion", description="AWS Region where the ECR registry is located")

class GcpRegistry(PermissiveModel):
    type_: Literal["gcp"] = Field(..., validation_alias="type", serialization_alias="type", description="Type of registry authentication")
    service_account_json: str = Field(..., validation_alias="serviceAccountJson", serialization_alias="serviceAccountJson", description="Service Account JSON for GCP authentication")

class GeneralRegistry(PermissiveModel):
    type_: Literal["registry"] = Field(..., validation_alias="type", serialization_alias="type", description="Type of registry authentication")
    username: str = Field(..., description="Username to use for the registry")
    password: str = Field(..., description="Password to use for the registry")

class SandboxVolumeMount(PermissiveModel):
    name: str = Field(..., description="Name of the volume")
    path: str = Field(..., description="Path of the volume")

class TemplateStep(PermissiveModel):
    """Step in the template build process"""
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Type of the step")
    args: list[str] | None = Field([], description="Arguments for the step")
    files_hash: str | None = Field(None, validation_alias="filesHash", serialization_alias="filesHash", description="Hash of the files used in the step")
    force: bool | None = Field(False, description="Whether the step should be forced to run regardless of the cache")

class Volume(PermissiveModel):
    volume_id: str = Field(..., validation_alias="volumeID", serialization_alias="volumeID", description="ID of the volume")
    name: str = Field(..., description="Name of the volume")


# Rebuild models to resolve forward references (required for circular refs)
AwsRegistry.model_rebuild()
GcpRegistry.model_rebuild()
GeneralRegistry.model_rebuild()
SandboxVolumeMount.model_rebuild()
TemplateStep.model_rebuild()
Volume.model_rebuild()

"""
Circleci MCP Server - Pydantic Models

Generated: 2026-05-11 23:15:02 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AddEnvironmentVariableToContextRequest",
    "ApprovePendingApprovalJobByIdRequest",
    "CancelJobByJobIdRequest",
    "CancelJobByJobNumberRequest",
    "CancelWorkflowRequest",
    "ContinuePipelineRequest",
    "CreateCheckoutKeyRequest",
    "CreateContextRequest",
    "CreateContextRestrictionRequest",
    "CreateEnvVarRequest",
    "CreateOrganizationGroupRequest",
    "CreateOrganizationRequest",
    "CreateOtelExporterRequest",
    "CreatePipelineDefinitionRequest",
    "CreateProjectRequest",
    "CreateScheduleRequest",
    "CreateTriggerRequest",
    "CreateUrlOrbAllowListEntryRequest",
    "CreateUsageExportRequest",
    "CreateWebhookRequest",
    "DeleteCheckoutKeyRequest",
    "DeleteContextRequest",
    "DeleteContextRestrictionRequest",
    "DeleteEnvironmentVariableFromContextRequest",
    "DeleteEnvVarRequest",
    "DeleteGroupRequest",
    "DeleteOrganizationRequest",
    "DeleteOrgClaimsRequest",
    "DeleteOtelExporterRequest",
    "DeletePipelineDefinitionRequest",
    "DeleteProjectBySlugRequest",
    "DeleteProjectClaimsRequest",
    "DeleteScheduleByIdRequest",
    "DeleteTriggerRequest",
    "DeleteWebhookRequest",
    "GetAllInsightsBranchesRequest",
    "GetCheckoutKeyRequest",
    "GetComponentRequest",
    "GetContextRequest",
    "GetContextRestrictionsRequest",
    "GetDecisionLogPolicyBundleRequest",
    "GetDecisionLogRequest",
    "GetDecisionLogsRequest",
    "GetEnvironmentRequest",
    "GetEnvVarRequest",
    "GetFlakyTestsRequest",
    "GetGroupRequest",
    "GetJobArtifactsRequest",
    "GetJobDetailsRequest",
    "GetJobTimeseriesRequest",
    "GetOrganizationGroupsRequest",
    "GetOrganizationRequest",
    "GetOrgClaimsRequest",
    "GetOrgSummaryDataRequest",
    "GetPipelineByIdRequest",
    "GetPipelineByNumberRequest",
    "GetPipelineConfigByIdRequest",
    "GetPipelineDefinitionRequest",
    "GetPipelineValuesByIdRequest",
    "GetPolicyBundleRequest",
    "GetProjectBySlugRequest",
    "GetProjectClaimsRequest",
    "GetProjectSettingsRequest",
    "GetProjectWorkflowJobMetricsRequest",
    "GetProjectWorkflowMetricsRequest",
    "GetProjectWorkflowRunsRequest",
    "GetProjectWorkflowsPageDataRequest",
    "GetProjectWorkflowTestMetricsRequest",
    "GetScheduleByIdRequest",
    "GetTestsRequest",
    "GetTriggerRequest",
    "GetUsageExportRequest",
    "GetUserRequest",
    "GetWebhookByIdRequest",
    "GetWebhooksRequest",
    "GetWorkflowByIdRequest",
    "GetWorkflowSummaryRequest",
    "ListCheckoutKeysRequest",
    "ListComponentsRequest",
    "ListComponentVersionsRequest",
    "ListContextsRequest",
    "ListEnvironmentsRequest",
    "ListEnvironmentVariablesFromContextRequest",
    "ListEnvVarsRequest",
    "ListMyPipelinesRequest",
    "ListOtelExportersRequest",
    "ListPipelineDefinitionsRequest",
    "ListPipelineDefinitionTriggersRequest",
    "ListPipelinesForProjectRequest",
    "ListPipelinesRequest",
    "ListSchedulesForProjectRequest",
    "ListUrlOrbAllowListEntriesRequest",
    "ListWorkflowJobsRequest",
    "ListWorkflowsByPipelineIdRequest",
    "PatchOrgClaimsRequest",
    "PatchProjectClaimsRequest",
    "PatchProjectSettingsRequest",
    "RemoveUrlOrbAllowListEntryRequest",
    "RerunWorkflowRequest",
    "RollbackProjectRequest",
    "TriggerPipelineRequest",
    "TriggerPipelineRunRequest",
    "UpdatePipelineDefinitionRequest",
    "UpdateScheduleRequest",
    "UpdateTriggerRequest",
    "UpdateWebhookRequest",
    "CreateContextBodyOwnerV0",
    "CreateContextBodyOwnerV1",
    "CreatePipelineDefinitionBodyConfigSourceV0",
    "CreatePipelineDefinitionBodyConfigSourceV1",
    "CreateScheduleBodyTimetableV0",
    "CreateScheduleBodyTimetableV1",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_project_workflow_summary
class GetProjectWorkflowsPageDataRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug identifying the target project, formed as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped.")
class GetProjectWorkflowsPageDataRequestQuery(StrictModel):
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(default=None, validation_alias="reporting-window", serialization_alias="reporting-window", description="The time window over which summary metrics are calculated. Trends are only supported for windows up to 30 days; defaults to last-90-days if omitted.")
    branches: dict[str, Any] | None = Field(default=None, description="One or more VCS branch names to filter branch-level workflow metrics. Multiple branches can be specified by repeating the query parameter.")
    workflow_names: dict[str, Any] | None = Field(default=None, validation_alias="workflow-names", serialization_alias="workflow-names", description="One or more workflow names to filter workflow-level metrics. Multiple workflow names can be specified by repeating the query parameter.")
class GetProjectWorkflowsPageDataRequest(StrictModel):
    """Retrieves aggregated summary metrics and trends for a project across its workflows and branches, covering up to 90 days of workflow run history. Note: Insights data is not suitable for precise credit reporting; use the CircleCI Plan Overview page for billing accuracy."""
    path: GetProjectWorkflowsPageDataRequestPath
    query: GetProjectWorkflowsPageDataRequestQuery | None = None

# Operation: list_job_timeseries
class GetJobTimeseriesRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name.")
    workflow_name: str = Field(default=..., validation_alias="workflow-name", serialization_alias="workflow-name", description="The exact name of the workflow for which to retrieve job timeseries data.")
class GetJobTimeseriesRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The name of the VCS branch to scope results to. Defaults to the repository's default branch if omitted.")
    granularity: Literal["daily", "hourly"] | None = Field(default=None, description="The time resolution for the returned timeseries data, either per hour or per day. Hourly data is only available for the past 48 hours; daily data is available for up to 90 days.")
    start_date: str | None = Field(default=None, validation_alias="start-date", serialization_alias="start-date", description="The inclusive start of the time range filter, in ISO 8601 date-time format. Must be provided if an end-date is specified.", json_schema_extra={'format': 'date-time'})
    end_date: str | None = Field(default=None, validation_alias="end-date", serialization_alias="end-date", description="The exclusive end of the time range filter, in ISO 8601 date-time format. Must be no more than 90 days after the start-date.", json_schema_extra={'format': 'date-time'})
class GetJobTimeseriesRequest(StrictModel):
    """Retrieve timeseries performance data for all jobs within a specified workflow, supporting hourly or daily granularity. Hourly data is retained for 48 hours and daily data for 90 days."""
    path: GetJobTimeseriesRequestPath
    query: GetJobTimeseriesRequestQuery | None = None

# Operation: get_org_summary
class GetOrgSummaryDataRequestPath(StrictModel):
    org_slug: str = Field(default=..., validation_alias="org-slug", serialization_alias="org-slug", description="The organization slug identifying the target org, combining the VCS provider slug and organization name separated by a forward slash (which may be URL-encoded).")
class GetOrgSummaryDataRequestQuery(StrictModel):
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(default=None, validation_alias="reporting-window", serialization_alias="reporting-window", description="The time window over which summary metrics are calculated and trends are derived. Defaults to the last 90 days if not specified.")
    project_names: dict[str, Any] | None = Field(default=None, validation_alias="project-names", serialization_alias="project-names", description="An optional list of project names used to filter results to specific projects within the org. Provide the parameter multiple times to include multiple projects.")
class GetOrgSummaryDataRequest(StrictModel):
    """Retrieves aggregated performance metrics and trends for an entire organization and each of its projects. Supports filtering by a specific reporting window and an optional subset of projects."""
    path: GetOrgSummaryDataRequestPath
    query: GetOrgSummaryDataRequestQuery | None = None

# Operation: list_project_branches
class GetAllInsightsBranchesRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped.")
class GetAllInsightsBranchesRequestQuery(StrictModel):
    workflow_name: str | None = Field(default=None, validation_alias="workflow-name", serialization_alias="workflow-name", description="Filters the returned branches to only those associated with the specified workflow name. When omitted, branches are scoped to the entire project across all workflows.")
class GetAllInsightsBranchesRequest(StrictModel):
    """Retrieves all branches currently tracked within Insights for a specified project. Returns up to 5,000 branches, optionally scoped to a specific workflow."""
    path: GetAllInsightsBranchesRequestPath
    query: GetAllInsightsBranchesRequestQuery | None = None

# Operation: list_flaky_tests
class GetFlakyTestsRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped.")
class GetFlakyTestsRequest(StrictModel):
    """Retrieves all flaky tests for a given project, where a flaky test is defined as one that both passed and failed within the same commit. Results are branch-agnostic."""
    path: GetFlakyTestsRequestPath

# Operation: list_workflow_metrics
class GetProjectWorkflowMetricsRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the Organization ID (from Organization Settings) as org-name, and the Project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
class GetProjectWorkflowMetricsRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Filters metrics to a specific VCS branch by name. If omitted, metrics are scoped to the project's default branch.")
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(default=None, validation_alias="reporting-window", serialization_alias="reporting-window", description="Defines the time window over which summary metrics are calculated. Accepts predefined window values; if omitted, defaults to the last 90 days.")
class GetProjectWorkflowMetricsRequest(StrictModel):
    """Retrieves aggregated summary metrics for all workflows in a project, covering up to the last 90 days. Metrics are refreshed daily and are intended for performance insights, not precise credit or billing reporting."""
    path: GetProjectWorkflowMetricsRequestPath
    query: GetProjectWorkflowMetricsRequestQuery | None = None

# Operation: list_workflow_runs
class GetProjectWorkflowRunsRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the Organization ID as org-name, and the Project ID as repo-name.")
    workflow_name: str = Field(default=..., validation_alias="workflow-name", serialization_alias="workflow-name", description="The exact name of the workflow whose runs you want to retrieve, as defined in the project's pipeline configuration.")
class GetProjectWorkflowRunsRequestQuery(StrictModel):
    all_branches: bool | None = Field(default=None, validation_alias="all-branches", serialization_alias="all-branches", description="When set to true, aggregates data across all branches. Use either this parameter or the branch parameter, but not both simultaneously.")
    branch: str | None = Field(default=None, description="Filters results to a specific VCS branch by name. Defaults to the repository's default branch if omitted; cannot be used together with all-branches.")
    start_date: str | None = Field(default=None, validation_alias="start-date", serialization_alias="start-date", description="Filters results to only include workflow runs that started at or after this ISO 8601 datetime. Required when an end-date is specified.", json_schema_extra={'format': 'date-time'})
    end_date: str | None = Field(default=None, validation_alias="end-date", serialization_alias="end-date", description="Filters results to only include workflow runs that started before this ISO 8601 datetime. Must be no more than 90 days after the start-date.", json_schema_extra={'format': 'date-time'})
class GetProjectWorkflowRunsRequest(StrictModel):
    """Retrieves recent runs of a specific workflow within a project, covering executions up to 90 days in the past. Note that Insights data is not suitable for precise credit reporting; use the CircleCI UI Plan Overview page for accurate billing information."""
    path: GetProjectWorkflowRunsRequestPath
    query: GetProjectWorkflowRunsRequestQuery | None = None

# Operation: list_workflow_job_metrics
class GetProjectWorkflowJobMetricsRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the form `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
    workflow_name: str = Field(default=..., validation_alias="workflow-name", serialization_alias="workflow-name", description="The exact name of the workflow whose job metrics you want to retrieve.")
class GetProjectWorkflowJobMetricsRequestQuery(StrictModel):
    all_branches: bool | None = Field(default=None, validation_alias="all-branches", serialization_alias="all-branches", description="When set to true, aggregates metrics across all branches. Use either this parameter or the branch parameter, not both.")
    branch: str | None = Field(default=None, description="Filters metrics to a specific VCS branch by name. Defaults to the repository's default branch if neither this nor all-branches is provided.")
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(default=None, validation_alias="reporting-window", serialization_alias="reporting-window", description="Defines the time window over which summary metrics are calculated. Defaults to the last 90 days if not specified.")
    job_name: str | None = Field(default=None, validation_alias="job-name", serialization_alias="job-name", description="Filters results to jobs whose names match the provided string, either as a full job name or a substring. Returns metrics for all jobs in the workflow if omitted.")
class GetProjectWorkflowJobMetricsRequest(StrictModel):
    """Retrieves aggregated summary metrics for all jobs within a specific project workflow, covering up to the last 90 days. Metrics are refreshed daily and are intended for performance analysis, not precise credit or billing reporting."""
    path: GetProjectWorkflowJobMetricsRequestPath
    query: GetProjectWorkflowJobMetricsRequestQuery | None = None

# Operation: get_workflow_summary
class GetWorkflowSummaryRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project, formatted as vcs-slug/org-name/repo-name. For GitLab or GitHub App projects, use 'circleci' as the vcs-slug, the organization ID as org-name, and the project ID as repo-name.")
    workflow_name: str = Field(default=..., validation_alias="workflow-name", serialization_alias="workflow-name", description="The exact name of the workflow for which to retrieve summary metrics.")
class GetWorkflowSummaryRequestQuery(StrictModel):
    all_branches: bool | None = Field(default=None, validation_alias="all-branches", serialization_alias="all-branches", description="When set to true, aggregates metrics across all branches instead of a single branch. Use either this parameter or the branch parameter, not both.")
    branch: str | None = Field(default=None, description="The name of the VCS branch to scope metrics to. If omitted and all-branches is not set, results default to the repository's default branch.")
class GetWorkflowSummaryRequest(StrictModel):
    """Retrieves aggregated metrics and trends for a specific workflow within a project, such as duration, success rate, and run frequency. Results can be scoped to a single branch or aggregated across all branches."""
    path: GetWorkflowSummaryRequestPath
    query: GetWorkflowSummaryRequestQuery | None = None

# Operation: get_workflow_test_metrics
class GetProjectWorkflowTestMetricsRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped.")
    workflow_name: str = Field(default=..., validation_alias="workflow-name", serialization_alias="workflow-name", description="The exact name of the workflow for which test metrics should be retrieved.")
class GetProjectWorkflowTestMetricsRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Scopes results to a specific VCS branch name. Defaults to the repository's default branch if omitted. Mutually exclusive with the all-branches parameter.")
    all_branches: bool | None = Field(default=None, validation_alias="all-branches", serialization_alias="all-branches", description="When set to true, aggregates test metrics across all branches rather than a single branch. Mutually exclusive with the branch parameter; use one or the other, not both.")
class GetProjectWorkflowTestMetricsRequest(StrictModel):
    """Retrieves test metrics for a specific workflow within a project, calculated from the 10 most recent workflow runs. Results can be scoped to a specific branch or aggregated across all branches."""
    path: GetProjectWorkflowTestMetricsRequestPath
    query: GetProjectWorkflowTestMetricsRequestQuery | None = None

# Operation: cancel_job
class CancelJobByJobIdRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="job-id", serialization_alias="job-id", description="The unique identifier of the job to cancel, in UUID format.", json_schema_extra={'format': 'uuid'})
class CancelJobByJobIdRequest(StrictModel):
    """Cancels an active job identified by its unique job ID. Use this to stop a job that is pending or in progress before it completes."""
    path: CancelJobByJobIdRequestPath

# Operation: create_organization
class CreateOrganizationRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the organization being created.")
    vcs_type: Literal["github", "bitbucket", "circleci"] | None = Field(default=None, description="The version control system associated with the organization, or 'circleci' for a standalone organization not tied to a VCS provider.")
class CreateOrganizationRequest(StrictModel):
    """Creates a new organization, either by validating access and syncing data for a VCS provider (GitHub or Bitbucket), or by provisioning a standalone CircleCI organization."""
    body: CreateOrganizationRequestBody | None = None

# Operation: get_organization
class GetOrganizationRequestPath(StrictModel):
    org_slug_or_id: str = Field(default=..., validation_alias="org-slug-or-id", serialization_alias="org-slug-or-id", description="The organization identifier, either as a UUID or a VCS slug in the format `vcs-slug/org-name` (e.g., `gh/` for GitHub, `bb/` for Bitbucket). For GitLab or GitHub App integrations, use `circleci` as the VCS slug and provide the numeric organization ID (found in Organization Settings) in place of the org name.")
class GetOrganizationRequest(StrictModel):
    """Retrieves details for a specific organization by its slug or UUID. Supports organizations across GitHub, Bitbucket, and GitLab (via CircleCI VCS slug)."""
    path: GetOrganizationRequestPath

# Operation: delete_organization
class DeleteOrganizationRequestPath(StrictModel):
    org_slug_or_id: str = Field(default=..., validation_alias="org-slug-or-id", serialization_alias="org-slug-or-id", description="The unique identifier for the organization, either as a UUID or a VCS-prefixed slug in the format `vcs-slug/org-name`. For organizations using GitLab or GitHub App, use `circleci` as the VCS slug and the organization ID (found in Organization Settings) as the org name.")
class DeleteOrganizationRequest(StrictModel):
    """Permanently deletes an organization and all associated projects and build data. This action is irreversible and will remove all resources tied to the organization."""
    path: DeleteOrganizationRequestPath

# Operation: create_project
class CreateProjectRequestPath(StrictModel):
    org_slug_or_id: str = Field(default=..., validation_alias="org-slug-or-id", serialization_alias="org-slug-or-id", description="The unique identifier for the organization, either as a UUID or a VCS-based slug in the format `vcs-slug/org-name`. For organizations using GitLab or GitHub App integrations, use `circleci` as the VCS slug and provide the numeric organization ID (available in Organization Settings) in place of the org name.")
class CreateProjectRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the new project. Should be unique within the organization and clearly identify the project.")
class CreateProjectRequest(StrictModel):
    """Creates a new project within the specified organization. Works across all organization types including GitHub, GitLab, and CircleCI-managed organizations."""
    path: CreateProjectRequestPath
    body: CreateProjectRequestBody | None = None

# Operation: list_url_orb_allow_list_entries
class ListUrlOrbAllowListEntriesRequestPath(StrictModel):
    org_slug_or_id: str = Field(default=..., validation_alias="org-slug-or-id", serialization_alias="org-slug-or-id", description="The organization identifier, either as a UUID or a slug in the format `vcs-slug/org-name`. For organizations using GitLab or GitHub App, use `circleci` as the VCS slug and provide the organization ID (available in Organization Settings) in place of the org name.")
class ListUrlOrbAllowListEntriesRequest(StrictModel):
    """Retrieves all entries in the URL Orb allow-list for the specified organization. Use this to review which URLs are permitted under the org's URL Orb configuration."""
    path: ListUrlOrbAllowListEntriesRequestPath

# Operation: create_url_orb_allow_list_entry
class CreateUrlOrbAllowListEntryRequestPath(StrictModel):
    org_slug_or_id: str = Field(default=..., validation_alias="org-slug-or-id", serialization_alias="org-slug-or-id", description="The organization identifier, either as a UUID or a slug in the form `vcs-slug/org-name`. For organizations using GitLab or GitHub App, use `circleci` as the vcs-slug and the organization ID (found in Organization Settings) as the org-name.")
class CreateUrlOrbAllowListEntryRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable label for this allow-list entry to help identify its purpose within the organization.")
    prefix: Any | None = Field(default=None, description="The URL prefix that defines which URL orb references are permitted; any orb reference URL beginning with this prefix will be allowed by this entry.")
class CreateUrlOrbAllowListEntryRequest(StrictModel):
    """Adds a new URL prefix entry to an organization's URL Orb allow-list, permitting orb references that begin with the specified URL prefix to be used in pipelines."""
    path: CreateUrlOrbAllowListEntryRequestPath
    body: CreateUrlOrbAllowListEntryRequestBody | None = None

# Operation: delete_url_orb_allow_list_entry
class RemoveUrlOrbAllowListEntryRequestPath(StrictModel):
    org_slug_or_id: str = Field(default=..., validation_alias="org-slug-or-id", serialization_alias="org-slug-or-id", description="The organization identifier, either as a UUID or a slug in the format `vcs-slug/org-name`. For GitLab or GitHub App projects, use `circleci` as the `vcs-slug` and provide the organization ID (found in Organization Settings) as the `org-name`.")
    allow_list_entry_id: str = Field(default=..., validation_alias="allow-list-entry-id", serialization_alias="allow-list-entry-id", description="The UUID of the URL orb allow-list entry to remove. This uniquely identifies the specific allow-list entry to be deleted.")
class RemoveUrlOrbAllowListEntryRequest(StrictModel):
    """Removes a specific entry from the organization's URL orb allow-list by its unique ID. Use this to revoke previously permitted URLs from the allow-list."""
    path: RemoveUrlOrbAllowListEntryRequestPath

# Operation: list_pipelines
class ListPipelinesRequestQuery(StrictModel):
    org_slug: str | None = Field(default=None, validation_alias="org-slug", serialization_alias="org-slug", description="The organization slug identifying the target organization, formatted as vcs-slug/org-name. For GitLab or GitHub App projects, use 'circleci' as the vcs-slug and supply the organization ID (found in Organization Settings) as the org-name.")
    mine: bool | None = Field(default=None, description="When set to true, restricts results to only pipelines triggered by the authenticated user.")
class ListPipelinesRequest(StrictModel):
    """Retrieves up to 250 pipelines from the most recently built projects you follow within an organization. Optionally filter by organization or limit results to pipelines triggered by your user."""
    query: ListPipelinesRequestQuery | None = None

# Operation: continue_pipeline
class ContinuePipelineRequestBody(StrictModel):
    continuation_key: str | None = Field(default=None, validation_alias="continuation-key", serialization_alias="continuation-key", description="The unique continuation key that identifies the paused pipeline to resume, obtained from the pipeline setup phase.")
    configuration: str | None = Field(default=None, description="The full pipeline configuration string to apply when continuing the pipeline, used to supply dynamic configuration at runtime.")
    parameters: dict[str, int | str | bool] | None = Field(default=None, description="A key-value map of pipeline parameter names to their values, subject to limits of 100 max entries, 128-character maximum key length, and 512-character maximum value length.")
class ContinuePipelineRequest(StrictModel):
    """Resumes a pipeline from the setup phase using a continuation key, allowing dynamic configuration and parameter injection. Refer to the Pipeline values and parameters documentation for guidance on using pipeline parameters with dynamic configuration."""
    body: ContinuePipelineRequestBody | None = None

# Operation: get_pipeline
class GetPipelineByIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., validation_alias="pipeline-id", serialization_alias="pipeline-id", description="The unique identifier of the pipeline to retrieve, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetPipelineByIdRequest(StrictModel):
    """Retrieves detailed information about a specific pipeline using its unique identifier. Returns the full pipeline configuration and metadata."""
    path: GetPipelineByIdRequestPath

# Operation: get_pipeline_config
class GetPipelineConfigByIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., validation_alias="pipeline-id", serialization_alias="pipeline-id", description="The unique identifier of the pipeline whose configuration you want to retrieve. Must be a valid UUID corresponding to an existing pipeline.", json_schema_extra={'format': 'uuid'})
class GetPipelineConfigByIdRequest(StrictModel):
    """Retrieves the full configuration for a specific pipeline by its unique ID. Useful for inspecting pipeline settings, stages, and parameters without modifying them."""
    path: GetPipelineConfigByIdRequestPath

# Operation: get_pipeline_values
class GetPipelineValuesByIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., validation_alias="pipeline-id", serialization_alias="pipeline-id", description="The unique identifier of the pipeline whose values you want to retrieve, in UUID format.", json_schema_extra={'format': 'uuid'})
class GetPipelineValuesByIdRequest(StrictModel):
    """Retrieves a map of built-in pipeline values (such as pipeline number, trigger parameters, and VCS metadata) for a specific pipeline. Useful for inspecting runtime context associated with a pipeline execution."""
    path: GetPipelineValuesByIdRequestPath

# Operation: list_pipeline_workflows
class ListWorkflowsByPipelineIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., validation_alias="pipeline-id", serialization_alias="pipeline-id", description="The unique identifier of the pipeline whose workflows you want to retrieve. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class ListWorkflowsByPipelineIdRequest(StrictModel):
    """Retrieves a paginated list of workflows associated with a specific pipeline. Use this to inspect all workflows belonging to a given pipeline by its unique identifier."""
    path: ListWorkflowsByPipelineIdRequestPath

# Operation: get_project
class GetProjectBySlugRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the VCS slug, the organization ID (from Organization Settings) as the org name, and the project ID (from Project Settings) as the repo name.")
class GetProjectBySlugRequest(StrictModel):
    """Retrieves detailed information about a specific CircleCI project using its unique project slug. Supports projects hosted on GitHub, GitLab, and Bitbucket, including those using the GitHub App integration."""
    path: GetProjectBySlugRequestPath

# Operation: delete_project
class DeleteProjectBySlugRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
class DeleteProjectBySlugRequest(StrictModel):
    """Permanently deletes a project from CircleCI using its unique project slug. This action is irreversible and removes all associated project data."""
    path: DeleteProjectBySlugRequestPath

# Operation: list_checkout_keys
class ListCheckoutKeysRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug uniquely identifying the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID in place of org-name, and the project ID in place of repo-name; forward slashes may be URL-encoded.")
class ListCheckoutKeysRequestQuery(StrictModel):
    digest: Literal["sha256", "md5"] | None = Field(default=None, description="The hashing algorithm used to format the returned key fingerprints; accepted values are `md5` or `sha256`, defaulting to `md5` if omitted.")
class ListCheckoutKeysRequest(StrictModel):
    """Retrieves all checkout keys associated with a specified project, returning their fingerprints and metadata. Useful for auditing or managing SSH keys used during CI/CD checkout steps."""
    path: ListCheckoutKeysRequestPath
    query: ListCheckoutKeysRequestQuery | None = None

# Operation: create_checkout_key
class CreateCheckoutKeyRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug identifying the target project, formed as vcs-slug/org-name/repo-name. For GitLab or GitHub App projects, use 'circleci' as the vcs-slug with the organization ID and project ID in place of org-name and repo-name respectively.")
class CreateCheckoutKeyRequestBody(StrictModel):
    type_: Literal["user-key", "deploy-key"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of checkout key to create: 'deploy-key' grants read-only repository access for deployments, while 'user-key' grants access tied to a specific GitHub user account.")
class CreateCheckoutKeyRequest(StrictModel):
    """Creates a new checkout key (deploy key or user key) for a specified project. Only available for GitHub and Bitbucket projects using a user API token; requires GitHub account authorization before creating user keys."""
    path: CreateCheckoutKeyRequestPath
    body: CreateCheckoutKeyRequestBody | None = None

# Operation: get_checkout_key
class GetCheckoutKeyRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped.")
    fingerprint: str = Field(default=..., description="The SSH key fingerprint used to uniquely identify the checkout key, accepted in either MD5 or SHA256 format. SHA256 fingerprints must be URL-encoded.")
class GetCheckoutKeyRequest(StrictModel):
    """Retrieves a specific checkout key for a project using its MD5 or SHA256 fingerprint. SHA256 fingerprints must be URL-encoded before being passed as the fingerprint parameter."""
    path: GetCheckoutKeyRequestPath

# Operation: delete_checkout_key
class DeleteCheckoutKeyRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug identifying the target project, formed as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped.")
    fingerprint: str = Field(default=..., description="The MD5 or SHA256 fingerprint of the SSH checkout key to delete. SHA256 fingerprints must be URL-encoded.")
class DeleteCheckoutKeyRequest(StrictModel):
    """Deletes a specific checkout key for a project using its MD5 or SHA256 fingerprint. SHA256 fingerprints must be URL-encoded before being passed as the fingerprint parameter."""
    path: DeleteCheckoutKeyRequestPath

# Operation: list_env_vars
class ListEnvVarsRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
class ListEnvVarsRequest(StrictModel):
    """Retrieves all environment variables for a specified CircleCI project. Values are masked, returning only the last four characters prefixed with four 'x' characters, matching the display behavior on the CircleCI website."""
    path: ListEnvVarsRequestPath

# Operation: create_env_var
class CreateEnvVarRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug uniquely identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped.")
class CreateEnvVarRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The name of the environment variable to create, which must be unique within the project and will be used to reference the variable in pipeline configurations.")
    value: str | None = Field(default=None, description="The value to assign to the environment variable; once stored, this value will be masked and not returned in plaintext by the API.")
class CreateEnvVarRequest(StrictModel):
    """Creates a new environment variable for a specified CircleCI project, making it available to pipelines and jobs running within that project."""
    path: CreateEnvVarRequestPath
    body: CreateEnvVarRequestBody | None = None

# Operation: get_env_var
class GetEnvVarRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug identifying the target project, formed as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped.")
    name: str = Field(default=..., description="The exact name of the environment variable to retrieve, matching the name as defined in the project's environment variable settings.")
class GetEnvVarRequest(StrictModel):
    """Retrieves the masked value of a specific environment variable for a given project. The returned value is masked for security purposes."""
    path: GetEnvVarRequestPath

# Operation: delete_env_var
class DeleteEnvVarRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug uniquely identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name; forward slashes may be URL-encoded.")
    name: str = Field(default=..., description="The exact name of the environment variable to delete, matching the variable's name as it appears in the project's environment variable settings.")
class DeleteEnvVarRequest(StrictModel):
    """Permanently deletes a specific environment variable from a CircleCI project. This action is irreversible and immediately removes the variable from the project's configuration."""
    path: DeleteEnvVarRequestPath

# Operation: get_job_details
class GetJobDetailsRequestPath(StrictModel):
    job_number: Any = Field(default=..., validation_alias="job-number", serialization_alias="job-number", description="The unique numeric identifier of the job to retrieve details for.")
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Project slug identifying the target project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name.")
class GetJobDetailsRequest(StrictModel):
    """Retrieves detailed information about a specific job within a project, including its status, timing, and configuration. Use this to inspect the outcome or metadata of a particular job run."""
    path: GetJobDetailsRequestPath

# Operation: cancel_job_by_number
class CancelJobByJobNumberRequestPath(StrictModel):
    job_number: Any = Field(default=..., validation_alias="job-number", serialization_alias="job-number", description="The unique numeric identifier of the job to cancel within the project.")
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Project slug identifying the target project, formatted as vcs-slug/org-name/repo-name. For GitLab or GitHub App projects, use circleci as the vcs-slug, the organization ID as org-name, and the project ID as repo-name; forward slashes may be URL-escaped.")
class CancelJobByJobNumberRequest(StrictModel):
    """Cancels a running job in a specified project using its job number. Useful for stopping unwanted or erroneous builds mid-execution."""
    path: CancelJobByJobNumberRequestPath

# Operation: list_project_pipelines
class ListPipelinesForProjectRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
class ListPipelinesForProjectRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Filters returned pipelines to only those triggered on the specified branch name. When omitted, pipelines from all branches are returned.")
class ListPipelinesForProjectRequest(StrictModel):
    """Retrieves all pipelines for a specified project, optionally filtered by branch. Useful for monitoring CI/CD activity and pipeline history across a project."""
    path: ListPipelinesForProjectRequestPath
    query: ListPipelinesForProjectRequestQuery | None = None

# Operation: trigger_pipeline
class TriggerPipelineRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where forward slashes may be URL-encoded. For GitLab or GitHub App projects, use `circleci` as the vcs-slug with the organization ID and project ID in place of org and repo names.")
class TriggerPipelineRequestBody(StrictModel):
    branch: str | None = Field(default=None, description="The branch to run the pipeline against, using the HEAD commit of that branch. Mutually exclusive with `tag`; only one may be provided. To target a pull request, use `pull/<number>/head` for the PR ref or `pull/<number>/merge` for the merge ref (GitHub only).")
    tag: str | None = Field(default=None, description="A Git tag whose pointed-to commit will be used for the pipeline run. Mutually exclusive with `branch`; only one may be provided.")
    parameters: dict[str, int | str | bool] | None = Field(default=None, description="A key-value map of pipeline parameter names to their values, used to customize the pipeline run. Limited to 100 entries, with keys up to 128 characters and values up to 512 characters each.")
class TriggerPipelineRequest(StrictModel):
    """Triggers a new pipeline run on a specified project using a branch, tag, or custom parameters. Note: this endpoint does not support GitLab or GitHub App projects — use the Trigger Pipeline Run API for those."""
    path: TriggerPipelineRequestPath
    body: TriggerPipelineRequestBody | None = None

# Operation: list_my_pipelines
class ListMyPipelinesRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
class ListMyPipelinesRequest(StrictModel):
    """Retrieves all pipelines for a specified project that were triggered by the authenticated user. Returns results as a sequence ordered by trigger time."""
    path: ListMyPipelinesRequestPath

# Operation: get_pipeline_by_number
class GetPipelineByNumberRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project slug identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name.")
    pipeline_number: Any = Field(default=..., validation_alias="pipeline-number", serialization_alias="pipeline-number", description="The sequential number assigned to the pipeline within the project, uniquely identifying it among all pipelines for that project.")
class GetPipelineByNumberRequest(StrictModel):
    """Retrieves a specific pipeline by its number within a given project. Returns full pipeline details including status, configuration, and metadata."""
    path: GetPipelineByNumberRequestPath

# Operation: list_project_schedules
class ListSchedulesForProjectRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")
class ListSchedulesForProjectRequest(StrictModel):
    """Retrieves all schedule triggers associated with GitHub OAuth or Bitbucket Cloud pipeline definitions for a given project. Note: schedules for GitHub App pipelines are not included and must be fetched via the List Pipeline Definition Triggers endpoint."""
    path: ListSchedulesForProjectRequestPath

# Operation: create_schedule
class CreateScheduleRequestPath(StrictModel):
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="The project identifier in the format `vcs-slug/org-name/repo-name`, where forward slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug with the organization ID and project ID in place of org and repo names.")
class CreateScheduleRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the schedule used to identify it within the project.")
    timetable: CreateScheduleBodyTimetableV0 | CreateScheduleBodyTimetableV1 | None = Field(default=None, description="The timetable definition specifying when the schedule should trigger, including frequency, days, and time settings.")
    attribution_actor: Literal["current", "system"] | None = Field(default=None, validation_alias="attribution-actor", serialization_alias="attribution-actor", description="Determines which actor's permissions are used when the scheduled pipeline runs — `current` uses the token owner's permissions, while `system` uses neutral system-level permissions.")
    parameters: dict[str, int | str | bool] | None = Field(default=None, description="Key-value pairs of pipeline parameters passed to each triggered pipeline run; must include at least a `branch` or `tag` key to specify the target ref.")
    description: str | None = Field(default=None, description="An optional human-readable description providing additional context about the schedule's purpose or behavior.")
class CreateScheduleRequest(StrictModel):
    """Creates a recurring pipeline schedule for a project and returns the created schedule. Available only for Bitbucket and GitHub OAuth organizations; for GitHub App or CircleCI project types, use the Create Trigger endpoint instead."""
    path: CreateScheduleRequestPath
    body: CreateScheduleRequestBody | None = None

# Operation: list_job_artifacts
class GetJobArtifactsRequestPath(StrictModel):
    job_number: Any = Field(default=..., validation_alias="job-number", serialization_alias="job-number", description="The unique number identifying the job within the project whose artifacts you want to retrieve.")
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Project slug uniquely identifying the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped.")
class GetJobArtifactsRequest(StrictModel):
    """Retrieves all artifacts produced by a specific job in a CircleCI project. Useful for accessing build outputs such as test reports, binaries, or logs."""
    path: GetJobArtifactsRequestPath

# Operation: list_job_tests
class GetTestsRequestPath(StrictModel):
    job_number: Any = Field(default=..., validation_alias="job-number", serialization_alias="job-number", description="The unique numeric identifier of the job whose test metadata you want to retrieve.")
    project_slug: str = Field(default=..., validation_alias="project-slug", serialization_alias="project-slug", description="Project slug identifying the target project in the format `vcs-slug/org-name/repo-name`, where URL-escaping of `/` is supported. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name.")
class GetTestsRequest(StrictModel):
    """Retrieves test metadata for a specific job within a project, including results and timing information. Returns no results if test data exceeds 250MB for the job."""
    path: GetTestsRequestPath

# Operation: get_schedule
class GetScheduleByIdRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="schedule-id", serialization_alias="schedule-id", description="The unique identifier of the schedule to retrieve, in UUID format.", json_schema_extra={'format': 'uuid'})
class GetScheduleByIdRequest(StrictModel):
    """Retrieves the details of a specific pipeline schedule by its unique ID. Only available for schedules associated with GitHub OAuth or Bitbucket Cloud pipeline definitions."""
    path: GetScheduleByIdRequestPath

# Operation: update_schedule
class UpdateScheduleRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="schedule-id", serialization_alias="schedule-id", description="The unique UUID identifying the schedule to update.", json_schema_extra={'format': 'uuid'})
class UpdateScheduleRequestBodyTimetable(StrictModel):
    per_hour: int | None = Field(default=None, validation_alias="per-hour", serialization_alias="per-hour", description="How many times the schedule triggers per hour; must be a whole number between 1 and 60. Mutually exclusive with hour-based scheduling fields.", json_schema_extra={'format': 'integer'})
    hours_of_day: list[Annotated[int, Field(json_schema_extra={'format': 'integer'})]] | None = Field(default=None, validation_alias="hours-of-day", serialization_alias="hours-of-day", description="List of hours within a day (0–23) during which the schedule triggers; order is not significant.")
    days_of_week: list[Literal["TUE", "SAT", "SUN", "MON", "THU", "WED", "FRI"]] | None = Field(default=None, validation_alias="days-of-week", serialization_alias="days-of-week", description="List of days of the week on which the schedule triggers (e.g., MON, TUE); mutually exclusive with days-of-month.")
    days_of_month: list[Annotated[int, Field(json_schema_extra={'format': 'integer'})]] | None = Field(default=None, validation_alias="days-of-month", serialization_alias="days-of-month", description="List of calendar days of the month (1–31) on which the schedule triggers; mutually exclusive with days-of-week.")
    months: list[Literal["MAR", "NOV", "DEC", "JUN", "MAY", "OCT", "FEB", "APR", "SEP", "AUG", "JAN", "JUL"]] | None = Field(default=None, validation_alias="months", serialization_alias="months", description="List of months in which the schedule triggers (e.g., JAN, FEB); order is not significant.")
class UpdateScheduleRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A human-readable description of the schedule's purpose or behavior.")
    name: str | None = Field(default=None, description="The display name of the schedule.")
    attribution_actor: Literal["current", "system"] | None = Field(default=None, validation_alias="attribution-actor", serialization_alias="attribution-actor", description="Determines whose permissions are used when the scheduled pipeline runs: 'current' uses the token owner's permissions, 'system' uses a neutral system actor.")
    parameters: dict[str, int | str | bool] | None = Field(default=None, description="Key-value pairs of pipeline parameters to pass when the schedule triggers; must include either a branch or tag key to specify the target ref.")
    timetable: UpdateScheduleRequestBodyTimetable | None = None
class UpdateScheduleRequest(StrictModel):
    """Updates an existing pipeline schedule by ID and returns the updated schedule. Only available for schedules associated with GitHub OAuth or Bitbucket Cloud pipeline definitions; use the Update Trigger endpoint for GitHub App pipeline definitions."""
    path: UpdateScheduleRequestPath
    body: UpdateScheduleRequestBody | None = None

# Operation: delete_schedule
class DeleteScheduleByIdRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="schedule-id", serialization_alias="schedule-id", description="The unique identifier of the schedule to delete, in UUID format.", json_schema_extra={'format': 'uuid'})
class DeleteScheduleByIdRequest(StrictModel):
    """Permanently deletes a pipeline schedule by its unique ID. Only available for schedules associated with GitHub OAuth or Bitbucket Cloud pipeline definitions."""
    path: DeleteScheduleByIdRequestPath

# Operation: get_user
class GetUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose information should be retrieved, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetUserRequest(StrictModel):
    """Retrieves profile and account information for a specific user. Use this to look up user details by their unique identifier."""
    path: GetUserRequestPath

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    scope_id: str = Field(default=..., validation_alias="scope-id", serialization_alias="scope-id", description="The unique identifier of the scope entity to filter webhooks by. Currently only project IDs are supported.", json_schema_extra={'format': 'uuid'})
    scope_type: Literal["project"] = Field(default=..., validation_alias="scope-type", serialization_alias="scope-type", description="The type of scope used to filter webhooks. Determines how the scope-id is interpreted; currently only 'project' is supported.")
class GetWebhooksRequest(StrictModel):
    """Retrieves all outbound webhooks associated with a given scope. Currently supports project-level scoping by providing a project ID."""
    query: GetWebhooksRequestQuery

# Operation: create_webhook
class CreateWebhookRequestBodyScope(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The UUID of the scope (e.g., a project) this webhook is associated with; currently only project IDs are supported.", json_schema_extra={'format': 'uuid'})
    type_: Literal["project"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of scope the provided ID refers to; currently only project-level scopes are supported.")
class CreateWebhookRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Human-readable name to identify the webhook.")
    events: list[Literal["workflow-completed", "job-completed"]] | None = Field(default=None, description="List of event types that will trigger this webhook; order is not significant and each item should be a valid event type string.")
    url: str | None = Field(default=None, description="The destination URL where webhook payloads will be delivered; must include the protocol prefix and only HTTPS is supported.")
    verify_tls: bool | None = Field(default=None, validation_alias="verify-tls", serialization_alias="verify-tls", description="When set to true, enforces strict TLS certificate verification on the destination URL before delivering the webhook payload.")
    signing_secret: str | None = Field(default=None, validation_alias="signing-secret", serialization_alias="signing-secret", description="A secret string used to generate an HMAC hash of the outgoing payload, which is passed as a header so the receiver can verify authenticity.")
    scope: CreateWebhookRequestBodyScope | None = None
class CreateWebhookRequest(StrictModel):
    """Creates an outbound webhook that listens for specified events and delivers payloads to a designated HTTPS URL. Supports TLS verification enforcement and HMAC payload signing for secure delivery."""
    body: CreateWebhookRequestBody | None = None

# Operation: get_webhook
class GetWebhookByIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhook-id", serialization_alias="webhook-id", description="The unique identifier of the outbound webhook to retrieve, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetWebhookByIdRequest(StrictModel):
    """Retrieves the configuration and details of a specific outbound webhook by its unique identifier. Use this to inspect webhook settings such as target URL, events, and status."""
    path: GetWebhookByIdRequestPath

# Operation: update_webhook
class UpdateWebhookRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhook-id", serialization_alias="webhook-id", description="The unique identifier of the webhook to update.", json_schema_extra={'format': 'uuid'})
class UpdateWebhookRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable label for the webhook, used to identify it in listings and logs.")
    events: list[Literal["workflow-completed", "job-completed"]] | None = Field(default=None, description="List of event types that will trigger this webhook; order is not significant and each item should be a valid event type string supported by the platform.")
    url: str | None = Field(default=None, description="The destination URL where webhook payloads will be delivered; must use the HTTPS protocol (HTTP is not supported).")
    signing_secret: str | None = Field(default=None, validation_alias="signing-secret", serialization_alias="signing-secret", description="A secret string used to generate an HMAC signature of the payload, which is passed as a request header so the receiver can verify the webhook's authenticity.")
    verify_tls: bool | None = Field(default=None, validation_alias="verify-tls", serialization_alias="verify-tls", description="When set to true, enforces strict TLS certificate validation on the destination URL; set to false only if delivering to an endpoint with a self-signed or otherwise unverifiable certificate.")
class UpdateWebhookRequest(StrictModel):
    """Updates the configuration of an existing outbound webhook, allowing changes to its name, target URL, triggered events, signing secret, and TLS verification behavior. Only fields provided in the request will be updated."""
    path: UpdateWebhookRequestPath
    body: UpdateWebhookRequestBody | None = None

# Operation: delete_webhook
class DeleteWebhookRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhook-id", serialization_alias="webhook-id", description="The unique identifier of the outbound webhook to delete, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteWebhookRequest(StrictModel):
    """Permanently deletes an outbound webhook, stopping all future event deliveries to its configured endpoint. This action cannot be undone."""
    path: DeleteWebhookRequestPath

# Operation: get_workflow
class GetWorkflowByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow to retrieve, in UUID format.", json_schema_extra={'format': 'uuid'})
class GetWorkflowByIdRequest(StrictModel):
    """Retrieves summary fields for a specific workflow by its unique identifier. Useful for checking workflow metadata such as name, status, and configuration details."""
    path: GetWorkflowByIdRequestPath

# Operation: approve_workflow_job
class ApprovePendingApprovalJobByIdRequestPath(StrictModel):
    approval_request_id: str = Field(default=..., description="The unique identifier of the pending approval job to approve, in UUID format.", json_schema_extra={'format': 'uuid'})
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow containing the pending approval job, in UUID format.", json_schema_extra={'format': 'uuid'})
class ApprovePendingApprovalJobByIdRequest(StrictModel):
    """Approves a pending approval job within a specified workflow, allowing the workflow to continue past the approval gate."""
    path: ApprovePendingApprovalJobByIdRequestPath

# Operation: cancel_workflow
class CancelWorkflowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow to cancel. Must correspond to an existing, currently running workflow.", json_schema_extra={'format': 'uuid'})
class CancelWorkflowRequest(StrictModel):
    """Cancels a currently running workflow, halting any further execution. Use this to stop a workflow that is in progress before it completes naturally."""
    path: CancelWorkflowRequestPath

# Operation: list_workflow_jobs
class ListWorkflowJobsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow whose jobs you want to retrieve.", json_schema_extra={'format': 'uuid'})
class ListWorkflowJobsRequest(StrictModel):
    """Retrieves the ordered sequence of jobs associated with a specific workflow. Use this to inspect all jobs belonging to a workflow and their current states."""
    path: ListWorkflowJobsRequestPath

# Operation: rerun_workflow
class RerunWorkflowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow to rerun.", json_schema_extra={'format': 'uuid'})
class RerunWorkflowRequestBody(StrictModel):
    enable_ssh: bool | None = Field(default=None, description="When true, enables SSH access for the triggering user on the newly rerun job. Requires the jobs parameter to be specified and is mutually exclusive with from_failed.")
    from_failed: bool | None = Field(default=None, description="When true, reruns the workflow starting from the first failed job rather than the beginning. Mutually exclusive with the jobs and sparse_tree parameters.")
    jobs: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(default=None, description="A list of specific job IDs (UUIDs) to rerun within the workflow. Order is not significant. Mutually exclusive with from_failed.")
    sparse_tree: bool | None = Field(default=None, description="When true, applies sparse tree optimization logic during the rerun, improving performance for workflows containing disconnected subgraphs. Requires the jobs parameter and is mutually exclusive with from_failed.")
class RerunWorkflowRequest(StrictModel):
    """Reruns an existing workflow by its ID, with options to rerun from the first failed job, target specific jobs, or apply sparse tree optimization for complex workflow graphs."""
    path: RerunWorkflowRequestPath
    body: RerunWorkflowRequestBody | None = None

# Operation: list_org_oidc_custom_claims
class GetOrgClaimsRequestPath(StrictModel):
    org_id: str = Field(default=..., validation_alias="orgID", serialization_alias="orgID", description="The unique identifier of the organization whose OIDC custom claims should be retrieved.", json_schema_extra={'format': 'uuid'})
class GetOrgClaimsRequest(StrictModel):
    """Retrieves the org-level custom claims configured for OIDC identity tokens. Use this to inspect which additional claims are included in tokens issued for the specified organization."""
    path: GetOrgClaimsRequestPath

# Operation: update_org_oidc_claims
class PatchOrgClaimsRequestPath(StrictModel):
    org_id: str = Field(default=..., validation_alias="orgID", serialization_alias="orgID", description="The unique identifier of the organization whose OIDC custom claims will be updated.", json_schema_extra={'format': 'uuid'})
class PatchOrgClaimsRequestBody(StrictModel):
    audience: list[str] | None = Field(default=None, description="List of intended recipients (audiences) for the OIDC token; order is not significant and each item should be a valid audience identifier string.")
    ttl: str | None = Field(default=None, description="Token time-to-live duration specifying how long the OIDC token remains valid; composed of one to seven time unit segments using milliseconds (ms), seconds (s), minutes (m), hours (h), days (d), or weeks (w).", pattern='^([0-9]+(ms|s|m|h|d|w)){1,7}$')
class PatchOrgClaimsRequest(StrictModel):
    """Creates or updates org-level custom claims on OIDC identity tokens for the specified organization. Use this to configure audience restrictions and token time-to-live settings."""
    path: PatchOrgClaimsRequestPath
    body: PatchOrgClaimsRequestBody | None = None

# Operation: delete_org_oidc_claims
class DeleteOrgClaimsRequestPath(StrictModel):
    org_id: str = Field(default=..., validation_alias="orgID", serialization_alias="orgID", description="The unique identifier of the organization whose custom OIDC claims will be deleted.", json_schema_extra={'format': 'uuid'})
class DeleteOrgClaimsRequestQuery(StrictModel):
    claims: str = Field(default=..., description="Comma-separated list of custom OIDC claim names to delete. Valid values are 'audience' and 'ttl'; multiple values may be combined in a single request.")
class DeleteOrgClaimsRequest(StrictModel):
    """Deletes one or more custom OIDC identity token claims configured at the organization level. Supports removing the 'audience' and/or 'ttl' claim overrides."""
    path: DeleteOrgClaimsRequestPath
    query: DeleteOrgClaimsRequestQuery

# Operation: get_project_oidc_claims
class GetProjectClaimsRequestPath(StrictModel):
    org_id: str = Field(default=..., validation_alias="orgID", serialization_alias="orgID", description="The unique identifier of the organization that owns the project.", json_schema_extra={'format': 'uuid'})
    project_id: str = Field(default=..., validation_alias="projectID", serialization_alias="projectID", description="The unique identifier of the project whose custom OIDC claims are being retrieved.", json_schema_extra={'format': 'uuid'})
class GetProjectClaimsRequest(StrictModel):
    """Retrieves the custom OIDC identity token claims configured at the project level. Use this to inspect which additional claims are included in tokens issued for a specific project."""
    path: GetProjectClaimsRequestPath

# Operation: update_project_oidc_claims
class PatchProjectClaimsRequestPath(StrictModel):
    org_id: str = Field(default=..., validation_alias="orgID", serialization_alias="orgID", description="Unique identifier of the organization that owns the project.", json_schema_extra={'format': 'uuid'})
    project_id: str = Field(default=..., validation_alias="projectID", serialization_alias="projectID", description="Unique identifier of the project whose OIDC custom claims are being created or updated.", json_schema_extra={'format': 'uuid'})
class PatchProjectClaimsRequestBody(StrictModel):
    audience: list[str] | None = Field(default=None, description="List of intended audiences for the OIDC token. Order is not significant; each item should be a valid audience string identifying a recipient that the token is intended for.")
    ttl: str | None = Field(default=None, description="Time-to-live duration for the OIDC token, specifying how long it remains valid. Accepts a compound duration string composed of up to seven unit segments in descending order, using units: weeks (w), days (d), hours (h), minutes (m), seconds (s), and milliseconds (ms).", pattern='^([0-9]+(ms|s|m|h|d|w)){1,7}$')
class PatchProjectClaimsRequest(StrictModel):
    """Creates or updates project-level custom claims on OIDC identity tokens for the specified project. Use this to configure audience restrictions and token time-to-live at the project scope."""
    path: PatchProjectClaimsRequestPath
    body: PatchProjectClaimsRequestBody | None = None

# Operation: delete_project_oidc_claims
class DeleteProjectClaimsRequestPath(StrictModel):
    org_id: str = Field(default=..., validation_alias="orgID", serialization_alias="orgID", description="Unique identifier of the organization that owns the project.", json_schema_extra={'format': 'uuid'})
    project_id: str = Field(default=..., validation_alias="projectID", serialization_alias="projectID", description="Unique identifier of the project whose OIDC custom claims will be deleted.", json_schema_extra={'format': 'uuid'})
class DeleteProjectClaimsRequestQuery(StrictModel):
    claims: str = Field(default=..., description="Comma-separated list of custom claim names to delete. Valid values are 'audience' and 'ttl'; multiple values may be combined in a single request.")
class DeleteProjectClaimsRequest(StrictModel):
    """Deletes one or more custom claims from the OIDC identity token configuration at the project level. Only the 'audience' and 'ttl' claims are eligible for deletion."""
    path: DeleteProjectClaimsRequestPath
    query: DeleteProjectClaimsRequestQuery

# Operation: list_decision_logs
class GetDecisionLogsRequestPath(StrictModel):
    owner_id: str = Field(default=..., validation_alias="ownerID", serialization_alias="ownerID", description="The unique identifier of the owner whose policy decision logs are being retrieved.")
    context: str = Field(default=..., description="The policy context scope under which decisions were evaluated and logged.")
class GetDecisionLogsRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Filters results to only include decisions that match the specified decision status (e.g., approved or rejected).")
    after: str | None = Field(default=None, description="Filters results to only include decisions made after this timestamp. Must be a valid ISO 8601 date-time string.", json_schema_extra={'format': 'date-time'})
    before: str | None = Field(default=None, description="Filters results to only include decisions made before this timestamp. Must be a valid ISO 8601 date-time string.", json_schema_extra={'format': 'date-time'})
    branch: str | None = Field(default=None, description="Filters results to only include decisions made on the specified branch name.")
    project_id: str | None = Field(default=None, description="Filters results to only include decisions associated with the specified project identifier.")
    build_number: str | None = Field(default=None, description="Filters results to only include decisions associated with the specified build number.")
    offset: int | None = Field(default=None, description="The number of records to skip before returning results, enabling pagination through large result sets.")
class GetDecisionLogsRequest(StrictModel):
    """Retrieves a paginated list of policy decision audit logs for the specified owner and context. Results can be filtered by status, date range, branch, project, or build number."""
    path: GetDecisionLogsRequestPath
    query: GetDecisionLogsRequestQuery | None = None

# Operation: get_decision_log
class GetDecisionLogRequestPath(StrictModel):
    owner_id: str = Field(default=..., validation_alias="ownerID", serialization_alias="ownerID", description="The unique identifier of the owner whose decision audit log is being retrieved.")
    context: str = Field(default=..., description="The context scope under which the decision was recorded, used to namespace or categorize decisions for the given owner.")
    decision_id: str = Field(default=..., validation_alias="decisionID", serialization_alias="decisionID", description="The unique identifier of the specific decision log entry to retrieve.")
class GetDecisionLogRequest(StrictModel):
    """Retrieves a specific decision audit log entry for a given owner and context. Use this to inspect the details and outcome of a previously recorded decision by its unique ID."""
    path: GetDecisionLogRequestPath

# Operation: get_decision_policy_bundle
class GetDecisionLogPolicyBundleRequestPath(StrictModel):
    owner_id: str = Field(default=..., validation_alias="ownerID", serialization_alias="ownerID", description="The unique identifier of the owner (organization or user) whose decision log is being queried.")
    context: str = Field(default=..., description="The policy context scope under which the decision was evaluated, used to namespace and organize policies.")
    decision_id: str = Field(default=..., validation_alias="decisionID", serialization_alias="decisionID", description="The unique identifier of the decision log entry for which the associated policy bundle should be retrieved.")
class GetDecisionLogPolicyBundleRequest(StrictModel):
    """Retrieves the policy bundle associated with a specific decision log entry. Useful for auditing which policies were evaluated at the time a given decision was made."""
    path: GetDecisionLogPolicyBundleRequestPath

# Operation: get_policy_bundle
class GetPolicyBundleRequestPath(StrictModel):
    owner_id: str = Field(default=..., validation_alias="ownerID", serialization_alias="ownerID", description="The unique identifier of the owner whose policy bundle is being retrieved.")
    context: str = Field(default=..., description="The context scope under which the policy bundle is organized, used to namespace or categorize policies for the specified owner.")
class GetPolicyBundleRequest(StrictModel):
    """Retrieves the complete policy bundle associated with a specific context for a given owner. Returns all policies grouped within that bundle for review or enforcement purposes."""
    path: GetPolicyBundleRequestPath

# Operation: list_contexts
class ListContextsRequestQuery(StrictModel):
    owner_id: str | None = Field(default=None, validation_alias="owner-id", serialization_alias="owner-id", description="The unique UUID of the organization that owns the contexts. Use this or owner-slug to identify the organization — find both in CircleCI web app under Organization Settings > Overview.", json_schema_extra={'format': 'uuid'})
    owner_slug: str | None = Field(default=None, validation_alias="owner-slug", serialization_alias="owner-slug", description="The slug identifier for the organization that owns the contexts. Use this or owner-id to identify the organization — find both in CircleCI web app under Organization Settings > Overview. Not supported on CircleCI server.")
    owner_type: Literal["account", "organization"] | None = Field(default=None, validation_alias="owner-type", serialization_alias="owner-type", description="Specifies whether the owner is an organization or an individual account. Defaults to 'organization'; use 'account' when working with CircleCI server.")
class ListContextsRequest(StrictModel):
    """Retrieves all contexts belonging to a specified organization or owner, enabling management of shared environment variables and secrets across projects."""
    query: ListContextsRequestQuery | None = None

# Operation: create_context
class CreateContextRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The human-readable name to assign to the new context, used to identify it within the organization.")
    owner: CreateContextBodyOwnerV0 | CreateContextBodyOwnerV1 | None = Field(default=None, description="The owner of the context, typically representing the organization or account under which the context will be created.")
class CreateContextRequest(StrictModel):
    """Creates a new named context within a specified organization, allowing you to group and manage related environment variables or secrets."""
    body: CreateContextRequestBody | None = None

# Operation: get_context
class GetContextRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context to retrieve, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetContextRequest(StrictModel):
    """Retrieves basic information about a specific context by its unique identifier. Use this to look up context details when you have a known context ID."""
    path: GetContextRequestPath

# Operation: delete_context
class DeleteContextRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context to delete. Deleting a context will also remove all environment variables stored within it.", json_schema_extra={'format': 'uuid'})
class DeleteContextRequest(StrictModel):
    """Permanently deletes a context and all of its associated environment variables by context ID. This action is irreversible."""
    path: DeleteContextRequestPath

# Operation: list_context_environment_variables
class ListEnvironmentVariablesFromContextRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context whose environment variables should be listed.", json_schema_extra={'format': 'uuid'})
class ListEnvironmentVariablesFromContextRequest(StrictModel):
    """Retrieves a list of environment variables defined within a specified context, returning metadata such as names but excluding their values for security."""
    path: ListEnvironmentVariablesFromContextRequestPath

# Operation: set_context_environment_variable
class AddEnvironmentVariableToContextRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context in which to create or update the environment variable.", json_schema_extra={'format': 'uuid'})
    env_var_name: str = Field(default=..., description="The name of the environment variable to create or update within the context.")
class AddEnvironmentVariableToContextRequestBody(StrictModel):
    value: str | None = Field(default=None, description="The value to assign to the environment variable; treated as a secret and not returned in responses.")
class AddEnvironmentVariableToContextRequest(StrictModel):
    """Creates or updates a named environment variable within a specified context. Returns metadata about the variable after the operation, excluding its value."""
    path: AddEnvironmentVariableToContextRequestPath
    body: AddEnvironmentVariableToContextRequestBody | None = None

# Operation: delete_context_environment_variable
class DeleteEnvironmentVariableFromContextRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context from which the environment variable will be deleted.", json_schema_extra={'format': 'uuid'})
    env_var_name: str = Field(default=..., description="The exact name of the environment variable to delete, matching the name as it was originally stored in the context.")
class DeleteEnvironmentVariableFromContextRequest(StrictModel):
    """Permanently removes a named environment variable from the specified context. This action cannot be undone and will immediately make the variable unavailable to pipelines using that context."""
    path: DeleteEnvironmentVariableFromContextRequestPath

# Operation: list_context_restrictions
class GetContextRestrictionsRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context whose restrictions should be retrieved, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetContextRestrictionsRequest(StrictModel):
    """Retrieves all project and expression restrictions associated with a specific context. Returns the complete list of restrictions currently applied to the given context."""
    path: GetContextRestrictionsRequestPath

# Operation: add_context_restriction
class CreateContextRestrictionRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context to which the restriction will be added.", json_schema_extra={'format': 'uuid'})
class CreateContextRestrictionRequestBody(StrictModel):
    restriction_type: Literal["project", "expression", "group"] | None = Field(default=None, description="The category of restriction to apply: 'project' limits access to a specific project, 'expression' applies a rule-based condition, and 'group' restricts access to a specific group.")
    restriction_value: str | None = Field(default=None, description="The value that defines the restriction rule, interpreted based on the restriction type: a project UUID for 'project' restrictions, or an expression rule string for 'expression' restrictions.")
class CreateContextRestrictionRequest(StrictModel):
    """Adds an access restriction to a context, limiting its use to specific projects, groups, or expression-based rules. Use this to control which projects or conditions are permitted to access the context."""
    path: CreateContextRestrictionRequestPath
    body: CreateContextRestrictionRequestBody | None = None

# Operation: delete_context_restriction
class DeleteContextRestrictionRequestPath(StrictModel):
    context_id: str = Field(default=..., description="The unique identifier of the context from which the restriction will be deleted.", json_schema_extra={'format': 'uuid'})
    restriction_id: str = Field(default=..., description="The unique identifier of the specific restriction to delete within the given context.")
class DeleteContextRestrictionRequest(StrictModel):
    """Permanently removes a specific restriction (project, expression, or group) from a context. This action cannot be undone and immediately revokes the associated access control rule."""
    path: DeleteContextRestrictionRequestPath

# Operation: get_project_settings
class GetProjectSettingsRequestPath(StrictModel):
    provider: Literal["github", "gh", "bitbucket", "bb", "circleci"] = Field(default=..., description="The version control or CI provider portion of the project slug, identifying which platform hosts the project.")
    organization: str = Field(default=..., description="The organization segment of the project slug, which may be an organization name or a unique organization ID depending on the account type.")
    project: str = Field(default=..., description="The project segment of the project slug, which may be a project name or a unique project ID depending on the account type.")
class GetProjectSettingsRequest(StrictModel):
    """Retrieves the advanced settings for a specified CircleCI project, returning each setting with a boolean indicating whether it is enabled or disabled."""
    path: GetProjectSettingsRequestPath

# Operation: update_project_settings
class PatchProjectSettingsRequestPath(StrictModel):
    provider: Literal["github", "gh", "bitbucket", "bb", "circleci"] = Field(default=..., description="The version control provider for the project, corresponding to the first segment of the project slug visible in Project Settings > Overview.")
    organization: str = Field(default=..., description="The organization identifier, corresponding to the second segment of the project slug visible in Project Settings > Overview. May be an org name or an org ID depending on the organization type.")
    project: str = Field(default=..., description="The project identifier, corresponding to the third segment of the project slug visible in Project Settings > Overview. May be a project name or a project ID depending on the organization type.")
class PatchProjectSettingsRequestBodyAdvanced(StrictModel):
    autocancel_builds: bool | None = Field(default=None, validation_alias="autocancel_builds", serialization_alias="autocancel_builds", description="When enabled, any running pipelines on a non-default branch are automatically cancelled when a new pipeline starts on that same branch.")
    build_fork_prs: bool | None = Field(default=None, validation_alias="build_fork_prs", serialization_alias="build_fork_prs", description="When enabled, CircleCI will run builds triggered by pull requests that originate from forked repositories.")
    build_prs_only: bool | None = Field(default=None, validation_alias="build_prs_only", serialization_alias="build_prs_only", description="When enabled, CircleCI will only build branches that have at least one associated open pull request.")
    disable_ssh: bool | None = Field(default=None, validation_alias="disable_ssh", serialization_alias="disable_ssh", description="When set to true, disables the ability to re-run jobs with SSH debugging access for this project.")
    forks_receive_secret_env_vars: bool | None = Field(default=None, validation_alias="forks_receive_secret_env_vars", serialization_alias="forks_receive_secret_env_vars", description="When enabled, builds triggered by forked pull requests will have access to this project's environment variables and secrets.")
    oss: bool | None = Field(default=None, validation_alias="oss", serialization_alias="oss", description="When enabled, marks the project as Free and Open Source, granting additional build credits and making builds publicly visible via the web UI and API.")
    set_github_status: bool | None = Field(default=None, validation_alias="set_github_status", serialization_alias="set_github_status", description="When enabled, CircleCI reports the build status of every pushed commit to GitHub's status API, with updates provided per job.")
    setup_workflows: bool | None = Field(default=None, validation_alias="setup_workflows", serialization_alias="setup_workflows", description="When enabled, allows pipeline configurations to be conditionally triggered from directories outside the primary `.circleci` parent directory using setup workflows.")
    write_settings_requires_admin: bool | None = Field(default=None, validation_alias="write_settings_requires_admin", serialization_alias="write_settings_requires_admin", description="When enabled, only organization administrators can update project settings; when disabled, any project member may update settings.")
    pr_only_branch_overrides: list[str] | None = Field(default=None, validation_alias="pr_only_branch_overrides", serialization_alias="pr_only_branch_overrides", description="A list of branch names that will always trigger a build regardless of the `build_prs_only` setting. The provided list completely overwrites the existing value; order is not significant.")
class PatchProjectSettingsRequestBody(StrictModel):
    """The setting(s) to update, including one or more fields in the JSON object. Note that `oss: true` will only be set on projects whose underlying repositories are actually open source."""
    advanced: PatchProjectSettingsRequestBodyAdvanced | None = None
class PatchProjectSettingsRequest(StrictModel):
    """Updates one or more advanced settings for a CircleCI project, such as build behavior, fork policies, SSH access, and GitHub status reporting. Only the settings fields provided in the request body will be modified."""
    path: PatchProjectSettingsRequestPath
    body: PatchProjectSettingsRequestBody | None = None

# Operation: list_organization_groups
class GetOrganizationGroupsRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization whose groups you want to retrieve.")
class GetOrganizationGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of group results to return per page. Use this to control pagination when an organization has many groups.")
class GetOrganizationGroupsRequest(StrictModel):
    """Retrieves all groups belonging to a specified organization. Supports pagination to control the number of results returned per page."""
    path: GetOrganizationGroupsRequestPath
    query: GetOrganizationGroupsRequestQuery | None = None

# Operation: create_group
class CreateOrganizationGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique opaque identifier of the organization under which the group will be created.")
class CreateOrganizationGroupRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new group, used to identify it within the organization.")
    description: str | None = Field(default=None, description="An optional human-readable description providing additional context or purpose for the group.")
class CreateOrganizationGroupRequest(StrictModel):
    """Creates a new group within a standalone organization, allowing members and resources to be organized under a named group. Only supported for standalone organizations."""
    path: CreateOrganizationGroupRequestPath
    body: CreateOrganizationGroupRequestBody

# Operation: get_group
class GetGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique opaque identifier of the organization that contains the group.")
    group_id: str = Field(default=..., description="The unique identifier of the group to retrieve, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetGroupRequest(StrictModel):
    """Retrieves details for a specific group within an organization. Currently only supported for standalone organizations."""
    path: GetGroupRequestPath

# Operation: delete_group
class DeleteGroupRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique opaque identifier of the organization that contains the group to be deleted.")
    group_id: str = Field(default=..., description="The unique UUID identifier of the group to delete. All members and associated role grants will be removed upon deletion.", json_schema_extra={'format': 'uuid'})
class DeleteGroupRequest(StrictModel):
    """Permanently deletes a group from a standalone organization, removing all its members and revoking any role grants associated with the group."""
    path: DeleteGroupRequestPath

# Operation: create_usage_export
class CreateUsageExportRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization for which the usage export will be generated.")
class CreateUsageExportRequestBody(StrictModel):
    start: str = Field(default=..., description="The start date and time (inclusive) of the export range in ISO 8601 format. Must be no more than one year in the past.", json_schema_extra={'format': 'date-time'})
    end: str = Field(default=..., description="The end date and time (inclusive) of the export range in ISO 8601 format. Must be no more than 31 days after the start date.", json_schema_extra={'format': 'date-time'})
    shared_org_ids: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(default=None, description="A list of additional organization IDs whose usage data should be included in the export, useful for aggregating usage across shared or linked organizations. Order is not significant.")
class CreateUsageExportRequest(StrictModel):
    """Submits a job to export usage data for an organization within a specified date range. The export covers up to 31 days of data and can optionally include usage from shared organizations."""
    path: CreateUsageExportRequestPath
    body: CreateUsageExportRequestBody

# Operation: get_usage_export_job
class GetUsageExportRequestPath(StrictModel):
    org_id: str = Field(default=..., description="The unique opaque identifier of the organization whose usage export job is being retrieved.")
    usage_export_job_id: str = Field(default=..., description="The unique UUID identifier of the usage export job to retrieve.", json_schema_extra={'format': 'uuid'})
class GetUsageExportRequest(StrictModel):
    """Retrieves the status and details of a specific usage export job for an organization, including download information once the export is complete."""
    path: GetUsageExportRequestPath

# Operation: trigger_pipeline_run
class TriggerPipelineRunRequestPath(StrictModel):
    provider: Literal["github", "gh", "bitbucket", "bb", "circleci"] = Field(default=..., description="The VCS or platform provider, corresponding to the first segment of the slash-separated project slug found in Project Settings > Overview.")
    organization: str = Field(default=..., description="The second segment of the slash-separated project slug, representing either a human-readable organization name or an opaque organization ID, as shown in Project Settings > Overview.")
    project: str = Field(default=..., description="The third segment of the slash-separated project slug, representing either a human-readable project name or an opaque project ID, as shown in Project Settings > Overview.")
class TriggerPipelineRunRequestBodyConfig(StrictModel):
    branch: str | None = Field(default=None, validation_alias="branch", serialization_alias="branch", description="The branch from which the pipeline config file should be fetched. Mutually exclusive with the config tag field. For GitHub PRs, use pull/<number>/head or pull/<number>/merge.")
    tag: str | None = Field(default=None, validation_alias="tag", serialization_alias="tag", description="The tag used to fetch the pipeline config file; the pipeline runs against the commit the tag points to. Mutually exclusive with the config branch field.")
class TriggerPipelineRunRequestBodyCheckout(StrictModel):
    branch: str | None = Field(default=None, validation_alias="branch", serialization_alias="branch", description="The branch to check out source code from during a checkout step. Mutually exclusive with the checkout tag field. For GitHub PRs, use pull/<number>/head or pull/<number>/merge.")
    tag: str | None = Field(default=None, validation_alias="tag", serialization_alias="tag", description="The tag used to check out source code during a checkout step; the pipeline runs against the commit the tag points to. Mutually exclusive with the checkout branch field.")
class TriggerPipelineRunRequestBody(StrictModel):
    definition_id: str | None = Field(default=None, description="The UUID of the pipeline definition to run, found in Project Settings > Pipelines. If omitted, the default pipeline definition is used.", json_schema_extra={'format': 'uuid'})
    parameters: dict[str, Any] | None = Field(default=None, description="A key-value map of pipeline parameter names to their values. Limited to 100 entries, with keys up to 128 characters and values up to 512 characters. Values may be strings, booleans, or integers.")
    config: TriggerPipelineRunRequestBodyConfig | None = None
    checkout: TriggerPipelineRunRequestBodyCheckout | None = None
class TriggerPipelineRunRequest(StrictModel):
    """Trigger a new pipeline run for a project using a specific pipeline definition. Supports GitHub, Bitbucket, and CircleCI integrations (GitLab not supported)."""
    path: TriggerPipelineRunRequestPath
    body: TriggerPipelineRunRequestBody | None = None

# Operation: list_pipeline_definitions
class ListPipelineDefinitionsRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the project whose pipeline definitions should be listed.")
class ListPipelineDefinitionsRequest(StrictModel):
    """Retrieves all pipeline definitions associated with a specified project. Pipeline definitions describe the structure and configuration of pipelines available within the project."""
    path: ListPipelineDefinitionsRequestPath

# Operation: create_pipeline_definition
class CreatePipelineDefinitionRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project under which the pipeline definition will be created.")
class CreatePipelineDefinitionRequestBodyCheckoutSourceRepo(StrictModel):
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="The external identifier for the repository as defined by the version control provider, used to link the pipeline definition to the correct repository.")
class CreatePipelineDefinitionRequestBodyCheckoutSource(StrictModel):
    provider: Literal["github_app"] | None = Field(default=None, validation_alias="provider", serialization_alias="provider", description="The version control integration provider for the pipeline definition's configuration source. Currently only 'github_app' is supported.")
    repo: CreatePipelineDefinitionRequestBodyCheckoutSourceRepo | None = None
class CreatePipelineDefinitionRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the pipeline definition to distinguish it within the project.")
    description: str | None = Field(default=None, description="An optional description providing additional context or details about the purpose of this pipeline definition.")
    config_source: CreatePipelineDefinitionBodyConfigSourceV0 | CreatePipelineDefinitionBodyConfigSourceV1 | None = Field(default=None, description="The configuration source object that specifies where and how the pipeline configuration is sourced, including the provider and repository details.")
    checkout_source: CreatePipelineDefinitionRequestBodyCheckoutSource | None = None
class CreatePipelineDefinitionRequest(StrictModel):
    """Creates a new pipeline definition for a specified project, allowing you to define the configuration source and metadata. Currently only supported for projects using the GitHub App integration provider."""
    path: CreatePipelineDefinitionRequestPath
    body: CreatePipelineDefinitionRequestBody | None = None

# Operation: get_pipeline_definition
class GetPipelineDefinitionRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project containing the pipeline definition.")
    pipeline_definition_id: str = Field(default=..., description="The unique opaque identifier of the pipeline definition to retrieve.")
class GetPipelineDefinitionRequest(StrictModel):
    """Retrieves detailed configuration metadata for a specific pipeline definition within a project. Supported for pipeline definitions using GitHub App, GitHub OAuth, Bitbucket DC, Bitbucket OAuth, or GitLab as the config source provider."""
    path: GetPipelineDefinitionRequestPath

# Operation: update_pipeline_definition
class UpdatePipelineDefinitionRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project containing the pipeline definition to update.")
    pipeline_definition_id: str = Field(default=..., description="The unique opaque identifier of the pipeline definition to update.")
class UpdatePipelineDefinitionRequestBodyConfigSource(StrictModel):
    file_path: str | None = Field(default=None, validation_alias="file_path", serialization_alias="file_path", description="The relative path within the repository to the CircleCI YAML configuration file that this pipeline definition should use.")
class UpdatePipelineDefinitionRequestBodyCheckoutSourceRepo(StrictModel):
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="The repository identifier as defined by the version control provider, used to associate the pipeline definition with a specific external repository.")
class UpdatePipelineDefinitionRequestBodyCheckoutSource(StrictModel):
    provider: str | None = Field(default=None, validation_alias="provider", serialization_alias="provider", description="The version control integration provider for the pipeline definition's config source. Currently only 'github_app' is supported.")
    repo: UpdatePipelineDefinitionRequestBodyCheckoutSourceRepo | None = None
class UpdatePipelineDefinitionRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable display name for the pipeline definition.")
    description: str | None = Field(default=None, description="A brief explanation of the pipeline definition's purpose or behavior.")
    config_source: UpdatePipelineDefinitionRequestBodyConfigSource | None = None
    checkout_source: UpdatePipelineDefinitionRequestBodyCheckoutSource | None = None
class UpdatePipelineDefinitionRequest(StrictModel):
    """Updates an existing pipeline definition for a project, allowing changes to its name, description, config file path, or version control source settings. Currently supported only for pipeline definitions using GitHub App or Bitbucket Data Center as the config source provider."""
    path: UpdatePipelineDefinitionRequestPath
    body: UpdatePipelineDefinitionRequestBody | None = None

# Operation: delete_pipeline_definition
class DeletePipelineDefinitionRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project containing the pipeline definition to delete.")
    pipeline_definition_id: str = Field(default=..., description="The unique opaque identifier of the pipeline definition to delete.")
class DeletePipelineDefinitionRequest(StrictModel):
    """Permanently deletes a pipeline definition from a project. Currently only supported for pipeline definitions using GitHub App or Bitbucket Data Center as the config source provider."""
    path: DeletePipelineDefinitionRequestPath

# Operation: list_pipeline_definition_triggers
class ListPipelineDefinitionTriggersRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the project containing the pipeline definition.")
    pipeline_definition_id: str = Field(default=..., description="The unique identifier of the pipeline definition whose triggers you want to list.")
class ListPipelineDefinitionTriggersRequest(StrictModel):
    """Retrieves all triggers configured for a specific pipeline definition within a project. Supported only for pipeline definitions using GitHub OAuth, GitHub App, or Bitbucket Data Center as the config source provider."""
    path: ListPipelineDefinitionTriggersRequestPath

# Operation: create_pipeline_trigger
class CreateTriggerRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project in which the pipeline definition resides.")
    pipeline_definition_id: str = Field(default=..., description="The unique opaque identifier of the pipeline definition for which the trigger will be created.")
class CreateTriggerRequestBodyEventSourceRepo(StrictModel):
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="The repository identifier as defined by the version control provider, used to associate the trigger with a specific repository.")
class CreateTriggerRequestBodyEventSourceWebhook(StrictModel):
    sender: str | None = Field(default=None, validation_alias="sender", serialization_alias="sender", description="Identifies the entity sending the webhook event; only applicable when the provider is `webhook`.")
class CreateTriggerRequestBodyEventSource(StrictModel):
    provider: str | None = Field(default=None, validation_alias="provider", serialization_alias="provider", description="The version control or integration provider for the trigger's event source. Accepted values are `github_app`, `github_oauth`, and `webhook`.")
    repo: CreateTriggerRequestBodyEventSourceRepo | None = None
    webhook: CreateTriggerRequestBodyEventSourceWebhook | None = None
class CreateTriggerRequestBody(StrictModel):
    event_preset: Literal["all-pushes", "only-tags", "default-branch-pushes", "only-build-prs", "only-open-prs", "only-labeled-prs", "only-merged-prs", "only-ready-for-review-prs", "only-branch-delete", "only-build-pushes-to-non-draft-prs", "only-merged-or-closed-prs", "pr-comment-equals-run-ci", "non-draft-pr-opened", "pushes-to-merge-queues"] | None = Field(default=None, description="Specifies which category of events will activate this trigger using a named preset. Only applicable when `event_source.provider` is `github_app`; choose from the supported preset values to control which push, PR, or branch events fire the trigger.")
    checkout_ref: str | None = Field(default=None, description="The Git ref used to check out source code for pipeline runs created by this trigger. Required when the provider is `webhook`; for `github_app`, only provide this if the event source repository differs from the pipeline definition's checkout source repository.")
    config_ref: str | None = Field(default=None, description="The Git ref used to fetch the pipeline configuration for runs created by this trigger. Required when the provider is `webhook`; for `github_app`, only provide this if the event source repository differs from the pipeline definition's config source repository.")
    event_name: str | None = Field(default=None, description="The name of the event that activates this trigger. Should only be set when the provider is `webhook`.")
    disabled: bool | None = Field(default=None, description="When set to `true`, the trigger is created in a disabled state and will not fire until explicitly enabled. Not supported for pipeline definitions using `github_oauth` as the config source provider.")
    event_source: CreateTriggerRequestBodyEventSource | None = None
class CreateTriggerRequest(StrictModel):
    """Creates a trigger for a specified pipeline definition, enabling automated pipeline runs in response to events. Currently supported only for pipeline definitions using GitHub OAuth or GitHub App as the config source provider."""
    path: CreateTriggerRequestPath
    body: CreateTriggerRequestBody | None = None

# Operation: get_trigger
class GetTriggerRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project that owns the trigger.")
    trigger_id: str = Field(default=..., description="The unique opaque identifier of the trigger to retrieve.")
class GetTriggerRequest(StrictModel):
    """Retrieves detailed configuration and metadata for a specific project trigger. Currently supported for triggers with GitHub OAuth, GitHub App, Bitbucket Data Center, or webhook event sources."""
    path: GetTriggerRequestPath

# Operation: update_trigger
class UpdateTriggerRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project that owns the trigger.")
    trigger_id: str = Field(default=..., description="The unique opaque identifier of the trigger to update.")
class UpdateTriggerRequestBodyEventSourceWebhook(StrictModel):
    sender: str | None = Field(default=None, validation_alias="sender", serialization_alias="sender", description="The identity of the entity sending the webhook payload. Only settable for triggers where the provider is `webhook`.")
class UpdateTriggerRequestBodyEventSource(StrictModel):
    webhook: UpdateTriggerRequestBodyEventSourceWebhook | None = None
class UpdateTriggerRequestBody(StrictModel):
    event_preset: Literal["all-pushes", "only-tags", "default-branch-pushes", "only-build-prs", "only-open-prs", "only-labeled-prs", "only-merged-prs", "only-ready-for-review-prs", "only-branch-delete", "only-build-pushes-to-non-draft-prs", "only-merged-or-closed-prs", "pr-comment-equals-run-ci", "non-draft-pr-opened", "pushes-to-merge-queues"] | None = Field(default=None, description="A predefined event filtering preset that determines which GitHub events activate this trigger. Only applicable when the trigger's provider is `github_app`.")
    checkout_ref: str | None = Field(default=None, description="The Git ref (branch, tag, or commit SHA) used to check out source code when pipeline runs are created from this trigger.")
    config_ref: str | None = Field(default=None, description="The Git ref used to fetch the pipeline configuration file when pipeline runs are created from this trigger.")
    event_name: str | None = Field(default=None, description="The name of the event that activates this trigger. Only settable for triggers where the provider is `webhook`.")
    disabled: bool | None = Field(default=None, description="Whether the trigger is disabled and should not create pipeline runs when events occur. Only settable for triggers where the provider is `github_oauth`, `github_app`, or `webhook`.")
    event_source: UpdateTriggerRequestBodyEventSource | None = None
class UpdateTriggerRequest(StrictModel):
    """Update configuration for an existing pipeline trigger on a project. Currently supported for triggers with a provider of `github_oauth`, `github_app`, `bitbucket_dc`, or `webhook`."""
    path: UpdateTriggerRequestPath
    body: UpdateTriggerRequestBody | None = None

# Operation: delete_trigger
class DeleteTriggerRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project from which the trigger will be deleted.")
    trigger_id: str = Field(default=..., description="The unique opaque identifier of the trigger to be deleted.")
class DeleteTriggerRequest(StrictModel):
    """Permanently deletes a trigger from the specified project. Supported only for triggers with an event source provider of GitHub OAuth, GitHub App, Bitbucket Data Center, or webhook."""
    path: DeleteTriggerRequestPath

# Operation: rollback_project
class RollbackProjectRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique opaque identifier of the project in which the rollback will be performed.")
class RollbackProjectRequestBody(StrictModel):
    component_name: str = Field(default=..., description="The name of the component within the project to be rolled back.")
    current_version: str = Field(default=..., description="The version of the component currently deployed, which will be replaced by the rollback.")
    environment_name: str = Field(default=..., description="The name of the environment in which the rollback will be executed (e.g., production, staging).")
    namespace: str | None = Field(default=None, description="The Kubernetes or deployment namespace where the component resides. Defaults to the project's default namespace if not specified.")
    parameters: dict[str, Any] | None = Field(default=None, description="A key-value map of additional parameters to pass to the rollback pipeline, allowing customization of pipeline behavior beyond standard inputs.")
    reason: str | None = Field(default=None, description="A human-readable explanation for why the rollback is being performed, useful for audit trails and incident tracking.")
    target_version: str = Field(default=..., description="The version to roll back to, which should be a previously stable and deployed version of the component.")
class RollbackProjectRequest(StrictModel):
    """Rolls back a specific component in a project to a target version by triggering a rollback pipeline. Use this to recover from a bad deployment by reverting a component from its current version to a previously stable version."""
    path: RollbackProjectRequestPath
    body: RollbackProjectRequestBody

# Operation: list_environments
class ListEnvironmentsRequestQuery(StrictModel):
    org_id: str = Field(default=..., validation_alias="org-id", serialization_alias="org-id", description="The unique identifier of the organization whose environments you want to list, provided as a UUID.", json_schema_extra={'format': 'uuid'})
    page_size: int = Field(default=..., validation_alias="page-size", serialization_alias="page-size", description="The maximum number of environments to return per page. Use this alongside pagination controls to iterate through large result sets.")
class ListEnvironmentsRequest(StrictModel):
    """Retrieves a paginated list of deployment environments belonging to a specified organization. Use this to browse available environments for deployment targeting or configuration management."""
    query: ListEnvironmentsRequestQuery

# Operation: get_environment
class GetEnvironmentRequestPath(StrictModel):
    environment_id: str = Field(default=..., description="The unique UUID identifying the deployment environment to retrieve.", json_schema_extra={'format': 'uuid'})
class GetEnvironmentRequest(StrictModel):
    """Retrieves detailed information about a specific deployment environment by its unique identifier. Use this to inspect environment configuration, status, or metadata for a known environment."""
    path: GetEnvironmentRequestPath

# Operation: list_components
class ListComponentsRequestQuery(StrictModel):
    org_id: str = Field(default=..., validation_alias="org-id", serialization_alias="org-id", description="The unique identifier of the organization whose components will be listed.", json_schema_extra={'format': 'uuid'})
    project_id: str | None = Field(default=None, validation_alias="project-id", serialization_alias="project-id", description="The unique identifier of a project used to filter components to only those belonging to that project.", json_schema_extra={'format': 'uuid'})
    page_size: int = Field(default=..., validation_alias="page-size", serialization_alias="page-size", description="The maximum number of components to return in a single page of results. Use in combination with pagination tokens to iterate through all components.")
class ListComponentsRequest(StrictModel):
    """Retrieves a paginated list of deployed components belonging to a specified organization. Optionally filter results by project to narrow the scope of returned components."""
    query: ListComponentsRequestQuery

# Operation: get_component
class GetComponentRequestPath(StrictModel):
    component_id: str = Field(default=..., description="The unique opaque identifier of the component to retrieve, as returned when the component was created or listed.")
class GetComponentRequest(StrictModel):
    """Retrieves the full details of a deployed component by its unique identifier. Use this to inspect configuration, status, or metadata for a specific component."""
    path: GetComponentRequestPath

# Operation: list_component_versions
class ListComponentVersionsRequestPath(StrictModel):
    component_id: str = Field(default=..., description="The unique identifier of the component whose versions you want to retrieve.")
class ListComponentVersionsRequestQuery(StrictModel):
    environment_id: str | None = Field(default=None, validation_alias="environment-id", serialization_alias="environment-id", description="The unique identifier of an environment to filter component versions by, returning only versions relevant to that environment. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class ListComponentVersionsRequest(StrictModel):
    """Retrieves all available versions for a specified component. Optionally filter results by environment to see versions relevant to a particular deployment context."""
    path: ListComponentVersionsRequestPath
    query: ListComponentVersionsRequestQuery | None = None

# Operation: list_otel_exporters
class ListOtelExportersRequestQuery(StrictModel):
    org_id: str = Field(default=..., validation_alias="org-id", serialization_alias="org-id", description="The unique identifier of the organization whose OTLP exporter configurations should be retrieved, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class ListOtelExportersRequest(StrictModel):
    """Retrieves all OpenTelemetry (OTLP) exporter configurations associated with the specified organization. This is an experimental feature and may be subject to change."""
    query: ListOtelExportersRequestQuery

# Operation: create_otlp_exporter
class CreateOtelExporterRequestBody(StrictModel):
    org_id: str = Field(default=..., description="The unique identifier of the organization for which the OTLP exporter will be created.", json_schema_extra={'format': 'uuid'})
    endpoint: str = Field(default=..., description="The destination OTLP collector endpoint, specified as hostname and port only — omit any scheme prefix such as https:// or grpc://.")
    protocol: Literal["grpc", "http"] = Field(default=..., description="The transport protocol used when exporting telemetry data; choose grpc for gRPC transport or http for HTTP/protobuf transport.")
    insecure: bool | None = Field(default=None, description="When set to true, the exporter connects to the endpoint without TLS encryption; defaults to false for secure connections.")
    headers: dict[str, str] | None = Field(default=None, description="A key-value map of additional HTTP or gRPC headers to include with every export request, useful for authentication tokens or routing metadata.")
class CreateOtelExporterRequest(StrictModel):
    """Creates a new OTLP exporter configuration for a specified organization, defining how telemetry spans are exported to an external observability backend. This is an experimental feature supporting both gRPC and HTTP transport protocols."""
    body: CreateOtelExporterRequestBody

# Operation: delete_otlp_exporter
class DeleteOtelExporterRequestPath(StrictModel):
    otel_exporter_id: str = Field(default=..., description="The unique identifier of the OTLP exporter configuration to delete.", json_schema_extra={'format': 'uuid'})
class DeleteOtelExporterRequest(StrictModel):
    """Permanently deletes an OTLP exporter configuration by its unique identifier. This is an experimental feature and the behavior may change in future releases."""
    path: DeleteOtelExporterRequestPath

# ============================================================================
# Component Models
# ============================================================================

class CreateContextBodyOwnerV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the owner of the context. This is the organization ID. Specify either owner/organization ID or the owner/organization slug. Find the organization ID and slug in the CircleCI web app (Organization Settings > Overview). Owner/organization slug is not supported for CircleCI server.", json_schema_extra={'format': 'uuid'})
    type_: Literal["account", "organization"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the owner. Defaults to \"organization\". Use \"account\" if you are using CircleCI server.")

class CreateContextBodyOwnerV1(StrictModel):
    slug: str = Field(..., description="A string that represents an organization. This is the organization slug. Specify either this or organization/owner ID. Find the organization ID and slug in the CircleCI web app (Organization Settings > Overview). Owner/organization slug is not supported for CircleCI server.")
    type_: Literal["organization"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of owner. Defaults to \"organization\". Accounts are only used as context owners in server and must be specified by an id instead of a slug.")

class CreatePipelineDefinitionBodyConfigSourceV0Repo(StrictModel):
    external_id: str = Field(..., description="External identifier for the repository, as defined by the respective version control provider.")

class CreatePipelineDefinitionBodyConfigSourceV0(StrictModel):
    """Config source for external providers (repo required)"""
    provider: Literal["github_app"] = Field(..., description="The integration provider for this resource. Currently `github_app` is the only supported external provider.")
    repo: CreatePipelineDefinitionBodyConfigSourceV0Repo
    file_path: str = Field(..., description="Path to CircleCI config YAML file to use for this pipeline definition.")

class CreatePipelineDefinitionBodyConfigSourceV1(StrictModel):
    """Config source for CircleCI provider (no repo required)"""
    provider: Literal["circleci"] = Field(..., description="The integration provider for this resource.")
    file_path: str = Field(..., description="Path to CircleCI config YAML file to use for this pipeline definition.")

class CreatePipelineDefinitionRequestCheckoutSourceRepo(StrictModel):
    external_id: str = Field(..., description="External identifier for the repository, as defined by the respective version control provider.")

class CreatePipelineDefinitionRequestCheckoutSource(StrictModel):
    """The resource to be used when running the `checkout` command."""
    provider: Literal["github_app"] = Field(..., description="The integration provider for this resource. Currently `github_app` is the only supported value.")
    repo: CreatePipelineDefinitionRequestCheckoutSourceRepo

class CreatePipelineDefinitionRequestConfigSourceV0Repo(StrictModel):
    external_id: str = Field(..., description="External identifier for the repository, as defined by the respective version control provider.")

class CreatePipelineDefinitionRequestConfigSourceV0(StrictModel):
    """Config source for external providers (repo required)"""
    provider: Literal["github_app"] = Field(..., description="The integration provider for this resource. Currently `github_app` is the only supported external provider.")
    repo: CreatePipelineDefinitionRequestConfigSourceV0Repo
    file_path: str = Field(..., description="Path to CircleCI config YAML file to use for this pipeline definition.")

class CreatePipelineDefinitionRequestConfigSourceV1(StrictModel):
    """Config source for CircleCI provider (no repo required)"""
    provider: Literal["circleci"] = Field(..., description="The integration provider for this resource.")
    file_path: str = Field(..., description="Path to CircleCI config YAML file to use for this pipeline definition.")

class CreateScheduleBodyTimetableV0(PermissiveModel):
    per_hour: int = Field(..., validation_alias="per-hour", serialization_alias="per-hour", description="Number of times a schedule triggers per hour, value must be between 1 and 60", json_schema_extra={'format': 'integer'})
    hours_of_day: list[Annotated[int, Field(json_schema_extra={'format': 'integer'})]] = Field(..., validation_alias="hours-of-day", serialization_alias="hours-of-day", description="Hours in a day in which the schedule triggers.")
    days_of_week: list[Literal["TUE", "SAT", "SUN", "MON", "THU", "WED", "FRI"]] = Field(..., validation_alias="days-of-week", serialization_alias="days-of-week", description="Days in a week in which the schedule triggers.")
    days_of_month: list[Annotated[int, Field(json_schema_extra={'format': 'integer'})]] | None = Field(None, validation_alias="days-of-month", serialization_alias="days-of-month", description="Days in a month in which the schedule triggers. This is mutually exclusive with days in a week.")
    months: list[Literal["MAR", "NOV", "DEC", "JUN", "MAY", "OCT", "FEB", "APR", "SEP", "AUG", "JAN", "JUL"]] | None = Field(None, description="Months in which the schedule triggers.")

class CreateScheduleBodyTimetableV1(PermissiveModel):
    per_hour: int = Field(..., validation_alias="per-hour", serialization_alias="per-hour", description="Number of times a schedule triggers per hour, value must be between 1 and 60", json_schema_extra={'format': 'integer'})
    hours_of_day: list[Annotated[int, Field(json_schema_extra={'format': 'integer'})]] = Field(..., validation_alias="hours-of-day", serialization_alias="hours-of-day", description="Hours in a day in which the schedule triggers.")
    days_of_month: list[Annotated[int, Field(json_schema_extra={'format': 'integer'})]] = Field(..., validation_alias="days-of-month", serialization_alias="days-of-month", description="Days in a month in which the schedule triggers. This is mutually exclusive with days in a week.")
    days_of_week: list[Literal["TUE", "SAT", "SUN", "MON", "THU", "WED", "FRI"]] | None = Field(None, validation_alias="days-of-week", serialization_alias="days-of-week", description="Days in a week in which the schedule triggers.")
    months: list[Literal["MAR", "NOV", "DEC", "JUN", "MAY", "OCT", "FEB", "APR", "SEP", "AUG", "JAN", "JUL"]] | None = Field(None, description="Months in which the schedule triggers.")

class CreateTriggerRequestEventSourceRepo(StrictModel):
    """Information pertaining to the repository used as a source of events for this trigger, if applicable."""
    external_id: str = Field(..., description="External identifier for the repository, as defined by the respective version control provider.")

class CreateTriggerRequestEventSourceWebhook(StrictModel):
    """Information pertaining to the custom webhook being used as a source of events for this trigger, if applicable."""
    sender: str | None = Field(None, description="The sender of the webhook.")

class CreateTriggerRequestEventSource(StrictModel):
    """The source of events to use for this trigger. The `repo` object must be specified when `provider` is `github_app` or `github_oauth`, and the `webhook` object may only be specified when `provider` is `webhook`."""
    provider: str = Field(..., description="The integration provider for this resource. Currently `github_app`, `github_oauth`, and `webhook` are the only supported values.")
    repo: CreateTriggerRequestEventSourceRepo | None = Field(None, description="Information pertaining to the repository used as a source of events for this trigger, if applicable.")
    webhook: CreateTriggerRequestEventSourceWebhook | None = Field(None, description="Information pertaining to the custom webhook being used as a source of events for this trigger, if applicable.")

class TriggerEventSourceRepo(StrictModel):
    """Information pertaining to the repository used as a source of events for this trigger, if applicable."""
    full_name: str | None = Field(None, description="The fully-qualified name of the repository.")
    external_id: str | None = Field(None, description="External identifier for the repository, as defined by the respective version control provider.")

class TriggerEventSourceWebhook(StrictModel):
    """Information pertaining to the custom webhook used as a source of events for this trigger, if applicable."""
    url: str | None = Field(None, description="The URL to use when triggering this webhook.")
    sender: str | None = Field(None, description="The name of the webhook sender..")

class TriggerEventSource(StrictModel):
    """The source of events to use for this trigger. Will contain either a `repo` or `webhook` object depending on the `provider`. (The `github_app` and `github_oauth` providers imply a `repo` and `webhook` implies a `webhook`.)"""
    provider: str | None = Field(None, description="The integration provider for this resource. Currently `github_app`, `github_oauth`, and `webhook` are the only supported values.")
    repo: TriggerEventSourceRepo | None = Field(None, description="Information pertaining to the repository used as a source of events for this trigger, if applicable.")
    webhook: TriggerEventSourceWebhook | None = Field(None, description="Information pertaining to the custom webhook used as a source of events for this trigger, if applicable.")

class Trigger(StrictModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique ID of the trigger.", json_schema_extra={'format': 'uuid'})
    event_name: str | None = Field(None, description="The name of the event that will trigger the pipeline.")
    created_at: str | None = Field(None, description="The date and time the trigger was created.", json_schema_extra={'format': 'date-time'})
    event_source: TriggerEventSource | None = Field(None, description="The source of events to use for this trigger. Will contain either a `repo` or `webhook` object depending on the `provider`. (The `github_app` and `github_oauth` providers imply a `repo` and `webhook` implies a `webhook`.)")
    event_preset: Literal["all-pushes", "only-tags", "default-branch-pushes", "only-build-prs", "only-open-prs", "only-labeled-prs", "only-merged-prs", "only-ready-for-review-prs", "only-branch-delete", "only-build-pushes-to-non-draft-prs", "only-merged-or-closed-prs", "pr-comment-equals-run-ci", "non-draft-pr-opened", "pushes-to-merge-queues"] | None = None
    checkout_ref: str | None = Field(None, description="The ref to use when checking out code for pipeline runs created from this trigger. If empty, the ref provided in the trigger event is used.")
    config_ref: str | None = Field(None, description="The ref to use when fetching config for pipeline runs created from this trigger. If empty, the ref provided in the trigger event is used.")
    disabled: bool | None = Field(None, description="Whether the trigger is disabled. Not supported for pipeline definitions where `config_source.provider` is `github_oauth`.")

class TriggerPipelineRequestCheckout(StrictModel):
    branch: str | None = Field(None, description="The branch that should be used to check out code on a checkout step.\nNote that branch and tag are mutually exclusive.\nTo trigger a pipeline for a PR by number use pull/<number>/head for the PR ref or pull/<number>/merge for the merge ref (GitHub only)\n")
    tag: str | None = Field(None, description="The tag that should be used to check out code on a checkout step.\nThe commit that this tag points to is used for the pipeline. Note that branch and tag are mutually exclusive.\n")

class TriggerPipelineRequestConfig(StrictModel):
    branch: str | None = Field(None, description="The branch that should be used to fetch the config file.\nNote that branch and tag are mutually exclusive.\nTo trigger a pipeline for a PR by number use pull/<number>/head for the PR ref or pull/<number>/merge for the merge ref (GitHub only)\n")
    tag: str | None = Field(None, description="The tag that should be used to fetch the config file.\nThe commit that this tag points to is used for the pipeline.\nNote that branch and tag are mutually exclusive.\n")

class UpdatePipelineDefinitionRequestCheckoutSourceRepo(StrictModel):
    external_id: str | None = Field(None, description="External identifier for the repository, as defined by the respective version control provider.")

class UpdatePipelineDefinitionRequestCheckoutSource(StrictModel):
    """The resource to be used when running the `checkout` command."""
    provider: str | None = Field(None, description="The integration provider for this resource. Currently `github_app` is the only supported value.")
    repo: UpdatePipelineDefinitionRequestCheckoutSourceRepo | None = None

class UpdatePipelineDefinitionRequestConfigSource(StrictModel):
    """The resource that stores the CircleCI config YAML used for this pipeline definition."""
    file_path: str | None = Field(None, description="Path to CircleCI config YAML file to use for this pipeline definition.")

class UpdateTriggerRequestEventSourceWebhook(StrictModel):
    sender: str | None = Field(None, description="The sender of the webhook. This can only be set for triggers where `provider` is `webhook`.")

class UpdateTriggerRequestEventSource(StrictModel):
    webhook: UpdateTriggerRequestEventSourceWebhook | None = None


# Rebuild models to resolve forward references (required for circular refs)
CreateContextBodyOwnerV0.model_rebuild()
CreateContextBodyOwnerV1.model_rebuild()
CreatePipelineDefinitionBodyConfigSourceV0.model_rebuild()
CreatePipelineDefinitionBodyConfigSourceV0Repo.model_rebuild()
CreatePipelineDefinitionBodyConfigSourceV1.model_rebuild()
CreatePipelineDefinitionRequestCheckoutSource.model_rebuild()
CreatePipelineDefinitionRequestCheckoutSourceRepo.model_rebuild()
CreatePipelineDefinitionRequestConfigSourceV0.model_rebuild()
CreatePipelineDefinitionRequestConfigSourceV0Repo.model_rebuild()
CreatePipelineDefinitionRequestConfigSourceV1.model_rebuild()
CreateScheduleBodyTimetableV0.model_rebuild()
CreateScheduleBodyTimetableV1.model_rebuild()
CreateTriggerRequestEventSource.model_rebuild()
CreateTriggerRequestEventSourceRepo.model_rebuild()
CreateTriggerRequestEventSourceWebhook.model_rebuild()
Trigger.model_rebuild()
TriggerEventSource.model_rebuild()
TriggerEventSourceRepo.model_rebuild()
TriggerEventSourceWebhook.model_rebuild()
TriggerPipelineRequestCheckout.model_rebuild()
TriggerPipelineRequestConfig.model_rebuild()
UpdatePipelineDefinitionRequestCheckoutSource.model_rebuild()
UpdatePipelineDefinitionRequestCheckoutSourceRepo.model_rebuild()
UpdatePipelineDefinitionRequestConfigSource.model_rebuild()
UpdateTriggerRequestEventSource.model_rebuild()
UpdateTriggerRequestEventSourceWebhook.model_rebuild()

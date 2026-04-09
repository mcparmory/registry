"""
Codacy MCP Server - Pydantic Models

Generated: 2026-04-09 17:17:58 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AddEnterpriseTokenRequest",
    "AddOrganizationRequest",
    "AddPatternFeedbackRequest",
    "AddPeopleToOrganizationRequest",
    "AddRepositoryRequest",
    "AdminSearchRequest",
    "AnalyzeDastTargetRequest",
    "ApplyCodingStandardToRepositoriesRequest",
    "ApplyGatePolicyToRepositoriesRequest",
    "ApplyProviderSettingsRequest",
    "BulkIgnoreIssuesRequest",
    "BypassPullRequestAnalysisRequest",
    "ChangeOrganizationPlanRequest",
    "CheckIfUserCanLeaveRequest",
    "CheckSubmodulesRequest",
    "CodingStandardToolPatternsOverviewRequest",
    "ConfigureToolRequest",
    "CreateBadgePullRequest",
    "CreateCodingStandardPresetRequest",
    "CreateCodingStandardRequest",
    "CreateComplianceStandardRequest",
    "CreateDastTargetRequest",
    "CreateGatePolicyRequest",
    "CreateJiraTicketRequest",
    "CreatePostCommitHookRequest",
    "CreateRepositoryApiTokenRequest",
    "CreateUserApiTokenRequest",
    "DeclineRequestsToJoinOrganizationRequest",
    "DeleteCodingStandardRequest",
    "DeleteDastTargetRequest",
    "DeleteDormantAccountsRequest",
    "DeleteEnterpriseTokenRequest",
    "DeleteGatePolicyRequest",
    "DeleteImageSbomsRequest",
    "DeleteImageTagRequest",
    "DeleteIntegrationRequest",
    "DeleteJiraIntegrationRequest",
    "DeleteOrganizationJoinRequest",
    "DeleteOrganizationRequest",
    "DeleteRepositoryApiTokenRequest",
    "DeleteRepositoryRequest",
    "DeleteSecurityManagerRequest",
    "DeleteSubscriptionRequest",
    "DeleteUserApiTokenRequest",
    "DuplicateCodingStandardRequest",
    "FollowAddedRepositoryRequest",
    "GetAiRiskCheckListRequest",
    "GetAvailableJiraProjectsRequest",
    "GetBranchRequiredChecksRequest",
    "GetBuildServerAnalysisSettingRequest",
    "GetCodingStandardRequest",
    "GetCommitDeltaStatisticsRequest",
    "GetCommitDetailsByCommitIdRequest",
    "GetCommitDiffRequest",
    "GetCommitQualitySettingsRequest",
    "GetCommitRequest",
    "GetCoverageReportRequest",
    "GetDastTargetsRequest",
    "GetDiffBetweenCommitsRequest",
    "GetEnterpriseRequest",
    "GetFileClonesRequest",
    "GetFileContentRequest",
    "GetFileCoverageRequest",
    "GetFileIssuesRequest",
    "GetFileWithAnalysisRequest",
    "GetFirstAnalysisOverviewRequest",
    "GetGatePolicyRequest",
    "GetIssueRequest",
    "GetJiraIntegrationRequest",
    "GetJiraProjectIssueFieldsRequest",
    "GetJiraProjectIssueTypesRequest",
    "GetJiraTicketsRequest",
    "GetOrganizationByInstallationIdRequest",
    "GetOrganizationRequest",
    "GetPatternRequest",
    "GetProviderSettingsRequest",
    "GetPullRequestCommitsRequest",
    "GetPullRequestCoverageReportsRequest",
    "GetPullRequestDiffRequest",
    "GetPullRequestQuickfixesPatchRequest",
    "GetQuickfixesPatchRequest",
    "GetReportSecurityItemsRequest",
    "GetRepositoryIntegrationsSettingsRequest",
    "GetRepositoryLanguagesRequest",
    "GetRepositoryPublicSshKeyRequest",
    "GetRepositoryPullRequest",
    "GetRepositoryPullRequestCoverageRequest",
    "GetRepositoryPullRequestFilesCoverageRequest",
    "GetRepositoryRequest",
    "GetRepositorySbomPresignedUrlRequest",
    "GetRepositoryToolPatternRequest",
    "GetRepositoryWithAnalysisRequest",
    "GetSecurityItemRequest",
    "GetSegmentsKeysRequest",
    "GetSegmentsKeysWithIdsRequest",
    "GetSegmentsRequest",
    "GetSegmentsSyncStatusRequest",
    "GetSlackIntegrationRequest",
    "GetUserApiTokensRequest",
    "GetUserOrganizationRequest",
    "GitProviderAppPermissionsRequest",
    "HasQuickfixSuggestionsRequest",
    "IgnoreFalsePositiveRequest",
    "IgnoreSecurityItemRequest",
    "InitiateMetricsForOrganizationRequest",
    "IssuesOverviewRequest",
    "JoinOrganizationRequest",
    "ListAuditLogsForOrganizationRequest",
    "ListCategoryOverviewsRequest",
    "ListCodingStandardPatternsRequest",
    "ListCodingStandardRepositoriesRequest",
    "ListCodingStandardsRequest",
    "ListCodingStandardToolsRequest",
    "ListCommitAnalysisStatsRequest",
    "ListCommitClonesRequest",
    "ListCommitCoverageReportsRequest",
    "ListCommitDeltaIssuesRequest",
    "ListCommitFilesRequest",
    "ListCommitLogsRequest",
    "ListCoverageReportsRequest",
    "ListDastReportsRequest",
    "ListEnterpriseOrganizationsRequest",
    "ListEnterpriseSeatsCsvRequest",
    "ListEnterpriseSeatsRequest",
    "ListEnterprisesRequest",
    "ListFilesRequest",
    "ListGatePoliciesRequest",
    "ListIgnoredFilesRequest",
    "ListImageTagsRequest",
    "ListOrganizationImagesRequest",
    "ListOrganizationJoinRequestsRequest",
    "ListOrganizationPullRequestsRequest",
    "ListOrganizationRepositoriesRequest",
    "ListOrganizationRepositoriesWithAnalysisRequest",
    "ListOrganizationsRequest",
    "ListPatternsRequest",
    "ListPeopleFromOrganizationCsvRequest",
    "ListPeopleFromOrganizationRequest",
    "ListProviderIntegrationsRequest",
    "ListPullRequestClonesRequest",
    "ListPullRequestFilesRequest",
    "ListPullRequestIssuesRequest",
    "ListPullRequestLogsRequest",
    "ListRepositoriesFollowingGatePolicyRequest",
    "ListRepositoryApiTokensRequest",
    "ListRepositoryBranchesRequest",
    "ListRepositoryCommitsRequest",
    "ListRepositoryPullRequestsRequest",
    "ListRepositoryToolConflictsRequest",
    "ListRepositoryToolPatternConflictsRequest",
    "ListRepositoryToolPatternsRequest",
    "ListRepositoryToolsRequest",
    "ListSecurityCategoriesRequest",
    "ListSecurityManagersRequest",
    "ListSecurityRepositoriesRequest",
    "ListToolsRequest",
    "ListUserIntegrationsRequest",
    "ListUserOrganizationsRequest",
    "OrganizationBillingAddCardRequest",
    "OrganizationBillingCardRequest",
    "OrganizationBillingEstimationRequest",
    "OrganizationDetailedBillingRequest",
    "PatchRepositoryLanguageResponseSettingsRequest",
    "PatchUserRequest",
    "PeopleSuggestionsForOrganizationRequest",
    "PeopleSuggestionsForRepositoryRequest",
    "PostSecurityManagerRequest",
    "PromoteDraftCodingStandardRequest",
    "ReadyMetricsForEnterpriseRequest",
    "ReadyMetricsForOrganizationRequest",
    "ReanalyzeCommitByIdRequest",
    "ReanalyzeCoverageRequest",
    "RefreshProviderRepositoryIntegrationRequest",
    "RegenerateRepositorySshKeyRequest",
    "RegenerateUserSshKeyRequest",
    "RemovePeopleFromOrganizationRequest",
    "ResetCommitsQualitySettingsRequest",
    "ResetRepositoryQualitySettingsRequest",
    "RetrieveGroupedValuesForPeriodForEnterpriseRequest",
    "RetrieveGroupedValuesForPeriodRequest",
    "RetrieveLatestMetricGroupedValuesForEnterpriseRequest",
    "RetrieveLatestMetricGroupedValuesRequest",
    "RetrieveLatestMetricValueForEnterpriseRequest",
    "RetrieveLatestMetricValueRequest",
    "RetrieveOrganizationOnboardingProgressRequest",
    "RetrieveTimerangeMetricValuesForEnterpriseRequest",
    "RetrieveTimerangeMetricValuesRequest",
    "RetrieveValueForPeriodForEnterpriseRequest",
    "RetrieveValueForPeriodRequest",
    "SearchOrganizationRepositoriesWithAnalysisRequest",
    "SearchReportSecurityItemsRequest",
    "SearchRepositoriesOfSbomDependencyRequest",
    "SearchRepositoryIgnoredIssuesRequest",
    "SearchRepositoryIssuesRequest",
    "SearchSbomDependenciesRequest",
    "SearchSbomRepositoriesRequest",
    "SearchSecurityDashboardCategoriesRequest",
    "SearchSecurityDashboardHistoryRequest",
    "SearchSecurityDashboardRepositoriesRequest",
    "SearchSecurityDashboardRequest",
    "SearchSecurityItemsRequest",
    "SetCodacyDefaultRequest",
    "SetDefaultCodingStandardRequest",
    "SetDefaultGatePolicyRequest",
    "SetRepositoryBranchAsDefaultRequest",
    "SyncOrganizationNameRequest",
    "SyncRepositoryWithProviderRequest",
    "ToolPatternsOverviewRequest",
    "TriggerPullRequestAiReviewRequest",
    "UnfollowRepositoryRequest",
    "UnignoreSecurityItemRequest",
    "UnlinkRepositoryJiraTicketRequest",
    "UpdateCodingStandardPatternsRequest",
    "UpdateCodingStandardToolConfigurationRequest",
    "UpdateFileStateRequest",
    "UpdateGatePolicyRequest",
    "UpdateIssueStateRequest",
    "UpdateJoinModeRequest",
    "UpdateOrganizationDetailedBillingRequest",
    "UpdateProviderSettingsRequest",
    "UpdateRepositoryBranchConfigurationRequest",
    "UpdateRepositoryIntegrationsSettingsRequest",
    "UpdateRepositoryQualitySettingsRequest",
    "UpdateRepositoryToolPatternsRequest",
    "UploadDastReportRequest",
    "UploadImageSbomRequest",
    "ConfigurePattern",
    "CreateJiraTicketElement",
    "DimensionsFilter",
    "RepositoryLanguageUpdate",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_organization_repositories_with_analysis
class ListOrganizationRepositoriesWithAnalysisRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier code for the desired provider.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider.")
class ListOrganizationRepositoriesWithAnalysisRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per page. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned repositories to those whose names contain the provided string.")
    segments: str | None = Field(default=None, description="Restricts results to repositories belonging to the specified segments, provided as a comma-separated list of numeric segment identifiers.")
class ListOrganizationRepositoriesWithAnalysisRequest(StrictModel):
    """Retrieves repositories belonging to a specified organization on a Git provider, including their analysis metadata. Supports filtering by name or segment, with pagination cursor that must be URL-encoded for Bitbucket."""
    path: ListOrganizationRepositoriesWithAnalysisRequestPath
    query: ListOrganizationRepositoriesWithAnalysisRequestQuery | None = None

# Operation: search_organization_repositories
class SearchOrganizationRepositoriesWithAnalysisRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target platform (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider. Must match the exact organization identifier used by the provider.")
class SearchOrganizationRepositoriesWithAnalysisRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class SearchOrganizationRepositoriesWithAnalysisRequestBody(StrictModel):
    """Search query body"""
    names: list[str] | None = Field(default=None, description="Filter results to only the specified repository names. Each item should be a repository name string; order does not affect results.")
class SearchOrganizationRepositoriesWithAnalysisRequest(StrictModel):
    """Search repositories within an organization on a specified Git provider, returning results enriched with analysis information. Supports filtering by repository name and paginated results."""
    path: SearchOrganizationRepositoriesWithAnalysisRequestPath
    query: SearchOrganizationRepositoriesWithAnalysisRequestQuery | None = None
    body: SearchOrganizationRepositoriesWithAnalysisRequestBody | None = None

# Operation: get_repository_analysis
class GetRepositoryWithAnalysisRequestPath(StrictModel):
    provider: str = Field(default=..., description="The short identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class GetRepositoryWithAnalysisRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The name of a branch enabled on Codacy for this repository. If omitted, the main branch configured in Codacy repository settings is used. Use the listRepositoryBranches endpoint to retrieve valid branch names.")
class GetRepositoryWithAnalysisRequest(StrictModel):
    """Retrieves detailed analysis information for a specific repository on Codacy, including code quality metrics and insights for the authenticated user. Optionally scoped to a specific enabled branch, defaulting to the repository's main branch."""
    path: GetRepositoryWithAnalysisRequestPath
    query: GetRepositoryWithAnalysisRequestQuery | None = None

# Operation: list_repository_tools
class ListRepositoryToolsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ListRepositoryToolsRequest(StrictModel):
    """Retrieves the analysis tool settings configured for a specific repository, including which tools are enabled and their configurations. No authentication is required when accessing public repositories."""
    path: ListRepositoryToolsRequestPath

# Operation: list_tool_conflicts
class ListRepositoryToolConflictsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class ListRepositoryToolConflictsRequest(StrictModel):
    """Retrieves a list of analysis tools that have configuration conflicts in the specified repository. Useful for diagnosing tool setup issues that may affect code analysis results."""
    path: ListRepositoryToolConflictsRequestPath

# Operation: configure_repository_tool
class ConfigureToolRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the specified organization on the Git provider.")
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="UUID uniquely identifying the analysis tool to configure.")
class ConfigureToolRequestBody(StrictModel):
    enabled: bool | None = Field(default=None, description="Set to true to enable the tool for analysis or false to disable it entirely for this repository.")
    use_configuration_file: bool | None = Field(default=None, validation_alias="useConfigurationFile", serialization_alias="useConfigurationFile", description="Set to true to have the tool read its settings from a configuration file in the repository, or false to use Codacy-managed settings.")
    patterns: list[ConfigurePattern] | None = Field(default=None, description="List of pattern objects to enable or disable for this tool; each item should specify the pattern identifier and its desired enabled state. Order is not significant.")
class ConfigureToolRequest(StrictModel):
    """Enable or disable an analysis tool and its patterns for a specific repository. Changes are applied immediately without checking whether the repository is linked to a coding standard."""
    path: ConfigureToolRequestPath
    body: ConfigureToolRequestBody | None = None

# Operation: list_repository_tool_patterns
class ListRepositoryToolPatternsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID uniquely identifying the analysis tool whose patterns should be retrieved.")
class ListRepositoryToolPatternsRequestQuery(StrictModel):
    languages: str | None = Field(default=None, description="Comma-separated list of programming language names to restrict results to patterns applicable to those languages.")
    categories: str | None = Field(default=None, description="Comma-separated list of pattern categories to filter by. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance.")
    severity_levels: str | None = Field(default=None, validation_alias="severityLevels", serialization_alias="severityLevels", description="Comma-separated list of severity levels to filter by. Valid values are Error, High, Warning, and Info.")
    tags: str | None = Field(default=None, description="Comma-separated list of pattern tags to filter results by, such as framework or technology tags.")
    search: str | None = Field(default=None, description="A search string used to filter patterns by matching against pattern names or descriptions.")
    enabled: bool | None = Field(default=None, description="When set to true, returns only enabled patterns; when set to false, returns only disabled patterns. Omit to return all patterns regardless of enabled status.")
    recommended: bool | None = Field(default=None, description="When set to true, returns only recommended patterns; when set to false, returns only non-recommended patterns. Omit to return all patterns regardless of recommended status.")
    sort: str | None = Field(default=None, description="The field by which to sort the returned patterns. Valid values are category, recommended, and severity.")
    direction: str | None = Field(default=None, description="The direction in which to sort results, either ascending (asc) or descending (desc).")
    limit: int | None = Field(default=None, description="Maximum number of patterns to return in a single response, between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListRepositoryToolPatternsRequest(StrictModel):
    """Retrieves the code pattern configurations for a specific analysis tool applied to a repository. Returns standard organization-level settings if applied, otherwise falls back to repository-specific settings."""
    path: ListRepositoryToolPatternsRequestPath
    query: ListRepositoryToolPatternsRequestQuery | None = None

# Operation: bulk_update_repository_tool_patterns
class UpdateRepositoryToolPatternsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the organization on the Git provider.")
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="UUID that uniquely identifies the tool whose patterns will be updated.")
class UpdateRepositoryToolPatternsRequestQuery(StrictModel):
    languages: str | None = Field(default=None, description="Comma-separated list of programming language names to restrict the update to patterns applicable to those languages only.")
    categories: str | None = Field(default=None, description="Comma-separated list of pattern categories to restrict the update. Valid values are `Security`, `ErrorProne`, `CodeStyle`, `Compatibility`, `UnusedCode`, `Complexity`, `Comprehensibility`, `Documentation`, `BestPractice`, and `Performance`.")
    severity_levels: str | None = Field(default=None, validation_alias="severityLevels", serialization_alias="severityLevels", description="Comma-separated list of severity levels to restrict the update. Valid values are `Error`, `High`, `Warning`, and `Info`.")
    tags: str | None = Field(default=None, description="Comma-separated list of pattern tags to restrict the update to patterns that carry any of the specified tags.")
    search: str | None = Field(default=None, description="Free-text search string used to filter patterns by name or description before applying the bulk update.")
    recommended: bool | None = Field(default=None, description="When set to `true`, restricts the update to recommended patterns only; when set to `false`, restricts it to non-recommended patterns only. Omit to include patterns regardless of recommended status.")
class UpdateRepositoryToolPatternsRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="Set to `true` to enable all matched code patterns, or `false` to disable them.")
class UpdateRepositoryToolPatternsRequest(StrictModel):
    """Bulk enables or disables code patterns for a specific tool in a repository. Use optional filters to target a subset of patterns by language, category, severity, tags, or search term; omit all filters to apply the change to every pattern for the tool."""
    path: UpdateRepositoryToolPatternsRequestPath
    query: UpdateRepositoryToolPatternsRequestQuery | None = None
    body: UpdateRepositoryToolPatternsRequestBody

# Operation: get_repository_tool_pattern_config
class GetRepositoryToolPatternRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID uniquely identifying the analysis tool whose pattern configuration is being retrieved.")
    pattern_id: str = Field(default=..., validation_alias="patternId", serialization_alias="patternId", description="The identifier for the specific pattern within the tool whose configuration is being retrieved.")
class GetRepositoryToolPatternRequest(StrictModel):
    """Retrieves the pattern configuration for a specific tool pattern applied to a repository. Returns the organization-level standard configuration if one is applied, otherwise falls back to the repository-level settings."""
    path: GetRepositoryToolPatternRequestPath

# Operation: get_tool_patterns_overview
class ToolPatternsOverviewRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider for the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization or account that owns the repository on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the specified organization on the Git provider.")
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="UUID uniquely identifying the analysis tool whose pattern overview is being retrieved.")
class ToolPatternsOverviewRequestQuery(StrictModel):
    languages: str | None = Field(default=None, description="Comma-separated list of programming language names to restrict the overview to patterns applicable to those languages.")
    categories: str | None = Field(default=None, description="Comma-separated list of pattern categories to include in the overview. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance.")
    severity_levels: str | None = Field(default=None, validation_alias="severityLevels", serialization_alias="severityLevels", description="Comma-separated list of severity levels to filter patterns by. Valid values are Error, High, Warning, and Info.")
    tags: str | None = Field(default=None, description="Comma-separated list of tags to filter patterns by, allowing narrowing results to patterns associated with specific frameworks or topics.")
    search: str | None = Field(default=None, description="Search string used to filter patterns by matching against pattern names or descriptions.")
    enabled: bool | None = Field(default=None, description="When set to true, returns only enabled patterns; when set to false, returns only disabled patterns. Omit to return patterns regardless of enabled status.")
    recommended: bool | None = Field(default=None, description="When set to true, returns only patterns marked as recommended; when set to false, returns only non-recommended patterns. Omit to return patterns regardless of recommended status.")
class ToolPatternsOverviewRequest(StrictModel):
    """Retrieves an overview of code patterns for a specific analysis tool in a repository, showing counts and summaries by category, severity, and status. Uses standard settings if applied, otherwise falls back to repository-level tool configuration."""
    path: ToolPatternsOverviewRequestPath
    query: ToolPatternsOverviewRequestQuery | None = None

# Operation: list_tool_pattern_conflicts
class ListRepositoryToolPatternConflictsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID uniquely identifying the analysis tool whose pattern conflicts should be retrieved.")
class ListRepositoryToolPatternConflictsRequest(StrictModel):
    """Retrieves a list of patterns for a specific tool that conflict with the repository's configured Coding Standards, helping identify rule inconsistencies that may affect code analysis."""
    path: ListRepositoryToolPatternConflictsRequestPath

# Operation: get_repository_analysis_progress
class GetFirstAnalysisOverviewRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization that owns the repository on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the organization on the Git provider.")
class GetFirstAnalysisOverviewRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The branch to check analysis progress for; must be a branch enabled in Codacy repository settings. Defaults to the main branch configured in Codacy if omitted.")
class GetFirstAnalysisOverviewRequest(StrictModel):
    """Retrieves the analysis progress overview for a specific repository on Codacy, indicating how far along the initial analysis has advanced. No authentication is required when accessing public repositories."""
    path: GetFirstAnalysisOverviewRequestPath
    query: GetFirstAnalysisOverviewRequestQuery | None = None

# Operation: list_pull_requests
class ListRepositoryPullRequestsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ListRepositoryPullRequestsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of pull requests to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned pull requests to those whose names or metadata contain the provided string.")
    include_not_analyzed: bool | None = Field(default=None, validation_alias="includeNotAnalyzed", serialization_alias="includeNotAnalyzed", description="When set to true, includes pull requests that have not yet been analyzed by Codacy alongside analyzed ones.")
class ListRepositoryPullRequestsRequest(StrictModel):
    """Retrieves a list of pull requests for a specified repository, supporting sorting by last-updated, impact, or merged status. No authentication is required for public repositories."""
    path: ListRepositoryPullRequestsRequestPath
    query: ListRepositoryPullRequestsRequestQuery | None = None

# Operation: get_pull_request
class GetRepositoryPullRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique numeric identifier of the pull request within the repository, as assigned by the Git provider.", json_schema_extra={'format': 'int32'})
class GetRepositoryPullRequest(StrictModel):
    """Retrieves detailed analysis data for a specific pull request in a repository. No authentication is required when accessing public repositories."""
    path: GetRepositoryPullRequestPath

# Operation: get_pull_request_coverage
class GetRepositoryPullRequestCoverageRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The numeric identifier of the pull request for which to retrieve coverage data.", json_schema_extra={'format': 'int32'})
class GetRepositoryPullRequestCoverageRequest(StrictModel):
    """Retrieves code coverage information for a specific pull request in a repository. No authentication is required when accessing public repositories."""
    path: GetRepositoryPullRequestCoverageRequestPath

# Operation: list_pull_request_file_coverage
class GetRepositoryPullRequestFilesCoverageRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The numeric identifier of the pull request for which file coverage data is being requested.", json_schema_extra={'format': 'int32'})
class GetRepositoryPullRequestFilesCoverageRequest(StrictModel):
    """Retrieves per-file code coverage information for a specific pull request in a repository. No authentication is required when accessing public repositories."""
    path: GetRepositoryPullRequestFilesCoverageRequestPath

# Operation: reanalyze_pull_request_coverage
class ReanalyzeCoverageRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository. Use the provider's abbreviated identifier.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The numeric identifier of the pull request whose coverage report should be reanalyzed.", json_schema_extra={'format': 'int32'})
class ReanalyzeCoverageRequest(StrictModel):
    """Triggers a reanalysis of the latest coverage report uploaded for a specific pull request. Useful when coverage data needs to be reprocessed without uploading a new report."""
    path: ReanalyzeCoverageRequestPath

# Operation: list_pull_request_commits
class GetPullRequestCommitsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository. Use the short identifier for the target platform (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique number identifying the pull request within the repository, as assigned by the Git provider.", json_schema_extra={'format': 'int32'})
class GetPullRequestCommitsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of commit results to return in a single response. Accepts values between 1 and 100; defaults to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetPullRequestCommitsRequest(StrictModel):
    """Retrieves analysis results for all commits within a specified pull request, including code quality and issue data per commit. Results are paginated and scoped to a repository on a supported Git provider."""
    path: GetPullRequestCommitsRequestPath
    query: GetPullRequestCommitsRequestQuery | None = None

# Operation: bypass_pull_request_analysis
class BypassPullRequestAnalysisRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The numeric identifier of the pull request whose analysis status should be bypassed.", json_schema_extra={'format': 'int32'})
class BypassPullRequestAnalysisRequest(StrictModel):
    """Bypasses the analysis status check for a specific pull request, allowing it to proceed regardless of analysis results. Useful when overriding blocking analysis gates in CI/CD workflows."""
    path: BypassPullRequestAnalysisRequestPath

# Operation: trigger_pull_request_ai_review
class TriggerPullRequestAiReviewRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider for the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The numeric identifier of the pull request to be reviewed, as assigned by the Git provider.", json_schema_extra={'format': 'int32'})
class TriggerPullRequestAiReviewRequest(StrictModel):
    """Triggers an AI-powered code review for a specific pull request in a repository. Initiates automated analysis and feedback generation for the pull request's changes."""
    path: TriggerPullRequestAiReviewRequestPath

# Operation: list_pull_request_coverage_reports
class GetPullRequestCoverageReportsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique number identifying the pull request within the repository.", json_schema_extra={'format': 'int32'})
class GetPullRequestCoverageReportsRequest(StrictModel):
    """Retrieves all coverage reports uploaded for both the common ancestor commit and the head commit of a pull request branch. Useful for comparing coverage changes introduced by the pull request."""
    path: GetPullRequestCoverageReportsRequestPath

# Operation: list_pull_request_issues
class ListPullRequestIssuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique number identifying the pull request within the repository.", json_schema_extra={'format': 'int32'})
class ListPullRequestIssuesRequestQuery(StrictModel):
    status: Literal["all", "new", "fixed"] | None = Field(default=None, description="Filters issues by their status relative to the pull request. Use 'new' for issues introduced, 'fixed' for issues resolved, or 'all' to return both.")
    only_potential: bool | None = Field(default=None, validation_alias="onlyPotential", serialization_alias="onlyPotential", description="When set to true, restricts results to potential issues only, which are lower-confidence findings that may require additional review.")
    limit: int | None = Field(default=None, description="Maximum number of issues to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListPullRequestIssuesRequest(StrictModel):
    """Retrieves the list of issues found in a specific pull request for a given repository. Use the status filter to narrow results to new, fixed, or all issues, and optionally surface only potential issues."""
    path: ListPullRequestIssuesRequestPath
    query: ListPullRequestIssuesRequestQuery | None = None

# Operation: list_pull_request_clones
class ListPullRequestClonesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The numeric identifier of the pull request for which duplicate code blocks should be retrieved.", json_schema_extra={'format': 'int32'})
class ListPullRequestClonesRequestQuery(StrictModel):
    status: Literal["all", "new", "fixed"] | None = Field(default=None, description="Filters returned clones by their status relative to the pull request: 'new' for clones introduced, 'fixed' for clones resolved, or 'all' for every detected clone regardless of status.")
    only_potential: bool | None = Field(default=None, validation_alias="onlyPotential", serialization_alias="onlyPotential", description="When set to true, restricts results to only potential (lower-confidence) duplicate code blocks rather than confirmed clones.")
    limit: int | None = Field(default=None, description="Maximum number of clone results to return in a single response, between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListPullRequestClonesRequest(StrictModel):
    """Retrieves duplicate code blocks (clones) detected in a specific pull request for a repository. Use the status filter to narrow results to new, fixed, or all duplicate occurrences."""
    path: ListPullRequestClonesRequestPath
    query: ListPullRequestClonesRequestQuery | None = None

# Operation: list_commit_clones
class ListCommitClonesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The UUID or full SHA hash identifying the specific commit to analyze for duplicate code blocks.")
class ListCommitClonesRequestQuery(StrictModel):
    status: Literal["all", "new", "fixed"] | None = Field(default=None, description="Filters duplicate code blocks by their status relative to the commit: all returns every clone, new returns only newly introduced clones, and fixed returns only clones resolved in this commit.")
    only_potential: bool | None = Field(default=None, validation_alias="onlyPotential", serialization_alias="onlyPotential", description="When set to true, restricts results to only potential duplicate code issues, excluding confirmed clones.")
    limit: int | None = Field(default=None, description="Maximum number of duplicate code block results to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListCommitClonesRequest(StrictModel):
    """Retrieves duplicate code blocks (clones) detected in a specific commit for a repository. Use the status parameter to filter results by new, fixed, or all duplicate occurrences."""
    path: ListCommitClonesRequestPath
    query: ListCommitClonesRequestQuery | None = None

# Operation: list_pull_request_logs
class ListPullRequestLogsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique number identifying the pull request within the repository, as assigned by the Git provider.", json_schema_extra={'format': 'int32'})
class ListPullRequestLogsRequest(StrictModel):
    """Retrieves analysis logs for a specific pull request in a repository, useful for diagnosing issues or reviewing the details of a Codacy analysis run."""
    path: ListPullRequestLogsRequestPath

# Operation: list_commit_analysis_logs
class ListCommitLogsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The unique identifier of the commit whose analysis logs are being requested, provided as a UUID or full commit SHA hash.")
class ListCommitLogsRequest(StrictModel):
    """Retrieves the analysis log entries for a specific commit in a repository, providing details about the analysis process and any issues encountered during execution."""
    path: ListCommitLogsRequestPath

# Operation: list_commit_files
class ListCommitFilesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The unique identifier of the commit, provided as a UUID or full SHA hash string.")
class ListCommitFilesRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The branch to scope the analysis results to; must be a branch enabled on Codacy. Defaults to the repository's main branch if omitted.")
    filter_: Literal["withCoverageChanges"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Narrows the returned files by type: omit to return all files changed in the commit or with coverage changes, or use 'withCoverageChanges' to return only files that have coverage changes.")
    limit: int | None = Field(default=None, description="Maximum number of file results to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the results to only include files whose relative path contains the specified string.")
    sort_column: Literal["totalCoverage", "deltaCoverage", "filename"] | None = Field(default=None, validation_alias="sortColumn", serialization_alias="sortColumn", description="The field by which to sort the returned files: 'filename' (default) sorts alphabetically, 'deltaCoverage' sorts by coverage change, and 'totalCoverage' sorts by overall coverage value.")
    column_order: Literal["asc", "desc"] | None = Field(default=None, validation_alias="columnOrder", serialization_alias="columnOrder", description="The direction in which to sort results: 'asc' for ascending order (default) or 'desc' for descending order.")
class ListCommitFilesRequest(StrictModel):
    """Retrieves the list of files changed in a specific commit along with their static analysis and coverage results. Supports filtering, searching, sorting, and pagination to narrow down results."""
    path: ListCommitFilesRequestPath
    query: ListCommitFilesRequestQuery | None = None

# Operation: list_pull_request_files
class ListPullRequestFilesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique numeric identifier of the pull request within the repository.", json_schema_extra={'format': 'int32'})
class ListPullRequestFilesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of file results to return per request. Must be between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    sort_column: Literal["totalCoverage", "deltaCoverage", "filename"] | None = Field(default=None, validation_alias="sortColumn", serialization_alias="sortColumn", description="The field by which to sort the returned files. Use `filename` to sort alphabetically by file path, `deltaCoverage` to sort by the change in coverage, or `totalCoverage` to sort by the overall coverage value.")
    column_order: Literal["asc", "desc"] | None = Field(default=None, validation_alias="columnOrder", serialization_alias="columnOrder", description="The direction in which to order the sorted results, either ascending or descending.")
class ListPullRequestFilesRequest(StrictModel):
    """Retrieves the list of files changed in a pull request along with their static analysis results. Supports sorting by filename, coverage delta, or total coverage."""
    path: ListPullRequestFilesRequestPath
    query: ListPullRequestFilesRequestQuery | None = None

# Operation: follow_repository
class FollowAddedRepositoryRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization to follow.")
class FollowAddedRepositoryRequest(StrictModel):
    """Follow a repository that has already been added to Codacy, enabling tracking of its analysis and quality metrics for the authenticated user."""
    path: FollowAddedRepositoryRequestPath

# Operation: unfollow_repository
class UnfollowRepositoryRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization to unfollow.")
class UnfollowRepositoryRequest(StrictModel):
    """Stops following a repository in the specified organization on a Git provider, removing it from the list of monitored repositories."""
    path: UnfollowRepositoryRequestPath

# Operation: update_repository_quality_settings
class UpdateRepositoryQualitySettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class UpdateRepositoryQualitySettingsRequestBody(StrictModel):
    """The new value for the quality goals of the repository"""
    max_issue_percentage: int | None = Field(default=None, validation_alias="maxIssuePercentage", serialization_alias="maxIssuePercentage", description="The maximum acceptable percentage of files with issues; the repository is flagged as unhealthy if this threshold is exceeded. Must be a non-negative integer representing a percentage.", json_schema_extra={'format': 'int32'})
    max_duplicated_files_percentage: int | None = Field(default=None, validation_alias="maxDuplicatedFilesPercentage", serialization_alias="maxDuplicatedFilesPercentage", description="The maximum acceptable percentage of duplicated files; the repository is flagged as unhealthy if this threshold is exceeded. Must be a non-negative integer representing a percentage.", json_schema_extra={'format': 'int32'})
    min_coverage_percentage: int | None = Field(default=None, validation_alias="minCoveragePercentage", serialization_alias="minCoveragePercentage", description="The minimum required code coverage percentage; the repository is flagged as unhealthy if coverage falls below this threshold. Must be a non-negative integer representing a percentage.", json_schema_extra={'format': 'int32'})
    max_complex_files_percentage: int | None = Field(default=None, validation_alias="maxComplexFilesPercentage", serialization_alias="maxComplexFilesPercentage", description="The maximum acceptable percentage of complex files; the repository is flagged as unhealthy if this threshold is exceeded. Must be a non-negative integer representing a percentage.", json_schema_extra={'format': 'int32'})
    file_duplication_block_threshold: int | None = Field(default=None, validation_alias="fileDuplicationBlockThreshold", serialization_alias="fileDuplicationBlockThreshold", description="The number of cloned blocks above which a file is considered duplicated within this repository. Must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    file_complexity_value_threshold: int | None = Field(default=None, validation_alias="fileComplexityValueThreshold", serialization_alias="fileComplexityValueThreshold", description="The complexity score above which a file is considered complex within this repository. Must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
class UpdateRepositoryQualitySettingsRequest(StrictModel):
    """Updates the quality gate thresholds for a specific repository, defining the criteria under which the repository is considered healthy or unhealthy across issues, duplication, coverage, and complexity metrics."""
    path: UpdateRepositoryQualitySettingsRequestPath
    body: UpdateRepositoryQualitySettingsRequestBody | None = None

# Operation: regenerate_repository_ssh_user_key
class RegenerateUserSshKeyRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository, such as gh for GitHub, gl for GitLab, or bb for Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class RegenerateUserSshKeyRequest(StrictModel):
    """Regenerates the user SSH key Codacy uses to clone the specified repository, automatically adding the new public key to the user's account on the Git provider. Using a user SSH key is recommended when the repository includes submodules."""
    path: RegenerateUserSshKeyRequestPath

# Operation: regenerate_repository_ssh_key
class RegenerateRepositorySshKeyRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
class RegenerateRepositorySshKeyRequest(StrictModel):
    """Regenerates the SSH key Codacy uses to clone a specific repository, automatically updating the new public key on the Git provider."""
    path: RegenerateRepositorySshKeyRequestPath

# Operation: get_repository_ssh_key
class GetRepositoryPublicSshKeyRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class GetRepositoryPublicSshKeyRequest(StrictModel):
    """Retrieves the most recently generated public SSH key associated with a repository, which may be either a user or repository-level SSH key. Useful for verifying or displaying the active SSH key configured for repository access."""
    path: GetRepositoryPublicSshKeyRequestPath

# Operation: sync_repository
class SyncRepositoryWithProviderRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears under the organization on the Git provider.")
class SyncRepositoryWithProviderRequest(StrictModel):
    """Synchronizes a repository's name and visibility settings in Codacy with the current state from the upstream Git provider. Useful after renaming or changing the visibility of a repository directly on the provider."""
    path: SyncRepositoryWithProviderRequestPath

# Operation: get_build_server_analysis_setting
class GetBuildServerAnalysisSettingRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class GetBuildServerAnalysisSettingRequest(StrictModel):
    """Retrieves the current status of the 'Run analysis on your build server' setting for a specific repository. Use this to check whether build server analysis is enabled or disabled."""
    path: GetBuildServerAnalysisSettingRequestPath

# Operation: list_repository_languages
class GetRepositoryLanguagesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears within the Git provider organization.")
class GetRepositoryLanguagesRequest(StrictModel):
    """Retrieves all programming languages detected in a repository, including their associated file extensions and whether each language is enabled for analysis."""
    path: GetRepositoryLanguagesRequestPath

# Operation: configure_repository_language_settings
class PatchRepositoryLanguageResponseSettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class PatchRepositoryLanguageResponseSettingsRequestBody(StrictModel):
    languages: list[RepositoryLanguageUpdate] = Field(default=..., description="The complete list of languages to configure for this repository. Each item should represent a language identifier; order is not significant, and the full desired set must be provided as this replaces existing settings.")
class PatchRepositoryLanguageResponseSettingsRequest(StrictModel):
    """Updates the language response settings for a specific repository, controlling which programming languages are recognized and analyzed. Use this to tailor language detection behavior for a given repository within an organization."""
    path: PatchRepositoryLanguageResponseSettingsRequestPath
    body: PatchRepositoryLanguageResponseSettingsRequestBody

# Operation: get_repository_commit_quality_settings
class GetCommitQualitySettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class GetCommitQualitySettingsRequest(StrictModel):
    """Retrieves the quality gate settings applied to commits for a specific repository. Note that diff coverage threshold is not included, as it is not currently supported for commit-level quality checks."""
    path: GetCommitQualitySettingsRequestPath

# Operation: reset_repository_commit_quality_settings
class ResetCommitsQualitySettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization on the Git provider under which the repository resides.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization whose commit quality settings will be reset.")
class ResetCommitsQualitySettingsRequest(StrictModel):
    """Resets the commit quality settings for a specific repository to Codacy's default values, discarding any custom configurations previously applied."""
    path: ResetCommitsQualitySettingsRequestPath

# Operation: reset_repository_quality_settings
class ResetRepositoryQualitySettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The exact repository name as it appears under the organization on the Git provider.")
class ResetRepositoryQualitySettingsRequest(StrictModel):
    """Resets all quality settings for a specific repository back to Codacy's default values, discarding any custom configurations that were previously applied."""
    path: ResetRepositoryQualitySettingsRequestPath

# Operation: list_organization_pull_requests
class ListOrganizationPullRequestsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider.")
class ListOrganizationPullRequestsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of pull requests to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters pull requests by matching the provided string against repository names or other relevant fields.")
class ListOrganizationPullRequestsRequest(StrictModel):
    """Retrieves pull requests across all repositories in an organization that the authenticated user has access to. Results can be sorted by last updated date (default), impact, or merged status."""
    path: ListOrganizationPullRequestsRequestPath
    query: ListOrganizationPullRequestsRequestQuery | None = None

# Operation: list_commit_statistics
class ListCommitAnalysisStatsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ListCommitAnalysisStatsRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The repository branch to retrieve commit statistics for, which must be a branch enabled in Codacy settings. Defaults to the main branch configured in the Codacy repository settings if omitted.")
    days: int | None = Field(default=None, description="The number of days of commit statistics to return, ranging from 1 to 365. Returns the most recent days that have analysis data, defaulting to 31 if not specified.", ge=1, le=365, json_schema_extra={'format': 'int32'})
class ListCommitAnalysisStatsRequest(StrictModel):
    """Retrieves daily commit analysis statistics for a repository over the last N days that have available analysis data. Note that returned days reflect days with actual data, which may not align with the last N consecutive calendar days."""
    path: ListCommitAnalysisStatsRequestPath
    query: ListCommitAnalysisStatsRequestQuery | None = None

# Operation: list_repository_category_overviews
class ListCategoryOverviewsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the specified organization on the Git provider.")
class ListCategoryOverviewsRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Name of a branch enabled on Codacy for which to retrieve category overviews; defaults to the main branch configured in Codacy repository settings if omitted.")
class ListCategoryOverviewsRequest(StrictModel):
    """Retrieves analysis category overviews (e.g., code quality, security, complexity) for a specific repository, summarizing issue counts and grades per category. Authentication is not required for public repositories."""
    path: ListCategoryOverviewsRequestPath
    query: ListCategoryOverviewsRequestQuery | None = None

# Operation: search_repository_issues
class SearchRepositoryIssuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the repository, such as GitHub, GitLab, or Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
class SearchRepositoryIssuesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of issues to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class SearchRepositoryIssuesRequest(StrictModel):
    """Searches and returns issues found by Codacy in a specific repository, equivalent to the Issues page view. Supports filtering via request body to narrow results by category, severity, or other criteria."""
    path: SearchRepositoryIssuesRequestPath
    query: SearchRepositoryIssuesRequestQuery | None = None

# Operation: bulk_ignore_repository_issues
class BulkIgnoreIssuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class BulkIgnoreIssuesRequestBody(StrictModel):
    """List of issue ids to ignore"""
    issue_ids: list[str] = Field(default=..., validation_alias="issueIds", serialization_alias="issueIds", description="An unordered list of unique issue IDs to ignore. Maximum of 50 IDs per request; each item should be a valid issue identifier.")
    reason: str | None = Field(default=None, description="An optional reason categorizing why the issues are being ignored, used for tracking and audit purposes.")
    comment: str | None = Field(default=None, description="An optional free-text comment providing additional context or explanation for ignoring the specified issues.")
class BulkIgnoreIssuesRequest(StrictModel):
    """Ignores a batch of issues in a specified repository, suppressing them from analysis results. Accepts up to 50 issue IDs per request, with an optional reason and comment for audit purposes."""
    path: BulkIgnoreIssuesRequestPath
    body: BulkIgnoreIssuesRequestBody

# Operation: get_repository_issues_overview
class IssuesOverviewRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., GitHub, GitLab, or Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class IssuesOverviewRequest(StrictModel):
    """Retrieves a summary of issues found by Codacy in a specific repository, including issue counts and breakdowns as shown on the Issues page. Supports filtering via request body parameters."""
    path: IssuesOverviewRequestPath

# Operation: get_repository_issue
class GetIssueRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    issue_id: int = Field(default=..., validation_alias="issueId", serialization_alias="issueId", description="The unique numeric identifier of the open issue to retrieve.", json_schema_extra={'format': 'int64'})
class GetIssueRequest(StrictModel):
    """Retrieves detailed information about a specific open issue in a repository. Requires identifying the Git provider, organization, repository, and issue ID."""
    path: GetIssueRequestPath

# Operation: set_issue_ignored_state
class UpdateIssueStateRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the organization on the Git provider.")
    issue_id: str = Field(default=..., validation_alias="issueId", serialization_alias="issueId", description="Unique identifier of the issue to update.")
class UpdateIssueStateRequestBody(StrictModel):
    """New ignored status of the issue"""
    ignored: bool = Field(default=..., description="Set to true to ignore the issue or false to unignore it and restore it to an active state.")
    reason: Literal["AcceptedUse", "FalsePositive", "NotExploitable", "TestCode", "ExternalCode"] | None = Field(default=None, description="Predefined category explaining why the issue is being ignored; required when ignoring an issue to ensure consistent classification.")
    comment: str | None = Field(default=None, description="Free-text comment providing additional context or justification for the ignore action, supplementing the predefined reason.")
class UpdateIssueStateRequest(StrictModel):
    """Ignore or unignore a specific code analysis issue in a repository, optionally providing a predefined reason and comment to justify the action."""
    path: UpdateIssueStateRequestPath
    body: UpdateIssueStateRequestBody

# Operation: ignore_issue_false_positive
class IgnoreFalsePositiveRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    issue_id: str = Field(default=..., validation_alias="issueId", serialization_alias="issueId", description="The unique identifier of the issue whose false positive result should be ignored.")
class IgnoreFalsePositiveRequest(StrictModel):
    """Marks a false positive result on a specific issue as ignored, suppressing it from future analysis reports. Use this to dismiss incorrectly flagged issues within a repository."""
    path: IgnoreFalsePositiveRequestPath

# Operation: list_ignored_issues
class SearchRepositoryIgnoredIssuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class SearchRepositoryIgnoredIssuesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of ignored issues to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class SearchRepositoryIgnoredIssuesRequest(StrictModel):
    """Retrieves a paginated list of issues that Codacy detected but were manually marked as ignored in the specified repository. Supports filtering via request body parameters."""
    path: SearchRepositoryIgnoredIssuesRequestPath
    query: SearchRepositoryIgnoredIssuesRequestQuery | None = None

# Operation: list_repository_commits
class ListRepositoryCommitsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ListRepositoryCommitsRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The name of a branch enabled on Codacy for this repository, as returned by listRepositoryBranches. Defaults to the main branch configured in Codacy repository settings if omitted.")
    limit: int | None = Field(default=None, description="Maximum number of commit results to return. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListRepositoryCommitsRequest(StrictModel):
    """Retrieves Codacy analysis results for commits in a specified branch of a repository. Defaults to the main branch if no branch is specified."""
    path: ListRepositoryCommitsRequestPath
    query: ListRepositoryCommitsRequestQuery | None = None

# Operation: get_commit_analysis
class GetCommitRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository, such as 'gh' for GitHub, 'gl' for GitLab, or 'bb' for Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The full SHA hash or UUID that uniquely identifies the commit to retrieve analysis results for.")
class GetCommitRequest(StrictModel):
    """Retrieves the analysis results for a specific commit in a repository, including code quality metrics and issue findings. Useful for inspecting the impact of a particular commit on overall code health."""
    path: GetCommitRequestPath

# Operation: get_commit_delta_statistics
class GetCommitDeltaStatisticsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The unique identifier for the commit, provided as a UUID or full SHA hash string.")
class GetCommitDeltaStatisticsRequest(StrictModel):
    """Retrieves quality metric deltas introduced by a specific commit, showing how the commit changed code quality indicators. Returns zero or null values for metrics if Codacy has not yet analyzed the commit."""
    path: GetCommitDeltaStatisticsRequestPath

# Operation: list_commit_delta_issues
class ListCommitDeltaIssuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    src_commit_uuid: str = Field(default=..., validation_alias="srcCommitUuid", serialization_alias="srcCommitUuid", description="The SHA or UUID of the source commit to analyze; the delta is calculated from this commit against its parent or the specified target commit.")
class ListCommitDeltaIssuesRequestQuery(StrictModel):
    target_commit_uuid: str | None = Field(default=None, validation_alias="targetCommitUuid", serialization_alias="targetCommitUuid", description="The SHA or UUID of an optional target commit to use as the comparison baseline instead of the source commit's parent.")
    status: Literal["all", "new", "fixed"] | None = Field(default=None, description="Filters results by issue status: all returns every delta issue, new returns only introduced issues, and fixed returns only resolved issues.")
    only_potential: bool | None = Field(default=None, validation_alias="onlyPotential", serialization_alias="onlyPotential", description="When set to true, restricts results to potential issues only, excluding confirmed issues from the response.")
    limit: int | None = Field(default=None, description="Maximum number of issues to return per request; must be between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListCommitDeltaIssuesRequest(StrictModel):
    """Retrieves issues introduced or fixed by a specific commit, calculated as a delta between the source commit and its parent (or an optional target commit). Use this to audit code quality changes at the commit level."""
    path: ListCommitDeltaIssuesRequestPath
    query: ListCommitDeltaIssuesRequestQuery | None = None

# Operation: update_current_user
class PatchUserRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name to assign to the authenticated user's profile.")
    should_do_client_qualification: bool | None = Field(default=None, validation_alias="shouldDoClientQualification", serialization_alias="shouldDoClientQualification", description="Whether the system should trigger client qualification checks for this user.")
class PatchUserRequest(StrictModel):
    """Updates profile settings for the currently authenticated user. Only the fields provided will be modified."""
    body: PatchUserRequestBody | None = None

# Operation: list_organizations
class ListUserOrganizationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of organizations to return in a single response, between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListUserOrganizationsRequest(StrictModel):
    """Retrieves all organizations that the currently authenticated user belongs to. Returns a paginated list up to the specified limit."""
    query: ListUserOrganizationsRequestQuery | None = None

# Operation: list_organizations_by_provider
class ListOrganizationsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider to query for organizations. Use the short identifier code for the desired platform (e.g., GitHub, GitLab, Bitbucket).")
class ListOrganizationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of organizations to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListOrganizationsRequest(StrictModel):
    """Retrieves all organizations associated with the authenticated user for a specified Git provider. Useful for discovering available organizations before performing organization-scoped operations."""
    path: ListOrganizationsRequestPath
    query: ListOrganizationsRequestQuery | None = None

# Operation: get_organization_for_user
class GetUserOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
class GetUserOrganizationRequest(StrictModel):
    """Retrieves details for a specific organization associated with the authenticated user on a given Git provider. Useful for confirming organization membership and accessing organization-level metadata."""
    path: GetUserOrganizationRequestPath

# Operation: list_integrations
class ListUserIntegrationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of integrations to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListUserIntegrationsRequest(StrictModel):
    """Retrieves all integrations connected to the authenticated user's account. Returns a paginated list of integration records up to the specified limit."""
    query: ListUserIntegrationsRequestQuery | None = None

# Operation: delete_integration
class DeleteIntegrationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The identifier for the Git provider whose integration should be deleted. Accepted values include short codes for supported providers such as GitHub, GitLab, and Bitbucket.")
class DeleteIntegrationRequest(StrictModel):
    """Permanently removes the connected Git provider integration for the authenticated user. Once deleted, the user will need to re-authenticate to restore access for that provider."""
    path: DeleteIntegrationRequestPath

# Operation: get_organization
class GetOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider.")
class GetOrganizationRequest(StrictModel):
    """Retrieves details for a specific organization from a Git provider. Returns organization metadata such as name, settings, and associated information."""
    path: GetOrganizationRequestPath

# Operation: delete_organization
class DeleteOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform.")
class DeleteOrganizationRequest(StrictModel):
    """Permanently removes an organization from Codacy by deleting its association with the specified Git provider. This action cannot be undone and will remove all related configuration and data within Codacy."""
    path: DeleteOrganizationRequestPath

# Operation: get_organization_by_installation_id
class GetOrganizationByInstallationIdRequestPath(StrictModel):
    provider: str = Field(default=..., description="The git provider identifier for the installation. Currently only GitHub ('gh') is supported.")
    installation_id: int = Field(default=..., validation_alias="installationId", serialization_alias="installationId", description="The unique numeric identifier of the Codacy installation to look up the associated organization for.", json_schema_extra={'format': 'int64'})
class GetOrganizationByInstallationIdRequest(StrictModel):
    """Retrieves an organization associated with a specific provider installation ID. Currently supports GitHub ('gh') as the git provider."""
    path: GetOrganizationByInstallationIdRequestPath

# Operation: get_organization_billing
class OrganizationDetailedBillingRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
class OrganizationDetailedBillingRequest(StrictModel):
    """Retrieves detailed billing information for a specific organization on a Git provider, including subscription and usage details."""
    path: OrganizationDetailedBillingRequestPath

# Operation: update_organization_billing
class UpdateOrganizationDetailedBillingRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
class UpdateOrganizationDetailedBillingRequest(StrictModel):
    """Updates the billing information for a specified organization on a given Git provider. Use this to modify billing details associated with the organization's Codacy account."""
    path: UpdateOrganizationDetailedBillingRequestPath

# Operation: get_organization_billing_card
class OrganizationBillingCardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
class OrganizationBillingCardRequest(StrictModel):
    """Retrieves the payment card details associated with an organization's billing account on a specified Git provider. Useful for reviewing current billing payment method information."""
    path: OrganizationBillingCardRequestPath

# Operation: add_billing_card
class OrganizationBillingAddCardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
class OrganizationBillingAddCardRequest(StrictModel):
    """Adds a payment card to the specified organization's billing profile using a Stripe token. The token must be obtained from the Stripe /v1/tokens API prior to calling this endpoint."""
    path: OrganizationBillingAddCardRequestPath

# Operation: estimate_organization_billing
class OrganizationBillingEstimationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class OrganizationBillingEstimationRequestQuery(StrictModel):
    payment_plan_code: str = Field(default=..., validation_alias="paymentPlanCode", serialization_alias="paymentPlanCode", description="The code identifying the payment plan to estimate costs for. Available plan codes can be retrieved using the listPaymentPlans operation.")
    promo_code: str | None = Field(default=None, validation_alias="promoCode", serialization_alias="promoCode", description="An optional promotional code to apply discounts or adjustments to the billing estimation.")
class OrganizationBillingEstimationRequest(StrictModel):
    """Retrieves a billing cost estimation for an organization based on a specified payment plan and optional promotional code. Useful for previewing pricing before committing to a plan."""
    path: OrganizationBillingEstimationRequestPath
    query: OrganizationBillingEstimationRequestQuery

# Operation: change_organization_billing_plan
class ChangeOrganizationPlanRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
class ChangeOrganizationPlanRequest(StrictModel):
    """Changes the billing plan for a specified organization on a Git provider. Available plan codes can be retrieved using the list_payment_plans operation."""
    path: ChangeOrganizationPlanRequestPath

# Operation: apply_organization_provider_settings
class ApplyProviderSettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by its short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
class ApplyProviderSettingsRequest(StrictModel):
    """Applies the organization's default provider settings to all repositories within the specified Git provider organization. Use this to propagate updated integration settings uniformly across all repositories at once."""
    path: ApplyProviderSettingsRequestPath

# Operation: get_provider_settings
class GetProviderSettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider identifier representing the source control platform to query (e.g., GitHub, GitLab, or Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider platform.")
class GetProviderSettingsRequest(StrictModel):
    """Retrieves Git provider integration settings for a specific organization, including configuration details for the connected provider account."""
    path: GetProviderSettingsRequestPath

# Operation: configure_provider_settings
class UpdateProviderSettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider platform hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class UpdateProviderSettingsRequestBody(StrictModel):
    commit_status: bool | None = Field(default=None, validation_alias="commitStatus", serialization_alias="commitStatus", description="Enables or disables Codacy commit status checks, which report analysis results directly on commits and pull requests.")
    pull_request_comment: bool | None = Field(default=None, validation_alias="pullRequestComment", serialization_alias="pullRequestComment", description="Enables or disables inline issue annotations posted as pull request comments by Codacy.")
    pull_request_summary: bool | None = Field(default=None, validation_alias="pullRequestSummary", serialization_alias="pullRequestSummary", description="Enables or disables pull request summary comments that aggregate Codacy issue findings.")
    coverage_summary: bool | None = Field(default=None, validation_alias="coverageSummary", serialization_alias="coverageSummary", description="Enables or disables coverage summary reporting on pull requests. Supported on GitHub only.")
    suggestions: bool | None = Field(default=None, description="Enables or disables AI-generated suggested code fixes posted on pull requests. Supported on GitHub only.")
    ai_enhanced_comments: bool | None = Field(default=None, validation_alias="aiEnhancedComments", serialization_alias="aiEnhancedComments", description="Enables or disables AI-enhanced pull request comments; when combined with Suggested Fixes (GitHub only), AI comments also include inline code fix suggestions.")
    ai_pull_request_reviewer: bool | None = Field(default=None, validation_alias="aiPullRequestReviewer", serialization_alias="aiPullRequestReviewer", description="Enables or disables the AI Pull Request Reviewer, which automatically analyzes pull requests and posts comments on code quality and potential issues. Supported on GitHub only.")
    ai_pull_request_reviewer_automatic: bool | None = Field(default=None, validation_alias="aiPullRequestReviewerAutomatic", serialization_alias="aiPullRequestReviewerAutomatic", description="Enables or disables automatic triggering of the AI Pull Request Reviewer on each new pull request; after the initial automatic review, subsequent reviews must be explicitly requested. Supported on GitHub only.")
    pull_request_unified_summary: bool | None = Field(default=None, validation_alias="pullRequestUnifiedSummary", serialization_alias="pullRequestUnifiedSummary", description="Enables or disables a unified pull request summary that combines both coverage and analysis results into a single Codacy comment. Supported on GitHub only.")
class UpdateProviderSettingsRequest(StrictModel):
    """Creates or updates Git provider integration settings for an organization, controlling which Codacy features are active such as status checks, pull request annotations, AI-powered reviews, and coverage summaries."""
    path: UpdateProviderSettingsRequestPath
    body: UpdateProviderSettingsRequestBody | None = None

# Operation: get_repository_provider_integration_settings
class GetRepositoryIntegrationsSettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class GetRepositoryIntegrationsSettingsRequest(StrictModel):
    """Retrieves the Git provider integration settings for a specific repository, including configuration details that control how Codacy interacts with the provider for that repository."""
    path: GetRepositoryIntegrationsSettingsRequestPath

# Operation: update_repository_integration_settings
class UpdateRepositoryIntegrationsSettingsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears under the organization on the Git provider.")
class UpdateRepositoryIntegrationsSettingsRequestBody(StrictModel):
    commit_status: bool | None = Field(default=None, validation_alias="commitStatus", serialization_alias="commitStatus", description="Enables or disables commit status checks, which report Codacy analysis results directly on commits and pull requests.")
    pull_request_comment: bool | None = Field(default=None, validation_alias="pullRequestComment", serialization_alias="pullRequestComment", description="Enables or disables inline issue annotations posted as pull request comments for each identified code issue.")
    pull_request_summary: bool | None = Field(default=None, validation_alias="pullRequestSummary", serialization_alias="pullRequestSummary", description="Enables or disables pull request summary comments that aggregate all issues found in the analysis.")
    coverage_summary: bool | None = Field(default=None, validation_alias="coverageSummary", serialization_alias="coverageSummary", description="Enables or disables a coverage summary comment on pull requests showing coverage changes. Available on GitHub only.")
    suggestions: bool | None = Field(default=None, description="Enables or disables suggested code fixes posted as pull request comments. Available on GitHub only.")
    ai_enhanced_comments: bool | None = Field(default=None, validation_alias="aiEnhancedComments", serialization_alias="aiEnhancedComments", description="Enables or disables AI-enhanced comments on pull requests; when combined with Suggested Fixes (GitHub only), the AI comments also include fix suggestions.")
    ai_pull_request_reviewer: bool | None = Field(default=None, validation_alias="aiPullRequestReviewer", serialization_alias="aiPullRequestReviewer", description="Enables or disables the AI Pull Request Reviewer, which automatically analyzes pull requests and posts comments on code quality and potential issues. Available on GitHub only.")
    ai_pull_request_reviewer_automatic: bool | None = Field(default=None, validation_alias="aiPullRequestReviewerAutomatic", serialization_alias="aiPullRequestReviewerAutomatic", description="Enables or disables automatic triggering of the AI Pull Request Reviewer on each new pull request; after the initial automatic review, subsequent reviews must be explicitly requested. Available on GitHub only.")
    pull_request_unified_summary: bool | None = Field(default=None, validation_alias="pullRequestUnifiedSummary", serialization_alias="pullRequestUnifiedSummary", description="Enables or disables a unified pull request summary that combines both coverage and analysis results into a single comment. Available on GitHub only.")
class UpdateRepositoryIntegrationsSettingsRequest(StrictModel):
    """Updates the Git provider integration settings for a specific repository, controlling which Codacy features are active such as status checks, pull request comments, AI reviews, and coverage summaries."""
    path: UpdateRepositoryIntegrationsSettingsRequestPath
    body: UpdateRepositoryIntegrationsSettingsRequestBody | None = None

# Operation: create_post_commit_hook
class CreatePostCommitHookRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider under which the repository resides.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization for which the post-commit hook will be created.")
class CreatePostCommitHookRequest(StrictModel):
    """Creates a post-commit hook integration for a repository, enabling Codacy to receive commit notifications and trigger analysis automatically after each push."""
    path: CreatePostCommitHookRequestPath

# Operation: refresh_repository_provider_integration
class RefreshProviderRepositoryIntegrationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository. Accepted values are 'gh' for GitHub, 'gl' for GitLab, or 'bb' for Bitbucket. Note: this operation is only supported for GitLab and Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or workspace on the Git provider under which the repository resides.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class RefreshProviderRepositoryIntegrationRequest(StrictModel):
    """Refreshes the Git provider integration for a specific repository on GitLab or Bitbucket, using the authenticated user's credentials to enable commenting on new pull requests."""
    path: RefreshProviderRepositoryIntegrationRequestPath

# Operation: list_organization_repositories
class ListOrganizationRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier code for the desired provider.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
class ListOrganizationRepositoriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100; note the API may return more results than specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="A search string used to filter repositories by name. Only repositories whose names contain this string will be returned.")
    filter_: Literal["Synced", "NotSynced", "AllSynced"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Controls which repositories are returned based on their sync status: `Synced` returns repositories the user has access to, `NotSynced` returns repositories fetched from the provider but not yet synced, and `AllSynced` returns all organization repositories (requires admin access).")
    languages: str | None = Field(default=None, description="Filters results to repositories that use the specified programming languages, provided as a comma-separated list of language names.")
    segments: str | None = Field(default=None, description="Filters results to repositories belonging to the specified segments, provided as a comma-separated list of integer segment identifiers.")
class ListOrganizationRepositoriesRequest(StrictModel):
    """Retrieves repositories belonging to a specific organization on a Git provider for the authenticated user. Supports filtering by sync status, language, and segment, with cursor-based pagination (Bitbucket cursors must be URL-encoded before use in subsequent requests)."""
    path: ListOrganizationRepositoriesRequestPath
    query: ListOrganizationRepositoriesRequestQuery | None = None

# Operation: get_organization_onboarding_progress
class RetrieveOrganizationOnboardingProgressRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider where the organization is hosted. Use the provider's abbreviated identifier.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform.")
class RetrieveOrganizationOnboardingProgressRequest(StrictModel):
    """Retrieves the current onboarding progress for a specific organization on a Git provider. Useful for tracking setup completion status during the organization integration workflow."""
    path: RetrieveOrganizationOnboardingProgressRequestPath

# Operation: list_organization_people
class ListPeopleFromOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
class ListPeopleFromOrganizationRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of people to return per request; must be between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned people by matching the provided string against their name or related identifiers.")
    only_members: bool | None = Field(default=None, validation_alias="onlyMembers", serialization_alias="onlyMembers", description="When true, restricts results to only registered Codacy users; when false, also includes commit authors who have not joined Codacy.")
class ListPeopleFromOrganizationRequest(StrictModel):
    """Retrieves a list of people associated with a specific organization on a Git provider, including Codacy users and optionally commit authors who are not Codacy users."""
    path: ListPeopleFromOrganizationRequestPath
    query: ListPeopleFromOrganizationRequestQuery | None = None

# Operation: add_organization_members
class AddPeopleToOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class AddPeopleToOrganizationRequest(StrictModel):
    """Adds people to an organization on the specified Git provider, assigning them as members or committers based on whether they have a pending join request."""
    path: AddPeopleToOrganizationRequestPath

# Operation: export_organization_people_csv
class ListPeopleFromOrganizationCsvRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by its short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class ListPeopleFromOrganizationCsvRequest(StrictModel):
    """Generates and returns a CSV file listing all people in the specified organization, including their name, email, last login date, and last analysis date."""
    path: ListPeopleFromOrganizationCsvRequestPath

# Operation: remove_organization_members
class RemovePeopleFromOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target platform.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
class RemovePeopleFromOrganizationRequestBody(StrictModel):
    """List of committers/members to remove"""
    emails: list[str] = Field(default=..., description="List of member email addresses to remove from the organization. Each item must be a valid email address; order is not significant.")
class RemovePeopleFromOrganizationRequest(StrictModel):
    """Removes one or more members from a Git provider organization by their email addresses. Useful for revoking access when offboarding users or managing organization membership."""
    path: RemovePeopleFromOrganizationRequestPath
    body: RemovePeopleFromOrganizationRequestBody

# Operation: get_git_provider_app_permissions
class GitProviderAppPermissionsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, or Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform.")
class GitProviderAppPermissionsRequest(StrictModel):
    """Retrieves the current status of Codacy's Git provider app permissions for a specified organization, indicating which permissions have been granted or are missing."""
    path: GitProviderAppPermissionsRequestPath

# Operation: list_organization_people_suggestions
class PeopleSuggestionsForOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
class PeopleSuggestionsForOrganizationRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of people suggestions to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned suggestions to those whose name or identifier contains the provided search string.")
class PeopleSuggestionsForOrganizationRequest(StrictModel):
    """Retrieves suggested people (users) to add to an organization on a specified Git provider. Useful for discovering potential members based on activity or association with the organization."""
    path: PeopleSuggestionsForOrganizationRequestPath
    query: PeopleSuggestionsForOrganizationRequestQuery | None = None

# Operation: reanalyze_commit
class ReanalyzeCommitByIdRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ReanalyzeCommitByIdRequestBody(StrictModel):
    """UUID or SHA string that identifies the commit"""
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The full UUID or SHA hash string that uniquely identifies the commit to be reanalyzed.")
    clean_cache: bool | None = Field(default=None, validation_alias="cleanCache", serialization_alias="cleanCache", description="When set to true, clears any cached analysis data before reanalyzing the commit, ensuring the results are not influenced by previous runs.")
class ReanalyzeCommitByIdRequest(StrictModel):
    """Triggers a reanalysis of a specific commit in a repository. Optionally clears the cache before running the analysis to ensure fresh results."""
    path: ReanalyzeCommitByIdRequestPath
    body: ReanalyzeCommitByIdRequestBody

# Operation: get_repository
class GetRepositoryRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider platform.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears within the organization on the Git provider platform.")
class GetRepositoryRequest(StrictModel):
    """Retrieves detailed information about a specific repository within an organization on a given Git provider. Authentication is not required when accessing public repositories."""
    path: GetRepositoryRequestPath

# Operation: delete_repository
class DeleteRepositoryRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The exact name of the repository within the specified organization on the Git provider.")
class DeleteRepositoryRequest(StrictModel):
    """Permanently removes the specified repository from the organization on the given Git provider. This action cannot be undone and will remove all associated data from Codacy."""
    path: DeleteRepositoryRequestPath

# Operation: list_repository_people_suggestions
class PeopleSuggestionsForRepositoryRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class PeopleSuggestionsForRepositoryRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of people suggestions to return. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned suggestions to those whose names or identifiers match the provided search string.")
class PeopleSuggestionsForRepositoryRequest(StrictModel):
    """Retrieves suggested people (collaborators or contributors) for a specific repository within an organization. Useful for discovering relevant users to add or assign within a given repository context."""
    path: PeopleSuggestionsForRepositoryRequestPath
    query: PeopleSuggestionsForRepositoryRequestQuery | None = None

# Operation: list_repository_branches
class ListRepositoryBranchesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The short identifier for the Git provider hosting the repository (e.g., 'gh' for GitHub, 'gl' for GitLab, 'bb' for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ListRepositoryBranchesRequestQuery(StrictModel):
    enabled: bool | None = Field(default=None, description="Filters branches by their enabled status. When set to true, only enabled branches are returned; when set to false, only disabled branches are returned. Omit to return all branches regardless of status.")
    limit: int | None = Field(default=None, description="The maximum number of branches to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="A string used to filter branches by name, returning only branches whose names contain the provided value.")
    sort: str | None = Field(default=None, description="The field by which to sort the returned branches. Accepted values are 'name' to sort alphabetically or 'last-updated' to sort by most recent activity.")
    direction: str | None = Field(default=None, description="The direction in which to sort the results. Use 'asc' for ascending order or 'desc' for descending order.")
class ListRepositoryBranchesRequest(StrictModel):
    """Retrieves a paginated list of branches for a specified repository, with optional filtering by enabled status or search term. No authentication is required when accessing public repositories."""
    path: ListRepositoryBranchesRequestPath
    query: ListRepositoryBranchesRequestQuery | None = None

# Operation: configure_branch_analysis
class UpdateRepositoryBranchConfigurationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears under the organization on the Git provider.")
    branch_name: str = Field(default=..., validation_alias="branchName", serialization_alias="branchName", description="The exact name of the branch within the repository to configure.")
class UpdateRepositoryBranchConfigurationRequestBody(StrictModel):
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Set to true to enable Codacy analysis on this branch, or false to disable it.")
class UpdateRepositoryBranchConfigurationRequest(StrictModel):
    """Enable or disable Codacy analysis for a specific repository branch. Use this to control which branches are actively analyzed within a given organization and repository."""
    path: UpdateRepositoryBranchConfigurationRequestPath
    body: UpdateRepositoryBranchConfigurationRequestBody | None = None

# Operation: set_organization_join_mode
class UpdateJoinModeRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
class UpdateJoinModeRequestBody(StrictModel):
    """New join mode of the organization"""
    join_mode: Literal["auto", "adminAuto", "request"] = Field(default=..., validation_alias="joinMode", serialization_alias="joinMode", description="The join mode to apply to the organization: 'auto' allows anyone to join automatically, 'adminAuto' grants automatic access after admin approval, and 'request' requires members to submit a join request.")
class UpdateJoinModeRequest(StrictModel):
    """Updates the membership join mode for an organization on a specified Git provider, controlling how new members are admitted (automatically, admin-approved automatically, or by request)."""
    path: UpdateJoinModeRequestPath
    body: UpdateJoinModeRequestBody

# Operation: set_default_branch
class SetRepositoryBranchAsDefaultRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the organization on the Git provider.")
    branch_name: str = Field(default=..., validation_alias="branchName", serialization_alias="branchName", description="Name of the branch to designate as the new default; this branch must already be enabled on Codacy.")
class SetRepositoryBranchAsDefaultRequest(StrictModel):
    """Sets the default branch for a specified repository on Codacy. The target branch must already be enabled on Codacy before it can be designated as the default."""
    path: SetRepositoryBranchAsDefaultRequestPath

# Operation: list_branch_required_checks
class GetBranchRequiredChecksRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    branch_name: str = Field(default=..., validation_alias="branchName", serialization_alias="branchName", description="The name of the branch for which required status checks will be retrieved.")
class GetBranchRequiredChecksRequest(StrictModel):
    """Retrieves the required status checks configured for a specific branch in a repository. These checks must pass before pull requests can be merged into the branch."""
    path: GetBranchRequiredChecksRequestPath

# Operation: add_codacy_badge
class CreateBadgePullRequestPath(StrictModel):
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class CreateBadgePullRequest(StrictModel):
    """Creates a pull request that adds the Codacy static analysis badge to the repository's README. Only applies to public GitHub repositories that do not already have the badge; the pull request is created asynchronously and may fail after a successful response."""
    path: CreateBadgePullRequestPath

# Operation: check_organization_leave_eligibility
class CheckIfUserCanLeaveRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class CheckIfUserCanLeaveRequest(StrictModel):
    """Checks whether the authenticated user is eligible to leave the specified organization, returning either confirmation or the specific reasons preventing them from leaving."""
    path: CheckIfUserCanLeaveRequestPath

# Operation: list_organization_join_requests
class ListOrganizationJoinRequestsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The short identifier for the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
class ListOrganizationJoinRequestsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of join requests to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned join requests to those matching the provided search string, such as a username or partial name.")
class ListOrganizationJoinRequestsRequest(StrictModel):
    """Retrieves all pending requests from users asking to join a specified organization on a Git provider. Supports filtering by search term and pagination via a result limit."""
    path: ListOrganizationJoinRequestsRequestPath
    query: ListOrganizationJoinRequestsRequestQuery | None = None

# Operation: join_organization
class JoinOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider where the organization is hosted. Accepted values include identifiers for GitHub, GitLab, and Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider. This must match the organization's remote identifier on that platform.")
class JoinOrganizationRequest(StrictModel):
    """Joins an organization on a specified Git provider, granting the authenticated user membership in that organization. Requires the provider identifier and the organization's remote name."""
    path: JoinOrganizationRequestPath

# Operation: decline_organization_join_requests
class DeclineRequestsToJoinOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization. Use the short code for the target platform (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider. This must match the exact organization identifier used by the provider.")
class DeclineRequestsToJoinOrganizationRequest(StrictModel):
    """Declines pending requests from users seeking to join a specified organization on a Git provider. Targets the organization by provider and name, rejecting the specified user emails."""
    path: DeclineRequestsToJoinOrganizationRequestPath

# Operation: delete_organization_join_request
class DeleteOrganizationJoinRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    account_identifier: int = Field(default=..., validation_alias="accountIdentifier", serialization_alias="accountIdentifier", description="The unique numeric identifier of the user account whose join request should be deleted.", json_schema_extra={'format': 'int64'})
class DeleteOrganizationJoinRequest(StrictModel):
    """Cancels or removes a pending request for a user to join an organization on the specified Git provider. Identified by the provider, organization name, and the user's account identifier."""
    path: DeleteOrganizationJoinRequestPath

# Operation: add_repository
class AddRepositoryRequestBody(StrictModel):
    """Information of repository to add"""
    repository_full_path: str = Field(default=..., validation_alias="repositoryFullPath", serialization_alias="repositoryFullPath", description="The full path of the repository on the Git provider, beginning at the organization level with each path segment separated by a forward slash.")
    provider: str = Field(default=..., description="The Git provider that hosts the repository, identifying the source platform where the repository resides.")
class AddRepositoryRequest(StrictModel):
    """Adds a new repository to an existing Codacy organization, enabling code quality analysis and tracking for that repository."""
    body: AddRepositoryRequestBody

# Operation: add_organization
class AddOrganizationRequestBody(StrictModel):
    """Information of the organization to add"""
    provider: str = Field(default=..., description="The Git provider that hosts the organization, such as GitHub, GitLab, or Bitbucket.")
    remote_identifier: str = Field(default=..., validation_alias="remoteIdentifier", serialization_alias="remoteIdentifier", description="The unique identifier for the organization on the Git provider, used to locate and link the organization remotely.")
    name: str = Field(default=..., description="The display name of the organization as it appears on the Git provider.")
    type_: Literal["Account", "Organization"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Specifies whether the entity is a personal account or a shared organization, which determines available features and permissions.")
    products: list[Literal["quality", "coverage"]] | None = Field(default=None, description="A list of Codacy products to enable for the organization, where each item represents a product identifier. Order is not significant.")
class AddOrganizationRequest(StrictModel):
    """Registers an organization from a Git provider with Codacy, enabling code quality analysis and management for that organization's repositories."""
    body: AddOrganizationRequestBody

# Operation: delete_enterprise_token
class DeleteEnterpriseTokenRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider whose enterprise token should be deleted. Accepts short provider codes representing supported Git hosting services.")
class DeleteEnterpriseTokenRequest(StrictModel):
    """Deletes the stored GitHub Enterprise account token for the authenticated user. Once removed, the token will no longer be used to access enterprise-level resources."""
    path: DeleteEnterpriseTokenRequestPath

# Operation: add_enterprise_token
class AddEnterpriseTokenRequestBody(StrictModel):
    """Information of the enterprise token to create"""
    token: str = Field(default=..., description="The GitHub Enterprise personal access token with read permissions to be stored and used for authenticating enterprise-level resource requests.")
    provider: str = Field(default=..., description="The Git hosting provider associated with the enterprise account token being added.")
class AddEnterpriseTokenRequest(StrictModel):
    """Adds a GitHub Enterprise account token with read permissions for the authenticated user, enabling access to enterprise-level resources and repositories."""
    body: AddEnterpriseTokenRequestBody

# Operation: list_api_tokens
class GetUserApiTokensRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of API tokens to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetUserApiTokensRequest(StrictModel):
    """Retrieves all API tokens associated with the authenticated user's account. Useful for auditing active tokens or managing programmatic access credentials."""
    query: GetUserApiTokensRequestQuery | None = None

# Operation: create_api_token
class CreateUserApiTokenRequestBody(StrictModel):
    """Optional token expiration timestamp"""
    expires_at: str | None = Field(default=None, validation_alias="expiresAt", serialization_alias="expiresAt", description="Optional expiration date and time for the API token in ISO 8601 format. If omitted, the token does not expire.", json_schema_extra={'format': 'date-time'})
class CreateUserApiTokenRequest(StrictModel):
    """Creates a new account-level API token for the authenticated user, optionally scoped to a specific expiration date. API tokens are used to authenticate requests to the Codacy."""
    body: CreateUserApiTokenRequestBody | None = None

# Operation: delete_user_token
class DeleteUserApiTokenRequestPath(StrictModel):
    token_id: int = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique numeric identifier of the API token to delete. Obtain this ID from the list of tokens associated with the authenticated user's account.", json_schema_extra={'format': 'int64'})
class DeleteUserApiTokenRequest(StrictModel):
    """Permanently deletes a specific API token belonging to the authenticated user. Once deleted, any integrations or clients using this token will lose access immediately."""
    path: DeleteUserApiTokenRequestPath

# Operation: delete_billing_subscription
class DeleteSubscriptionRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, or Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider.")
class DeleteSubscriptionRequest(StrictModel):
    """Permanently removes the billing subscription for a specified organization on a given Git provider. This action cancels the organization's current billing plan and cannot be undone."""
    path: DeleteSubscriptionRequestPath

# Operation: list_provider_integrations
class ListProviderIntegrationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of provider integrations to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListProviderIntegrationsRequest(StrictModel):
    """Retrieves a list of provider integrations configured on Codacy's platform. Use this to discover available third-party integrations such as version control, CI, or issue tracking providers."""
    query: ListProviderIntegrationsRequestQuery | None = None

# Operation: search_entities
class AdminSearchRequestQuery(StrictModel):
    search: str | None = Field(default=None, description="A search string used to filter results by matching against entity names or IDs such as organizations or repositories.")
class AdminSearchRequest(StrictModel):
    """Search across Codacy entities such as Organizations and Repositories by name or ID. Restricted to Codacy admins only."""
    query: AdminSearchRequestQuery | None = None

# Operation: delete_dormant_accounts
class DeleteDormantAccountsRequestBody(StrictModel):
    """CSV file containing email addresses of the users to delete in a column called "email\""""
    body: str | None = Field(default=None, description="Raw CSV content exported from GitHub Enterprise identifying the dormant user accounts to be deleted.")
class DeleteDormantAccountsRequest(StrictModel):
    """Permanently deletes Codacy user accounts identified as dormant, based on a CSV file exported from GitHub Enterprise. Restricted to Codacy administrators only."""
    body: DeleteDormantAccountsRequestBody | None = None

# Operation: list_tools
class ListToolsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of tools to return in the response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListToolsRequest(StrictModel):
    """Retrieve a paginated list of available tools. Use the limit parameter to control how many tools are returned in a single response."""
    query: ListToolsRequestQuery | None = None

# Operation: list_tool_patterns
class ListPatternsRequestPath(StrictModel):
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The unique UUID identifying the tool whose patterns should be retrieved.")
class ListPatternsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of patterns to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    enabled: bool | None = Field(default=None, description="Filters patterns by their enabled status. Set to true to return only enabled patterns, or false to return only disabled patterns. Omit to return all patterns regardless of status.")
class ListPatternsRequest(StrictModel):
    """Retrieves the list of patterns associated with a specific tool. Supports filtering by enabled status and limiting the number of results returned."""
    path: ListPatternsRequestPath
    query: ListPatternsRequestQuery | None = None

# Operation: submit_pattern_feedback
class AddPatternFeedbackRequestPath(StrictModel):
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The unique UUID identifying the tool whose pattern is being reviewed.")
    pattern_id: str = Field(default=..., validation_alias="patternId", serialization_alias="patternId", description="The identifier of the specific pattern within the tool that the feedback applies to.")
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization on the specified Git provider whose context scopes this feedback.")
class AddPatternFeedbackRequestBody(StrictModel):
    reaction_feedback: bool = Field(default=..., validation_alias="reactionFeedback", serialization_alias="reactionFeedback", description="Boolean vote on the enriched pattern's relevance — true indicates the pattern is considered good or relevant, false indicates it is not.")
    feedback: str | None = Field(default=None, description="Optional free-text explanation describing why the enriched pattern is considered irrelevant or problematic, providing additional context for the negative feedback.")
class AddPatternFeedbackRequest(StrictModel):
    """Submits user feedback on an enriched tool pattern for a specific organization, indicating whether the pattern is considered relevant and optionally providing a written explanation."""
    path: AddPatternFeedbackRequestPath
    body: AddPatternFeedbackRequestBody

# Operation: get_pattern
class GetPatternRequestPath(StrictModel):
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID uniquely identifying the tool whose pattern you want to retrieve.")
    pattern_id: str = Field(default=..., validation_alias="patternId", serialization_alias="patternId", description="The identifier of the specific pattern to retrieve, typically referencing a named rule or checker within the tool.")
class GetPatternRequest(StrictModel):
    """Retrieves the full definition of a specific pattern associated with a given tool. Use this to inspect pattern rules, configuration, and metadata for a tool's code analysis or style enforcement pattern."""
    path: GetPatternRequestPath

# Operation: start_organization_metrics_collection
class InitiateMetricsForOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class InitiateMetricsForOrganizationRequestBody(StrictModel):
    metrics: list[str] | None = Field(default=None, description="List of specific metric identifiers to start collecting. If omitted, collection is initiated for all missing metrics. Order is not significant.")
class InitiateMetricsForOrganizationRequest(StrictModel):
    """Initiates data collection for any missing metrics within the specified organization. The organization must have metrics support enabled before calling this endpoint."""
    path: InitiateMetricsForOrganizationRequestPath
    body: InitiateMetricsForOrganizationRequestBody | None = None

# Operation: list_ready_metrics
class ReadyMetricsForOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization. Accepted values include identifiers for GitHub, GitLab, and Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider, used to scope the metrics retrieval to that specific organization.")
class ReadyMetricsForOrganizationRequest(StrictModel):
    """Retrieves the list of metrics that have completed data collection for a specified organization on a Git provider. Use this to determine which metrics are available and ready to query before requesting detailed metric data."""
    path: ReadyMetricsForOrganizationRequestPath

# Operation: get_latest_metric_value
class RetrieveLatestMetricValueRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The identifier of the metric to retrieve. Use the readyMetricsForOrganization endpoint to list all available metric names for the organization.")
class RetrieveLatestMetricValueRequestBodyEntityFilter(StrictModel):
    repositories: list[str] | None = Field(default=None, validation_alias="repositories", serialization_alias="repositories", description="Optional list of repository identifiers to scope the metric value to specific repositories within the organization. Order is not significant.")
    segment_ids: list[int] | None = Field(default=None, validation_alias="segmentIds", serialization_alias="segmentIds", description="Optional list of segment IDs used to filter the metric value by predefined organizational segments. Order is not significant.")
class RetrieveLatestMetricValueRequestBody(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="Optional list of dimension filters to narrow the metric query by specific dimensional criteria. Order is not significant.")
    entity_filter: RetrieveLatestMetricValueRequestBodyEntityFilter | None = Field(default=None, validation_alias="entityFilter", serialization_alias="entityFilter")
class RetrieveLatestMetricValueRequest(StrictModel):
    """Retrieves the current (latest) value of an aggregating metric for an organization, such as open issues. Note: this endpoint only supports aggregating metrics and does not work for accumulating metrics like fixed issues."""
    path: RetrieveLatestMetricValueRequestPath
    body: RetrieveLatestMetricValueRequestBody | None = None

# Operation: get_latest_grouped_metric_values
class RetrieveLatestMetricGroupedValuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, used to identify which platform to query.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The name of the aggregating metric to retrieve latest grouped values for. Use the readyMetricsForOrganization endpoint to list all available metric names.")
class RetrieveLatestMetricGroupedValuesRequestBodyFilterEntityFilter(StrictModel):
    repositories: list[str] | None = Field(default=None, validation_alias="repositories", serialization_alias="repositories", description="List of repository names to scope the metric results to. When omitted, results span all repositories in the organization.")
    segment_ids: list[int] | None = Field(default=None, validation_alias="segmentIds", serialization_alias="segmentIds", description="List of segment identifiers to filter the metric results by. When omitted, no segment filtering is applied.")
class RetrieveLatestMetricGroupedValuesRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="List of dimension filter values to narrow the metric results. Valid dimension values depend on the requested metric.")
    entity_filter: RetrieveLatestMetricGroupedValuesRequestBodyFilterEntityFilter | None = Field(default=None, validation_alias="entityFilter", serialization_alias="entityFilter")
class RetrieveLatestMetricGroupedValuesRequestBodyGroupBy(StrictModel):
    group_by: list[str] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="One or more grouping dimensions that determine how metric values are aggregated and returned. Accepted values are `organization`, `repository`, or a metric-specific dimension; for OpenIssues, NewIssues, and FixedIssues the supported dimensions are `category` and `severity`.")
    sort_direction: str | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Direction in which the returned metric values are sorted, either ascending or descending.")
    limit: int | None = Field(default=None, validation_alias="limit", serialization_alias="limit", description="Maximum number of grouped metric value entries to return in the response.")
class RetrieveLatestMetricGroupedValuesRequestBody(StrictModel):
    filter_: RetrieveLatestMetricGroupedValuesRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
    group_by: RetrieveLatestMetricGroupedValuesRequestBodyGroupBy = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy")
class RetrieveLatestMetricGroupedValuesRequest(StrictModel):
    """Retrieves the latest values for an aggregating metric grouped by a specified dimension such as organization, repository, or a metric-specific dimension like category or severity. Not compatible with accumulating metrics such as fixed issues."""
    path: RetrieveLatestMetricGroupedValuesRequestPath
    body: RetrieveLatestMetricGroupedValuesRequestBody

# Operation: get_metric_period_value
class RetrieveValueForPeriodRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, specified as a short identifier code.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The unique name of the metric to retrieve. Use the readyMetricsForOrganization operation to list all available metric names for the organization.")
class RetrieveValueForPeriodRequestBodyFilterEntityFilter(StrictModel):
    repositories: list[str] | None = Field(default=None, validation_alias="repositories", serialization_alias="repositories", description="Optional list of repository names to scope the metric retrieval. When omitted, the metric is calculated across all repositories in the organization.")
    segment_ids: list[int] | None = Field(default=None, validation_alias="segmentIds", serialization_alias="segmentIds", description="Optional list of segment IDs to filter the metric data by predefined organizational segments.")
class RetrieveValueForPeriodRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="Optional list of dimension filters to narrow the metric data by specific dimensional criteria.")
    entity_filter: RetrieveValueForPeriodRequestBodyFilterEntityFilter | None = Field(default=None, validation_alias="entityFilter", serialization_alias="entityFilter")
class RetrieveValueForPeriodRequestBody(StrictModel):
    date: str = Field(default=..., description="The start date of the period for which to retrieve the metric value, in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    period: Literal["day", "week", "month"] = Field(default=..., description="The granularity of the time period to retrieve the metric for, determining how the start date is interpreted and the duration of the window.")
    filter_: RetrieveValueForPeriodRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RetrieveValueForPeriodRequest(StrictModel):
    """Retrieves the value of a specific organization metric for a given time period, identified by its start date. Aggregating metrics return the average value for the period, while accumulating metrics return the total historical sum."""
    path: RetrieveValueForPeriodRequestPath
    body: RetrieveValueForPeriodRequestBody

# Operation: get_grouped_metric_values_for_period
class RetrieveGroupedValuesForPeriodRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The metric to retrieve values for. Use the readyMetricsForOrganization endpoint to list all available metric names for your organization.")
class RetrieveGroupedValuesForPeriodRequestBodyFilterEntityFilter(StrictModel):
    repositories: list[str] | None = Field(default=None, validation_alias="repositories", serialization_alias="repositories", description="List of repository names to scope the metric results to. When omitted, results include all repositories in the organization.")
    segment_ids: list[int] | None = Field(default=None, validation_alias="segmentIds", serialization_alias="segmentIds", description="List of segment identifiers to filter the metric results by. When omitted, no segment filtering is applied.")
class RetrieveGroupedValuesForPeriodRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="List of dimension filter values to narrow metric results to specific dimension members. Items should match valid dimension values for the requested metric.")
    entity_filter: RetrieveGroupedValuesForPeriodRequestBodyFilterEntityFilter | None = Field(default=None, validation_alias="entityFilter", serialization_alias="entityFilter")
class RetrieveGroupedValuesForPeriodRequestBodyGroupBy(StrictModel):
    group_by: list[str] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="Dimension by which to group the returned metric values. Accepts 'organization', 'repository', or a metric-specific dimension. For OpenIssues, NewIssues, and FixedIssues, valid dimensions are 'category' and 'severity'.")
    sort_direction: str | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Direction in which to sort the returned grouped values, either ascending or descending.")
    limit: int | None = Field(default=None, validation_alias="limit", serialization_alias="limit", description="Maximum number of grouped value entries to return in the response.")
class RetrieveGroupedValuesForPeriodRequestBody(StrictModel):
    date: str = Field(default=..., description="The start date of the period for which to retrieve metric values, specified in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    period: Literal["day", "week", "month"] = Field(default=..., description="The granularity of the time period to retrieve metric values for, relative to the provided start date.")
    filter_: RetrieveGroupedValuesForPeriodRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
    group_by: RetrieveGroupedValuesForPeriodRequestBodyGroupBy = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy")
class RetrieveGroupedValuesForPeriodRequest(StrictModel):
    """Retrieves metric values for a specific time period, grouped by a chosen dimension such as organization, repository, or a metric-specific dimension. Aggregating metrics return averages while accumulating metrics return sums representing total historical change."""
    path: RetrieveGroupedValuesForPeriodRequestPath
    body: RetrieveGroupedValuesForPeriodRequestBody

# Operation: get_metric_time_range_values
class RetrieveTimerangeMetricValuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The metric to retrieve values for. Use the readyMetricsForOrganization endpoint to discover all available metric names for your organization.")
class RetrieveTimerangeMetricValuesRequestBodyFilterEntityFilter(StrictModel):
    repositories: list[str] | None = Field(default=None, validation_alias="repositories", serialization_alias="repositories", description="List of repository names to scope the metric results to. When omitted, results cover all repositories in the organization.")
    segment_ids: list[int] | None = Field(default=None, validation_alias="segmentIds", serialization_alias="segmentIds", description="List of segment IDs to filter the metric results by. When omitted, no segment filtering is applied.")
class RetrieveTimerangeMetricValuesRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="List of dimension filters to narrow metric results to specific dimension values. Valid dimensions depend on the requested metric.")
    entity_filter: RetrieveTimerangeMetricValuesRequestBodyFilterEntityFilter | None = Field(default=None, validation_alias="entityFilter", serialization_alias="entityFilter")
class RetrieveTimerangeMetricValuesRequestBodyGroupBy(StrictModel):
    group_by: list[str] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="Specifies how results are grouped. Accepted values are `organization`, `repository`, or a metric-specific dimension (e.g., `category` or `severity` for issue-related metrics). Order of items is not significant.")
    sort_direction: str | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Controls the sort direction of the returned results. Applies to the ordering of grouped or time-series data.")
    limit: int | None = Field(default=None, validation_alias="limit", serialization_alias="limit", description="Maximum number of results to return. When omitted, the backend applies a default limit.")
class RetrieveTimerangeMetricValuesRequestBody(StrictModel):
    period: Literal["day", "week", "month"] | None = Field(default=None, description="Time granularity for grouping metric values. When omitted, the backend selects a default granularity based on the requested time range.")
    from_: dict | None = Field(default=None, validation_alias="from", serialization_alias="from", json_schema_extra={'format': 'date-time'})
    to: str | None = Field(default=None, json_schema_extra={'format': 'date-time'})
    filter_: RetrieveTimerangeMetricValuesRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
    group_by: RetrieveTimerangeMetricValuesRequestBodyGroupBy = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy")
class RetrieveTimerangeMetricValuesRequest(StrictModel):
    """Retrieves time-series values for a specific metric within an organization, grouped by period and optionally by repository, organization, or a metric-specific dimension. Supports filtering by repositories or segments and controlling time granularity via the period parameter."""
    path: RetrieveTimerangeMetricValuesRequestPath
    body: RetrieveTimerangeMetricValuesRequestBody

# Operation: list_ready_enterprise_metrics
class ReadyMetricsForEnterpriseRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the enterprise. Specifies which version control platform to target.")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The unique slug (URL-friendly name) identifying the enterprise whose ready metrics are being retrieved.")
class ReadyMetricsForEnterpriseRequest(StrictModel):
    """Retrieves the list of metrics that have completed data collection for each organization within a specified enterprise. Useful for determining which metrics are available and ready to query before fetching detailed analytics."""
    path: ReadyMetricsForEnterpriseRequestPath

# Operation: get_latest_enterprise_metric_values
class RetrieveLatestMetricValueForEnterpriseRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the enterprise.")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The name of the aggregating metric to retrieve latest values for. Use the readyMetricsForOrganization endpoint to discover all available metric names.")
class RetrieveLatestMetricValueForEnterpriseRequestBody(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="Optional list of dimension filters to narrow the metric results. Each item specifies a dimension constraint to apply when retrieving metric values across organizations.")
class RetrieveLatestMetricValueForEnterpriseRequest(StrictModel):
    """Retrieves the most recent value of a specified aggregating metric (e.g., open issues) for every organization within an enterprise. Note: this endpoint only supports aggregating metrics and does not work for accumulating metrics such as fixed issues."""
    path: RetrieveLatestMetricValueForEnterpriseRequestPath
    body: RetrieveLatestMetricValueForEnterpriseRequestBody | None = None

# Operation: list_enterprise_metric_latest_values_grouped
class RetrieveLatestMetricGroupedValuesForEnterpriseRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the enterprise.")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The name of the metric to retrieve latest grouped values for. Must be a non-accumulating metric; use the ready metrics endpoint to discover available metric names.")
class RetrieveLatestMetricGroupedValuesForEnterpriseRequestBodyGroupBy(StrictModel):
    group_by: list[str] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="One or more grouping dimensions that determine how results are aggregated. Accepted values are `organization` or a valid metric dimension; for OpenIssues, NewIssues, and FixedIssues the supported dimensions are `category` and `severity`. Grouping by `repository` is not allowed.")
    sort_direction: str | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Direction in which the grouped results are sorted, either ascending or descending.")
    limit: int | None = Field(default=None, validation_alias="limit", serialization_alias="limit", description="Maximum number of grouped result entries to return.")
class RetrieveLatestMetricGroupedValuesForEnterpriseRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="List of dimension values used to filter the grouped results, restricting output to only the specified dimension entries.")
class RetrieveLatestMetricGroupedValuesForEnterpriseRequestBody(StrictModel):
    group_by: RetrieveLatestMetricGroupedValuesForEnterpriseRequestBodyGroupBy = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy")
    filter_: RetrieveLatestMetricGroupedValuesForEnterpriseRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RetrieveLatestMetricGroupedValuesForEnterpriseRequest(StrictModel):
    """Retrieves the latest values of a non-accumulating aggregating metric for all organizations in an enterprise, grouped by a specified dimension such as organization, category, or severity. Grouping by repository is not supported, and accumulating metrics (e.g., fixed issues) are excluded."""
    path: RetrieveLatestMetricGroupedValuesForEnterpriseRequestPath
    body: RetrieveLatestMetricGroupedValuesForEnterpriseRequestBody

# Operation: get_enterprise_metric_by_period
class RetrieveValueForPeriodForEnterpriseRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the enterprise.")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The URL-friendly slug name of the enterprise to retrieve metrics for.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The name of the metric to retrieve. Use the list available metrics operation to discover valid metric names.")
class RetrieveValueForPeriodForEnterpriseRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="Optional list of dimension filters to narrow results. Each item specifies a dimension and value to filter by; order is not significant.")
class RetrieveValueForPeriodForEnterpriseRequestBody(StrictModel):
    date: str = Field(default=..., description="The start date of the period to retrieve, in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    period: Literal["day", "week", "month"] = Field(default=..., description="The granularity of the time period to aggregate metric values over. Must be one of: day, week, or month.")
    filter_: RetrieveValueForPeriodForEnterpriseRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RetrieveValueForPeriodForEnterpriseRequest(StrictModel):
    """Retrieves metric values for each organization within an enterprise for a specific time period, identified by its start date. Aggregating metrics return the average value, while accumulating metrics return the total historical sum."""
    path: RetrieveValueForPeriodForEnterpriseRequestPath
    body: RetrieveValueForPeriodForEnterpriseRequestBody

# Operation: get_enterprise_metric_grouped_by_period
class RetrieveGroupedValuesForPeriodForEnterpriseRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the enterprise.")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The name of the metric to retrieve data for. Use the list available metrics operation to discover valid metric names.")
class RetrieveGroupedValuesForPeriodForEnterpriseRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="Optional list of dimension filters to narrow results. Each item specifies a dimension and value to filter by, limiting the data returned to matching entries.")
class RetrieveGroupedValuesForPeriodForEnterpriseRequestBodyGroupBy(StrictModel):
    group_by: list[str] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="Specifies how results should be grouped. Accepted values are `organization` or a valid dimension for the requested metric (e.g., `category` or `severity` for issue-related metrics). Grouping by `repository` is not supported.")
    sort_direction: str | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Controls the sort order of the returned values, either ascending or descending.")
    limit: int | None = Field(default=None, validation_alias="limit", serialization_alias="limit", description="Maximum number of grouped result entries to return.")
class RetrieveGroupedValuesForPeriodForEnterpriseRequestBody(StrictModel):
    date: str = Field(default=..., description="The start date and time of the period to retrieve, in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    period: Literal["day", "week", "month"] = Field(default=..., description="The granularity of the time period to retrieve data for, determining whether the period spans a day, week, or month from the specified start date.")
    filter_: RetrieveGroupedValuesForPeriodForEnterpriseRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
    group_by: RetrieveGroupedValuesForPeriodForEnterpriseRequestBodyGroupBy = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy")
class RetrieveGroupedValuesForPeriodForEnterpriseRequest(StrictModel):
    """Retrieves metric values grouped by a specified dimension (such as organization or a metric-specific dimension) for all organizations in an enterprise, scoped to a single time period identified by its start date. Aggregating metrics return averages while accumulating metrics return sums representing total historical change."""
    path: RetrieveGroupedValuesForPeriodForEnterpriseRequestPath
    body: RetrieveGroupedValuesForPeriodForEnterpriseRequestBody

# Operation: get_enterprise_metric_timeseries
class RetrieveTimerangeMetricValuesForEnterpriseRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the enterprise.")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The URL-friendly slug name that uniquely identifies the enterprise.")
    metric_name: str = Field(default=..., validation_alias="metricName", serialization_alias="metricName", description="The metric to retrieve time-series data for. Use the readyMetricsForOrganization endpoint to list all available metric names.")
class RetrieveTimerangeMetricValuesForEnterpriseRequestBodyFilter(StrictModel):
    dimensions_filter: list[DimensionsFilter] | None = Field(default=None, validation_alias="dimensionsFilter", serialization_alias="dimensionsFilter", description="Optional list of dimension filters to narrow results. Each item should specify a dimension and its filter value relevant to the requested metric.")
class RetrieveTimerangeMetricValuesForEnterpriseRequestBodyGroupBy(StrictModel):
    group_by: list[str] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="Specifies how results are grouped in addition to period date. Accepted values are `organization` or a valid dimension for the metric (e.g., `category` or `severity` for OpenIssues, NewIssues, and FixedIssues). Grouping by `repository` is not supported.")
    sort_direction: str | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Controls the sort order of returned results. Determines whether values are sorted in ascending or descending order.")
    limit: int | None = Field(default=None, validation_alias="limit", serialization_alias="limit", description="Maximum number of results to return. Use to cap the size of the response payload.")
class RetrieveTimerangeMetricValuesForEnterpriseRequestBody(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="Start of the time range for which metric values are retrieved, inclusive. Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    to: str = Field(default=..., description="End of the time range for which metric values are retrieved, inclusive. Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    period: Literal["day", "week", "month"] | None = Field(default=None, description="Time granularity for grouping returned data points. If omitted, the backend selects a default granularity based on the requested range.")
    filter_: RetrieveTimerangeMetricValuesForEnterpriseRequestBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
    group_by: RetrieveTimerangeMetricValuesForEnterpriseRequestBodyGroupBy = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy")
class RetrieveTimerangeMetricValuesForEnterpriseRequest(StrictModel):
    """Retrieves time-series values for a specific metric across all organizations in an enterprise, grouped by period and optionally by organization or a metric dimension. Aggregating metrics return averages while accumulating metrics return sums; time granularity is controlled via the period parameter."""
    path: RetrieveTimerangeMetricValuesForEnterpriseRequestPath
    body: RetrieveTimerangeMetricValuesForEnterpriseRequestBody

# Operation: list_repository_files
class ListFilesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears under the organization on the Git provider.")
class ListFilesRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Name of a branch enabled on Codacy to scope the file analysis results. Defaults to the repository's main branch if omitted.")
    search: str | None = Field(default=None, description="Filters the returned files to those whose relative path contains this string, enabling partial-match searches.")
    sort: str | None = Field(default=None, description="Field by which to sort the file list. Accepted values are filename, issues, grade, duplication, complexity, and coverage.")
    direction: str | None = Field(default=None, description="Order in which to return sorted results — ascending (asc) or descending (desc).")
    limit: int | None = Field(default=None, description="Maximum number of files to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListFilesRequest(StrictModel):
    """Retrieves the most recent analysis results for all tracked files in a repository, equivalent to the Codacy Files page view. Ignored files are excluded from results."""
    path: ListFilesRequestPath
    query: ListFilesRequestQuery | None = None

# Operation: list_ignored_files
class ListIgnoredFilesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class ListIgnoredFilesRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="The name of a branch enabled on Codacy to scope the ignored files results; defaults to the main branch configured in Codacy repository settings if omitted.")
    search: str | None = Field(default=None, description="A string used to filter results, returning only files whose relative path contains this value anywhere within it.")
    limit: int | None = Field(default=None, description="The maximum number of ignored files to return in a single response, between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListIgnoredFilesRequest(StrictModel):
    """Retrieves the most recently recorded list of ignored files for a repository on Codacy. When a Codacy configuration file is present, the ignored files list is read-only and reflects what was excluded during the last analysis."""
    path: ListIgnoredFilesRequestPath
    query: ListIgnoredFilesRequestQuery | None = None

# Operation: get_file_analysis
class GetFileWithAnalysisRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository, such as gh for GitHub, gl for GitLab, or bb for Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique numeric identifier for a file tied to a specific commit, used to retrieve its analysis and coverage data.", json_schema_extra={'format': 'int64'})
class GetFileWithAnalysisRequest(StrictModel):
    """Retrieves analysis information and coverage metrics for a specific file in a repository. Returns quality insights and coverage data associated with the file at a particular commit."""
    path: GetFileWithAnalysisRequestPath

# Operation: list_file_clones
class GetFileClonesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique numeric identifier for a file tied to a specific commit. This ID is commit-scoped and can be obtained from file listing endpoints.", json_schema_extra={'format': 'int64'})
class GetFileClonesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of duplicate code block results to return. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetFileClonesRequest(StrictModel):
    """Retrieves all duplicated code blocks (clones) detected within a specific file in a repository. Useful for identifying code duplication issues at the file level."""
    path: GetFileClonesRequestPath
    query: GetFileClonesRequestQuery | None = None

# Operation: list_file_issues
class GetFileIssuesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier for a file tied to a specific commit. This ID is commit-scoped and may differ across commits for the same file path.", json_schema_extra={'format': 'int64'})
class GetFileIssuesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of issues to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetFileIssuesRequest(StrictModel):
    """Retrieves the list of code quality issues found in a specific file within a repository. Results are scoped to the file identified by its commit-specific file ID."""
    path: GetFileIssuesRequestPath
    query: GetFileIssuesRequestQuery | None = None

# Operation: get_ai_risk_checklist
class GetAiRiskCheckListRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
class GetAiRiskCheckListRequest(StrictModel):
    """Retrieves the AI risk checklist for a specified organization on a Git provider, summarizing potential security, compliance, and quality risks identified by AI analysis."""
    path: GetAiRiskCheckListRequestPath

# Operation: list_coding_standards
class ListCodingStandardsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, used to identify which platform to query.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider, used to scope the coding standards lookup.")
class ListCodingStandardsRequest(StrictModel):
    """Retrieves all coding standards for a specified organization, including both active and draft coding standards. Useful for auditing or managing code quality rules across an organization."""
    path: ListCodingStandardsRequestPath

# Operation: create_coding_standard
class CreateCodingStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class CreateCodingStandardRequestQuery(StrictModel):
    source_repository: str | None = Field(default=None, validation_alias="sourceRepository", serialization_alias="sourceRepository", description="Name of an existing repository within the same organization to use as a template for tool and language settings when creating the new coding standard.")
    source_coding_standard: int | None = Field(default=None, validation_alias="sourceCodingStandard", serialization_alias="sourceCodingStandard", description="Numeric identifier of an existing coding standard to use as a template, carrying over its enabled repositories and default coding standard status to the new one.", json_schema_extra={'format': 'int64'})
class CreateCodingStandardRequestBody(StrictModel):
    """Details of the coding standard to create"""
    name: str = Field(default=..., description="Human-readable name for the new coding standard, used to identify it within the organization.")
    languages: list[str] = Field(default=..., description="List of programming languages the new coding standard will cover. Order is not significant; each item should be a supported language name.")
class CreateCodingStandardRequest(StrictModel):
    """Creates a new draft coding standard for an organization, optionally using an existing repository or coding standard as a template. The draft must be promoted to become effective; use promoteDraftCodingStandard to complete that step."""
    path: CreateCodingStandardRequestPath
    query: CreateCodingStandardRequestQuery | None = None
    body: CreateCodingStandardRequestBody

# Operation: create_compliance_standard
class CreateComplianceStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class CreateComplianceStandardRequestBody(StrictModel):
    """Details of the compliance standard to create"""
    name: str = Field(default=..., description="A human-readable display name for the compliance standard being created.")
    compliance_type: Literal["ai-risk"] = Field(default=..., validation_alias="complianceType", serialization_alias="complianceType", description="The category of compliance standard to create. Currently supports AI risk compliance, which enforces policies around AI-generated code usage.")
class CreateComplianceStandardRequest(StrictModel):
    """Creates a new compliance standard for the specified organization on a Git provider. Use this to establish compliance frameworks, such as AI risk policies, that govern code quality and usage rules across the organization."""
    path: CreateComplianceStandardRequestPath
    body: CreateComplianceStandardRequestBody

# Operation: create_coding_standard_from_preset
class CreateCodingStandardPresetRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class CreateCodingStandardPresetRequestBodyPresets(StrictModel):
    bug_risk: int = Field(default=..., validation_alias="bugRisk", serialization_alias="bugRisk", description="Preset level for bug risk rules, controlling how strictly potential bugs and error-prone patterns are flagged. Accepts values from 1 (least strict) to 4 (most strict).", ge=1, le=4, json_schema_extra={'format': 'int32'})
    security: int = Field(default=..., validation_alias="security", serialization_alias="security", description="Preset level for security rules, controlling how strictly security vulnerabilities and unsafe coding patterns are flagged. Accepts values from 1 (least strict) to 4 (most strict).", ge=1, le=4, json_schema_extra={'format': 'int32'})
    best_practices: int = Field(default=..., validation_alias="bestPractices", serialization_alias="bestPractices", description="Preset level for best practice rules, controlling how strictly deviations from recommended coding conventions are flagged. Accepts values from 1 (least strict) to 4 (most strict).", ge=1, le=4, json_schema_extra={'format': 'int32'})
    code_style: int = Field(default=..., validation_alias="codeStyle", serialization_alias="codeStyle", description="Preset level for code style rules, controlling how strictly formatting and stylistic inconsistencies are flagged. Accepts values from 1 (least strict) to 4 (most strict).", ge=1, le=4, json_schema_extra={'format': 'int32'})
    documentation: int = Field(default=..., validation_alias="documentation", serialization_alias="documentation", description="Preset level for documentation rules, controlling how strictly missing or inadequate code documentation is flagged. Accepts values from 1 (least strict) to 4 (most strict).", ge=1, le=4, json_schema_extra={'format': 'int32'})
class CreateCodingStandardPresetRequestBody(StrictModel):
    """Details of the coding standard to create"""
    name: str | None = Field(default=None, description="A human-readable label for the new coding standard to help identify it within the organization.")
    is_default: bool = Field(default=..., validation_alias="isDefault", serialization_alias="isDefault", description="When set to true, this coding standard will automatically become the default applied to all repositories in the organization.")
    presets: CreateCodingStandardPresetRequestBodyPresets
class CreateCodingStandardPresetRequest(StrictModel):
    """Creates a new coding standard for an organization by selecting preset severity levels across key code quality categories. Optionally sets the new standard as the organization's default."""
    path: CreateCodingStandardPresetRequestPath
    body: CreateCodingStandardPresetRequestBody

# Operation: get_coding_standard
class GetCodingStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the coding standard to retrieve, as assigned by Codacy.", json_schema_extra={'format': 'int64'})
class GetCodingStandardRequest(StrictModel):
    """Retrieves the details of a specific coding standard within an organization, including its configured rules and settings. Useful for inspecting or auditing code quality policies applied to repositories."""
    path: GetCodingStandardRequestPath

# Operation: delete_coding_standard
class DeleteCodingStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the coding standard to delete, as returned when the coding standard was created or listed.", json_schema_extra={'format': 'int64'})
class DeleteCodingStandardRequest(StrictModel):
    """Permanently deletes a coding standard from the specified organization. This action is irreversible and removes all associated rule configurations."""
    path: DeleteCodingStandardRequestPath

# Operation: duplicate_coding_standard
class DuplicateCodingStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the coding standard to duplicate.", json_schema_extra={'format': 'int64'})
class DuplicateCodingStandardRequest(StrictModel):
    """Creates a copy of an existing coding standard within the specified organization, preserving all rules and configurations from the original. Useful for creating variations of a standard without modifying the source."""
    path: DuplicateCodingStandardRequestPath

# Operation: list_coding_standard_tools
class ListCodingStandardToolsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the coding standard whose tools should be listed.", json_schema_extra={'format': 'int64'})
class ListCodingStandardToolsRequest(StrictModel):
    """Retrieves all tools configured within a specific coding standard for an organization. Useful for auditing which static analysis tools are enabled and their associated rule configurations."""
    path: ListCodingStandardToolsRequestPath

# Operation: set_default_coding_standard
class SetDefaultCodingStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the coding standard to set or unset as the default.", json_schema_extra={'format': 'int64'})
class SetDefaultCodingStandardRequestBody(StrictModel):
    is_default: bool = Field(default=..., validation_alias="isDefault", serialization_alias="isDefault", description="When true, designates this coding standard as the organization's default; when false, removes its default status.")
class SetDefaultCodingStandardRequest(StrictModel):
    """Sets or unsets a specific coding standard as the default for an organization, controlling which coding standard is automatically applied to new projects."""
    path: SetDefaultCodingStandardRequestPath
    body: SetDefaultCodingStandardRequestBody

# Operation: list_coding_standard_tool_patterns
class ListCodingStandardPatternsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The short identifier for the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The numeric identifier of the coding standard to retrieve patterns from.", json_schema_extra={'format': 'int64'})
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID identifying the specific tool whose patterns should be listed.")
class ListCodingStandardPatternsRequestQuery(StrictModel):
    languages: str | None = Field(default=None, description="Comma-separated list of programming language names to filter patterns by; only patterns applicable to the specified languages are returned.")
    categories: str | None = Field(default=None, description="Comma-separated list of pattern categories to filter by. Valid values are `Security`, `ErrorProne`, `CodeStyle`, `Compatibility`, `UnusedCode`, `Complexity`, `Comprehensibility`, `Documentation`, `BestPractice`, and `Performance`.")
    severity_levels: str | None = Field(default=None, validation_alias="severityLevels", serialization_alias="severityLevels", description="Comma-separated list of severity levels to filter by. Valid values are `Error`, `High`, `Warning`, and `Info`.")
    tags: str | None = Field(default=None, description="Comma-separated list of pattern tags to filter by; only patterns matching at least one of the specified tags are returned.")
    search: str | None = Field(default=None, description="A search string used to filter patterns by name or description; returns patterns whose metadata contains this value.")
    enabled: bool | None = Field(default=None, description="When set to `true`, returns only enabled patterns; when set to `false`, returns only disabled patterns. Omit to return patterns regardless of enabled status.")
    recommended: bool | None = Field(default=None, description="When set to `true`, returns only recommended patterns; when set to `false`, returns only non-recommended patterns. Omit to return patterns regardless of recommended status.")
    sort: str | None = Field(default=None, description="The field by which to sort the returned patterns. Valid values are `category`, `recommended`, and `severity`.")
    direction: str | None = Field(default=None, description="The direction in which results are sorted — `asc` for ascending or `desc` for descending.")
    limit: int | None = Field(default=None, description="Maximum number of patterns to return per request. Must be between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListCodingStandardPatternsRequest(StrictModel):
    """Retrieves the list of code patterns configured for a specific tool within a coding standard, supporting filtering by language, category, severity, tags, and enabled/recommended status."""
    path: ListCodingStandardPatternsRequestPath
    query: ListCodingStandardPatternsRequestQuery | None = None

# Operation: get_coding_standard_tool_patterns_overview
class CodingStandardToolPatternsOverviewRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The numeric identifier of the coding standard whose tool patterns overview is being requested.", json_schema_extra={'format': 'int64'})
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID uniquely identifying the tool within the coding standard.")
class CodingStandardToolPatternsOverviewRequestQuery(StrictModel):
    languages: str | None = Field(default=None, description="Comma-separated list of programming language names to restrict the overview to patterns applicable to those languages.")
    categories: str | None = Field(default=None, description="Comma-separated list of pattern categories to filter by. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance.")
    severity_levels: str | None = Field(default=None, validation_alias="severityLevels", serialization_alias="severityLevels", description="Comma-separated list of severity levels to filter by. Valid values are Error, High, Warning, and Info.")
    tags: str | None = Field(default=None, description="Comma-separated list of pattern tags to filter results to only patterns associated with those tags.")
    search: str | None = Field(default=None, description="A search string used to filter patterns by matching against pattern names or descriptions.")
    enabled: bool | None = Field(default=None, description="When set to true, returns only enabled patterns; when set to false, returns only disabled patterns. Omit to return patterns regardless of enabled state.")
    recommended: bool | None = Field(default=None, description="When set to true, returns only patterns marked as recommended; when set to false, returns only non-recommended patterns. Omit to return patterns regardless of recommended status.")
class CodingStandardToolPatternsOverviewRequest(StrictModel):
    """Retrieves a summary overview of code patterns for a specific tool within a coding standard, showing counts and distribution across categories, severities, and statuses. Supports filtering by language, category, severity, tags, search term, enabled state, and recommended status."""
    path: CodingStandardToolPatternsOverviewRequestPath
    query: CodingStandardToolPatternsOverviewRequestQuery | None = None

# Operation: bulk_update_coding_standard_tool_patterns
class UpdateCodingStandardPatternsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Exact name of the organization as it appears on the Git provider.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="Numeric identifier of the coding standard to update patterns within.", json_schema_extra={'format': 'int64'})
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="UUID of the tool whose code patterns will be updated within the coding standard.")
class UpdateCodingStandardPatternsRequestQuery(StrictModel):
    languages: str | None = Field(default=None, description="Comma-separated list of programming language names to restrict which patterns are updated.")
    categories: str | None = Field(default=None, description="Comma-separated list of pattern categories to restrict which patterns are updated. Valid values are Security, ErrorProne, CodeStyle, Compatibility, UnusedCode, Complexity, Comprehensibility, Documentation, BestPractice, and Performance.")
    severity_levels: str | None = Field(default=None, validation_alias="severityLevels", serialization_alias="severityLevels", description="Comma-separated list of severity levels to restrict which patterns are updated. Valid values are Error, High, Warning, and Info.")
    tags: str | None = Field(default=None, description="Comma-separated list of pattern tags to restrict which patterns are updated.")
    search: str | None = Field(default=None, description="Free-text string used to filter patterns by name or description before applying the update.")
    recommended: bool | None = Field(default=None, description="Restricts the update to patterns based on their recommended status; true targets only recommended patterns, false targets only non-recommended patterns.")
class UpdateCodingStandardPatternsRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="Whether to enable or disable the matched code patterns; true enables them and false disables them.")
class UpdateCodingStandardPatternsRequest(StrictModel):
    """Enable or disable multiple code patterns for a specific tool within a coding standard. Use optional filters to target a subset of patterns by language, category, severity, tags, or search term, or omit all filters to apply the update to every pattern in the tool."""
    path: UpdateCodingStandardPatternsRequestPath
    query: UpdateCodingStandardPatternsRequestQuery | None = None
    body: UpdateCodingStandardPatternsRequestBody

# Operation: configure_coding_standard_tool
class UpdateCodingStandardToolConfigurationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The numeric identifier of the draft coding standard to configure. Only draft coding standards can be updated.", json_schema_extra={'format': 'int64'})
    tool_uuid: str = Field(default=..., validation_alias="toolUuid", serialization_alias="toolUuid", description="The UUID uniquely identifying the tool to configure within the coding standard.")
class UpdateCodingStandardToolConfigurationRequest(StrictModel):
    """Toggle a tool's enabled status and update its code patterns within a draft coding standard. Only the code patterns included in the request body are modified, with a maximum of 1000 code patterns configurable per call."""
    path: UpdateCodingStandardToolConfigurationRequestPath

# Operation: list_coding_standard_repositories
class ListCodingStandardRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the coding standard whose associated repositories should be listed.", json_schema_extra={'format': 'int64'})
class ListCodingStandardRepositoriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100; defaults to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListCodingStandardRepositoriesRequest(StrictModel):
    """Retrieves the list of repositories currently using a specific coding standard within an organization. Useful for auditing which repositories are governed by a given set of coding rules."""
    path: ListCodingStandardRepositoriesRequestPath
    query: ListCodingStandardRepositoriesRequestQuery | None = None

# Operation: update_coding_standard_repositories
class ApplyCodingStandardToRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="Unique numeric identifier of the coding standard to update.", json_schema_extra={'format': 'int64'})
class ApplyCodingStandardToRepositoriesRequestBody(StrictModel):
    link: list[str] = Field(default=..., description="List of repository names to associate with the coding standard. Order is not significant; each item should be the repository's name as it appears on the Git provider.")
    unlink: list[str] = Field(default=..., description="List of repository names to dissociate from the coding standard. Order is not significant; each item should be the repository's name as it appears on the Git provider.")
class ApplyCodingStandardToRepositoriesRequest(StrictModel):
    """Links or unlinks a set of repositories to a specified coding standard within an organization. If the coding standard is in draft state, changes take effect only upon promoting it."""
    path: ApplyCodingStandardToRepositoriesRequestPath
    body: ApplyCodingStandardToRepositoriesRequestBody

# Operation: set_default_gate_policy
class SetDefaultGatePolicyRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform.")
    gate_policy_id: int = Field(default=..., validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="The unique numeric identifier of the gate policy to designate as the default.", json_schema_extra={'format': 'int64'})
class SetDefaultGatePolicyRequest(StrictModel):
    """Sets a specified gate policy as the default for an organization, ensuring it is applied automatically when no other policy is explicitly assigned."""
    path: SetDefaultGatePolicyRequestPath

# Operation: set_default_gate_policy_to_codacy_builtin
class SetCodacyDefaultRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., GitHub, GitLab, or Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
class SetCodacyDefaultRequest(StrictModel):
    """Sets the built-in Codacy gate policy as the default quality gate for the specified organization, replacing any previously configured default policy."""
    path: SetCodacyDefaultRequestPath

# Operation: get_gate_policy
class GetGatePolicyRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider platform.")
    gate_policy_id: int = Field(default=..., validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="The unique numeric identifier of the gate policy to retrieve.", json_schema_extra={'format': 'int64'})
class GetGatePolicyRequest(StrictModel):
    """Retrieves the details of a specific gate policy within an organization. Gate policies define quality and security criteria that must be met before code changes are accepted."""
    path: GetGatePolicyRequestPath

# Operation: update_gate_policy
class UpdateGatePolicyRequestPath(StrictModel):
    provider: str = Field(default=..., description="The short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    gate_policy_id: int = Field(default=..., validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="The unique numeric identifier of the gate policy to update.", json_schema_extra={'format': 'int64'})
class UpdateGatePolicyRequestBodySettingsIssueThreshold(StrictModel):
    threshold: int = Field(default=..., validation_alias="threshold", serialization_alias="threshold", description="The maximum number of new issues allowed before the quality gate fails. Must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(default=None, validation_alias="minimumSeverity", serialization_alias="minimumSeverity", description="The minimum severity level of issues that count toward the issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical.")
class UpdateGatePolicyRequestBodySettings(StrictModel):
    security_issue_threshold: int | None = Field(default=None, validation_alias="securityIssueThreshold", serialization_alias="securityIssueThreshold", description="The maximum number of new security issues allowed before the quality gate fails. Must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    security_issue_minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(default=None, validation_alias="securityIssueMinimumSeverity", serialization_alias="securityIssueMinimumSeverity", description="The minimum severity level of security issues that count toward the security issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical.")
    duplication_threshold: int | None = Field(default=None, validation_alias="duplicationThreshold", serialization_alias="duplicationThreshold", description="The maximum number of new duplicated code blocks allowed before the quality gate fails.", json_schema_extra={'format': 'int32'})
    coverage_threshold_with_decimals: float | None = Field(default=None, validation_alias="coverageThresholdWithDecimals", serialization_alias="coverageThresholdWithDecimals", description="The minimum required change in coverage percentage; the gate fails if coverage varies by less than this value. Accepts negative values to allow coverage decreases up to a specified amount, with a maximum value of 1.00 (representing 100%).", json_schema_extra={'format': 'double'})
    diff_coverage_threshold: int | None = Field(default=None, validation_alias="diffCoverageThreshold", serialization_alias="diffCoverageThreshold", description="The minimum required diff coverage percentage; the gate fails if diff coverage falls below this value. Must be between 0 and 100 inclusive.", ge=0, le=100, json_schema_extra={'format': 'int32'})
    complexity_threshold: int | None = Field(default=None, validation_alias="complexityThreshold", serialization_alias="complexityThreshold", description="The maximum allowed complexity value introduced by new code; the gate fails if this threshold is exceeded. Must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    issue_threshold: UpdateGatePolicyRequestBodySettingsIssueThreshold = Field(default=..., validation_alias="issueThreshold", serialization_alias="issueThreshold")
class UpdateGatePolicyRequestBody(StrictModel):
    """The new values for the name, default status, or quality gates of the gate policy"""
    gate_policy_name: str | None = Field(default=None, validation_alias="gatePolicyName", serialization_alias="gatePolicyName", description="The human-readable display name for the gate policy.")
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="When true, this gate policy becomes the default applied to all repositories in the organization that do not have an explicitly assigned policy.")
    settings: UpdateGatePolicyRequestBodySettings
class UpdateGatePolicyRequest(StrictModel):
    """Updates an existing quality gate policy for an organization, allowing modification of thresholds, severity filters, and default status. Quality gate policies define the criteria that must be met for a pull request or commit to pass code quality checks."""
    path: UpdateGatePolicyRequestPath
    body: UpdateGatePolicyRequestBody

# Operation: delete_gate_policy
class DeleteGatePolicyRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider for the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    gate_policy_id: int = Field(default=..., validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="The unique numeric identifier of the gate policy to delete.", json_schema_extra={'format': 'int64'})
class DeleteGatePolicyRequest(StrictModel):
    """Permanently deletes a specific gate policy from an organization on the specified Git provider. This action is irreversible and removes all associated policy configurations."""
    path: DeleteGatePolicyRequestPath

# Operation: list_gate_policies
class ListGatePoliciesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider.")
class ListGatePoliciesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of gate policies to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListGatePoliciesRequest(StrictModel):
    """Retrieves all gate policies configured for a specified organization on a Git provider. Gate policies define quality or security gates that govern code merging and deployment workflows."""
    path: ListGatePoliciesRequestPath
    query: ListGatePoliciesRequestQuery | None = None

# Operation: create_gate_policy
class CreateGatePolicyRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class CreateGatePolicyRequestBodySettingsIssueThreshold(StrictModel):
    threshold: int = Field(default=..., validation_alias="threshold", serialization_alias="threshold", description="The maximum number of new issues allowed before the quality gate fails; must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(default=None, validation_alias="minimumSeverity", serialization_alias="minimumSeverity", description="The minimum severity level of issues counted toward the issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical.")
class CreateGatePolicyRequestBodySettings(StrictModel):
    security_issue_threshold: int | None = Field(default=None, validation_alias="securityIssueThreshold", serialization_alias="securityIssueThreshold", description="The maximum number of new security issues allowed before the quality gate fails; must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    security_issue_minimum_severity: Literal["Info", "Warning", "High", "Error"] | None = Field(default=None, validation_alias="securityIssueMinimumSeverity", serialization_alias="securityIssueMinimumSeverity", description="The minimum severity level of security issues counted toward the security issue threshold. Severity levels map to the UI as: Info → Minor, Warning → Medium, High → High, Error → Critical.")
    duplication_threshold: int | None = Field(default=None, validation_alias="duplicationThreshold", serialization_alias="duplicationThreshold", description="The maximum number of new duplicated blocks allowed before the quality gate fails.", json_schema_extra={'format': 'int32'})
    coverage_threshold_with_decimals: float | None = Field(default=None, validation_alias="coverageThresholdWithDecimals", serialization_alias="coverageThresholdWithDecimals", description="The minimum change in coverage percentage required to pass the quality gate; use a negative value to allow coverage to decrease by that amount (e.g., -0.02 allows up to a 2% drop). Must be at most 1.00.", json_schema_extra={'format': 'double'})
    diff_coverage_threshold: int | None = Field(default=None, validation_alias="diffCoverageThreshold", serialization_alias="diffCoverageThreshold", description="The minimum diff coverage percentage required to pass the quality gate; must be between 0 and 100 inclusive.", ge=0, le=100, json_schema_extra={'format': 'int32'})
    complexity_threshold: int | None = Field(default=None, validation_alias="complexityThreshold", serialization_alias="complexityThreshold", description="The maximum cumulative complexity value allowed before the quality gate fails; must be zero or greater.", ge=0, json_schema_extra={'format': 'int32'})
    issue_threshold: CreateGatePolicyRequestBodySettingsIssueThreshold = Field(default=..., validation_alias="issueThreshold", serialization_alias="issueThreshold")
class CreateGatePolicyRequestBody(StrictModel):
    """Details of the gate policy to create"""
    gate_policy_name: str = Field(default=..., validation_alias="gatePolicyName", serialization_alias="gatePolicyName", description="A unique, human-readable name to identify this gate policy within the organization.")
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="When true, this policy becomes the default gate policy applied to repositories in the organization that have no explicitly assigned policy.")
    settings: CreateGatePolicyRequestBodySettings
class CreateGatePolicyRequest(StrictModel):
    """Creates a new quality gate policy for an organization on a Git provider, defining thresholds for issues, duplication, coverage, and complexity that must be met for a gate to pass."""
    path: CreateGatePolicyRequestPath
    body: CreateGatePolicyRequestBody

# Operation: sync_organization_name
class SyncOrganizationNameRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization, such as gh for GitHub, gl for GitLab, or bb for Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider, used to locate the correct organization for synchronization.")
class SyncOrganizationNameRequest(StrictModel):
    """Synchronizes the organization's display name in Codacy with the current name from the specified Git provider, ensuring both systems remain consistent."""
    path: SyncOrganizationNameRequestPath

# Operation: check_submodules_enabled
class CheckSubmodulesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider for the organization, such as GitHub, GitLab, or Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
class CheckSubmodulesRequest(StrictModel):
    """Checks whether the submodules option is currently enabled for a specified organization on a Git provider. Useful for verifying organization-level repository settings before performing submodule-dependent operations."""
    path: CheckSubmodulesRequestPath

# Operation: list_gate_policy_repositories
class ListRepositoriesFollowingGatePolicyRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target provider.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization name as it appears on the Git provider.")
    gate_policy_id: int = Field(default=..., validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="The unique numeric identifier of the gate policy whose associated repositories should be listed.", json_schema_extra={'format': 'int64'})
class ListRepositoriesFollowingGatePolicyRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListRepositoriesFollowingGatePolicyRequest(StrictModel):
    """Retrieves all repositories that are following a specific gate policy within an organization. Useful for auditing which repositories are governed by a given quality gate configuration."""
    path: ListRepositoriesFollowingGatePolicyRequestPath
    query: ListRepositoriesFollowingGatePolicyRequestQuery | None = None

# Operation: update_gate_policy_repositories
class ApplyGatePolicyToRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
    gate_policy_id: int = Field(default=..., validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="The unique numeric identifier of the gate policy to which repositories will be linked or unlinked.", json_schema_extra={'format': 'int64'})
class ApplyGatePolicyToRepositoriesRequestBody(StrictModel):
    link: list[str] = Field(default=..., description="List of repository names to associate with the gate policy. Order is not significant; each item should be the repository's name as it appears on the Git provider.")
    unlink: list[str] = Field(default=..., description="List of repository names to disassociate from the gate policy. Order is not significant; each item should be the repository's name as it appears on the Git provider.")
class ApplyGatePolicyToRepositoriesRequest(StrictModel):
    """Links or unlinks a set of repositories to a specified gate policy within an organization. Allows simultaneous association and disassociation of repositories in a single request."""
    path: ApplyGatePolicyToRepositoriesRequestPath
    body: ApplyGatePolicyToRepositoriesRequestBody

# Operation: promote_coding_standard
class PromoteDraftCodingStandardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    coding_standard_id: int = Field(default=..., validation_alias="codingStandardId", serialization_alias="codingStandardId", description="The unique numeric identifier of the draft coding standard to promote.", json_schema_extra={'format': 'int64'})
class PromoteDraftCodingStandardRequest(StrictModel):
    """Promotes a draft coding standard to active/effective status for the specified organization, making it the default if it was marked as such. Returns the results of applying the promoted coding standard across the organization's repositories."""
    path: PromoteDraftCodingStandardRequestPath

# Operation: list_repository_api_tokens
class ListRepositoryApiTokensRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization as it appears on the Git provider platform.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
class ListRepositoryApiTokensRequest(StrictModel):
    """Retrieves all API tokens associated with a specific repository in a Codacy organization. These tokens can be used to authenticate API requests scoped to the repository."""
    path: ListRepositoryApiTokensRequestPath

# Operation: create_repository_token
class CreateRepositoryApiTokenRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider platform.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
class CreateRepositoryApiTokenRequest(StrictModel):
    """Creates a new API token scoped to a specific repository, enabling authenticated access to that repository's resources via the Codacy."""
    path: CreateRepositoryApiTokenRequestPath

# Operation: delete_repository_token
class DeleteRepositoryApiTokenRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization and repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider platform.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears under the organization on the Git provider platform.")
    token_id: int = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The numeric identifier of the repository API token to delete. Obtain this ID from the list repository tokens operation.", json_schema_extra={'format': 'int64'})
class DeleteRepositoryApiTokenRequest(StrictModel):
    """Permanently deletes a specific API token associated with a repository by its unique ID. This revokes any access previously granted through that token."""
    path: DeleteRepositoryApiTokenRequestPath

# Operation: list_coverage_reports
class ListCoverageReportsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class ListCoverageReportsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of coverage reports to return, between 1 and 100 inclusive. Defaults to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListCoverageReportsRequest(StrictModel):
    """Retrieves the most recent coverage reports and their statuses for a specified repository. Useful for monitoring code coverage trends and identifying the latest analysis results."""
    path: ListCoverageReportsRequestPath
    query: ListCoverageReportsRequestQuery | None = None

# Operation: list_commit_coverage_reports
class ListCommitCoverageReportsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The full commit UUID or SHA hash that uniquely identifies the commit whose coverage reports should be listed.")
class ListCommitCoverageReportsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of coverage reports to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListCommitCoverageReportsRequest(StrictModel):
    """Retrieves all code coverage reports associated with a specific commit in a repository. Useful for reviewing coverage data uploaded from multiple sources or tools for a given commit."""
    path: ListCommitCoverageReportsRequestPath
    query: ListCommitCoverageReportsRequestQuery | None = None

# Operation: get_commit_coverage_report
class GetCoverageReportRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The UUID or full SHA hash that uniquely identifies the commit whose coverage report is being retrieved.")
    report_uuid: str = Field(default=..., validation_alias="reportUuid", serialization_alias="reportUuid", description="The UUID that uniquely identifies the specific coverage report to retrieve within the commit.")
class GetCoverageReportRequest(StrictModel):
    """Retrieves a specific coverage report and its contents for a given commit in a repository. Use this to inspect detailed coverage data associated with a particular report UUID."""
    path: GetCoverageReportRequestPath

# Operation: get_file_content
class GetFileContentRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name within the specified organization on the Git provider.")
    file_path: str = Field(default=..., validation_alias="filePath", serialization_alias="filePath", description="URL-encoded path to the file from the root of the repository, with path separators and spaces percent-encoded.")
class GetFileContentRequestQuery(StrictModel):
    start_line: int | None = Field(default=None, validation_alias="startLine", serialization_alias="startLine", description="The first line of the file to include in the response; when combined with endLine, returns only that line range.", json_schema_extra={'format': 'int32'})
    end_line: int | None = Field(default=None, validation_alias="endLine", serialization_alias="endLine", description="The last line of the file to include in the response; must be greater than or equal to startLine.", json_schema_extra={'format': 'int32'})
    commit_ref: str | None = Field(default=None, validation_alias="commitRef", serialization_alias="commitRef", description="A commit reference (branch name, tag, or full commit hash) specifying which version of the file to retrieve; defaults to HEAD of the default branch.")
class GetFileContentRequest(StrictModel):
    """Retrieves the raw content of a specific file from a repository at a given commit reference, with optional line range filtering. Files exceeding 1MB will return a PayloadTooLarge error."""
    path: GetFileContentRequestPath
    query: GetFileContentRequestQuery | None = None

# Operation: get_file_coverage
class GetFileCoverageRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique numeric identifier for a file within a specific commit, used to scope coverage data to that file.", json_schema_extra={'format': 'int64'})
class GetFileCoverageRequest(StrictModel):
    """Retrieves code coverage information for a specific file at the head commit of a repository branch. Returns coverage metrics to help identify tested and untested code areas."""
    path: GetFileCoverageRequestPath

# Operation: set_file_ignored_state
class UpdateFileStateRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the repository (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization or account name as it appears on the Git provider.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The repository name as it appears under the organization on the Git provider.")
class UpdateFileStateRequestBody(StrictModel):
    ignored: bool = Field(default=..., description="Set to true to ignore the file (exclude it from analysis) or false to unignore it (re-include it in analysis).")
    filepath: str = Field(default=..., description="The relative path to the file within the repository, starting from the repository root.")
class UpdateFileStateRequest(StrictModel):
    """Ignore or unignore a specific file in a repository, controlling whether Codacy includes it in analysis. Use this to suppress analysis on generated, vendored, or otherwise irrelevant files."""
    path: UpdateFileStateRequestPath
    body: UpdateFileStateRequestBody

# Operation: ignore_security_item
class IgnoreSecurityItemRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
    srm_item_id: str = Field(default=..., validation_alias="srmItemId", serialization_alias="srmItemId", description="The unique UUID identifier of the security and risk management item to ignore.", json_schema_extra={'format': 'uuid'})
class IgnoreSecurityItemRequestBody(StrictModel):
    """Request body of ignore item information"""
    reason: str | None = Field(default=None, description="Categorized reason for ignoring the item. Must be one of: AcceptedUse (intentional usage), FalsePositive (incorrect detection), NotExploitable (not actionable in context), TestCode (issue exists in test code), or ExternalCode (issue originates in third-party code).")
    comment: str | None = Field(default=None, description="Free-text comment providing additional context or justification for why the security item is being ignored.")
class IgnoreSecurityItemRequest(StrictModel):
    """Marks a specific security and risk management (SRM) item as ignored for an organization, optionally providing a reason category and explanatory comment. Useful for suppressing known false positives, accepted risks, or non-applicable findings."""
    path: IgnoreSecurityItemRequestPath
    body: IgnoreSecurityItemRequestBody | None = None

# Operation: unignore_security_item
class UnignoreSecurityItemRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
    srm_item_id: str = Field(default=..., validation_alias="srmItemId", serialization_alias="srmItemId", description="The unique UUID identifying the security and risk management item to be unignored.", json_schema_extra={'format': 'uuid'})
class UnignoreSecurityItemRequest(StrictModel):
    """Restores a previously ignored security and risk management item to an active state within the specified organization. Only items that have been explicitly ignored can be unignored."""
    path: UnignoreSecurityItemRequestPath

# Operation: get_security_item
class GetSecurityItemRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, specified as a short identifier code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider platform.")
    srm_item_id: str = Field(default=..., validation_alias="srmItemId", serialization_alias="srmItemId", description="The unique identifier of the SRM finding to retrieve, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetSecurityItemRequest(StrictModel):
    """Retrieves detailed information for a single security and risk management (SRM) finding within an organization. Use this to inspect a specific SRM item by its unique identifier."""
    path: GetSecurityItemRequestPath

# Operation: search_security_items
class SearchSecurityItemsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Identifies which platform to query.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class SearchSecurityItemsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of security items to return per request. Must be between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    sort: Literal["Status", "DetectedAt"] | None = Field(default=None, description="The field by which to sort the returned security items.")
    direction: str | None = Field(default=None, description="The direction in which to sort results, either ascending or descending.")
class SearchSecurityItemsRequestBody(StrictModel):
    """Request body with items filters."""
    repositories: list[str] | None = Field(default=None, description="List of repository names within the organization to restrict results to. Order is not significant.")
    priorities: list[str] | None = Field(default=None, description="List of priority levels to filter security items by. Refer to SrmPriority for valid values. Order is not significant.")
    statuses: list[str] | None = Field(default=None, description="List of statuses to filter security items by. Refer to SrmStatus for valid values. Order is not significant.")
    categories: list[str] | None = Field(default=None, description="List of security categories to filter by. Use the special value `_other_` to include items that have no assigned security category. Order is not significant.")
    scan_types: list[str] | None = Field(default=None, validation_alias="scanTypes", serialization_alias="scanTypes", description="List of scan types to filter results by, such as static analysis, dependency scanning, secrets detection, and others. Order is not significant.")
    segments: list[int] | None = Field(default=None, description="List of segment IDs to filter security items by. Segments represent logical groupings within the organization. Order is not significant.")
    dast_target_urls: list[str] | None = Field(default=None, validation_alias="dastTargetUrls", serialization_alias="dastTargetUrls", description="List of DAST target URLs to filter results to only items associated with those targets. Order is not significant.")
    search_text: str | None = Field(default=None, validation_alias="searchText", serialization_alias="searchText", description="Free-text search string to match against security item content, such as titles or descriptions.")
class SearchSecurityItemsRequest(StrictModel):
    """Search and filter security and risk management (SRM) items across repositories in an organization. Supports filtering by priority, status, category, scan type, and more to help identify and triage security issues."""
    path: SearchSecurityItemsRequestPath
    query: SearchSecurityItemsRequestQuery | None = None
    body: SearchSecurityItemsRequestBody | None = None

# Operation: get_security_dashboard_metrics
class SearchSecurityDashboardRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target provider.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class SearchSecurityDashboardRequestBody(StrictModel):
    """Request body with dashboard filters."""
    repositories: list[str] | None = Field(default=None, description="List of repository names to scope the dashboard metrics to. When omitted, metrics are aggregated across all repositories in the organization.")
    priorities: list[Literal["Low", "Medium", "High", "Critical"]] | None = Field(default=None, description="List of security issue priority levels to include in the metrics. Refer to SrmPriority for the set of valid priority values.")
    categories: list[str] | None = Field(default=None, description="List of security categories to filter issues by. Use the special value `_other_` to include issues that have no assigned security category.")
    scan_types: list[str] | None = Field(default=None, validation_alias="scanTypes", serialization_alias="scanTypes", description="List of scan types to restrict metrics to. Multiple scan types can be specified to combine results across different analysis methods.")
    segments: list[int] | None = Field(default=None, description="List of numeric segment IDs to filter the dashboard metrics by. Segments represent logical groupings of repositories or teams within the organization.")
class SearchSecurityDashboardRequest(StrictModel):
    """Retrieves aggregated security and risk management metrics for an organization's dashboard, with optional filtering by repositories, priorities, categories, scan types, and segments."""
    path: SearchSecurityDashboardRequestPath
    body: SearchSecurityDashboardRequestBody | None = None

# Operation: search_repositories_with_security_findings
class SearchSecurityDashboardRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class SearchSecurityDashboardRepositoriesRequestBody(StrictModel):
    """Request body with filters."""
    repositories: list[str] | None = Field(default=None, description="List of repository names to narrow results to specific repositories; order is not significant. If omitted, all repositories in the organization are considered.")
    segments: list[int] | None = Field(default=None, description="List of segment IDs to filter repositories by organizational segment; order is not significant. If omitted, all segments are included.")
class SearchSecurityDashboardRepositoriesRequest(StrictModel):
    """Searches repositories within an organization for security findings, returning matching results with their associated security data. If no filters are applied, defaults to returning the 10 repositories with the highest number of findings."""
    path: SearchSecurityDashboardRepositoriesRequestPath
    body: SearchSecurityDashboardRepositoriesRequestBody | None = None

# Operation: search_security_findings_history
class SearchSecurityDashboardHistoryRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target platform.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class SearchSecurityDashboardHistoryRequestBody(StrictModel):
    """Request body with filters."""
    repositories: list[str] | None = Field(default=None, description="List of repository names to scope the history results to. When omitted, results cover all repositories in the organization. Order is not significant.")
    segments: list[int] | None = Field(default=None, description="List of segment IDs to filter the history results by. Segments represent logical groupings within the organization. Order is not significant.")
class SearchSecurityDashboardHistoryRequest(StrictModel):
    """Retrieves the historical evolution of security findings over time for an organization, optionally filtered by specific repositories or segments. Useful for tracking security posture trends and identifying improvements or regressions."""
    path: SearchSecurityDashboardHistoryRequestPath
    body: SearchSecurityDashboardHistoryRequestBody | None = None

# Operation: search_security_category_finding
class SearchSecurityDashboardCategoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class SearchSecurityDashboardCategoriesRequestBody(StrictModel):
    """Request body with filters."""
    repositories: list[str] | None = Field(default=None, description="List of repository names to scope the results to; omit to include all repositories in the organization. Order is not significant.")
    segments: list[int] | None = Field(default=None, description="List of segment IDs to filter results by; omit to include all segments. Order is not significant.")
class SearchSecurityDashboardCategoriesRequest(StrictModel):
    """Retrieves security categories with their associated findings for an organization, optionally filtered by repositories or segments. If no filters are provided, returns the 10 categories with the highest finding counts."""
    path: SearchSecurityDashboardCategoriesRequestPath
    body: SearchSecurityDashboardCategoriesRequestBody | None = None

# Operation: upload_dast_report
class UploadDastReportRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short identifier for the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the remote Git provider.")
    tool_name: Literal["ZAP"] = Field(default=..., validation_alias="toolName", serialization_alias="toolName", description="The DAST tool that generated the report. Currently only ZAP (OWASP Zed Attack Proxy) is supported.")
class UploadDastReportRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The binary file containing the DAST scan results. For ZAP reports, ensure the `@generated` timestamp field is in English locale using the format `EEE, d MMM yyyy HH:mm:ss` (ZAP's default), otherwise the report will be rejected.", json_schema_extra={'format': 'binary'})
    report_format: Literal["json"] = Field(default=..., validation_alias="reportFormat", serialization_alias="reportFormat", description="The format of the uploaded report file. Must match the structure expected for the specified tool.")
class UploadDastReportRequest(StrictModel):
    """Uploads a Dynamic Application Security Testing (DAST) scan report to Codacy for the specified organization and tool. The report is parsed and integrated into the organization's security findings dashboard."""
    path: UploadDastReportRequestPath
    body: UploadDastReportRequestBody

# Operation: list_dast_reports
class ListDastReportsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, used to identify the source control platform.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class ListDastReportsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of DAST reports to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListDastReportsRequest(StrictModel):
    """Retrieves a paginated list of uploaded DAST (Dynamic Application Security Testing) scan reports for an organization, including their current processing state. Results are sorted by submission date from latest to earliest."""
    path: ListDastReportsRequestPath
    query: ListDastReportsRequestQuery | None = None

# Operation: list_security_managers
class ListSecurityManagersRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the Git provider.")
class ListSecurityManagersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of security managers to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListSecurityManagersRequest(StrictModel):
    """Retrieves the list of organization admins and security managers for a specified organization on a Git provider. Useful for auditing access control and identifying users with elevated security permissions."""
    path: ListSecurityManagersRequestPath
    query: ListSecurityManagersRequestQuery | None = None

# Operation: assign_security_manager
class PostSecurityManagerRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization. Use the short code for the desired provider (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class PostSecurityManagerRequestBody(StrictModel):
    """User ID of the organization member to be promoted to security manager."""
    user_id: int = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique numeric identifier of the organization member to be assigned the Security Manager role. Must correspond to an existing member of the organization.", json_schema_extra={'format': 'int64'})
class PostSecurityManagerRequest(StrictModel):
    """Promotes an existing organization member to the Security Manager role within the specified Git provider organization. This grants the user elevated permissions to oversee and manage security-related settings and findings."""
    path: PostSecurityManagerRequestPath
    body: PostSecurityManagerRequestBody

# Operation: revoke_security_manager
class DeleteSecurityManagerRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the Git provider.")
    user_id: int = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique numeric identifier of the organization member whose Security Manager role is being revoked.", json_schema_extra={'format': 'int64'})
class DeleteSecurityManagerRequest(StrictModel):
    """Revokes the Security Manager role from a specified organization member, removing their elevated security permissions within the organization on the given Git provider."""
    path: DeleteSecurityManagerRequestPath

# Operation: list_repositories_with_security_issues
class ListSecurityRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target provider.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class ListSecurityRepositoriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Must be between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    segments: str | None = Field(default=None, description="Narrows results to repositories belonging to the specified segments, provided as a comma-separated list of segment identifiers.")
class ListSecurityRepositoriesRequest(StrictModel):
    """Retrieves a list of repositories within an organization that have active security issues. Supports pagination and optional filtering by segment identifiers."""
    path: ListSecurityRepositoriesRequestPath
    query: ListSecurityRepositoriesRequestQuery | None = None

# Operation: list_security_categories
class ListSecurityCategoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Identifies which platform to query for security data.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider. Must match the exact organization identifier used on the platform.")
class ListSecurityCategoriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of security categories to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListSecurityCategoriesRequest(StrictModel):
    """Retrieves a list of security subcategories that have active security issues for the specified organization. Useful for identifying which vulnerability categories require attention across the organization's repositories."""
    path: ListSecurityCategoriesRequestPath
    query: ListSecurityCategoriesRequestQuery | None = None

# Operation: search_sbom_dependencies
class SearchSbomDependenciesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target platform.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class SearchSbomDependenciesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of dependency records to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    sort_column: Literal["severity", "ossfScore"] | None = Field(default=None, validation_alias="sortColumn", serialization_alias="sortColumn", description="Field by which to sort the returned results. Use `severity` to order by the dependency's vulnerability severity, or `ossfScore` to order by the OpenSSF scorecard score.")
    column_order: Literal["asc", "desc"] | None = Field(default=None, validation_alias="columnOrder", serialization_alias="columnOrder", description="Direction in which to sort the results relative to the chosen sort column. Use `asc` for ascending or `desc` for descending order.")
class SearchSbomDependenciesRequestBody(StrictModel):
    """Request body with filters."""
    text: str | None = Field(default=None, description="Free-text search string matched against SBOM component fields including package URL (purl) and full component name.")
    repositories: list[str] | None = Field(default=None, description="List of repository names within the organization to restrict results to. Order is not significant; each item should be a repository name string.")
    segments: list[int] | None = Field(default=None, description="List of segment IDs to restrict results to. Order is not significant; each item should be an integer segment identifier.")
    finding_severities: list[Literal["Critical", "High", "Medium", "Low"]] | None = Field(default=None, validation_alias="findingSeverities", serialization_alias="findingSeverities", description="List of vulnerability severity levels to include in results. Order is not significant; valid values are `Critical`, `High`, `Medium`, and `Low`.")
    risk_categories: list[Literal["Forbidden", "Restricted", "Reciprocal", "Notice", "Permissive", "Unencumbered", "Unknown"]] | None = Field(default=None, validation_alias="riskCategories", serialization_alias="riskCategories", description="List of license risk category labels to filter dependencies by. Order is not significant; each item should be a valid license risk category string.")
class SearchSbomDependenciesRequest(StrictModel):
    """Search and filter SBOM (Software Bill of Materials) dependencies used across an organization, returning vulnerability and license risk details for matched components. Supports filtering by severity, repository, segment, and text search against component identifiers."""
    path: SearchSbomDependenciesRequestPath
    query: SearchSbomDependenciesRequestQuery | None = None
    body: SearchSbomDependenciesRequestBody | None = None

# Operation: search_dependency_repositories
class SearchRepositoriesOfSbomDependencyRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the target platform.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization name as it appears on the Git provider.")
class SearchRepositoriesOfSbomDependencyRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per page. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class SearchRepositoriesOfSbomDependencyRequestBody(StrictModel):
    """Request body with filters."""
    dependency_full_name: str = Field(default=..., validation_alias="dependencyFullName", serialization_alias="dependencyFullName", description="The fully qualified name of the SBOM dependency to search for across repositories.")
    repositories_filter: list[str] | None = Field(default=None, validation_alias="repositoriesFilter", serialization_alias="repositoriesFilter", description="An optional list of repository names to restrict the search to. Order is not significant; each item should be a repository name string.")
class SearchRepositoriesOfSbomDependencyRequest(StrictModel):
    """Search for repositories within an organization that use a specific SBOM dependency, returning a paginated list of matches. Optionally filter results to a subset of repositories by name."""
    path: SearchRepositoriesOfSbomDependencyRequestPath
    query: SearchRepositoriesOfSbomDependencyRequestQuery | None = None
    body: SearchRepositoriesOfSbomDependencyRequestBody

# Operation: search_sbom_repositories
class SearchSbomRepositoriesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider.")
class SearchSbomRepositoriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class SearchSbomRepositoriesRequestBody(StrictModel):
    """Request body with filters."""
    body: dict[str, Any] | None = Field(default=None, description="Optional request body to filter repositories by specific dependencies. Each item should be a dependency identifier in the format 'ecosystem/package-name'.")
class SearchSbomRepositoriesRequest(StrictModel):
    """Search and list repositories within an organization that contain SBOM (Software Bill of Materials) dependency information, optionally filtering by specific dependencies."""
    path: SearchSbomRepositoriesRequestPath
    query: SearchSbomRepositoriesRequestQuery | None = None
    body: SearchSbomRepositoriesRequestBody | None = None

# Operation: get_repository_sbom_download_url
class GetRepositorySbomPresignedUrlRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
class GetRepositorySbomPresignedUrlRequest(StrictModel):
    """Retrieves a presigned URL for downloading the latest Software Bill of Materials (SBOM) for a specified repository. The URL provides temporary, authenticated access to the SBOM artifact."""
    path: GetRepositorySbomPresignedUrlRequestPath

# Operation: upload_image_sbom
class UploadImageSbomRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class UploadImageSbomRequestBody(StrictModel):
    sbom: str = Field(default=..., description="The SBOM file to upload, provided as binary data in either SPDX or CycloneDX format.", json_schema_extra={'format': 'binary'})
    environment: str | None = Field(default=None, description="The deployment environment associated with the Docker image (e.g., production, staging), used to contextualize the SBOM within a specific runtime environment.")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="Name of the Docker image")
    tag: str | None = Field(default=None, description="Tag of the Docker image")
    repository_name: dict | None = Field(default=None, validation_alias="repositoryName", serialization_alias="repositoryName", description="Repository name")
class UploadImageSbomRequest(StrictModel):
    """Uploads a Software Bill of Materials (SBOM) for a Docker image to the specified organization, enabling vulnerability tracking and dependency analysis. Accepts SBOM files in SPDX or CycloneDX format."""
    path: UploadImageSbomRequestPath
    body: UploadImageSbomRequestBody

# Operation: delete_image_sboms
class DeleteImageSbomsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
    image_name: str = Field(default=..., validation_alias="imageName", serialization_alias="imageName", description="The name of the container image whose SBOMs should be deleted. Must match the image name used when the SBOMs were originally uploaded.")
class DeleteImageSbomsRequest(StrictModel):
    """Deletes all Software Bill of Materials (SBOMs) associated with a specific container image in the given organization. This action is irreversible and removes all SBOM records for the specified image."""
    path: DeleteImageSbomsRequestPath

# Operation: delete_image_tag_sbom
class DeleteImageTagRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
    image_name: str = Field(default=..., validation_alias="imageName", serialization_alias="imageName", description="The name of the container image whose SBOM entry is being deleted.")
    tag: str = Field(default=..., description="The specific tag of the container image whose SBOM entry is being deleted.")
class DeleteImageTagRequest(StrictModel):
    """Deletes the SBOM (Software Bill of Materials) associated with a specific image and tag combination within an organization. This action permanently removes the SBOM data for the given image/tag pair."""
    path: DeleteImageTagRequestPath

# Operation: list_organization_images
class ListOrganizationImagesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider.")
class ListOrganizationImagesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of Docker images to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListOrganizationImagesRequest(StrictModel):
    """Retrieves the list of Docker images available for a specified organization on a Git provider. Supports pagination to control the number of results returned."""
    path: ListOrganizationImagesRequestPath
    query: ListOrganizationImagesRequestQuery | None = None

# Operation: list_image_tags
class ListImageTagsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
    image_name: str = Field(default=..., validation_alias="imageName", serialization_alias="imageName", description="The name of the Docker image for which to list available tags.")
class ListImageTagsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of image tags to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListImageTagsRequest(StrictModel):
    """Retrieves all Docker image tags associated with a specific image in an organization's SBOM registry. Results are paginated and scoped to the specified Git provider and organization."""
    path: ListImageTagsRequestPath
    query: ListImageTagsRequestQuery | None = None

# Operation: list_jira_tickets
class GetJiraTicketsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class GetJiraTicketsRequestQuery(StrictModel):
    element_type: Literal["issue", "finding", "file", "dependency"] = Field(default=..., validation_alias="elementType", serialization_alias="elementType", description="The category of Codacy element whose linked Jira tickets should be retrieved. Must be one of: issue, finding, file, or dependency.")
    element_id: str = Field(default=..., validation_alias="elementId", serialization_alias="elementId", description="The unique identifier of the specific Codacy element for which Jira tickets are being requested.")
class GetJiraTicketsRequest(StrictModel):
    """Retrieves Jira tickets linked to a specific Codacy element (such as an issue, finding, file, or dependency) within an organization. Useful for tracing code quality findings back to their associated Jira work items."""
    path: GetJiraTicketsRequestPath
    query: GetJiraTicketsRequestQuery

# Operation: create_jira_ticket
class CreateJiraTicketRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class CreateJiraTicketRequestBody(StrictModel):
    """Create Ticket Fields"""
    element_type: Literal["issue", "finding", "file", "dependency"] = Field(default=..., validation_alias="elementType", serialization_alias="elementType", description="The category of code element the Jira ticket will be associated with, such as a code issue, security finding, file, or dependency.")
    jira_project_id: int = Field(default=..., validation_alias="jiraProjectId", serialization_alias="jiraProjectId", description="The unique numeric identifier of the Jira project in which the ticket will be created.", json_schema_extra={'format': 'int64'})
    create_jira_ticket_elements: list[CreateJiraTicketElement] = Field(default=..., validation_alias="createJiraTicketElements", serialization_alias="createJiraTicketElements", description="List of code element identifiers to associate with the Jira ticket; each item should correspond to an element of the specified elementType. Order is not significant.")
    issue_type_id: int = Field(default=..., validation_alias="issueTypeId", serialization_alias="issueTypeId", description="The numeric identifier of the Jira issue type (e.g., Bug, Task, Story) to assign to the new ticket.", json_schema_extra={'format': 'int64'})
    summary: str = Field(default=..., description="A short, descriptive title summarizing the purpose or content of the Jira ticket.")
    due_date: str | None = Field(default=None, validation_alias="dueDate", serialization_alias="dueDate", description="Optional target completion date for the ticket, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    description: str | None = Field(default=None, description="JIRA description written in Atlassian Document Format https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/#json-schema")
class CreateJiraTicketRequest(StrictModel):
    """Creates a new Jira ticket linked to a specific Codacy organization, associating it with one or more code elements such as issues, findings, files, or dependencies."""
    path: CreateJiraTicketRequestPath
    body: CreateJiraTicketRequestBody

# Operation: unlink_jira_ticket
class UnlinkRepositoryJiraTicketRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization. Use the short identifier for the provider (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization as it appears on the Git provider platform.")
    jira_ticket_identifier: int = Field(default=..., validation_alias="jiraTicketIdentifier", serialization_alias="jiraTicketIdentifier", description="The unique numeric identifier of the Jira ticket to unlink. This is the internal Jira ticket ID, not the human-readable issue key.", json_schema_extra={'format': 'int64'})
class UnlinkRepositoryJiraTicketRequestBody(StrictModel):
    """Unlink Jira Ticket Element Identification"""
    element_type: Literal["issue", "finding", "file", "dependency"] = Field(default=..., validation_alias="elementType", serialization_alias="elementType", description="The type of repository element from which the Jira ticket will be unlinked. Must be one of: issue, finding, file, or dependency.")
    element_id: str = Field(default=..., validation_alias="elementId", serialization_alias="elementId", description="The unique identifier of the specific repository element (of the type specified by elementType) from which the Jira ticket will be unlinked.")
class UnlinkRepositoryJiraTicketRequest(StrictModel):
    """Removes the association between a Jira ticket and a specific repository element (such as an issue, finding, file, or dependency) within an organization. Use this to detach a previously linked Jira ticket from a code analysis element."""
    path: UnlinkRepositoryJiraTicketRequestPath
    body: UnlinkRepositoryJiraTicketRequestBody

# Operation: get_jira_integration
class GetJiraIntegrationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
class GetJiraIntegrationRequest(StrictModel):
    """Retrieves the Jira integration configuration for a specified organization on a Git provider. Useful for inspecting whether Jira is connected and reviewing its current settings."""
    path: GetJiraIntegrationRequestPath

# Operation: delete_jira_integration
class DeleteJiraIntegrationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization. Use the provider's abbreviated identifier.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class DeleteJiraIntegrationRequest(StrictModel):
    """Removes the Jira integration and all associated resources from the specified organization on a Git provider. This action is irreversible and will disconnect Jira from the organization."""
    path: DeleteJiraIntegrationRequestPath

# Operation: list_jira_projects
class GetAvailableJiraProjectsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The short identifier for the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider.")
class GetAvailableJiraProjectsRequestQuery(StrictModel):
    search: str | None = Field(default=None, description="Optional search string to filter returned Jira projects by name, returning only projects whose names contain the provided value.")
    limit: int | None = Field(default=None, description="Maximum number of Jira projects to return in a single response, between 1 and 100 inclusive. Defaults to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetAvailableJiraProjectsRequest(StrictModel):
    """Retrieves the available Jira projects linked to a specific Git provider organization, enabling users to associate repositories with Jira for issue tracking. Supports filtering and pagination to narrow down results."""
    path: GetAvailableJiraProjectsRequestPath
    query: GetAvailableJiraProjectsRequestQuery | None = None

# Operation: list_jira_issue_types
class GetJiraProjectIssueTypesRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider for the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    jira_project_id: int = Field(default=..., validation_alias="jiraProjectId", serialization_alias="jiraProjectId", description="The unique numeric identifier of the Jira project whose issue types should be retrieved.", json_schema_extra={'format': 'int64'})
class GetJiraProjectIssueTypesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of issue types to return per request. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetJiraProjectIssueTypesRequest(StrictModel):
    """Retrieves all available issue types (e.g., Bug, Story, Task) for a specific Jira project, enabling users to select valid types when creating or managing Jira issues linked to a Git organization."""
    path: GetJiraProjectIssueTypesRequestPath
    query: GetJiraProjectIssueTypesRequestQuery | None = None

# Operation: list_jira_issue_type_fields
class GetJiraProjectIssueFieldsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    jira_project_id: int = Field(default=..., validation_alias="jiraProjectId", serialization_alias="jiraProjectId", description="The numeric identifier of the Jira project whose issue type fields are being queried.", json_schema_extra={'format': 'int64'})
    jira_issue_type_id: str = Field(default=..., validation_alias="jiraIssueTypeId", serialization_alias="jiraIssueTypeId", description="The identifier of the Jira issue type within the project for which available fields are returned.")
class GetJiraProjectIssueFieldsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of fields to return per response. Accepts values between 1 and 100, defaulting to 100 when omitted.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetJiraProjectIssueFieldsRequest(StrictModel):
    """Retrieves the available fields for a specific Jira issue type within a project, enabling dynamic form construction when creating or editing issues. Results are scoped to the organization identified by the Git provider and organization name."""
    path: GetJiraProjectIssueFieldsRequestPath
    query: GetJiraProjectIssueFieldsRequestQuery | None = None

# Operation: get_slack_integration
class GetSlackIntegrationRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization. Use the provider's abbreviated identifier.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class GetSlackIntegrationRequest(StrictModel):
    """Retrieves the Slack integration configuration for a specified organization on a Git provider. Use this to check whether Slack notifications are enabled and review the current integration settings."""
    path: GetSlackIntegrationRequestPath

# Operation: get_pull_request_diff
class GetPullRequestDiffRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider for the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique numeric identifier of the pull request within the repository.", json_schema_extra={'format': 'int32'})
class GetPullRequestDiffRequest(StrictModel):
    """Retrieves the human-readable Git diff for a specific pull request, showing all file changes, additions, and deletions. Useful for reviewing code changes before merging."""
    path: GetPullRequestDiffRequestPath

# Operation: get_commit_diff
class GetCommitDiffRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git hosting provider (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    commit_uuid: str = Field(default=..., validation_alias="commitUuid", serialization_alias="commitUuid", description="The full SHA hash or UUID that uniquely identifies the commit whose diff should be retrieved.")
class GetCommitDiffRequest(StrictModel):
    """Retrieves the human-readable Git diff for a specific commit in a repository, showing all file changes introduced by that commit."""
    path: GetCommitDiffRequestPath

# Operation: get_commit_diff_between
class GetDiffBetweenCommitsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified Git provider organization.")
    base_commit_uuid: str = Field(default=..., validation_alias="baseCommitUuid", serialization_alias="baseCommitUuid", description="The SHA or UUID of the base (earlier) commit to use as the starting point of the diff comparison.")
    head_commit_uuid: str = Field(default=..., validation_alias="headCommitUuid", serialization_alias="headCommitUuid", description="The SHA or UUID of the head (later) commit to use as the ending point of the diff comparison, representing the changes introduced since the base commit.")
class GetDiffBetweenCommitsRequest(StrictModel):
    """Retrieves the human-readable Git diff between a base commit and a head commit in a specified repository, showing all changes introduced between the two points in history."""
    path: GetDiffBetweenCommitsRequestPath

# Operation: export_organization_security_items
class GetReportSecurityItemsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization. Each provider has a short code (e.g., GitHub, GitLab, Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact name of the organization as it appears on the specified Git provider. This is the organization's handle or slug, not a display name.")
class GetReportSecurityItemsRequest(StrictModel):
    """Generates and downloads a CSV report listing all security and risk management items for a specified organization on a Git provider. Useful for auditing, compliance tracking, and offline analysis of an organization's security posture."""
    path: GetReportSecurityItemsRequestPath

# Operation: export_security_items_csv
class SearchReportSecurityItemsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class SearchReportSecurityItemsRequestBody(StrictModel):
    """Optional filters for the CSV export"""
    repositories: list[str] | None = Field(default=None, description="List of repository names within the organization to restrict results to. Order is not significant.")
    priorities: list[Literal["Low", "Medium", "High", "Critical"]] | None = Field(default=None, description="List of priority levels to filter security issues by. Valid values are defined by the SrmPriority enumeration. Order is not significant.")
    statuses: list[Literal["Overdue", "OnTrack", "DueSoon", "ClosedOnTime", "ClosedLate", "Ignored"]] | None = Field(default=None, description="List of statuses to filter security issues by. Valid values are defined by the SrmStatus enumeration. Order is not significant.")
    categories: list[str] | None = Field(default=None, description="List of security categories to filter by. Use the special value `_other_` to include issues that have no assigned security category. Order is not significant.")
    scan_types: list[str] | None = Field(default=None, validation_alias="scanTypes", serialization_alias="scanTypes", description="List of scan types to restrict results to. Order is not significant.")
    segments: list[int] | None = Field(default=None, description="List of numeric segment IDs to filter results by. Order is not significant.")
    search_text: str | None = Field(default=None, validation_alias="searchText", serialization_alias="searchText", description="Free-text string used to search within security item fields, such as title or description.")
class SearchReportSecurityItemsRequest(StrictModel):
    """Generates a filtered CSV export of security and risk management items for an organization. Supports filtering by repository, priority, status, category, scan type, segment, and free-text search."""
    path: SearchReportSecurityItemsRequestPath
    body: SearchReportSecurityItemsRequestBody | None = None

# Operation: get_commit
class GetCommitDetailsByCommitIdRequestPath(StrictModel):
    commit_id: int = Field(default=..., validation_alias="commitId", serialization_alias="commitId", description="The unique numeric identifier of the commit to retrieve.", json_schema_extra={'format': 'int64'})
class GetCommitDetailsByCommitIdRequest(StrictModel):
    """Retrieves detailed information about a specific commit, including its metadata, changes, and associated data. Use this to inspect the full details of a known commit by its unique identifier."""
    path: GetCommitDetailsByCommitIdRequestPath

# Operation: check_repository_quickfix_suggestions
class HasQuickfixSuggestionsRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the specified Git provider organization.")
class HasQuickfixSuggestionsRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Name of a branch enabled on Codacy for this repository. Must be a branch tracked by Codacy, as returned by the listRepositoryBranches endpoint. Defaults to the main branch configured in Codacy repository settings if omitted.")
class HasQuickfixSuggestionsRequest(StrictModel):
    """Checks whether a repository has any available quick fix suggestions for issues on a specified branch. If no branch is provided, the repository's default branch is used."""
    path: HasQuickfixSuggestionsRequestPath
    query: HasQuickfixSuggestionsRequestQuery | None = None

# Operation: get_issue_quickfixes_patch
class GetQuickfixesPatchRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the repository.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="Name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="Name of the repository within the specified organization on the Git provider.")
class GetQuickfixesPatchRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Name of a branch enabled on Codacy for this repository. Defaults to the main branch configured in Codacy repository settings if omitted.")
class GetQuickfixesPatchRequest(StrictModel):
    """Retrieves quickfix suggestions for repository issues in patch format, allowing automated code corrections to be applied directly. If no branch is specified, the repository's default branch is used."""
    path: GetQuickfixesPatchRequestPath
    query: GetQuickfixesPatchRequestQuery | None = None

# Operation: get_pull_request_issues_patch
class GetPullRequestQuickfixesPatchRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the repository, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The name of the organization or account on the Git provider that owns the repository.")
    repository_name: str = Field(default=..., validation_alias="repositoryName", serialization_alias="repositoryName", description="The name of the repository within the specified organization on the Git provider.")
    pull_request_number: int = Field(default=..., validation_alias="pullRequestNumber", serialization_alias="pullRequestNumber", description="The unique number identifying the pull request within the repository, as shown in the Git provider's interface.", json_schema_extra={'format': 'int32'})
class GetPullRequestQuickfixesPatchRequest(StrictModel):
    """Retrieves quickfix patches for issues found in a specific pull request, formatted as a unified diff patch. The patch can be applied directly to resolve detected issues in the pull request's code."""
    path: GetPullRequestQuickfixesPatchRequestPath

# Operation: list_organization_audit_logs
class ListAuditLogsForOrganizationRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider.")
class ListAuditLogsForOrganizationRequestQuery(StrictModel):
    from_: int | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the audit log time window as a Unix epoch timestamp in milliseconds. If omitted, defaults to the earliest available audit log entry.", json_schema_extra={'format': 'int64'})
    to: int | None = Field(default=None, description="End of the audit log time window as a Unix epoch timestamp in milliseconds. If omitted, defaults to the current time.", json_schema_extra={'format': 'int64'})
class ListAuditLogsForOrganizationRequest(StrictModel):
    """Retrieves audit logs for the specified organization within an optional time range. Requires Business plan and organization admin or manager role."""
    path: ListAuditLogsForOrganizationRequestPath
    query: ListAuditLogsForOrganizationRequestQuery | None = None

# Operation: get_segment_sync_status
class GetSegmentsSyncStatusRequestPath(StrictModel):
    provider: str = Field(default=..., description="Identifier for the Git provider hosting the organization. Use the short code for the desired platform (e.g., GitHub, GitLab, or Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider. This must match the exact remote organization name used by the provider.")
class GetSegmentsSyncStatusRequest(StrictModel):
    """Retrieves the current synchronization status of segments for a specified organization on a Git provider. Useful for monitoring whether segment data is up to date or still processing."""
    path: GetSegmentsSyncStatusRequestPath

# Operation: list_segment_keys
class GetSegmentsKeysRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The exact organization name as it appears on the specified Git provider.")
class GetSegmentsKeysRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of segment keys to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Narrows results to segment keys whose names contain the provided string, enabling targeted lookups within large organizations.")
class GetSegmentsKeysRequest(StrictModel):
    """Retrieves the available segment keys for a specified organization on a Git provider. Segment keys can be filtered by search term and support pagination via a configurable result limit."""
    path: GetSegmentsKeysRequestPath
    query: GetSegmentsKeysRequestQuery | None = None

# Operation: list_segment_keys_with_ids
class GetSegmentsKeysWithIdsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
class GetSegmentsKeysWithIdsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of segment key records to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Filters the returned segment keys to those matching the provided search string, useful for locating specific segments by name or partial name.")
class GetSegmentsKeysWithIdsRequest(StrictModel):
    """Retrieves segment keys along with their associated IDs for a specified organization on a Git provider. Supports pagination and text-based filtering to narrow results."""
    path: GetSegmentsKeysWithIdsRequestPath
    query: GetSegmentsKeysWithIdsRequestQuery | None = None

# Operation: list_segment_values
class GetSegmentsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    segment_key: str = Field(default=..., validation_alias="segmentKey", serialization_alias="segmentKey", description="The unique key identifying the segment whose values should be retrieved.")
class GetSegmentsRequestQuery(StrictModel):
    search: str | None = Field(default=None, description="Optional search string to filter returned segment values by name or identifier, returning only items that match the provided text.")
    limit: int | None = Field(default=None, description="Maximum number of segment values to return in a single response, accepting values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetSegmentsRequest(StrictModel):
    """Retrieves the list of values for a specific segment within an organization, identified by its segment key. Supports optional filtering by name and result count limiting."""
    path: GetSegmentsRequestPath
    query: GetSegmentsRequestQuery | None = None

# Operation: list_dast_targets
class GetDastTargetsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the organization, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the specified Git provider.")
class GetDastTargetsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of DAST targets to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class GetDastTargetsRequest(StrictModel):
    """Retrieves all configured Dynamic Application Security Testing (DAST) targets for the specified organization. Returns a paginated list of targets that have been set up for security scanning."""
    path: GetDastTargetsRequestPath
    query: GetDastTargetsRequestQuery | None = None

# Operation: create_dast_target
class CreateDastTargetRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
class CreateDastTargetRequestBody(StrictModel):
    url: str = Field(default=..., description="The fully qualified URL of the application or API endpoint to be scanned. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    target_type: Literal["webapp", "openapi", "graphql"] | None = Field(default=None, validation_alias="targetType", serialization_alias="targetType", description="Specifies the type of DAST target to scan: 'webapp' for standard web applications, 'openapi' for REST APIs described by an OpenAPI specification, or 'graphql' for GraphQL APIs. Defaults to 'webapp' if not provided.")
    api_definition_url: str | None = Field(default=None, validation_alias="apiDefinitionUrl", serialization_alias="apiDefinitionUrl", description="The URL pointing to the API definition file (e.g., an OpenAPI or GraphQL schema), required when the target type is 'openapi' or 'graphql'.")
class CreateDastTargetRequest(StrictModel):
    """Creates a new Dynamic Application Security Testing (DAST) target for a specified organization, defining the URL and type of application to be scanned for vulnerabilities."""
    path: CreateDastTargetRequestPath
    body: CreateDastTargetRequestBody

# Operation: delete_dast_target
class DeleteDastTargetRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    dast_target_id: int = Field(default=..., validation_alias="dastTargetId", serialization_alias="dastTargetId", description="The unique numeric identifier of the DAST target to delete.", json_schema_extra={'format': 'int64'})
class DeleteDastTargetRequest(StrictModel):
    """Permanently deletes a DAST (Dynamic Application Security Testing) target from the specified organization. This removes the target configuration and stops any associated security scans."""
    path: DeleteDastTargetRequestPath

# Operation: trigger_dast_analysis
class AnalyzeDastTargetRequestPath(StrictModel):
    provider: str = Field(default=..., description="Short code identifying the Git provider hosting the organization, such as GitHub, GitLab, or Bitbucket.")
    remote_organization_name: str = Field(default=..., validation_alias="remoteOrganizationName", serialization_alias="remoteOrganizationName", description="The organization's name as it appears on the Git provider platform.")
    dast_target_id: int = Field(default=..., validation_alias="dastTargetId", serialization_alias="dastTargetId", description="Unique numeric identifier of the DAST target to be analyzed. Must reference an existing target configured under the organization.", json_schema_extra={'format': 'int64'})
class AnalyzeDastTargetRequest(StrictModel):
    """Enqueues a Dynamic Application Security Testing (DAST) analysis for a specified target within an organization. Use this to initiate a security scan against a previously configured DAST target."""
    path: AnalyzeDastTargetRequestPath

# Operation: list_enterprise_organizations
class ListEnterpriseOrganizationsRequestPath(StrictModel):
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The unique slug identifier for the enterprise whose organizations you want to retrieve.")
    provider: str = Field(default=..., description="The Git provider hosting the enterprise, specified as a short identifier code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
class ListEnterpriseOrganizationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of organizations to return in a single response. Accepts values between 1 and 100, defaulting to 100 if not specified.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListEnterpriseOrganizationsRequest(StrictModel):
    """Retrieves the list of organizations belonging to a specified enterprise on a given Git provider. Supports pagination via a configurable result limit."""
    path: ListEnterpriseOrganizationsRequestPath
    query: ListEnterpriseOrganizationsRequestQuery | None = None

# Operation: list_enterprises
class ListEnterprisesRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider to query for enterprises, identified by its short code (e.g., GitHub, GitLab, Bitbucket).")
class ListEnterprisesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of enterprise records to return in a single response, between 1 and 100 inclusive.", ge=1, le=100, json_schema_extra={'format': 'int32'})
class ListEnterprisesRequest(StrictModel):
    """Retrieves all enterprises associated with the authenticated user for a specified Git provider. Returns a paginated list of enterprise accounts the user has access to."""
    path: ListEnterprisesRequestPath
    query: ListEnterprisesRequestQuery | None = None

# Operation: get_enterprise
class GetEnterpriseRequestPath(StrictModel):
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The unique slug identifier for the enterprise, typically a lowercase hyphenated name used in URLs.")
    provider: str = Field(default=..., description="The short code identifying the git provider hosting the enterprise (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
class GetEnterpriseRequest(StrictModel):
    """Retrieves details for a specific enterprise account by its slug identifier and git provider. Use this to fetch enterprise-level configuration, metadata, or status."""
    path: GetEnterpriseRequestPath

# Operation: list_enterprise_seats
class ListEnterpriseSeatsRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the enterprise, identified by a short code (e.g., gh for GitHub, gl for GitLab, bb for Bitbucket).")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The URL-friendly slug identifier of the enterprise whose seats are being listed.")
class ListEnterpriseSeatsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of seat records to return in a single response. Accepts values between 1 and 100.", ge=1, le=100, json_schema_extra={'format': 'int32'})
    search: str | None = Field(default=None, description="Optional search string used to filter the returned seats, matching against relevant seat or user identifiers.")
class ListEnterpriseSeatsRequest(StrictModel):
    """Retrieves a paginated list of seats allocated within a specified enterprise on a given Git provider. Supports filtering by search term to narrow results."""
    path: ListEnterpriseSeatsRequestPath
    query: ListEnterpriseSeatsRequestQuery | None = None

# Operation: export_enterprise_seats_csv
class ListEnterpriseSeatsCsvRequestPath(StrictModel):
    provider: str = Field(default=..., description="The Git provider hosting the enterprise, identified by a short slug (e.g., GitHub, GitLab, Bitbucket).")
    enterprise_name: str = Field(default=..., validation_alias="enterpriseName", serialization_alias="enterpriseName", description="The unique slug (URL-friendly identifier) of the enterprise whose seat data should be exported.")
class ListEnterpriseSeatsCsvRequest(StrictModel):
    """Exports a CSV file containing seat allocation and usage data for a specified enterprise on a given Git provider. Useful for auditing license consumption and user activity across the enterprise."""
    path: ListEnterpriseSeatsCsvRequestPath

# ============================================================================
# Component Models
# ============================================================================

class Badges(PermissiveModel):
    grade: str = Field(..., description="Repository grade badge URL")
    coverage: str = Field(..., description="Repository coverage badge URL")

class CodingStandardInfo(PermissiveModel):
    """Coding standard identifier and name"""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Identifier of the coding standard", json_schema_extra={'format': 'int64'})
    name: str = Field(..., description="Name of the coding standard")

class ConfiguredParameter(PermissiveModel):
    """Parameter to configure a code pattern for a tool"""
    name: str = Field(..., description="Code pattern parameter name")
    value: str = Field(..., description="Code pattern parameter value")

class ConfiguredParametersList(RootModel[list[ConfiguredParameter]]):
    pass

class ConfigurePattern(PermissiveModel):
    """A pattern to enable or disable."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The pattern's id.")
    enabled: bool = Field(..., description="Whether to enable or disable the pattern.")
    parameters: ConfiguredParametersList | None = None

class CreateJiraTicketElement(PermissiveModel):
    element_id: str = Field(..., validation_alias="elementId", serialization_alias="elementId")
    repository_name: str | None = Field(None, validation_alias="repositoryName", serialization_alias="repositoryName")

class DimensionsFilter(PermissiveModel):
    dimension: str
    value: str

class Language(PermissiveModel):
    """Language information"""
    name: str = Field(..., description="name of the language")

class ProblemLink(PermissiveModel):
    name: str
    url: str

class ApiError(PermissiveModel):
    message: str
    inner_message: str | None = Field(None, validation_alias="innerMessage", serialization_alias="innerMessage")
    actions: list[ProblemLink]

class Forbidden(PermissiveModel):
    message: str
    inner_message: str | None = Field(None, validation_alias="innerMessage", serialization_alias="innerMessage")
    actions: list[ProblemLink]
    error: str

class PayloadTooLarge(PermissiveModel):
    message: str
    inner_message: str | None = Field(None, validation_alias="innerMessage", serialization_alias="innerMessage")
    actions: list[ProblemLink]
    error: str

class PullRequestOwner(PermissiveModel):
    name: str
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl")
    username: str | None = None
    email: str | None = None

class PullRequest(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    number: int = Field(..., json_schema_extra={'format': 'int32'})
    updated: str = Field(..., json_schema_extra={'format': 'date-time'})
    status: str = Field(..., description="Pull request status")
    repository: str
    title: str
    owner: PullRequestOwner
    head_commit_sha: str = Field(..., validation_alias="headCommitSha", serialization_alias="headCommitSha")
    common_ancestor_commit_sha: str = Field(..., validation_alias="commonAncestorCommitSha", serialization_alias="commonAncestorCommitSha")
    origin_branch: str | None = Field(None, validation_alias="originBranch", serialization_alias="originBranch")
    target_branch: str | None = Field(None, validation_alias="targetBranch", serialization_alias="targetBranch")
    git_href: str = Field(..., validation_alias="gitHref", serialization_alias="gitHref", description="URL to the pull request on the Git provider")

class RepositoryLanguageUpdate(PermissiveModel):
    name: str = Field(..., description="name of the language")
    extensions: list[str] | None = Field(None, description="List of custom file extensions for the language. If left undefined, then the extensions will not be updated.")
    enabled: bool | None = Field(None, description="Whether this language is to be analyzed for this repository. If left undefined, then the flag will not be updated.")

class RepositoryProblem(PermissiveModel):
    message: str
    actions: list[ProblemLink]
    code: str = Field(..., description="A stable identifier for a problem.")
    severity: str = Field(..., description="The extent to which this problem affects the repository in terms of analysis execution.")

class RepositorySummary(PermissiveModel):
    """Essential information to describe a repository."""
    repository_id: int | None = Field(None, validation_alias="repositoryId", serialization_alias="repositoryId", description="Codacy identifier for this repository.", json_schema_extra={'format': 'int64'})
    provider: str
    owner: str = Field(..., description="Name of the organization that owns the repository.")
    name: str = Field(..., description="Name of the repository.")

class User(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    name: str | None = None
    main_email: str = Field(..., validation_alias="mainEmail", serialization_alias="mainEmail")
    other_emails: list[str] = Field(..., validation_alias="otherEmails", serialization_alias="otherEmails")
    is_admin: bool = Field(..., validation_alias="isAdmin", serialization_alias="isAdmin")
    is_active: bool = Field(..., validation_alias="isActive", serialization_alias="isActive")
    created: str = Field(..., json_schema_extra={'format': 'date-time'})
    intercom_hash: str | None = Field(None, validation_alias="intercomHash", serialization_alias="intercomHash")
    zendesk_hash: str | None = Field(None, validation_alias="zendeskHash", serialization_alias="zendeskHash")
    should_do_client_qualification: bool | None = Field(None, validation_alias="shouldDoClientQualification", serialization_alias="shouldDoClientQualification")

class Branch(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    name: str
    is_default: bool = Field(..., validation_alias="isDefault", serialization_alias="isDefault")
    is_enabled: bool = Field(..., validation_alias="isEnabled", serialization_alias="isEnabled")
    last_updated: str | None = Field(None, validation_alias="lastUpdated", serialization_alias="lastUpdated", json_schema_extra={'format': 'date-time'})
    branch_type: Literal["Branch", "PullRequest"] = Field(..., validation_alias="branchType", serialization_alias="branchType")
    last_commit: str | None = Field(None, validation_alias="lastCommit", serialization_alias="lastCommit")

class Organization(PermissiveModel):
    identifier: int | None = Field(None, json_schema_extra={'format': 'int64'})
    remote_identifier: str = Field(..., validation_alias="remoteIdentifier", serialization_alias="remoteIdentifier")
    name: str
    avatar: str | None = None
    created: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    provider: str
    join_mode: Literal["auto", "adminAuto", "request"] | None = Field(None, validation_alias="joinMode", serialization_alias="joinMode")
    type_: Literal["Account", "Organization"] = Field(..., validation_alias="type", serialization_alias="type")
    join_status: Literal["member", "pendingMember", "remoteMember"] | None = Field(None, validation_alias="joinStatus", serialization_alias="joinStatus")
    single_provider_login: bool = Field(..., validation_alias="singleProviderLogin", serialization_alias="singleProviderLogin")
    has_dast_access: bool = Field(..., validation_alias="hasDastAccess", serialization_alias="hasDastAccess")
    has_sca_enabled: bool = Field(..., validation_alias="hasScaEnabled", serialization_alias="hasScaEnabled")
    image_sbom_enabled: bool = Field(..., validation_alias="imageSbomEnabled", serialization_alias="imageSbomEnabled")

class Repository(PermissiveModel):
    repository_id: int | None = Field(None, validation_alias="repositoryId", serialization_alias="repositoryId", description="Codacy identifier for this repository.", json_schema_extra={'format': 'int64'})
    provider: str
    owner: str = Field(..., description="Name of the organization that owns the repository.")
    name: str = Field(..., description="Name of the repository.")
    full_path: str | None = Field(None, validation_alias="fullPath", serialization_alias="fullPath", description="Full path of the repository on the Git provider")
    visibility: Literal["Public", "Private", "LoginPublic"]
    remote_identifier: str | None = Field(None, validation_alias="remoteIdentifier", serialization_alias="remoteIdentifier", description="Unique identifier of the repository on the Git provider")
    last_updated: str | None = Field(None, validation_alias="lastUpdated", serialization_alias="lastUpdated", description="Timestamp when the repository was last updated. See [Git provider documentation](https://docs.codacy.com/organizations/organization-overview/#last-updated-repositories) for details.", json_schema_extra={'format': 'date-time'})
    permission: Literal["admin", "write", "read"] | None = None
    problems: list[RepositoryProblem]
    languages: list[str] = Field(..., description="List of the languages in the repository")
    default_branch: Branch | None = Field(None, validation_alias="defaultBranch", serialization_alias="defaultBranch")
    badges: Badges | None = None
    coding_standard_id: int | None = Field(None, validation_alias="codingStandardId", serialization_alias="codingStandardId", description="**Deprecated:** Use `standards` field instead. Coding standard identifier.", json_schema_extra={'format': 'int64'})
    coding_standard_name: str | None = Field(None, validation_alias="codingStandardName", serialization_alias="codingStandardName", description="**Deprecated:** Use `standards` field instead. Coding standard name.")
    standards: list[CodingStandardInfo] = Field(..., description="List of the coding standard identifiers and names")
    added_state: Literal["NotAdded", "Added", "Following"] = Field(..., validation_alias="addedState", serialization_alias="addedState")
    gate_policy_id: int | None = Field(None, validation_alias="gatePolicyId", serialization_alias="gatePolicyId", description="Identifier of the gate policy the repository is following. If not defined, the repository does not follow a gate policy.", json_schema_extra={'format': 'int64'})
    gate_policy_name: str | None = Field(None, validation_alias="gatePolicyName", serialization_alias="gatePolicyName", description="Name of the gate policy the repository is following. Present only if the gatePolicyId is defined.")


# Rebuild models to resolve forward references (required for circular refs)
ApiError.model_rebuild()
Badges.model_rebuild()
Branch.model_rebuild()
CodingStandardInfo.model_rebuild()
ConfiguredParameter.model_rebuild()
ConfiguredParametersList.model_rebuild()
ConfigurePattern.model_rebuild()
CreateJiraTicketElement.model_rebuild()
DimensionsFilter.model_rebuild()
Forbidden.model_rebuild()
Language.model_rebuild()
Organization.model_rebuild()
PayloadTooLarge.model_rebuild()
ProblemLink.model_rebuild()
PullRequest.model_rebuild()
PullRequestOwner.model_rebuild()
Repository.model_rebuild()
RepositoryLanguageUpdate.model_rebuild()
RepositoryProblem.model_rebuild()
RepositorySummary.model_rebuild()
User.model_rebuild()

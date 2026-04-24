"""
Api Reference MCP Server - Pydantic Models

Generated: 2026-04-24 11:01:40 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AddAMemberToAnOrganizationRequest",
    "AddAnOrganizationMemberToATeamRequest",
    "AddASymbolSourceToAProjectRequest",
    "AddATeamToAProjectRequest",
    "BulkDeleteAlertsRequest",
    "BulkDeleteMonitorsRequest",
    "BulkMutateAListOfIssuesRequest",
    "BulkMutateAnOrganizationSIssuesRequest",
    "BulkRemoveAListOfIssuesRequest",
    "BulkRemoveAnOrganizationSIssuesRequest",
    "CreateADataForwarderForAnOrganizationRequest",
    "CreateADeployRequest",
    "CreateAMonitorForAProjectRequest",
    "CreateAMonitorRequest",
    "CreateAnAlertForAnOrganizationRequest",
    "CreateANewClientKeyRequest",
    "CreateANewDashboardForAnOrganizationRequest",
    "CreateANewProjectRequest",
    "CreateANewReleaseForAnOrganizationRequest",
    "CreateANewSavedQueryRequest",
    "CreateANewTeamRequest",
    "CreateAnExternalTeamRequest",
    "CreateAnExternalUserRequest",
    "CreateOrUpdateAnExternalIssueRequest",
    "CreateReplayBatchDeletionJobRequest",
    "DebugIssuesRelatedToSourceMapsForAGivenEventRequest",
    "DeleteAClientKeyRequest",
    "DeleteACustomIntegrationRequest",
    "DeleteADataForwarderForAnOrganizationRequest",
    "DeleteAMonitorOrMonitorEnvironmentsForAProjectRequest",
    "DeleteAMonitorOrMonitorEnvironmentsRequest",
    "DeleteAMonitorRequest",
    "DeleteAnAlertRequest",
    "DeleteAnExternalIssueRequest",
    "DeleteAnExternalTeamRequest",
    "DeleteAnExternalUserRequest",
    "DeleteAnIntegrationForAnOrganizationRequest",
    "DeleteAnOrganizationMemberFromATeamRequest",
    "DeleteAnOrganizationMemberRequest",
    "DeleteAnOrganizationReleaseSFileRequest",
    "DeleteAnOrganizationSCustomDashboardRequest",
    "DeleteAnOrganizationSDiscoverSavedQueryRequest",
    "DeleteAnOrganizationSReleaseRequest",
    "DeleteAProjectReleaseSFileRequest",
    "DeleteAProjectRequest",
    "DeleteAReplayInstanceRequest",
    "DeleteASpecificProjectSDebugInformationFileRequest",
    "DeleteASymbolSourceFromAProjectRequest",
    "DeleteATeamFromAProjectRequest",
    "DeleteATeamRequest",
    "DeprecatedDeleteAnIssueAlertRuleRequest",
    "DeprecatedRetrieveAnIssueAlertRuleForAProjectRequest",
    "DeprecatedUpdateAMetricAlertRuleRequest",
    "DeprecatedUpdateAnIssueAlertRuleRequest",
    "DisableSpikeProtectionRequest",
    "EditAnOrganizationSCustomDashboardRequest",
    "EditAnOrganizationSDiscoverSavedQueryRequest",
    "EnableSpikeProtectionRequest",
    "FetchAlertsRequest",
    "FetchAMonitorRequest",
    "FetchAnAlertRequest",
    "FetchAnOrganizationSMonitorsRequest",
    "GetIntegrationProviderInformationRequest",
    "GetsSyncingStatusForRepositoriesForAnIntegratedOrgRequest",
    "GetTheLatestInstallableBuildForAProjectRequest",
    "ListAnIssueSEventsRequest",
    "ListAnIssueSHashesRequest",
    "ListAnOrganizationReleaseSCommitsRequest",
    "ListAnOrganizationSAvailableIntegrationsRequest",
    "ListAnOrganizationSClientKeysRequest",
    "ListAnOrganizationSCustomDashboardsRequest",
    "ListAnOrganizationSDiscoverSavedQueriesRequest",
    "ListAnOrganizationSEnvironmentsRequest",
    "ListAnOrganizationSIntegrationPlatformInstallationsRequest",
    "ListAnOrganizationSIssuesRequest",
    "ListAnOrganizationSMembersRequest",
    "ListAnOrganizationSPaginatedTeamsRequest",
    "ListAnOrganizationSProjectsRequest",
    "ListAnOrganizationSReleaseFilesRequest",
    "ListAnOrganizationSReleasesRequest",
    "ListAnOrganizationSReplaysRequest",
    "ListAnOrganizationSRepositoriesRequest",
    "ListAnOrganizationSScimMembersRequest",
    "ListAnOrganizationSSelectorsRequest",
    "ListAnOrganizationSTeamsRequest",
    "ListAnOrganizationSTrustedRelaysRequest",
    "ListAProjectReleaseSCommitsRequest",
    "ListAProjectSClientKeysRequest",
    "ListAProjectSDataFiltersRequest",
    "ListAProjectSDebugInformationFilesRequest",
    "ListAProjectSEnvironmentsRequest",
    "ListAProjectSErrorEventsRequest",
    "ListAProjectSIssuesRequest",
    "ListAProjectSOrganizationMembersRequest",
    "ListAProjectSReleaseFilesRequest",
    "ListAProjectSServiceHooksRequest",
    "ListAProjectSTeamsRequest",
    "ListAProjectSUserFeedbackRequest",
    "ListAProjectSUsersRequest",
    "ListAReleaseSDeploysRequest",
    "ListARepositorySCommitsRequest",
    "ListATagSValuesForAnIssueRequest",
    "ListATagSValuesRequest",
    "ListATeamSMembersRequest",
    "ListATeamSProjectsRequest",
    "ListAUserSTeamsForAnOrganizationRequest",
    "ListClickedNodesRequest",
    "ListRecordingSegmentsRequest",
    "ListReplayBatchDeletionJobsRequest",
    "ListSpikeProtectionNotificationsRequest",
    "ListUsersWhoHaveViewedAReplayRequest",
    "ListYourOrganizationsRequest",
    "MutateAnOrganizationSAlertsRequest",
    "MutateAnOrganizationSMonitorsRequest",
    "ProvisionANewOrganizationMemberRequest",
    "ProvisionANewTeamRequest",
    "QueryExploreEventsInTableFormatRequest",
    "QueryExploreEventsInTimeseriesFormatRequest",
    "RegeneratesARepositoryUploadTokenAndReturnsTheNewTokenRequest",
    "RemoveAnIssueRequest",
    "RemoveAServiceHookRequest",
    "ResolveAnEventIdRequest",
    "ResolveAShortIdRequest",
    "RetrieveAClientKeyRequest",
    "RetrieveACountOfReplaysForAGivenIssueOrTransactionRequest",
    "RetrieveACustomIntegrationByIdOrSlugRequest",
    "RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequest",
    "RetrieveAMonitorForAProjectRequest",
    "RetrieveAMonitorRequest",
    "RetrieveAnEventForAProjectRequest",
    "RetrieveAnIntegrationForAnOrganizationRequest",
    "RetrieveAnIssueEventRequest",
    "RetrieveAnIssueRequest",
    "RetrieveAnOrganizationMemberRequest",
    "RetrieveAnOrganizationReleaseSFileRequest",
    "RetrieveAnOrganizationRequest",
    "RetrieveAnOrganizationSCustomDashboardRequest",
    "RetrieveAnOrganizationSDiscoverSavedQueryRequest",
    "RetrieveAnOrganizationSEventsCountByProjectRequest",
    "RetrieveAnOrganizationSReleaseRequest",
    "RetrieveAProjectEnvironmentRequest",
    "RetrieveAProjectReleaseSFileRequest",
    "RetrieveAProjectRequest",
    "RetrieveAProjectSSymbolSourcesRequest",
    "RetrieveARecordingSegmentRequest",
    "RetrieveAReplayBatchDeletionJobRequest",
    "RetrieveAReplayInstanceRequest",
    "RetrieveAServiceHookRequest",
    "RetrieveASpikeProtectionNotificationActionRequest",
    "RetrieveATeamRequest",
    "RetrieveCheckInsForAMonitorByProjectRequest",
    "RetrieveCheckInsForAMonitorRequest",
    "RetrieveCustomIntegrationIssueLinksForTheGivenSentryIssueRequest",
    "RetrieveDataForwardersForAnOrganizationRequest",
    "RetrieveEventCountsForAnOrganizationV2Request",
    "RetrieveEventCountsForAProjectRequest",
    "RetrieveFilesChangedInAReleaseSCommitsRequest",
    "RetrieveInstallInfoForAGivenArtifactRequest",
    "RetrieveMonitorsForAnOrganizationRequest",
    "RetrieveOwnershipConfigurationForAProjectRequest",
    "RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequest",
    "RetrieveReleaseHealthSessionStatisticsRequest",
    "RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequest",
    "RetrievesASingleRepositoryForAGivenOwnerRequest",
    "RetrieveSeerIssueFixStateRequest",
    "RetrieveSizeAnalysisResultsForAGivenArtifactRequest",
    "RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequest",
    "RetrievesListOfRepositoriesForAGivenOwnerRequest",
    "RetrieveStatusesOfReleaseThresholdsAlphaRequest",
    "RetrieveTagDetailsRequest",
    "RetrieveTestSuitesBelongingToARepositorySTestResultsRequest",
    "RetrieveTheCustomIntegrationsCreatedByAnOrganizationRequest",
    "StartSeerIssueFixRequest",
    "SubmitUserFeedbackRequest",
    "SyncsRepositoriesFromAnIntegratedOrgWithGitHubRequest",
    "UpdateAClientKeyRequest",
    "UpdateADataForwarderForAnOrganizationRequest",
    "UpdateAMonitorByIdRequest",
    "UpdateAMonitorForAProjectRequest",
    "UpdateAMonitorRequest",
    "UpdateAnAlertByIdRequest",
    "UpdateAnExternalTeamRequest",
    "UpdateAnExternalUserRequest",
    "UpdateAnInboundDataFilterRequest",
    "UpdateAnIssueRequest",
    "UpdateAnOrganizationMemberSRolesRequest",
    "UpdateAnOrganizationMemberSTeamRoleRequest",
    "UpdateAnOrganizationReleaseFileRequest",
    "UpdateAnOrganizationRequest",
    "UpdateAnOrganizationSReleaseRequest",
    "UpdateAProjectEnvironmentRequest",
    "UpdateAProjectReleaseFileRequest",
    "UpdateAProjectRequest",
    "UpdateAProjectSSymbolSourceRequest",
    "UpdateAServiceHookRequest",
    "UpdateATeamRequest",
    "UpdateOwnershipConfigurationForAProjectRequest",
    "UploadANewFileRequest",
    "UploadANewOrganizationReleaseFileRequest",
    "UploadANewProjectReleaseFileRequest",
    "BulkMutateAnOrganizationSIssuesBodyStatusDetails",
    "CreateAMonitorBodyConfig",
    "CreateAMonitorForAProjectBodyConditionGroup",
    "CreateAnAlertForAnOrganizationBodyTriggers",
    "CreateANewDashboardForAnOrganizationBodyPermissions",
    "CreateANewDashboardForAnOrganizationBodyWidgetsItem",
    "CreateANewReleaseForAnOrganizationBodyRefsItem",
    "EditAnOrganizationSCustomDashboardBodyPermissions",
    "EditAnOrganizationSCustomDashboardBodyWidgetsItem",
    "UpdateAMonitorBodyConfig",
    "UpdateAMonitorByIdBodyConditionGroup",
    "UpdateAMonitorForAProjectBodyConfig",
    "UpdateAnAlertByIdBodyTriggers",
    "UpdateAnOrganizationSReleaseBodyRefsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_organizations
class ListYourOrganizationsRequestQuery(StrictModel):
    owner: bool | None = Field(default=None, description="Set to `true` to filter results to only organizations where you have owner-level permissions.")
    query: str | None = Field(default=None, description="Filter organizations using query syntax supporting multiple fields: `id`, `slug`, `status` (active, pending_deletion, or deletion_in_progress), `email` or `member_id` for specific members, `platform` for projects using a given platform, and `query` for substring matching against name, slug, and member information. Supports boolean operators (AND, OR) and complex expressions.")
class ListYourOrganizationsRequest(StrictModel):
    """Retrieve a list of organizations accessible to the authenticated session. For user-bound contexts, returns all member organizations; for API key requests, returns only the organization associated with that key."""
    query: ListYourOrganizationsRequestQuery | None = None

# Operation: get_organization
class RetrieveAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The unique identifier or slug of the organization. Use either the numeric ID or the URL-friendly slug name.")
class RetrieveAnOrganizationRequestQuery(StrictModel):
    detailed: str | None = Field(default=None, description="Set to `\"0\"` to retrieve only basic organization details while excluding projects and teams from the response. Omit to include full details.")
class RetrieveAnOrganizationRequest(StrictModel):
    """Retrieve detailed information about a specific organization, including membership access levels and associated teams."""
    path: RetrieveAnOrganizationRequestPath
    query: RetrieveAnOrganizationRequestQuery | None = None

# Operation: update_organization
class UpdateAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class UpdateAnOrganizationRequestBody(StrictModel):
    slug: str | None = Field(default=None, description="New organization slug for URLs; must be unique across the instance and not exceed 50 characters.", max_length=50)
    name: str | None = Field(default=None, description="New display name for the organization; limited to 64 characters.", max_length=64)
    is_early_adopter: bool | None = Field(default=None, validation_alias="isEarlyAdopter", serialization_alias="isEarlyAdopter", description="Enable early access to unreleased features and experimental functionality.")
    hide_ai_features: bool | None = Field(default=None, validation_alias="hideAiFeatures", serialization_alias="hideAiFeatures", description="Hide AI-powered features and recommendations from the organization's interface.")
    codecov_access: bool | None = Field(default=None, validation_alias="codecovAccess", serialization_alias="codecovAccess", description="Enable Code Coverage Insights for tracking test coverage trends; available only on Team plan and above.")
    default_role: Literal["member", "admin", "manager", "owner"] | None = Field(default=None, validation_alias="defaultRole", serialization_alias="defaultRole", description="Default role assigned to newly invited members: member, admin, manager, or owner.")
    open_membership: bool | None = Field(default=None, validation_alias="openMembership", serialization_alias="openMembership", description="Allow organization members to join any team without explicit invitation.")
    events_member_admin: bool | None = Field(default=None, validation_alias="eventsMemberAdmin", serialization_alias="eventsMemberAdmin", description="Grant all members the ability to delete events and use the delete & discard action.")
    alerts_member_write: bool | None = Field(default=None, validation_alias="alertsMemberWrite", serialization_alias="alertsMemberWrite", description="Grant all members the ability to create, edit, and delete alert rules.")
    attachments_role: Literal["member", "admin", "manager", "owner"] | None = Field(default=None, validation_alias="attachmentsRole", serialization_alias="attachmentsRole", description="Minimum role required to download event attachments such as crash reports and log files: member, admin, manager, or owner.")
    debug_files_role: Literal["member", "admin", "manager", "owner"] | None = Field(default=None, validation_alias="debugFilesRole", serialization_alias="debugFilesRole", description="Minimum role required to download debug files, ProGuard mappings, and source maps: member, admin, manager, or owner.")
    has_granular_replay_permissions: bool | None = Field(default=None, validation_alias="hasGranularReplayPermissions", serialization_alias="hasGranularReplayPermissions", description="Enable per-member access control for session replay data instead of role-based access.")
    replay_access_members: list[int] | None = Field(default=None, validation_alias="replayAccessMembers", serialization_alias="replayAccessMembers", description="List of user IDs granted access to replay data; only enforced when granular replay permissions are enabled.")
    avatar: str | None = Field(default=None, description="Organization avatar image encoded as base64; required when avatarType is set to upload.")
    require2fa: bool | None = Field(default=None, validation_alias="require2FA", serialization_alias="require2FA", description="Require and enforce two-factor authentication for all organization members.")
    allow_shared_issues: bool | None = Field(default=None, validation_alias="allowSharedIssues", serialization_alias="allowSharedIssues", description="Allow sharing of limited issue details with anonymous users via public links.")
    enhanced_privacy: bool | None = Field(default=None, validation_alias="enhancedPrivacy", serialization_alias="enhancedPrivacy", description="Enable enhanced privacy mode to minimize personally identifiable information and source code in notifications and exports.")
    scrape_java_script: bool | None = Field(default=None, validation_alias="scrapeJavaScript", serialization_alias="scrapeJavaScript", description="Allow Sentry to automatically fetch missing JavaScript source context from public CDNs when available.")
    store_crash_reports: Literal[0, 1, 5, 10, 20, 50, 100, -1] | None = Field(default=None, validation_alias="storeCrashReports", serialization_alias="storeCrashReports", description="Number of native crash reports (minidumps, etc.) to retain per issue: 0 (disabled), 1, 5, 10, 20, 50, 100, or -1 (unlimited).")
    allow_join_requests: bool | None = Field(default=None, validation_alias="allowJoinRequests", serialization_alias="allowJoinRequests", description="Allow users to submit requests to join the organization without requiring an explicit invitation.")
    data_scrubber_defaults: bool | None = Field(default=None, validation_alias="dataScrubberDefaults", serialization_alias="dataScrubberDefaults", description="Apply default data scrubbers organization-wide to prevent sensitive data like passwords and credit card numbers from being stored.")
    sensitive_fields: list[str] | None = Field(default=None, validation_alias="sensitiveFields", serialization_alias="sensitiveFields", description="List of additional field names to scrub across all projects; matched against event data during processing.")
    safe_fields: list[str] | None = Field(default=None, validation_alias="safeFields", serialization_alias="safeFields", description="List of field names that data scrubbers should explicitly ignore and not redact.")
    scrub_ip_addresses: bool | None = Field(default=None, validation_alias="scrubIPAddresses", serialization_alias="scrubIPAddresses", description="Prevent IP addresses from being stored in new events across all projects.")
    relay_pii_config: str | None = Field(default=None, validation_alias="relayPiiConfig", serialization_alias="relayPiiConfig", description="Advanced data scrubbing rules as a JSON string for masking or removing sensitive data patterns; overwrites existing rules and applies only to new events. See documentation for rule syntax and examples.")
    trusted_relays: list[dict[str, Any]] | None = Field(default=None, validation_alias="trustedRelays", serialization_alias="trustedRelays", description="List of local Relay instances registered for the organization, each containing name, public key, and description; available only on Business and Enterprise plans.")
    github_pr_bot: bool | None = Field(default=None, validation_alias="githubPRBot", serialization_alias="githubPRBot", description="Enable Sentry to post comments on recent GitHub pull requests suspected of introducing issues; requires GitHub integration.")
    github_nudge_invite: bool | None = Field(default=None, validation_alias="githubNudgeInvite", serialization_alias="githubNudgeInvite", description="Enable Sentry to detect GitHub repository committers not yet in the organization and suggest invitations; requires GitHub integration.")
    gitlab_pr_bot: bool | None = Field(default=None, validation_alias="gitlabPRBot", serialization_alias="gitlabPRBot", description="Enable Sentry to post comments on recent GitLab merge requests suspected of introducing issues; requires GitLab integration.")
    issue_alerts_thread_flag: bool | None = Field(default=None, validation_alias="issueAlertsThreadFlag", serialization_alias="issueAlertsThreadFlag", description="Allow Sentry Slack integration to post Issue Alert notifications as threaded replies instead of standalone messages; requires Slack integration.")
    metric_alerts_thread_flag: bool | None = Field(default=None, validation_alias="metricAlertsThreadFlag", serialization_alias="metricAlertsThreadFlag", description="Allow Sentry Slack integration to post Metric Alert notifications as threaded replies instead of standalone messages; requires Slack integration.")
    cancel_deletion: bool | None = Field(default=None, validation_alias="cancelDeletion", serialization_alias="cancelDeletion", description="Restore an organization that is currently scheduled for deletion, canceling the deletion process.")
class UpdateAnOrganizationRequest(StrictModel):
    """Update organization settings, membership policies, security configurations, data privacy controls, and integration permissions. Changes apply to all projects within the organization."""
    path: UpdateAnOrganizationRequestPath
    body: UpdateAnOrganizationRequestBody | None = None

# Operation: update_metric_alert_rule
class DeprecatedUpdateAMetricAlertRuleRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The ID or slug of the organization that owns the alert rule.")
    alert_rule_id: int = Field(default=..., description="The numeric ID of the alert rule to update.")
class DeprecatedUpdateAMetricAlertRuleRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the alert rule, up to 256 characters.", max_length=256)
    aggregate: str = Field(default=..., description="The aggregate function to apply to the metric. Valid options are: count, count_unique, percentage, avg, apdex, failure_rate, p50, p75, p95, p99, p100, or percentile.")
    time_window: Literal[1, 5, 10, 15, 30, 60, 120, 240, 1440] = Field(default=..., validation_alias="timeWindow", serialization_alias="timeWindow", description="The time window over which to aggregate the metric. Valid options are: 1 minute, 5 minutes, 10 minutes, 15 minutes, 30 minutes, 1 hour, 2 hours, 4 hours, or 24 hours.")
    projects: list[str] = Field(default=..., description="A list of project names to monitor. The alert will only apply to events from these projects.")
    query: str = Field(default=..., description="An event search query to filter which events trigger the alert (e.g., 'http.status_code:400'). Use an empty string to monitor all events without filtering.")
    threshold_type: Literal[0, 1] = Field(default=..., validation_alias="thresholdType", serialization_alias="thresholdType", description="The comparison operator for thresholds: 0 for 'Above' or 1 for 'Below'. The resolved threshold operator is automatically set to the opposite.")
    triggers: list[Any] = Field(default=..., description="A list of trigger objects, each with a label (critical or warning), alertThreshold value, and actions array. At least one critical trigger is required. Actions specify how to notify (email, Slack, PagerDuty, etc.) and to whom.")
    environment: str | None = Field(default=None, description="Optional environment name to filter events by (e.g., 'production', 'staging'). Defaults to all environments if not specified.")
    dataset: str | None = Field(default=None, description="The dataset to query: events, transactions, metrics, sessions, or generic-metrics. Defaults to events.")
    query_type: Literal[0, 1, 2] | None = Field(default=None, validation_alias="queryType", serialization_alias="queryType", description="The query type: 0 for error events, 1 for transactions, or 2 for none. Defaults based on the specified dataset if not provided.")
    event_types: list[str] | None = Field(default=None, validation_alias="eventTypes", serialization_alias="eventTypes", description="Optional list of event types to monitor: default (Capture Message events), error, or transaction.")
    comparison_delta: int | None = Field(default=None, validation_alias="comparisonDelta", serialization_alias="comparisonDelta", description="Optional time delta in minutes for percentage change comparisons. Required when using a percentage change threshold (e.g., 'x% higher than 60 minutes ago'). Not supported for Crash Free Session/User Rate alerts.")
    resolve_threshold: float | None = Field(default=None, validation_alias="resolveThreshold", serialization_alias="resolveThreshold", description="Optional threshold value at which the alert resolves. If not provided, it is automatically set based on the lowest severity trigger's threshold. Must be greater than the critical threshold when thresholdType is 0, or less than the critical threshold when thresholdType is 1.", json_schema_extra={'format': 'double'})
    owner: str | None = Field(default=None, description="Optional ID of the team or user that owns this alert rule.")
class DeprecatedUpdateAMetricAlertRuleRequest(StrictModel):
    """Update a metric alert rule configuration that defines conditions for triggering alerts based on metrics like error count, latency, or failure rate. Warning: This operation fully overwrites the specified metric alert rule. (Deprecated: use Update a Monitor by ID or Update an Alert by ID instead)"""
    path: DeprecatedUpdateAMetricAlertRuleRequestPath
    body: DeprecatedUpdateAMetricAlertRuleRequestBody

# Operation: list_integration_providers
class GetIntegrationProviderInformationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class GetIntegrationProviderInformationRequestQuery(StrictModel):
    provider_key: str | None = Field(default=None, validation_alias="providerKey", serialization_alias="providerKey", description="Optional filter to retrieve details for a single integration provider (e.g., 'slack'). When omitted, information for all available providers is returned.")
class GetIntegrationProviderInformationRequest(StrictModel):
    """Retrieve information about all available integration providers for an organization, with optional filtering by a specific provider type."""
    path: GetIntegrationProviderInformationRequestPath
    query: GetIntegrationProviderInformationRequestQuery | None = None

# Operation: list_organization_dashboards
class ListAnOrganizationSCustomDashboardsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The unique identifier or slug of the organization. Use either the numeric ID or the organization's URL-friendly slug.")
class ListAnOrganizationSCustomDashboardsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of dashboards to return in a single response. Defaults to 100 if not specified; cannot exceed 100.")
class ListAnOrganizationSCustomDashboardsRequest(StrictModel):
    """Retrieve all custom dashboards associated with an organization. Results can be paginated to control the number of dashboards returned per request."""
    path: ListAnOrganizationSCustomDashboardsRequestPath
    query: ListAnOrganizationSCustomDashboardsRequestQuery | None = None

# Operation: create_dashboard
class CreateANewDashboardForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class CreateANewDashboardForAnOrganizationRequestBody(StrictModel):
    title: str = Field(default=..., description="A human-readable name for the dashboard. Limited to 255 characters.", max_length=255)
    widgets: list[CreateANewDashboardForAnOrganizationBodyWidgetsItem] | None = Field(default=None, description="An ordered list of widget objects that define the visualizations and data displayed on the dashboard.")
    projects: list[int] | None = Field(default=None, description="A list of project identifiers to filter dashboard data to specific projects.")
    environment: list[str] | None = Field(default=None, description="A list of environment names to filter dashboard data to specific environments.")
    filters: dict[str, Any] | None = Field(default=None, description="A structured object containing saved search filters and query parameters applied to the dashboard.")
    utc: bool | None = Field(default=None, description="When enabled, displays all time ranges and timestamps on the dashboard in UTC timezone instead of the user's local timezone.")
    permissions: CreateANewDashboardForAnOrganizationBodyPermissions | None = Field(default=None, description="Access control settings that determine which users can view and edit this dashboard.")
    is_favorited: bool | None = Field(default=None, description="When set to true, automatically adds this dashboard to the requesting user's favorites list.")
class CreateANewDashboardForAnOrganizationRequest(StrictModel):
    """Create a new dashboard for an organization to visualize and monitor project metrics, events, and custom data. Dashboards can include widgets, project filters, environment filters, and saved search criteria."""
    path: CreateANewDashboardForAnOrganizationRequestPath
    body: CreateANewDashboardForAnOrganizationRequestBody

# Operation: get_organization_dashboard
class RetrieveAnOrganizationSCustomDashboardRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    dashboard_id: int = Field(default=..., description="The numeric ID of the dashboard to retrieve.")
class RetrieveAnOrganizationSCustomDashboardRequest(StrictModel):
    """Retrieve detailed information about a specific custom dashboard within an organization, including its configuration and contents."""
    path: RetrieveAnOrganizationSCustomDashboardRequestPath

# Operation: update_organization_dashboard
class EditAnOrganizationSCustomDashboardRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    dashboard_id: int = Field(default=..., description="The numeric ID of the dashboard to update.")
class EditAnOrganizationSCustomDashboardRequestBody(StrictModel):
    title: str | None = Field(default=None, description="The dashboard's display name. Must not exceed 255 characters.", max_length=255)
    widgets: list[EditAnOrganizationSCustomDashboardBodyWidgetsItem] | None = Field(default=None, description="An ordered array of widget objects representing the dashboard's visualizations. Each widget can include query definitions, field selections, and display type configurations.")
    projects: list[int] | None = Field(default=None, description="An array of project identifiers to filter the dashboard's data scope. Only events from these projects will be displayed.")
    environment: list[str] | None = Field(default=None, description="An array of environment names to filter the dashboard's data scope. Only events from these environments will be displayed.")
    filters: dict[str, Any] | None = Field(default=None, description="An object containing saved filter criteria applied across the dashboard. Filters are applied to all widgets unless overridden at the widget level.")
    utc: bool | None = Field(default=None, description="When enabled, displays all saved time ranges and timestamps in UTC timezone instead of the user's local timezone.")
    permissions: EditAnOrganizationSCustomDashboardBodyPermissions | None = Field(default=None, description="Access control settings that define which users can view or edit this dashboard.")
class EditAnOrganizationSCustomDashboardRequest(StrictModel):
    """Update an organization's custom dashboard configuration, including its title, widgets, filters, and display settings. Supports bulk edits to widget arrangements, queries, fields, and display types."""
    path: EditAnOrganizationSCustomDashboardRequestPath
    body: EditAnOrganizationSCustomDashboardRequestBody | None = None

# Operation: delete_organization_dashboard
class DeleteAnOrganizationSCustomDashboardRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    dashboard_id: int = Field(default=..., description="The numeric ID of the dashboard to delete.")
class DeleteAnOrganizationSCustomDashboardRequest(StrictModel):
    """Delete an organization's custom dashboard or tombstone a pre-built dashboard to effectively remove it from the organization."""
    path: DeleteAnOrganizationSCustomDashboardRequestPath

# Operation: list_organization_monitors
class FetchAnOrganizationSMonitorsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's monitors are returned.")
class FetchAnOrganizationSMonitorsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional search query to filter monitors by name, type (e.g., error, metric_issue, issue_stream), or assignee (email, username, team reference with # prefix, 'me', or 'none').")
class FetchAnOrganizationSMonitorsRequest(StrictModel):
    """Retrieve all monitors configured for an organization. This endpoint supports the new monitoring and alerting system and allows filtering by monitor properties such as name, type, and assignee."""
    path: FetchAnOrganizationSMonitorsRequestPath
    query: FetchAnOrganizationSMonitorsRequestQuery | None = None

# Operation: update_organization_monitors_enabled_state
class MutateAnOrganizationSMonitorsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the organization slug.")
class MutateAnOrganizationSMonitorsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional search query to filter which monitors are affected. Supports filtering by monitor name, type (such as error, metric_issue, or issue_stream), or assignee (email, username, team reference with # prefix, 'me', or 'none').")
class MutateAnOrganizationSMonitorsRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="Set to true to enable the selected monitors or false to disable them.")
class MutateAnOrganizationSMonitorsRequest(StrictModel):
    """Bulk enable or disable monitors across an organization, optionally filtered by search criteria. This beta endpoint supports the New Monitors and Alerts system."""
    path: MutateAnOrganizationSMonitorsRequestPath
    query: MutateAnOrganizationSMonitorsRequestQuery | None = None
    body: MutateAnOrganizationSMonitorsRequestBody

# Operation: delete_monitors_bulk
class BulkDeleteMonitorsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the organization slug.")
class BulkDeleteMonitorsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional search query to filter which monitors to delete. Supports filtering by name, type (error, metric_issue, issue_stream), or assignee (email, username, #team, me, none).")
class BulkDeleteMonitorsRequest(StrictModel):
    """Bulk delete monitors for an organization, optionally filtered by search criteria. This beta endpoint supports the New Monitors and Alerts system."""
    path: BulkDeleteMonitorsRequestPath
    query: BulkDeleteMonitorsRequestQuery | None = None

# Operation: get_monitor_detector
class FetchAMonitorRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    detector_id: int = Field(default=..., description="The numeric ID of the monitor to retrieve.")
class FetchAMonitorRequest(StrictModel):
    """Retrieve detailed information about a specific monitor (detector). This endpoint is part of the New Monitors and Alerts system and is currently in beta."""
    path: FetchAMonitorRequestPath

# Operation: update_monitor_detector
class UpdateAMonitorByIdRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
    detector_id: int = Field(default=..., description="The numeric ID of the monitor to update.")
class UpdateAMonitorByIdRequestBody(StrictModel):
    name: str = Field(default=..., description="Display name for the monitor. Maximum 200 characters.", max_length=200)
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The monitor classification type. Currently supports `metric_issue` for metric-based monitoring.")
    workflow_ids: list[int] | None = Field(default=None, description="Array of alert workflow IDs to connect this monitor to. Use the Fetch Alerts endpoint to discover available workflow IDs.")
    data_sources: list[Any] | None = Field(default=None, description="Array of data source configurations defining what metric to measure. Each source specifies the aggregate function (e.g., count(), p95(span.duration)), dataset (events, events_analytics_platform, or generic_metrics), environment, event types to include, query filters, query type, and time window in seconds. Refer to monitor type examples for valid aggregate and dataset combinations.")
    config: dict[str, Any] | None = Field(default=None, description="Detection algorithm configuration. Choose `static` for threshold-based alerts, `percent` for change-based detection (requires comparisonDelta in minutes), or `dynamic` for anomaly detection.")
    condition_group: UpdateAMonitorByIdBodyConditionGroup | None = Field(default=None, description="Condition group defining alert triggers and priority levels. Specify logic type, conditions with comparison operators (gt, lte, anomaly_detection), threshold values, and resulting issue states (75=high priority, 50=low priority, 0=resolved). For dynamic monitors, configure seasonality, sensitivity (low/medium/high), and threshold direction.")
    owner: str | None = Field(default=None, description="Owner assignment as either a user ID (prefixed with 'user:') or team ID (prefixed with 'team:'). Example: 'user:123456' or 'team:456789'.")
    description: str | None = Field(default=None, description="Detailed description of the monitor's purpose and scope. Will be included in generated issues.")
    enabled: bool | None = Field(default=None, description="Boolean flag to enable or disable the monitor. Set to false to deactivate without deleting.")
class UpdateAMonitorByIdRequest(StrictModel):
    """Update an existing metric monitor with new configuration, data sources, detection rules, and alert connections. This beta endpoint supports threshold-based, change-based, and dynamic anomaly detection monitors."""
    path: UpdateAMonitorByIdRequestPath
    body: UpdateAMonitorByIdRequestBody

# Operation: delete_monitor
class DeleteAMonitorRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug of the organization that owns the monitor.")
    detector_id: int = Field(default=..., description="The numeric ID of the monitor to delete.")
class DeleteAMonitorRequest(StrictModel):
    """Permanently delete a monitor (detector) from an organization. This beta endpoint is part of the New Monitors and Alerts system and may not yet be visible in the UI."""
    path: DeleteAMonitorRequestPath

# Operation: list_organization_discover_saved_queries
class ListAnOrganizationSDiscoverSavedQueriesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL-friendly slug.")
class ListAnOrganizationSDiscoverSavedQueriesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of results to return per page, up to 100 (default is 100).")
    query: str | None = Field(default=None, description="Filter results by the exact or partial name of the saved Discover query.")
class ListAnOrganizationSDiscoverSavedQueriesRequest(StrictModel):
    """Retrieve all saved Discover queries associated with an organization, with optional filtering by query name and pagination support."""
    path: ListAnOrganizationSDiscoverSavedQueriesRequestPath
    query: ListAnOrganizationSDiscoverSavedQueriesRequestQuery | None = None

# Operation: create_saved_query
class CreateANewSavedQueryRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
class CreateANewSavedQueryRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the saved query, up to 255 characters.", max_length=255)
    projects: list[int] | None = Field(default=None, description="An array of project IDs to filter the query results by. If omitted, the query applies to all projects in the organization.")
    range_: str | None = Field(default=None, validation_alias="range", serialization_alias="range", description="A time range period for the query (e.g., '24h', '7d', '30d'). Defines the default time window when the saved query is loaded.")
    fields: list[str] | None = Field(default=None, description="An array of up to 20 fields, functions, or equations to retrieve. Fields can be event properties (e.g., 'transaction'), tags (e.g., 'tag[isEnterprise]'), functions (e.g., 'count_if(transaction.duration,greater,300)'), or equations prefixed with 'equation|'.")
    orderby: str | None = Field(default=None, description="The field or function to sort results by. Must be one of the fields specified in the fields array, and cannot be an equation.")
    environment: list[str] | None = Field(default=None, description="An array of environment names to filter the query by (e.g., 'production', 'staging'). If omitted, all environments are included.")
    query: str | None = Field(default=None, description="A search query using Sentry's query syntax to filter results further. Supports boolean operators and field-specific filters.")
    y_axis: list[str] | None = Field(default=None, validation_alias="yAxis", serialization_alias="yAxis", description="An array of aggregate functions to plot on the chart (e.g., 'count()', 'avg(transaction.duration)'). Used for time-series visualization.")
    display: str | None = Field(default=None, description="The chart visualization type: 'default' (line chart), 'previous' (comparison), 'top5' (top 5 series), 'daily' (daily breakdown), 'dailytop5' (daily top 5), or 'bar' (bar chart).")
    top_events: int | None = Field(default=None, validation_alias="topEvents", serialization_alias="topEvents", description="The number of top events' time-series to display on the chart, between 1 and 10. Only applies when using top-events visualization modes.", ge=1, le=10)
class CreateANewSavedQueryRequest(StrictModel):
    """Create a new saved query for an organization to store custom Discover search configurations, including filters, fields, aggregations, and visualization settings."""
    path: CreateANewSavedQueryRequestPath
    body: CreateANewSavedQueryRequestBody

# Operation: get_discover_saved_query
class RetrieveAnOrganizationSDiscoverSavedQueryRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    query_id: int = Field(default=..., description="The numeric ID of the saved Discover query to retrieve.")
class RetrieveAnOrganizationSDiscoverSavedQueryRequest(StrictModel):
    """Retrieve a saved Discover query by its ID within a specific organization. This returns the full configuration and metadata of the saved query."""
    path: RetrieveAnOrganizationSDiscoverSavedQueryRequestPath

# Operation: update_discover_saved_query
class EditAnOrganizationSDiscoverSavedQueryRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    query_id: int = Field(default=..., description="The numeric ID of the saved Discover query to modify.")
class EditAnOrganizationSDiscoverSavedQueryRequestBody(StrictModel):
    name: str = Field(default=..., description="A user-defined name for the saved query. Maximum 255 characters.", max_length=255)
    projects: list[int] | None = Field(default=None, description="Array of project IDs to filter the query results by. Order is not significant.")
    range_: str | None = Field(default=None, validation_alias="range", serialization_alias="range", description="A time range period for the query (e.g., '24h', '7d', '30d'). Determines the lookback window for events.")
    fields: list[str] | None = Field(default=None, description="Array of fields, functions, or equations to retrieve in query results. Maximum 20 items per request. Supports built-in event properties, tags (prefixed with 'tag['), aggregate functions, and equations (prefixed with 'equation|'). When functions are included, results are automatically grouped by tags and fields.")
    orderby: str | None = Field(default=None, description="Field or function name to sort results by. Must be a value from the fields array, excluding equations.")
    environment: list[str] | None = Field(default=None, description="Array of environment names to filter results by (e.g., 'production', 'staging'). Order is not significant.")
    query: str | None = Field(default=None, description="Query filter expression using Sentry's search syntax to narrow results by event properties and tags.")
    y_axis: list[str] | None = Field(default=None, validation_alias="yAxis", serialization_alias="yAxis", description="Array of aggregate functions to plot on the chart (e.g., 'count()', 'avg(transaction.duration)'). Order determines axis positioning.")
    display: str | None = Field(default=None, description="Chart visualization type. Choose from: default, previous, top5, daily, dailytop5, or bar.")
    top_events: int | None = Field(default=None, validation_alias="topEvents", serialization_alias="topEvents", description="Number of top events' timeseries to display on the chart. Must be between 1 and 10.", ge=1, le=10)
class EditAnOrganizationSDiscoverSavedQueryRequest(StrictModel):
    """Modify an existing saved Discover query, including its name, filters, fields, visualization settings, and aggregations."""
    path: EditAnOrganizationSDiscoverSavedQueryRequestPath
    body: EditAnOrganizationSDiscoverSavedQueryRequestBody

# Operation: delete_discover_saved_query
class DeleteAnOrganizationSDiscoverSavedQueryRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    query_id: int = Field(default=..., description="The numeric ID of the saved Discover query to delete.")
class DeleteAnOrganizationSDiscoverSavedQueryRequest(StrictModel):
    """Permanently delete a saved Discover query from an organization. This action cannot be undone."""
    path: DeleteAnOrganizationSDiscoverSavedQueryRequestPath

# Operation: list_organization_environments
class ListAnOrganizationSEnvironmentsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The unique identifier or slug of the organization. You can use either the numeric ID or the organization's URL-friendly slug.")
class ListAnOrganizationSEnvironmentsRequestQuery(StrictModel):
    visibility: Literal["all", "hidden", "visible"] | None = Field(default=None, description="Filter environments by their visibility status. Choose 'visible' to show only active environments, 'hidden' to show only inactive ones, or 'all' to retrieve both. Defaults to 'visible' if not specified.")
class ListAnOrganizationSEnvironmentsRequest(StrictModel):
    """Retrieves all environments for a specified organization, with optional filtering by visibility status. Use this to discover available deployment environments and their configurations."""
    path: ListAnOrganizationSEnvironmentsRequestPath
    query: ListAnOrganizationSEnvironmentsRequestQuery | None = None

# Operation: resolve_event_id
class ResolveAnEventIdRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    event_id: str = Field(default=..., description="The event ID to resolve. This is the unique identifier for the event you want to look up.")
class ResolveAnEventIdRequest(StrictModel):
    """Resolves an event ID to retrieve the associated project slug, internal issue ID, and internal event ID for a given organization."""
    path: ResolveAnEventIdRequestPath

# Operation: search_events_in_table_format
class QueryExploreEventsInTableFormatRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL-friendly slug.")
class QueryExploreEventsInTableFormatRequestQuery(StrictModel):
    field: list[str] = Field(default=..., description="The columns to include in results. Select up to 20 fields, which can be built-in properties (e.g., transaction, environment), tags in tag[name, type] format, functions like count() or count_if(), or equations prefixed with equation|. See searchable properties documentation for available fields per dataset.")
    dataset: Literal["logs", "profile_functions", "spans", "uptime_results"] = Field(default=..., description="The data source to query. Choose from logs, profile_functions, spans, or uptime_results; available fields vary by dataset.")
    environment: list[str] | None = Field(default=None, description="Filter results to specific environment names. Provide as a comma-separated list or multiple array values.")
    per_page: int | None = Field(default=None, description="Maximum number of result rows to return, up to 100 (default is 100).")
    query: str | None = Field(default=None, description="Filter events using Sentry query syntax with logical operators (AND, OR) and field conditions. Example: (transaction:foo AND release:abc) OR (transaction:[bar,baz]).")
class QueryExploreEventsInTableFormatRequest(StrictModel):
    """Retrieves a table of events from a specified organization matching your query criteria. Use this to explore event data with selected fields and optional filtering; not intended for full data exports."""
    path: QueryExploreEventsInTableFormatRequestPath
    query: QueryExploreEventsInTableFormatRequestQuery

# Operation: get_events_timeseries
class QueryExploreEventsInTimeseriesFormatRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL slug.")
class QueryExploreEventsInTimeseriesFormatRequestQuery(StrictModel):
    dataset: Literal["logs", "profile_functions", "spans", "uptime_results"] = Field(default=..., description="The dataset to query. Different datasets provide different available fields: logs, profile_functions, spans, or uptime_results.")
    environment: list[str] | None = Field(default=None, description="Filter results to specific environments by name. Accepts multiple environment names as an array.")
    top_events: int | None = Field(default=None, validation_alias="topEvents", serialization_alias="topEvents", description="Return the top N events by the sort criteria. Must be between 1 and 10. When specified, both groupBy and sort parameters become required.")
    comparison_delta: int | None = Field(default=None, validation_alias="comparisonDelta", serialization_alias="comparisonDelta", description="Return an additional offset timeseries shifted by this many seconds for comparison purposes.")
    group_by: list[str] | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="Fields to group results by, determining which events are considered 'top' when used with topEvents. Required when topEvents is specified. Accepts multiple field names as an array.")
    y_axis: str | None = Field(default=None, validation_alias="yAxis", serialization_alias="yAxis", description="The aggregate function to compute for the timeseries (e.g., count(), sum(), avg()). Defaults to count() if not provided.")
    query: str | None = Field(default=None, description="Filter results using Sentry query syntax. Supports boolean operators (AND, OR) and field matching with ranges or multiple values.")
class QueryExploreEventsInTimeseriesFormatRequest(StrictModel):
    """Retrieves event data for an organization as a timeseries, supporting single or multiple axes with optional grouping by top events. Results can be filtered by environment, time range, and custom query syntax."""
    path: QueryExploreEventsInTimeseriesFormatRequestPath
    query: QueryExploreEventsInTimeseriesFormatRequestQuery

# Operation: link_external_user
class CreateAnExternalUserRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
class CreateAnExternalUserRequestBody(StrictModel):
    user_id: int = Field(default=..., description="The numeric ID of the Sentry user to link to the external provider.")
    external_name: str = Field(default=..., description="The display name or username associated with the user in the external provider system.")
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(default=..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems.")
    integration_id: int = Field(default=..., description="The numeric ID of the integration configuration that connects Sentry to the external provider.")
    external_id: str | None = Field(default=None, description="The unique user identifier or account ID assigned by the external provider. This is optional if the external name is sufficient for identification.")
class CreateAnExternalUserRequest(StrictModel):
    """Link a user from an external provider (such as GitHub, Slack, Jira, or GitLab) to a Sentry user account, enabling cross-platform identity mapping and integration."""
    path: CreateAnExternalUserRequestPath
    body: CreateAnExternalUserRequestBody

# Operation: update_external_user
class UpdateAnExternalUserRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    external_user_id: int = Field(default=..., description="The unique identifier of the external user object to update, returned when the external user was initially created.")
class UpdateAnExternalUserRequestBody(StrictModel):
    user_id: int = Field(default=..., description="The numeric ID of the Sentry user account that this external user is linked to.")
    external_name: str = Field(default=..., description="The display name or username for this user in the external provider's system.")
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(default=..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems.")
    integration_id: int = Field(default=..., description="The numeric ID of the integration configuration that connects Sentry to the external provider.")
    external_id: str | None = Field(default=None, description="The user's unique identifier within the external provider system (e.g., user ID, handle, or account number). Optional if already set.")
class UpdateAnExternalUserRequest(StrictModel):
    """Update the details of an external user account linked to a Sentry user. This synchronizes user information across integrated external providers like GitHub, Slack, Jira, or GitLab."""
    path: UpdateAnExternalUserRequestPath
    body: UpdateAnExternalUserRequestBody

# Operation: delete_external_user
class DeleteAnExternalUserRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    external_user_id: int = Field(default=..., description="The unique identifier of the external user object to delete. This ID is provided when the external user is initially created.")
class DeleteAnExternalUserRequest(StrictModel):
    """Remove the link between an external provider user and a Sentry user account, effectively disconnecting the external identity from the organization."""
    path: DeleteAnExternalUserRequestPath

# Operation: list_data_forwarders_for_organization
class RetrieveDataForwardersForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
class RetrieveDataForwardersForAnOrganizationRequest(StrictModel):
    """Retrieves all data forwarders configured for a specific organization. Data forwarders enable automatic forwarding of events and data to external destinations."""
    path: RetrieveDataForwardersForAnOrganizationRequestPath

# Operation: create_data_forwarder_for_organization
class CreateADataForwarderForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the organization slug.")
class CreateADataForwarderForAnOrganizationRequestBody(StrictModel):
    organization_id: int = Field(default=..., description="The numeric ID of the organization that will own this data forwarder.")
    provider: Literal["segment", "sqs", "splunk"] = Field(default=..., description="The data destination provider: Segment, Amazon SQS, or Splunk. Each provider requires specific configuration keys.")
    is_enabled: bool | None = Field(default=None, description="Whether the data forwarder is active and forwarding data. Defaults to enabled.")
    enroll_new_projects: bool | None = Field(default=None, description="Whether newly created projects are automatically enrolled with this data forwarder. Defaults to disabled.")
    config: dict[str, str] | None = Field(default=None, description="Provider-specific configuration object. For SQS: queue_url, region, access_key, secret_key (required), plus optional message_group_id for FIFO queues and optional s3_bucket. For Segment: write_key (required). For Splunk: instance_url, index, source, token (all required).")
    project_ids: list[int] | None = Field(default=None, description="List of project IDs to enroll with this data forwarder. Projects not included will be unenrolled if they were previously connected.")
class CreateADataForwarderForAnOrganizationRequest(StrictModel):
    """Creates a new data forwarder for an organization to forward data to external providers like Segment, Amazon SQS, or Splunk. Only one data forwarder per provider is allowed per organization."""
    path: CreateADataForwarderForAnOrganizationRequestPath
    body: CreateADataForwarderForAnOrganizationRequestBody

# Operation: update_data_forwarder
class UpdateADataForwarderForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the organization slug.")
    data_forwarder_id: int = Field(default=..., description="The numeric ID of the data forwarder to update.")
class UpdateADataForwarderForAnOrganizationRequestBody(StrictModel):
    organization_id: int = Field(default=..., description="The numeric ID of the organization that owns the data forwarder.")
    provider: Literal["segment", "sqs", "splunk"] = Field(default=..., description="The data forwarding provider: Segment, Amazon SQS, or Splunk. Each provider requires specific configuration fields.")
    is_enabled: bool | None = Field(default=None, description="Whether the data forwarder is active. Defaults to true if not specified.")
    enroll_new_projects: bool | None = Field(default=None, description="Whether newly created projects should automatically be enrolled with this forwarder. Defaults to false if not specified.")
    config: dict[str, str] | None = Field(default=None, description="Provider-specific configuration object. For SQS: requires queue_url, region, access_key, secret_key (and message_group_id for FIFO queues; s3_bucket is optional). For Segment: requires write_key. For Splunk: requires instance_url, index, source, and token. When updating organization-level configuration, provide the complete config; for project overrides, only include fields to override.")
    project_ids: list[int] | None = Field(default=None, description="Array of project numeric IDs to connect to this forwarder. Projects not included will be unenrolled if previously connected. Required when updating organization-level configuration.")
class UpdateADataForwarderForAnOrganizationRequest(StrictModel):
    """Updates a data forwarder configuration for an organization, or creates/modifies project-specific overrides. Organization-level updates require the full configuration including project IDs, while project-level overrides only need the project ID, overrides object, and enabled status."""
    path: UpdateADataForwarderForAnOrganizationRequestPath
    body: UpdateADataForwarderForAnOrganizationRequestBody

# Operation: delete_data_forwarder_for_organization
class DeleteADataForwarderForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    data_forwarder_id: int = Field(default=..., description="The numeric ID of the data forwarder to delete.")
class DeleteADataForwarderForAnOrganizationRequest(StrictModel):
    """Permanently deletes a data forwarder from an organization, including all associated project-specific overrides."""
    path: DeleteADataForwarderForAnOrganizationRequestPath

# Operation: list_organization_integrations
class ListAnOrganizationSAvailableIntegrationsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class ListAnOrganizationSAvailableIntegrationsRequestQuery(StrictModel):
    provider_key: str | None = Field(default=None, validation_alias="providerKey", serialization_alias="providerKey", description="Filter results to a specific integration provider (e.g., slack, github, jira). Omit to return all providers.")
    features: list[str] | None = Field(default=None, description="Filter integrations by one or more capabilities they support, such as alert-rule, incident-management, or issue-sync. Items are matched inclusively (any matching feature will be included).")
    include_config: bool | None = Field(default=None, validation_alias="includeConfig", serialization_alias="includeConfig", description="Set to true to include third-party integration configurations in the response. Note: enabling this may significantly increase response time.")
class ListAnOrganizationSAvailableIntegrationsRequest(StrictModel):
    """Retrieve all available integrations for an organization, with optional filtering by provider and features. Use includeConfig to fetch third-party configuration details if needed."""
    path: ListAnOrganizationSAvailableIntegrationsRequestPath
    query: ListAnOrganizationSAvailableIntegrationsRequestQuery | None = None

# Operation: get_organization_integration
class RetrieveAnIntegrationForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    integration_id: str = Field(default=..., description="The unique identifier of the integration installed on the organization.")
class RetrieveAnIntegrationForAnOrganizationRequest(StrictModel):
    """Retrieve a specific integration installed on an organization. Both the integration and its organization-specific configuration must exist."""
    path: RetrieveAnIntegrationForAnOrganizationRequestPath

# Operation: delete_organization_integration
class DeleteAnIntegrationForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    integration_id: str = Field(default=..., description="The unique identifier of the integration that is installed on the organization.")
class DeleteAnIntegrationForAnOrganizationRequest(StrictModel):
    """Remove an integration from an organization. This operation requires both the Integration and OrganizationIntegration database entries to exist for the specified organization and integration."""
    path: DeleteAnIntegrationForAnOrganizationRequestPath

# Operation: list_organization_issues
class ListAnOrganizationSIssuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class ListAnOrganizationSIssuesRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter issues by one or more environment names. Provide as a list of environment identifiers.")
    group_stats_period: Literal["", "14d", "24h", "auto"] | None = Field(default=None, validation_alias="groupStatsPeriod", serialization_alias="groupStatsPeriod", description="The time period for which to calculate group statistics. Choose from: empty string (no stats), '24h' (last 24 hours), '14d' (last 14 days), or 'auto' (automatic period selection).")
    query: str | None = Field(default=None, description="Search query to filter issues using Sentry's query syntax (e.g., 'is:unresolved', 'error.type:ValueError'). Leave empty to retrieve all issues; if omitted, defaults to 'is:unresolved'.")
    limit: int | None = Field(default=None, description="Maximum number of issues to return in the response. Must be between 1 and 100; defaults to 100.")
    expand: list[Literal["inbox", "integrationIssues", "latestEventHasAttachments", "owners", "pluginActions", "pluginIssues", "sentryAppIssues", "sessions"]] | None = Field(default=None, description="Specify additional data fields to include in the response for each issue (e.g., 'sessions', 'latestEventHasUrl'). Provide as a list of field names.")
    collapse: list[Literal["base", "filtered", "lifetime", "stats", "unhandled"]] | None = Field(default=None, description="Specify fields to exclude from the response to reduce payload size and improve performance. Provide as a list of field names to omit.")
class ListAnOrganizationSIssuesRequest(StrictModel):
    """Retrieve a list of issues for an organization with optional filtering, search, and pagination. By default, only unresolved issues are returned unless a custom query is provided."""
    path: ListAnOrganizationSIssuesRequestPath
    query: ListAnOrganizationSIssuesRequestQuery | None = None

# Operation: bulk_update_issues
class BulkMutateAnOrganizationSIssuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug.")
class BulkMutateAnOrganizationSIssuesRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter issues by one or more environment names. Specify as an array of environment identifiers.")
    query: str | None = Field(default=None, description="Search query to filter issues (e.g., `is:unresolved`). Defaults to `is:unresolved` if not provided; use an empty string to include all results.")
    limit: int | None = Field(default=None, description="Maximum number of issues to update, up to 100. Defaults to 100.")
class BulkMutateAnOrganizationSIssuesRequestBody(StrictModel):
    inbox: bool = Field(default=..., description="Mark the issue as reviewed by the requesting user when set to true.")
    status: Literal["resolved", "unresolved", "ignored", "resolvedInNextRelease", "muted"] = Field(default=..., description="Limit mutations to issues with this status: `resolved`, `unresolved`, `ignored`, `resolvedInNextRelease`, or `muted`.")
    status_details: BulkMutateAnOrganizationSIssuesBodyStatusDetails = Field(default=..., validation_alias="statusDetails", serialization_alias="statusDetails", description="Additional context for the status change, such as release information for resolution details. Release-based updates are restricted to issues within a single project.")
    substatus: Literal["archived_until_escalating", "archived_until_condition_met", "archived_forever", "escalating", "ongoing", "regressed", "new"] | None = Field(default=..., description="Set the issue substatus to one of: `archived_until_escalating`, `archived_until_condition_met`, `archived_forever`, `escalating`, `ongoing`, `regressed`, or `new`. Omit or set to null to leave unchanged.")
    has_seen: bool = Field(default=..., validation_alias="hasSeen", serialization_alias="hasSeen", description="Mark the issue as seen by the requesting user when set to true.")
    is_bookmarked: bool = Field(default=..., validation_alias="isBookmarked", serialization_alias="isBookmarked", description="Bookmark the issue for the requesting user when set to true.")
    is_public: bool = Field(default=..., validation_alias="isPublic", serialization_alias="isPublic", description="Publish the issue to make it publicly visible when set to true.")
    is_subscribed: bool = Field(default=..., validation_alias="isSubscribed", serialization_alias="isSubscribed", description="Subscribe the requesting user to the issue when set to true.")
    merge: bool = Field(default=..., description="Merge the selected issues together when set to true.")
    discard: bool = Field(default=..., description="Discard the selected issues instead of updating them when set to true.")
    assigned_to: str = Field(default=..., validation_alias="assignedTo", serialization_alias="assignedTo", description="Assign the issues to a user or team. Specify as `<user_id>`, `user:<user_id>`, `<username>`, `<user_primary_email>`, or `team:<team_id>`.")
    priority: Literal["low", "medium", "high"] = Field(default=..., description="Set the priority level for the issues: `low`, `medium`, or `high`.")
class BulkMutateAnOrganizationSIssuesRequest(StrictModel):
    """Bulk update attributes on up to 1000 issues in an organization. Use the `id` query parameter for non-status updates, or omit it for status updates to match issues by filter criteria. Issues out of scope are silently skipped; returns HTTP 204 if no issues match."""
    path: BulkMutateAnOrganizationSIssuesRequestPath
    query: BulkMutateAnOrganizationSIssuesRequestQuery | None = None
    body: BulkMutateAnOrganizationSIssuesRequestBody

# Operation: delete_organization_issues
class BulkRemoveAnOrganizationSIssuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug.")
class BulkRemoveAnOrganizationSIssuesRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter issues by one or more environment names. Only issues matching all specified environments will be affected.")
    query: str | None = Field(default=None, description="Search query to filter issues by status, assignee, or other criteria. Defaults to unresolved issues only. Use an empty string to match all issues regardless of status.")
    limit: int | None = Field(default=None, description="Maximum number of issues to delete in this operation. Capped at 100 issues per request.")
class BulkRemoveAnOrganizationSIssuesRequest(StrictModel):
    """Permanently remove issues from an organization. Specify issues by ID for precise deletion, or use query filters to target multiple issues. Returns success even if no matching issues are found."""
    path: BulkRemoveAnOrganizationSIssuesRequestPath
    query: BulkRemoveAnOrganizationSIssuesRequestQuery | None = None

# Operation: list_organization_members
class ListAnOrganizationSMembersRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or a URL-friendly slug.")
class ListAnOrganizationSMembersRequest(StrictModel):
    """Retrieve all members of an organization, including pending invitations that have been approved by owners or managers but not yet accepted by invitees."""
    path: ListAnOrganizationSMembersRequestPath

# Operation: add_member_to_organization
class AddAMemberToAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
class AddAMemberToAnOrganizationRequestBody(StrictModel):
    email: str = Field(default=..., description="Email address of the member to invite. Must be a valid email format with a maximum length of 75 characters.", max_length=75, json_schema_extra={'format': 'email'})
    org_role: Literal["billing", "member", "manager", "owner", "admin"] | None = Field(default=None, validation_alias="orgRole", serialization_alias="orgRole", description="Organization-level role for the new member. Options range from `member` (view and act on events) to `owner` (unrestricted access). Defaults to `member`. Note: `admin` role is deprecated for Business and Enterprise plans.")
    team_roles: list[dict[str, Any]] | None = Field(default=None, validation_alias="teamRoles", serialization_alias="teamRoles", description="Array of team assignments with associated roles. Each entry assigns the member to a team with either `contributor` (view and act on issues) or `admin` (full team management) permissions.")
    send_invite: bool | None = Field(default=None, validation_alias="sendInvite", serialization_alias="sendInvite", description="Whether to send an email invitation notification to the member. Defaults to true.")
    reinvite: bool | None = Field(default=None, description="Whether to re-invite a member who has already received an invitation to the organization. Defaults to true.")
class AddAMemberToAnOrganizationRequest(StrictModel):
    """Add or invite a member to an organization with optional role assignment and team membership. Sends an email invitation by default unless disabled."""
    path: AddAMemberToAnOrganizationRequestPath
    body: AddAMemberToAnOrganizationRequestBody

# Operation: get_organization_member
class RetrieveAnOrganizationMemberRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    member_id: str = Field(default=..., description="The unique identifier of the organization member to retrieve.")
class RetrieveAnOrganizationMemberRequest(StrictModel):
    """Retrieve details for a specific organization member, including pending invite status if the member has been approved by owners or managers but hasn't yet accepted the invitation."""
    path: RetrieveAnOrganizationMemberRequestPath

# Operation: update_organization_member_roles
class UpdateAnOrganizationMemberSRolesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug.")
    member_id: str = Field(default=..., description="The numeric ID of the member whose roles should be updated.")
class UpdateAnOrganizationMemberSRolesRequestBody(StrictModel):
    org_role: Literal["billing", "member", "manager", "owner", "admin"] | None = Field(default=None, validation_alias="orgRole", serialization_alias="orgRole", description="The organization-level role to assign. Options range from billing (payment/compliance only) through member, manager, and owner (unrestricted access). The admin role is deprecated for Business and Enterprise plans. You can only assign roles at or below your own permission level.")
    team_roles: list[dict[str, Any]] | None = Field(default=None, validation_alias="teamRoles", serialization_alias="teamRoles", description="Array of team-level role assignments. Each entry specifies a team (by slug) and assigns either contributor (view and act on issues) or admin (full team management) role. Order is not significant. Omit to leave team roles unchanged.")
class UpdateAnOrganizationMemberSRolesRequest(StrictModel):
    """Update an organization member's roles at both the organization and team levels. Requires user auth tokens and enforces permission hierarchy—you can only assign roles with equal or lower permissions than your own."""
    path: UpdateAnOrganizationMemberSRolesRequestPath
    body: UpdateAnOrganizationMemberSRolesRequestBody | None = None

# Operation: delete_organization_member
class DeleteAnOrganizationMemberRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    member_id: str = Field(default=..., description="The unique identifier of the organization member to remove.")
class DeleteAnOrganizationMemberRequest(StrictModel):
    """Remove a member from an organization. This operation permanently deletes the member's association with the organization."""
    path: DeleteAnOrganizationMemberRequestPath

# Operation: add_member_to_team
class AddAnOrganizationMemberToATeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug. Used to scope the operation to a specific organization.")
    member_id: str = Field(default=..., description="The numeric ID of the organization member to add to the team.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug. Identifies which team the member should be added to.")
class AddAnOrganizationMemberToATeamRequest(StrictModel):
    """Add an organization member to a team. The operation returns different success codes based on context: 201 if successfully added, 202 if an access request is generated (pending approval), or 204 if the member is already on the team. Permission requirements vary based on the organization's 'Open Membership' setting and token type."""
    path: AddAnOrganizationMemberToATeamRequestPath

# Operation: update_organization_member_team_role
class UpdateAnOrganizationMemberSTeamRoleRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    member_id: str = Field(default=..., description="The numeric ID of the organization member whose team role should be updated.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug.")
class UpdateAnOrganizationMemberSTeamRoleRequestBody(StrictModel):
    team_role: Literal["contributor", "admin"] | None = Field(default=None, validation_alias="teamRole", serialization_alias="teamRole", description="The team-level role to assign. Choose 'contributor' for view and event action permissions, or 'admin' for full team management including project and membership control. Defaults to 'contributor' if not specified.")
class UpdateAnOrganizationMemberSTeamRoleRequest(StrictModel):
    """Update an organization member's role within a specific team. The member must already be part of the team. Note that organization admins, managers, and owners automatically receive a minimum team role of admin on all their teams."""
    path: UpdateAnOrganizationMemberSTeamRoleRequestPath
    body: UpdateAnOrganizationMemberSTeamRoleRequestBody | None = None

# Operation: remove_member_from_team
class DeleteAnOrganizationMemberFromATeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    member_id: str = Field(default=..., description="The numeric ID of the organization member to remove from the team.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug of the team.")
class DeleteAnOrganizationMemberFromATeamRequest(StrictModel):
    """Remove an organization member from a specific team. Requires appropriate authorization scopes; org:read scope can only remove yourself from teams you belong to."""
    path: DeleteAnOrganizationMemberFromATeamRequestPath

# Operation: list_monitors_for_organization
class RetrieveMonitorsForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class RetrieveMonitorsForAnOrganizationRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter results to include only monitors from specified environments. Accepts multiple environment names; monitors matching any of the provided environments will be included.")
    owner: str | None = Field(default=None, description="Filter results to monitors owned by a specific user or team. Use the format `user:id` for individual users or `team:id` for teams. Can be specified multiple times to include monitors from multiple owners.")
class RetrieveMonitorsForAnOrganizationRequest(StrictModel):
    """Retrieves all monitors for an organization, including their nested environments. Results can be filtered by specific projects or environments, and optionally filtered by monitor owner."""
    path: RetrieveMonitorsForAnOrganizationRequestPath
    query: RetrieveMonitorsForAnOrganizationRequestQuery | None = None

# Operation: create_monitor
class CreateAMonitorRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class CreateAMonitorRequestBody(StrictModel):
    project: str = Field(default=..., description="The project slug that this monitor will be associated with.")
    name: str = Field(default=..., description="A human-readable name for the monitor (up to 128 characters) used in notifications. If no slug is provided, it will be automatically derived from this name.", max_length=128)
    config: CreateAMonitorBodyConfig = Field(default=..., description="The monitor configuration object that defines check-in rules, thresholds, and behavior.")
    slug: str | None = Field(default=None, description="A unique identifier for the monitor within the organization (up to 50 characters). Must start with a letter or underscore and contain only lowercase letters, numbers, hyphens, and underscores. Required for check-in API calls, so changing it later requires updating instrumented code.", max_length=50)
    status: Literal["active", "disabled"] | None = Field(default=None, description="The operational status of the monitor. Active monitors accept events and count toward quota; disabled monitors do not. Defaults to active.")
    owner: str | None = Field(default=None, description="The team or user responsible for the monitor, specified as 'user:{user_id}' or 'team:{team_id}'.")
    is_muted: bool | None = Field(default=None, description="When enabled, prevents the creation of monitor incidents even when check-in failures occur.")
class CreateAMonitorRequest(StrictModel):
    """Create a new monitor for uptime or performance tracking within an organization. The monitor will be associated with a specific project and can be configured with custom check-in rules and notification settings."""
    path: CreateAMonitorRequestPath
    body: CreateAMonitorRequestBody

# Operation: get_monitor
class RetrieveAMonitorRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, which can be either the numeric ID or the URL-friendly slug of the monitor.")
class RetrieveAMonitorRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to filter the monitor data by. Specify multiple environments as separate array items.")
class RetrieveAMonitorRequest(StrictModel):
    """Retrieves detailed information about a specific monitor, including its configuration, status, and settings."""
    path: RetrieveAMonitorRequestPath
    query: RetrieveAMonitorRequestQuery | None = None

# Operation: update_monitor
class UpdateAMonitorRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the organization slug.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, either the numeric ID or the monitor slug.")
class UpdateAMonitorRequestBody(StrictModel):
    project: str = Field(default=..., description="The slug of the project to associate with this monitor.")
    name: str = Field(default=..., description="A descriptive name for the monitor used in notifications and UI display. Maximum 128 characters. If not provided, the slug will be derived from this name.", max_length=128)
    config: UpdateAMonitorBodyConfig = Field(default=..., description="The monitor's configuration object defining its behavior, check intervals, and alert thresholds.")
    slug: str | None = Field(default=None, description="A unique identifier for the monitor within the organization. Must contain only lowercase letters, numbers, hyphens, and underscores, and cannot be purely numeric. Maximum 50 characters. Changing this requires updating any check-in calls that reference it.", max_length=50)
    status: Literal["active", "disabled"] | None = Field(default=None, description="The operational status of the monitor. Disabled monitors will not process events and do not count toward your monitor quota. Defaults to active.")
    owner: str | None = Field(default=None, description="The team or user responsible for the monitor, specified as 'user:{user_id}' or 'team:{team_id}'.")
    is_muted: bool | None = Field(default=None, description="When enabled, prevents the creation of new monitor incidents while keeping the monitor active for check-ins.")
class UpdateAMonitorRequest(StrictModel):
    """Update an existing monitor's configuration, status, ownership, and notification settings. Changes to the slug will require updates to any instrumented check-in calls referencing the monitor."""
    path: UpdateAMonitorRequestPath
    body: UpdateAMonitorRequestBody

# Operation: delete_monitor_or_monitor_environments
class DeleteAMonitorOrMonitorEnvironmentsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, either the numeric ID or the URL slug of the monitor.")
class DeleteAMonitorOrMonitorEnvironmentsRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to delete. When specified, only these environments are removed from the monitor rather than deleting the entire monitor. Omit to delete the monitor entirely.")
class DeleteAMonitorOrMonitorEnvironmentsRequest(StrictModel):
    """Delete a monitor or specific monitor environments. If environment names are provided, only those environments are deleted; otherwise, the entire monitor is deleted."""
    path: DeleteAMonitorOrMonitorEnvironmentsRequestPath
    query: DeleteAMonitorOrMonitorEnvironmentsRequestQuery | None = None

# Operation: list_checkins_for_monitor
class RetrieveCheckInsForAMonitorRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, which can be either the numeric ID or the URL-friendly slug of the monitor within the organization.")
class RetrieveCheckInsForAMonitorRequest(StrictModel):
    """Retrieve all check-ins recorded for a specific monitor, showing the history of uptime verification events."""
    path: RetrieveCheckInsForAMonitorRequestPath

# Operation: list_spike_protection_notifications
class ListSpikeProtectionNotificationsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug.")
class ListSpikeProtectionNotificationsRequestQuery(StrictModel):
    trigger_type: str | None = Field(default=None, validation_alias="triggerType", serialization_alias="triggerType", description="Filter notifications by trigger type. Currently, only `spike-protection` is supported.")
class ListSpikeProtectionNotificationsRequest(StrictModel):
    """Retrieve all Spike Protection Notification Actions configured for an organization. These actions notify designated members via services like Slack or email when spike protection is triggered."""
    path: ListSpikeProtectionNotificationsRequestPath
    query: ListSpikeProtectionNotificationsRequestQuery | None = None

# Operation: get_spike_protection_notification_action
class RetrieveASpikeProtectionNotificationActionRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. Use whichever format you have available.")
    action_id: int = Field(default=..., description="The numeric identifier of the notification action to retrieve.")
class RetrieveASpikeProtectionNotificationActionRequest(StrictModel):
    """Retrieve a specific Spike Protection Notification Action that notifies organization members when spike detection is triggered. This action defines how and which members are alerted through services like Slack or email."""
    path: RetrieveASpikeProtectionNotificationActionRequestPath

# Operation: get_artifact_install_details
class RetrieveInstallInfoForAGivenArtifactRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    artifact_id: str = Field(default=..., description="The unique identifier of the build artifact for which to retrieve installation details.")
class RetrieveInstallInfoForAGivenArtifactRequest(StrictModel):
    """Retrieve installation and distribution details for a preprod artifact, including installability status, install URL, download metrics, and iOS code signing information."""
    path: RetrieveInstallInfoForAGivenArtifactRequestPath

# Operation: get_artifact_size_analysis
class RetrieveSizeAnalysisResultsForAGivenArtifactRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    artifact_id: str = Field(default=..., description="The unique identifier of the build artifact to analyze.")
class RetrieveSizeAnalysisResultsForAGivenArtifactRequestQuery(StrictModel):
    base_artifact_id: str | None = Field(default=None, validation_alias="baseArtifactId", serialization_alias="baseArtifactId", description="Optional artifact ID to use as a baseline for size comparison. If omitted, the system uses the default base artifact from commit comparison.")
class RetrieveSizeAnalysisResultsForAGivenArtifactRequest(StrictModel):
    """Retrieve size analysis results for a build artifact, including download and install size metrics. Optionally compare against a base artifact to see size differences."""
    path: RetrieveSizeAnalysisResultsForAGivenArtifactRequestPath
    query: RetrieveSizeAnalysisResultsForAGivenArtifactRequestQuery | None = None

# Operation: list_repositories_for_owner
class RetrievesListOfRepositoriesForAGivenOwnerRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL slug. This determines which organization's repositories to query.")
    owner: str = Field(default=..., description="The owner identifier whose repositories should be retrieved.")
class RetrievesListOfRepositoriesForAGivenOwnerRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of repositories to return per request. Defaults to 20 if not specified.")
    term: str | None = Field(default=None, description="Optional substring filter to match against repository names using case-sensitive containment matching.")
class RetrievesListOfRepositoriesForAGivenOwnerRequest(StrictModel):
    """Retrieves a paginated list of repositories owned by a specified owner within an organization. Results can be filtered by name substring."""
    path: RetrievesListOfRepositoriesForAGivenOwnerRequestPath
    query: RetrievesListOfRepositoriesForAGivenOwnerRequestQuery | None = None

# Operation: get_repository_sync_status
class GetsSyncingStatusForRepositoriesForAnIntegratedOrgRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    owner: str = Field(default=..., description="The repository owner identifier, typically a username or organization name that owns the repositories being queried.")
class GetsSyncingStatusForRepositoriesForAnIntegratedOrgRequest(StrictModel):
    """Retrieves the synchronization status of repositories for an integrated organization, showing which repositories are currently syncing and their progress."""
    path: GetsSyncingStatusForRepositoriesForAnIntegratedOrgRequestPath

# Operation: sync_repositories_for_owner
class SyncsRepositoriesFromAnIntegratedOrgWithGitHubRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's GitHub integration will be used for the sync operation.")
    owner: str = Field(default=..., description="The GitHub username or organization name that owns the repositories to be synchronized. Only repositories owned by this entity will be synced.")
class SyncsRepositoriesFromAnIntegratedOrgWithGitHubRequest(StrictModel):
    """Synchronizes repositories from a specified owner with an integrated GitHub organization, ensuring the local repository list matches the current state in GitHub."""
    path: SyncsRepositoriesFromAnIntegratedOrgWithGitHubRequestPath

# Operation: list_repository_tokens_for_owner
class RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL slug. This determines which organization's tokens to retrieve.")
    owner: str = Field(default=..., description="The repository owner whose tokens should be listed. Filters results to tokens belonging to this specific owner.")
class RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of tokens to return per request. Defaults to 20 if not specified. Use this to control pagination size.")
class RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequest(StrictModel):
    """Retrieves a paginated list of repository tokens for a specified owner within an organization. Use this to view all tokens associated with a particular repository owner."""
    path: RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequestPath
    query: RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequestQuery | None = None

# Operation: get_repository
class RetrievesASingleRepositoryForAGivenOwnerRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    owner: str = Field(default=..., description="The owner identifier of the repository, typically a user or team name within the organization.")
    repository: str = Field(default=..., description="The name of the repository to retrieve.")
class RetrievesASingleRepositoryForAGivenOwnerRequest(StrictModel):
    """Retrieves detailed metadata for a single repository within an organization, identified by its owner and repository name."""
    path: RetrievesASingleRepositoryForAGivenOwnerRequestPath

# Operation: list_repository_branches
class RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    owner: str = Field(default=..., description="The repository owner's username or identifier.")
    repository: str = Field(default=..., description="The name of the repository to retrieve branches from.")
class RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of branches to return per request; defaults to 20 if not specified.")
    term: str | None = Field(default=None, description="Optional substring to filter branches by name using case-sensitive contains matching.")
class RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequest(StrictModel):
    """Retrieves a paginated list of branches for a specified repository, with optional filtering by branch name substring."""
    path: RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequestPath
    query: RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequestQuery | None = None

# Operation: list_test_results_for_repository
class RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    owner: str = Field(default=..., description="The repository owner or account name.")
    repository: str = Field(default=..., description="The repository name.")
class RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequestQuery(StrictModel):
    filter_by: str | None = Field(default=None, validation_alias="filterBy", serialization_alias="filterBy", description="Filter results by test category: flaky tests, failed tests, slowest tests, or skipped tests. If omitted, all test results are returned.")
    branch: str | None = Field(default=None, description="Limit results to a specific branch. If omitted, results from all branches are included.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per page. Defaults to 20 if not specified.")
    term: str | None = Field(default=None, description="Filter test results by name substring using case-sensitive contains matching.")
class RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequest(StrictModel):
    """Retrieves a paginated list of test results for a specific repository, with optional filtering by test status, branch, and name substring matching."""
    path: RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequestPath
    query: RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequestQuery | None = None

# Operation: get_test_results_aggregates_for_repository
class RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's data is accessed.")
    owner: str = Field(default=..., description="The owner or account name that owns the repository. Used to scope the repository lookup within the organization.")
    repository: str = Field(default=..., description="The name of the repository for which to retrieve test result metrics.")
class RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequestQuery(StrictModel):
    branch: str | None = Field(default=None, description="Optional branch name to filter results. When omitted, metrics are aggregated across all branches of the repository.")
class RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequest(StrictModel):
    """Retrieves aggregated test result metrics for a specific repository within an organization, with optional filtering by branch. Metrics can be scoped to a particular time period via query parameters."""
    path: RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequestPath
    query: RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequestQuery | None = None

# Operation: list_test_suites_for_repository
class RetrieveTestSuitesBelongingToARepositorySTestResultsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    owner: str = Field(default=..., description="The owner or account name that owns the repository.")
    repository: str = Field(default=..., description="The name of the repository to retrieve test suites from.")
class RetrieveTestSuitesBelongingToARepositorySTestResultsRequestQuery(StrictModel):
    term: str | None = Field(default=None, description="Optional substring to filter test suites by name using case-sensitive contains matching.")
class RetrieveTestSuitesBelongingToARepositorySTestResultsRequest(StrictModel):
    """Retrieves all test suites associated with a repository's test results, with optional filtering by name substring."""
    path: RetrieveTestSuitesBelongingToARepositorySTestResultsRequestPath
    query: RetrieveTestSuitesBelongingToARepositorySTestResultsRequestQuery | None = None

# Operation: regenerate_repository_upload_token
class RegeneratesARepositoryUploadTokenAndReturnsTheNewTokenRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    owner: str = Field(default=..., description="The owner identifier of the repository, typically a user or organization name.")
    repository: str = Field(default=..., description="The name of the repository for which to regenerate the upload token.")
class RegeneratesARepositoryUploadTokenAndReturnsTheNewTokenRequest(StrictModel):
    """Regenerates an existing repository upload token, invalidating the previous token and returning a new one for repository uploads."""
    path: RegeneratesARepositoryUploadTokenAndReturnsTheNewTokenRequestPath

# Operation: list_organization_client_keys
class ListAnOrganizationSClientKeysRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its unique ID or human-readable slug.")
class ListAnOrganizationSClientKeysRequestQuery(StrictModel):
    team: str | None = Field(default=None, description="Optional filter to retrieve keys only for projects belonging to a specific team, identified by team slug or ID.", min_length=1)
    status: Literal["active", "inactive"] | None = Field(default=None, description="Optional filter to retrieve keys by their operational status: 'active' for enabled keys or 'inactive' for disabled keys.", min_length=1)
class ListAnOrganizationSClientKeysRequest(StrictModel):
    """Retrieve all client keys (DSNs) across projects in an organization, with optional filtering by team and key status. Results are paginated for efficient retrieval of large key sets."""
    path: ListAnOrganizationSClientKeysRequestPath
    query: ListAnOrganizationSClientKeysRequestQuery | None = None

# Operation: list_organization_projects
class ListAnOrganizationSProjectsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
class ListAnOrganizationSProjectsRequest(StrictModel):
    """Retrieve all projects associated with a specific organization. Returns a list of projects bound to the organization identified by ID or slug."""
    path: ListAnOrganizationSProjectsRequestPath

# Operation: create_metric_monitor_for_project
class CreateAMonitorForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL slug.")
class CreateAMonitorForAProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the monitor. Maximum 200 characters.", max_length=200)
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The monitor classification type. Currently supports `metric_issue` for metric-based monitoring.")
    workflow_ids: list[int] | None = Field(default=None, description="Optional array of alert workflow IDs to automatically connect this monitor to existing alerts. Use the Fetch Alerts endpoint to discover available workflow IDs.")
    data_sources: list[Any] | None = Field(default=None, description="Array of data source configurations defining what metric to measure. Each source specifies the aggregate function (e.g., count(), p95(span.duration)), dataset (events, events_analytics_platform, or generic_metrics), environment, event types to include, query filters, and time window in seconds. Refer to documentation for metric-specific configurations like error counts, throughput, duration, failure rate, or custom measurements.")
    config: dict[str, Any] | None = Field(default=None, description="Detection algorithm configuration. Choose `static` for threshold-based alerts, `percent` for change-based detection (requires comparisonDelta in minutes: 300, 900, 3600, 86400, 604800, or 2592000), or `dynamic` for anomaly detection.")
    condition_group: CreateAMonitorForAProjectBodyConditionGroup | None = Field(default=None, description="Condition group defining when to trigger issue creation and priority assignment. Specify logic type, comparison operators (gt, lte, anomaly_detection), thresholds, and result states (75=high priority, 50=low priority, 0=resolved). For dynamic monitors, configure seasonality, sensitivity (low/medium/high), and threshold direction.")
    owner: str | None = Field(default=None, description="The owner of this monitor, specified as either a user ID (format: `user:123456`) or team ID (format: `team:456789`).")
    description: str | None = Field(default=None, description="Optional descriptive text about the monitor's purpose. This text will be included in any resulting issues created by the monitor.")
    enabled: bool | None = Field(default=None, description="Set to `false` to create the monitor in a disabled state. Defaults to `true` (enabled).")
class CreateAMonitorForAProjectRequest(StrictModel):
    """Create a metric-based monitor for a project to detect issues based on error counts, performance metrics, or custom measurements. This beta endpoint supports multiple monitor types including threshold-based, change-based, and dynamic anomaly detection."""
    path: CreateAMonitorForAProjectRequestPath
    body: CreateAMonitorForAProjectRequestBody

# Operation: list_organization_trusted_relays
class ListAnOrganizationSTrustedRelaysRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
class ListAnOrganizationSTrustedRelaysRequest(StrictModel):
    """Retrieve a list of all trusted relays configured for an organization. Relays are used to forward events and requests securely within the organization's infrastructure."""
    path: ListAnOrganizationSTrustedRelaysRequestPath

# Operation: list_release_threshold_statuses
class RetrieveStatusesOfReleaseThresholdsAlphaRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class RetrieveStatusesOfReleaseThresholdsAlphaRequestQuery(StrictModel):
    start: str = Field(default=..., description="The start of the time range as a UTC datetime in ISO 8601 format or Unix epoch seconds (inclusive).", json_schema_extra={'format': 'date-time'})
    end: str = Field(default=..., description="The end of the time range as a UTC datetime in ISO 8601 format or Unix epoch seconds (inclusive). Must be used with `start`.", json_schema_extra={'format': 'date-time'})
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to filter results. Specify multiple environments as separate array items.")
    release: list[str] | None = Field(default=None, description="Optional list of release versions to filter results. Specify multiple releases as separate array items.")
class RetrieveStatusesOfReleaseThresholdsAlphaRequest(StrictModel):
    """Retrieve the health statuses of release thresholds within a specified time range. Returns threshold statuses keyed by release version and project, including full threshold details and derived health indicators. **Note: This is an experimental Alpha API subject to change.**"""
    path: RetrieveStatusesOfReleaseThresholdsAlphaRequestPath
    query: RetrieveStatusesOfReleaseThresholdsAlphaRequestQuery

# Operation: get_organization_release
class RetrieveAnOrganizationSReleaseRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    version: str = Field(default=..., description="The version identifier that uniquely identifies the release within the organization.")
class RetrieveAnOrganizationSReleaseRequestQuery(StrictModel):
    project_id: str | None = Field(default=None, description="Filter release data to a specific project within the organization.")
    health: bool | None = Field(default=None, description="Include health metrics and crash data with the release details. Disabled by default.")
    adoption_stages: bool | None = Field(default=None, validation_alias="adoptionStages", serialization_alias="adoptionStages", description="Include adoption stage information showing how the release is being adopted across your user base. Disabled by default.")
    summary_stats_period: Literal["14d", "1d", "1h", "24h", "2d", "30d", "48h", "7d", "90d"] | None = Field(default=None, validation_alias="summaryStatsPeriod", serialization_alias="summaryStatsPeriod", description="Time period for aggregating summary statistics. Defaults to 14 days. Valid periods range from 1 hour to 90 days.")
    health_stats_period: Literal["14d", "1d", "1h", "24h", "2d", "30d", "48h", "7d", "90d"] | None = Field(default=None, validation_alias="healthStatsPeriod", serialization_alias="healthStatsPeriod", description="Time period for aggregating health statistics when health data is enabled. Defaults to 24 hours if health is enabled. Valid periods range from 1 hour to 90 days.")
    status: Literal["archived", "open"] | None = Field(default=None, description="Filter results by release status: archived releases or actively open releases.")
    query: str | None = Field(default=None, description="Apply advanced filters using query syntax to narrow results by transaction, release, and other attributes. Supports boolean operators (AND, OR) and comma-separated value lists.")
class RetrieveAnOrganizationSReleaseRequest(StrictModel):
    """Retrieve detailed information about a specific release within an organization, including optional health metrics, adoption stages, and summary statistics."""
    path: RetrieveAnOrganizationSReleaseRequestPath
    query: RetrieveAnOrganizationSReleaseRequestQuery | None = None

# Operation: update_organization_release
class UpdateAnOrganizationSReleaseRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    version: str = Field(default=..., description="The semantic version string that uniquely identifies the release within the organization.")
class UpdateAnOrganizationSReleaseRequestBody(StrictModel):
    url: str | None = Field(default=None, description="A URI pointing to the release, such as a GitHub repository URL or deployment interface. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
    date_released: str | None = Field(default=None, validation_alias="dateReleased", serialization_alias="dateReleased", description="An ISO 8601 formatted date-time indicating when the release was deployed to production. If omitted, the current server time is used.", json_schema_extra={'format': 'date-time'})
    refs: list[UpdateAnOrganizationSReleaseBodyRefsItem] | None = Field(default=None, description="An array of commit references for each repository in the release. Each entry must include the repository identifier and commit SHA (HEAD). Optionally include the previous commit SHA if this is the first time sending commit data for this repository. Order reflects the sequence of repositories in the release.")
class UpdateAnOrganizationSReleaseRequest(StrictModel):
    """Update release metadata including repository references, deployment URL, and release date. Allows modification of commit information, external links, and timing details for an existing release."""
    path: UpdateAnOrganizationSReleaseRequestPath
    body: UpdateAnOrganizationSReleaseRequestBody | None = None

# Operation: delete_organization_release
class DeleteAnOrganizationSReleaseRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    version: str = Field(default=..., description="The version string that uniquely identifies the release within the organization.")
class DeleteAnOrganizationSReleaseRequest(StrictModel):
    """Permanently delete a release from an organization, including all associated files and artifacts. This action cannot be undone."""
    path: DeleteAnOrganizationSReleaseRequestPath

# Operation: list_release_deploys
class ListAReleaseSDeploysRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    version: str = Field(default=..., description="The version string that uniquely identifies the release for which to retrieve deployments.")
class ListAReleaseSDeploysRequest(StrictModel):
    """Retrieve all deployments for a specific release version within an organization. Returns deployment history and status information for the given release."""
    path: ListAReleaseSDeploysRequestPath

# Operation: create_deploy_for_release
class CreateADeployRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    version: str = Field(default=..., description="The release version identifier to deploy.")
class CreateADeployRequestBody(StrictModel):
    environment: str = Field(default=..., description="The target environment for this deployment (e.g., production, staging, development). Limited to 64 characters.", max_length=64)
    name: str | None = Field(default=None, description="A human-readable name for this deployment. Limited to 64 characters.", max_length=64)
    url: str | None = Field(default=None, description="A URL pointing to deployment details, logs, or related resources. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    date_started: str | None = Field(default=None, validation_alias="dateStarted", serialization_alias="dateStarted", description="The timestamp when the deployment began, in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    date_finished: str | None = Field(default=None, validation_alias="dateFinished", serialization_alias="dateFinished", description="The timestamp when the deployment completed, in ISO 8601 format. Defaults to the current time if not provided.", json_schema_extra={'format': 'date-time'})
    projects: list[str] | None = Field(default=None, description="A list of project slugs to associate with this deployment. If omitted, the deployment applies to all projects in the release.")
class CreateADeployRequest(StrictModel):
    """Create a deployment record for a specific release version to a target environment. This tracks when and where a release was deployed, optionally linking it to specific projects."""
    path: CreateADeployRequestPath
    body: CreateADeployRequestBody

# Operation: get_replay_count_for_issues_or_transactions
class RetrieveACountOfReplaysForAGivenIssueOrTransactionRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
class RetrieveACountOfReplaysForAGivenIssueOrTransactionRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to narrow results to specific deployment environments.")
    query: str | None = Field(default=None, description="Required search query using Sentry query syntax to specify which replays to count. Must include exactly one of: issue.id (for issues), transaction (for transactions), or replay_id (for specific replays). Supports boolean operators and multiple values in bracket notation.")
class RetrieveACountOfReplaysForAGivenIssueOrTransactionRequest(StrictModel):
    """Retrieve the count of replays associated with specified issues, transactions, or replay IDs within an organization. Use the query parameter to filter by issue ID, transaction name, or replay ID."""
    path: RetrieveACountOfReplaysForAGivenIssueOrTransactionRequestPath
    query: RetrieveACountOfReplaysForAGivenIssueOrTransactionRequestQuery | None = None

# Operation: list_organization_replay_selectors
class ListAnOrganizationSSelectorsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class ListAnOrganizationSSelectorsRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter selectors by one or more environments. Specify as an array of environment names.")
    per_page: int | None = Field(default=None, description="Maximum number of results to return per page, up to 100. Defaults to 100 if not specified.")
    query: str | None = Field(default=None, description="Filter selectors using Sentry's query syntax, supporting logical operators (AND, OR) and field-based conditions like transaction names and release versions.")
class ListAnOrganizationSSelectorsRequest(StrictModel):
    """Retrieve a list of replay selectors configured for an organization, with optional filtering by environment, query criteria, and pagination controls."""
    path: ListAnOrganizationSSelectorsRequestPath
    query: ListAnOrganizationSSelectorsRequestQuery | None = None

# Operation: list_organization_replays
class ListAnOrganizationSReplaysRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class ListAnOrganizationSReplaysRequestQuery(StrictModel):
    field: list[Literal["activity", "browser", "count_dead_clicks", "count_errors", "count_rage_clicks", "count_segments", "count_urls", "device", "dist", "duration", "environment", "error_ids", "finished_at", "id", "is_archived", "os", "platform", "project_id", "releases", "sdk", "started_at", "tags", "trace_ids", "urls", "user", "clicks", "info_ids", "warning_ids", "count_warnings", "count_infos", "has_viewed"]] | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. Only valid field names are accepted; invalid fields will cause an error.")
    environment: str | None = Field(default=None, description="Filter replays by environment name (e.g., production, staging, development). Must be at least 1 character.", min_length=1)
    query: str | None = Field(default=None, description="A structured query string to filter results (e.g., by user, duration, or other replay attributes). Must be at least 1 character.", min_length=1)
    per_page: int | None = Field(default=None, description="Maximum number of replays to return per page for pagination.")
class ListAnOrganizationSReplaysRequest(StrictModel):
    """Retrieve a paginated list of session replays for an organization, with optional filtering by environment and structured query parameters."""
    path: ListAnOrganizationSReplaysRequestPath
    query: ListAnOrganizationSReplaysRequestQuery | None = None

# Operation: get_replay_instance
class RetrieveAReplayInstanceRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. Required to scope the replay to the correct organization.")
    replay_id: str = Field(default=..., description="The unique identifier of the replay to retrieve, formatted as a UUID. This must be a valid UUID string.", json_schema_extra={'format': 'uuid'})
class RetrieveAReplayInstanceRequestQuery(StrictModel):
    field: list[Literal["activity", "browser", "count_dead_clicks", "count_errors", "count_rage_clicks", "count_segments", "count_urls", "device", "dist", "duration", "environment", "error_ids", "finished_at", "id", "is_archived", "os", "platform", "project_id", "releases", "sdk", "started_at", "tags", "trace_ids", "urls", "user", "clicks", "info_ids", "warning_ids", "count_warnings", "count_infos", "has_viewed"]] | None = Field(default=None, description="Optional list of specific fields to include in the response. Only the specified fields will be marshaled in the output; invalid field names will be rejected.")
    environment: str | None = Field(default=None, description="Optional environment name to filter the replay data. Must be a non-empty string if provided.", min_length=1)
    query: str | None = Field(default=None, description="Optional structured query string to filter the replay output. Must be a non-empty string if provided and should follow the API's query syntax.", min_length=1)
    per_page: int | None = Field(default=None, description="Optional limit on the number of rows to return in the result set. Useful for paginating large replay datasets.")
class RetrieveAReplayInstanceRequest(StrictModel):
    """Retrieve detailed information about a specific replay session by its ID. Returns comprehensive replay data including metadata, events, and user interactions."""
    path: RetrieveAReplayInstanceRequestPath
    query: RetrieveAReplayInstanceRequestQuery | None = None

# Operation: list_repository_commits
class ListARepositorySCommitsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    repo_id: str = Field(default=..., description="The unique identifier of the repository within the organization.")
class ListARepositorySCommitsRequest(StrictModel):
    """Retrieve a paginated list of commits for a specific repository within an organization. Use this to view the commit history and details for a given repository."""
    path: ListARepositorySCommitsRequestPath

# Operation: list_organization_teams_scim
class ListAnOrganizationSPaginatedTeamsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug.")
class ListAnOrganizationSPaginatedTeamsRequestQuery(StrictModel):
    start_index: int | None = Field(default=None, validation_alias="startIndex", serialization_alias="startIndex", description="The starting position for pagination using 1-based indexing. Defaults to 1 if not specified.", ge=1)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="A SCIM filter expression to narrow results. Currently supports only equality (`eq`) comparisons.", min_length=1)
    excluded_attributes: list[str] | None = Field(default=None, validation_alias="excludedAttributes", serialization_alias="excludedAttributes", description="Array of field names to exclude from the response. Currently only `members` is supported for exclusion.")
class ListAnOrganizationSPaginatedTeamsRequest(StrictModel):
    """Retrieve a paginated list of teams in an organization using SCIM Groups protocol. Note that the members field is capped at 10,000 members per team."""
    path: ListAnOrganizationSPaginatedTeamsRequestPath
    query: ListAnOrganizationSPaginatedTeamsRequestQuery | None = None

# Operation: create_team_in_organization
class ProvisionANewTeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
class ProvisionANewTeamRequestBody(StrictModel):
    display_name: str = Field(default=..., validation_alias="displayName", serialization_alias="displayName", description="The display name for the team as shown in the UI. This will be normalized to a URL-friendly slug format (lowercase, spaces converted to dashes).")
class ProvisionANewTeamRequest(StrictModel):
    """Create a new team within an organization using SCIM Groups protocol. The team is initialized with an empty member set, and the display name is normalized to lowercase with spaces converted to dashes."""
    path: ProvisionANewTeamRequestPath
    body: ProvisionANewTeamRequestBody

# Operation: list_organization_scim_members
class ListAnOrganizationSScimMembersRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug.")
class ListAnOrganizationSScimMembersRequestQuery(StrictModel):
    start_index: int | None = Field(default=None, validation_alias="startIndex", serialization_alias="startIndex", description="The starting position for pagination using 1-based indexing (defaults to 1 if not specified).", ge=1)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="A SCIM filter expression to refine results; currently supports only equality (`eq`) comparisons.", min_length=1)
    excluded_attributes: list[str] | None = Field(default=None, validation_alias="excludedAttributes", serialization_alias="excludedAttributes", description="Array of field names to exclude from the response. Currently only `members` is supported for exclusion.")
class ListAnOrganizationSScimMembersRequest(StrictModel):
    """Retrieves a paginated list of SCIM-provisioned members in an organization. Use SCIM filter expressions to narrow results or exclude specific attributes from the response."""
    path: ListAnOrganizationSScimMembersRequestPath
    query: ListAnOrganizationSScimMembersRequestQuery | None = None

# Operation: create_organization_member
class ProvisionANewOrganizationMemberRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
class ProvisionANewOrganizationMemberRequestBody(StrictModel):
    user_name: str = Field(default=..., validation_alias="userName", serialization_alias="userName", description="The email address for the new member, used as the SAML identifier. Must be a valid email format.", json_schema_extra={'format': 'email'})
    sentry_org_role: Literal["billing", "member", "manager", "admin"] | None = Field(default=None, validation_alias="sentryOrgRole", serialization_alias="sentryOrgRole", description="The organization role to assign the member. Determines permissions for billing management, event handling, team/project administration, and global integrations. Defaults to the organization's default role if not specified. Options are: billing (payment and compliance), member (events and data viewing), manager (full team and project management), or admin (global integrations and project management).")
class ProvisionANewOrganizationMemberRequest(StrictModel):
    """Provision a new organization member via SCIM protocol. The member will be assigned the organization's default role unless a specific role is provided."""
    path: ProvisionANewOrganizationMemberRequestPath
    body: ProvisionANewOrganizationMemberRequestBody

# Operation: list_sentry_apps
class RetrieveTheCustomIntegrationsCreatedByAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. Use the slug for human-readable requests or the ID for programmatic access.")
class RetrieveTheCustomIntegrationsCreatedByAnOrganizationRequest(StrictModel):
    """Retrieve all custom integrations (Sentry Apps) created by an organization. This returns the organization's internal integrations that extend Sentry's functionality."""
    path: RetrieveTheCustomIntegrationsCreatedByAnOrganizationRequestPath

# Operation: list_release_health_session_statistics
class RetrieveReleaseHealthSessionStatisticsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class RetrieveReleaseHealthSessionStatisticsRequestQuery(StrictModel):
    field: list[str] = Field(default=..., description="One or more metrics to retrieve, such as session counts, unique user counts, crash rates, or session duration percentiles. Multiple fields can be requested in a single query.")
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to filter results by (e.g., production, staging, development). If omitted, all environments are included.")
    per_page: int | None = Field(default=None, description="Maximum number of result groups to return per request. Useful for pagination when results are large.")
    group_by: list[str] | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="One or more dimensions to group results by, such as project, release, environment, or session status. Grouping affects the maximum number of data points returned (capped at 10,000 total).")
    include_totals: int | None = Field(default=None, validation_alias="includeTotals", serialization_alias="includeTotals", description="Set to 0 to exclude aggregate totals from the response; defaults to 1 (include totals).")
    include_series: int | None = Field(default=None, validation_alias="includeSeries", serialization_alias="includeSeries", description="Set to 0 to exclude time series data from the response; defaults to 1 (include series).")
    query: str | None = Field(default=None, description="Filter results using Sentry's query syntax to match specific conditions on transactions, releases, and other attributes. Multiple conditions can be combined with AND/OR operators.")
class RetrieveReleaseHealthSessionStatisticsRequest(StrictModel):
    """Retrieves time series data for release health session statistics across projects in an organization. Results are aggregated by specified intervals and grouped by optional dimensions, with automatic rounding to align with the selected time interval."""
    path: RetrieveReleaseHealthSessionStatisticsRequestPath
    query: RetrieveReleaseHealthSessionStatisticsRequestQuery

# Operation: resolve_short_id
class ResolveAShortIdRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's namespace to search within.")
    issue_id: str = Field(default=..., description="The short ID of the issue to resolve. This is a condensed identifier that maps to a specific issue within the organization.")
class ResolveAShortIdRequest(StrictModel):
    """Resolve a short issue ID to retrieve the associated project slug and group (issue) details. This allows you to look up full issue information using a condensed identifier."""
    path: ResolveAShortIdRequestPath

# Operation: get_organization_events_count_by_project
class RetrieveAnOrganizationSEventsCountByProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class RetrieveAnOrganizationSEventsCountByProjectRequestQuery(StrictModel):
    field: Literal["sum(quantity)", "sum(times_seen)"] = Field(default=..., description="The aggregation metric to retrieve: `sum(quantity)` returns event counts (or total bytes for attachments), while `sum(times_seen)` returns the number of times events were observed (or unique session counts for sessions, total attachments for attachments).", min_length=1)
    category: Literal["error", "transaction", "attachment", "replays", "profiles"] | None = Field(default=None, description="Filter results by event category. Note: attachments cannot be combined with other categories as quantity values differ (bytes vs. event counts). Filtering by `error` automatically includes `default` and `security` categories.", min_length=1)
    outcome: Literal["accepted", "filtered", "rate_limited", "invalid", "abuse", "client_discard", "cardinality_limited"] | None = Field(default=None, description="Filter results by event outcome status, indicating whether events were accepted, filtered, rate-limited, invalid, abused, client-discarded, or cardinality-limited. See Sentry's stats documentation for detailed outcome definitions.", min_length=1)
    reason: str | None = Field(default=None, description="Filter results by the specific reason an event was filtered or dropped. Provide the reason as a string value.", min_length=1)
    download: bool | None = Field(default=None, description="If true, download the response as a CSV file instead of JSON.")
class RetrieveAnOrganizationSEventsCountByProjectRequest(StrictModel):
    """Retrieve summarized event counts aggregated by project for an organization. Use this to analyze event volume, filtering by category (errors, transactions, attachments, replays, profiles), outcome status, and other dimensions."""
    path: RetrieveAnOrganizationSEventsCountByProjectRequestPath
    query: RetrieveAnOrganizationSEventsCountByProjectRequestQuery

# Operation: get_event_counts_for_organization
class RetrieveEventCountsForAnOrganizationV2RequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class RetrieveEventCountsForAnOrganizationV2RequestQuery(StrictModel):
    group_by: list[Literal["outcome", "category", "reason", "project"]] = Field(default=..., validation_alias="groupBy", serialization_alias="groupBy", description="One or more dimensions to group results by (e.g., project, outcome, category). Multiple groupBy parameters can be passed to create multi-dimensional breakdowns. Note: grouping by project may omit rows if the project/interval combination is very large; for large project counts, filter and query individually. Project grouping does not support timeseries intervals and returns aggregated sums instead.")
    field: Literal["sum(quantity)", "sum(times_seen)"] = Field(default=..., description="The metric to aggregate: `sum(quantity)` counts events (or bytes for attachments), while `sum(times_seen)` counts unique occurrences (sessions for replay data, or attachment count for attachments).", min_length=1)
    category: Literal["error", "transaction", "attachment", "replay", "profile", "profile_duration", "profile_duration_ui", "profile_chunk", "profile_chunk_ui", "monitor"] | None = Field(default=None, description="Filter results to a specific data category. Each category represents a distinct data type: errors, transactions, file attachments, session replays, performance profiles, profile duration metrics, or cron monitors. Attachment and profile_duration categories cannot be combined with others due to their unique quantity units (bytes and milliseconds respectively).", min_length=1)
    outcome: Literal["accepted", "filtered", "rate_limited", "invalid", "abuse", "client_discard", "cardinality_limited"] | None = Field(default=None, description="Filter results by event outcome status, indicating whether an event was accepted, rate-limited, filtered, invalid, abused, discarded by client, or subject to cardinality limits. See Sentry documentation for detailed outcome definitions.", min_length=1)
    reason: str | None = Field(default=None, description="Filter results by the specific reason an event was filtered or dropped. Provide the reason string to narrow results to events rejected for a particular cause.", min_length=1)
    stats_period: str | None = Field(default=None, validation_alias="statsPeriod", serialization_alias="statsPeriod", description="This defines the range of the time series, relative to now. The range is given in a `<number><unit>` format. For example `1d` for a one day range. Possible units are `m` for minutes, `h` for hours, `d` for days and `w` for weeks.You must either provide a `statsPeriod`, or a `start` and `end`.", min_length=1)
    interval: str | None = Field(default=None, description="This is the resolution of the time series, given in the same format as `statsPeriod`. The default resolution is `1h` and the minimum resolution is currently restricted to `1h` as well. Intervals larger than `1d` are not supported, and the interval has to cleanly divide one day.", min_length=1)
    start: str | None = Field(default=None, description="This defines the start of the time series range as an explicit datetime, either in UTC ISO8601 or epoch seconds.Use along with `end` instead of `statsPeriod`.", json_schema_extra={'format': 'date-time'})
    end: str | None = Field(default=None, description="This defines the inclusive end of the time series range as an explicit datetime, either in UTC ISO8601 or epoch seconds.Use along with `start` instead of `statsPeriod`.", json_schema_extra={'format': 'date-time'})
    project: list[Any] | None = Field(default=None, description="The ID of the projects to filter by.\n\nUse `-1` to include all accessible projects.")
class RetrieveEventCountsForAnOrganizationV2Request(StrictModel):
    """Retrieve aggregated event counts for an organization over a specified time period. Query by event type, outcome, and other dimensions using flexible grouping and filtering options."""
    path: RetrieveEventCountsForAnOrganizationV2RequestPath
    query: RetrieveEventCountsForAnOrganizationV2RequestQuery

# Operation: list_organization_teams
class ListAnOrganizationSTeamsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The unique identifier or slug of the organization. Use either the numeric ID or the organization's URL-friendly slug.")
class ListAnOrganizationSTeamsRequestQuery(StrictModel):
    detailed: str | None = Field(default=None, description="Set to \"0\" to return team information without including associated project details, reducing response size.")
class ListAnOrganizationSTeamsRequest(StrictModel):
    """Retrieves a list of all teams associated with a specific organization. Optionally filter the response to exclude project details for a lighter payload."""
    path: ListAnOrganizationSTeamsRequestPath
    query: ListAnOrganizationSTeamsRequestQuery | None = None

# Operation: create_team
class CreateANewTeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL-friendly slug.")
class CreateANewTeamRequestBody(StrictModel):
    slug: str | None = Field(default=None, description="A URL-friendly identifier for the team (lowercase alphanumeric characters, hyphens, and underscores; cannot be purely numeric). Maximum 50 characters. If omitted, it will be automatically generated from the team name.", max_length=50)
class CreateANewTeamRequest(StrictModel):
    """Create a new team within an organization. At least one of `name` or `slug` must be provided in the request body."""
    path: CreateANewTeamRequestPath
    body: CreateANewTeamRequestBody | None = None

# Operation: list_user_teams_in_organization
class ListAUserSTeamsForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
class ListAUserSTeamsForAnOrganizationRequest(StrictModel):
    """Retrieve all teams within an organization that the authenticated user has access to. This endpoint requires user authentication tokens and is useful for discovering team membership and permissions."""
    path: ListAUserSTeamsForAnOrganizationRequestPath

# Operation: list_alerts
class FetchAlertsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
class FetchAlertsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional search query to filter alerts by name, status, or other alert properties.")
class FetchAlertsRequest(StrictModel):
    """Retrieve a list of alerts for an organization. This endpoint is currently in beta and supports the New Monitors and Alerts feature."""
    path: FetchAlertsRequestPath
    query: FetchAlertsRequestQuery | None = None

# Operation: create_alert_for_organization
class CreateAnAlertForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
class CreateAnAlertForAnOrganizationRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the alert, up to 256 characters in length.", max_length=256)
    enabled: bool | None = Field(default=None, description="Whether the alert is active and will evaluate conditions. Defaults to enabled if not specified.")
    detector_ids: list[int] | None = Field(default=None, description="Array of monitor IDs to associate with this alert. Use the Fetch Organization Monitors endpoint to retrieve available monitor IDs.")
    config: dict[str, Any] | None = Field(default=None, description="Configuration object specifying the evaluation frequency in minutes. Supported values are 0, 5, 10, 30, 60, 180, 720, or 1440 minutes (up to 24 hours).")
    environment: str | None = Field(default=None, description="The environment name where the alert will evaluate conditions, such as 'production' or 'staging'.")
    triggers: CreateAnAlertForAnOrganizationBodyTriggers | None = Field(default=None, description="Trigger conditions that determine when the alert fires. Includes organization ID, logic type (any-short, all, or none), an array of condition objects (first_seen_event, issue_resolved_trigger, reappeared_event, regression_event), and associated actions.")
    action_filters: list[Any] | None = Field(default=None, description="Array of action filter groups that define conditions and corresponding actions to execute. Each filter group contains a logic type, conditions array (supporting age, assignment, category, frequency, priority, user impact, event count, and attribute matching), and actions array (email, Slack, PagerDuty, Discord, MSTeams, OpsGenie, Azure DevOps, Jira, or GitHub).")
    owner: str | None = Field(default=None, description="The user or team who owns this alert, specified as 'user:USER_ID' or 'team:TEAM_ID'.")
class CreateAnAlertForAnOrganizationRequest(StrictModel):
    """Creates a new alert for an organization to monitor issues and trigger notifications based on specified conditions. This endpoint is currently in beta and supports the New Monitors and Alerts system."""
    path: CreateAnAlertForAnOrganizationRequestPath
    body: CreateAnAlertForAnOrganizationRequestBody

# Operation: update_organization_alerts_bulk
class MutateAnOrganizationSAlertsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class MutateAnOrganizationSAlertsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional search query to filter which alerts are affected by this operation. If omitted, the operation applies to all alerts in the organization.")
class MutateAnOrganizationSAlertsRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="Set to true to enable the selected alerts, or false to disable them.")
class MutateAnOrganizationSAlertsRequest(StrictModel):
    """Bulk enable or disable alerts across an organization, optionally filtered by search query. This beta endpoint supports the New Monitors and Alerts system."""
    path: MutateAnOrganizationSAlertsRequestPath
    query: MutateAnOrganizationSAlertsRequestQuery | None = None
    body: MutateAnOrganizationSAlertsRequestBody

# Operation: delete_alerts_bulk
class BulkDeleteAlertsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class BulkDeleteAlertsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="An optional search query to filter which alerts should be deleted. If omitted, the operation applies to all alerts in the organization.")
class BulkDeleteAlertsRequest(StrictModel):
    """Bulk delete alerts for an organization, optionally filtered by a search query. This endpoint is currently in beta and supported by New Monitors and Alerts."""
    path: BulkDeleteAlertsRequestPath
    query: BulkDeleteAlertsRequestQuery | None = None

# Operation: get_alert
class FetchAnAlertRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This determines which organization's alert you're accessing.")
    workflow_id: int = Field(default=..., description="The numeric ID of the alert (workflow) to retrieve.")
class FetchAnAlertRequest(StrictModel):
    """Retrieve a specific alert (workflow) by its ID. This endpoint is part of the New Monitors and Alerts system and is currently in beta."""
    path: FetchAnAlertRequestPath

# Operation: update_alert
class UpdateAnAlertByIdRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    workflow_id: int = Field(default=..., description="The numeric ID of the alert to update.")
class UpdateAnAlertByIdRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the alert. Must not exceed 256 characters.", max_length=256)
    enabled: bool | None = Field(default=None, description="Whether the alert is active and will evaluate conditions. Defaults to true if not specified.")
    detector_ids: list[int] | None = Field(default=None, description="Array of monitor IDs to associate with this alert. Use the organization monitors endpoint to retrieve available monitor IDs.")
    config: dict[str, Any] | None = Field(default=None, description="Configuration object specifying the evaluation frequency in minutes. Supported values are 0, 5, 10, 30, 60, 180, 720, or 1440 minutes.")
    environment: str | None = Field(default=None, description="The environment name where this alert will evaluate conditions. Filters alert evaluation to a specific environment.")
    triggers: UpdateAnAlertByIdBodyTriggers | None = Field(default=None, description="Trigger conditions that determine when the alert fires. Supports event-based triggers (first_seen_event, reappeared_event, regression_event, issue_resolved_trigger) with configurable logic type (any-short, all, none) and optional actions.")
    action_filters: list[Any] | None = Field(default=None, description="Array of action filter groups that define conditions and corresponding notification actions. Each filter group contains a logic type, conditions array, and actions array specifying email, Slack, PagerDuty, Discord, MSTeams, OpsGenie, Azure DevOps, Jira, or GitHub integrations.")
    owner: str | None = Field(default=None, description="The owner of the alert, specified as either 'user:USER_ID' or 'team:TEAM_ID' to indicate individual or team ownership.")
class UpdateAnAlertByIdRequest(StrictModel):
    """Updates an existing alert configuration including its name, enabled status, trigger conditions, action filters, and connected monitors. This endpoint supports the New Monitors and Alerts system and is currently in beta."""
    path: UpdateAnAlertByIdRequestPath
    body: UpdateAnAlertByIdRequestBody

# Operation: delete_alert
class DeleteAnAlertRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    workflow_id: int = Field(default=..., description="The numeric ID of the alert to delete.")
class DeleteAnAlertRequest(StrictModel):
    """Permanently deletes an alert from a workflow. This endpoint is currently in beta and supported by New Monitors and Alerts."""
    path: DeleteAnAlertRequestPath

# Operation: get_project
class RetrieveAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
class RetrieveAProjectRequest(StrictModel):
    """Retrieve detailed information about a specific project, including its configuration, settings, and metadata."""
    path: RetrieveAProjectRequestPath

# Operation: update_project
class UpdateAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either its numeric ID or URL-friendly slug.")
class UpdateAProjectRequestBody(StrictModel):
    is_bookmarked: bool | None = Field(default=None, validation_alias="isBookmarked", serialization_alias="isBookmarked", description="Star or unstar the project in the projects tab. Updatable with project:read permission.")
    name: str | None = Field(default=None, description="The display name for the project. Must not exceed 200 characters.", max_length=200)
    slug: str | None = Field(default=None, description="A URL-friendly identifier for the project used in the interface. Must be 1-100 characters, contain only lowercase letters, numbers, hyphens, and underscores, and cannot be purely numeric.", max_length=100)
    platform: str | None = Field(default=None, description="The platform or technology stack associated with the project (e.g., 'javascript', 'python', 'java').")
    subject_prefix: str | None = Field(default=None, validation_alias="subjectPrefix", serialization_alias="subjectPrefix", description="A custom prefix prepended to email subjects for alerts from this project. Must not exceed 200 characters.", max_length=200)
    subject_template: str | None = Field(default=None, validation_alias="subjectTemplate", serialization_alias="subjectTemplate", description="The email subject template for individual alerts, supporting variables like $title, $shortID, $projectID, $orgID, and tag references (e.g., ${tag:environment}). Must not exceed 200 characters.", max_length=200)
    resolve_age: int | None = Field(default=None, validation_alias="resolveAge", serialization_alias="resolveAge", description="Hours of inactivity after which issues are automatically resolved. Set to 0 to disable auto-resolution.")
    scm_source_context_enabled: bool | None = Field(default=None, validation_alias="scmSourceContextEnabled", serialization_alias="scmSourceContextEnabled", description="Enable automatic source context retrieval from configured SCM integrations to enrich stack traces with code snippets.")
class UpdateAProjectRequest(StrictModel):
    """Update project settings, metadata, and configuration options. Most settings require elevated permissions; only bookmarking and preprod-related automation settings can be modified with basic project:read access."""
    path: UpdateAProjectRequestPath
    body: UpdateAProjectRequestBody | None = None

# Operation: delete_project
class DeleteAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL slug of the project to be deleted.")
class DeleteAProjectRequest(StrictModel):
    """Schedules a project for deletion. The deletion process is asynchronous, so the project won't be immediately removed, but its state will change and it will be hidden from most public views once deletion begins."""
    path: DeleteAProjectRequestPath

# Operation: list_project_environments
class ListAProjectSEnvironmentsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its unique ID or URL-friendly slug. Required to scope the project within the correct organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either its unique ID or URL-friendly slug. Required to specify which project's environments to list.")
class ListAProjectSEnvironmentsRequestQuery(StrictModel):
    visibility: Literal["all", "hidden", "visible"] | None = Field(default=None, description="Filter environments by their visibility status. Choose 'visible' to show only active environments, 'hidden' to show only inactive ones, or 'all' to include both. Defaults to 'visible' if not specified.")
class ListAProjectSEnvironmentsRequest(StrictModel):
    """Retrieve all environments configured for a specific project, with optional filtering by visibility status. Useful for discovering available deployment targets and their configurations."""
    path: ListAProjectSEnvironmentsRequestPath
    query: ListAProjectSEnvironmentsRequestQuery | None = None

# Operation: get_project_environment
class RetrieveAProjectEnvironmentRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project.")
    environment: str = Field(default=..., description="The name of the environment to retrieve (e.g., 'production', 'staging', 'development').")
class RetrieveAProjectEnvironmentRequest(StrictModel):
    """Retrieve detailed information about a specific environment within a project, including its configuration and settings."""
    path: RetrieveAProjectEnvironmentRequestPath

# Operation: update_project_environment_visibility
class UpdateAProjectEnvironmentRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    environment: str = Field(default=..., description="The name of the environment to update (e.g., 'production', 'staging', 'development').")
class UpdateAProjectEnvironmentRequestBody(StrictModel):
    is_hidden: bool = Field(default=..., validation_alias="isHidden", serialization_alias="isHidden", description="Set to `true` to make the environment visible, or `false` to hide it from the project's environment list.")
class UpdateAProjectEnvironmentRequest(StrictModel):
    """Update the visibility status of a project environment, allowing you to show or hide it from the project's environment list."""
    path: UpdateAProjectEnvironmentRequestPath
    body: UpdateAProjectEnvironmentRequestBody

# Operation: list_project_error_events
class ListAProjectSErrorEventsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
class ListAProjectSErrorEventsRequestQuery(StrictModel):
    full: bool | None = Field(default=None, description="Include the complete event payload with stacktraces and additional details. Defaults to false for a lighter response.")
    sample: bool | None = Field(default=None, description="Return events in a deterministic pseudo-random order. Identical queries will always return the same events in the same order. Defaults to false for chronological ordering.")
class ListAProjectSErrorEventsRequest(StrictModel):
    """Retrieve a list of error events for a specific project. Optionally include full event details such as stacktraces, and control result ordering."""
    path: ListAProjectSErrorEventsRequestPath
    query: ListAProjectSErrorEventsRequestQuery | None = None

# Operation: get_source_map_debug_for_event
class DebugIssuesRelatedToSourceMapsForAGivenEventRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    event_id: str = Field(default=..., description="The event identifier as a UUID that uniquely identifies the error event to debug.", json_schema_extra={'format': 'uuid'})
class DebugIssuesRelatedToSourceMapsForAGivenEventRequestQuery(StrictModel):
    frame_idx: int = Field(default=..., description="The zero-based index of the stack frame within the exception to analyze for source map resolution issues.")
    exception_idx: int = Field(default=..., description="The zero-based index of the exception within the event's exception chain to analyze for source map resolution issues.")
class DebugIssuesRelatedToSourceMapsForAGivenEventRequest(StrictModel):
    """Retrieve source map resolution errors for a specific stack frame and exception within an event, helping diagnose why source maps failed to map minified code back to original sources."""
    path: DebugIssuesRelatedToSourceMapsForAGivenEventRequestPath
    query: DebugIssuesRelatedToSourceMapsForAGivenEventRequestQuery

# Operation: list_project_filters
class ListAProjectSDataFiltersRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
class ListAProjectSDataFiltersRequest(StrictModel):
    """Retrieve all filters configured for a specific project. Filters can be active as either boolean flags or legacy browser filter lists."""
    path: ListAProjectSDataFiltersRequestPath

# Operation: update_inbound_data_filter
class UpdateAnInboundDataFilterRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL-friendly slug.")
    filter_id: str = Field(default=..., description="The type of inbound filter to update: browser-extensions (blocks extension-caused errors), localhost (blocks 127.0.0.1 and ::1 traffic), filtered-transaction (blocks health checks and pings), web-crawlers (blocks known crawler errors), or legacy-browser (blocks errors from outdated browsers).")
class UpdateAnInboundDataFilterRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Set to true to enable the filter or false to disable it. Controls whether the specified filter actively blocks matching events.")
class UpdateAnInboundDataFilterRequest(StrictModel):
    """Enable or disable a specific inbound data filter for a project to control which events are captured and processed. Filters can target browser extensions, localhost traffic, health check transactions, web crawlers, and legacy browser errors."""
    path: UpdateAnInboundDataFilterRequestPath
    body: UpdateAnInboundDataFilterRequestBody | None = None

# Operation: list_project_client_keys
class ListAProjectSClientKeysRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
class ListAProjectSClientKeysRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Filter results to show only active or inactive client keys. If omitted, all keys are returned regardless of status.")
class ListAProjectSClientKeysRequest(StrictModel):
    """Retrieve all client keys associated with a project. Optionally filter by active or inactive status to manage project authentication credentials."""
    path: ListAProjectSClientKeysRequestPath
    query: ListAProjectSClientKeysRequestQuery | None = None

# Operation: create_project_client_key
class CreateANewClientKeyRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL-friendly slug.")
class CreateANewClientKeyRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the key (up to 64 characters). If omitted, the server will auto-generate a name.", max_length=64)
    use_case: Literal["user", "profiling", "tempest", "demo"] | None = Field(default=None, validation_alias="useCase", serialization_alias="useCase", description="The intended use case for this key: `user` for standard client integration, `profiling` for performance profiling, `tempest` for testing, or `demo` for demonstration purposes. Defaults to `user` if not specified.")
class CreateANewClientKeyRequest(StrictModel):
    """Generate a new client key for a project with server-generated secret and public key credentials. Use this to create authentication keys for integrating with the project."""
    path: CreateANewClientKeyRequestPath
    body: CreateANewClientKeyRequestBody | None = None

# Operation: get_client_key
class RetrieveAClientKeyRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
    key_id: str = Field(default=..., description="The unique identifier of the client key to retrieve.")
class RetrieveAClientKeyRequest(StrictModel):
    """Retrieve a specific client key associated with a project. Returns the key details including its configuration and status."""
    path: RetrieveAClientKeyRequestPath

# Operation: update_client_key
class UpdateAClientKeyRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The ID or slug of the organization that owns the project containing this client key.")
    project_id_or_slug: str = Field(default=..., description="The ID or slug of the project that contains this client key.")
    key_id: str = Field(default=..., description="The unique identifier of the client key to update.")
class UpdateAClientKeyRequestBodyDynamicSdkLoaderOptions(StrictModel):
    has_replay: bool | None = Field(default=None, validation_alias="hasReplay", serialization_alias="hasReplay", description="Enable or disable session replay capture for events sent with this key.")
    has_performance: bool | None = Field(default=None, validation_alias="hasPerformance", serialization_alias="hasPerformance", description="Enable or disable performance monitoring and transaction tracking for events sent with this key.")
    has_debug: bool | None = Field(default=None, validation_alias="hasDebug", serialization_alias="hasDebug", description="Enable or disable debug mode to include additional diagnostic information in events sent with this key.")
    has_feedback: bool | None = Field(default=None, validation_alias="hasFeedback", serialization_alias="hasFeedback", description="Enable or disable user feedback collection for events sent with this key.")
    has_logs_and_metrics: bool | None = Field(default=None, validation_alias="hasLogsAndMetrics", serialization_alias="hasLogsAndMetrics", description="Enable or disable logs and metrics collection for events sent with this key.")
class UpdateAClientKeyRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the client key to help identify its purpose or associated application.")
    is_active: bool | None = Field(default=None, validation_alias="isActive", serialization_alias="isActive", description="Enable or disable the client key; when deactivated, the key will not accept new events.")
    browser_sdk_version: Literal["latest", "7.x"] | None = Field(default=None, validation_alias="browserSdkVersion", serialization_alias="browserSdkVersion", description="The Sentry JavaScript SDK version to use with this key. Choose 'latest' for the most recent version or '7.x' for version 7 releases.")
    dynamic_sdk_loader_options: UpdateAClientKeyRequestBodyDynamicSdkLoaderOptions | None = Field(default=None, validation_alias="dynamicSdkLoaderOptions", serialization_alias="dynamicSdkLoaderOptions")
class UpdateAClientKeyRequest(StrictModel):
    """Update configuration settings for a client key, including its name, activation status, SDK version, and feature flags for replay, performance monitoring, debug mode, feedback, and logs/metrics collection."""
    path: UpdateAClientKeyRequestPath
    body: UpdateAClientKeyRequestBody | None = None

# Operation: delete_client_key
class DeleteAClientKeyRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    key_id: str = Field(default=..., description="The unique identifier of the client key to be deleted.")
class DeleteAClientKeyRequest(StrictModel):
    """Permanently delete a client key from a project. This action cannot be undone and will invalidate the key for authentication."""
    path: DeleteAClientKeyRequestPath

# Operation: list_project_members
class ListAProjectSOrganizationMembersRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
class ListAProjectSOrganizationMembersRequest(StrictModel):
    """Retrieves all active organization members who are assigned to at least one team associated with the specified project."""
    path: ListAProjectSOrganizationMembersRequestPath

# Operation: get_monitor_project
class RetrieveAMonitorForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, which can be either the numeric ID or the URL-friendly slug uniquely identifying the monitor within the project.")
class RetrieveAMonitorForAProjectRequest(StrictModel):
    """Retrieves detailed information about a specific monitor within a project, including its configuration, status, and alert rules."""
    path: RetrieveAMonitorForAProjectRequestPath

# Operation: update_monitor_project
class UpdateAMonitorForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL-friendly slug.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, either the numeric ID or URL-friendly slug.")
class UpdateAMonitorForAProjectRequestBody(StrictModel):
    project: str = Field(default=..., description="The project slug to associate this monitor with.")
    name: str = Field(default=..., description="Display name for the monitor used in notifications and UI. Maximum 128 characters. If not provided, the slug will be auto-derived from this name.", max_length=128)
    config: UpdateAMonitorForAProjectBodyConfig = Field(default=..., description="The monitor's configuration object defining its behavior, thresholds, and check-in expectations.")
    slug: str | None = Field(default=None, description="Unique identifier for the monitor within the organization. Must start with a letter or underscore, contain only lowercase letters, numbers, hyphens, and underscores, and not exceed 50 characters. Changing this requires updating any check-in calls that reference it.", max_length=50)
    status: Literal["active", "disabled"] | None = Field(default=None, description="Current operational state of the monitor. Disabled monitors will not accept events and do not count toward quota limits. Defaults to active.")
    owner: str | None = Field(default=None, description="The team or user responsible for this monitor, specified as 'user:{user_id}' or 'team:{team_id}'.")
    is_muted: bool | None = Field(default=None, description="When enabled, prevents the creation of new monitor incidents while keeping the monitor active.")
class UpdateAMonitorForAProjectRequest(StrictModel):
    """Update an existing monitor's configuration, name, status, and ownership settings. Changes to the monitor slug will require updates to any instrumented check-in calls referencing the old slug."""
    path: UpdateAMonitorForAProjectRequestPath
    body: UpdateAMonitorForAProjectRequestBody

# Operation: delete_monitor_for_project
class DeleteAMonitorOrMonitorEnvironmentsForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, either the numeric ID or the URL-friendly slug.")
class DeleteAMonitorOrMonitorEnvironmentsForAProjectRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to delete. When provided, only the specified environments are removed from the monitor; when omitted, the entire monitor is deleted.")
class DeleteAMonitorOrMonitorEnvironmentsForAProjectRequest(StrictModel):
    """Delete a monitor or specific monitor environments within a project. Optionally target specific environments for deletion; if no environments are specified, the entire monitor is deleted."""
    path: DeleteAMonitorOrMonitorEnvironmentsForAProjectRequestPath
    query: DeleteAMonitorOrMonitorEnvironmentsForAProjectRequestQuery | None = None

# Operation: list_checkins_for_monitor_in_project
class RetrieveCheckInsForAMonitorByProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific project within the organization.")
    monitor_id_or_slug: str = Field(default=..., description="The monitor identifier, either the numeric ID or the URL-friendly slug. This specifies which monitor's check-ins to retrieve.")
class RetrieveCheckInsForAMonitorByProjectRequest(StrictModel):
    """Retrieve all check-ins recorded for a specific monitor within a project. Check-ins represent heartbeat or status update events tracked by the monitor."""
    path: RetrieveCheckInsForAMonitorByProjectRequestPath

# Operation: get_project_ownership_configuration
class RetrieveOwnershipConfigurationForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL slug of the project within the organization.")
class RetrieveOwnershipConfigurationForAProjectRequest(StrictModel):
    """Retrieve the ownership configuration for a project, including details about code ownership rules and assignments."""
    path: RetrieveOwnershipConfigurationForAProjectRequestPath

# Operation: update_project_ownership_configuration
class UpdateOwnershipConfigurationForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The ID or slug of the organization that owns the project.")
    project_id_or_slug: str = Field(default=..., description="The ID or slug of the project whose ownership configuration will be updated.")
class UpdateOwnershipConfigurationForAProjectRequestBody(StrictModel):
    raw: str | None = Field(default=None, description="Raw ownership rules configuration in the format specified by the Ownership Rules documentation. This defines which team members or groups own specific code paths or issue types.")
    fallthrough: bool | None = Field(default=None, description="Determines ownership assignment when no ownership rule matches. When true, all project members become owners; when false, no owners are assigned for unmatched cases.")
    auto_assignment: str | None = Field(default=None, validation_alias="autoAssignment", serialization_alias="autoAssignment", description="Configures automatic issue assignment behavior. Choose from: auto-assign to the issue creator, auto-assign based on suspect commits from version control, or disable auto-assignment entirely.")
    codeowners_auto_sync: bool | None = Field(default=None, validation_alias="codeownersAutoSync", serialization_alias="codeownersAutoSync", description="When enabled, automatically syncs issue owners with updates to the CODEOWNERS file in releases. Defaults to true.")
class UpdateOwnershipConfigurationForAProjectRequest(StrictModel):
    """Updates ownership configurations for a project, including rules, fallthrough behavior, auto-assignment settings, and CODEOWNERS synchronization. Only submitted attributes are modified."""
    path: UpdateOwnershipConfigurationForAProjectRequestPath
    body: UpdateOwnershipConfigurationForAProjectRequestBody | None = None

# Operation: get_latest_installable_build
class GetTheLatestInstallableBuildForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL-friendly slug.")
class GetTheLatestInstallableBuildForAProjectRequestQuery(StrictModel):
    app_id: str = Field(default=..., validation_alias="appId", serialization_alias="appId", description="The application identifier to match exactly against available builds.")
    platform: str = Field(default=..., description="The target platform for the build: either 'apple' for iOS or 'android' for Android.")
    build_version: str | None = Field(default=None, validation_alias="buildVersion", serialization_alias="buildVersion", description="The current build version installed on the device. When provided, the response includes the current build details and indicates whether an update is available.")
    build_configuration: str | None = Field(default=None, validation_alias="buildConfiguration", serialization_alias="buildConfiguration", description="Filter results to a specific build configuration by exact name match (e.g., 'debug', 'release').")
    codesigning_type: str | None = Field(default=None, validation_alias="codesigningType", serialization_alias="codesigningType", description="Filter results by code signing type to match your app's signing configuration.")
    install_groups: list[str] | None = Field(default=None, validation_alias="installGroups", serialization_alias="installGroups", description="Filter results to one or more install groups by name. Specify multiple times to include builds from multiple groups.")
class GetTheLatestInstallableBuildForAProjectRequest(StrictModel):
    """Retrieve the latest installable build for a project matching the specified criteria. Optionally check for available updates by providing the current build version."""
    path: GetTheLatestInstallableBuildForAProjectRequestPath
    query: GetTheLatestInstallableBuildForAProjectRequestQuery

# Operation: delete_replay
class DeleteAReplayInstanceRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    replay_id: str = Field(default=..., description="The unique identifier (UUID) of the replay to delete.", json_schema_extra={'format': 'uuid'})
class DeleteAReplayInstanceRequest(StrictModel):
    """Permanently delete a replay instance from a project. This action cannot be undone."""
    path: DeleteAReplayInstanceRequestPath

# Operation: list_clicked_nodes
class ListClickedNodesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its unique ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either its unique ID or URL-friendly slug.")
    replay_id: str = Field(default=..., description="The unique identifier (UUID format) of the replay session to retrieve click data from.", json_schema_extra={'format': 'uuid'})
class ListClickedNodesRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter results to include only clicks from sessions in specified environments. Provide as a list of environment names.")
    per_page: int | None = Field(default=None, description="Limit the number of results returned. Maximum allowed is 100 (default).")
    query: str | None = Field(default=None, description="Filter results using Sentry's query syntax to narrow down clicks by transaction, release, or other attributes. Supports boolean operators (AND, OR) and comma-separated value lists.")
class ListClickedNodesRequest(StrictModel):
    """Retrieve all DOM nodes that were clicked during a session replay, including their RRWeb node IDs and exact click timestamps. Use this to understand user interaction patterns within a specific replay."""
    path: ListClickedNodesRequestPath
    query: ListClickedNodesRequestQuery | None = None

# Operation: list_replay_recording_segments
class ListRecordingSegmentsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL-friendly slug.")
    replay_id: str = Field(default=..., description="The unique identifier (UUID) of the replay session whose recording segments you want to retrieve.", json_schema_extra={'format': 'uuid'})
class ListRecordingSegmentsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of segments to return per request. Defaults to 100 and cannot exceed 100.")
class ListRecordingSegmentsRequest(StrictModel):
    """Retrieve all recording segments for a specific replay session. Recording segments contain the captured user interaction data that makes up a replay."""
    path: ListRecordingSegmentsRequestPath
    query: ListRecordingSegmentsRequestQuery | None = None

# Operation: get_recording_segment
class RetrieveARecordingSegmentRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's resources are accessed.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL-friendly slug. This determines which project within the organization contains the replay.")
    replay_id: str = Field(default=..., description="The unique identifier of the replay session, formatted as a UUID. This identifies which replay the segment belongs to.", json_schema_extra={'format': 'uuid'})
    segment_id: int = Field(default=..., description="The numeric identifier of the recording segment within the replay. Segments are indexed sequentially and represent discrete portions of the replay recording.")
class RetrieveARecordingSegmentRequest(StrictModel):
    """Retrieve a specific recording segment from a replay session. Recording segments contain the captured user interaction data for a portion of the replay."""
    path: RetrieveARecordingSegmentRequestPath

# Operation: list_users_who_viewed_replay
class ListUsersWhoHaveViewedAReplayRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug. Used to scope the resource within your organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL-friendly slug. Used to scope the replay within a specific project.")
    replay_id: str = Field(default=..., description="The unique identifier of the replay in UUID format. Specifies which replay's viewers you want to retrieve.", json_schema_extra={'format': 'uuid'})
class ListUsersWhoHaveViewedAReplayRequest(StrictModel):
    """Retrieve a list of users who have viewed a specific replay within a project. Useful for understanding replay engagement and visibility."""
    path: ListUsersWhoHaveViewedAReplayRequestPath

# Operation: list_replay_deletion_jobs
class ListReplayBatchDeletionJobsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific project within the organization.")
class ListReplayBatchDeletionJobsRequest(StrictModel):
    """Retrieve a list of all replay deletion jobs for a project. Use this to monitor the status and history of bulk replay deletion operations."""
    path: ListReplayBatchDeletionJobsRequestPath

# Operation: create_replay_deletion_job
class CreateReplayBatchDeletionJobRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug of the project.")
class CreateReplayBatchDeletionJobRequestBodyData(StrictModel):
    range_start: str = Field(default=..., validation_alias="rangeStart", serialization_alias="rangeStart", description="The start of the time range for replay deletion, specified as an ISO 8601 formatted datetime string (inclusive).", json_schema_extra={'format': 'date-time'})
    range_end: str = Field(default=..., validation_alias="rangeEnd", serialization_alias="rangeEnd", description="The end of the time range for replay deletion, specified as an ISO 8601 formatted datetime string (inclusive).", json_schema_extra={'format': 'date-time'})
    environments: list[str] = Field(default=..., validation_alias="environments", serialization_alias="environments", description="A list of environment names to filter replays for deletion. Only replays from these environments will be included in the job.")
    query: str | None = Field(default=..., validation_alias="query", serialization_alias="query", description="A search query string to further filter which replays should be deleted. The query uses the same syntax as replay search filters.")
class CreateReplayBatchDeletionJobRequestBody(StrictModel):
    data: CreateReplayBatchDeletionJobRequestBodyData
class CreateReplayBatchDeletionJobRequest(StrictModel):
    """Create a new batch job to delete replays matching specified criteria. The job will process replays within the given time range, environments, and query filters."""
    path: CreateReplayBatchDeletionJobRequestPath
    body: CreateReplayBatchDeletionJobRequestBody

# Operation: get_replay_deletion_job
class RetrieveAReplayBatchDeletionJobRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific project within the organization.")
    job_id: int = Field(default=..., description="The unique identifier of the replay deletion job. This must be a positive integer representing the specific job you want to retrieve.")
class RetrieveAReplayBatchDeletionJobRequest(StrictModel):
    """Retrieve the status and details of a specific replay batch deletion job by its ID. Use this to monitor the progress and outcome of a deletion operation."""
    path: RetrieveAReplayBatchDeletionJobRequestPath

# Operation: get_issue_alert_rule
class DeprecatedRetrieveAnIssueAlertRuleForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug of the project.")
    rule_id: int = Field(default=..., description="The numeric ID of the alert rule to retrieve.")
class DeprecatedRetrieveAnIssueAlertRuleForAProjectRequest(StrictModel):
    """Retrieve details for a specific issue alert rule in a project. Issue alert rules define triggers, filters, and actions that determine when alerts are sent for matching issues. Note: This endpoint is deprecated; use the Fetch an Alert endpoint instead."""
    path: DeprecatedRetrieveAnIssueAlertRuleForAProjectRequestPath

# Operation: update_issue_alert_rule
class DeprecatedUpdateAnIssueAlertRuleRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL slug.")
    rule_id: int = Field(default=..., description="The numeric ID of the alert rule to update.")
class DeprecatedUpdateAnIssueAlertRuleRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the alert rule, up to 256 characters.", max_length=256)
    action_match: Literal["all", "any", "none"] = Field(default=..., validation_alias="actionMatch", serialization_alias="actionMatch", description="Determines how conditions are evaluated: 'all' requires all conditions to be true, 'any' requires at least one to be true, and 'none' requires all to be false.")
    conditions: list[dict[str, Any]] = Field(default=..., description="An array of trigger conditions that determine when the rule fires. Refer to the Create an Issue Alert Rule endpoint for valid condition types and structures.")
    actions: list[dict[str, Any]] = Field(default=..., description="An array of actions to execute when conditions and filters are met. Refer to the Create an Issue Alert Rule endpoint for valid action types and structures.")
    frequency: int = Field(default=..., description="The interval in minutes between repeated actions for the same issue, ranging from 5 to 43200 minutes (30 days).", ge=5, le=43200)
    environment: str | None = Field(default=None, description="Optional environment name to filter alerts by. If specified, the rule only applies to events from this environment.")
    filter_match: Literal["all", "any", "none"] | None = Field(default=None, validation_alias="filterMatch", serialization_alias="filterMatch", description="Determines how filters are evaluated: 'all' requires all filters to match, 'any' requires at least one to match, and 'none' requires all to not match.")
    filters: list[dict[str, Any]] | None = Field(default=None, description="An optional array of filters that further refine when the rule fires after conditions are met. Refer to the Create an Issue Alert Rule endpoint for valid filter types and structures.")
    owner: str | None = Field(default=None, description="Optional identifier of the team or user that owns this alert rule.")
class DeprecatedUpdateAnIssueAlertRuleRequest(StrictModel):
    """Update an issue alert rule that triggers on events matching specified conditions. This operation fully overwrites the alert rule, so all required fields must be provided. Note: This endpoint is deprecated; use the Alert by ID endpoint instead."""
    path: DeprecatedUpdateAnIssueAlertRuleRequestPath
    body: DeprecatedUpdateAnIssueAlertRuleRequestBody

# Operation: delete_issue_alert_rule
class DeprecatedDeleteAnIssueAlertRuleRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization that owns the project.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug of the project containing the alert rule.")
    rule_id: int = Field(default=..., description="The numeric ID of the alert rule to delete.")
class DeprecatedDeleteAnIssueAlertRuleRequest(StrictModel):
    """Delete a specific issue alert rule from a project. Issue alert rules trigger on new events matching specified conditions (such as resolved issues reappearing or issues affecting many users) and are configured with triggers, filters, and actions. Note: This endpoint is deprecated; use the Delete an Alert endpoint instead."""
    path: DeprecatedDeleteAnIssueAlertRuleRequestPath

# Operation: list_project_symbol_sources
class RetrieveAProjectSSymbolSourcesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
class RetrieveAProjectSSymbolSourcesRequest(StrictModel):
    """Retrieve all custom symbol sources configured for a specific project. Symbol sources enable the project to resolve debug symbols from external repositories."""
    path: RetrieveAProjectSSymbolSourcesRequestPath

# Operation: add_symbol_source_to_project
class AddASymbolSourceToAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL-friendly slug.")
class AddASymbolSourceToAProjectRequestBodyLayout(StrictModel):
    type_: Literal["native", "symstore", "symstore_index2", "ssqp", "unified", "debuginfod", "slashsymbols"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The directory layout format used by the symbol source: native, symstore, symstore_index2, SSQP, unified, debuginfod, or /symbols.")
    casing: Literal["lowercase", "uppercase", "default"] = Field(default=..., validation_alias="casing", serialization_alias="casing", description="How file paths are normalized: lowercase, uppercase, or default (no transformation).")
class AddASymbolSourceToAProjectRequestBodyFilters(StrictModel):
    filetypes: list[Literal["pe", "pdb", "portablepdb", "mach_debug", "mach_code", "elf_debug", "elf_code", "wasm_debug", "wasm_code", "breakpad", "sourcebundle", "uuidmap", "bcsymbolmap", "il2cpp", "proguard", "dartsymbolmap"]] | None = Field(default=None, validation_alias="filetypes", serialization_alias="filetypes", description="Array of file extensions to enable for this source (e.g., 'pdb', 'elf', 'dwarf'). If omitted, all supported types are enabled.")
    path_patterns: list[str] | None = Field(default=None, validation_alias="path_patterns", serialization_alias="path_patterns", description="Array of glob patterns to match against debug and code file paths. If omitted, all paths are accepted.")
    requires_checksum: bool | None = Field(default=None, validation_alias="requires_checksum", serialization_alias="requires_checksum", description="Whether debug checksums must be present and validated for files from this source.")
class AddASymbolSourceToAProjectRequestBody(StrictModel):
    type_: Literal["http", "gcs", "s3"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The symbol source backend type: HTTP (SymbolServer), Google Cloud Storage, or Amazon S3.")
    name: str = Field(default=..., description="A human-readable display name for this symbol source.")
    url: str | None = Field(default=None, description="The base URL of the symbol server. Required for HTTP sources; must be omitted for GCS and S3 sources.")
    username: str | None = Field(default=None, description="Username for HTTP Basic Authentication. Valid only for HTTP sources.")
    password: str | None = Field(default=None, description="Password for HTTP Basic Authentication. Valid only for HTTP sources.")
    bucket: str | None = Field(default=None, description="The bucket name containing symbols. Required for GCS and S3 sources; must be omitted for HTTP sources.")
    region: Literal["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ap-east-1", "ap-south-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "sa-east-1", "us-gov-east-1", "us-gov-west-1"] | None = Field(default=None, description="The AWS region where the S3 bucket is located. Required for S3 sources; must be omitted for HTTP and GCS sources.")
    access_key: str | None = Field(default=None, description="The AWS Access Key for S3 authentication. Required for S3 sources; must be omitted for HTTP and GCS sources.")
    secret_key: str | None = Field(default=None, description="The AWS Secret Access Key for S3 authentication. Required for S3 sources; must be omitted for HTTP and GCS sources.")
    prefix: str | None = Field(default=None, description="A path prefix within the bucket to scope symbol lookups. Optional for GCS and S3 sources; must be omitted for HTTP sources.")
    client_email: str | None = Field(default=None, description="The service account email address for GCS authentication. Required for GCS sources; must be omitted for HTTP and S3 sources.")
    private_key: str | None = Field(default=None, description="The private key for GCS service account authentication. Required for GCS sources unless using impersonated tokens; must be omitted for HTTP and S3 sources.")
    layout: AddASymbolSourceToAProjectRequestBodyLayout
    filters: AddASymbolSourceToAProjectRequestBodyFilters | None = None
class AddASymbolSourceToAProjectRequest(StrictModel):
    """Add a custom symbol source to a project for debug symbol resolution. Supports HTTP, Google Cloud Storage, and Amazon S3 backends with configurable layout types and casing rules."""
    path: AddASymbolSourceToAProjectRequestPath
    body: AddASymbolSourceToAProjectRequestBody

# Operation: update_project_symbol_source
class UpdateAProjectSSymbolSourceRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL-friendly slug.")
class UpdateAProjectSSymbolSourceRequestQuery(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the symbol source to update.")
class UpdateAProjectSSymbolSourceRequestBodyLayout(StrictModel):
    type_: Literal["native", "symstore", "symstore_index2", "ssqp", "unified", "debuginfod", "slashsymbols"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The directory structure layout format used by the symbol source: native, symstore, symstore_index2, ssqp, unified, debuginfod, or slashsymbols.")
    casing: Literal["lowercase", "uppercase", "default"] = Field(default=..., validation_alias="casing", serialization_alias="casing", description="Path casing normalization rule: lowercase, uppercase, or default (no transformation).")
class UpdateAProjectSSymbolSourceRequestBodyFilters(StrictModel):
    filetypes: list[Literal["pe", "pdb", "portablepdb", "mach_debug", "mach_code", "elf_debug", "elf_code", "wasm_debug", "wasm_code", "breakpad", "sourcebundle", "uuidmap", "bcsymbolmap", "il2cpp", "proguard", "dartsymbolmap"]] | None = Field(default=None, validation_alias="filetypes", serialization_alias="filetypes", description="Array of file type extensions to enable for symbol resolution (e.g., 'pdb', 'dwarf', 'macho'). Order is not significant.")
    path_patterns: list[str] | None = Field(default=None, validation_alias="path_patterns", serialization_alias="path_patterns", description="Array of glob patterns to filter which debug and code file paths are queried from this source. Order is not significant.")
    requires_checksum: bool | None = Field(default=None, validation_alias="requires_checksum", serialization_alias="requires_checksum", description="Whether symbol lookups from this source must include and validate debug checksums.")
class UpdateAProjectSSymbolSourceRequestBody(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Custom internal identifier for the source. Must be unique across all sources in the project and cannot begin with 'sentry:'. If omitted, a UUID will be automatically generated.")
    type_: Literal["http", "gcs", "s3"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The symbol source backend type: HTTP (SymbolServer), Google Cloud Storage, or Amazon S3.")
    name: str = Field(default=..., description="A human-readable display name for the symbol source.")
    url: str | None = Field(default=None, description="The base URL of the HTTP symbol server. Required only for HTTP sources; invalid for cloud storage sources.")
    username: str | None = Field(default=None, description="Username for HTTP Basic Authentication. Valid only for HTTP sources.")
    password: str | None = Field(default=None, description="Password for HTTP Basic Authentication. Valid only for HTTP sources.")
    bucket: str | None = Field(default=None, description="The bucket name in Google Cloud Storage or Amazon S3. Required for GCS and S3 sources; invalid for HTTP sources.")
    region: Literal["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ap-east-1", "ap-south-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "sa-east-1", "us-gov-east-1", "us-gov-west-1"] | None = Field(default=None, description="The AWS region where the S3 bucket is located. Required for S3 sources; invalid for HTTP and GCS sources.")
    access_key: str | None = Field(default=None, description="The AWS Access Key for S3 authentication. Required for S3 sources; invalid for HTTP and GCS sources.")
    secret_key: str | None = Field(default=None, description="The AWS Secret Access Key for S3 authentication. Required for S3 sources; invalid for HTTP and GCS sources.")
    prefix: str | None = Field(default=None, description="The object key prefix path within the GCS or S3 bucket. Optional for cloud storage sources; invalid for HTTP sources.")
    client_email: str | None = Field(default=None, description="The service account email address for GCS authentication. Required for GCS sources; invalid for HTTP and S3 sources.")
    private_key: str | None = Field(default=None, description="The private key for GCS service account authentication. Required for GCS sources when not using impersonated tokens; invalid for HTTP and S3 sources.")
    layout: UpdateAProjectSSymbolSourceRequestBodyLayout
    filters: UpdateAProjectSSymbolSourceRequestBodyFilters | None = None
class UpdateAProjectSSymbolSourceRequest(StrictModel):
    """Update an existing custom symbol source configuration in a project. Modify source type, layout, authentication credentials, and file filtering rules for symbol resolution."""
    path: UpdateAProjectSSymbolSourceRequestPath
    query: UpdateAProjectSSymbolSourceRequestQuery
    body: UpdateAProjectSSymbolSourceRequestBody

# Operation: delete_symbol_source
class DeleteASymbolSourceFromAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
class DeleteASymbolSourceFromAProjectRequestQuery(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the symbol source to delete.")
class DeleteASymbolSourceFromAProjectRequest(StrictModel):
    """Remove a custom symbol source from a project. This permanently deletes the symbol source configuration and its associated data."""
    path: DeleteASymbolSourceFromAProjectRequestPath
    query: DeleteASymbolSourceFromAProjectRequestQuery

# Operation: list_teams_for_project
class ListAProjectSTeamsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project.")
class ListAProjectSTeamsRequest(StrictModel):
    """Retrieve all teams that have access to a specific project within an organization."""
    path: ListAProjectSTeamsRequestPath

# Operation: add_team_to_project
class AddATeamToAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, which can be either the numeric ID or the URL-friendly slug of the team to grant access.")
class AddATeamToAProjectRequest(StrictModel):
    """Grant a team access to a project, enabling collaboration and resource sharing within the specified organization."""
    path: AddATeamToAProjectRequestPath

# Operation: delete_team_from_project
class DeleteATeamFromAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug.")
class DeleteATeamFromAProjectRequest(StrictModel):
    """Revoke a team's access to a project. Team Admins can only revoke access for teams they administer."""
    path: DeleteATeamFromAProjectRequestPath

# Operation: get_custom_integration
class RetrieveACustomIntegrationByIdOrSlugRequestPath(StrictModel):
    sentry_app_id_or_slug: str = Field(default=..., description="The unique identifier or URL-friendly slug of the custom integration. You can use either the numeric ID or the slug string to identify which custom integration to retrieve.")
class RetrieveACustomIntegrationByIdOrSlugRequest(StrictModel):
    """Retrieve details about a custom integration (Sentry App) by its unique identifier or slug. Use this to fetch configuration, permissions, and metadata for a specific custom integration."""
    path: RetrieveACustomIntegrationByIdOrSlugRequestPath

# Operation: delete_custom_integration
class DeleteACustomIntegrationRequestPath(StrictModel):
    sentry_app_id_or_slug: str = Field(default=..., description="The unique identifier or slug of the custom integration to delete. You can use either the numeric ID or the URL-friendly slug name.")
class DeleteACustomIntegrationRequest(StrictModel):
    """Permanently delete a custom integration (Sentry app) from your organization. This action cannot be undone."""
    path: DeleteACustomIntegrationRequestPath

# Operation: get_team
class RetrieveATeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the team lookup to a specific organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL-friendly slug. Combined with the organization identifier to uniquely identify the team.")
class RetrieveATeamRequestQuery(StrictModel):
    expand: str | None = Field(default=None, description="Comma-separated list of related data to include in the response. Supports `projects` to include team projects and `externalTeams` to include external team integrations.")
    collapse: str | None = Field(default=None, description="Comma-separated list of data fields to exclude from the response. Supports `organization` to omit the parent organization details.")
class RetrieveATeamRequest(StrictModel):
    """Retrieve detailed information about a specific team within an organization. Use organization and team identifiers (IDs or slugs) to fetch the team resource with optional expansion of related data."""
    path: RetrieveATeamRequestPath
    query: RetrieveATeamRequestQuery | None = None

# Operation: update_team
class UpdateATeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL-friendly slug.")
class UpdateATeamRequestBody(StrictModel):
    slug: str = Field(default=..., description="A unique identifier for the team using lowercase letters, numbers, hyphens, and underscores (cannot be purely numeric). Maximum 50 characters.", max_length=50)
class UpdateATeamRequest(StrictModel):
    """Update team attributes and configurable settings such as the team slug and other team-level properties."""
    path: UpdateATeamRequestPath
    body: UpdateATeamRequestBody

# Operation: delete_team
class DeleteATeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, which can be either the numeric ID or the URL slug of the team to be deleted.")
class DeleteATeamRequest(StrictModel):
    """Schedules a team for deletion. The deletion process is asynchronous, so the team won't be immediately removed, but its slug will be released immediately while the deletion completes in the background."""
    path: DeleteATeamRequestPath

# Operation: link_external_team
class CreateAnExternalTeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug of the team within the organization.")
class CreateAnExternalTeamRequestBody(StrictModel):
    external_name: str = Field(default=..., description="The name or identifier of the external team as it appears in the provider system.")
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(default=..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems.")
    integration_id: int = Field(default=..., description="The numeric ID of the integration configuration that connects Sentry to the external provider.")
    external_id: str | None = Field(default=None, description="The unique identifier of the external team or user within the provider system. This field is optional and may be required depending on the provider.")
class CreateAnExternalTeamRequest(StrictModel):
    """Link a team from an external provider (such as GitHub, Slack, Jira, or GitLab) to a Sentry team, enabling cross-platform team synchronization and integration."""
    path: CreateAnExternalTeamRequestPath
    body: CreateAnExternalTeamRequestBody

# Operation: update_external_team
class UpdateAnExternalTeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug of the team within the organization.")
    external_team_id: int = Field(default=..., description="The unique identifier of the external team object to update, returned when the external team was originally created.")
class UpdateAnExternalTeamRequestBody(StrictModel):
    external_name: str = Field(default=..., description="The display name or identifier for the external team in the provider system.")
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(default=..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems.")
    integration_id: int = Field(default=..., description="The numeric ID of the integration that connects Sentry to the external provider.")
    external_id: str | None = Field(default=None, description="The unique identifier or handle for the external team within the provider system (e.g., user ID, team ID, or handle). Optional if not applicable to the provider.")
class UpdateAnExternalTeamRequest(StrictModel):
    """Update the configuration of an external team (from GitHub, Slack, Jira, etc.) that is linked to a Sentry team. This allows you to modify the external team's name, provider details, and associated identifiers."""
    path: UpdateAnExternalTeamRequestPath
    body: UpdateAnExternalTeamRequestBody

# Operation: delete_external_team_link
class DeleteAnExternalTeamRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization containing the team.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either the numeric ID or the URL slug of the Sentry team to disconnect from the external provider.")
    external_team_id: int = Field(default=..., description="The numeric ID of the external team link to delete, as returned when the external team integration was originally created.")
class DeleteAnExternalTeamRequest(StrictModel):
    """Remove the integration link between an external team (from a provider like GitHub or Slack) and a Sentry team, effectively disconnecting the external team from Sentry's team management."""
    path: DeleteAnExternalTeamRequestPath

# Operation: list_team_members
class ListATeamSMembersRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, which can be either the numeric ID or the URL slug of the team within the organization.")
class ListATeamSMembersRequest(StrictModel):
    """Retrieve all active members of a team within an organization. Note that members with pending invitations are excluded from the results."""
    path: ListATeamSMembersRequestPath

# Operation: list_team_projects
class ListATeamSProjectsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, which can be either the numeric ID or the URL-friendly slug of the team within the organization.")
class ListATeamSProjectsRequest(StrictModel):
    """Retrieve all projects associated with a specific team within an organization. Returns a list of projects bound to the team."""
    path: ListATeamSProjectsRequestPath

# Operation: create_project_for_team
class CreateANewProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug.")
    team_id_or_slug: str = Field(default=..., description="The team identifier, either its numeric ID or URL slug.")
class CreateANewProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the project. Must not exceed 50 characters.", max_length=50)
    slug: str | None = Field(default=None, description="A URL-safe identifier for the project used in the interface. If omitted, it will be auto-generated from the project name. Must contain only lowercase letters, numbers, hyphens, and underscores, cannot be purely numeric, and must not exceed 100 characters.", max_length=100)
    platform: str | None = Field(default=None, description="The platform or technology stack associated with the project (e.g., JavaScript, Python, Java).")
    default_rules: bool | None = Field(default=None, description="Whether to enable default alert rules that notify on every new issue. Defaults to true; set to false to require manual alert configuration.")
class CreateANewProjectRequest(StrictModel):
    """Create a new project within a team. Requires org:write or team:admin scope if your organization has disabled member project creation."""
    path: CreateANewProjectRequestPath
    body: CreateANewProjectRequestBody

# Operation: list_organization_repositories
class ListAnOrganizationSRepositoriesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the organization's slug (short name). Use the slug for human-readable requests or the ID for programmatic lookups.")
class ListAnOrganizationSRepositoriesRequest(StrictModel):
    """Retrieve all version control repositories belonging to a specified organization. Returns a paginated list of repositories accessible to the authenticated user."""
    path: ListAnOrganizationSRepositoriesRequestPath

# Operation: list_debug_information_files
class ListAProjectSDebugInformationFilesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
class ListAProjectSDebugInformationFilesRequest(StrictModel):
    """Retrieve all debug information files (dSYMs and other debug symbols) associated with a specific project. These files are used for symbolication and error tracking."""
    path: ListAProjectSDebugInformationFilesRequestPath

# Operation: upload_dsym_file
class UploadANewFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug. Used to scope the project within your organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug. Specifies which project receives the debug information file.")
class UploadANewFileRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The dSYM file to upload as binary data. Must be a zip archive containing Apple .dSYM folders with debug images.", json_schema_extra={'format': 'binary'})
class UploadANewFileRequest(StrictModel):
    """Upload a debug information file (dSYM) for a specific release. The file must be a zip archive containing Apple .dSYM folders with debug images; uploading creates separate files for each contained image. Use region-specific domains (e.g., us.sentry.io or de.sentry.io) for this request."""
    path: UploadANewFileRequestPath
    body: UploadANewFileRequestBody

# Operation: delete_debug_information_file
class DeleteASpecificProjectSDebugInformationFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug of the organization that owns the project.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug of the project containing the debug information file to delete.")
class DeleteASpecificProjectSDebugInformationFileRequestQuery(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the debug information file to delete.")
class DeleteASpecificProjectSDebugInformationFileRequest(StrictModel):
    """Permanently delete a specific debug information file (DIF) from a project. This removes the debug symbols associated with the given DIF ID."""
    path: DeleteASpecificProjectSDebugInformationFileRequestPath
    query: DeleteASpecificProjectSDebugInformationFileRequestQuery

# Operation: list_project_users
class ListAProjectSUsersRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or a URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or a URL-friendly slug.")
class ListAProjectSUsersRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional search filter to narrow results by user attributes. Use prefixed queries in the format `field:value` where field is one of: `id`, `email`, `username`, or `ip`. Multiple filters can be combined.")
class ListAProjectSUsersRequest(StrictModel):
    """Retrieve a list of users who have been seen or are active within a specific project. Optionally filter results by user attributes such as ID, email, username, or IP address."""
    path: ListAProjectSUsersRequestPath
    query: ListAProjectSUsersRequestQuery | None = None

# Operation: list_tag_values
class ListATagSValuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug.")
    key: str = Field(default=..., description="The tag key name to retrieve associated values for.")
class ListATagSValuesRequest(StrictModel):
    """Retrieve all values associated with a specific tag key in a project. Supports filtering values using a contains-based query parameter and returns up to 1000 results per page."""
    path: ListATagSValuesRequestPath

# Operation: get_event_counts_for_project
class RetrieveEventCountsForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug.")
class RetrieveEventCountsForAProjectRequestQuery(StrictModel):
    stat: Literal["received", "rejected", "blacklisted", "generated"] | None = Field(default=None, description="The type of event statistic to retrieve: received (accepted events), rejected (rate-limited events), blacklisted (filtered events), or generated (server-generated events).")
    since: str | None = Field(default=None, description="The start of the query time range as an ISO 8601 formatted timestamp. If omitted, defaults to a recent time window.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the query time range as an ISO 8601 formatted timestamp. If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    resolution: Literal["10s", "1h", "1d"] | None = Field(default=None, description="The time bucket size for aggregating results: 10 seconds for fine-grained data, 1 hour for daily trends, or 1 day for long-term analysis. If omitted, Sentry selects an appropriate resolution based on the query range.")
class RetrieveEventCountsForAProjectRequest(StrictModel):
    """Retrieve event statistics for a project over a specified time range. Returns normalized timestamps with event counts aggregated at the requested resolution. Query ranges are limited by Sentry's configured time-series resolutions."""
    path: RetrieveEventCountsForAProjectRequestPath
    query: RetrieveEventCountsForAProjectRequestQuery | None = None

# Operation: list_project_user_feedback
class ListAProjectSUserFeedbackRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug.")
class ListAProjectSUserFeedbackRequest(StrictModel):
    """Retrieve a list of user feedback items submitted to a project. Note: This returns legacy User Reports format feedback; for User Feedback Widget submissions, use the issues API with the `issue.category:feedback` filter instead."""
    path: ListAProjectSUserFeedbackRequestPath

# Operation: submit_user_feedback
class SubmitUserFeedbackRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug.")
class SubmitUserFeedbackRequestBody(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to attach feedback to. This value can be obtained from the beforeSend callback in your SDK configuration.")
    name: str = Field(default=..., description="The full name of the user providing feedback.")
    email: str = Field(default=..., description="The email address of the user providing feedback.")
    comments: str = Field(default=..., description="The user's feedback comments or message describing their experience.")
class SubmitUserFeedbackRequest(StrictModel):
    """Submit user feedback for a specific event. This endpoint is deprecated; use the User Feedback Widget or platform-specific User Feedback API instead. Feedback must be submitted within 30 minutes of the event and can be overwritten within 5 minutes of initial submission."""
    path: SubmitUserFeedbackRequestPath
    body: SubmitUserFeedbackRequestBody

# Operation: list_project_service_hooks
class ListAProjectSServiceHooksRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
class ListAProjectSServiceHooksRequest(StrictModel):
    """Retrieve all service hooks configured for a specific project. Service hooks enable integrations that trigger on project events."""
    path: ListAProjectSServiceHooksRequestPath

# Operation: get_service_hook
class RetrieveAServiceHookRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    hook_id: str = Field(default=..., description="The unique identifier (GUID) of the service hook to retrieve.")
class RetrieveAServiceHookRequest(StrictModel):
    """Retrieve a specific service hook configured for a project. Returns the hook's configuration and metadata."""
    path: RetrieveAServiceHookRequestPath

# Operation: update_service_hook
class UpdateAServiceHookRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    hook_id: str = Field(default=..., description="The unique identifier (GUID) of the service hook to update.")
class UpdateAServiceHookRequestBody(StrictModel):
    url: str = Field(default=..., description="The destination URL where webhook payloads will be sent. Must be a valid HTTP or HTTPS endpoint.")
    events: list[str] = Field(default=..., description="An array of event types to subscribe to. The hook will trigger for each specified event. Order is not significant.")
class UpdateAServiceHookRequest(StrictModel):
    """Update an existing service hook configuration for a project, including its webhook URL and subscribed event types."""
    path: UpdateAServiceHookRequestPath
    body: UpdateAServiceHookRequestBody

# Operation: remove_service_hook
class RemoveAServiceHookRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    hook_id: str = Field(default=..., description="The unique identifier (GUID) of the service hook to remove.")
class RemoveAServiceHookRequest(StrictModel):
    """Delete a service hook from a project. This removes the webhook integration and stops it from receiving events."""
    path: RemoveAServiceHookRequestPath

# Operation: get_event
class RetrieveAnEventForAProjectRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
    event_id: str = Field(default=..., description="The unique hexadecimal identifier of the event to retrieve, as reported by the client SDK.")
class RetrieveAnEventForAProjectRequest(StrictModel):
    """Retrieve detailed information about a specific event within a project, including error data, breadcrumbs, and other event metadata."""
    path: RetrieveAnEventForAProjectRequestPath

# Operation: list_project_issues
class ListAProjectSIssuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL slug.")
class ListAProjectSIssuesRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="A Sentry structured search query to filter results. If omitted, defaults to `is:unresolved`. Use an empty query to retrieve all issues regardless of status. Supports filtering by issue category (e.g., `issue.category:feedback` for user feedback items).")
    hashes: str | None = Field(default=None, description="A list of issue group hashes to retrieve, up to a maximum of 100. Cannot be used together with the query parameter. Hashes should be provided as comma-separated values.")
class ListAProjectSIssuesRequest(StrictModel):
    """Retrieve a list of issues (groups) for a specific project. By default, only unresolved issues are returned unless a custom query is provided. This endpoint is deprecated in favor of the Organization Issues endpoint."""
    path: ListAProjectSIssuesRequestPath
    query: ListAProjectSIssuesRequestQuery | None = None

# Operation: update_issues_bulk
class BulkMutateAListOfIssuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or URL slug.")
class BulkMutateAListOfIssuesRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Optionally filter mutations to only affect issues with a specific status: resolved, reprocessing, unresolved, or ignored.")
class BulkMutateAListOfIssuesRequestBodyStatusDetails(StrictModel):
    ignore_duration: int | None = Field(default=None, validation_alias="ignoreDuration", serialization_alias="ignoreDuration", description="Duration in milliseconds for which an ignored issue should remain ignored before auto-resolving.")
    ignore_count: int | None = Field(default=None, validation_alias="ignoreCount", serialization_alias="ignoreCount", description="Number of occurrences before an issue is automatically ignored.")
    ignore_window: int | None = Field(default=None, validation_alias="ignoreWindow", serialization_alias="ignoreWindow", description="Time window in milliseconds within which occurrences are counted for auto-ignore.")
    ignore_user_count: int | None = Field(default=None, validation_alias="ignoreUserCount", serialization_alias="ignoreUserCount", description="Number of unique users affected before an issue is automatically ignored.")
    ignore_user_window: int | None = Field(default=None, validation_alias="ignoreUserWindow", serialization_alias="ignoreUserWindow", description="Time window in milliseconds within which unique user counts are measured for auto-ignore.")
class BulkMutateAListOfIssuesRequestBody(StrictModel):
    status: str | None = Field(default=None, description="Set the new status for targeted issues. Accepts: resolved, resolvedInNextRelease, unresolved, or ignored.")
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Make the issue publicly visible (true) or restrict to organization members only (false).")
    merge: bool | None = Field(default=None, description="Merge multiple issues into one (true) or separate a merged issue (false).")
    assigned_to: str | None = Field(default=None, validation_alias="assignedTo", serialization_alias="assignedTo", description="Assign the issue to a user or team by their actor ID or username.")
    has_seen: bool | None = Field(default=None, validation_alias="hasSeen", serialization_alias="hasSeen", description="Mark whether the current user has viewed this issue (true) or not (false). Only applicable when invoked with user context.")
    is_bookmarked: bool | None = Field(default=None, validation_alias="isBookmarked", serialization_alias="isBookmarked", description="Add or remove the issue from the current user's bookmarks (true to bookmark, false to remove). Only applicable when invoked with user context.")
    status_details: BulkMutateAListOfIssuesRequestBodyStatusDetails | None = Field(default=None, validation_alias="statusDetails", serialization_alias="statusDetails")
class BulkMutateAListOfIssuesRequest(StrictModel):
    """Bulk update multiple issues by modifying their attributes such as status, assignment, visibility, and user-specific flags. Target issues using the `id` query parameter (repeatable), with optional filtering by current status."""
    path: BulkMutateAListOfIssuesRequestPath
    query: BulkMutateAListOfIssuesRequestQuery | None = None
    body: BulkMutateAListOfIssuesRequestBody | None = None

# Operation: delete_issues
class BulkRemoveAListOfIssuesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either its numeric ID or URL slug. Used to scope the project and issues being deleted.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either its numeric ID or URL slug. Combined with the organization to locate the issues for deletion.")
class BulkRemoveAListOfIssuesRequest(StrictModel):
    """Permanently remove one or more issues from a project. Specify issue IDs via query parameters; the operation succeeds even if some IDs are invalid or out of scope without modifying any data."""
    path: BulkRemoveAListOfIssuesRequestPath

# Operation: list_tag_values_for_issue
class ListATagSValuesForAnIssueRequestPath(StrictModel):
    issue_id: int = Field(default=..., description="The numeric identifier of the issue to query for tag values.")
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    key: str = Field(default=..., description="The tag key name to retrieve associated values for.")
class ListATagSValuesForAnIssueRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to filter tag values by. When specified, only values from the listed environments are returned.")
class ListATagSValuesForAnIssueRequest(StrictModel):
    """Retrieve all values associated with a specific tag key for an issue, useful for understanding what tags have been applied and their values. Returns up to 1000 values when paginated."""
    path: ListATagSValuesForAnIssueRequestPath
    query: ListATagSValuesForAnIssueRequestQuery | None = None

# Operation: list_issue_hashes
class ListAnIssueSHashesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    issue_id: str = Field(default=..., description="The numeric or string identifier of the issue whose hashes should be retrieved.")
class ListAnIssueSHashesRequestQuery(StrictModel):
    full: bool | None = Field(default=None, description="When enabled, the response includes the complete event payload with full details such as stack traces. Defaults to true.")
class ListAnIssueSHashesRequest(StrictModel):
    """Retrieve the list of hashes (generated checksums) associated with an issue, which are used to aggregate individual events into the issue."""
    path: ListAnIssueSHashesRequestPath
    query: ListAnIssueSHashesRequestQuery | None = None

# Operation: get_issue
class RetrieveAnIssueRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization that owns the issue.")
    issue_id: str = Field(default=..., description="The unique identifier of the issue to retrieve.")
class RetrieveAnIssueRequest(StrictModel):
    """Retrieve detailed information about a specific issue, including its core metadata (title, first/last seen timestamps), engagement metrics (comments, user reports), and summarized event data."""
    path: RetrieveAnIssueRequestPath

# Operation: update_issue
class UpdateAnIssueRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    issue_id: str = Field(default=..., description="The unique identifier of the issue to update.")
class UpdateAnIssueRequestBody(StrictModel):
    status: str | None = Field(default=None, description="The new status for the issue. Must be one of: resolved, resolvedInNextRelease, unresolved, or ignored.")
    assigned_to: str | None = Field(default=None, validation_alias="assignedTo", serialization_alias="assignedTo", description="The actor identifier (user ID, username, or team ID) to assign this issue to. Use null or omit to unassign.")
    has_seen: bool | None = Field(default=None, validation_alias="hasSeen", serialization_alias="hasSeen", description="Mark whether the current user has viewed this issue. Only applicable when the request is made in a user context.")
    is_bookmarked: bool | None = Field(default=None, validation_alias="isBookmarked", serialization_alias="isBookmarked", description="Mark whether the current user has bookmarked this issue. Only applicable when the request is made in a user context.")
    is_subscribed: bool | None = Field(default=None, validation_alias="isSubscribed", serialization_alias="isSubscribed", description="Subscribe or unsubscribe the current user from workflow notifications for this issue. Only applicable when the request is made in a user context.")
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Set the issue's visibility to public (true) or private (false).")
class UpdateAnIssueRequest(StrictModel):
    """Modify an issue's attributes such as status, assignment, visibility, and user-specific flags. Only the attributes provided in the request are updated; omitted fields remain unchanged."""
    path: UpdateAnIssueRequestPath
    body: UpdateAnIssueRequestBody | None = None

# Operation: delete_issue
class RemoveAnIssueRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    issue_id: str = Field(default=..., description="The unique identifier of the issue to be deleted.")
class RemoveAnIssueRequest(StrictModel):
    """Permanently removes an individual issue from an organization. This action cannot be undone."""
    path: RemoveAnIssueRequestPath

# Operation: list_organization_releases
class ListAnOrganizationSReleasesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
class ListAnOrganizationSReleasesRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Optional filter to match releases by version prefix using a 'starts with' comparison.")
class ListAnOrganizationSReleasesRequest(StrictModel):
    """Retrieve all releases for a given organization, with optional filtering by version prefix."""
    path: ListAnOrganizationSReleasesRequestPath
    query: ListAnOrganizationSReleasesRequestQuery | None = None

# Operation: create_release_for_organization
class CreateANewReleaseForAnOrganizationRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either a numeric ID or URL-friendly slug.")
class CreateANewReleaseForAnOrganizationRequestBody(StrictModel):
    version: str = Field(default=..., description="A unique version identifier for this release, such as a semantic version number, commit hash, or other build identifier.")
    projects: list[str] = Field(default=..., description="A list of project slugs associated with this release. Order is not significant. Each item should be a valid project slug string.")
    url: str | None = Field(default=None, description="An optional URL pointing to the release, such as a link to the source code repository or release notes page.")
    date_released: str | None = Field(default=None, validation_alias="dateReleased", serialization_alias="dateReleased", description="An optional timestamp indicating when the release was deployed to production. If omitted, the current time is used. Must be in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    refs: list[CreateANewReleaseForAnOrganizationBodyRefsItem] | None = Field(default=None, description="An optional array of commit references for repositories included in this release. Each reference should include `repository` and `commit` (the HEAD SHA), and may optionally include `previousCommit` (the previous HEAD SHA, recommended for first-time submissions). The `commit` field can specify a range using the format `previousCommit..commit`.")
class CreateANewReleaseForAnOrganizationRequest(StrictModel):
    """Create a new release for an organization to enable Sentry's error reporting, source map uploads, and debug features. Releases correlate first-seen events with the code version that introduced issues."""
    path: CreateANewReleaseForAnOrganizationRequestPath
    body: CreateANewReleaseForAnOrganizationRequestBody

# Operation: list_release_files
class ListAnOrganizationSReleaseFilesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug name of the organization.")
    version: str = Field(default=..., description="The version string that uniquely identifies the release. This should match the exact version identifier used when the release was created.")
class ListAnOrganizationSReleaseFilesRequest(StrictModel):
    """Retrieve all files associated with a specific release version within an organization. This returns the complete list of artifacts and source files included in that release."""
    path: ListAnOrganizationSReleaseFilesRequestPath

# Operation: upload_release_file
class UploadANewOrganizationReleaseFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    version: str = Field(default=..., description="The release version identifier to associate this file with.")
class UploadANewOrganizationReleaseFileRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The file content to upload, provided as binary multipart form data.", json_schema_extra={'format': 'binary'})
    name: str | None = Field(default=None, description="The absolute path or URI where this file will be referenced (e.g., a full web URI for JavaScript files). If omitted, the original filename is used.")
    dist: str | None = Field(default=None, description="The distribution name to associate with this file, useful for organizing files across different build variants or platforms.")
    header: str | None = Field(default=None, description="HTTP headers to attach to the file, specified as key:value pairs. This parameter can be supplied multiple times to add multiple headers (e.g., to define content type or caching directives).")
class UploadANewOrganizationReleaseFileRequest(StrictModel):
    """Upload a new file to a release. Files must be submitted using multipart/form-data encoding and requests should target region-specific domains (e.g., us.sentry.io or de.sentry.io)."""
    path: UploadANewOrganizationReleaseFileRequestPath
    body: UploadANewOrganizationReleaseFileRequestBody

# Operation: list_release_files_for_project
class ListAProjectSReleaseFilesRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
    version: str = Field(default=..., description="The release version identifier, typically a semantic version string or tag that uniquely identifies the release.")
class ListAProjectSReleaseFilesRequest(StrictModel):
    """Retrieve all files associated with a specific release version within a project. This returns the complete list of artifacts and source files included in that release."""
    path: ListAProjectSReleaseFilesRequestPath

# Operation: upload_release_file_project
class UploadANewProjectReleaseFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug.")
    version: str = Field(default=..., description="The release version identifier to associate this file with.")
class UploadANewProjectReleaseFileRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The file content to upload as binary data via multipart form encoding.", json_schema_extra={'format': 'binary'})
    name: str | None = Field(default=None, description="Optional absolute path or URI where this file will be referenced (e.g., full web URI for JavaScript files).")
    dist: str | None = Field(default=None, description="Optional distribution name to associate with this file artifact.")
    header: str | None = Field(default=None, description="Optional HTTP headers to attach to the file, specified as key:value pairs. This parameter can be supplied multiple times for multiple headers (e.g., to define content type).")
class UploadANewProjectReleaseFileRequest(StrictModel):
    """Upload a new file artifact for a specific release version. Files must be submitted using multipart/form-data encoding and requests should target region-specific domains (e.g., us.sentry.io or de.sentry.io)."""
    path: UploadANewProjectReleaseFileRequestPath
    body: UploadANewProjectReleaseFileRequestBody

# Operation: get_release_file
class RetrieveAnOrganizationReleaseSFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug name.")
    version: str = Field(default=..., description="The release version identifier, typically a semantic version string or tag name.")
    file_id: str = Field(default=..., description="The unique identifier of the file within the release.")
class RetrieveAnOrganizationReleaseSFileRequestQuery(StrictModel):
    download: bool | None = Field(default=None, description="Set to true to retrieve the raw file contents as a binary payload, or false (default) to receive file metadata as JSON.")
class RetrieveAnOrganizationReleaseSFileRequest(StrictModel):
    """Retrieve a specific file from a release, either as file metadata or raw file contents. Use the download parameter to control whether you receive JSON metadata or the actual file data."""
    path: RetrieveAnOrganizationReleaseSFileRequestPath
    query: RetrieveAnOrganizationReleaseSFileRequestQuery | None = None

# Operation: update_organization_release_file
class UpdateAnOrganizationReleaseFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    version: str = Field(default=..., description="The version string that identifies the release.")
    file_id: str = Field(default=..., description="The unique identifier of the file to update.")
class UpdateAnOrganizationReleaseFileRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new full file path or name for the release file.")
    dist: str | None = Field(default=None, description="The new distribution name to associate with the file.")
class UpdateAnOrganizationReleaseFileRequest(StrictModel):
    """Update metadata for a file associated with an organization release, such as its name or distribution identifier."""
    path: UpdateAnOrganizationReleaseFileRequestPath
    body: UpdateAnOrganizationReleaseFileRequestBody | None = None

# Operation: delete_release_file
class DeleteAnOrganizationReleaseSFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization.")
    version: str = Field(default=..., description="The version string that uniquely identifies the release within the organization.")
    file_id: str = Field(default=..., description="The unique identifier of the file to be deleted from the release.")
class DeleteAnOrganizationReleaseSFileRequest(StrictModel):
    """Permanently delete a file associated with a specific release in an organization. This action cannot be undone."""
    path: DeleteAnOrganizationReleaseSFileRequestPath

# Operation: get_release_file_project
class RetrieveAProjectReleaseSFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL slug of the project within the organization.")
    version: str = Field(default=..., description="The version string that identifies the release (e.g., semantic version or commit hash).")
    file_id: str = Field(default=..., description="The unique identifier of the file within the release.")
class RetrieveAProjectReleaseSFileRequestQuery(StrictModel):
    download: bool | None = Field(default=None, description="When true, returns the raw file contents as the response payload; when false or omitted, returns file metadata as JSON.")
class RetrieveAProjectReleaseSFileRequest(StrictModel):
    """Retrieve a file associated with a specific release, either as file metadata or raw file contents depending on the download parameter."""
    path: RetrieveAProjectReleaseSFileRequestPath
    query: RetrieveAProjectReleaseSFileRequestQuery | None = None

# Operation: update_release_file
class UpdateAProjectReleaseFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either as a numeric ID or URL-friendly slug.")
    version: str = Field(default=..., description="The release version identifier to target.")
    file_id: str = Field(default=..., description="The unique identifier of the file to update.")
class UpdateAProjectReleaseFileRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new full file path or name for the release file.")
    dist: str | None = Field(default=None, description="The new distribution name to associate with the file.")
class UpdateAProjectReleaseFileRequest(StrictModel):
    """Update metadata for a specific file within a project release, such as its name or distribution identifier."""
    path: UpdateAProjectReleaseFileRequestPath
    body: UpdateAProjectReleaseFileRequestBody | None = None

# Operation: delete_release_file_for_project
class DeleteAProjectReleaseSFileRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, either the numeric ID or the URL-friendly slug.")
    version: str = Field(default=..., description="The release version string used to identify the specific release.")
    file_id: str = Field(default=..., description="The unique identifier of the file to be deleted from the release.")
class DeleteAProjectReleaseSFileRequest(StrictModel):
    """Permanently delete a file associated with a specific release. This action cannot be undone."""
    path: DeleteAProjectReleaseSFileRequestPath

# Operation: list_release_commits
class ListAnOrganizationReleaseSCommitsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    version: str = Field(default=..., description="The version string that uniquely identifies the release within the organization.")
class ListAnOrganizationReleaseSCommitsRequest(StrictModel):
    """Retrieve all commits associated with a specific release in an organization. This lists the commits that were included when the release version was created."""
    path: ListAnOrganizationReleaseSCommitsRequestPath

# Operation: list_release_commits_for_project
class ListAProjectReleaseSCommitsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")
    project_id_or_slug: str = Field(default=..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization.")
    version: str = Field(default=..., description="The release version identifier, typically a semantic version string or tag name that uniquely identifies the release.")
class ListAProjectReleaseSCommitsRequest(StrictModel):
    """Retrieve all commits associated with a specific project release. This lists the commits that were included in the release version."""
    path: ListAProjectReleaseSCommitsRequestPath

# Operation: list_files_changed_in_release_commits
class RetrieveFilesChangedInAReleaseSCommitsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or the organization's URL slug. Use the slug for human-readable requests or the ID for programmatic lookups.")
    version: str = Field(default=..., description="The release version identifier. This should match the version tag or semantic version string used to identify the release in your system.")
class RetrieveFilesChangedInAReleaseSCommitsRequest(StrictModel):
    """Retrieve all files that were modified across the commits included in a specific release. This helps identify what code changes were shipped in a particular version."""
    path: RetrieveFilesChangedInAReleaseSCommitsRequestPath

# Operation: list_organization_sentry_app_installations
class ListAnOrganizationSIntegrationPlatformInstallationsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, which can be either the numeric ID or the organization's URL slug (short name). Use the slug for human-readable references or the ID for programmatic lookups.")
class ListAnOrganizationSIntegrationPlatformInstallationsRequest(StrictModel):
    """Retrieve all integration platform (Sentry App) installations configured for a specific organization. This returns the list of third-party integrations that have been installed and are active within the organization."""
    path: ListAnOrganizationSIntegrationPlatformInstallationsRequestPath

# Operation: create_or_update_external_issue
class CreateOrUpdateAnExternalIssueRequestPath(StrictModel):
    uuid_: str = Field(default=..., validation_alias="uuid", serialization_alias="uuid", description="The unique identifier of the integration platform installation that will handle the external issue creation or update.")
class CreateOrUpdateAnExternalIssueRequestBody(StrictModel):
    issue_id: int = Field(default=..., validation_alias="issueId", serialization_alias="issueId", description="The numeric ID of the Sentry issue to link with the external issue.")
    web_url: str = Field(default=..., validation_alias="webUrl", serialization_alias="webUrl", description="The full URL of the external issue in the integrated service (e.g., the direct link to the issue in the external tracker).")
    project: str = Field(default=..., description="The project identifier or key in the external service where the issue exists or will be created.")
    identifier: str = Field(default=..., description="A unique identifier for the external issue within the external service (e.g., issue number, ticket ID, or key). This is used to prevent duplicate creations and to identify the issue for updates.")
class CreateOrUpdateAnExternalIssueRequest(StrictModel):
    """Create or update an external issue linked to a Sentry issue through an integration platform installation. This establishes a bidirectional link between a Sentry issue and an external service's issue tracker."""
    path: CreateOrUpdateAnExternalIssueRequestPath
    body: CreateOrUpdateAnExternalIssueRequestBody

# Operation: delete_external_issue
class DeleteAnExternalIssueRequestPath(StrictModel):
    uuid_: str = Field(default=..., validation_alias="uuid", serialization_alias="uuid", description="The unique identifier of the Sentry app installation (integration platform integration) that owns the external issue.")
    external_issue_id: str = Field(default=..., description="The unique identifier of the external issue to delete from the integration platform.")
class DeleteAnExternalIssueRequest(StrictModel):
    """Delete an external issue linked to a Sentry app installation. This removes the association between the external issue and the integration platform."""
    path: DeleteAnExternalIssueRequestPath

# Operation: enable_spike_protection_for_projects
class EnableSpikeProtectionRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This determines which organization's projects will have Spike Protection enabled.")
class EnableSpikeProtectionRequestBody(StrictModel):
    projects: list[str] = Field(default=..., description="Array of project slugs to enable Spike Protection for. Use the special value `$all` to enable Spike Protection across all projects in the organization, or provide specific project slugs as an array of strings.")
class EnableSpikeProtectionRequest(StrictModel):
    """Enables Spike Protection feature for specified projects within an organization. Spike Protection helps manage error rate spikes by automatically adjusting error sampling thresholds."""
    path: EnableSpikeProtectionRequestPath
    body: EnableSpikeProtectionRequestBody

# Operation: disable_spike_protection_for_projects
class DisableSpikeProtectionRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization containing the projects.")
class DisableSpikeProtectionRequestBody(StrictModel):
    projects: list[str] = Field(default=..., description="Array of project slugs to disable Spike Protection for. Use the special value `$all` to disable Spike Protection for all projects in the organization at once.")
class DisableSpikeProtectionRequest(StrictModel):
    """Disables Spike Protection for specified projects within an organization. Use the special value `$all` to disable Spike Protection across all projects in the organization."""
    path: DisableSpikeProtectionRequestPath
    body: DisableSpikeProtectionRequestBody

# Operation: get_issue_autofix_state
class RetrieveSeerIssueFixStateRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug. Required to scope the issue within the correct organization.")
    issue_id: int = Field(default=..., description="The numeric identifier of the issue. Required to retrieve the specific autofix state for that issue.")
class RetrieveSeerIssueFixStateRequest(StrictModel):
    """Retrieve the current state and progress of an automated fix process for a specific issue, including status, completed steps, root cause analysis, proposed solution, and generated code changes. Note: This endpoint is experimental and the response structure may change."""
    path: RetrieveSeerIssueFixStateRequestPath

# Operation: trigger_issue_autofix
class StartSeerIssueFixRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug of the organization.")
    issue_id: int = Field(default=..., description="The numeric ID of the issue to analyze and fix.")
class StartSeerIssueFixRequestBody(StrictModel):
    event_id: str | None = Field(default=None, description="Optional event ID to analyze. If omitted, the system will use the recommended event for the issue.")
    instruction: str | None = Field(default=None, description="Optional custom instruction to guide the autofix analysis and solution generation process.")
    pr_to_comment_on_url: str | None = Field(default=None, description="Optional URL of a pull request where the autofix should post comments with findings and recommendations.", json_schema_extra={'format': 'uri'})
    stopping_point: Literal["root_cause", "solution", "code_changes", "open_pr"] | None = Field(default=None, description="Optional stopping point for the autofix process. Defaults to root cause analysis if not specified. Valid stages are: root_cause (stop after identifying the cause), solution (stop after proposing a fix), code_changes (stop after generating code), or open_pr (complete the process by creating a pull request).")
class StartSeerIssueFixRequest(StrictModel):
    """Trigger an automated issue fix analysis that identifies root causes, proposes solutions, generates code changes, and optionally creates a pull request. The process runs asynchronously and can be monitored via the GET endpoint."""
    path: StartSeerIssueFixRequestPath
    body: StartSeerIssueFixRequestBody | None = None

# Operation: list_issue_events
class ListAnIssueSEventsRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug.")
    issue_id: int = Field(default=..., description="The numeric ID of the issue to retrieve events for.")
class ListAnIssueSEventsRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Filter events to only those from specified environments. Provide as an array of environment names.")
    full: bool | None = Field(default=None, description="Set to true to include complete event details such as stack traces and breadcrumbs. Defaults to false for lighter payloads.")
    sample: bool | None = Field(default=None, description="Set to true to return events in pseudo-random but deterministic order, ensuring consistent results across identical queries.")
    query: str | None = Field(default=None, description="Filter events using Sentry's search syntax. Supports queries like `transaction:foo AND release:abc`. Refer to Sentry's search documentation for available event properties and operators.")
class ListAnIssueSEventsRequest(StrictModel):
    """Retrieve a list of error events associated with a specific issue. Optionally filter by environment, search criteria, or request full event details including stack traces."""
    path: ListAnIssueSEventsRequestPath
    query: ListAnIssueSEventsRequestQuery | None = None

# Operation: get_issue_event
class RetrieveAnIssueEventRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL-friendly slug (e.g., 'my-org'). This determines which organization's resources are accessed.")
    issue_id: int = Field(default=..., description="The numeric ID of the issue containing the event you want to retrieve.")
    event_id: Literal["latest", "oldest", "recommended"] = Field(default=..., description="The event identifier to retrieve. Accepts a specific event ID or one of three special values: 'latest' for the most recent event, 'oldest' for the first event, or 'recommended' for a system-suggested event.")
class RetrieveAnIssueEventRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional filter to limit results to events from specific environments. Provide as a list of environment names; events matching any of the specified environments will be included.")
class RetrieveAnIssueEventRequest(StrictModel):
    """Retrieves detailed information about a specific event associated with an issue, such as comments, status changes, or assignments. You can fetch a particular event by ID or retrieve special event references like the latest, oldest, or recommended event."""
    path: RetrieveAnIssueEventRequestPath
    query: RetrieveAnIssueEventRequestQuery | None = None

# Operation: list_external_issues_for_issue
class RetrieveCustomIntegrationIssueLinksForTheGivenSentryIssueRequestPath(StrictModel):
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either the numeric ID or the URL slug. Use the slug for human-readable references or the ID for programmatic lookups.")
    issue_id: int = Field(default=..., description="The numeric ID of the Sentry issue. Must be a positive integer representing a valid issue within the organization.")
class RetrieveCustomIntegrationIssueLinksForTheGivenSentryIssueRequest(StrictModel):
    """Retrieve all custom integration issue links (external issues) associated with a specific Sentry issue. This shows connections between the Sentry issue and external tracking systems."""
    path: RetrieveCustomIntegrationIssueLinksForTheGivenSentryIssueRequestPath

# Operation: get_tag_values_for_issue
class RetrieveTagDetailsRequestPath(StrictModel):
    issue_id: int = Field(default=..., description="The numeric identifier of the issue to query for tag values.")
    organization_id_or_slug: str = Field(default=..., description="The organization identifier, either as a numeric ID or URL-friendly slug.")
    key: str = Field(default=..., description="The tag key name to retrieve associated values for.")
class RetrieveTagDetailsRequestQuery(StrictModel):
    environment: list[str] | None = Field(default=None, description="Optional list of environment names to filter tag values by. When specified, only values from the listed environments are returned.")
class RetrieveTagDetailsRequest(StrictModel):
    """Retrieve all values associated with a specific tag key for an issue, with optional filtering by environment. Results are paginated and return at most 1000 values."""
    path: RetrieveTagDetailsRequestPath
    query: RetrieveTagDetailsRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class BulkMutateAnOrganizationSIssuesBodyStatusDetailsInCommit(PermissiveModel):
    """The commit data that the issue should use for resolution."""
    commit: str = Field(..., description="The SHA of the resolving commit.")
    repository: str = Field(..., description="The name of the repository (as it appears in Sentry).")

class BulkMutateAnOrganizationSIssuesBodyStatusDetails(PermissiveModel):
    """Additional details about the resolution. Status detail updates that include release data are only allowed for issues within a single project."""
    in_next_release: bool = Field(..., validation_alias="inNextRelease", serialization_alias="inNextRelease", description="If true, marks the issue as resolved in the next release.")
    in_release: str = Field(..., validation_alias="inRelease", serialization_alias="inRelease", description="The version of the release that the issue should be resolved in.If set to `latest`, the latest release will be used.")
    in_commit: BulkMutateAnOrganizationSIssuesBodyStatusDetailsInCommit | None = Field(None, validation_alias="inCommit", serialization_alias="inCommit", description="The commit data that the issue should use for resolution.")
    ignore_duration: int = Field(..., validation_alias="ignoreDuration", serialization_alias="ignoreDuration", description="Ignore the issue until for this many minutes.")
    ignore_count: int = Field(..., validation_alias="ignoreCount", serialization_alias="ignoreCount", description="Ignore the issue until it has occurred this many times in `ignoreWindow` minutes.")
    ignore_window: int = Field(..., validation_alias="ignoreWindow", serialization_alias="ignoreWindow", description="Ignore the issue until it has occurred `ignoreCount` times in this many minutes. (Max: 1 week)", le=10080)
    ignore_user_count: int = Field(..., validation_alias="ignoreUserCount", serialization_alias="ignoreUserCount", description="Ignore the issue until it has affected this many users in `ignoreUserWindow` minutes.")
    ignore_user_window: int = Field(..., validation_alias="ignoreUserWindow", serialization_alias="ignoreUserWindow", description="Ignore the issue until it has affected `ignoreUserCount` users in this many minutes. (Max: 1 week)", le=10080)

class CreateAMonitorBodyConfig(PermissiveModel):
    """The configuration for the monitor."""
    schedule_type: Literal["crontab", "interval"] | None = Field(None, description="Currently supports \"crontab\" or \"interval\"\n\n* `crontab`\n* `interval`")
    schedule: Any = Field(..., description="Varies depending on the schedule_type. Is either a crontab string, or a 2 element tuple for intervals (e.g. [1, 'day'])")
    checkin_margin: int | None = Field(None, description="How long (in minutes) after the expected checkin time will we wait until we consider the checkin to have been missed.", ge=1, le=40320)
    max_runtime: int | None = Field(None, description="How long (in minutes) is the checkin allowed to run for in CheckInStatus.IN_PROGRESS before it is considered failed.", ge=1, le=40320)
    timezone_: Literal["Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara", "Africa/Asmera", "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre", "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome", "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Timbuktu", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak", "America/Anchorage", "America/Anguilla", "America/Antigua", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Argentina/Catamarca", "America/Argentina/ComodRivadavia", "America/Argentina/Cordoba", "America/Argentina/Jujuy", "America/Argentina/La_Rioja", "America/Argentina/Mendoza", "America/Argentina/Rio_Gallegos", "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis", "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Aruba", "America/Asuncion", "America/Atikokan", "America/Atka", "America/Bahia", "America/Bahia_Banderas", "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise", "America/Buenos_Aires", "America/Cambridge_Bay", "America/Campo_Grande", "America/Cancun", "America/Caracas", "America/Catamarca", "America/Cayenne", "America/Cayman", "America/Chicago", "America/Chihuahua", "America/Ciudad_Juarez", "America/Coral_Harbour", "America/Cordoba", "America/Costa_Rica", "America/Coyhaique", "America/Creston", "America/Cuiaba", "America/Curacao", "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek", "America/Denver", "America/Detroit", "America/Dominica", "America/Edmonton", "America/Eirunepe", "America/El_Salvador", "America/Ensenada", "America/Fort_Nelson", "America/Fort_Wayne", "America/Fortaleza", "America/Glace_Bay", "America/Godthab", "America/Goose_Bay", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala", "America/Guayaquil", "America/Guyana", "America/Halifax", "America/Havana", "America/Hermosillo", "America/Indiana/Indianapolis", "America/Indiana/Knox", "America/Indiana/Marengo", "America/Indiana/Petersburg", "America/Indiana/Tell_City", "America/Indiana/Vevay", "America/Indiana/Vincennes", "America/Indiana/Winamac", "America/Indianapolis", "America/Inuvik", "America/Iqaluit", "America/Jamaica", "America/Jujuy", "America/Juneau", "America/Kentucky/Louisville", "America/Kentucky/Monticello", "America/Knox_IN", "America/Kralendijk", "America/La_Paz", "America/Lima", "America/Los_Angeles", "America/Louisville", "America/Lower_Princes", "America/Maceio", "America/Managua", "America/Manaus", "America/Marigot", "America/Martinique", "America/Matamoros", "America/Mazatlan", "America/Mendoza", "America/Menominee", "America/Merida", "America/Metlakatla", "America/Mexico_City", "America/Miquelon", "America/Moncton", "America/Monterrey", "America/Montevideo", "America/Montreal", "America/Montserrat", "America/Nassau", "America/New_York", "America/Nipigon", "America/Nome", "America/Noronha", "America/North_Dakota/Beulah", "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Nuuk", "America/Ojinaga", "America/Panama", "America/Pangnirtung", "America/Paramaribo", "America/Phoenix", "America/Port-au-Prince", "America/Port_of_Spain", "America/Porto_Acre", "America/Porto_Velho", "America/Puerto_Rico", "America/Punta_Arenas", "America/Rainy_River", "America/Rankin_Inlet", "America/Recife", "America/Regina", "America/Resolute", "America/Rio_Branco", "America/Rosario", "America/Santa_Isabel", "America/Santarem", "America/Santiago", "America/Santo_Domingo", "America/Sao_Paulo", "America/Scoresbysund", "America/Shiprock", "America/Sitka", "America/St_Barthelemy", "America/St_Johns", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa", "America/Thule", "America/Thunder_Bay", "America/Tijuana", "America/Toronto", "America/Tortola", "America/Vancouver", "America/Virgin", "America/Whitehorse", "America/Winnipeg", "America/Yakutat", "America/Yellowknife", "Antarctica/Casey", "Antarctica/Davis", "Antarctica/DumontDUrville", "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo", "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/South_Pole", "Antarctica/Syowa", "Antarctica/Troll", "Antarctica/Vostok", "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman", "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Ashkhabad", "Asia/Atyrau", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Barnaul", "Asia/Beirut", "Asia/Bishkek", "Asia/Brunei", "Asia/Calcutta", "Asia/Chita", "Asia/Choibalsan", "Asia/Chongqing", "Asia/Chungking", "Asia/Colombo", "Asia/Dacca", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Famagusta", "Asia/Gaza", "Asia/Harbin", "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd", "Asia/Irkutsk", "Asia/Istanbul", "Asia/Jakarta", "Asia/Jayapura", "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi", "Asia/Kashgar", "Asia/Kathmandu", "Asia/Katmandu", "Asia/Khandyga", "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Kuwait", "Asia/Macao", "Asia/Macau", "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk", "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang", "Asia/Qatar", "Asia/Qostanay", "Asia/Qyzylorda", "Asia/Rangoon", "Asia/Riyadh", "Asia/Saigon", "Asia/Sakhalin", "Asia/Samarkand", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Srednekolymsk", "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran", "Asia/Tel_Aviv", "Asia/Thimbu", "Asia/Thimphu", "Asia/Tokyo", "Asia/Tomsk", "Asia/Ujung_Pandang", "Asia/Ulaanbaatar", "Asia/Ulan_Bator", "Asia/Urumqi", "Asia/Ust-Nera", "Asia/Vientiane", "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yangon", "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores", "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde", "Atlantic/Faeroe", "Atlantic/Faroe", "Atlantic/Jan_Mayen", "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia", "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/ACT", "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill", "Australia/Canberra", "Australia/Currie", "Australia/Darwin", "Australia/Eucla", "Australia/Hobart", "Australia/LHI", "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne", "Australia/NSW", "Australia/North", "Australia/Perth", "Australia/Queensland", "Australia/South", "Australia/Sydney", "Australia/Tasmania", "Australia/Victoria", "Australia/West", "Australia/Yancowinna", "Brazil/Acre", "Brazil/DeNoronha", "Brazil/East", "Brazil/West", "CET", "CST6CDT", "Canada/Atlantic", "Canada/Central", "Canada/Eastern", "Canada/Mountain", "Canada/Newfoundland", "Canada/Pacific", "Canada/Saskatchewan", "Canada/Yukon", "Chile/Continental", "Chile/EasterIsland", "Cuba", "EET", "EST", "EST5EDT", "Egypt", "Eire", "Etc/GMT", "Etc/GMT+0", "Etc/GMT+1", "Etc/GMT+10", "Etc/GMT+11", "Etc/GMT+12", "Etc/GMT+2", "Etc/GMT+3", "Etc/GMT+4", "Etc/GMT+5", "Etc/GMT+6", "Etc/GMT+7", "Etc/GMT+8", "Etc/GMT+9", "Etc/GMT-0", "Etc/GMT-1", "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12", "Etc/GMT-13", "Etc/GMT-14", "Etc/GMT-2", "Etc/GMT-3", "Etc/GMT-4", "Etc/GMT-5", "Etc/GMT-6", "Etc/GMT-7", "Etc/GMT-8", "Etc/GMT-9", "Etc/GMT0", "Etc/Greenwich", "Etc/UCT", "Etc/UTC", "Etc/Universal", "Etc/Zulu", "Europe/Amsterdam", "Europe/Andorra", "Europe/Astrakhan", "Europe/Athens", "Europe/Belfast", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest", "Europe/Budapest", "Europe/Busingen", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Kirov", "Europe/Kyiv", "Europe/Lisbon", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco", "Europe/Moscow", "Europe/Nicosia", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo", "Europe/Saratov", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Tiraspol", "Europe/Ulyanovsk", "Europe/Uzhgorod", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius", "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb", "Europe/Zaporozhye", "Europe/Zurich", "GB", "GB-Eire", "GMT", "GMT+0", "GMT-0", "GMT0", "Greenwich", "HST", "Hongkong", "Iceland", "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte", "Indian/Reunion", "Iran", "Israel", "Jamaica", "Japan", "Kwajalein", "Libya", "MET", "MST", "MST7MDT", "Mexico/BajaNorte", "Mexico/BajaSur", "Mexico/General", "NZ", "NZ-CHAT", "Navajo", "PRC", "PST8PDT", "Pacific/Apia", "Pacific/Auckland", "Pacific/Bougainville", "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier", "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Kanton", "Pacific/Kiritimati", "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei", "Pacific/Ponape", "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Samoa", "Pacific/Tahiti", "Pacific/Tarawa", "Pacific/Tongatapu", "Pacific/Truk", "Pacific/Wake", "Pacific/Wallis", "Pacific/Yap", "Poland", "Portugal", "ROC", "ROK", "Singapore", "Turkey", "UCT", "US/Alaska", "US/Aleutian", "US/Arizona", "US/Central", "US/East-Indiana", "US/Eastern", "US/Hawaii", "US/Indiana-Starke", "US/Michigan", "US/Mountain", "US/Pacific", "US/Samoa", "UTC", "Universal", "W-SU", "WET", "Zulu", "localtime", ""] | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="tz database style timezone string\n\n* `Africa/Abidjan`\n* `Africa/Accra`\n* `Africa/Addis_Ababa`\n* `Africa/Algiers`\n* `Africa/Asmara`\n* `Africa/Asmera`\n* `Africa/Bamako`\n* `Africa/Bangui`\n* `Africa/Banjul`\n* `Africa/Bissau`\n* `Africa/Blantyre`\n* `Africa/Brazzaville`\n* `Africa/Bujumbura`\n* `Africa/Cairo`\n* `Africa/Casablanca`\n* `Africa/Ceuta`\n* `Africa/Conakry`\n* `Africa/Dakar`\n* `Africa/Dar_es_Salaam`\n* `Africa/Djibouti`\n* `Africa/Douala`\n* `Africa/El_Aaiun`\n* `Africa/Freetown`\n* `Africa/Gaborone`\n* `Africa/Harare`\n* `Africa/Johannesburg`\n* `Africa/Juba`\n* `Africa/Kampala`\n* `Africa/Khartoum`\n* `Africa/Kigali`\n* `Africa/Kinshasa`\n* `Africa/Lagos`\n* `Africa/Libreville`\n* `Africa/Lome`\n* `Africa/Luanda`\n* `Africa/Lubumbashi`\n* `Africa/Lusaka`\n* `Africa/Malabo`\n* `Africa/Maputo`\n* `Africa/Maseru`\n* `Africa/Mbabane`\n* `Africa/Mogadishu`\n* `Africa/Monrovia`\n* `Africa/Nairobi`\n* `Africa/Ndjamena`\n* `Africa/Niamey`\n* `Africa/Nouakchott`\n* `Africa/Ouagadougou`\n* `Afri...")
    failure_issue_threshold: int | None = Field(None, description="How many consecutive missed or failed check-ins in a row before creating a new issue.", ge=1, le=720)
    recovery_threshold: int | None = Field(None, description="How many successful check-ins in a row before resolving an issue.", ge=1, le=720)

class CreateAMonitorForAProjectBodyConditionGroup(PermissiveModel):
    """
            Issue detection configuration for when to create an issue and at what priority level.


            - `logicType`: `any`
            - `type`: Any of `gt` (greater than), `lte` (less than or equal), or `anomaly_detection` (dynamic)
            - `comparison`: Any positive integer. This is threshold that must be crossed for the monitor to create an issue, e.g. "Create a metric issue when there are more than 5 unresolved error events".
                - If creating a **dynamic** monitor, see the options below.
                    - `seasonality`: `auto`
                    - `sensitivity`: Level of responsiveness. Options are one of `low`, `medium`, or `high`
                    - `thresholdType`: If you want to be alerted to anomalies that are moving above, below, or in both directions in relation to your threshold.
                        - `0`: Above
                        - `1`: Below
                        - `2`: Above and below

            - `conditionResult`: The issue state change when the threshold is crossed.
                - `75`: High priority
                - `50`: Low priority
                - `0`: Resolved


            **Threshold and Change Monitor**
            ```json
                "logicType": "any",
                "conditions": [
                    {
                        "type": "gt",
                        "comparison": 10,
                        "conditionResult": 75
                    },
                    {
                        "type": "lte",
                        "comparison": 10,
                        "conditionResult": 0
                    }
                ],
                "actions": []
            ```

            **Threshold Monitor with Medium Priority**
            ```json
                "logicType": "any",
                "conditions": [
                    {
                        type: "gt",
                        comparison: 5,
                        conditionResult: 75
                    },
                    {
                        type: "gt",
                        comparison: 2,
                        conditionResult: 50
                    },
                    {
                        type: "lte",
                        comparison: 2,
                        conditionResult: 0
                    }
                ],
                "actions": []
            ```

            **Dynamic Monitor**
            ```json
                "logicType": "any",
                "conditions": [
                    {
                        "type": "anomaly_detection",
                        "comparison": {
                            "seasonality": "auto",
                            "sensitivity": "medium",
                            "thresholdType": 2
                        },
                        "conditionResult": 75
                    }
                ],
                "actions": []
            ```
"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    logic_type: Literal["any", "any-short", "all", "none"] = Field(..., description="* `any`\n* `any-short`\n* `all`\n* `none`")
    conditions: list[Any] | None = None

class CreateANewDashboardForAnOrganizationBodyPermissions(PermissiveModel):
    """Permissions that restrict users from editing dashboards"""
    is_editable_by_everyone: bool = Field(..., description="Whether the dashboard is editable by everyone.")
    teams_with_edit_access: list[int] | None = Field(None, description="List of team IDs that have edit access to a dashboard.")

class CreateANewDashboardForAnOrganizationBodyWidgetsItemLayout(PermissiveModel):
    x: int = Field(..., description="Column position (0-indexed).", ge=0, le=5)
    y: int = Field(..., description="Row position (0-indexed).", ge=0)
    w: int = Field(..., description="Width in grid columns (1-6).", ge=1, le=6)
    h: int = Field(..., description="Height in grid rows.", ge=1)
    min_h: int = Field(..., description="Minimum height in grid rows.", ge=1)

class CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItemLinkedDashboardsItem(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    field: str
    dashboard_id: str

class CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItemOnDemandExtraction(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    extraction_state: str | None = None
    enabled: bool | None = None

class CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItem(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    fields: list[str] | None = None
    aggregates: list[str] | None = None
    columns: list[str] | None = None
    field_aliases: list[str] | None = None
    name: str | None = None
    conditions: str | None = None
    orderby: str | None = None
    is_hidden: bool | None = None
    on_demand_extraction: CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItemOnDemandExtraction | None = Field(None, description="Allows parameters to be defined in snake case, but passed as camel case.\n\nErrors are output in camel case.")
    on_demand_extraction_disabled: bool | None = None
    selected_aggregate: int | None = None
    linked_dashboards: list[CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItemLinkedDashboardsItem] | None = None

class CreateANewDashboardForAnOrganizationBodyWidgetsItem(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    thresholds: dict[str, Any] | None = None
    display_type: Literal["line", "area", "stacked_area", "bar", "table", "big_number", "top_n", "details", "categorical_bar", "wheel", "rage_and_dead_clicks", "server_tree", "text", "agents_traces_table"] | None = Field(None, description="* `line`\n* `area`\n* `stacked_area`\n* `bar`\n* `table`\n* `big_number`\n* `top_n`\n* `details`\n* `categorical_bar`\n* `wheel`\n* `rage_and_dead_clicks`\n* `server_tree`\n* `text`\n* `agents_traces_table`")
    interval: str | None = Field(None, max_length=10)
    queries: list[CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItem] | None = None
    widget_type: Literal["discover", "issue", "metrics", "error-events", "transaction-like", "spans", "logs", "tracemetrics", "preprod-app-size"] | None = Field(None, description="* `discover`\n* `issue`\n* `metrics`\n* `error-events`\n* `transaction-like`\n* `spans`\n* `logs`\n* `tracemetrics`\n* `preprod-app-size`")
    limit: int | None = Field(None, ge=1)
    layout: CreateANewDashboardForAnOrganizationBodyWidgetsItemLayout | None = None
    axis_range: Literal["auto", "dataMin"] | None = Field(None, description="* `auto`\n* `dataMin`")
    legend_type: Literal["default", "breakdown"] | None = Field(None, description="* `default`\n* `breakdown`")

class CreateANewReleaseForAnOrganizationBodyRefsItem(PermissiveModel):
    repository: str | None = Field(None, description="The full name of the repository the commit belongs to.")
    commit: str | None = Field(None, description="The current release's commit.")
    previous_commit: str | None = Field(None, validation_alias="previousCommit", serialization_alias="previousCommit", description="The previous release's commit.")

class CreateAnAlertForAnOrganizationBodyTriggers(PermissiveModel):
    """The conditions on which the alert will trigger. See available options below.
        ```json
            "triggers": {
                "organizationId": "1",
                "logicType": "any-short",
                "conditions": [
                    {
                        "type": "first_seen_event",
                        "comparison": true,
                        "conditionResult": true
                    },
                    {
                        "type": "issue_resolved_trigger",
                        "comparison": true,
                        "conditionResult": true
                    },
                    {
                        "type": "reappeared_event",
                        "comparison": true,
                        "conditionResult": true
                    },
                    {
                        "type": "regression_event",
                        "comparison": true,
                        "conditionResult": true
                    }
                ],
                "actions": []
            }
        ```
"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    logic_type: Literal["any", "any-short", "all", "none"] = Field(..., description="* `any`\n* `any-short`\n* `all`\n* `none`")
    conditions: list[Any] | None = None

class EditAnOrganizationSCustomDashboardBodyPermissions(PermissiveModel):
    """Permissions that restrict users from editing dashboards"""
    is_editable_by_everyone: bool = Field(..., description="Whether the dashboard is editable by everyone.")
    teams_with_edit_access: list[int] | None = Field(None, description="List of team IDs that have edit access to a dashboard.")

class EditAnOrganizationSCustomDashboardBodyWidgetsItemLayout(PermissiveModel):
    x: int = Field(..., description="Column position (0-indexed).", ge=0, le=5)
    y: int = Field(..., description="Row position (0-indexed).", ge=0)
    w: int = Field(..., description="Width in grid columns (1-6).", ge=1, le=6)
    h: int = Field(..., description="Height in grid rows.", ge=1)
    min_h: int = Field(..., description="Minimum height in grid rows.", ge=1)

class EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItemLinkedDashboardsItem(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    field: str
    dashboard_id: str

class EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItemOnDemandExtraction(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    extraction_state: str | None = None
    enabled: bool | None = None

class EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItem(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    fields: list[str] | None = None
    aggregates: list[str] | None = None
    columns: list[str] | None = None
    field_aliases: list[str] | None = None
    name: str | None = None
    conditions: str | None = None
    orderby: str | None = None
    is_hidden: bool | None = None
    on_demand_extraction: EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItemOnDemandExtraction | None = Field(None, description="Allows parameters to be defined in snake case, but passed as camel case.\n\nErrors are output in camel case.")
    on_demand_extraction_disabled: bool | None = None
    selected_aggregate: int | None = None
    linked_dashboards: list[EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItemLinkedDashboardsItem] | None = None

class EditAnOrganizationSCustomDashboardBodyWidgetsItem(PermissiveModel):
    """Allows parameters to be defined in snake case, but passed as camel case.

Errors are output in camel case."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    thresholds: dict[str, Any] | None = None
    display_type: Literal["line", "area", "stacked_area", "bar", "table", "big_number", "top_n", "details", "categorical_bar", "wheel", "rage_and_dead_clicks", "server_tree", "text", "agents_traces_table"] | None = Field(None, description="* `line`\n* `area`\n* `stacked_area`\n* `bar`\n* `table`\n* `big_number`\n* `top_n`\n* `details`\n* `categorical_bar`\n* `wheel`\n* `rage_and_dead_clicks`\n* `server_tree`\n* `text`\n* `agents_traces_table`")
    interval: str | None = Field(None, max_length=10)
    queries: list[EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItem] | None = None
    widget_type: Literal["discover", "issue", "metrics", "error-events", "transaction-like", "spans", "logs", "tracemetrics", "preprod-app-size"] | None = Field(None, description="* `discover`\n* `issue`\n* `metrics`\n* `error-events`\n* `transaction-like`\n* `spans`\n* `logs`\n* `tracemetrics`\n* `preprod-app-size`")
    limit: int | None = Field(None, ge=1)
    layout: EditAnOrganizationSCustomDashboardBodyWidgetsItemLayout | None = None
    axis_range: Literal["auto", "dataMin"] | None = Field(None, description="* `auto`\n* `dataMin`")
    legend_type: Literal["default", "breakdown"] | None = Field(None, description="* `default`\n* `breakdown`")

class Filters(PermissiveModel):
    """Filter settings for the source. This is optional for all sources.

**`filetypes`** ***(list)*** - A list of file types that can be found on this source. If this is left empty, all file types will be enabled. The options are:
- `pe` - Windows executable files
- `pdb` - Windows debug files
- `portablepdb` - .NET portable debug files
- `mach_code` - MacOS executable files
- `mach_debug` - MacOS debug files
- `elf_code` - ELF executable files
- `elf_debug` - ELF debug files
- `wasm_code` - WASM executable files
- `wasm_debug` - WASM debug files
- `breakpad` - Breakpad symbol files
- `sourcebundle` - Source code bundles
- `uuidmap` - Apple UUID mapping files
- `bcsymbolmap` - Apple bitcode symbol maps
- `il2cpp` - Unity IL2CPP mapping files
- `proguard` - ProGuard mapping files

**`path_patterns`** ***(list)*** - A list of glob patterns to check against the debug and code file paths of debug files. Only files that match one of these patterns will be requested from the source. If this is left empty, no path-based filtering takes place.

**`requires_checksum`** ***(boolean)*** - Whether this source requires a debug checksum to be sent with each request. Defaults to `false`.

```json
{
    "filters": {
        "filetypes": ["pe", "pdb", "portablepdb"],
        "path_patterns": ["*ffmpeg*"]
    }
}
```"""
    filetypes: list[Literal["pe", "pdb", "portablepdb", "mach_debug", "mach_code", "elf_debug", "elf_code", "wasm_debug", "wasm_code", "breakpad", "sourcebundle", "uuidmap", "bcsymbolmap", "il2cpp", "proguard", "dartsymbolmap"]] | None = Field(None, description="The file types enabled for the source.")
    path_patterns: list[str] | None = Field(None, description="The debug and code file paths enabled for the source.")
    requires_checksum: bool | None = Field(None, description="Whether the source requires debug checksums.")

class MonitorAlertRuleTargetsItem(PermissiveModel):
    target_identifier: int = Field(..., validation_alias="targetIdentifier", serialization_alias="targetIdentifier")
    target_type: str = Field(..., validation_alias="targetType", serialization_alias="targetType")

class MonitorAlertRule(PermissiveModel):
    targets: list[MonitorAlertRuleTargetsItem]
    environment: str

class MonitorConfig(PermissiveModel):
    schedule_type: Literal["crontab", "interval"]
    schedule: str | list[int]
    checkin_margin: int | None = Field(...)
    max_runtime: int | None = Field(...)
    timezone_: str | None = Field(..., validation_alias="timezone", serialization_alias="timezone")
    failure_issue_threshold: int | None = Field(...)
    recovery_threshold: int | None = Field(...)
    alert_rule_id: int | None = Field(...)

class MonitorEnvironmentsActiveIncidentBrokenNotice(PermissiveModel):
    user_notified_timestamp: str = Field(..., validation_alias="userNotifiedTimestamp", serialization_alias="userNotifiedTimestamp", json_schema_extra={'format': 'date-time'})
    environment_muted_timestamp: str = Field(..., validation_alias="environmentMutedTimestamp", serialization_alias="environmentMutedTimestamp", json_schema_extra={'format': 'date-time'})

class MonitorEnvironmentsActiveIncident(PermissiveModel):
    starting_timestamp: str = Field(..., validation_alias="startingTimestamp", serialization_alias="startingTimestamp", json_schema_extra={'format': 'date-time'})
    resolving_timestamp: str = Field(..., validation_alias="resolvingTimestamp", serialization_alias="resolvingTimestamp", json_schema_extra={'format': 'date-time'})
    broken_notice: MonitorEnvironmentsActiveIncidentBrokenNotice | None = Field(..., validation_alias="brokenNotice", serialization_alias="brokenNotice")

class MonitorEnvironments(PermissiveModel):
    name: str
    status: str
    is_muted: bool = Field(..., validation_alias="isMuted", serialization_alias="isMuted")
    date_created: str = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    last_check_in: str = Field(..., validation_alias="lastCheckIn", serialization_alias="lastCheckIn", json_schema_extra={'format': 'date-time'})
    next_check_in: str = Field(..., validation_alias="nextCheckIn", serialization_alias="nextCheckIn", json_schema_extra={'format': 'date-time'})
    next_check_in_latest: str = Field(..., validation_alias="nextCheckInLatest", serialization_alias="nextCheckInLatest", json_schema_extra={'format': 'date-time'})
    active_incident: MonitorEnvironmentsActiveIncident | None = Field(..., validation_alias="activeIncident", serialization_alias="activeIncident")

class MonitorOwner(PermissiveModel):
    type_: Literal["user", "team"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    email: str | None = None

class MonitorProjectAvatar(PermissiveModel):
    avatar_type: str | None = Field(None, validation_alias="avatarType", serialization_alias="avatarType")
    avatar_uuid: str | None = Field(None, validation_alias="avatarUuid", serialization_alias="avatarUuid")
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl")

class MonitorProject(PermissiveModel):
    stats: Any | None = None
    transaction_stats: Any | None = Field(None, validation_alias="transactionStats", serialization_alias="transactionStats")
    session_stats: Any | None = Field(None, validation_alias="sessionStats", serialization_alias="sessionStats")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    slug: str
    name: str
    platform: str | None = Field(...)
    date_created: str = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    is_bookmarked: bool = Field(..., validation_alias="isBookmarked", serialization_alias="isBookmarked")
    is_member: bool = Field(..., validation_alias="isMember", serialization_alias="isMember")
    features: list[str]
    first_event: str | None = Field(..., validation_alias="firstEvent", serialization_alias="firstEvent", json_schema_extra={'format': 'date-time'})
    first_transaction_event: bool = Field(..., validation_alias="firstTransactionEvent", serialization_alias="firstTransactionEvent")
    access: list[str]
    has_access: bool = Field(..., validation_alias="hasAccess", serialization_alias="hasAccess")
    has_feedbacks: bool = Field(..., validation_alias="hasFeedbacks", serialization_alias="hasFeedbacks")
    has_flags: bool = Field(..., validation_alias="hasFlags", serialization_alias="hasFlags")
    has_minified_stack_trace: bool = Field(..., validation_alias="hasMinifiedStackTrace", serialization_alias="hasMinifiedStackTrace")
    has_monitors: bool = Field(..., validation_alias="hasMonitors", serialization_alias="hasMonitors")
    has_new_feedbacks: bool = Field(..., validation_alias="hasNewFeedbacks", serialization_alias="hasNewFeedbacks")
    has_profiles: bool = Field(..., validation_alias="hasProfiles", serialization_alias="hasProfiles")
    has_replays: bool = Field(..., validation_alias="hasReplays", serialization_alias="hasReplays")
    has_sessions: bool = Field(..., validation_alias="hasSessions", serialization_alias="hasSessions")
    has_insights_http: bool = Field(..., validation_alias="hasInsightsHttp", serialization_alias="hasInsightsHttp")
    has_insights_db: bool = Field(..., validation_alias="hasInsightsDb", serialization_alias="hasInsightsDb")
    has_insights_assets: bool = Field(..., validation_alias="hasInsightsAssets", serialization_alias="hasInsightsAssets")
    has_insights_app_start: bool = Field(..., validation_alias="hasInsightsAppStart", serialization_alias="hasInsightsAppStart")
    has_insights_screen_load: bool = Field(..., validation_alias="hasInsightsScreenLoad", serialization_alias="hasInsightsScreenLoad")
    has_insights_vitals: bool = Field(..., validation_alias="hasInsightsVitals", serialization_alias="hasInsightsVitals")
    has_insights_caches: bool = Field(..., validation_alias="hasInsightsCaches", serialization_alias="hasInsightsCaches")
    has_insights_queues: bool = Field(..., validation_alias="hasInsightsQueues", serialization_alias="hasInsightsQueues")
    has_insights_agent_monitoring: bool = Field(..., validation_alias="hasInsightsAgentMonitoring", serialization_alias="hasInsightsAgentMonitoring")
    has_insights_mcp: bool = Field(..., validation_alias="hasInsightsMCP", serialization_alias="hasInsightsMCP")
    has_logs: bool = Field(..., validation_alias="hasLogs", serialization_alias="hasLogs")
    has_trace_metrics: bool = Field(..., validation_alias="hasTraceMetrics", serialization_alias="hasTraceMetrics")
    is_internal: bool = Field(..., validation_alias="isInternal", serialization_alias="isInternal")
    is_public: bool = Field(..., validation_alias="isPublic", serialization_alias="isPublic")
    avatar: MonitorProjectAvatar
    color: str
    status: str

class Monitor(PermissiveModel):
    alert_rule: MonitorAlertRule | None = Field(None, validation_alias="alertRule", serialization_alias="alertRule")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    slug: str
    status: str
    is_muted: bool = Field(..., validation_alias="isMuted", serialization_alias="isMuted")
    is_upserting: bool = Field(..., validation_alias="isUpserting", serialization_alias="isUpserting")
    config: MonitorConfig
    date_created: str = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    project: MonitorProject
    environments: MonitorEnvironments
    owner: MonitorOwner

class RuleCreatedBy(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    email: str

class RuleErrorsItem(PermissiveModel):
    detail: str

class Rule(PermissiveModel):
    """This represents a Sentry Rule."""
    owner: str | None = None
    created_by: RuleCreatedBy | None = Field(None, validation_alias="createdBy", serialization_alias="createdBy")
    environment: str | None = None
    last_triggered: str | None = Field(None, validation_alias="lastTriggered", serialization_alias="lastTriggered")
    snooze_created_by: str | None = Field(None, validation_alias="snoozeCreatedBy", serialization_alias="snoozeCreatedBy")
    snooze_for_everyone: bool | None = Field(None, validation_alias="snoozeForEveryone", serialization_alias="snoozeForEveryone")
    disable_reason: str | None = Field(None, validation_alias="disableReason", serialization_alias="disableReason")
    disable_date: str | None = Field(None, validation_alias="disableDate", serialization_alias="disableDate")
    errors: list[RuleErrorsItem] | None = None
    id_: str | None = Field(..., validation_alias="id", serialization_alias="id")
    conditions: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    action_match: str = Field(..., validation_alias="actionMatch", serialization_alias="actionMatch")
    filter_match: str = Field(..., validation_alias="filterMatch", serialization_alias="filterMatch")
    frequency: int
    name: str
    date_created: str = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    projects: list[str]
    status: str
    snooze: bool

class TeamAvatar(PermissiveModel):
    avatar_type: str | None = Field(None, validation_alias="avatarType", serialization_alias="avatarType")
    avatar_uuid: str | None = Field(None, validation_alias="avatarUuid", serialization_alias="avatarUuid")
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl")

class TeamExternalTeamsItem(PermissiveModel):
    external_id: str | None = Field(None, validation_alias="externalId", serialization_alias="externalId")
    user_id: str | None = Field(None, validation_alias="userId", serialization_alias="userId")
    team_id: str | None = Field(None, validation_alias="teamId", serialization_alias="teamId")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    provider: str
    external_name: str = Field(..., validation_alias="externalName", serialization_alias="externalName")
    integration_id: str = Field(..., validation_alias="integrationId", serialization_alias="integrationId")

class TeamOrganizationAvatar(PermissiveModel):
    avatar_type: str | None = Field(None, validation_alias="avatarType", serialization_alias="avatarType")
    avatar_uuid: str | None = Field(None, validation_alias="avatarUuid", serialization_alias="avatarUuid")
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl")

class TeamOrganizationLinks(PermissiveModel):
    organization_url: str = Field(..., validation_alias="organizationUrl", serialization_alias="organizationUrl")
    region_url: str = Field(..., validation_alias="regionUrl", serialization_alias="regionUrl")

class TeamOrganizationOnboardingTasksItem(PermissiveModel):
    task: str | None = Field(...)
    status: str
    completion_seen: str | None = Field(..., validation_alias="completionSeen", serialization_alias="completionSeen", json_schema_extra={'format': 'date-time'})
    date_completed: str = Field(..., validation_alias="dateCompleted", serialization_alias="dateCompleted", json_schema_extra={'format': 'date-time'})
    data: Any

class TeamOrganizationStatus(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str

class TeamOrganization(PermissiveModel):
    features: list[str] | None = None
    extra_options: dict[str, dict[str, Any]] | None = Field(None, validation_alias="extraOptions", serialization_alias="extraOptions")
    access: list[str] | None = None
    onboarding_tasks: list[TeamOrganizationOnboardingTasksItem] | None = Field(None, validation_alias="onboardingTasks", serialization_alias="onboardingTasks")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    slug: str
    status: TeamOrganizationStatus
    name: str
    date_created: str = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    is_early_adopter: bool = Field(..., validation_alias="isEarlyAdopter", serialization_alias="isEarlyAdopter")
    require2fa: bool = Field(..., validation_alias="require2FA", serialization_alias="require2FA")
    avatar: TeamOrganizationAvatar
    links: TeamOrganizationLinks
    has_auth_provider: bool = Field(..., validation_alias="hasAuthProvider", serialization_alias="hasAuthProvider")
    allow_member_invite: bool = Field(..., validation_alias="allowMemberInvite", serialization_alias="allowMemberInvite")
    allow_member_project_creation: bool = Field(..., validation_alias="allowMemberProjectCreation", serialization_alias="allowMemberProjectCreation")
    allow_superuser_access: bool = Field(..., validation_alias="allowSuperuserAccess", serialization_alias="allowSuperuserAccess")

class TeamProjectsItemAvatar(PermissiveModel):
    avatar_type: str | None = Field(None, validation_alias="avatarType", serialization_alias="avatarType")
    avatar_uuid: str | None = Field(None, validation_alias="avatarUuid", serialization_alias="avatarUuid")
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl")

class TeamProjectsItem(PermissiveModel):
    stats: Any | None = None
    transaction_stats: Any | None = Field(None, validation_alias="transactionStats", serialization_alias="transactionStats")
    session_stats: Any | None = Field(None, validation_alias="sessionStats", serialization_alias="sessionStats")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    slug: str
    name: str
    platform: str | None = Field(...)
    date_created: str = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    is_bookmarked: bool = Field(..., validation_alias="isBookmarked", serialization_alias="isBookmarked")
    is_member: bool = Field(..., validation_alias="isMember", serialization_alias="isMember")
    features: list[str]
    first_event: str | None = Field(..., validation_alias="firstEvent", serialization_alias="firstEvent", json_schema_extra={'format': 'date-time'})
    first_transaction_event: bool = Field(..., validation_alias="firstTransactionEvent", serialization_alias="firstTransactionEvent")
    access: list[str]
    has_access: bool = Field(..., validation_alias="hasAccess", serialization_alias="hasAccess")
    has_feedbacks: bool = Field(..., validation_alias="hasFeedbacks", serialization_alias="hasFeedbacks")
    has_flags: bool = Field(..., validation_alias="hasFlags", serialization_alias="hasFlags")
    has_minified_stack_trace: bool = Field(..., validation_alias="hasMinifiedStackTrace", serialization_alias="hasMinifiedStackTrace")
    has_monitors: bool = Field(..., validation_alias="hasMonitors", serialization_alias="hasMonitors")
    has_new_feedbacks: bool = Field(..., validation_alias="hasNewFeedbacks", serialization_alias="hasNewFeedbacks")
    has_profiles: bool = Field(..., validation_alias="hasProfiles", serialization_alias="hasProfiles")
    has_replays: bool = Field(..., validation_alias="hasReplays", serialization_alias="hasReplays")
    has_sessions: bool = Field(..., validation_alias="hasSessions", serialization_alias="hasSessions")
    has_insights_http: bool = Field(..., validation_alias="hasInsightsHttp", serialization_alias="hasInsightsHttp")
    has_insights_db: bool = Field(..., validation_alias="hasInsightsDb", serialization_alias="hasInsightsDb")
    has_insights_assets: bool = Field(..., validation_alias="hasInsightsAssets", serialization_alias="hasInsightsAssets")
    has_insights_app_start: bool = Field(..., validation_alias="hasInsightsAppStart", serialization_alias="hasInsightsAppStart")
    has_insights_screen_load: bool = Field(..., validation_alias="hasInsightsScreenLoad", serialization_alias="hasInsightsScreenLoad")
    has_insights_vitals: bool = Field(..., validation_alias="hasInsightsVitals", serialization_alias="hasInsightsVitals")
    has_insights_caches: bool = Field(..., validation_alias="hasInsightsCaches", serialization_alias="hasInsightsCaches")
    has_insights_queues: bool = Field(..., validation_alias="hasInsightsQueues", serialization_alias="hasInsightsQueues")
    has_insights_agent_monitoring: bool = Field(..., validation_alias="hasInsightsAgentMonitoring", serialization_alias="hasInsightsAgentMonitoring")
    has_insights_mcp: bool = Field(..., validation_alias="hasInsightsMCP", serialization_alias="hasInsightsMCP")
    has_logs: bool = Field(..., validation_alias="hasLogs", serialization_alias="hasLogs")
    has_trace_metrics: bool = Field(..., validation_alias="hasTraceMetrics", serialization_alias="hasTraceMetrics")
    is_internal: bool = Field(..., validation_alias="isInternal", serialization_alias="isInternal")
    is_public: bool = Field(..., validation_alias="isPublic", serialization_alias="isPublic")
    avatar: TeamProjectsItemAvatar
    color: str
    status: str

class Team(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    slug: str
    name: str
    date_created: str | None = Field(..., validation_alias="dateCreated", serialization_alias="dateCreated", json_schema_extra={'format': 'date-time'})
    is_member: bool = Field(..., validation_alias="isMember", serialization_alias="isMember")
    team_role: str | None = Field(..., validation_alias="teamRole", serialization_alias="teamRole")
    flags: dict[str, Any]
    access: list[str]
    has_access: bool = Field(..., validation_alias="hasAccess", serialization_alias="hasAccess")
    is_pending: bool = Field(..., validation_alias="isPending", serialization_alias="isPending")
    member_count: int = Field(..., validation_alias="memberCount", serialization_alias="memberCount")
    avatar: TeamAvatar
    external_teams: list[TeamExternalTeamsItem] | None = Field(None, validation_alias="externalTeams", serialization_alias="externalTeams")
    organization: TeamOrganization | None = None
    projects: list[TeamProjectsItem] | None = None

class UpdateAMonitorBodyConfig(PermissiveModel):
    """The configuration for the monitor."""
    schedule_type: Literal["crontab", "interval"] | None = Field(None, description="Currently supports \"crontab\" or \"interval\"\n\n* `crontab`\n* `interval`")
    schedule: Any = Field(..., description="Varies depending on the schedule_type. Is either a crontab string, or a 2 element tuple for intervals (e.g. [1, 'day'])")
    checkin_margin: int | None = Field(None, description="How long (in minutes) after the expected checkin time will we wait until we consider the checkin to have been missed.", ge=1, le=40320)
    max_runtime: int | None = Field(None, description="How long (in minutes) is the checkin allowed to run for in CheckInStatus.IN_PROGRESS before it is considered failed.", ge=1, le=40320)
    timezone_: Literal["Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara", "Africa/Asmera", "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre", "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome", "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Timbuktu", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak", "America/Anchorage", "America/Anguilla", "America/Antigua", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Argentina/Catamarca", "America/Argentina/ComodRivadavia", "America/Argentina/Cordoba", "America/Argentina/Jujuy", "America/Argentina/La_Rioja", "America/Argentina/Mendoza", "America/Argentina/Rio_Gallegos", "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis", "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Aruba", "America/Asuncion", "America/Atikokan", "America/Atka", "America/Bahia", "America/Bahia_Banderas", "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise", "America/Buenos_Aires", "America/Cambridge_Bay", "America/Campo_Grande", "America/Cancun", "America/Caracas", "America/Catamarca", "America/Cayenne", "America/Cayman", "America/Chicago", "America/Chihuahua", "America/Ciudad_Juarez", "America/Coral_Harbour", "America/Cordoba", "America/Costa_Rica", "America/Coyhaique", "America/Creston", "America/Cuiaba", "America/Curacao", "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek", "America/Denver", "America/Detroit", "America/Dominica", "America/Edmonton", "America/Eirunepe", "America/El_Salvador", "America/Ensenada", "America/Fort_Nelson", "America/Fort_Wayne", "America/Fortaleza", "America/Glace_Bay", "America/Godthab", "America/Goose_Bay", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala", "America/Guayaquil", "America/Guyana", "America/Halifax", "America/Havana", "America/Hermosillo", "America/Indiana/Indianapolis", "America/Indiana/Knox", "America/Indiana/Marengo", "America/Indiana/Petersburg", "America/Indiana/Tell_City", "America/Indiana/Vevay", "America/Indiana/Vincennes", "America/Indiana/Winamac", "America/Indianapolis", "America/Inuvik", "America/Iqaluit", "America/Jamaica", "America/Jujuy", "America/Juneau", "America/Kentucky/Louisville", "America/Kentucky/Monticello", "America/Knox_IN", "America/Kralendijk", "America/La_Paz", "America/Lima", "America/Los_Angeles", "America/Louisville", "America/Lower_Princes", "America/Maceio", "America/Managua", "America/Manaus", "America/Marigot", "America/Martinique", "America/Matamoros", "America/Mazatlan", "America/Mendoza", "America/Menominee", "America/Merida", "America/Metlakatla", "America/Mexico_City", "America/Miquelon", "America/Moncton", "America/Monterrey", "America/Montevideo", "America/Montreal", "America/Montserrat", "America/Nassau", "America/New_York", "America/Nipigon", "America/Nome", "America/Noronha", "America/North_Dakota/Beulah", "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Nuuk", "America/Ojinaga", "America/Panama", "America/Pangnirtung", "America/Paramaribo", "America/Phoenix", "America/Port-au-Prince", "America/Port_of_Spain", "America/Porto_Acre", "America/Porto_Velho", "America/Puerto_Rico", "America/Punta_Arenas", "America/Rainy_River", "America/Rankin_Inlet", "America/Recife", "America/Regina", "America/Resolute", "America/Rio_Branco", "America/Rosario", "America/Santa_Isabel", "America/Santarem", "America/Santiago", "America/Santo_Domingo", "America/Sao_Paulo", "America/Scoresbysund", "America/Shiprock", "America/Sitka", "America/St_Barthelemy", "America/St_Johns", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa", "America/Thule", "America/Thunder_Bay", "America/Tijuana", "America/Toronto", "America/Tortola", "America/Vancouver", "America/Virgin", "America/Whitehorse", "America/Winnipeg", "America/Yakutat", "America/Yellowknife", "Antarctica/Casey", "Antarctica/Davis", "Antarctica/DumontDUrville", "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo", "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/South_Pole", "Antarctica/Syowa", "Antarctica/Troll", "Antarctica/Vostok", "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman", "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Ashkhabad", "Asia/Atyrau", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Barnaul", "Asia/Beirut", "Asia/Bishkek", "Asia/Brunei", "Asia/Calcutta", "Asia/Chita", "Asia/Choibalsan", "Asia/Chongqing", "Asia/Chungking", "Asia/Colombo", "Asia/Dacca", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Famagusta", "Asia/Gaza", "Asia/Harbin", "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd", "Asia/Irkutsk", "Asia/Istanbul", "Asia/Jakarta", "Asia/Jayapura", "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi", "Asia/Kashgar", "Asia/Kathmandu", "Asia/Katmandu", "Asia/Khandyga", "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Kuwait", "Asia/Macao", "Asia/Macau", "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk", "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang", "Asia/Qatar", "Asia/Qostanay", "Asia/Qyzylorda", "Asia/Rangoon", "Asia/Riyadh", "Asia/Saigon", "Asia/Sakhalin", "Asia/Samarkand", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Srednekolymsk", "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran", "Asia/Tel_Aviv", "Asia/Thimbu", "Asia/Thimphu", "Asia/Tokyo", "Asia/Tomsk", "Asia/Ujung_Pandang", "Asia/Ulaanbaatar", "Asia/Ulan_Bator", "Asia/Urumqi", "Asia/Ust-Nera", "Asia/Vientiane", "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yangon", "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores", "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde", "Atlantic/Faeroe", "Atlantic/Faroe", "Atlantic/Jan_Mayen", "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia", "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/ACT", "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill", "Australia/Canberra", "Australia/Currie", "Australia/Darwin", "Australia/Eucla", "Australia/Hobart", "Australia/LHI", "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne", "Australia/NSW", "Australia/North", "Australia/Perth", "Australia/Queensland", "Australia/South", "Australia/Sydney", "Australia/Tasmania", "Australia/Victoria", "Australia/West", "Australia/Yancowinna", "Brazil/Acre", "Brazil/DeNoronha", "Brazil/East", "Brazil/West", "CET", "CST6CDT", "Canada/Atlantic", "Canada/Central", "Canada/Eastern", "Canada/Mountain", "Canada/Newfoundland", "Canada/Pacific", "Canada/Saskatchewan", "Canada/Yukon", "Chile/Continental", "Chile/EasterIsland", "Cuba", "EET", "EST", "EST5EDT", "Egypt", "Eire", "Etc/GMT", "Etc/GMT+0", "Etc/GMT+1", "Etc/GMT+10", "Etc/GMT+11", "Etc/GMT+12", "Etc/GMT+2", "Etc/GMT+3", "Etc/GMT+4", "Etc/GMT+5", "Etc/GMT+6", "Etc/GMT+7", "Etc/GMT+8", "Etc/GMT+9", "Etc/GMT-0", "Etc/GMT-1", "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12", "Etc/GMT-13", "Etc/GMT-14", "Etc/GMT-2", "Etc/GMT-3", "Etc/GMT-4", "Etc/GMT-5", "Etc/GMT-6", "Etc/GMT-7", "Etc/GMT-8", "Etc/GMT-9", "Etc/GMT0", "Etc/Greenwich", "Etc/UCT", "Etc/UTC", "Etc/Universal", "Etc/Zulu", "Europe/Amsterdam", "Europe/Andorra", "Europe/Astrakhan", "Europe/Athens", "Europe/Belfast", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest", "Europe/Budapest", "Europe/Busingen", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Kirov", "Europe/Kyiv", "Europe/Lisbon", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco", "Europe/Moscow", "Europe/Nicosia", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo", "Europe/Saratov", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Tiraspol", "Europe/Ulyanovsk", "Europe/Uzhgorod", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius", "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb", "Europe/Zaporozhye", "Europe/Zurich", "GB", "GB-Eire", "GMT", "GMT+0", "GMT-0", "GMT0", "Greenwich", "HST", "Hongkong", "Iceland", "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte", "Indian/Reunion", "Iran", "Israel", "Jamaica", "Japan", "Kwajalein", "Libya", "MET", "MST", "MST7MDT", "Mexico/BajaNorte", "Mexico/BajaSur", "Mexico/General", "NZ", "NZ-CHAT", "Navajo", "PRC", "PST8PDT", "Pacific/Apia", "Pacific/Auckland", "Pacific/Bougainville", "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier", "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Kanton", "Pacific/Kiritimati", "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei", "Pacific/Ponape", "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Samoa", "Pacific/Tahiti", "Pacific/Tarawa", "Pacific/Tongatapu", "Pacific/Truk", "Pacific/Wake", "Pacific/Wallis", "Pacific/Yap", "Poland", "Portugal", "ROC", "ROK", "Singapore", "Turkey", "UCT", "US/Alaska", "US/Aleutian", "US/Arizona", "US/Central", "US/East-Indiana", "US/Eastern", "US/Hawaii", "US/Indiana-Starke", "US/Michigan", "US/Mountain", "US/Pacific", "US/Samoa", "UTC", "Universal", "W-SU", "WET", "Zulu", "localtime", ""] | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="tz database style timezone string\n\n* `Africa/Abidjan`\n* `Africa/Accra`\n* `Africa/Addis_Ababa`\n* `Africa/Algiers`\n* `Africa/Asmara`\n* `Africa/Asmera`\n* `Africa/Bamako`\n* `Africa/Bangui`\n* `Africa/Banjul`\n* `Africa/Bissau`\n* `Africa/Blantyre`\n* `Africa/Brazzaville`\n* `Africa/Bujumbura`\n* `Africa/Cairo`\n* `Africa/Casablanca`\n* `Africa/Ceuta`\n* `Africa/Conakry`\n* `Africa/Dakar`\n* `Africa/Dar_es_Salaam`\n* `Africa/Djibouti`\n* `Africa/Douala`\n* `Africa/El_Aaiun`\n* `Africa/Freetown`\n* `Africa/Gaborone`\n* `Africa/Harare`\n* `Africa/Johannesburg`\n* `Africa/Juba`\n* `Africa/Kampala`\n* `Africa/Khartoum`\n* `Africa/Kigali`\n* `Africa/Kinshasa`\n* `Africa/Lagos`\n* `Africa/Libreville`\n* `Africa/Lome`\n* `Africa/Luanda`\n* `Africa/Lubumbashi`\n* `Africa/Lusaka`\n* `Africa/Malabo`\n* `Africa/Maputo`\n* `Africa/Maseru`\n* `Africa/Mbabane`\n* `Africa/Mogadishu`\n* `Africa/Monrovia`\n* `Africa/Nairobi`\n* `Africa/Ndjamena`\n* `Africa/Niamey`\n* `Africa/Nouakchott`\n* `Africa/Ouagadougou`\n* `Afri...")
    failure_issue_threshold: int | None = Field(None, description="How many consecutive missed or failed check-ins in a row before creating a new issue.", ge=1, le=720)
    recovery_threshold: int | None = Field(None, description="How many successful check-ins in a row before resolving an issue.", ge=1, le=720)

class UpdateAMonitorByIdBodyConditionGroup(PermissiveModel):
    """
            Issue detection configuration for when to create an issue and at what priority level.


            - `logicType`: `any`
            - `type`: Any of `gt` (greater than), `lte` (less than or equal), or `anomaly_detection` (dynamic)
            - `comparison`: Any positive integer. This is threshold that must be crossed for the monitor to create an issue, e.g. "Create a metric issue when there are more than 5 unresolved error events".
                - If creating a **dynamic** monitor, see the options below.
                    - `seasonality`: `auto`
                    - `sensitivity`: Level of responsiveness. Options are one of `low`, `medium`, or `high`
                    - `thresholdType`: If you want to be alerted to anomalies that are moving above, below, or in both directions in relation to your threshold.
                        - `0`: Above
                        - `1`: Below
                        - `2`: Above and below

            - `conditionResult`: The issue state change when the threshold is crossed.
                - `75`: High priority
                - `50`: Low priority
                - `0`: Resolved


            **Threshold and Change Monitor**
            ```json
                "logicType": "any",
                "conditions": [
                    {
                        "type": "gt",
                        "comparison": 10,
                        "conditionResult": 75
                    },
                    {
                        "type": "lte",
                        "comparison": 10,
                        "conditionResult": 0
                    }
                ],
                "actions": []
            ```

            **Threshold Monitor with Medium Priority**
            ```json
                "logicType": "any",
                "conditions": [
                    {
                        type: "gt",
                        comparison: 5,
                        conditionResult: 75
                    },
                    {
                        type: "gt",
                        comparison: 2,
                        conditionResult: 50
                    },
                    {
                        type: "lte",
                        comparison: 2,
                        conditionResult: 0
                    }
                ],
                "actions": []
            ```

            **Dynamic Monitor**
            ```json
                "logicType": "any",
                "conditions": [
                    {
                        "type": "anomaly_detection",
                        "comparison": {
                            "seasonality": "auto",
                            "sensitivity": "medium",
                            "thresholdType": 2
                        },
                        "conditionResult": 75
                    }
                ],
                "actions": []
            ```
"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    logic_type: Literal["any", "any-short", "all", "none"] = Field(..., description="* `any`\n* `any-short`\n* `all`\n* `none`")
    conditions: list[Any] | None = None

class UpdateAMonitorForAProjectBodyConfig(PermissiveModel):
    """The configuration for the monitor."""
    schedule_type: Literal["crontab", "interval"] | None = Field(None, description="Currently supports \"crontab\" or \"interval\"\n\n* `crontab`\n* `interval`")
    schedule: Any = Field(..., description="Varies depending on the schedule_type. Is either a crontab string, or a 2 element tuple for intervals (e.g. [1, 'day'])")
    checkin_margin: int | None = Field(None, description="How long (in minutes) after the expected checkin time will we wait until we consider the checkin to have been missed.", ge=1, le=40320)
    max_runtime: int | None = Field(None, description="How long (in minutes) is the checkin allowed to run for in CheckInStatus.IN_PROGRESS before it is considered failed.", ge=1, le=40320)
    timezone_: Literal["Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara", "Africa/Asmera", "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre", "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome", "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Timbuktu", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak", "America/Anchorage", "America/Anguilla", "America/Antigua", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Argentina/Catamarca", "America/Argentina/ComodRivadavia", "America/Argentina/Cordoba", "America/Argentina/Jujuy", "America/Argentina/La_Rioja", "America/Argentina/Mendoza", "America/Argentina/Rio_Gallegos", "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis", "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Aruba", "America/Asuncion", "America/Atikokan", "America/Atka", "America/Bahia", "America/Bahia_Banderas", "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise", "America/Buenos_Aires", "America/Cambridge_Bay", "America/Campo_Grande", "America/Cancun", "America/Caracas", "America/Catamarca", "America/Cayenne", "America/Cayman", "America/Chicago", "America/Chihuahua", "America/Ciudad_Juarez", "America/Coral_Harbour", "America/Cordoba", "America/Costa_Rica", "America/Coyhaique", "America/Creston", "America/Cuiaba", "America/Curacao", "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek", "America/Denver", "America/Detroit", "America/Dominica", "America/Edmonton", "America/Eirunepe", "America/El_Salvador", "America/Ensenada", "America/Fort_Nelson", "America/Fort_Wayne", "America/Fortaleza", "America/Glace_Bay", "America/Godthab", "America/Goose_Bay", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala", "America/Guayaquil", "America/Guyana", "America/Halifax", "America/Havana", "America/Hermosillo", "America/Indiana/Indianapolis", "America/Indiana/Knox", "America/Indiana/Marengo", "America/Indiana/Petersburg", "America/Indiana/Tell_City", "America/Indiana/Vevay", "America/Indiana/Vincennes", "America/Indiana/Winamac", "America/Indianapolis", "America/Inuvik", "America/Iqaluit", "America/Jamaica", "America/Jujuy", "America/Juneau", "America/Kentucky/Louisville", "America/Kentucky/Monticello", "America/Knox_IN", "America/Kralendijk", "America/La_Paz", "America/Lima", "America/Los_Angeles", "America/Louisville", "America/Lower_Princes", "America/Maceio", "America/Managua", "America/Manaus", "America/Marigot", "America/Martinique", "America/Matamoros", "America/Mazatlan", "America/Mendoza", "America/Menominee", "America/Merida", "America/Metlakatla", "America/Mexico_City", "America/Miquelon", "America/Moncton", "America/Monterrey", "America/Montevideo", "America/Montreal", "America/Montserrat", "America/Nassau", "America/New_York", "America/Nipigon", "America/Nome", "America/Noronha", "America/North_Dakota/Beulah", "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Nuuk", "America/Ojinaga", "America/Panama", "America/Pangnirtung", "America/Paramaribo", "America/Phoenix", "America/Port-au-Prince", "America/Port_of_Spain", "America/Porto_Acre", "America/Porto_Velho", "America/Puerto_Rico", "America/Punta_Arenas", "America/Rainy_River", "America/Rankin_Inlet", "America/Recife", "America/Regina", "America/Resolute", "America/Rio_Branco", "America/Rosario", "America/Santa_Isabel", "America/Santarem", "America/Santiago", "America/Santo_Domingo", "America/Sao_Paulo", "America/Scoresbysund", "America/Shiprock", "America/Sitka", "America/St_Barthelemy", "America/St_Johns", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa", "America/Thule", "America/Thunder_Bay", "America/Tijuana", "America/Toronto", "America/Tortola", "America/Vancouver", "America/Virgin", "America/Whitehorse", "America/Winnipeg", "America/Yakutat", "America/Yellowknife", "Antarctica/Casey", "Antarctica/Davis", "Antarctica/DumontDUrville", "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo", "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/South_Pole", "Antarctica/Syowa", "Antarctica/Troll", "Antarctica/Vostok", "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman", "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Ashkhabad", "Asia/Atyrau", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Barnaul", "Asia/Beirut", "Asia/Bishkek", "Asia/Brunei", "Asia/Calcutta", "Asia/Chita", "Asia/Choibalsan", "Asia/Chongqing", "Asia/Chungking", "Asia/Colombo", "Asia/Dacca", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Famagusta", "Asia/Gaza", "Asia/Harbin", "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd", "Asia/Irkutsk", "Asia/Istanbul", "Asia/Jakarta", "Asia/Jayapura", "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi", "Asia/Kashgar", "Asia/Kathmandu", "Asia/Katmandu", "Asia/Khandyga", "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Kuwait", "Asia/Macao", "Asia/Macau", "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk", "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang", "Asia/Qatar", "Asia/Qostanay", "Asia/Qyzylorda", "Asia/Rangoon", "Asia/Riyadh", "Asia/Saigon", "Asia/Sakhalin", "Asia/Samarkand", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Srednekolymsk", "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran", "Asia/Tel_Aviv", "Asia/Thimbu", "Asia/Thimphu", "Asia/Tokyo", "Asia/Tomsk", "Asia/Ujung_Pandang", "Asia/Ulaanbaatar", "Asia/Ulan_Bator", "Asia/Urumqi", "Asia/Ust-Nera", "Asia/Vientiane", "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yangon", "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores", "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde", "Atlantic/Faeroe", "Atlantic/Faroe", "Atlantic/Jan_Mayen", "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia", "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/ACT", "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill", "Australia/Canberra", "Australia/Currie", "Australia/Darwin", "Australia/Eucla", "Australia/Hobart", "Australia/LHI", "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne", "Australia/NSW", "Australia/North", "Australia/Perth", "Australia/Queensland", "Australia/South", "Australia/Sydney", "Australia/Tasmania", "Australia/Victoria", "Australia/West", "Australia/Yancowinna", "Brazil/Acre", "Brazil/DeNoronha", "Brazil/East", "Brazil/West", "CET", "CST6CDT", "Canada/Atlantic", "Canada/Central", "Canada/Eastern", "Canada/Mountain", "Canada/Newfoundland", "Canada/Pacific", "Canada/Saskatchewan", "Canada/Yukon", "Chile/Continental", "Chile/EasterIsland", "Cuba", "EET", "EST", "EST5EDT", "Egypt", "Eire", "Etc/GMT", "Etc/GMT+0", "Etc/GMT+1", "Etc/GMT+10", "Etc/GMT+11", "Etc/GMT+12", "Etc/GMT+2", "Etc/GMT+3", "Etc/GMT+4", "Etc/GMT+5", "Etc/GMT+6", "Etc/GMT+7", "Etc/GMT+8", "Etc/GMT+9", "Etc/GMT-0", "Etc/GMT-1", "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12", "Etc/GMT-13", "Etc/GMT-14", "Etc/GMT-2", "Etc/GMT-3", "Etc/GMT-4", "Etc/GMT-5", "Etc/GMT-6", "Etc/GMT-7", "Etc/GMT-8", "Etc/GMT-9", "Etc/GMT0", "Etc/Greenwich", "Etc/UCT", "Etc/UTC", "Etc/Universal", "Etc/Zulu", "Europe/Amsterdam", "Europe/Andorra", "Europe/Astrakhan", "Europe/Athens", "Europe/Belfast", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest", "Europe/Budapest", "Europe/Busingen", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Kirov", "Europe/Kyiv", "Europe/Lisbon", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco", "Europe/Moscow", "Europe/Nicosia", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo", "Europe/Saratov", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Tiraspol", "Europe/Ulyanovsk", "Europe/Uzhgorod", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius", "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb", "Europe/Zaporozhye", "Europe/Zurich", "GB", "GB-Eire", "GMT", "GMT+0", "GMT-0", "GMT0", "Greenwich", "HST", "Hongkong", "Iceland", "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte", "Indian/Reunion", "Iran", "Israel", "Jamaica", "Japan", "Kwajalein", "Libya", "MET", "MST", "MST7MDT", "Mexico/BajaNorte", "Mexico/BajaSur", "Mexico/General", "NZ", "NZ-CHAT", "Navajo", "PRC", "PST8PDT", "Pacific/Apia", "Pacific/Auckland", "Pacific/Bougainville", "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier", "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Kanton", "Pacific/Kiritimati", "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei", "Pacific/Ponape", "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Samoa", "Pacific/Tahiti", "Pacific/Tarawa", "Pacific/Tongatapu", "Pacific/Truk", "Pacific/Wake", "Pacific/Wallis", "Pacific/Yap", "Poland", "Portugal", "ROC", "ROK", "Singapore", "Turkey", "UCT", "US/Alaska", "US/Aleutian", "US/Arizona", "US/Central", "US/East-Indiana", "US/Eastern", "US/Hawaii", "US/Indiana-Starke", "US/Michigan", "US/Mountain", "US/Pacific", "US/Samoa", "UTC", "Universal", "W-SU", "WET", "Zulu", "localtime", ""] | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="tz database style timezone string\n\n* `Africa/Abidjan`\n* `Africa/Accra`\n* `Africa/Addis_Ababa`\n* `Africa/Algiers`\n* `Africa/Asmara`\n* `Africa/Asmera`\n* `Africa/Bamako`\n* `Africa/Bangui`\n* `Africa/Banjul`\n* `Africa/Bissau`\n* `Africa/Blantyre`\n* `Africa/Brazzaville`\n* `Africa/Bujumbura`\n* `Africa/Cairo`\n* `Africa/Casablanca`\n* `Africa/Ceuta`\n* `Africa/Conakry`\n* `Africa/Dakar`\n* `Africa/Dar_es_Salaam`\n* `Africa/Djibouti`\n* `Africa/Douala`\n* `Africa/El_Aaiun`\n* `Africa/Freetown`\n* `Africa/Gaborone`\n* `Africa/Harare`\n* `Africa/Johannesburg`\n* `Africa/Juba`\n* `Africa/Kampala`\n* `Africa/Khartoum`\n* `Africa/Kigali`\n* `Africa/Kinshasa`\n* `Africa/Lagos`\n* `Africa/Libreville`\n* `Africa/Lome`\n* `Africa/Luanda`\n* `Africa/Lubumbashi`\n* `Africa/Lusaka`\n* `Africa/Malabo`\n* `Africa/Maputo`\n* `Africa/Maseru`\n* `Africa/Mbabane`\n* `Africa/Mogadishu`\n* `Africa/Monrovia`\n* `Africa/Nairobi`\n* `Africa/Ndjamena`\n* `Africa/Niamey`\n* `Africa/Nouakchott`\n* `Africa/Ouagadougou`\n* `Afri...")
    failure_issue_threshold: int | None = Field(None, description="How many consecutive missed or failed check-ins in a row before creating a new issue.", ge=1, le=720)
    recovery_threshold: int | None = Field(None, description="How many successful check-ins in a row before resolving an issue.", ge=1, le=720)

class UpdateAnAlertByIdBodyTriggers(PermissiveModel):
    """The conditions on which the alert will trigger. See available options below.
        ```json
            "triggers": {
                "organizationId": "1",
                "logicType": "any-short",
                "conditions": [
                    {
                        "type": "first_seen_event",
                        "comparison": true,
                        "conditionResult": true
                    },
                    {
                        "type": "issue_resolved_trigger",
                        "comparison": true,
                        "conditionResult": true
                    },
                    {
                        "type": "reappeared_event",
                        "comparison": true,
                        "conditionResult": true
                    },
                    {
                        "type": "regression_event",
                        "comparison": true,
                        "conditionResult": true
                    }
                ],
                "actions": []
            }
        ```
"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    logic_type: Literal["any", "any-short", "all", "none"] = Field(..., description="* `any`\n* `any-short`\n* `all`\n* `none`")
    conditions: list[Any] | None = None

class UpdateAnOrganizationSReleaseBodyRefsItem(PermissiveModel):
    commit: str
    repository: str = Field(..., max_length=200)
    previous_commit: str | None = Field(None, validation_alias="previousCommit", serialization_alias="previousCommit", max_length=64)


# Rebuild models to resolve forward references (required for circular refs)
BulkMutateAnOrganizationSIssuesBodyStatusDetails.model_rebuild()
BulkMutateAnOrganizationSIssuesBodyStatusDetailsInCommit.model_rebuild()
CreateAMonitorBodyConfig.model_rebuild()
CreateAMonitorForAProjectBodyConditionGroup.model_rebuild()
CreateAnAlertForAnOrganizationBodyTriggers.model_rebuild()
CreateANewDashboardForAnOrganizationBodyPermissions.model_rebuild()
CreateANewDashboardForAnOrganizationBodyWidgetsItem.model_rebuild()
CreateANewDashboardForAnOrganizationBodyWidgetsItemLayout.model_rebuild()
CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItem.model_rebuild()
CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItemLinkedDashboardsItem.model_rebuild()
CreateANewDashboardForAnOrganizationBodyWidgetsItemQueriesItemOnDemandExtraction.model_rebuild()
CreateANewReleaseForAnOrganizationBodyRefsItem.model_rebuild()
EditAnOrganizationSCustomDashboardBodyPermissions.model_rebuild()
EditAnOrganizationSCustomDashboardBodyWidgetsItem.model_rebuild()
EditAnOrganizationSCustomDashboardBodyWidgetsItemLayout.model_rebuild()
EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItem.model_rebuild()
EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItemLinkedDashboardsItem.model_rebuild()
EditAnOrganizationSCustomDashboardBodyWidgetsItemQueriesItemOnDemandExtraction.model_rebuild()
Filters.model_rebuild()
Monitor.model_rebuild()
MonitorAlertRule.model_rebuild()
MonitorAlertRuleTargetsItem.model_rebuild()
MonitorConfig.model_rebuild()
MonitorEnvironments.model_rebuild()
MonitorEnvironmentsActiveIncident.model_rebuild()
MonitorEnvironmentsActiveIncidentBrokenNotice.model_rebuild()
MonitorOwner.model_rebuild()
MonitorProject.model_rebuild()
MonitorProjectAvatar.model_rebuild()
Rule.model_rebuild()
RuleCreatedBy.model_rebuild()
RuleErrorsItem.model_rebuild()
Team.model_rebuild()
TeamAvatar.model_rebuild()
TeamExternalTeamsItem.model_rebuild()
TeamOrganization.model_rebuild()
TeamOrganizationAvatar.model_rebuild()
TeamOrganizationLinks.model_rebuild()
TeamOrganizationOnboardingTasksItem.model_rebuild()
TeamOrganizationStatus.model_rebuild()
TeamProjectsItem.model_rebuild()
TeamProjectsItemAvatar.model_rebuild()
UpdateAMonitorBodyConfig.model_rebuild()
UpdateAMonitorByIdBodyConditionGroup.model_rebuild()
UpdateAMonitorForAProjectBodyConfig.model_rebuild()
UpdateAnAlertByIdBodyTriggers.model_rebuild()
UpdateAnOrganizationSReleaseBodyRefsItem.model_rebuild()

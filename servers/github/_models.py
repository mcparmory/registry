"""
Github MCP Server - Pydantic Models

Generated: 2026-05-05 15:02:43 UTC
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
    "ActionsAddCustomLabelsToSelfHostedRunnerForOrgRequest",
    "ActionsAddCustomLabelsToSelfHostedRunnerForRepoRequest",
    "ActionsAddRepoAccessToSelfHostedRunnerGroupInOrgRequest",
    "ActionsAddSelectedRepoToOrgSecretRequest",
    "ActionsAddSelectedRepoToOrgVariableRequest",
    "ActionsAddSelfHostedRunnerToGroupForOrgRequest",
    "ActionsApproveWorkflowRunRequest",
    "ActionsCancelWorkflowRunRequest",
    "ActionsCreateEnvironmentVariableRequest",
    "ActionsCreateHostedRunnerForOrgRequest",
    "ActionsCreateOrgVariableRequest",
    "ActionsCreateOrUpdateOrgSecretRequest",
    "ActionsCreateRegistrationTokenForOrgRequest",
    "ActionsCreateRemoveTokenForOrgRequest",
    "ActionsCreateRemoveTokenForRepoRequest",
    "ActionsCreateRepoVariableRequest",
    "ActionsCreateSelfHostedRunnerGroupForOrgRequest",
    "ActionsCreateWorkflowDispatchRequest",
    "ActionsDeleteActionsCacheByIdRequest",
    "ActionsDeleteActionsCacheByKeyRequest",
    "ActionsDeleteArtifactRequest",
    "ActionsDeleteCustomImageFromOrgRequest",
    "ActionsDeleteCustomImageVersionFromOrgRequest",
    "ActionsDeleteEnvironmentSecretRequest",
    "ActionsDeleteEnvironmentVariableRequest",
    "ActionsDeleteHostedRunnerForOrgRequest",
    "ActionsDeleteOrgSecretRequest",
    "ActionsDeleteOrgVariableRequest",
    "ActionsDeleteRepoSecretRequest",
    "ActionsDeleteRepoVariableRequest",
    "ActionsDeleteSelfHostedRunnerFromOrgRequest",
    "ActionsDeleteSelfHostedRunnerFromRepoRequest",
    "ActionsDeleteSelfHostedRunnerGroupFromOrgRequest",
    "ActionsDeleteWorkflowRunLogsRequest",
    "ActionsDeleteWorkflowRunRequest",
    "ActionsDisableSelectedRepositorySelfHostedRunnersOrganizationRequest",
    "ActionsDisableWorkflowRequest",
    "ActionsDownloadArtifactRequest",
    "ActionsDownloadJobLogsForWorkflowRunRequest",
    "ActionsDownloadWorkflowRunAttemptLogsRequest",
    "ActionsDownloadWorkflowRunLogsRequest",
    "ActionsEnableWorkflowRequest",
    "ActionsForceCancelWorkflowRunRequest",
    "ActionsGetActionsCacheListRequest",
    "ActionsGetActionsCacheRetentionLimitForRepositoryRequest",
    "ActionsGetActionsCacheStorageLimitForEnterpriseRequest",
    "ActionsGetActionsCacheStorageLimitForOrganizationRequest",
    "ActionsGetActionsCacheStorageLimitForRepositoryRequest",
    "ActionsGetActionsCacheUsageByRepoForOrgRequest",
    "ActionsGetActionsCacheUsageForOrgRequest",
    "ActionsGetActionsCacheUsageRequest",
    "ActionsGetArtifactRequest",
    "ActionsGetCustomImageForOrgRequest",
    "ActionsGetCustomImageVersionForOrgRequest",
    "ActionsGetCustomOidcSubClaimForRepoRequest",
    "ActionsGetEnvironmentPublicKeyRequest",
    "ActionsGetEnvironmentSecretRequest",
    "ActionsGetEnvironmentVariableRequest",
    "ActionsGetHostedRunnerForOrgRequest",
    "ActionsGetHostedRunnersGithubOwnedImagesForOrgRequest",
    "ActionsGetHostedRunnersLimitsForOrgRequest",
    "ActionsGetHostedRunnersMachineSpecsForOrgRequest",
    "ActionsGetHostedRunnersPartnerImagesForOrgRequest",
    "ActionsGetHostedRunnersPlatformsForOrgRequest",
    "ActionsGetJobForWorkflowRunRequest",
    "ActionsGetOrgPublicKeyRequest",
    "ActionsGetOrgSecretRequest",
    "ActionsGetOrgVariableRequest",
    "ActionsGetPendingDeploymentsForRunRequest",
    "ActionsGetRepoPublicKeyRequest",
    "ActionsGetRepoSecretRequest",
    "ActionsGetRepoVariableRequest",
    "ActionsGetReviewsForRunRequest",
    "ActionsGetSelfHostedRunnerForOrgRequest",
    "ActionsGetSelfHostedRunnerForRepoRequest",
    "ActionsGetSelfHostedRunnerGroupForOrgRequest",
    "ActionsGetWorkflowRequest",
    "ActionsGetWorkflowRunAttemptRequest",
    "ActionsGetWorkflowRunRequest",
    "ActionsGetWorkflowRunUsageRequest",
    "ActionsListArtifactsForRepoRequest",
    "ActionsListCustomImagesForOrgRequest",
    "ActionsListCustomImageVersionsForOrgRequest",
    "ActionsListEnvironmentSecretsRequest",
    "ActionsListEnvironmentVariablesRequest",
    "ActionsListGithubHostedRunnersInGroupForOrgRequest",
    "ActionsListHostedRunnersForOrgRequest",
    "ActionsListJobsForWorkflowRunAttemptRequest",
    "ActionsListJobsForWorkflowRunRequest",
    "ActionsListLabelsForSelfHostedRunnerForOrgRequest",
    "ActionsListLabelsForSelfHostedRunnerForRepoRequest",
    "ActionsListOrgSecretsRequest",
    "ActionsListOrgVariablesRequest",
    "ActionsListRepoAccessToSelfHostedRunnerGroupInOrgRequest",
    "ActionsListRepoOrganizationSecretsRequest",
    "ActionsListRepoOrganizationVariablesRequest",
    "ActionsListRepoSecretsRequest",
    "ActionsListRepoVariablesRequest",
    "ActionsListRepoWorkflowsRequest",
    "ActionsListRunnerApplicationsForOrgRequest",
    "ActionsListRunnerApplicationsForRepoRequest",
    "ActionsListSelectedReposForOrgSecretRequest",
    "ActionsListSelectedReposForOrgVariableRequest",
    "ActionsListSelectedRepositoriesEnabledGithubActionsOrganizationRequest",
    "ActionsListSelectedRepositoriesSelfHostedRunnersOrganizationRequest",
    "ActionsListSelfHostedRunnerGroupsForOrgRequest",
    "ActionsListSelfHostedRunnersForOrgRequest",
    "ActionsListSelfHostedRunnersForRepoRequest",
    "ActionsListSelfHostedRunnersInGroupForOrgRequest",
    "ActionsListWorkflowRunArtifactsRequest",
    "ActionsListWorkflowRunsForRepoRequest",
    "ActionsListWorkflowRunsRequest",
    "ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForOrgRequest",
    "ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForRepoRequest",
    "ActionsRemoveCustomLabelFromSelfHostedRunnerForOrgRequest",
    "ActionsRemoveCustomLabelFromSelfHostedRunnerForRepoRequest",
    "ActionsRemoveRepoAccessToSelfHostedRunnerGroupInOrgRequest",
    "ActionsRemoveSelectedRepoFromOrgSecretRequest",
    "ActionsRemoveSelectedRepoFromOrgVariableRequest",
    "ActionsRemoveSelfHostedRunnerFromGroupForOrgRequest",
    "ActionsReRunJobForWorkflowRunRequest",
    "ActionsReRunWorkflowFailedJobsRequest",
    "ActionsReRunWorkflowRequest",
    "ActionsReviewCustomGatesForRunRequest",
    "ActionsReviewPendingDeploymentsForRunRequest",
    "ActionsSetCustomLabelsForSelfHostedRunnerForOrgRequest",
    "ActionsSetCustomLabelsForSelfHostedRunnerForRepoRequest",
    "ActionsSetRepoAccessToSelfHostedRunnerGroupInOrgRequest",
    "ActionsSetSelectedReposForOrgSecretRequest",
    "ActionsSetSelectedReposForOrgVariableRequest",
    "ActionsSetSelfHostedRunnersInGroupForOrgRequest",
    "ActionsUpdateEnvironmentVariableRequest",
    "ActionsUpdateHostedRunnerForOrgRequest",
    "ActionsUpdateOrgVariableRequest",
    "ActionsUpdateRepoVariableRequest",
    "ActionsUpdateSelfHostedRunnerGroupForOrgRequest",
    "ActivityCheckRepoIsStarredByAuthenticatedUserRequest",
    "ActivityDeleteRepoSubscriptionRequest",
    "ActivityDeleteThreadSubscriptionRequest",
    "ActivityGetRepoSubscriptionRequest",
    "ActivityGetThreadRequest",
    "ActivityGetThreadSubscriptionForAuthenticatedUserRequest",
    "ActivityListEventsForAuthenticatedUserRequest",
    "ActivityListNotificationsForAuthenticatedUserRequest",
    "ActivityListOrgEventsForAuthenticatedUserRequest",
    "ActivityListPublicEventsForRepoNetworkRequest",
    "ActivityListPublicEventsForUserRequest",
    "ActivityListPublicOrgEventsRequest",
    "ActivityListReceivedEventsForUserRequest",
    "ActivityListReceivedPublicEventsForUserRequest",
    "ActivityListRepoEventsRequest",
    "ActivityListRepoNotificationsForAuthenticatedUserRequest",
    "ActivityListReposStarredByAuthenticatedUserRequest",
    "ActivityListReposStarredByUserRequest",
    "ActivityListReposWatchedByUserRequest",
    "ActivityListStargazersForRepoRequest",
    "ActivityListWatchersForRepoRequest",
    "ActivityMarkNotificationsAsReadRequest",
    "ActivityMarkRepoNotificationsAsReadRequest",
    "ActivityMarkThreadAsDoneRequest",
    "ActivityMarkThreadAsReadRequest",
    "ActivitySetRepoSubscriptionRequest",
    "ActivitySetThreadSubscriptionRequest",
    "ActivityStarRepoForAuthenticatedUserRequest",
    "ActivityUnstarRepoForAuthenticatedUserRequest",
    "ApiInsightsGetSubjectStatsRequest",
    "ApiInsightsGetSummaryStatsByActorRequest",
    "ApiInsightsGetSummaryStatsRequest",
    "ApiInsightsGetTimeStatsByActorRequest",
    "ApiInsightsGetTimeStatsByUserRequest",
    "ApiInsightsGetTimeStatsRequest",
    "ApiInsightsGetUserStatsRequest",
    "AppsAddRepoToInstallationForAuthenticatedUserRequest",
    "AppsDeleteAuthorizationRequest",
    "AppsDeleteInstallationRequest",
    "AppsDeleteTokenRequest",
    "AppsGetInstallationRequest",
    "AppsGetOrgInstallationRequest",
    "AppsGetRepoInstallationRequest",
    "AppsGetSubscriptionPlanForAccountRequest",
    "AppsGetSubscriptionPlanForAccountStubbedRequest",
    "AppsGetUserInstallationRequest",
    "AppsGetWebhookDeliveryRequest",
    "AppsListInstallationsRequest",
    "AppsRedeliverWebhookDeliveryRequest",
    "AppsRemoveRepoFromInstallationForAuthenticatedUserRequest",
    "AppsScopeTokenRequest",
    "AppsSuspendInstallationRequest",
    "AppsUnsuspendInstallationRequest",
    "BillingDeleteBudgetOrgRequest",
    "BillingGetAllBudgetsOrgRequest",
    "BillingGetBudgetOrgRequest",
    "BillingGetGithubBillingPremiumRequestUsageReportOrgRequest",
    "BillingGetGithubBillingPremiumRequestUsageReportUserRequest",
    "BillingGetGithubBillingUsageReportOrgRequest",
    "BillingGetGithubBillingUsageReportUserRequest",
    "BillingGetGithubBillingUsageSummaryReportOrgRequest",
    "BillingGetGithubBillingUsageSummaryReportUserRequest",
    "BillingUpdateBudgetOrgRequest",
    "CampaignsCreateCampaignRequest",
    "CampaignsDeleteCampaignRequest",
    "CampaignsGetCampaignSummaryRequest",
    "CampaignsListOrgCampaignsRequest",
    "CampaignsUpdateCampaignRequest",
    "ChecksCreateRequest",
    "ChecksCreateSuiteRequest",
    "ChecksGetRequest",
    "ChecksGetSuiteRequest",
    "ChecksListAnnotationsRequest",
    "ChecksListForRefRequest",
    "ChecksListForSuiteRequest",
    "ChecksListSuitesForRefRequest",
    "ChecksRerequestRunRequest",
    "ChecksRerequestSuiteRequest",
    "ChecksUpdateRequest",
    "ClassroomGetAClassroomRequest",
    "ClassroomGetAnAssignmentRequest",
    "ClassroomGetAssignmentGradesRequest",
    "ClassroomListAcceptedAssignmentsForAnAssignmentRequest",
    "ClassroomListAssignmentsForAClassroomRequest",
    "CodeScanningCommitAutofixRequest",
    "CodeScanningCreateAutofixRequest",
    "CodeScanningCreateVariantAnalysisRequest",
    "CodeScanningDeleteAnalysisRequest",
    "CodeScanningDeleteCodeqlDatabaseRequest",
    "CodeScanningGetAlertRequest",
    "CodeScanningGetAnalysisRequest",
    "CodeScanningGetAutofixRequest",
    "CodeScanningGetCodeqlDatabaseRequest",
    "CodeScanningGetDefaultSetupRequest",
    "CodeScanningGetSarifRequest",
    "CodeScanningGetVariantAnalysisRepoTaskRequest",
    "CodeScanningGetVariantAnalysisRequest",
    "CodeScanningListAlertInstancesRequest",
    "CodeScanningListAlertsForOrgRequest",
    "CodeScanningListAlertsForRepoRequest",
    "CodeScanningListCodeqlDatabasesRequest",
    "CodeScanningListRecentAnalysesRequest",
    "CodeScanningUpdateAlertRequest",
    "CodeScanningUploadSarifRequest",
    "CodeSecurityAttachConfigurationRequest",
    "CodeSecurityAttachEnterpriseConfigurationRequest",
    "CodeSecurityDeleteConfigurationForEnterpriseRequest",
    "CodeSecurityDeleteConfigurationRequest",
    "CodeSecurityDetachConfigurationRequest",
    "CodeSecurityGetConfigurationForRepositoryRequest",
    "CodeSecurityGetConfigurationRequest",
    "CodeSecurityGetConfigurationsForEnterpriseRequest",
    "CodeSecurityGetConfigurationsForOrgRequest",
    "CodeSecurityGetDefaultConfigurationsForEnterpriseRequest",
    "CodeSecurityGetDefaultConfigurationsRequest",
    "CodeSecurityGetRepositoriesForConfigurationRequest",
    "CodeSecurityGetRepositoriesForEnterpriseConfigurationRequest",
    "CodeSecurityGetSingleConfigurationForEnterpriseRequest",
    "CodeSecurityUpdateConfigurationRequest",
    "CodesOfConductGetConductCodeRequest",
    "CodespacesAddRepositoryForSecretForAuthenticatedUserRequest",
    "CodespacesAddSelectedRepoToOrgSecretRequest",
    "CodespacesCodespaceMachinesForAuthenticatedUserRequest",
    "CodespacesCreateForAuthenticatedUserRequest",
    "CodespacesCreateOrUpdateOrgSecretRequest",
    "CodespacesCreateOrUpdateRepoSecretRequest",
    "CodespacesCreateOrUpdateSecretForAuthenticatedUserRequest",
    "CodespacesCreateWithPrForAuthenticatedUserRequest",
    "CodespacesCreateWithRepoForAuthenticatedUserRequest",
    "CodespacesDeleteForAuthenticatedUserRequest",
    "CodespacesDeleteFromOrganizationRequest",
    "CodespacesDeleteOrgSecretRequest",
    "CodespacesDeleteRepoSecretRequest",
    "CodespacesDeleteSecretForAuthenticatedUserRequest",
    "CodespacesExportForAuthenticatedUserRequest",
    "CodespacesGetCodespacesForUserInOrgRequest",
    "CodespacesGetExportDetailsForAuthenticatedUserRequest",
    "CodespacesGetForAuthenticatedUserRequest",
    "CodespacesGetOrgSecretRequest",
    "CodespacesGetRepoPublicKeyRequest",
    "CodespacesGetRepoSecretRequest",
    "CodespacesGetSecretForAuthenticatedUserRequest",
    "CodespacesListDevcontainersInRepositoryForAuthenticatedUserRequest",
    "CodespacesListForAuthenticatedUserRequest",
    "CodespacesListInOrganizationRequest",
    "CodespacesListInRepositoryForAuthenticatedUserRequest",
    "CodespacesListOrgSecretsRequest",
    "CodespacesListRepoSecretsRequest",
    "CodespacesListRepositoriesForSecretForAuthenticatedUserRequest",
    "CodespacesListSelectedReposForOrgSecretRequest",
    "CodespacesPreFlightWithRepoForAuthenticatedUserRequest",
    "CodespacesPublishForAuthenticatedUserRequest",
    "CodespacesRemoveRepositoryForSecretForAuthenticatedUserRequest",
    "CodespacesRemoveSelectedRepoFromOrgSecretRequest",
    "CodespacesRepoMachinesForAuthenticatedUserRequest",
    "CodespacesSetRepositoriesForSecretForAuthenticatedUserRequest",
    "CodespacesSetSelectedReposForOrgSecretRequest",
    "CodespacesStartForAuthenticatedUserRequest",
    "CodespacesStopForAuthenticatedUserRequest",
    "CodespacesStopInOrganizationRequest",
    "CodespacesUpdateForAuthenticatedUserRequest",
    "CopilotAddCopilotSeatsForTeamsRequest",
    "CopilotAddCopilotSeatsForUsersRequest",
    "CopilotCancelCopilotSeatAssignmentForTeamsRequest",
    "CopilotCancelCopilotSeatAssignmentForUsersRequest",
    "CopilotCopilotContentExclusionForOrganizationRequest",
    "CopilotCopilotMetricsForOrganizationRequest",
    "CopilotCopilotMetricsForTeamRequest",
    "CopilotEnableCopilotCodingAgentForRepositoryInOrganizationRequest",
    "CopilotGetCopilotCodingAgentPermissionsOrganizationRequest",
    "CopilotGetCopilotOrganizationDetailsRequest",
    "CopilotGetCopilotSeatDetailsForUserRequest",
    "CopilotListCopilotCodingAgentSelectedRepositoriesForOrganizationRequest",
    "CopilotListCopilotSeatsRequest",
    "DependabotAddSelectedRepoToOrgSecretRequest",
    "DependabotCreateOrUpdateOrgSecretRequest",
    "DependabotCreateOrUpdateRepoSecretRequest",
    "DependabotDeleteOrgSecretRequest",
    "DependabotDeleteRepoSecretRequest",
    "DependabotGetAlertRequest",
    "DependabotGetOrgPublicKeyRequest",
    "DependabotGetOrgSecretRequest",
    "DependabotGetRepoPublicKeyRequest",
    "DependabotGetRepoSecretRequest",
    "DependabotListAlertsForEnterpriseRequest",
    "DependabotListAlertsForOrgRequest",
    "DependabotListAlertsForRepoRequest",
    "DependabotListOrgSecretsRequest",
    "DependabotListRepoSecretsRequest",
    "DependabotListSelectedReposForOrgSecretRequest",
    "DependabotRemoveSelectedRepoFromOrgSecretRequest",
    "DependabotRepositoryAccessForOrgRequest",
    "DependabotSetSelectedReposForOrgSecretRequest",
    "DependabotUpdateAlertRequest",
    "DependabotUpdateRepositoryAccessForOrgRequest",
    "DependencyGraphCreateRepositorySnapshotRequest",
    "DependencyGraphDiffRangeRequest",
    "DependencyGraphExportSbomRequest",
    "EnterpriseTeamMembershipsAddRequest",
    "EnterpriseTeamMembershipsBulkAddRequest",
    "EnterpriseTeamMembershipsBulkRemoveRequest",
    "EnterpriseTeamMembershipsGetRequest",
    "EnterpriseTeamMembershipsListRequest",
    "EnterpriseTeamMembershipsRemoveRequest",
    "EnterpriseTeamOrganizationsAddRequest",
    "EnterpriseTeamOrganizationsBulkAddRequest",
    "EnterpriseTeamOrganizationsBulkRemoveRequest",
    "EnterpriseTeamOrganizationsDeleteRequest",
    "EnterpriseTeamOrganizationsGetAssignmentRequest",
    "EnterpriseTeamOrganizationsGetAssignmentsRequest",
    "EnterpriseTeamsCreateRequest",
    "EnterpriseTeamsDeleteRequest",
    "EnterpriseTeamsGetRequest",
    "EnterpriseTeamsListRequest",
    "EnterpriseTeamsUpdateRequest",
    "GistsCheckIsStarredRequest",
    "GistsCreateCommentRequest",
    "GistsCreateRequest",
    "GistsDeleteCommentRequest",
    "GistsDeleteRequest",
    "GistsForkRequest",
    "GistsGetCommentRequest",
    "GistsGetRequest",
    "GistsGetRevisionRequest",
    "GistsListCommentsRequest",
    "GistsListCommitsRequest",
    "GistsListForksRequest",
    "GistsListForUserRequest",
    "GistsListPublicRequest",
    "GistsListRequest",
    "GistsListStarredRequest",
    "GistsStarRequest",
    "GistsUnstarRequest",
    "GistsUpdateCommentRequest",
    "GistsUpdateRequest",
    "GitCreateBlobRequest",
    "GitCreateCommitRequest",
    "GitCreateRefRequest",
    "GitCreateTagRequest",
    "GitCreateTreeRequest",
    "GitDeleteRefRequest",
    "GitGetBlobRequest",
    "GitGetCommitRequest",
    "GitGetRefRequest",
    "GitGetTagRequest",
    "GitGetTreeRequest",
    "GitignoreGetTemplateRequest",
    "GitListMatchingRefsRequest",
    "GitUpdateRefRequest",
    "HostedComputeDeleteNetworkConfigurationFromOrgRequest",
    "HostedComputeGetNetworkConfigurationForOrgRequest",
    "HostedComputeGetNetworkSettingsForOrgRequest",
    "HostedComputeListNetworkConfigurationsForOrgRequest",
    "HostedComputeUpdateNetworkConfigurationForOrgRequest",
    "InteractionsGetRestrictionsForOrgRequest",
    "InteractionsGetRestrictionsForRepoRequest",
    "InteractionsRemoveRestrictionsForRepoRequest",
    "IssuesAddAssigneesRequest",
    "IssuesAddBlockedByDependencyRequest",
    "IssuesAddIssueFieldValuesRequest",
    "IssuesAddLabelsRequest",
    "IssuesAddSubIssueRequest",
    "IssuesCheckUserCanBeAssignedRequest",
    "IssuesCheckUserCanBeAssignedToIssueRequest",
    "IssuesCreateCommentRequest",
    "IssuesCreateLabelRequest",
    "IssuesCreateMilestoneRequest",
    "IssuesCreateRequest",
    "IssuesDeleteCommentRequest",
    "IssuesDeleteIssueFieldValueRequest",
    "IssuesDeleteLabelRequest",
    "IssuesDeleteMilestoneRequest",
    "IssuesGetCommentRequest",
    "IssuesGetEventRequest",
    "IssuesGetLabelRequest",
    "IssuesGetMilestoneRequest",
    "IssuesGetParentRequest",
    "IssuesGetRequest",
    "IssuesListAssigneesRequest",
    "IssuesListCommentsForRepoRequest",
    "IssuesListCommentsRequest",
    "IssuesListDependenciesBlockedByRequest",
    "IssuesListDependenciesBlockingRequest",
    "IssuesListEventsForRepoRequest",
    "IssuesListEventsForTimelineRequest",
    "IssuesListEventsRequest",
    "IssuesListForAuthenticatedUserRequest",
    "IssuesListForOrgRequest",
    "IssuesListForRepoRequest",
    "IssuesListLabelsForMilestoneRequest",
    "IssuesListLabelsForRepoRequest",
    "IssuesListLabelsOnIssueRequest",
    "IssuesListMilestonesRequest",
    "IssuesListRequest",
    "IssuesListSubIssuesRequest",
    "IssuesLockRequest",
    "IssuesPinCommentRequest",
    "IssuesRemoveAllLabelsRequest",
    "IssuesRemoveAssigneesRequest",
    "IssuesRemoveDependencyBlockedByRequest",
    "IssuesRemoveLabelRequest",
    "IssuesRemoveSubIssueRequest",
    "IssuesReprioritizeSubIssueRequest",
    "IssuesSetIssueFieldValuesRequest",
    "IssuesSetLabelsRequest",
    "IssuesUnlockRequest",
    "IssuesUnpinCommentRequest",
    "IssuesUpdateCommentRequest",
    "IssuesUpdateLabelRequest",
    "IssuesUpdateMilestoneRequest",
    "IssuesUpdateRequest",
    "LicensesGetAllCommonlyUsedRequest",
    "LicensesGetForRepoRequest",
    "LicensesGetRequest",
    "MigrationsDeleteArchiveForAuthenticatedUserRequest",
    "MigrationsDeleteArchiveForOrgRequest",
    "MigrationsDownloadArchiveForOrgRequest",
    "MigrationsGetArchiveForAuthenticatedUserRequest",
    "MigrationsGetStatusForAuthenticatedUserRequest",
    "MigrationsGetStatusForOrgRequest",
    "MigrationsListForOrgRequest",
    "MigrationsListReposForAuthenticatedUserRequest",
    "MigrationsListReposForOrgRequest",
    "MigrationsUnlockRepoForAuthenticatedUserRequest",
    "MigrationsUnlockRepoForOrgRequest",
    "OidcCreateOidcCustomPropertyInclusionForEnterpriseRequest",
    "OidcCreateOidcCustomPropertyInclusionForOrgRequest",
    "OidcListOidcCustomPropertyInclusionsForEnterpriseRequest",
    "OidcListOidcCustomPropertyInclusionsForOrgRequest",
    "OrgsAssignTeamToOrgRoleRequest",
    "OrgsAssignUserToOrgRoleRequest",
    "OrgsCancelInvitationRequest",
    "OrgsCheckBlockedUserRequest",
    "OrgsCheckMembershipForUserRequest",
    "OrgsCheckPublicMembershipForUserRequest",
    "OrgsConvertMemberToOutsideCollaboratorRequest",
    "OrgsCreateArtifactDeploymentRecordRequest",
    "OrgsCreateArtifactStorageRecordRequest",
    "OrgsCreateInvitationRequest",
    "OrgsCreateIssueFieldRequest",
    "OrgsCreateIssueTypeRequest",
    "OrgsCreateWebhookRequest",
    "OrgsCustomPropertiesForReposCreateOrUpdateOrganizationValuesRequest",
    "OrgsCustomPropertiesForReposGetOrganizationDefinitionRequest",
    "OrgsCustomPropertiesForReposGetOrganizationDefinitionsRequest",
    "OrgsCustomPropertiesForReposGetOrganizationValuesRequest",
    "OrgsDeleteAttestationsBulkRequest",
    "OrgsDeleteAttestationsByIdRequest",
    "OrgsDeleteAttestationsBySubjectDigestRequest",
    "OrgsDeleteIssueFieldRequest",
    "OrgsDeleteIssueTypeRequest",
    "OrgsDeleteRequest",
    "OrgsDeleteWebhookRequest",
    "OrgsDisableSelectedRepositoryImmutableReleasesOrganizationRequest",
    "OrgsEnableSelectedRepositoryImmutableReleasesOrganizationRequest",
    "OrgsGetImmutableReleasesSettingsRepositoriesRequest",
    "OrgsGetMembershipForAuthenticatedUserRequest",
    "OrgsGetMembershipForUserRequest",
    "OrgsGetOrgRoleRequest",
    "OrgsGetOrgRulesetHistoryRequest",
    "OrgsGetOrgRulesetVersionRequest",
    "OrgsGetRequest",
    "OrgsGetWebhookConfigForOrgRequest",
    "OrgsGetWebhookDeliveryRequest",
    "OrgsGetWebhookRequest",
    "OrgsListAppInstallationsRequest",
    "OrgsListArtifactDeploymentRecordsRequest",
    "OrgsListArtifactStorageRecordsRequest",
    "OrgsListAttestationRepositoriesRequest",
    "OrgsListAttestationsBulkRequest",
    "OrgsListAttestationsRequest",
    "OrgsListBlockedUsersRequest",
    "OrgsListFailedInvitationsRequest",
    "OrgsListForUserRequest",
    "OrgsListInvitationTeamsRequest",
    "OrgsListIssueFieldsRequest",
    "OrgsListIssueTypesRequest",
    "OrgsListMembershipsForAuthenticatedUserRequest",
    "OrgsListMembersRequest",
    "OrgsListOrgRolesRequest",
    "OrgsListOrgRoleTeamsRequest",
    "OrgsListOrgRoleUsersRequest",
    "OrgsListOutsideCollaboratorsRequest",
    "OrgsListPatGrantRepositoriesRequest",
    "OrgsListPatGrantRequestRepositoriesRequest",
    "OrgsListPatGrantRequestsRequest",
    "OrgsListPatGrantsRequest",
    "OrgsListPendingInvitationsRequest",
    "OrgsListPublicMembersRequest",
    "OrgsListRequest",
    "OrgsListWebhookDeliveriesRequest",
    "OrgsListWebhooksRequest",
    "OrgsRedeliverWebhookDeliveryRequest",
    "OrgsRemoveMembershipForUserRequest",
    "OrgsRemoveOutsideCollaboratorRequest",
    "OrgsRemovePublicMembershipForAuthenticatedUserRequest",
    "OrgsReviewPatGrantRequest",
    "OrgsReviewPatGrantRequestsInBulkRequest",
    "OrgsRevokeAllOrgRolesTeamRequest",
    "OrgsRevokeAllOrgRolesUserRequest",
    "OrgsRevokeOrgRoleTeamRequest",
    "OrgsRevokeOrgRoleUserRequest",
    "OrgsSetClusterDeploymentRecordsRequest",
    "OrgsSetMembershipForUserRequest",
    "OrgsSetPublicMembershipForAuthenticatedUserRequest",
    "OrgsUnblockUserRequest",
    "OrgsUpdateMembershipForAuthenticatedUserRequest",
    "OrgsUpdatePatAccessesRequest",
    "OrgsUpdatePatAccessRequest",
    "OrgsUpdateRequest",
    "OrgsUpdateWebhookConfigForOrgRequest",
    "OrgsUpdateWebhookRequest",
    "PackagesDeletePackageForAuthenticatedUserRequest",
    "PackagesDeletePackageForOrgRequest",
    "PackagesDeletePackageForUserRequest",
    "PackagesDeletePackageVersionForAuthenticatedUserRequest",
    "PackagesDeletePackageVersionForOrgRequest",
    "PackagesDeletePackageVersionForUserRequest",
    "PackagesGetAllPackageVersionsForPackageOwnedByAuthenticatedUserRequest",
    "PackagesGetAllPackageVersionsForPackageOwnedByOrgRequest",
    "PackagesGetAllPackageVersionsForPackageOwnedByUserRequest",
    "PackagesGetPackageForAuthenticatedUserRequest",
    "PackagesGetPackageForOrganizationRequest",
    "PackagesGetPackageForUserRequest",
    "PackagesGetPackageVersionForAuthenticatedUserRequest",
    "PackagesGetPackageVersionForOrganizationRequest",
    "PackagesGetPackageVersionForUserRequest",
    "PackagesListDockerMigrationConflictingPackagesForOrganizationRequest",
    "PackagesListPackagesForAuthenticatedUserRequest",
    "PackagesListPackagesForOrganizationRequest",
    "PackagesListPackagesForUserRequest",
    "PackagesRestorePackageForAuthenticatedUserRequest",
    "PackagesRestorePackageForOrgRequest",
    "PackagesRestorePackageForUserRequest",
    "PackagesRestorePackageVersionForAuthenticatedUserRequest",
    "PackagesRestorePackageVersionForOrgRequest",
    "PackagesRestorePackageVersionForUserRequest",
    "PrivateRegistriesCreateOrgPrivateRegistryRequest",
    "PrivateRegistriesDeleteOrgPrivateRegistryRequest",
    "PrivateRegistriesGetOrgPrivateRegistryRequest",
    "PrivateRegistriesGetOrgPublicKeyRequest",
    "PrivateRegistriesListOrgPrivateRegistriesRequest",
    "PrivateRegistriesUpdateOrgPrivateRegistryRequest",
    "ProjectsAddFieldForOrgRequest",
    "ProjectsAddFieldForUserRequest",
    "ProjectsAddItemForOrgRequest",
    "ProjectsAddItemForUserRequest",
    "ProjectsCreateDraftItemForAuthenticatedUserRequest",
    "ProjectsCreateDraftItemForOrgRequest",
    "ProjectsCreateViewForOrgRequest",
    "ProjectsCreateViewForUserRequest",
    "ProjectsDeleteItemForOrgRequest",
    "ProjectsDeleteItemForUserRequest",
    "ProjectsGetFieldForOrgRequest",
    "ProjectsGetFieldForUserRequest",
    "ProjectsGetForOrgRequest",
    "ProjectsGetForUserRequest",
    "ProjectsGetOrgItemRequest",
    "ProjectsGetUserItemRequest",
    "ProjectsListFieldsForOrgRequest",
    "ProjectsListFieldsForUserRequest",
    "ProjectsListForOrgRequest",
    "ProjectsListForUserRequest",
    "ProjectsListItemsForOrgRequest",
    "ProjectsListItemsForUserRequest",
    "ProjectsListViewItemsForOrgRequest",
    "ProjectsListViewItemsForUserRequest",
    "ProjectsUpdateItemForOrgRequest",
    "ProjectsUpdateItemForUserRequest",
    "PullsCheckIfMergedRequest",
    "PullsCreateReplyForReviewCommentRequest",
    "PullsCreateRequest",
    "PullsCreateReviewCommentRequest",
    "PullsCreateReviewRequest",
    "PullsDeletePendingReviewRequest",
    "PullsDeleteReviewCommentRequest",
    "PullsDismissReviewRequest",
    "PullsGetRequest",
    "PullsGetReviewCommentRequest",
    "PullsGetReviewRequest",
    "PullsListCommentsForReviewRequest",
    "PullsListCommitsRequest",
    "PullsListFilesRequest",
    "PullsListRequest",
    "PullsListRequestedReviewersRequest",
    "PullsListReviewCommentsForRepoRequest",
    "PullsListReviewCommentsRequest",
    "PullsListReviewsRequest",
    "PullsMergeRequest",
    "PullsRemoveRequestedReviewersRequest",
    "PullsRequestReviewersRequest",
    "PullsSubmitReviewRequest",
    "PullsUpdateBranchRequest",
    "PullsUpdateRequest",
    "PullsUpdateReviewCommentRequest",
    "PullsUpdateReviewRequest",
    "ReactionsCreateForCommitCommentRequest",
    "ReactionsCreateForIssueCommentRequest",
    "ReactionsCreateForIssueRequest",
    "ReactionsCreateForPullRequestReviewCommentRequest",
    "ReactionsCreateForReleaseRequest",
    "ReactionsDeleteForCommitCommentRequest",
    "ReactionsDeleteForIssueCommentRequest",
    "ReactionsDeleteForIssueRequest",
    "ReactionsDeleteForPullRequestCommentRequest",
    "ReactionsDeleteForReleaseRequest",
    "ReactionsListForCommitCommentRequest",
    "ReactionsListForIssueCommentRequest",
    "ReactionsListForIssueRequest",
    "ReactionsListForPullRequestReviewCommentRequest",
    "ReactionsListForReleaseRequest",
    "ReposAcceptInvitationForAuthenticatedUserRequest",
    "ReposAddCollaboratorRequest",
    "ReposAddTeamAccessRestrictionsRequest",
    "ReposAddUserAccessRestrictionsRequest",
    "ReposCancelPagesDeploymentRequest",
    "ReposCheckAutomatedSecurityFixesRequest",
    "ReposCheckCollaboratorRequest",
    "ReposCheckImmutableReleasesRequest",
    "ReposCheckPrivateVulnerabilityReportingRequest",
    "ReposCheckVulnerabilityAlertsRequest",
    "ReposCodeownersErrorsRequest",
    "ReposCompareCommitsRequest",
    "ReposCreateAttestationRequest",
    "ReposCreateAutolinkRequest",
    "ReposCreateCommitCommentRequest",
    "ReposCreateCommitStatusRequest",
    "ReposCreateDeployKeyRequest",
    "ReposCreateDeploymentBranchPolicyRequest",
    "ReposCreateDeploymentRequest",
    "ReposCreateDeploymentStatusRequest",
    "ReposCreateForAuthenticatedUserRequest",
    "ReposCreateForkRequest",
    "ReposCreateInOrgRequest",
    "ReposCreateOrUpdateEnvironmentRequest",
    "ReposCreateOrUpdateFileContentsRequest",
    "ReposCreatePagesDeploymentRequest",
    "ReposCreatePagesSiteRequest",
    "ReposCreateReleaseRequest",
    "ReposCreateUsingTemplateRequest",
    "ReposCreateWebhookRequest",
    "ReposCustomPropertiesForReposCreateOrUpdateRepositoryValuesRequest",
    "ReposCustomPropertiesForReposGetRepositoryValuesRequest",
    "ReposDeclineInvitationForAuthenticatedUserRequest",
    "ReposDeleteAccessRestrictionsRequest",
    "ReposDeleteAdminBranchProtectionRequest",
    "ReposDeleteAnEnvironmentRequest",
    "ReposDeleteAutolinkRequest",
    "ReposDeleteBranchProtectionRequest",
    "ReposDeleteCommitCommentRequest",
    "ReposDeleteCommitSignatureProtectionRequest",
    "ReposDeleteDeployKeyRequest",
    "ReposDeleteDeploymentBranchPolicyRequest",
    "ReposDeleteDeploymentRequest",
    "ReposDeleteFileRequest",
    "ReposDeleteInvitationRequest",
    "ReposDeleteOrgRulesetRequest",
    "ReposDeletePagesSiteRequest",
    "ReposDeleteReleaseAssetRequest",
    "ReposDeleteReleaseRequest",
    "ReposDeleteRequest",
    "ReposDeleteWebhookRequest",
    "ReposDisableAutomatedSecurityFixesRequest",
    "ReposDisableDeploymentProtectionRuleRequest",
    "ReposDisableVulnerabilityAlertsRequest",
    "ReposDownloadTarballArchiveRequest",
    "ReposDownloadZipballArchiveRequest",
    "ReposEnableAutomatedSecurityFixesRequest",
    "ReposEnableVulnerabilityAlertsRequest",
    "ReposGenerateReleaseNotesRequest",
    "ReposGetAccessRestrictionsRequest",
    "ReposGetAdminBranchProtectionRequest",
    "ReposGetAllDeploymentProtectionRulesRequest",
    "ReposGetAllEnvironmentsRequest",
    "ReposGetAllStatusCheckContextsRequest",
    "ReposGetAllTopicsRequest",
    "ReposGetAppsWithAccessToProtectedBranchRequest",
    "ReposGetAutolinkRequest",
    "ReposGetBranchProtectionRequest",
    "ReposGetBranchRequest",
    "ReposGetBranchRulesRequest",
    "ReposGetClonesRequest",
    "ReposGetCodeFrequencyStatsRequest",
    "ReposGetCollaboratorPermissionLevelRequest",
    "ReposGetCombinedStatusForRefRequest",
    "ReposGetCommitActivityStatsRequest",
    "ReposGetCommitCommentRequest",
    "ReposGetCommitRequest",
    "ReposGetCommitSignatureProtectionRequest",
    "ReposGetCommunityProfileMetricsRequest",
    "ReposGetContentRequest",
    "ReposGetContributorsStatsRequest",
    "ReposGetCustomDeploymentProtectionRuleRequest",
    "ReposGetDeployKeyRequest",
    "ReposGetDeploymentBranchPolicyRequest",
    "ReposGetDeploymentRequest",
    "ReposGetDeploymentStatusRequest",
    "ReposGetEnvironmentRequest",
    "ReposGetLatestPagesBuildRequest",
    "ReposGetLatestReleaseRequest",
    "ReposGetOrgRulesetRequest",
    "ReposGetOrgRulesetsRequest",
    "ReposGetOrgRuleSuiteRequest",
    "ReposGetOrgRuleSuitesRequest",
    "ReposGetPagesBuildRequest",
    "ReposGetPagesDeploymentRequest",
    "ReposGetPagesRequest",
    "ReposGetParticipationStatsRequest",
    "ReposGetPunchCardStatsRequest",
    "ReposGetReadmeInDirectoryRequest",
    "ReposGetReadmeRequest",
    "ReposGetReleaseAssetRequest",
    "ReposGetReleaseByTagRequest",
    "ReposGetReleaseRequest",
    "ReposGetRepoRulesetHistoryRequest",
    "ReposGetRepoRulesetRequest",
    "ReposGetRepoRulesetVersionRequest",
    "ReposGetRepoRuleSuiteRequest",
    "ReposGetRepoRuleSuitesRequest",
    "ReposGetRequest",
    "ReposGetStatusChecksProtectionRequest",
    "ReposGetTeamsWithAccessToProtectedBranchRequest",
    "ReposGetTopPathsRequest",
    "ReposGetUsersWithAccessToProtectedBranchRequest",
    "ReposGetViewsRequest",
    "ReposGetWebhookConfigForRepoRequest",
    "ReposGetWebhookDeliveryRequest",
    "ReposGetWebhookRequest",
    "ReposListActivitiesRequest",
    "ReposListAttestationsRequest",
    "ReposListAutolinksRequest",
    "ReposListBranchesForHeadCommitRequest",
    "ReposListBranchesRequest",
    "ReposListCollaboratorsRequest",
    "ReposListCommentsForCommitRequest",
    "ReposListCommitCommentsForRepoRequest",
    "ReposListCommitsRequest",
    "ReposListCommitStatusesForRefRequest",
    "ReposListContributorsRequest",
    "ReposListCustomDeploymentRuleIntegrationsRequest",
    "ReposListDeployKeysRequest",
    "ReposListDeploymentBranchPoliciesRequest",
    "ReposListDeploymentsRequest",
    "ReposListDeploymentStatusesRequest",
    "ReposListForAuthenticatedUserRequest",
    "ReposListForksRequest",
    "ReposListForOrgRequest",
    "ReposListForUserRequest",
    "ReposListInvitationsRequest",
    "ReposListLanguagesRequest",
    "ReposListPagesBuildsRequest",
    "ReposListPublicRequest",
    "ReposListPullRequestsAssociatedWithCommitRequest",
    "ReposListReleaseAssetsRequest",
    "ReposListReleasesRequest",
    "ReposListTagsRequest",
    "ReposListTeamsRequest",
    "ReposListWebhookDeliveriesRequest",
    "ReposListWebhooksRequest",
    "ReposMergeRequest",
    "ReposMergeUpstreamRequest",
    "ReposPingWebhookRequest",
    "ReposRedeliverWebhookDeliveryRequest",
    "ReposRemoveAppAccessRestrictionsRequest",
    "ReposRemoveCollaboratorRequest",
    "ReposRemoveStatusCheckContextsRequest",
    "ReposRemoveStatusCheckProtectionRequest",
    "ReposRemoveTeamAccessRestrictionsRequest",
    "ReposRemoveUserAccessRestrictionsRequest",
    "ReposRenameBranchRequest",
    "ReposReplaceAllTopicsRequest",
    "ReposRequestPagesBuildRequest",
    "ReposSetAdminBranchProtectionRequest",
    "ReposSetAppAccessRestrictionsRequest",
    "ReposSetTeamAccessRestrictionsRequest",
    "ReposTestPushWebhookRequest",
    "ReposTransferRequest",
    "ReposUpdateBranchProtectionRequest",
    "ReposUpdateCommitCommentRequest",
    "ReposUpdateDeploymentBranchPolicyRequest",
    "ReposUpdateInformationAboutPagesSiteRequest",
    "ReposUpdateInvitationRequest",
    "ReposUpdateReleaseAssetRequest",
    "ReposUpdateReleaseRequest",
    "ReposUpdateRequest",
    "ReposUpdateWebhookConfigForRepoRequest",
    "ReposUpdateWebhookRequest",
    "ReposUploadReleaseAssetRequest",
    "SearchCodeRequest",
    "SearchCommitsRequest",
    "SearchIssuesAndPullRequestsRequest",
    "SearchLabelsRequest",
    "SearchReposRequest",
    "SearchTopicsRequest",
    "SearchUsersRequest",
    "SecretScanningCreatePushProtectionBypassRequest",
    "SecretScanningGetAlertRequest",
    "SecretScanningGetScanHistoryRequest",
    "SecretScanningListAlertsForOrgRequest",
    "SecretScanningListAlertsForRepoRequest",
    "SecretScanningListLocationsForAlertRequest",
    "SecretScanningListOrgPatternConfigsRequest",
    "SecretScanningUpdateAlertRequest",
    "SecurityAdvisoriesCreateForkRequest",
    "SecurityAdvisoriesCreatePrivateVulnerabilityReportRequest",
    "SecurityAdvisoriesCreateRepositoryAdvisoryCveRequest",
    "SecurityAdvisoriesCreateRepositoryAdvisoryRequest",
    "SecurityAdvisoriesGetRepositoryAdvisoryRequest",
    "SecurityAdvisoriesListGlobalAdvisoriesRequest",
    "SecurityAdvisoriesListOrgRepositoryAdvisoriesRequest",
    "SecurityAdvisoriesListRepositoryAdvisoriesRequest",
    "SecurityAdvisoriesUpdateRepositoryAdvisoryRequest",
    "TeamsAddOrUpdateMembershipForUserInOrgRequest",
    "TeamsAddOrUpdateRepoPermissionsInOrgRequest",
    "TeamsCheckPermissionsForRepoInOrgRequest",
    "TeamsCreateRequest",
    "TeamsDeleteInOrgRequest",
    "TeamsGetByNameRequest",
    "TeamsGetMembershipForUserInOrgRequest",
    "TeamsListChildInOrgRequest",
    "TeamsListMembersInOrgRequest",
    "TeamsListPendingInvitationsInOrgRequest",
    "TeamsListReposInOrgRequest",
    "TeamsListRequest",
    "TeamsRemoveMembershipForUserInOrgRequest",
    "TeamsRemoveRepoInOrgRequest",
    "TeamsUpdateInOrgRequest",
    "UsersAddEmailForAuthenticatedUserRequest",
    "UsersAddSocialAccountForAuthenticatedUserRequest",
    "UsersBlockRequest",
    "UsersCheckBlockedRequest",
    "UsersCheckFollowingForUserRequest",
    "UsersCheckPersonIsFollowedByAuthenticatedRequest",
    "UsersCreateGpgKeyForAuthenticatedUserRequest",
    "UsersCreatePublicSshKeyForAuthenticatedUserRequest",
    "UsersDeleteAttestationsBulkRequest",
    "UsersDeleteAttestationsByIdRequest",
    "UsersDeleteAttestationsBySubjectDigestRequest",
    "UsersDeleteEmailForAuthenticatedUserRequest",
    "UsersDeleteGpgKeyForAuthenticatedUserRequest",
    "UsersDeletePublicSshKeyForAuthenticatedUserRequest",
    "UsersDeleteSocialAccountForAuthenticatedUserRequest",
    "UsersFollowRequest",
    "UsersGetByIdRequest",
    "UsersGetByUsernameRequest",
    "UsersGetContextForUserRequest",
    "UsersGetGpgKeyForAuthenticatedUserRequest",
    "UsersGetPublicSshKeyForAuthenticatedUserRequest",
    "UsersListAttestationsBulkRequest",
    "UsersListAttestationsRequest",
    "UsersListFollowersForUserRequest",
    "UsersListFollowingForUserRequest",
    "UsersListGpgKeysForUserRequest",
    "UsersListPublicKeysForUserRequest",
    "UsersListRequest",
    "UsersListSocialAccountsForUserRequest",
    "UsersListSshSigningKeysForUserRequest",
    "UsersSetPrimaryEmailVisibilityForAuthenticatedUserRequest",
    "UsersUnblockRequest",
    "UsersUnfollowRequest",
    "UsersUpdateAuthenticatedRequest",
    "AppPermissions",
    "CampaignsCreateCampaignBodyCodeScanningAlertsItem",
    "ChecksCreateBodyV0",
    "ChecksCreateBodyV1",
    "ChecksUpdateBodyV0",
    "ChecksUpdateBodyV1",
    "CodeSecurityUpdateConfigurationBodySecretScanningDelegatedBypassOptionsReviewersItem",
    "CodespacesCreateForAuthenticatedUserBodyV0",
    "CodespacesCreateForAuthenticatedUserBodyV1",
    "CustomPropertyValue",
    "GistsCreateBodyFilesValue",
    "GistsUpdateBodyFilesValue",
    "GitCreateTreeBodyTreeItem",
    "IssuesAddIssueFieldValuesBodyIssueFieldValuesItem",
    "IssuesAddLabelsBodyV0",
    "IssuesAddLabelsBodyV2Item",
    "IssuesCreateBodyLabelsItem",
    "IssuesSetIssueFieldValuesBodyIssueFieldValuesItem",
    "IssuesSetLabelsBody",
    "IssuesUpdateBodyIssueFieldValuesItem",
    "IssuesUpdateBodyLabelsItem",
    "Manifest",
    "OrgsCreateIssueFieldBodyOptionsItem",
    "OrgsDeleteAttestationsBulkBodyV0",
    "OrgsDeleteAttestationsBulkBodyV1",
    "OrgsSetClusterDeploymentRecordsBodyDeploymentsItem",
    "ProjectsAddFieldForOrgBodyV0",
    "ProjectsAddFieldForOrgBodyV1",
    "ProjectsAddFieldForOrgBodyV2",
    "ProjectsAddFieldForOrgBodyV3",
    "ProjectsAddFieldForUserBodyIterationConfiguration",
    "ProjectsUpdateItemForOrgBodyFieldsItem",
    "ProjectsUpdateItemForUserBodyFieldsItem",
    "ReposAddTeamAccessRestrictionsBodyV0",
    "ReposCreateOrUpdateEnvironmentBodyReviewersItem",
    "ReposRemoveStatusCheckContextsBodyV0",
    "ReposRemoveTeamAccessRestrictionsBodyV0",
    "ReposSetTeamAccessRestrictionsBodyV0",
    "ReposUpdateBodySecurityAndAnalysisSecretScanningDelegatedBypassOptionsReviewersItem",
    "ReposUpdateBranchProtectionBodyRequiredStatusChecksChecksItem",
    "SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItem",
    "SecurityAdvisoriesCreateRepositoryAdvisoryBodyCreditsItem",
    "SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItem",
    "SecurityAdvisoriesUpdateRepositoryAdvisoryBodyCreditsItem",
    "SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItem",
    "UsersAddEmailForAuthenticatedUserBody",
    "UsersDeleteAttestationsBulkBodyV0",
    "UsersDeleteAttestationsBulkBodyV1",
    "UsersDeleteEmailForAuthenticatedUserBody",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_advisories
class SecurityAdvisoriesListGlobalAdvisoriesRequestQuery(StrictModel):
    ghsa_id: str | None = Field(default=None, description="Filter results to a specific GitHub Security Advisory (GHSA) identifier.")
    type_: Literal["reviewed", "malware", "unreviewed"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results by advisory type. Reviewed advisories are returned by default; use 'malware' to include malware advisories or 'unreviewed' for community-contributed advisories.")
    cve_id: str | None = Field(default=None, description="Filter results to a specific Common Vulnerabilities and Exposures (CVE) identifier.")
    ecosystem: Literal["rubygems", "npm", "pip", "maven", "nuget", "composer", "go", "rust", "erlang", "actions", "pub", "other", "swift"] | None = Field(default=None, description="Filter results to advisories affecting specific package ecosystems.")
    cwes: str | list[str] | None = Field(default=None, description="Filter results to advisories with specific Common Weakness Enumeration (CWE) identifiers. Accepts comma-separated values or array format.")
    is_withdrawn: bool | None = Field(default=None, description="Filter results to only withdrawn advisories when set to true.")
    affects: str | list[str] | None = Field(default=None, description="Filter results to advisories affecting specific packages, optionally with version constraints. Accepts comma-separated values or array format. Maximum 1000 packages per request; use package name alone or package@version format.")
    modified: str | None = Field(default=None, description="Filter results to advisories updated or published within a specified date or date range using GitHub search syntax.")
    epss_percentage: str | None = Field(default=None, description="Filter results to advisories with an Exploit Prediction Scoring System (EPSS) percentage score matching the specified value, representing the likelihood of exploitation.")
    epss_percentile: str | None = Field(default=None, description="Filter results to advisories with an EPSS percentile score matching the specified value, representing the relative rank of exploitation likelihood compared to other CVEs.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order.")
class SecurityAdvisoriesListGlobalAdvisoriesRequest(StrictModel):
    """Retrieve global security advisories filtered by various criteria such as identifier, type, ecosystem, and vulnerability metrics. By default, returns only GitHub-reviewed advisories excluding malware."""
    query: SecurityAdvisoriesListGlobalAdvisoriesRequestQuery | None = None

# Operation: get_webhook_delivery_app
class AppsGetWebhookDeliveryRequestPath(StrictModel):
    delivery_id: str = Field(default=..., description="The unique identifier of the webhook delivery to retrieve.", json_schema_extra={'format': 'int64'})
class AppsGetWebhookDeliveryRequest(StrictModel):
    """Retrieve a specific webhook delivery record for a GitHub App. Requires JWT authentication as the GitHub App."""
    path: AppsGetWebhookDeliveryRequestPath

# Operation: redeliver_webhook_delivery_app
class AppsRedeliverWebhookDeliveryRequestPath(StrictModel):
    delivery_id: str = Field(default=..., description="The unique identifier of the webhook delivery attempt to redeliver.", json_schema_extra={'format': 'int64'})
class AppsRedeliverWebhookDeliveryRequest(StrictModel):
    """Redeliver a previously failed webhook delivery for a GitHub App. Requires JWT authentication as a GitHub App."""
    path: AppsRedeliverWebhookDeliveryRequestPath

# Operation: list_app_installations
class AppsListInstallationsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Filter results to show only installations updated after the specified timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class AppsListInstallationsRequest(StrictModel):
    """Retrieve all installations of the authenticated GitHub App, including their assigned permissions. Requires JWT authentication as the GitHub App."""
    query: AppsListInstallationsRequestQuery | None = None

# Operation: get_app_installation
class AppsGetInstallationRequestPath(StrictModel):
    installation_id: int = Field(default=..., description="The unique identifier of the GitHub App installation to retrieve.", examples=[1])
class AppsGetInstallationRequest(StrictModel):
    """Retrieve installation details for an authenticated GitHub App using the installation ID. Requires JWT authentication."""
    path: AppsGetInstallationRequestPath

# Operation: uninstall_app
class AppsDeleteInstallationRequestPath(StrictModel):
    installation_id: int = Field(default=..., description="The unique identifier of the app installation to uninstall.", examples=[1])
class AppsDeleteInstallationRequest(StrictModel):
    """Uninstall a GitHub App from a user, organization, or enterprise account. Requires JWT authentication as the GitHub App."""
    path: AppsDeleteInstallationRequestPath

# Operation: suspend_app_installation
class AppsSuspendInstallationRequestPath(StrictModel):
    installation_id: int = Field(default=..., description="The unique identifier of the app installation to suspend.", examples=[1])
class AppsSuspendInstallationRequest(StrictModel):
    """Suspend a GitHub App installation on a user, organization, or enterprise account, blocking the app from accessing that account's resources and API/webhook events. Requires JWT authentication as the GitHub App."""
    path: AppsSuspendInstallationRequestPath

# Operation: unsuspend_app_installation
class AppsUnsuspendInstallationRequestPath(StrictModel):
    installation_id: int = Field(default=..., description="The unique identifier of the GitHub App installation to unsuspend.", examples=[1])
class AppsUnsuspendInstallationRequest(StrictModel):
    """Removes a suspension on a GitHub App installation, allowing it to resume normal operation. Requires JWT authentication as a GitHub App."""
    path: AppsUnsuspendInstallationRequestPath

# Operation: revoke_app_authorization
class AppsDeleteAuthorizationRequestPath(StrictModel):
    client_id: str = Field(default=..., description="The client ID of the GitHub application whose authorization should be revoked.", examples=['Iv1.8a61f9b3a7aba766'])
class AppsDeleteAuthorizationRequestBody(StrictModel):
    access_token: str = Field(default=..., description="The OAuth access token for the user whose authorization is being revoked. The grant associated with this token's owner will be deleted.")
class AppsDeleteAuthorizationRequest(StrictModel):
    """Revoke an OAuth or GitHub application's authorization for a specific user. This permanently deletes the application grant and all associated OAuth tokens, removing the application's access to the user's account."""
    path: AppsDeleteAuthorizationRequestPath
    body: AppsDeleteAuthorizationRequestBody

# Operation: revoke_application_token
class AppsDeleteTokenRequestPath(StrictModel):
    client_id: str = Field(default=..., description="The client ID of the GitHub application whose token should be revoked.", examples=['Iv1.8a61f9b3a7aba766'])
class AppsDeleteTokenRequestBody(StrictModel):
    access_token: str = Field(default=..., description="The OAuth access token to be revoked. This token must be valid and associated with the specified application.")
class AppsDeleteTokenRequest(StrictModel):
    """Revoke a single OAuth access token for a GitHub application. Only the application owner or the token holder can perform this action."""
    path: AppsDeleteTokenRequestPath
    body: AppsDeleteTokenRequestBody

# Operation: create_scoped_token
class AppsScopeTokenRequestPath(StrictModel):
    client_id: str = Field(default=..., description="The client ID of the GitHub App requesting the scoped token.", examples=['Iv1.8a61f9b3a7aba766'])
class AppsScopeTokenRequestBody(StrictModel):
    access_token: str = Field(default=..., description="The non-scoped user access token to exchange for a scoped token.")
    target_id: int | None = Field(default=None, description="The ID of the user or organization to scope the token to. Required unless target is specified.")
    permissions: AppPermissions | None = Field(default=None, description="GitHub App permissions to scope the token to. Each key is a permission scope (e.g. actions, contents, issues) with value 'read' or 'write'.")
class AppsScopeTokenRequest(StrictModel):
    """Create a repository-scoped and/or permission-scoped access token from an existing non-scoped user access token. Specify which repositories the token can access and which permissions are granted."""
    path: AppsScopeTokenRequestPath
    body: AppsScopeTokenRequestBody

# Operation: get_assignment
class ClassroomGetAnAssignmentRequestPath(StrictModel):
    assignment_id: int = Field(default=..., description="The unique identifier of the classroom assignment to retrieve.")
class ClassroomGetAnAssignmentRequest(StrictModel):
    """Retrieve a specific GitHub Classroom assignment by its ID. Only administrators of the classroom containing the assignment can access this operation."""
    path: ClassroomGetAnAssignmentRequestPath

# Operation: list_accepted_assignments
class ClassroomListAcceptedAssignmentsForAnAssignmentRequestPath(StrictModel):
    assignment_id: int = Field(default=..., description="The unique identifier of the classroom assignment for which to list accepted student repositories.")
class ClassroomListAcceptedAssignmentsForAnAssignmentRequest(StrictModel):
    """Retrieves all student assignment repositories created by accepting a GitHub Classroom assignment. Only accessible to administrators of the GitHub Classroom."""
    path: ClassroomListAcceptedAssignmentsForAnAssignmentRequestPath

# Operation: list_assignment_grades
class ClassroomGetAssignmentGradesRequestPath(StrictModel):
    assignment_id: int = Field(default=..., description="The unique identifier of the classroom assignment for which to retrieve grades.")
class ClassroomGetAssignmentGradesRequest(StrictModel):
    """Retrieve all grades for a GitHub Classroom assignment. Only accessible to administrators of the GitHub Classroom that owns the assignment."""
    path: ClassroomGetAssignmentGradesRequestPath

# Operation: get_classroom
class ClassroomGetAClassroomRequestPath(StrictModel):
    classroom_id: int = Field(default=..., description="The unique identifier of the classroom to retrieve.")
class ClassroomGetAClassroomRequest(StrictModel):
    """Retrieve a specific GitHub Classroom by ID. Only returns the classroom if the authenticated user is an administrator of that classroom."""
    path: ClassroomGetAClassroomRequestPath

# Operation: list_assignments
class ClassroomListAssignmentsForAClassroomRequestPath(StrictModel):
    classroom_id: int = Field(default=..., description="The unique identifier of the classroom for which to retrieve assignments.")
class ClassroomListAssignmentsForAClassroomRequest(StrictModel):
    """Retrieve all GitHub Classroom assignments for a specified classroom. Only administrators of the classroom can access this list."""
    path: ClassroomListAssignmentsForAClassroomRequestPath

# Operation: get_conduct_code
class CodesOfConductGetConductCodeRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier or key of the code of conduct to retrieve.")
class CodesOfConductGetConductCodeRequest(StrictModel):
    """Retrieve detailed information about a specific GitHub code of conduct. Use this to fetch the full content and metadata for a code of conduct by its unique identifier."""
    path: CodesOfConductGetConductCodeRequestPath

# Operation: get_enterprise_actions_cache_storage_limit
class ActionsGetActionsCacheStorageLimitForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the URL-friendly identifier used to reference the enterprise in API requests.")
class ActionsGetActionsCacheStorageLimitForEnterpriseRequest(StrictModel):
    """Retrieve the GitHub Actions cache storage limit for an enterprise. This limit applies to all organizations and repositories within the enterprise and cannot be exceeded by their individual cache storage configurations."""
    path: ActionsGetActionsCacheStorageLimitForEnterpriseRequestPath

# Operation: list_oidc_custom_property_inclusions
class OidcListOidcCustomPropertyInclusionsForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the URL-friendly identifier for the enterprise.")
class OidcListOidcCustomPropertyInclusionsForEnterpriseRequest(StrictModel):
    """Lists the repository custom properties that are included in OIDC tokens for repository actions within an enterprise. Requires admin:enterprise scope for authentication."""
    path: OidcListOidcCustomPropertyInclusionsForEnterpriseRequestPath

# Operation: add_oidc_custom_property
class OidcCreateOidcCustomPropertyInclusionForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise slug identifier (URL-friendly name) for which to configure the OIDC custom property inclusion.")
class OidcCreateOidcCustomPropertyInclusionForEnterpriseRequestBody(StrictModel):
    custom_property_name: str = Field(default=..., description="The name of the repository custom property to include in the OIDC token for repository actions.")
class OidcCreateOidcCustomPropertyInclusionForEnterpriseRequest(StrictModel):
    """Adds a repository custom property to be included in OIDC tokens issued for repository actions within an enterprise. Requires `admin:enterprise` scope."""
    path: OidcCreateOidcCustomPropertyInclusionForEnterpriseRequestPath
    body: OidcCreateOidcCustomPropertyInclusionForEnterpriseRequestBody

# Operation: list_code_security_configurations
class CodeSecurityGetConfigurationsForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the URL-friendly identifier for the enterprise.")
class CodeSecurityGetConfigurationsForEnterpriseRequest(StrictModel):
    """Lists all code security configurations available in an enterprise. The authenticated user must be an administrator of the enterprise to access this endpoint."""
    path: CodeSecurityGetConfigurationsForEnterpriseRequestPath

# Operation: list_enterprise_code_security_default_configurations
class CodeSecurityGetDefaultConfigurationsForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (lowercase with hyphens). This is the URL-friendly version of the enterprise name.")
class CodeSecurityGetDefaultConfigurationsForEnterpriseRequest(StrictModel):
    """Retrieves the default code security configurations for an enterprise. The authenticated user must be an administrator of the enterprise to access this endpoint."""
    path: CodeSecurityGetDefaultConfigurationsForEnterpriseRequestPath

# Operation: get_code_security_configuration_enterprise
class CodeSecurityGetSingleConfigurationForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (lowercase with hyphens).")
    configuration_id: int = Field(default=..., description="The unique numeric identifier of the code security configuration to retrieve.")
class CodeSecurityGetSingleConfigurationForEnterpriseRequest(StrictModel):
    """Retrieve a specific code security configuration for an enterprise. The authenticated user must be an enterprise administrator to access this endpoint."""
    path: CodeSecurityGetSingleConfigurationForEnterpriseRequestPath

# Operation: delete_code_security_configuration_enterprise
class CodeSecurityDeleteConfigurationForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the URL-friendly identifier for the enterprise.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to delete.")
class CodeSecurityDeleteConfigurationForEnterpriseRequest(StrictModel):
    """Deletes a code security configuration from an enterprise. Repositories attached to the configuration will retain their settings but will no longer be associated with the configuration."""
    path: CodeSecurityDeleteConfigurationForEnterpriseRequestPath

# Operation: attach_code_security_configuration
class CodeSecurityAttachEnterpriseConfigurationRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to attach.")
class CodeSecurityAttachEnterpriseConfigurationRequestBody(StrictModel):
    scope: Literal["all", "all_without_configurations"] = Field(default=..., description="The scope of repositories to attach the configuration to. Use 'all' to attach to all repositories, or 'all_without_configurations' to attach only to repositories not yet attached to any configuration.")
class CodeSecurityAttachEnterpriseConfigurationRequest(StrictModel):
    """Attach an enterprise code security configuration to repositories within the specified scope. Repositories already attached to a configuration will be re-attached to the provided configuration, with free features enabled if insufficient GHAS licenses are available."""
    path: CodeSecurityAttachEnterpriseConfigurationRequestPath
    body: CodeSecurityAttachEnterpriseConfigurationRequestBody

# Operation: list_code_security_configuration_repositories
class CodeSecurityGetRepositoriesForEnterpriseConfigurationRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the URL-friendly identifier for the enterprise.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration. This ID specifies which configuration's associated repositories to retrieve.")
class CodeSecurityGetRepositoriesForEnterpriseConfigurationRequest(StrictModel):
    """Lists all repositories associated with a specific enterprise code security configuration. The authenticated user must be an enterprise administrator to access this endpoint."""
    path: CodeSecurityGetRepositoriesForEnterpriseConfigurationRequestPath

# Operation: list_dependabot_alerts
class DependabotListAlertsForEnterpriseRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise slug identifier.")
class DependabotListAlertsForEnterpriseRequestQuery(StrictModel):
    state: str | None = Field(default=None, description="Filter alerts by state. Specify one or more comma-separated states to return only matching alerts.")
    ecosystem: str | None = Field(default=None, description="Filter alerts by package ecosystem. Specify one or more comma-separated ecosystems to return only matching alerts.")
    package: str | None = Field(default=None, description="Filter alerts by package name. Specify one or more comma-separated package names to return only matching alerts.")
    epss_percentage: str | None = Field(default=None, description="Filter alerts by CVE Exploit Prediction Scoring System (EPSS) percentage. Supports exact values, comparators (>, <, >=, <=), or ranges (n..n) where n is between 0.0 and 1.0.")
    has: str | list[Literal["patch"]] | None = Field(default=None, description="Filter alerts by presence of specific attributes. Currently supports 'patch' to filter for alerts with available patches. Multiple filters can be combined to match all criteria.")
    scope: Literal["development", "runtime"] | None = Field(default=None, description="Filter alerts by dependency scope within the project.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order.")
class DependabotListAlertsForEnterpriseRequest(StrictModel):
    """Lists Dependabot security alerts across repositories in an enterprise. Returns alerts only for organizations where you have owner or security manager permissions."""
    path: DependabotListAlertsForEnterpriseRequestPath
    query: DependabotListAlertsForEnterpriseRequestQuery | None = None

# Operation: list_teams_enterprise
class EnterpriseTeamsListRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (lowercase, hyphen-separated). This uniquely identifies the enterprise whose teams should be listed.")
class EnterpriseTeamsListRequest(StrictModel):
    """Retrieve all teams within an enterprise that the authenticated user has access to. This operation returns a complete list of teams for the specified enterprise."""
    path: EnterpriseTeamsListRequestPath

# Operation: create_enterprise_team
class EnterpriseTeamsCreateRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name that will contain the new team.")
class EnterpriseTeamsCreateRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the team to be created.")
    description: str | None = Field(default=None, description="An optional description providing details about the team's purpose or scope.")
    organization_selection_type: Literal["disabled", "selected", "all"] | None = Field(default=None, description="Specifies which organizations in the enterprise should have access to this team. Use 'disabled' to exclude the team from all organizations, 'selected' to assign it to specific organizations, or 'all' to assign it to all current and future organizations.")
    group_id: str | None = Field(default=None, description="The ID of the IdP group to assign team membership with. This enables automatic team membership provisioning through your identity provider.")
class EnterpriseTeamsCreateRequest(StrictModel):
    """Create a new team within an enterprise. The authenticated user must be an owner of the enterprise to perform this action."""
    path: EnterpriseTeamsCreateRequestPath
    body: EnterpriseTeamsCreateRequestBody

# Operation: list_enterprise_team_members
class EnterpriseTeamMembershipsListRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (URL-friendly lowercase name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format (URL-friendly lowercase name) or the numeric team ID.")
class EnterpriseTeamMembershipsListRequest(StrictModel):
    """Retrieves all members belonging to a specific enterprise team. Use this to view the complete roster of team members within an enterprise."""
    path: EnterpriseTeamMembershipsListRequestPath

# Operation: add_team_members
class EnterpriseTeamMembershipsBulkAddRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier as a slug (URL-friendly name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier as a slug or numeric ID.")
class EnterpriseTeamMembershipsBulkAddRequestBody(StrictModel):
    usernames: list[str] = Field(default=..., description="List of GitHub user handles to add to the team. Order is not significant. Each item should be a valid GitHub username.")
class EnterpriseTeamMembershipsBulkAddRequest(StrictModel):
    """Add multiple GitHub users to an enterprise team in bulk. Specify the enterprise and team by their slug identifiers, and provide a list of GitHub usernames to add."""
    path: EnterpriseTeamMembershipsBulkAddRequestPath
    body: EnterpriseTeamMembershipsBulkAddRequestBody

# Operation: remove_team_members
class EnterpriseTeamMembershipsBulkRemoveRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier as a URL-friendly slug (lowercase, hyphens allowed).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier as a URL-friendly slug or numeric team ID.")
class EnterpriseTeamMembershipsBulkRemoveRequestBody(StrictModel):
    usernames: list[str] = Field(default=..., description="Array of GitHub user handles to remove from the team. Order is not significant. Each username should be a valid GitHub account handle.")
class EnterpriseTeamMembershipsBulkRemoveRequest(StrictModel):
    """Remove multiple members from an enterprise team in a single operation. Specify the enterprise, team, and list of GitHub usernames to be removed."""
    path: EnterpriseTeamMembershipsBulkRemoveRequestPath
    body: EnterpriseTeamMembershipsBulkRemoveRequestBody

# Operation: check_enterprise_team_membership
class EnterpriseTeamMembershipsGetRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the URL-friendly identifier for the enterprise.")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The slug version of the enterprise team name, or alternatively the enterprise team ID. This uniquely identifies the team within the enterprise.")
    username: str = Field(default=..., description="The GitHub username (handle) of the user to check membership for.")
class EnterpriseTeamMembershipsGetRequest(StrictModel):
    """Check whether a user is a member of an enterprise team. Returns membership status for the specified user within the enterprise team."""
    path: EnterpriseTeamMembershipsGetRequestPath

# Operation: add_team_member
class EnterpriseTeamMembershipsAddRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug identifier for the enterprise organization.")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The slug identifier or numeric ID for the enterprise team.")
    username: str = Field(default=..., description="The GitHub username handle for the user to add to the team.")
class EnterpriseTeamMembershipsAddRequest(StrictModel):
    """Add a user to an enterprise team. The user will gain access to the team's resources and permissions within the enterprise."""
    path: EnterpriseTeamMembershipsAddRequestPath

# Operation: remove_team_member
class EnterpriseTeamMembershipsRemoveRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (lowercase with hyphens).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or numeric team ID.")
    username: str = Field(default=..., description="The GitHub username of the user whose team membership should be removed.")
class EnterpriseTeamMembershipsRemoveRequest(StrictModel):
    """Remove a user's membership from an enterprise team. This operation revokes the user's access to the team and its associated resources."""
    path: EnterpriseTeamMembershipsRemoveRequestPath

# Operation: list_organization_assignments
class EnterpriseTeamOrganizationsGetAssignmentsRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (URL-friendly name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or the numeric team ID.")
class EnterpriseTeamOrganizationsGetAssignmentsRequest(StrictModel):
    """Retrieve all organizations assigned to a specific enterprise team. Use this to view which organizations are linked to a team within an enterprise."""
    path: EnterpriseTeamOrganizationsGetAssignmentsRequestPath

# Operation: assign_team_to_organizations
class EnterpriseTeamOrganizationsBulkAddRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (URL-friendly name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or the numeric team ID.")
class EnterpriseTeamOrganizationsBulkAddRequestBody(StrictModel):
    organization_slugs: list[str] = Field(default=..., description="List of organization slugs to assign the team to. Each slug should be the URL-friendly identifier for the target organization.")
class EnterpriseTeamOrganizationsBulkAddRequest(StrictModel):
    """Assign an enterprise team to multiple organizations. This operation enables bulk assignment of a single team across multiple organizations within an enterprise."""
    path: EnterpriseTeamOrganizationsBulkAddRequestPath
    body: EnterpriseTeamOrganizationsBulkAddRequestBody

# Operation: unassign_team_from_organizations
class EnterpriseTeamOrganizationsBulkRemoveRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (URL-friendly name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or the numeric team ID.")
class EnterpriseTeamOrganizationsBulkRemoveRequestBody(StrictModel):
    organization_slugs: list[str] = Field(default=..., description="List of organization slugs to unassign the team from. Order is not significant. Each item should be the organization's slug identifier.")
class EnterpriseTeamOrganizationsBulkRemoveRequest(StrictModel):
    """Remove an enterprise team's assignments from multiple organizations. This operation unassigns the specified team from all provided organizations."""
    path: EnterpriseTeamOrganizationsBulkRemoveRequestPath
    body: EnterpriseTeamOrganizationsBulkRemoveRequestBody

# Operation: verify_team_organization_assignment
class EnterpriseTeamOrganizationsGetAssignmentRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (lowercase, hyphen-separated). This identifies the parent enterprise context.")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or UUID. Can be provided as either the team's slug name or its unique identifier.")
    org: str = Field(default=..., description="The organization name to check for team assignment. The lookup is case-insensitive.")
class EnterpriseTeamOrganizationsGetAssignmentRequest(StrictModel):
    """Verify whether an enterprise team is assigned to a specific organization. Use this to check team-organization relationships within your enterprise."""
    path: EnterpriseTeamOrganizationsGetAssignmentRequestPath

# Operation: assign_team_to_organization
class EnterpriseTeamOrganizationsAddRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (lowercase, hyphen-separated name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or numeric ID. The slug is the lowercase, hyphen-separated team name.")
    org: str = Field(default=..., description="The organization name to assign the team to. The name is case-insensitive.")
class EnterpriseTeamOrganizationsAddRequest(StrictModel):
    """Assign an enterprise team to an organization, enabling the team to access and manage resources within that organization."""
    path: EnterpriseTeamOrganizationsAddRequestPath

# Operation: unassign_team_from_organization
class EnterpriseTeamOrganizationsDeleteRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The enterprise identifier in slug format (URL-friendly name).")
    enterprise_team: str = Field(default=..., validation_alias="enterprise-team", serialization_alias="enterprise-team", description="The enterprise team identifier in slug format or the numeric team ID.")
    org: str = Field(default=..., description="The organization name to unassign the team from. The name is case-insensitive.")
class EnterpriseTeamOrganizationsDeleteRequest(StrictModel):
    """Remove an enterprise team's assignment from an organization. This operation unlinks the team from the specified organization within the enterprise."""
    path: EnterpriseTeamOrganizationsDeleteRequestPath

# Operation: get_enterprise_team
class EnterpriseTeamsGetRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name. This is the normalized identifier used in the enterprise URL.")
    team_slug: str = Field(default=..., description="The slug of the team name. GitHub generates this by normalizing the team name: converting to lowercase, replacing spaces with hyphens, removing special characters, and prefixing with 'ent:'.")
class EnterpriseTeamsGetRequest(StrictModel):
    """Retrieve a specific team within an enterprise using its slug identifier. The team slug is a normalized version of the team name with special characters removed, lowercase conversion, spaces replaced with hyphens, and prefixed with 'ent:'."""
    path: EnterpriseTeamsGetRequestPath

# Operation: update_enterprise_team
class EnterpriseTeamsUpdateRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug version of the enterprise name.")
    team_slug: str = Field(default=..., description="The slug of the team name.")
class EnterpriseTeamsUpdateRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A new description for the team.")
    organization_selection_type: Literal["disabled", "selected", "all"] | None = Field(default=None, description="Specifies which organizations in the enterprise should have access to this team. Use `disabled` to unassign from all organizations, `selected` to assign to specific organizations, or `all` to assign to all current and future organizations.")
    group_id: str | None = Field(default=None, description="The ID of the IdP group to assign team membership with. Replaces any existing IdP group assignment or direct members if the team is not currently linked to an IdP group.")
class EnterpriseTeamsUpdateRequest(StrictModel):
    """Update an enterprise team's configuration including description, organization access scope, and IdP group assignment. Requires enterprise owner authentication."""
    path: EnterpriseTeamsUpdateRequestPath
    body: EnterpriseTeamsUpdateRequestBody | None = None

# Operation: delete_enterprise_team
class EnterpriseTeamsDeleteRequestPath(StrictModel):
    enterprise: str = Field(default=..., description="The slug identifier for the enterprise containing the team to be deleted.")
    team_slug: str = Field(default=..., description="The slug identifier for the team to be deleted.")
class EnterpriseTeamsDeleteRequest(StrictModel):
    """Delete an enterprise team and all associated IdP mappings. The authenticated user must be an enterprise owner to perform this action."""
    path: EnterpriseTeamsDeleteRequestPath

# Operation: list_gists
class GistsListRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Filter results to show only gists last updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class GistsListRequest(StrictModel):
    """Retrieve gists for the authenticated user, or all public gists if called anonymously. Results can be filtered by last update time."""
    query: GistsListRequestQuery | None = None

# Operation: create_gist
class GistsCreateRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A brief description of the gist's purpose or content.")
    files: dict[str, GistsCreateBodyFilesValue] = Field(default=..., description="An object mapping file names to their content. Each file must have a unique name and contain the file content as a string.")
    public: str | None = Field(default=None, description="Whether the gist should be publicly accessible. Accepts boolean values or string representations of boolean values.")
class GistsCreateRequest(StrictModel):
    """Create a new gist with one or more files. A gist is a simple way to share code snippets and text with others."""
    body: GistsCreateRequestBody

# Operation: list_public_gists
class GistsListPublicRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Filter results to show only gists updated after the specified timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class GistsListPublicRequest(StrictModel):
    """Retrieve a list of public gists sorted by most recently updated first. Supports pagination to fetch up to 3000 gists total."""
    query: GistsListPublicRequestQuery | None = None

# Operation: list_starred_gists
class GistsListStarredRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Filter results to show only gists last updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class GistsListStarredRequest(StrictModel):
    """Retrieve all gists starred by the authenticated user. Results can be filtered to show only gists updated after a specified timestamp."""
    query: GistsListStarredRequestQuery | None = None

# Operation: get_gist
class GistsGetRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to retrieve.")
class GistsGetRequest(StrictModel):
    """Retrieve a specific gist by its unique identifier. Supports multiple response formats including raw markdown and base64-encoded content."""
    path: GistsGetRequestPath

# Operation: update_gist
class GistsUpdateRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to update.")
class GistsUpdateRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A new description for the gist.")
    files: dict[str, GistsUpdateBodyFilesValue] | None = Field(default=None, description="A mapping of gist files to update, rename, or delete. Each key must match the current filename including extension. To delete a file, set its value to null. To rename a file, include a new filename in the file object. Files not included in this object remain unchanged.")
class GistsUpdateRequest(StrictModel):
    """Update a gist's description and manage its files by updating content, renaming, or deleting files. At least one of description or files must be provided."""
    path: GistsUpdateRequestPath
    body: GistsUpdateRequestBody | None = None

# Operation: delete_gist
class GistsDeleteRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to delete.")
class GistsDeleteRequest(StrictModel):
    """Permanently delete a gist by its unique identifier. This action cannot be undone."""
    path: GistsDeleteRequestPath

# Operation: list_gist_comments
class GistsListCommentsRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist for which to retrieve comments.")
class GistsListCommentsRequest(StrictModel):
    """Retrieves all comments posted on a specific gist. Supports multiple response formats including raw markdown and base64-encoded content."""
    path: GistsListCommentsRequestPath

# Operation: create_gist_comment
class GistsCreateCommentRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to comment on.")
class GistsCreateCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The comment text content. Supports markdown formatting.", max_length=65535)
class GistsCreateCommentRequest(StrictModel):
    """Add a comment to a gist. The comment text supports markdown formatting and can be up to 65,535 characters."""
    path: GistsCreateCommentRequestPath
    body: GistsCreateCommentRequestBody

# Operation: get_gist_comment
class GistsGetCommentRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist containing the comment.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to retrieve.", json_schema_extra={'format': 'int64'})
class GistsGetCommentRequest(StrictModel):
    """Retrieve a specific comment from a gist. Supports multiple media types including raw markdown and base64-encoded content for handling special characters."""
    path: GistsGetCommentRequestPath

# Operation: update_gist_comment
class GistsUpdateCommentRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist containing the comment to update.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to update.", json_schema_extra={'format': 'int64'})
class GistsUpdateCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The updated comment text. Supports markdown formatting and can be up to 65,535 characters.", max_length=65535)
class GistsUpdateCommentRequest(StrictModel):
    """Updates an existing comment on a gist. The comment text can be up to 65,535 characters and supports markdown formatting."""
    path: GistsUpdateCommentRequestPath
    body: GistsUpdateCommentRequestBody

# Operation: delete_gist_comment
class GistsDeleteCommentRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist containing the comment to delete.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to delete.", json_schema_extra={'format': 'int64'})
class GistsDeleteCommentRequest(StrictModel):
    """Delete a specific comment from a gist. The authenticated user must have permission to delete the comment."""
    path: GistsDeleteCommentRequestPath

# Operation: list_gist_commits
class GistsListCommitsRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist whose commit history you want to retrieve.")
class GistsListCommitsRequest(StrictModel):
    """Retrieve the commit history for a specific gist, showing all revisions and changes made to the gist over time."""
    path: GistsListCommitsRequestPath

# Operation: list_gist_forks
class GistsListForksRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist for which to retrieve forks.")
class GistsListForksRequest(StrictModel):
    """Retrieve a list of all forks created from a specific gist. This allows you to discover derivative versions and track how a gist has been adapted by other users."""
    path: GistsListForksRequestPath

# Operation: fork_gist
class GistsForkRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to fork.")
class GistsForkRequest(StrictModel):
    """Create a fork of an existing gist under your account. The forked gist will be an independent copy that you can modify without affecting the original."""
    path: GistsForkRequestPath

# Operation: check_gist_starred
class GistsCheckIsStarredRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to check for starred status.")
class GistsCheckIsStarredRequest(StrictModel):
    """Check whether a specific gist has been starred by the authenticated user. Returns a 204 status if starred, or 404 if not starred."""
    path: GistsCheckIsStarredRequestPath

# Operation: star_gist
class GistsStarRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to star.")
class GistsStarRequest(StrictModel):
    """Star a gist to save it for quick access. Requires setting the Content-Length header to zero."""
    path: GistsStarRequestPath

# Operation: remove_gist_star
class GistsUnstarRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to unstar.")
class GistsUnstarRequest(StrictModel):
    """Remove a star from a gist, indicating you no longer want to mark it as a favorite. This action is only available for gists you have previously starred."""
    path: GistsUnstarRequestPath

# Operation: get_gist_revision
class GistsGetRevisionRequestPath(StrictModel):
    gist_id: str = Field(default=..., description="The unique identifier of the gist to retrieve a revision from.")
    sha: str = Field(default=..., description="The commit SHA that identifies the specific revision of the gist to retrieve.")
class GistsGetRevisionRequest(StrictModel):
    """Retrieve a specific revision of a gist by its SHA identifier. Supports multiple media types including raw markdown and base64-encoded content for handling special characters."""
    path: GistsGetRevisionRequestPath

# Operation: get_gitignore_template
class GitignoreGetTemplateRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the gitignore template to retrieve (e.g., 'Python', 'Node', 'Java'). Template names are case-sensitive.")
class GitignoreGetTemplateRequest(StrictModel):
    """Retrieve the content of a gitignore template by name. Supports raw content retrieval via custom media type."""
    path: GitignoreGetTemplateRequestPath

# Operation: list_issues
class IssuesListRequestQuery(StrictModel):
    filter_: Literal["assigned", "created", "mentioned", "subscribed", "repos", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Specifies which category of issues to return. Use 'assigned' for issues assigned to you, 'created' for issues you created, 'mentioned' for issues mentioning you, 'subscribed' for issues you're subscribed to, or 'all'/'repos' for all visible issues.")
    state: Literal["open", "closed", "all"] | None = Field(default=None, description="Filters issues by their current state. Use 'open' for active issues, 'closed' for resolved issues, or 'all' to include both.")
    labels: str | None = Field(default=None, description="Filters issues by one or more labels. Provide label names as a comma-separated list to match issues with any of the specified labels.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Determines the sort order of results. Use 'asc' for ascending order or 'desc' for descending order.")
    since: str | None = Field(default=None, description="Returns only issues that were last updated after the specified timestamp. Provide the timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    collab: bool | None = Field(default=None, description="When enabled, includes issues from repositories where you are a collaborator.")
    orgs: bool | None = Field(default=None, description="When enabled, includes issues from organization repositories.")
    owned: bool | None = Field(default=None, description="When enabled, includes issues from repositories you own.")
    pulls: bool | None = Field(default=None, description="When enabled, includes pull requests in the results. Note that GitHub treats pull requests as issues in this endpoint.")
class IssuesListRequest(StrictModel):
    """Retrieve issues assigned to the authenticated user across all visible repositories, including owned, member, and organization repositories. Use the filter parameter to customize which issues are returned."""
    query: IssuesListRequestQuery | None = None

# Operation: list_licenses
class LicensesGetAllCommonlyUsedRequestQuery(StrictModel):
    featured: bool | None = Field(default=None, description="Filter results to show only featured licenses. When enabled, returns a curated subset of the most popular licenses.")
class LicensesGetAllCommonlyUsedRequest(StrictModel):
    """Retrieve the most commonly used open source licenses on GitHub. This helps developers quickly find and apply standard licenses to their repositories."""
    query: LicensesGetAllCommonlyUsedRequestQuery | None = None

# Operation: get_license
class LicensesGetRequestPath(StrictModel):
    license_: str = Field(default=..., validation_alias="license", serialization_alias="license", description="The license identifier or SPDX license identifier to retrieve information for.")
class LicensesGetRequest(StrictModel):
    """Retrieve detailed information about a specific open source license. This is useful for understanding license terms and requirements when licensing a repository."""
    path: LicensesGetRequestPath

# Operation: get_subscription_plan
class AppsGetSubscriptionPlanForAccountRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier of the user or organization account to retrieve subscription information for.")
class AppsGetSubscriptionPlanForAccountRequest(StrictModel):
    """Retrieve the active subscription plan for a user or organization account on a GitHub App marketplace listing. Returns current subscription status and any pending plan changes scheduled for the next billing cycle."""
    path: AppsGetSubscriptionPlanForAccountRequestPath

# Operation: get_subscription_plan_stubbed
class AppsGetSubscriptionPlanForAccountStubbedRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier of the account (user or organization) to check subscription status for.")
class AppsGetSubscriptionPlanForAccountStubbedRequest(StrictModel):
    """Retrieve the active subscription plan for a GitHub account. Returns the current subscription status and any pending plan changes scheduled for the next billing cycle."""
    path: AppsGetSubscriptionPlanForAccountStubbedRequestPath

# Operation: list_network_events
class ActivityListPublicEventsForRepoNetworkRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActivityListPublicEventsForRepoNetworkRequest(StrictModel):
    """List public events for a network of repositories. Note: This API is not built to serve real-time use cases; event latency can range from 30 seconds to 6 hours depending on the time of day."""
    path: ActivityListPublicEventsForRepoNetworkRequestPath

# Operation: list_notifications
class ActivityListNotificationsForAuthenticatedUserRequestQuery(StrictModel):
    all_: bool | None = Field(default=None, validation_alias="all", serialization_alias="all", description="Include notifications marked as read in the results. By default, only unread notifications are returned.")
    participating: bool | None = Field(default=None, description="Show only notifications where you are directly participating or mentioned, excluding notifications you're merely watching.")
    since: str | None = Field(default=None, description="Return only notifications last updated after this timestamp. Use ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class ActivityListNotificationsForAuthenticatedUserRequest(StrictModel):
    """Retrieve all notifications for the authenticated user, sorted by most recent update. Use filters to show only unread notifications or those where you're directly participating."""
    query: ActivityListNotificationsForAuthenticatedUserRequestQuery | None = None

# Operation: mark_notifications_as_read
class ActivityMarkNotificationsAsReadRequestBody(StrictModel):
    last_read_at: str | None = Field(default=None, description="Timestamp marking the last point notifications were checked. Notifications updated after this time will not be marked as read. Omit to mark all notifications as read. Use ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class ActivityMarkNotificationsAsReadRequest(StrictModel):
    """Mark all notifications as read for the authenticated user. For large notification volumes, returns a 202 status and processes asynchronously; use the list notifications endpoint with `all=false` to verify completion."""
    body: ActivityMarkNotificationsAsReadRequestBody | None = None

# Operation: get_notification_thread
class ActivityGetThreadRequestPath(StrictModel):
    thread_id: int = Field(default=..., description="The unique identifier of the notification thread to retrieve. This ID is returned in the `id` field when listing notifications.")
class ActivityGetThreadRequest(StrictModel):
    """Retrieve detailed information about a specific notification thread. Use the thread ID from notification list operations to fetch thread-specific data."""
    path: ActivityGetThreadRequestPath

# Operation: mark_notification_thread_as_read
class ActivityMarkThreadAsReadRequestPath(StrictModel):
    thread_id: int = Field(default=..., description="The unique identifier of the notification thread to mark as read. This ID corresponds to the `id` field returned when retrieving notifications.")
class ActivityMarkThreadAsReadRequest(StrictModel):
    """Mark a notification thread as read, equivalent to dismissing a notification in your GitHub notification inbox. This updates the thread's read status without deleting it."""
    path: ActivityMarkThreadAsReadRequestPath

# Operation: mark_notification_thread_as_done
class ActivityMarkThreadAsDoneRequestPath(StrictModel):
    thread_id: int = Field(default=..., description="The unique identifier of the notification thread to mark as done. This ID corresponds to the `id` field returned when retrieving notifications.")
class ActivityMarkThreadAsDoneRequest(StrictModel):
    """Mark a notification thread as done, equivalent to archiving a notification in your GitHub notification inbox. This removes the thread from your active notifications."""
    path: ActivityMarkThreadAsDoneRequestPath

# Operation: get_thread_subscription
class ActivityGetThreadSubscriptionForAuthenticatedUserRequestPath(StrictModel):
    thread_id: int = Field(default=..., description="The unique identifier of the notification thread to check subscription status for.")
class ActivityGetThreadSubscriptionForAuthenticatedUserRequest(StrictModel):
    """Retrieve the subscription status of the authenticated user for a specific notification thread. Returns subscription details if the user is subscribed (e.g., through participation, mentions, or manual subscription)."""
    path: ActivityGetThreadSubscriptionForAuthenticatedUserRequestPath

# Operation: configure_thread_notification
class ActivitySetThreadSubscriptionRequestPath(StrictModel):
    thread_id: int = Field(default=..., description="The unique identifier of the notification thread returned in the `id` field from notification list operations.")
class ActivitySetThreadSubscriptionRequestBody(StrictModel):
    ignored: bool | None = Field(default=None, description="Set to true to block all notifications from this thread, or false to receive notifications normally.")
class ActivitySetThreadSubscriptionRequest(StrictModel):
    """Configure notification settings for a specific thread. Use this to ignore future notifications, subscribe to threads you're not currently watching, or unsubscribe from previously ignored threads."""
    path: ActivitySetThreadSubscriptionRequestPath
    body: ActivitySetThreadSubscriptionRequestBody | None = None

# Operation: mute_thread_subscription
class ActivityDeleteThreadSubscriptionRequestPath(StrictModel):
    thread_id: int = Field(default=..., description="The unique identifier of the notification thread, obtained from the `id` field when retrieving notifications.")
class ActivityDeleteThreadSubscriptionRequest(StrictModel):
    """Mute all future notifications for a thread until you comment or receive an @mention. Repository watching settings remain unaffected by this operation."""
    path: ActivityDeleteThreadSubscriptionRequestPath

# Operation: list_organizations
class OrgsListRequestQuery(StrictModel):
    since: int | None = Field(default=None, description="Organization ID cursor for pagination. Returns only organizations with an ID greater than this value to fetch the next page of results.")
class OrgsListRequest(StrictModel):
    """Retrieve all organizations ordered by creation date. Pagination is cursor-based using the `since` parameter to fetch subsequent pages via Link headers."""
    query: OrgsListRequestQuery | None = None

# Operation: get_actions_cache_storage_limit
class ActionsGetActionsCacheStorageLimitForOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class ActionsGetActionsCacheStorageLimitForOrganizationRequest(StrictModel):
    """Retrieve the GitHub Actions cache storage limit for an organization. This limit applies to all repositories within the organization and cannot be exceeded by individual repository settings."""
    path: ActionsGetActionsCacheStorageLimitForOrganizationRequestPath

# Operation: list_dependabot_repository_access
class DependabotRepositoryAccessForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class DependabotRepositoryAccessForOrgRequest(StrictModel):
    """Lists repositories that Dependabot has been granted access to within an organization. This allows organization admins to view which repositories Dependabot can access when updating dependencies."""
    path: DependabotRepositoryAccessForOrgRequestPath

# Operation: update_dependabot_repository_access
class DependabotUpdateRepositoryAccessForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class DependabotUpdateRepositoryAccessForOrgRequestBody(StrictModel):
    repository_ids_to_add: list[int] | None = Field(default=None, description="List of repository IDs to grant Dependabot access to. Each ID should be a valid repository identifier for the organization.")
    repository_ids_to_remove: list[int] | None = Field(default=None, description="List of repository IDs to revoke Dependabot access from. Each ID should be a valid repository identifier currently in the access list.")
class DependabotUpdateRepositoryAccessForOrgRequest(StrictModel):
    """Updates Dependabot's repository access permissions for an organization by adding and removing repositories from its authorized list. This operation allows organization admins to control which repositories Dependabot can access when managing dependencies."""
    path: DependabotUpdateRepositoryAccessForOrgRequestPath
    body: DependabotUpdateRepositoryAccessForOrgRequestBody | None = None

# Operation: list_organization_budgets
class BillingGetAllBudgetsOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class BillingGetAllBudgetsOrgRequestQuery(StrictModel):
    scope: Literal["enterprise", "organization", "repository", "cost_center"] | None = Field(default=None, description="Filter budgets by their scope type to narrow results to a specific budget category.")
class BillingGetAllBudgetsOrgRequest(StrictModel):
    """Retrieve all budgets configured for an organization. The authenticated user must have organization admin or billing manager permissions. Results are paginated with up to 10 budgets per page."""
    path: BillingGetAllBudgetsOrgRequestPath
    query: BillingGetAllBudgetsOrgRequestQuery | None = None

# Operation: get_budget
class BillingGetBudgetOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    budget_id: str = Field(default=..., description="The unique identifier of the budget to retrieve.")
class BillingGetBudgetOrgRequest(StrictModel):
    """Retrieve a specific budget for an organization by its ID. The authenticated user must have organization admin or billing manager permissions."""
    path: BillingGetBudgetOrgRequestPath

# Operation: update_budget
class BillingUpdateBudgetOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    budget_id: str = Field(default=..., description="The unique identifier for the budget to update.")
class BillingUpdateBudgetOrgRequestBody(StrictModel):
    budget_amount: int | None = Field(default=None, description="The budget limit in whole dollars. For license-based products, this represents the number of licenses.")
    prevent_further_usage: bool | None = Field(default=None, description="Whether to block additional spending once the budget limit is exceeded.")
    budget_scope: Literal["enterprise", "organization", "repository", "cost_center"] | None = Field(default=None, description="The hierarchical level at which the budget applies.")
    budget_entity_name: str | None = Field(default=None, description="The name of the specific entity (organization, repository, or cost center) to which the budget applies.")
    budget_type: str | None = Field(default=None, description="The pricing model type covered by this budget.")
    budget_product_sku: str | None = Field(default=None, description="A specific product or SKU identifier to include in the budget scope.")
class BillingUpdateBudgetOrgRequest(StrictModel):
    """Update an existing budget for an organization. The authenticated user must have organization admin or billing manager permissions."""
    path: BillingUpdateBudgetOrgRequestPath
    body: BillingUpdateBudgetOrgRequestBody | None = None

# Operation: delete_budget
class BillingDeleteBudgetOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    budget_id: str = Field(default=..., description="The unique identifier of the budget to delete.")
class BillingDeleteBudgetOrgRequest(StrictModel):
    """Deletes a budget for an organization. The authenticated user must have organization admin or billing manager permissions."""
    path: BillingDeleteBudgetOrgRequestPath

# Operation: get_premium_request_usage_report
class BillingGetGithubBillingPremiumRequestUsageReportOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class BillingGetGithubBillingPremiumRequestUsageReportOrgRequestQuery(StrictModel):
    year: int | None = Field(default=None, description="Filter results to a specific year. Provide a four-digit year value. Defaults to the current year if not specified.")
    month: int | None = Field(default=None, description="Filter results to a specific month within the year. Provide a value between 1 and 12. Defaults to the current month if year is not specified.")
    day: int | None = Field(default=None, description="Filter results to a specific day within the month. Provide a value between 1 and 31. Defaults to the current day if year and month are not specified.")
    user: str | None = Field(default=None, description="Filter usage results for a specific user. Case-insensitive.")
    model: str | None = Field(default=None, description="Filter usage results for a specific model. Case-insensitive.")
    product: str | None = Field(default=None, description="Filter usage results for a specific product. Case-insensitive.")
class BillingGetGithubBillingPremiumRequestUsageReportOrgRequest(StrictModel):
    """Retrieve a premium request usage report for an organization, with optional filtering by time period, user, model, or product. Requires organization administrator privileges and only returns data from the past 24 months."""
    path: BillingGetGithubBillingPremiumRequestUsageReportOrgRequestPath
    query: BillingGetGithubBillingPremiumRequestUsageReportOrgRequestQuery | None = None

# Operation: get_organization_billing_usage
class BillingGetGithubBillingUsageReportOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class BillingGetGithubBillingUsageReportOrgRequestQuery(StrictModel):
    year: int | None = Field(default=None, description="Filter results to a specific year. Specify as a four-digit integer representing the year. Defaults to the current year if not provided.")
    month: int | None = Field(default=None, description="Filter results to a specific month within the specified or default year. Valid range is 1-12, where 1 represents January and 12 represents December.")
    day: int | None = Field(default=None, description="Filter results to a specific day within the specified or default year and month. Valid range is 1-31.")
class BillingGetGithubBillingUsageReportOrgRequest(StrictModel):
    """Retrieve a detailed billing usage report for an organization. This endpoint requires administrator access and is only available to organizations with the enhanced billing platform enabled."""
    path: BillingGetGithubBillingUsageReportOrgRequestPath
    query: BillingGetGithubBillingUsageReportOrgRequestQuery | None = None

# Operation: get_billing_usage_summary
class BillingGetGithubBillingUsageSummaryReportOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class BillingGetGithubBillingUsageSummaryReportOrgRequestQuery(StrictModel):
    year: int | None = Field(default=None, description="Filter results to a specific year. Specify as a four-digit integer representing the year.")
    month: int | None = Field(default=None, description="Filter results to a specific month. Valid range is 1-12. Requires year to be specified or uses the default year.")
    day: int | None = Field(default=None, description="Filter results to a specific day. Valid range is 1-31. Requires year and month to be specified or uses the default year and month.")
    product: str | None = Field(default=None, description="Filter results by product name. Case-insensitive.")
    sku: str | None = Field(default=None, description="Filter results by SKU identifier.")
class BillingGetGithubBillingUsageSummaryReportOrgRequest(StrictModel):
    """Retrieve a summary report of billing usage for an organization. This endpoint requires administrator privileges and provides access to usage data from the past 24 months."""
    path: BillingGetGithubBillingUsageSummaryReportOrgRequestPath
    query: BillingGetGithubBillingUsageSummaryReportOrgRequestQuery | None = None

# Operation: get_organization
class OrgsGetRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name to retrieve. The name is case-insensitive.")
class OrgsGetRequest(StrictModel):
    """Retrieve detailed information about an organization, including its plan and security settings. Full details require organization owner privileges or appropriate OAuth/PAT scopes."""
    path: OrgsGetRequestPath

# Operation: update_organization
class OrgsUpdateRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class OrgsUpdateRequestBody(StrictModel):
    billing_email: str | None = Field(default=None, description="Billing email address for the organization. This address is not publicly displayed.")
    company: str | None = Field(default=None, description="The company name associated with the organization.")
    twitter_username: str | None = Field(default=None, description="The Twitter username of the company.")
    description: str | None = Field(default=None, description="A description of the company. Maximum 160 characters.")
    has_organization_projects: bool | None = Field(default=None, description="Whether the organization can use organization-level projects.")
    has_repository_projects: bool | None = Field(default=None, description="Whether repositories in the organization can use repository-level projects.")
    default_repository_permission: Literal["read", "write", "admin", "none"] | None = Field(default=None, description="Default permission level that members have for organization repositories.")
    members_can_create_internal_repositories: bool | None = Field(default=None, description="Whether organization members can create internal repositories (visible to all enterprise members). Only applicable for organizations associated with GitHub Enterprise Cloud or GitHub Enterprise Server 2.20+.")
    members_can_create_private_repositories: bool | None = Field(default=None, description="Whether organization members can create private repositories (visible to members with permission).")
    members_can_create_public_repositories: bool | None = Field(default=None, description="Whether organization members can create public repositories (visible to anyone).")
    members_can_create_public_pages: bool | None = Field(default=None, description="Whether organization members can create public GitHub Pages sites. Existing published sites are not affected.")
    members_can_create_private_pages: bool | None = Field(default=None, description="Whether organization members can create private GitHub Pages sites. Existing published sites are not affected.")
    members_can_fork_private_repositories: bool | None = Field(default=None, description="Whether organization members can fork private organization repositories.")
    web_commit_signoff_required: bool | None = Field(default=None, description="Whether contributors to organization repositories are required to sign off on commits made through GitHub's web interface.")
    blog: str | None = Field(default=None, description="The organization's blog or website URL.")
    secret_scanning_push_protection_custom_link: str | None = Field(default=None, description="The URL displayed to contributors who are blocked from pushing a secret, when secret scanning push protection is enabled.")
    deploy_keys_enabled_for_repositories: bool | None = Field(default=None, description="Whether deploy keys can be added and used for repositories in the organization.")
class OrgsUpdateRequest(StrictModel):
    """Update an organization's profile, settings, and member permissions. The authenticated user must be an organization owner. Requires `admin:org` or `repo` scope."""
    path: OrgsUpdateRequestPath
    body: OrgsUpdateRequestBody | None = None

# Operation: delete_organization
class OrgsDeleteRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name to delete. The name is case-insensitive.")
class OrgsDeleteRequest(StrictModel):
    """Permanently deletes an organization and all its associated repositories. The organization name will be unavailable for 90 days following deletion."""
    path: OrgsDeleteRequestPath

# Operation: get_actions_cache_usage_for_org
class ActionsGetActionsCacheUsageForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsGetActionsCacheUsageForOrgRequest(StrictModel):
    """Retrieve the total GitHub Actions cache usage for an organization. Cache usage data is refreshed approximately every 5 minutes, so values may take at least 5 minutes to reflect recent changes."""
    path: ActionsGetActionsCacheUsageForOrgRequestPath

# Operation: list_actions_cache_usage_by_repository
class ActionsGetActionsCacheUsageByRepoForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class ActionsGetActionsCacheUsageByRepoForOrgRequest(StrictModel):
    """Retrieve GitHub Actions cache usage statistics for all repositories within an organization. Cache usage data is refreshed approximately every 5 minutes."""
    path: ActionsGetActionsCacheUsageByRepoForOrgRequestPath

# Operation: list_hosted_runners
class ActionsListHostedRunnersForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsListHostedRunnersForOrgRequest(StrictModel):
    """Lists all GitHub-hosted runners configured in an organization. Requires `manage_runner:org` scope for authentication."""
    path: ActionsListHostedRunnersForOrgRequestPath

# Operation: create_hosted_runner
class ActionsCreateHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ActionsCreateHostedRunnerForOrgRequestBody(StrictModel):
    name: str = Field(default=..., description="Name of the runner. Must be 1-64 characters containing only letters (a-z, A-Z), numbers (0-9), periods, hyphens, and underscores.")
    size: str = Field(default=..., description="The machine size for the runner. Available sizes can be retrieved via the list hosted runner machine sizes operation.")
    runner_group_id: int = Field(default=..., description="The ID of an existing runner group to add this runner to.")
    maximum_runners: int | None = Field(default=None, description="The maximum number of runners to scale up to. Prevents auto-scaling beyond this limit to control costs.")
    enable_static_ip: bool | None = Field(default=None, description="Whether to assign a static public IP to this runner. Note that account-level limits apply; check account limits via the get hosted runner limits operation.")
    image_gen: bool | None = Field(default=None, description="Whether this runner should be used to generate custom images.")
class ActionsCreateHostedRunnerForOrgRequest(StrictModel):
    """Creates a GitHub-hosted runner for an organization with configurable machine size, scaling limits, and optional static IP assignment. Requires `manage_runners:org` OAuth scope or personal access token (classic)."""
    path: ActionsCreateHostedRunnerForOrgRequestPath
    body: ActionsCreateHostedRunnerForOrgRequestBody

# Operation: list_custom_runner_images
class ActionsListCustomImagesForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the custom images to a specific organization.")
class ActionsListCustomImagesForOrgRequest(StrictModel):
    """Retrieve all custom images available for GitHub Actions hosted runners in an organization. Requires `manage_runners:org` OAuth scope or personal access token (classic)."""
    path: ActionsListCustomImagesForOrgRequestPath

# Operation: get_custom_runner_image
class ActionsGetCustomImageForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the GitHub organization.")
    image_definition_id: int = Field(default=..., description="The unique identifier of the custom image definition to retrieve.")
class ActionsGetCustomImageForOrgRequest(StrictModel):
    """Retrieve a custom image definition for GitHub Actions Hosted Runners. Requires `manage_runners:org` scope for authentication."""
    path: ActionsGetCustomImageForOrgRequestPath

# Operation: delete_custom_runner_image
class ActionsDeleteCustomImageFromOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    image_definition_id: int = Field(default=..., description="The unique identifier of the custom image definition to delete.")
class ActionsDeleteCustomImageFromOrgRequest(StrictModel):
    """Delete a custom image from the organization's hosted runners. Requires `manage_runners:org` OAuth scope or personal access token (classic)."""
    path: ActionsDeleteCustomImageFromOrgRequestPath

# Operation: list_custom_image_versions
class ActionsListCustomImageVersionsForOrgRequestPath(StrictModel):
    image_definition_id: int = Field(default=..., description="The unique identifier of the custom image definition whose versions you want to list.")
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsListCustomImageVersionsForOrgRequest(StrictModel):
    """Retrieve all versions of a custom image for an organization. Requires `manage_runners:org` OAuth scope or personal access token (classic)."""
    path: ActionsListCustomImageVersionsForOrgRequestPath

# Operation: get_custom_runner_image_version
class ActionsGetCustomImageVersionForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    image_definition_id: int = Field(default=..., description="The unique identifier of the custom image definition.")
    version: str = Field(default=..., description="The semantic version of the custom image in major.minor.patch format.", pattern='^\\d+\\.\\d+\\.\\d+$')
class ActionsGetCustomImageVersionForOrgRequest(StrictModel):
    """Retrieve a specific version of a custom image for GitHub Actions Hosted Runners. Requires the `manage_runners:org` scope for authentication."""
    path: ActionsGetCustomImageVersionForOrgRequestPath

# Operation: delete_custom_image_version
class ActionsDeleteCustomImageVersionFromOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    image_definition_id: int = Field(default=..., description="The unique identifier of the custom image definition.")
    version: str = Field(default=..., description="The version of the custom image to delete, specified in semantic versioning format (major.minor.patch).", pattern='^\\d+\\.\\d+\\.\\d+$')
class ActionsDeleteCustomImageVersionFromOrgRequest(StrictModel):
    """Delete a specific version of a custom image from an organization's hosted runners. Requires the `manage_runners:org` OAuth scope or personal access token (classic)."""
    path: ActionsDeleteCustomImageVersionFromOrgRequestPath

# Operation: list_github_owned_runner_images
class ActionsGetHostedRunnersGithubOwnedImagesForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsGetHostedRunnersGithubOwnedImagesForOrgRequest(StrictModel):
    """Retrieve the list of GitHub-owned images available for GitHub-hosted runners in an organization. Use this to see which runner images can be used for workflows in the organization."""
    path: ActionsGetHostedRunnersGithubOwnedImagesForOrgRequestPath

# Operation: list_partner_runner_images
class ActionsGetHostedRunnersPartnerImagesForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsGetHostedRunnersPartnerImagesForOrgRequest(StrictModel):
    """Retrieve the list of partner images available for GitHub-hosted runners in an organization. This allows you to see which pre-configured runner images are available for use."""
    path: ActionsGetHostedRunnersPartnerImagesForOrgRequestPath

# Operation: get_hosted_runners_limits
class ActionsGetHostedRunnersLimitsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsGetHostedRunnersLimitsForOrgRequest(StrictModel):
    """Retrieve the usage limits and quotas for GitHub-hosted runners available to an organization. This includes information about concurrent runner usage and other resource constraints."""
    path: ActionsGetHostedRunnersLimitsForOrgRequestPath

# Operation: list_hosted_runner_machine_specs
class ActionsGetHostedRunnersMachineSpecsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsGetHostedRunnersMachineSpecsForOrgRequest(StrictModel):
    """Retrieve the available machine specifications for GitHub-hosted runners in an organization. This includes details about CPU, memory, and other hardware configurations supported for workflow runs."""
    path: ActionsGetHostedRunnersMachineSpecsForOrgRequestPath

# Operation: list_hosted_runner_platforms
class ActionsGetHostedRunnersPlatformsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ActionsGetHostedRunnersPlatformsForOrgRequest(StrictModel):
    """Retrieve the list of available platforms for GitHub-hosted runners in an organization. Use this to determine which runner platforms can be used for workflows."""
    path: ActionsGetHostedRunnersPlatformsForOrgRequestPath

# Operation: get_hosted_runner
class ActionsGetHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    hosted_runner_id: int = Field(default=..., description="The unique identifier of the GitHub-hosted runner to retrieve.")
class ActionsGetHostedRunnerForOrgRequest(StrictModel):
    """Retrieve details for a specific GitHub-hosted runner configured in an organization. Requires the `manage_runners:org` scope for authentication."""
    path: ActionsGetHostedRunnerForOrgRequestPath

# Operation: update_hosted_runner
class ActionsUpdateHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    hosted_runner_id: int = Field(default=..., description="The unique identifier of the GitHub-hosted runner to update.")
class ActionsUpdateHostedRunnerForOrgRequestBody(StrictModel):
    runner_group_id: int | None = Field(default=None, description="The ID of an existing runner group to assign this runner to.")
    maximum_runners: int | None = Field(default=None, description="The maximum number of runners to scale up to. Prevents auto-scaling beyond this limit to control costs.")
    enable_static_ip: bool | None = Field(default=None, description="Whether to assign a static public IP to this runner. Subject to account-level limits; check limits via the hosted-runners limits endpoint.")
    size: str | None = Field(default=None, description="The machine size for the runner. Available sizes can be retrieved from the hosted-runners machine-sizes endpoint.")
    image_id: str | None = Field(default=None, description="The unique identifier of the runner image to deploy. Available images include GitHub-owned, partner, and custom images.")
    image_version: str | None = Field(default=None, description="The version of the runner image to deploy. Only applicable when using custom images.")
class ActionsUpdateHostedRunnerForOrgRequest(StrictModel):
    """Updates configuration for a GitHub-hosted runner in an organization, including runner group assignment, scaling limits, static IP settings, and machine image specifications. Requires `manage_runners:org` OAuth scope."""
    path: ActionsUpdateHostedRunnerForOrgRequestPath
    body: ActionsUpdateHostedRunnerForOrgRequestBody | None = None

# Operation: delete_hosted_runner
class ActionsDeleteHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    hosted_runner_id: int = Field(default=..., description="The unique identifier of the GitHub-hosted runner to delete.")
class ActionsDeleteHostedRunnerForOrgRequest(StrictModel):
    """Deletes a GitHub-hosted runner from an organization. This action removes the runner and prevents it from accepting new jobs."""
    path: ActionsDeleteHostedRunnerForOrgRequestPath

# Operation: list_oidc_custom_property_inclusions_for_org
class OidcListOidcCustomPropertyInclusionsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the OIDC custom property inclusions.")
class OidcListOidcCustomPropertyInclusionsForOrgRequest(StrictModel):
    """Lists the repository custom properties that are included in the OIDC token issued for repository actions within an organization. Requires `read:org` scope for authentication."""
    path: OidcListOidcCustomPropertyInclusionsForOrgRequestPath

# Operation: add_oidc_custom_property_org
class OidcCreateOidcCustomPropertyInclusionForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OidcCreateOidcCustomPropertyInclusionForOrgRequestBody(StrictModel):
    custom_property_name: str = Field(default=..., description="The name of the custom property to include in the OIDC token for repository actions.")
class OidcCreateOidcCustomPropertyInclusionForOrgRequest(StrictModel):
    """Adds a repository custom property to be included in OIDC tokens issued for repository actions within an organization. Requires `admin:org` scope."""
    path: OidcCreateOidcCustomPropertyInclusionForOrgRequestPath
    body: OidcCreateOidcCustomPropertyInclusionForOrgRequestBody

# Operation: list_organization_github_actions_repositories
class ActionsListSelectedRepositoriesEnabledGithubActionsOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsListSelectedRepositoriesEnabledGithubActionsOrganizationRequest(StrictModel):
    """Lists the selected repositories that are enabled for GitHub Actions within an organization. This endpoint requires the organization's GitHub Actions permission policy to be configured for selected repositories."""
    path: ActionsListSelectedRepositoriesEnabledGithubActionsOrganizationRequestPath

# Operation: list_organization_self_hosted_runner_repositories
class ActionsListSelectedRepositoriesSelfHostedRunnersOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
class ActionsListSelectedRepositoriesSelfHostedRunnersOrganizationRequest(StrictModel):
    """Lists all repositories within an organization that are permitted to use self-hosted runners. Requires admin:org scope or Actions policies fine-grained permission."""
    path: ActionsListSelectedRepositoriesSelfHostedRunnersOrganizationRequestPath

# Operation: remove_repository_from_self_hosted_runners
class ActionsDisableSelectedRepositorySelfHostedRunnersOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    repository_id: int = Field(default=..., description="The unique numeric identifier of the repository to remove from self-hosted runner access.")
class ActionsDisableSelectedRepositorySelfHostedRunnersOrganizationRequest(StrictModel):
    """Remove a repository from the list of repositories allowed to use self-hosted runners in an organization. This prevents the specified repository from accessing organization-level self-hosted runners."""
    path: ActionsDisableSelectedRepositorySelfHostedRunnersOrganizationRequestPath

# Operation: list_runner_groups
class ActionsListSelfHostedRunnerGroupsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ActionsListSelfHostedRunnerGroupsForOrgRequestQuery(StrictModel):
    visible_to_repository: str | None = Field(default=None, description="Filter to return only runner groups that are allowed to be used by a specific repository.")
class ActionsListSelfHostedRunnerGroupsForOrgRequest(StrictModel):
    """Lists all self-hosted runner groups configured in an organization, including those inherited from an enterprise. Requires `admin:org` scope for authentication."""
    path: ActionsListSelfHostedRunnerGroupsForOrgRequestPath
    query: ActionsListSelfHostedRunnerGroupsForOrgRequestQuery | None = None

# Operation: create_runner_group
class ActionsCreateSelfHostedRunnerGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ActionsCreateSelfHostedRunnerGroupForOrgRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the runner group to create.")
    visibility: Literal["selected", "all", "private"] | None = Field(default=None, description="Controls which repositories can access this runner group. 'all' allows all repositories, 'selected' restricts to specified repositories, and 'private' limits to private repositories only.")
    selected_repository_ids: list[int] | None = Field(default=None, description="List of repository IDs that can access this runner group. Only applicable when visibility is set to 'selected'.")
    runners: list[int] | None = Field(default=None, description="List of runner IDs to add to this runner group upon creation.")
    allows_public_repositories: bool | None = Field(default=None, description="Whether public repositories can use runners in this group.")
    network_configuration_id: str | None = Field(default=None, description="The identifier of a hosted compute network configuration to associate with this runner group.")
class ActionsCreateSelfHostedRunnerGroupForOrgRequest(StrictModel):
    """Creates a new self-hosted runner group for an organization, allowing you to manage access to runners across repositories. Requires `admin:org` scope for authentication."""
    path: ActionsCreateSelfHostedRunnerGroupForOrgRequestPath
    body: ActionsCreateSelfHostedRunnerGroupForOrgRequestBody

# Operation: get_runner_group
class ActionsGetSelfHostedRunnerGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group to retrieve.")
class ActionsGetSelfHostedRunnerGroupForOrgRequest(StrictModel):
    """Retrieve a specific self-hosted runner group for an organization. Requires `admin:org` scope for authentication."""
    path: ActionsGetSelfHostedRunnerGroupForOrgRequestPath

# Operation: update_runner_group
class ActionsUpdateSelfHostedRunnerGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group to update.")
class ActionsUpdateSelfHostedRunnerGroupForOrgRequestBody(StrictModel):
    name: str = Field(default=..., description="The new name for the runner group.")
    visibility: Literal["selected", "all", "private"] | None = Field(default=None, description="The visibility level of the runner group, determining which repositories can access it.")
    allows_public_repositories: bool | None = Field(default=None, description="Whether the runner group can be used by public repositories.")
    network_configuration_id: str | None = Field(default=None, description="The identifier of a hosted compute network configuration to associate with this runner group.")
class ActionsUpdateSelfHostedRunnerGroupForOrgRequest(StrictModel):
    """Update the name and visibility settings of a self-hosted runner group in an organization. Requires `admin:org` scope for authentication."""
    path: ActionsUpdateSelfHostedRunnerGroupForOrgRequestPath
    body: ActionsUpdateSelfHostedRunnerGroupForOrgRequestBody

# Operation: delete_runner_group
class ActionsDeleteSelfHostedRunnerGroupFromOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the runner group.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group to delete.")
class ActionsDeleteSelfHostedRunnerGroupFromOrgRequest(StrictModel):
    """Delete a self-hosted runner group from an organization. Requires `admin:org` scope for authentication."""
    path: ActionsDeleteSelfHostedRunnerGroupFromOrgRequestPath

# Operation: list_github_hosted_runners_in_group
class ActionsListGithubHostedRunnersInGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the runner group to retrieve hosted runners from.")
class ActionsListGithubHostedRunnersInGroupForOrgRequest(StrictModel):
    """Lists all GitHub-hosted runners assigned to a specific runner group within an organization. Requires `admin:org` scope for authentication."""
    path: ActionsListGithubHostedRunnersInGroupForOrgRequestPath

# Operation: list_runner_group_repositories
class ActionsListRepoAccessToSelfHostedRunnerGroupInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group.")
class ActionsListRepoAccessToSelfHostedRunnerGroupInOrgRequest(StrictModel):
    """Lists all repositories that have access to a self-hosted runner group within an organization. Requires `admin:org` scope for authentication."""
    path: ActionsListRepoAccessToSelfHostedRunnerGroupInOrgRequestPath

# Operation: update_runner_group_repository_access
class ActionsSetRepoAccessToSelfHostedRunnerGroupInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group to update.")
class ActionsSetRepoAccessToSelfHostedRunnerGroupInOrgRequestBody(StrictModel):
    selected_repository_ids: list[int] = Field(default=..., description="An array of repository IDs that should have access to this runner group. Providing an empty array removes access for all repositories. The order of IDs in the array is not significant.")
class ActionsSetRepoAccessToSelfHostedRunnerGroupInOrgRequest(StrictModel):
    """Updates which repositories in an organization can access a self-hosted runner group. This replaces the entire list of authorized repositories for the specified runner group."""
    path: ActionsSetRepoAccessToSelfHostedRunnerGroupInOrgRequestPath
    body: ActionsSetRepoAccessToSelfHostedRunnerGroupInOrgRequestBody

# Operation: grant_runner_group_repository_access
class ActionsAddRepoAccessToSelfHostedRunnerGroupInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to grant access to the runner group.")
class ActionsAddRepoAccessToSelfHostedRunnerGroupInOrgRequest(StrictModel):
    """Grants a repository access to a self-hosted runner group in an organization. The runner group must have visibility set to 'selected'. Requires `admin:org` scope."""
    path: ActionsAddRepoAccessToSelfHostedRunnerGroupInOrgRequestPath

# Operation: revoke_runner_group_repository_access
class ActionsRemoveRepoAccessToSelfHostedRunnerGroupInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the runner group's access list.")
class ActionsRemoveRepoAccessToSelfHostedRunnerGroupInOrgRequest(StrictModel):
    """Remove a repository from a self-hosted runner group's access list in an organization. The runner group must have visibility set to 'selected'. Requires `admin:org` scope."""
    path: ActionsRemoveRepoAccessToSelfHostedRunnerGroupInOrgRequestPath

# Operation: list_runners_in_group
class ActionsListSelfHostedRunnersInGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. This value is case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group.")
class ActionsListSelfHostedRunnersInGroupForOrgRequest(StrictModel):
    """Lists all self-hosted runners that belong to a specific runner group within an organization. Requires `admin:org` scope for authentication."""
    path: ActionsListSelfHostedRunnersInGroupForOrgRequestPath

# Operation: update_runner_group_runners
class ActionsSetSelfHostedRunnersInGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group to update.")
class ActionsSetSelfHostedRunnersInGroupForOrgRequestBody(StrictModel):
    runners: list[int] = Field(default=..., description="List of self-hosted runner IDs to assign to the runner group. This replaces any previously assigned runners. Order is not significant.")
class ActionsSetSelfHostedRunnersInGroupForOrgRequest(StrictModel):
    """Replace the list of self-hosted runners assigned to an organization runner group. Requires admin:org scope for authentication."""
    path: ActionsSetSelfHostedRunnersInGroupForOrgRequestPath
    body: ActionsSetSelfHostedRunnersInGroupForOrgRequestBody

# Operation: add_runner_to_group
class ActionsAddSelfHostedRunnerToGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group to which the runner will be added.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to add to the group.")
class ActionsAddSelfHostedRunnerToGroupForOrgRequest(StrictModel):
    """Adds a self-hosted runner to a runner group within an organization. Requires `admin:org` scope for authentication."""
    path: ActionsAddSelfHostedRunnerToGroupForOrgRequestPath

# Operation: remove_runner_from_group
class ActionsRemoveSelfHostedRunnerFromGroupForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_group_id: int = Field(default=..., description="The unique identifier of the self-hosted runner group.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to remove from the group.")
class ActionsRemoveSelfHostedRunnerFromGroupForOrgRequest(StrictModel):
    """Remove a self-hosted runner from an organization's runner group, returning it to the default group. Requires `admin:org` scope."""
    path: ActionsRemoveSelfHostedRunnerFromGroupForOrgRequestPath

# Operation: list_organization_runners
class ActionsListSelfHostedRunnersForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the runner list to a specific organization.")
class ActionsListSelfHostedRunnersForOrgRequest(StrictModel):
    """Retrieve all self-hosted runners configured for an organization. Requires admin access to the organization and appropriate OAuth or personal access token scopes."""
    path: ActionsListSelfHostedRunnersForOrgRequestPath

# Operation: list_runner_applications
class ActionsListRunnerApplicationsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the runner applications to a specific organization.")
class ActionsListRunnerApplicationsForOrgRequest(StrictModel):
    """Lists available runner application binaries that can be downloaded and executed for an organization. Requires admin access to the organization."""
    path: ActionsListRunnerApplicationsForOrgRequestPath

# Operation: generate_runner_registration_token
class ActionsCreateRegistrationTokenForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the GitHub organization.")
class ActionsCreateRegistrationTokenForOrgRequest(StrictModel):
    """Generate a registration token for self-hosted runners in an organization. The token expires after one hour and is used to configure new runners via the config script."""
    path: ActionsCreateRegistrationTokenForOrgRequestPath

# Operation: generate_runner_removal_token
class ActionsCreateRemoveTokenForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization where the runner will be removed.")
class ActionsCreateRemoveTokenForOrgRequest(StrictModel):
    """Generate a short-lived token for removing a self-hosted runner from an organization. The token expires after one hour and is used with the config script to deregister the runner."""
    path: ActionsCreateRemoveTokenForOrgRequestPath

# Operation: get_runner
class ActionsGetSelfHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to retrieve.")
class ActionsGetSelfHostedRunnerForOrgRequest(StrictModel):
    """Retrieve details for a specific self-hosted runner in an organization. Requires admin access to the organization."""
    path: ActionsGetSelfHostedRunnerForOrgRequestPath

# Operation: remove_runner_from_organization
class ActionsDeleteSelfHostedRunnerFromOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the runner.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to remove from the organization.")
class ActionsDeleteSelfHostedRunnerFromOrgRequest(StrictModel):
    """Permanently remove a self-hosted runner from an organization. Use this endpoint when the runner machine no longer exists or you need to completely deregister it from the organization."""
    path: ActionsDeleteSelfHostedRunnerFromOrgRequestPath

# Operation: list_runner_labels
class ActionsListLabelsForSelfHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner.")
class ActionsListLabelsForSelfHostedRunnerForOrgRequest(StrictModel):
    """Retrieve all labels assigned to a self-hosted runner in an organization. Requires admin access to the organization."""
    path: ActionsListLabelsForSelfHostedRunnerForOrgRequestPath

# Operation: add_labels_to_runner
class ActionsAddCustomLabelsToSelfHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to label.")
class ActionsAddCustomLabelsToSelfHostedRunnerForOrgRequestBody(StrictModel):
    labels: list[str] = Field(default=..., description="An array of custom label names to add to the runner. Labels must be unique and non-empty.", min_length=1, max_length=100)
class ActionsAddCustomLabelsToSelfHostedRunnerForOrgRequest(StrictModel):
    """Add custom labels to a self-hosted runner in an organization. Requires admin access to the organization and the `admin:org` OAuth scope."""
    path: ActionsAddCustomLabelsToSelfHostedRunnerForOrgRequestPath
    body: ActionsAddCustomLabelsToSelfHostedRunnerForOrgRequestBody

# Operation: update_runner_labels
class ActionsSetCustomLabelsForSelfHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to update.")
class ActionsSetCustomLabelsForSelfHostedRunnerForOrgRequestBody(StrictModel):
    labels: list[str] = Field(default=..., description="An array of custom label names to assign to the runner. All previous labels will be replaced. Pass an empty array to remove all custom labels.", min_length=0, max_length=100)
class ActionsSetCustomLabelsForSelfHostedRunnerForOrgRequest(StrictModel):
    """Replace all custom labels for a self-hosted runner in an organization. Requires admin access to the organization and appropriate OAuth or personal access token scopes."""
    path: ActionsSetCustomLabelsForSelfHostedRunnerForOrgRequestPath
    body: ActionsSetCustomLabelsForSelfHostedRunnerForOrgRequestBody

# Operation: remove_all_custom_labels_from_runner
class ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the runner.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner from which to remove all custom labels.")
class ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForOrgRequest(StrictModel):
    """Remove all custom labels from a self-hosted runner in an organization. The runner will retain its read-only labels after this operation. Requires admin access to the organization."""
    path: ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForOrgRequestPath

# Operation: remove_custom_label_from_runner
class ActionsRemoveCustomLabelFromSelfHostedRunnerForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner.")
    name: str = Field(default=..., description="The name of the custom label to remove from the runner.")
class ActionsRemoveCustomLabelFromSelfHostedRunnerForOrgRequest(StrictModel):
    """Remove a custom label from a self-hosted runner in an organization. Returns the remaining labels on the runner after removal. Requires admin access to the organization."""
    path: ActionsRemoveCustomLabelFromSelfHostedRunnerForOrgRequestPath

# Operation: list_organization_secrets
class ActionsListOrgSecretsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. This value is case-insensitive.")
class ActionsListOrgSecretsRequest(StrictModel):
    """Retrieve all secrets configured at the organization level without exposing their encrypted values. Requires appropriate authentication scopes and collaborator access to the repository."""
    path: ActionsListOrgSecretsRequestPath

# Operation: get_organization_public_key
class ActionsGetOrgPublicKeyRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ActionsGetOrgPublicKeyRequest(StrictModel):
    """Retrieves the public key for an organization, which is required to encrypt secrets before creating or updating them. The authenticated user must have the appropriate permissions (admin:org scope for OAuth/PAT, or repo scope for private repositories)."""
    path: ActionsGetOrgPublicKeyRequestPath

# Operation: get_organization_secret
class ActionsGetOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class ActionsGetOrgSecretRequest(StrictModel):
    """Retrieve a single organization secret without revealing its encrypted value. The authenticated user must have collaborator access to the repository and appropriate OAuth scopes (admin:org for public repositories, repo for private repositories)."""
    path: ActionsGetOrgSecretRequestPath

# Operation: create_or_update_organization_secret
class ActionsCreateOrUpdateOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    secret_name: str = Field(default=..., description="The name of the secret to create or update.")
class ActionsCreateOrUpdateOrgSecretRequestBody(StrictModel):
    key_id: str = Field(default=..., description="The ID of the public key used to encrypt the secret value.")
    visibility: Literal["all", "private", "selected"] = Field(default=..., description="Controls which organization repositories have access to this secret. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to restrict access to specific repositories.")
    selected_repository_ids: list[int] | None = Field(default=None, description="Array of repository IDs that can access the secret. Only applicable when visibility is set to 'selected'. Manage this list using the dedicated repository selection endpoints.")
    encrypted_value: str | None = Field(default=None, description="Value for your secret, encrypted with [LibSodium](https://libsodium.gitbook.io/doc/bindings_for_other_languages) using the public key retrieved from the [Get an organization public key](https://docs.github.com/rest/actions/secrets#get-an-organization-public-key) endpoint.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
class ActionsCreateOrUpdateOrgSecretRequest(StrictModel):
    """Create or update an encrypted secret at the organization level, controlling which repositories can access it. The secret value must be encrypted using LibSodium before submission."""
    path: ActionsCreateOrUpdateOrgSecretRequestPath
    body: ActionsCreateOrUpdateOrgSecretRequestBody

# Operation: delete_organization_secret
class ActionsDeleteOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to delete.")
class ActionsDeleteOrgSecretRequest(StrictModel):
    """Deletes a secret from an organization by its name. Requires admin:org scope for OAuth/PAT, or repo scope if the repository is private."""
    path: ActionsDeleteOrgSecretRequestPath

# Operation: list_organization_secret_repositories
class ActionsListSelectedReposForOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve repository access for.")
class ActionsListSelectedReposForOrgSecretRequest(StrictModel):
    """Lists all repositories that have been granted access to an organization secret when visibility is set to selected. Requires collaborator access to the repository and appropriate OAuth or personal access token scopes."""
    path: ActionsListSelectedReposForOrgSecretRequestPath

# Operation: update_organization_secret_repositories
class ActionsSetSelectedReposForOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to update repository access for.")
class ActionsSetSelectedReposForOrgSecretRequestBody(StrictModel):
    selected_repository_ids: list[int] = Field(default=..., description="An array of repository IDs that will have access to the organization secret. This replaces all previously selected repositories. Only applicable when the secret's visibility is set to selected.")
class ActionsSetSelectedReposForOrgSecretRequest(StrictModel):
    """Replace all repositories that can access an organization secret when visibility is set to selected. This operation completely overwrites the existing repository list for the secret."""
    path: ActionsSetSelectedReposForOrgSecretRequestPath
    body: ActionsSetSelectedReposForOrgSecretRequestBody

# Operation: grant_repository_access_to_organization_secret
class ActionsAddSelectedRepoToOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret to grant access to.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to grant access to the secret.")
class ActionsAddSelectedRepoToOrgSecretRequest(StrictModel):
    """Grants a repository access to an organization secret that is configured with selected repository visibility. This operation is used to expand which repositories can access a specific organization secret."""
    path: ActionsAddSelectedRepoToOrgSecretRequestPath

# Operation: remove_repository_from_organization_secret
class ActionsRemoveSelectedRepoFromOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret to modify.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the secret's access list.")
class ActionsRemoveSelectedRepoFromOrgSecretRequest(StrictModel):
    """Remove a repository from an organization secret that has visibility restricted to selected repositories. This operation is used to revoke a repository's access to a shared organization secret."""
    path: ActionsRemoveSelectedRepoFromOrgSecretRequestPath

# Operation: list_organization_variables
class ActionsListOrgVariablesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is case-insensitive.")
class ActionsListOrgVariablesRequest(StrictModel):
    """Retrieve all variables defined at the organization level. Authenticated users need collaborator access to manage variables, and the request requires appropriate OAuth or personal access token scopes."""
    path: ActionsListOrgVariablesRequestPath

# Operation: create_organization_variable
class ActionsCreateOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class ActionsCreateOrgVariableRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the variable. This identifier is used to reference the variable in workflows.")
    value: str = Field(default=..., description="The value assigned to the variable. This can be any string content needed by your workflows.")
    visibility: Literal["all", "private", "selected"] = Field(default=..., description="Controls which repositories in the organization can access this variable. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to restrict access to specific repositories listed in selected_repository_ids.")
    selected_repository_ids: list[int] | None = Field(default=None, description="An array of repository IDs that can access this variable. Only applicable when visibility is set to 'selected'. Omit this field for 'all' or 'private' visibility settings.")
class ActionsCreateOrgVariableRequest(StrictModel):
    """Create an organization-level variable for use in GitHub Actions workflows. The variable's accessibility is controlled by visibility settings, allowing it to be shared across all repositories, private repositories only, or a specific subset of repositories."""
    path: ActionsCreateOrgVariableRequestPath
    body: ActionsCreateOrgVariableRequestBody

# Operation: get_organization_variable
class ActionsGetOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    name: str = Field(default=..., description="The name of the variable to retrieve.")
class ActionsGetOrgVariableRequest(StrictModel):
    """Retrieve a specific variable from an organization. The authenticated user must have collaborator access to the repository, and appropriate OAuth scopes (admin:org for public repositories, repo for private repositories) are required."""
    path: ActionsGetOrgVariableRequestPath

# Operation: update_organization_variable
class ActionsUpdateOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    name: str = Field(default=..., description="The name of the variable to update.")
class ActionsUpdateOrgVariableRequestBody(StrictModel):
    value: str | None = Field(default=None, description="The new value for the variable.")
    visibility: Literal["all", "private", "selected"] | None = Field(default=None, description="The visibility scope for the variable. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to restrict access to specific repositories.")
    selected_repository_ids: list[int] | None = Field(default=None, description="An array of repository IDs that can access the variable. Only applicable when visibility is set to 'selected'.")
class ActionsUpdateOrgVariableRequest(StrictModel):
    """Update an organization variable that can be referenced in GitHub Actions workflows. Requires collaborator access to the repository and appropriate OAuth or personal access token scopes."""
    path: ActionsUpdateOrgVariableRequestPath
    body: ActionsUpdateOrgVariableRequestBody | None = None

# Operation: delete_organization_variable
class ActionsDeleteOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    name: str = Field(default=..., description="The name of the organization variable to delete.")
class ActionsDeleteOrgVariableRequest(StrictModel):
    """Delete an organization variable by name. Requires collaborator access to the organization and appropriate OAuth scopes (admin:org for public repositories, repo for private repositories)."""
    path: ActionsDeleteOrgVariableRequestPath

# Operation: list_organization_variable_repositories
class ActionsListSelectedReposForOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    name: str = Field(default=..., description="The name of the organization variable. Variable names are case-sensitive.")
class ActionsListSelectedReposForOrgVariableRequest(StrictModel):
    """Lists all repositories that have access to a specific organization variable. Use this to view which repositories can use a selected-repository organization variable."""
    path: ActionsListSelectedReposForOrgVariableRequestPath

# Operation: update_org_variable_repositories
class ActionsSetSelectedReposForOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    name: str = Field(default=..., description="The name of the organization variable to update.")
class ActionsSetSelectedReposForOrgVariableRequestBody(StrictModel):
    selected_repository_ids: list[int] = Field(default=..., description="An array of repository IDs that will have access to this organization variable. The order of IDs is not significant. Replaces all previously selected repositories.")
class ActionsSetSelectedReposForOrgVariableRequest(StrictModel):
    """Replace all repositories that have access to an organization variable. This operation applies only to organization variables with visibility set to `selected`."""
    path: ActionsSetSelectedReposForOrgVariableRequestPath
    body: ActionsSetSelectedReposForOrgVariableRequestBody

# Operation: add_repository_to_org_variable
class ActionsAddSelectedRepoToOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    name: str = Field(default=..., description="The name of the organization variable to which the repository will be added.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to add to the organization variable.")
class ActionsAddSelectedRepoToOrgVariableRequest(StrictModel):
    """Adds a repository to an organization variable that is available to selected repositories. The variable must have its visibility set to 'selected' to use this endpoint."""
    path: ActionsAddSelectedRepoToOrgVariableRequestPath

# Operation: remove_repository_from_org_variable
class ActionsRemoveSelectedRepoFromOrgVariableRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    name: str = Field(default=..., description="The name of the organization variable from which to remove the repository.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the organization variable.")
class ActionsRemoveSelectedRepoFromOrgVariableRequest(StrictModel):
    """Remove a repository from an organization variable that is available to selected repositories. This operation is used to restrict variable access by removing a specific repository from the variable's selected repositories list."""
    path: ActionsRemoveSelectedRepoFromOrgVariableRequestPath

# Operation: record_artifact_deployment
class OrgsCreateArtifactDeploymentRecordRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name that owns the artifact.")
class OrgsCreateArtifactDeploymentRecordRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the artifact being deployed.", min_length=1, max_length=256)
    digest: str = Field(default=..., description="The SHA256 digest of the artifact in hexadecimal format.", min_length=71, max_length=71, pattern='^sha256:[a-f0-9]{64}$')
    status: Literal["deployed", "decommissioned"] = Field(default=..., description="The current status of the artifact deployment.")
    logical_environment: str = Field(default=..., description="The deployment stage or environment tier (e.g., development, staging, production).", min_length=1, max_length=128)
    physical_environment: str | None = Field(default=None, description="The geographic region or physical location where the artifact is deployed.", max_length=128)
    cluster: str | None = Field(default=None, description="The Kubernetes cluster or deployment cluster identifier.", max_length=128)
    deployment_name: str = Field(default=..., description="A unique identifier for this deployment within the cluster. Use the format {namespaceName}-{deploymentName}-{containerName} to distinguish between different namespaces and containers.", max_length=256)
    tags: dict[str, str] | None = Field(default=None, description="Key-value pairs for labeling and organizing the deployment record.", max_length=5)
    runtime_risks: Annotated[list[Literal["critical-resource", "internet-exposed", "lateral-movement", "sensitive-data"]], AfterValidator(_check_unique_items)] | None = Field(default=None, description="A list of identified runtime risks or vulnerabilities associated with this deployment.", max_length=4)
    github_repository: str | None = Field(default=None, description="The GitHub repository name associated with the artifact. Used only when provenance attestations are unavailable; if attestations exist, repository information from the attestation takes precedence.", min_length=1, max_length=100, pattern='^[A-Za-z0-9.\\-_]+$')
class OrgsCreateArtifactDeploymentRecordRequest(StrictModel):
    """Record or update deployment information for an artifact within an organization. Deployment records are uniquely identified by the combination of logical environment, physical environment, cluster, and deployment name—successive requests with identical identifiers will update the existing record rather than create duplicates."""
    path: OrgsCreateArtifactDeploymentRecordRequestPath
    body: OrgsCreateArtifactDeploymentRecordRequestBody

# Operation: record_cluster_deployments
class OrgsSetClusterDeploymentRecordsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    cluster: str = Field(default=..., description="The cluster identifier.", min_length=1, max_length=128, pattern='^[a-zA-Z0-9._-]+$')
class OrgsSetClusterDeploymentRecordsRequestBody(StrictModel):
    logical_environment: str = Field(default=..., description="The deployment stage or environment tier (e.g., development, staging, production).", min_length=1, max_length=128)
    physical_environment: str | None = Field(default=None, description="The geographic region or physical location where the deployment resides.", max_length=128)
    deployments: list[OrgsSetClusterDeploymentRecordsBodyDeploymentsItem] = Field(default=..., description="An ordered list of deployment records to create or update. Each deployment must include cluster, logical_environment, physical_environment, and deployment_name fields for matching and identification.", max_length=1000)
class OrgsSetClusterDeploymentRecordsRequest(StrictModel):
    """Record or update deployment information for a cluster across logical and physical environments. Existing records matching the cluster, logical environment, physical environment, and deployment name are updated; non-matching records are created as new."""
    path: OrgsSetClusterDeploymentRecordsRequestPath
    body: OrgsSetClusterDeploymentRecordsRequestBody

# Operation: register_artifact_storage
class OrgsCreateArtifactStorageRecordRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class OrgsCreateArtifactStorageRecordRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the artifact.", min_length=1, max_length=256)
    digest: str = Field(default=..., description="The digest of the artifact in the format algorithm:hex-encoded-digest (SHA256 only).", min_length=71, max_length=71, pattern='^sha256:[a-f0-9]{64}$')
    registry_url: str = Field(default=..., description="The base URL of the artifact registry (must use HTTPS).", min_length=1, pattern='^https://', json_schema_extra={'format': 'uri'})
    github_repository: str | None = Field(default=None, description="The GitHub repository name associated with the artifact. Use this when provenance attestations are unavailable. The repository must belong to the specified organization. If a provenance attestation exists, it takes precedence over this value.", min_length=1, max_length=100, pattern='^[A-Za-z0-9.\\-_]+$')
class OrgsCreateArtifactStorageRecordRequest(StrictModel):
    """Register a metadata storage record for an artifact in an organization's registry. This creates a new storage record for artifacts matching the provided digest and associated with a repository owned by the organization."""
    path: OrgsCreateArtifactStorageRecordRequestPath
    body: OrgsCreateArtifactStorageRecordRequestBody

# Operation: list_artifact_deployment_records
class OrgsListArtifactDeploymentRecordsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive). This identifies which organization's artifact metadata to query.")
    subject_digest: str = Field(default=..., description="The SHA256 digest of the artifact in the format `sha256:HEX_DIGEST`, where HEX_DIGEST is a 64-character hexadecimal string.", min_length=71, max_length=71, pattern='^sha256:[a-f0-9]{64}$')
class OrgsListArtifactDeploymentRecordsRequest(StrictModel):
    """Retrieve deployment records for an artifact's metadata within an organization. This shows the history of where and when the artifact has been deployed."""
    path: OrgsListArtifactDeploymentRecordsRequestPath

# Operation: list_artifact_storage_records
class OrgsListArtifactStorageRecordsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    subject_digest: str = Field(default=..., description="The SHA256 digest of the artifact's subject in the format sha256:HEX_DIGEST, where HEX_DIGEST is a 64-character hexadecimal string.", min_length=71, max_length=71, pattern='^sha256:[a-f0-9]{64}$')
class OrgsListArtifactStorageRecordsRequest(StrictModel):
    """Retrieve storage records for an artifact by its subject digest within an organization. Results are filtered based on the authenticated user's repository access permissions."""
    path: OrgsListArtifactStorageRecordsRequestPath

# Operation: list_attestations_by_digests
class OrgsListAttestationsBulkRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsListAttestationsBulkRequestBody(StrictModel):
    subject_digests: list[str] = Field(default=..., description="List of subject digests to fetch attestations for. Each digest identifies an artifact for which attestations will be retrieved.", min_length=1, max_length=1024)
    predicate_type: str | None = Field(default=None, description="Optional filter to retrieve attestations matching a specific predicate type. Supports standard types (provenance, sbom, release) or custom freeform text for custom predicate types.")
class OrgsListAttestationsBulkRequest(StrictModel):
    """Retrieve artifact attestations for multiple subject digests owned by an organization. Results are filtered based on the authenticated user's repository permissions and require the `attestations:read` permission for fine-grained access tokens."""
    path: OrgsListAttestationsBulkRequestPath
    body: OrgsListAttestationsBulkRequestBody

# Operation: delete_attestations
class OrgsDeleteAttestationsBulkRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the attestations.")
class OrgsDeleteAttestationsBulkRequestBody(StrictModel):
    body: OrgsDeleteAttestationsBulkBodyV0 | OrgsDeleteAttestationsBulkBodyV1 = Field(default=..., description="Request payload containing deletion criteria. Provide either subject_digests (array of digest strings in algorithm:hash format) or attestation_ids (array of numeric identifiers), but not both.", examples=[{'subject_digests': ['sha256:abc123', 'sha512:def456']}, {'attestation_ids': [111, 222]}])
class OrgsDeleteAttestationsBulkRequest(StrictModel):
    """Delete artifact attestations in bulk by specifying either subject digests or attestation IDs. Exactly one of these criteria must be provided in the request."""
    path: OrgsDeleteAttestationsBulkRequestPath
    body: OrgsDeleteAttestationsBulkRequestBody

# Operation: delete_attestation_by_subject_digest
class OrgsDeleteAttestationsBySubjectDigestRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    subject_digest: str = Field(default=..., description="The subject digest that uniquely identifies the artifact attestation to delete.")
class OrgsDeleteAttestationsBySubjectDigestRequest(StrictModel):
    """Delete an artifact attestation by its subject digest. This operation removes attestation records associated with a specific artifact digest within an organization."""
    path: OrgsDeleteAttestationsBySubjectDigestRequestPath

# Operation: list_attestation_repositories
class OrgsListAttestationRepositoriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class OrgsListAttestationRepositoriesRequestQuery(StrictModel):
    predicate_type: str | None = Field(default=None, description="Filter repositories by attestation predicate type. Accepts standard types (provenance, sbom, release) or custom freeform text for specialized predicate types.")
class OrgsListAttestationRepositoriesRequest(StrictModel):
    """List repositories in an organization that have created at least one attested artifact. Results are sorted in ascending order by repository ID."""
    path: OrgsListAttestationRepositoriesRequestPath
    query: OrgsListAttestationRepositoriesRequestQuery | None = None

# Operation: delete_attestation
class OrgsDeleteAttestationsByIdRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    attestation_id: int = Field(default=..., description="The unique identifier of the attestation to delete.")
class OrgsDeleteAttestationsByIdRequest(StrictModel):
    """Delete an artifact attestation by ID from an organization's repository. This operation removes the attestation record permanently."""
    path: OrgsDeleteAttestationsByIdRequestPath

# Operation: list_attestations_organization
class OrgsListAttestationsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    subject_digest: str = Field(default=..., description="The attestation subject's SHA256 digest in the format `sha256:HEX_DIGEST`.")
class OrgsListAttestationsRequestQuery(StrictModel):
    predicate_type: str | None = Field(default=None, description="Filter attestations by predicate type. Accepts standard types (provenance, sbom, release) or custom freeform text.")
class OrgsListAttestationsRequest(StrictModel):
    """Retrieve artifact attestations for a given subject digest across repositories owned by an organization. Results are filtered based on the authenticated user's repository access permissions."""
    path: OrgsListAttestationsRequestPath
    query: OrgsListAttestationsRequestQuery | None = None

# Operation: list_blocked_users
class OrgsListBlockedUsersRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class OrgsListBlockedUsersRequest(StrictModel):
    """Retrieve a list of all users blocked by an organization. This helps manage organization security and access control policies."""
    path: OrgsListBlockedUsersRequestPath

# Operation: check_blocked_user
class OrgsCheckBlockedUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle to check for blocking status.")
class OrgsCheckBlockedUserRequest(StrictModel):
    """Check if a user is blocked by an organization. Returns a 204 status if the user is blocked, or 404 if the user is not blocked or has been identified as spam."""
    path: OrgsCheckBlockedUserRequestPath

# Operation: unblock_user_organization
class OrgsUnblockUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    username: str = Field(default=..., description="The GitHub username handle to unblock from the organization.")
class OrgsUnblockUserRequest(StrictModel):
    """Unblock a user from an organization, restoring their access and permissions within that organization."""
    path: OrgsUnblockUserRequestPath

# Operation: list_campaigns
class CampaignsListOrgCampaignsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CampaignsListOrgCampaignsRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort direction for the returned campaigns.")
    state: Literal["open", "closed"] | None = Field(default=None, description="Filter campaigns by their current state. If omitted, campaigns in all states are returned.")
class CampaignsListOrgCampaignsRequest(StrictModel):
    """Retrieve all campaigns for an organization. The authenticated user must be an owner or security manager to access this endpoint."""
    path: CampaignsListOrgCampaignsRequestPath
    query: CampaignsListOrgCampaignsRequestQuery | None = None

# Operation: create_campaign
class CampaignsCreateCampaignRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class CampaignsCreateCampaignRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the campaign.", min_length=1, max_length=50)
    description: str = Field(default=..., description="A description of the campaign's purpose and scope.", min_length=1, max_length=255)
    ends_at: str = Field(default=..., description="The end date and time of the campaign in ISO 8601 format. The date must be in the future.", json_schema_extra={'format': 'date-time'})
    contact_link: str | None = Field(default=None, description="A URI for users to contact regarding the campaign or request assistance.", json_schema_extra={'format': 'uri'})
    code_scanning_alerts: list[CampaignsCreateCampaignBodyCodeScanningAlertsItem] | None = Field(default=None, description="An array of code scanning alert identifiers to include in this campaign. At least one alert is required if this field is provided.", min_length=1)
    generate_issues: bool | None = Field(default=None, description="Whether to automatically generate issues for each code scanning alert included in the campaign.")
class CampaignsCreateCampaignRequest(StrictModel):
    """Create a security campaign for an organization to track and remediate code scanning alerts. The authenticated user must be an owner or security manager for the organization."""
    path: CampaignsCreateCampaignRequestPath
    body: CampaignsCreateCampaignRequestBody

# Operation: get_campaign
class CampaignsGetCampaignSummaryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    campaign_number: int = Field(default=..., description="The numeric identifier for the campaign to retrieve.")
class CampaignsGetCampaignSummaryRequest(StrictModel):
    """Retrieve a specific campaign for an organization. The authenticated user must be an owner or security manager for the organization."""
    path: CampaignsGetCampaignSummaryRequestPath

# Operation: update_campaign
class CampaignsUpdateCampaignRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    campaign_number: int = Field(default=..., description="The numeric identifier of the campaign to update.")
class CampaignsUpdateCampaignRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A brief description of the campaign.", min_length=1, max_length=255)
    ends_at: str | None = Field(default=None, description="The end date and time of the campaign in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).", json_schema_extra={'format': 'date-time'})
    contact_link: str | None = Field(default=None, description="A URI pointing to contact information or resources related to the campaign.", json_schema_extra={'format': 'uri'})
    state: Literal["open", "closed"] | None = Field(default=None, description="The campaign status indicating whether it is actively accepting reports or closed.")
class CampaignsUpdateCampaignRequest(StrictModel):
    """Update an existing campaign within an organization. Requires owner or security manager permissions."""
    path: CampaignsUpdateCampaignRequestPath
    body: CampaignsUpdateCampaignRequestBody | None = None

# Operation: delete_campaign
class CampaignsDeleteCampaignRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the campaign.")
    campaign_number: int = Field(default=..., description="The numeric identifier of the campaign to delete.")
class CampaignsDeleteCampaignRequest(StrictModel):
    """Permanently delete a campaign from an organization. The authenticated user must have owner or security manager permissions for the organization."""
    path: CampaignsDeleteCampaignRequestPath

# Operation: list_code_scanning_alerts
class CodeScanningListAlertsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CodeScanningListAlertsForOrgRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort results by.")
    state: Literal["open", "closed", "dismissed", "fixed"] | None = Field(default=None, description="Filter alerts by their current state. Returns only alerts matching the specified state.")
    assignees: str | None = Field(default=None, description="Filter alerts by assignees using a comma-separated list of user handles. Use `*` to include alerts with at least one assignee, or `none` for unassigned alerts.")
class CodeScanningListAlertsForOrgRequest(StrictModel):
    """Lists code scanning alerts for the default branch across all eligible repositories in an organization. Only organization owners and security managers can access this endpoint."""
    path: CodeScanningListAlertsForOrgRequestPath
    query: CodeScanningListAlertsForOrgRequestQuery | None = None

# Operation: list_code_security_configurations_for_org
class CodeSecurityGetConfigurationsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class CodeSecurityGetConfigurationsForOrgRequestQuery(StrictModel):
    target_type: Literal["global", "all"] | None = Field(default=None, description="Filter configurations by target type. Use 'global' for organization-wide configurations or 'all' to include all configuration types.")
class CodeSecurityGetConfigurationsForOrgRequest(StrictModel):
    """Lists all code security configurations available in an organization. The authenticated user must be an administrator or security manager for the organization to use this endpoint."""
    path: CodeSecurityGetConfigurationsForOrgRequestPath
    query: CodeSecurityGetConfigurationsForOrgRequestQuery | None = None

# Operation: list_default_code_security_configurations
class CodeSecurityGetDefaultConfigurationsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the request to a specific organization.")
class CodeSecurityGetDefaultConfigurationsRequest(StrictModel):
    """Retrieves the default code security configurations for an organization. The authenticated user must be an administrator or security manager to access this endpoint."""
    path: CodeSecurityGetDefaultConfigurationsRequestPath

# Operation: detach_security_configurations
class CodeSecurityDetachConfigurationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CodeSecurityDetachConfigurationRequestBody(StrictModel):
    selected_repository_ids: list[int] | None = Field(default=None, description="Repository IDs to detach from configurations. Provide an array of up to 250 repository IDs.", min_length=1, max_length=250)
class CodeSecurityDetachConfigurationRequest(StrictModel):
    """Detach code security configurations from specified repositories. Repositories retain their current settings but are no longer managed by the configuration."""
    path: CodeSecurityDetachConfigurationRequestPath
    body: CodeSecurityDetachConfigurationRequestBody | None = None

# Operation: get_code_security_configuration
class CodeSecurityGetConfigurationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the code security configuration.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to retrieve.")
class CodeSecurityGetConfigurationRequest(StrictModel):
    """Retrieve a specific code security configuration from an organization. The authenticated user must be an administrator or security manager for the organization."""
    path: CodeSecurityGetConfigurationRequestPath

# Operation: update_code_security_configuration
class CodeSecurityUpdateConfigurationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to update.")
class CodeSecurityUpdateConfigurationRequestBodySecretScanningDelegatedBypassOptions(StrictModel):
    reviewers: list[CodeSecurityUpdateConfigurationBodySecretScanningDelegatedBypassOptionsReviewersItem] | None = Field(default=None, validation_alias="reviewers", serialization_alias="reviewers", description="The bypass reviewers for secret scanning delegated bypass. Array of reviewer identifiers.")
class CodeSecurityUpdateConfigurationRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A description of the code security configuration.", max_length=255)
    code_security: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of GitHub Code Security features.")
    dependency_graph: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of Dependency Graph.")
    dependency_graph_autosubmit_action: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of automatic dependency submission.")
    dependabot_alerts: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of Dependabot alerts.")
    dependabot_security_updates: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of Dependabot security updates.")
    dependabot_delegated_alert_dismissal: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of Dependabot delegated alert dismissal. Requires Dependabot alerts to be enabled.")
    code_scanning_default_setup: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of code scanning default setup.")
    code_scanning_delegated_alert_dismissal: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of code scanning delegated alert dismissal.")
    secret_scanning: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning.")
    secret_scanning_push_protection: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning push protection.")
    secret_scanning_delegated_bypass: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning delegated bypass.")
    secret_scanning_validity_checks: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning validity checks.")
    secret_scanning_non_provider_patterns: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning non-provider patterns.")
    secret_scanning_generic_secrets: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of Copilot secret scanning for generic secrets.")
    secret_scanning_delegated_alert_dismissal: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning delegated alert dismissal.")
    secret_scanning_extended_metadata: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of secret scanning extended metadata.")
    private_vulnerability_reporting: Literal["enabled", "disabled", "not_set"] | None = Field(default=None, description="The enablement status of private vulnerability reporting.")
    enforcement: Literal["enforced", "unenforced"] | None = Field(default=None, description="The enforcement status for the security configuration. Enforced configurations are applied to all repositories in the organization.")
    secret_scanning_delegated_bypass_options: CodeSecurityUpdateConfigurationRequestBodySecretScanningDelegatedBypassOptions | None = None
class CodeSecurityUpdateConfigurationRequest(StrictModel):
    """Update a code security configuration for an organization. Allows administrators and security managers to modify enablement status of various security features and enforcement policies."""
    path: CodeSecurityUpdateConfigurationRequestPath
    body: CodeSecurityUpdateConfigurationRequestBody | None = None

# Operation: delete_code_security_configuration
class CodeSecurityDeleteConfigurationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the configuration.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to delete.")
class CodeSecurityDeleteConfigurationRequest(StrictModel):
    """Delete a code security configuration from an organization. Repositories currently attached to the configuration will retain their settings but will no longer be associated with it."""
    path: CodeSecurityDeleteConfigurationRequestPath

# Operation: attach_security_configuration
class CodeSecurityAttachConfigurationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to attach.")
class CodeSecurityAttachConfigurationRequestBody(StrictModel):
    scope: Literal["all", "all_without_configurations", "public", "private_or_internal", "selected"] = Field(default=..., description="The scope of repositories to attach the configuration to. Use 'selected' to attach only to specific repositories identified by their IDs.")
    selected_repository_ids: list[int] | None = Field(default=None, description="An array of repository IDs to attach the configuration to. Required only when scope is set to 'selected'. Order is not significant.")
class CodeSecurityAttachConfigurationRequest(StrictModel):
    """Attach a code security configuration to repositories in an organization. Repositories already attached to a configuration will be re-attached to the specified configuration, with only free features enabled if insufficient GHAS licenses are available."""
    path: CodeSecurityAttachConfigurationRequestPath
    body: CodeSecurityAttachConfigurationRequestBody

# Operation: list_security_configuration_repositories
class CodeSecurityGetRepositoriesForConfigurationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    configuration_id: int = Field(default=..., description="The unique identifier of the code security configuration to retrieve associated repositories for.")
class CodeSecurityGetRepositoriesForConfigurationRequest(StrictModel):
    """Lists all repositories associated with a code security configuration within an organization. The authenticated user must have administrator or security manager permissions for the organization."""
    path: CodeSecurityGetRepositoriesForConfigurationRequestPath

# Operation: list_organization_codespaces
class CodespacesListInOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class CodespacesListInOrganizationRequest(StrictModel):
    """Lists all codespaces associated with a specified organization. Requires admin:org scope for OAuth apps and personal access tokens (classic)."""
    path: CodespacesListInOrganizationRequestPath

# Operation: list_organization_secrets_codespaces
class CodespacesListOrgSecretsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class CodespacesListOrgSecretsRequest(StrictModel):
    """Lists all Codespaces development environment secrets available at the organization level without revealing their encrypted values. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: CodespacesListOrgSecretsRequestPath

# Operation: get_organization_secret_codespace
class CodespacesGetOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class CodespacesGetOrgSecretRequest(StrictModel):
    """Retrieve an organization development environment secret without revealing its encrypted value. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: CodespacesGetOrgSecretRequestPath

# Operation: create_or_update_organization_secret_codespaces
class CodespacesCreateOrUpdateOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    secret_name: str = Field(default=..., description="The name of the secret to create or update.")
class CodespacesCreateOrUpdateOrgSecretRequestBody(StrictModel):
    encrypted_value: str | None = Field(default=None, description="The encrypted secret value, encrypted using LibSodium with the public key from the Get organization public key endpoint. Must be base64-encoded.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
    key_id: str | None = Field(default=None, description="The ID of the public key used to encrypt the secret value.")
    visibility: Literal["all", "private", "selected"] = Field(default=..., description="The access level for the secret. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to restrict access to specific repositories.")
    selected_repository_ids: list[int] | None = Field(default=None, description="An array of repository IDs that can access the secret. Only applicable when visibility is set to 'selected'. Order is not significant.")
class CodespacesCreateOrUpdateOrgSecretRequest(StrictModel):
    """Creates or updates an organization development environment secret with an encrypted value. The secret value must be encrypted using LibSodium with the organization's public key before submission."""
    path: CodespacesCreateOrUpdateOrgSecretRequestPath
    body: CodespacesCreateOrUpdateOrgSecretRequestBody

# Operation: delete_organization_secret_codespace
class CodespacesDeleteOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to delete.")
class CodespacesDeleteOrgSecretRequest(StrictModel):
    """Deletes a development environment secret from an organization by name. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: CodespacesDeleteOrgSecretRequestPath

# Operation: list_organization_secret_repositories_codespaces
class CodespacesListSelectedReposForOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret for which to list authorized repositories.")
class CodespacesListSelectedReposForOrgSecretRequest(StrictModel):
    """Lists all repositories that have been granted access to an organization secret when visibility is restricted to selected repositories. Requires admin:org scope for authentication."""
    path: CodespacesListSelectedReposForOrgSecretRequestPath

# Operation: update_organization_secret_repositories_codespaces
class CodespacesSetSelectedReposForOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret to configure repository access for.")
class CodespacesSetSelectedReposForOrgSecretRequestBody(StrictModel):
    selected_repository_ids: list[int] = Field(default=..., description="An array of repository IDs that should have access to this organization secret. Only applicable when the secret's visibility is set to 'selected'. This replaces all previously authorized repositories.")
class CodespacesSetSelectedReposForOrgSecretRequest(StrictModel):
    """Replace all repositories that can access an organization development environment secret. This operation applies only when the secret's visibility is set to 'selected'."""
    path: CodespacesSetSelectedReposForOrgSecretRequestPath
    body: CodespacesSetSelectedReposForOrgSecretRequestBody

# Operation: add_repository_to_organization_secret
class CodespacesAddSelectedRepoToOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret to which the repository will be granted access.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to add to the secret's access list.")
class CodespacesAddSelectedRepoToOrgSecretRequest(StrictModel):
    """Grants a repository access to an organization development environment secret when the secret's visibility is restricted to selected repositories. The repository must be within the organization."""
    path: CodespacesAddSelectedRepoToOrgSecretRequestPath

# Operation: remove_repository_from_organization_secret_codespaces
class CodespacesRemoveSelectedRepoFromOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret to modify.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the secret's access list.")
class CodespacesRemoveSelectedRepoFromOrgSecretRequest(StrictModel):
    """Removes a repository from an organization Codespaces secret when repository access is restricted to selected repositories. Requires admin:org scope for authentication."""
    path: CodespacesRemoveSelectedRepoFromOrgSecretRequestPath

# Operation: get_copilot_billing
class CopilotGetCopilotOrganizationDetailsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CopilotGetCopilotOrganizationDetailsRequest(StrictModel):
    """Retrieve Copilot subscription details for an organization, including seat allocation and feature policies. Only organization owners can access this information."""
    path: CopilotGetCopilotOrganizationDetailsRequestPath

# Operation: list_copilot_seats
class CopilotListCopilotSeatsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the seat billing query to a specific organization.")
class CopilotListCopilotSeatsRequest(StrictModel):
    """Retrieve all Copilot seat assignments currently being billed for an organization with a Copilot Business or Copilot Enterprise subscription. Only organization owners can access this information, which includes each user's most recent Copilot activity data."""
    path: CopilotListCopilotSeatsRequestPath

# Operation: grant_copilot_seats_to_teams
class CopilotAddCopilotSeatsForTeamsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class CopilotAddCopilotSeatsForTeamsRequestBody(StrictModel):
    selected_teams: list[str] = Field(default=..., description="List of team names within the organization to grant Copilot access to. Teams are processed in the order provided.", min_length=1)
class CopilotAddCopilotSeatsForTeamsRequest(StrictModel):
    """Purchases GitHub Copilot seats for all users within specified teams in an organization. The organization will be billed per seat based on its Copilot plan."""
    path: CopilotAddCopilotSeatsForTeamsRequestPath
    body: CopilotAddCopilotSeatsForTeamsRequestBody

# Operation: revoke_copilot_access_from_teams
class CopilotCancelCopilotSeatAssignmentForTeamsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CopilotCancelCopilotSeatAssignmentForTeamsRequestBody(StrictModel):
    selected_teams: list[str] = Field(default=..., description="The names of teams to revoke Copilot access from. Provide at least one team name.", min_length=1)
class CopilotCancelCopilotSeatAssignmentForTeamsRequest(StrictModel):
    """Remove teams from an organization's Copilot subscription, setting their members' seats to pending cancellation. Members will lose Copilot access at the end of the current billing cycle unless they retain access through another team."""
    path: CopilotCancelCopilotSeatAssignmentForTeamsRequestPath
    body: CopilotCancelCopilotSeatAssignmentForTeamsRequestBody

# Operation: grant_copilot_seats_to_users
class CopilotAddCopilotSeatsForUsersRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CopilotAddCopilotSeatsForUsersRequestBody(StrictModel):
    selected_usernames: list[str] = Field(default=..., description="The usernames of organization members to grant Copilot access to. Provide at least one username.", min_length=1)
class CopilotAddCopilotSeatsForUsersRequest(StrictModel):
    """Purchases GitHub Copilot seats for specified organization members. The organization will be billed based on its Copilot plan and must have a Business or Enterprise subscription with a configured suggestion matching policy."""
    path: CopilotAddCopilotSeatsForUsersRequestPath
    body: CopilotAddCopilotSeatsForUsersRequestBody

# Operation: revoke_copilot_seat_assignments
class CopilotCancelCopilotSeatAssignmentForUsersRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class CopilotCancelCopilotSeatAssignmentForUsersRequestBody(StrictModel):
    selected_usernames: list[str] = Field(default=..., description="The usernames of organization members whose Copilot access should be revoked. Provide at least one username.", min_length=1)
class CopilotCancelCopilotSeatAssignmentForUsersRequest(StrictModel):
    """Remove specified users from the organization's Copilot subscription by setting their seats to pending cancellation. Users will lose Copilot access at the end of the current billing cycle unless they retain access through team membership."""
    path: CopilotCancelCopilotSeatAssignmentForUsersRequestPath
    body: CopilotCancelCopilotSeatAssignmentForUsersRequestBody

# Operation: list_copilot_coding_agent_permissions
class CopilotGetCopilotCodingAgentPermissionsOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class CopilotGetCopilotCodingAgentPermissionsOrganizationRequest(StrictModel):
    """Retrieve the Copilot coding agent permission settings for an organization, showing which repositories have the agent enabled or disabled. Organization owners use this to view their current Copilot coding agent configuration across repositories."""
    path: CopilotGetCopilotCodingAgentPermissionsOrganizationRequestPath

# Operation: list_copilot_coding_agent_repositories
class CopilotListCopilotCodingAgentSelectedRepositoriesForOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
class CopilotListCopilotCodingAgentSelectedRepositoriesForOrganizationRequest(StrictModel):
    """Lists repositories enabled for Copilot coding agent in an organization when the repository policy is set to selected. Organization owners can use this endpoint to view which repositories have Copilot coding agent access enabled."""
    path: CopilotListCopilotCodingAgentSelectedRepositoriesForOrganizationRequestPath

# Operation: enable_copilot_coding_agent_for_repository
class CopilotEnableCopilotCodingAgentForRepositoryInOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to enable for Copilot coding agent.")
class CopilotEnableCopilotCodingAgentForRepositoryInOrganizationRequest(StrictModel):
    """Enable a repository for Copilot coding agent in an organization. This operation adds a repository to the list of selected repositories when the organization's coding agent repository policy is set to 'selected'."""
    path: CopilotEnableCopilotCodingAgentForRepositoryInOrganizationRequestPath

# Operation: list_copilot_content_exclusions
class CopilotCopilotContentExclusionForOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the content exclusion rules to a specific organization.")
class CopilotCopilotContentExclusionForOrganizationRequest(StrictModel):
    """Retrieve Copilot content exclusion path rules configured for an organization. This endpoint allows organization owners to view which paths are excluded from GitHub Copilot."""
    path: CopilotCopilotContentExclusionForOrganizationRequestPath

# Operation: get_copilot_metrics
class CopilotCopilotMetricsForOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class CopilotCopilotMetricsForOrganizationRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Start date for the metrics query in ISO 8601 format. Maximum lookback is 100 days ago.")
    until: str | None = Field(default=None, description="End date for the metrics query in ISO 8601 format. Must not precede the start date if provided.")
class CopilotCopilotMetricsForOrganizationRequest(StrictModel):
    """Retrieve aggregated GitHub Copilot usage metrics for an organization over a specified date range. Metrics are available for up to 100 days prior and only include data when the organization had five or more active Copilot license holders."""
    path: CopilotCopilotMetricsForOrganizationRequestPath
    query: CopilotCopilotMetricsForOrganizationRequestQuery | None = None

# Operation: list_organization_dependabot_alerts
class DependabotListAlertsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class DependabotListAlertsForOrgRequestQuery(StrictModel):
    state: str | None = Field(default=None, description="Filter alerts by their current state. Specify as comma-separated values to return alerts matching any of the provided states.")
    ecosystem: str | None = Field(default=None, description="Filter alerts by package ecosystem. Specify as comma-separated values to return alerts for packages in any of the provided ecosystems.")
    package: str | None = Field(default=None, description="Filter alerts by package name. Specify as comma-separated values to return alerts for any of the provided packages.")
    epss_percentage: str | None = Field(default=None, description="Filter alerts by CVE Exploit Prediction Scoring System (EPSS) percentage. Supports exact values, comparison operators (>, <, >=, <=), or ranges (e.g., 0.5..0.9) with values between 0.0 and 1.0.")
    has: str | list[Literal["patch", "deployment"]] | None = Field(default=None, description="Filter alerts based on specific attributes they possess. Multiple filters can be combined to return only alerts matching all specified criteria.")
    runtime_risk: str | None = Field(default=None, description="Filter alerts by runtime risk level. Specify as comma-separated values to return alerts for repositories with deployment records matching any of the provided risk types.")
    scope: Literal["development", "runtime"] | None = Field(default=None, description="Filter alerts by the scope of the vulnerable dependency (development or runtime dependencies).")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order.")
class DependabotListAlertsForOrgRequest(StrictModel):
    """Retrieve Dependabot security alerts for an organization with filtering options by state, ecosystem, package, and risk factors. Requires organization owner or security manager permissions."""
    path: DependabotListAlertsForOrgRequestPath
    query: DependabotListAlertsForOrgRequestQuery | None = None

# Operation: list_organization_secrets_dependabot
class DependabotListOrgSecretsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class DependabotListOrgSecretsRequest(StrictModel):
    """Lists all secrets available in an organization without revealing their encrypted values. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: DependabotListOrgSecretsRequestPath

# Operation: get_organization_dependabot_public_key
class DependabotGetOrgPublicKeyRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class DependabotGetOrgPublicKeyRequest(StrictModel):
    """Retrieves the public key for an organization's Dependabot secrets. This key is required to encrypt secrets before creating or updating them in Dependabot configuration."""
    path: DependabotGetOrgPublicKeyRequestPath

# Operation: get_organization_secret_dependabot
class DependabotGetOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class DependabotGetOrgSecretRequest(StrictModel):
    """Retrieve a single organization secret without revealing its encrypted value. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: DependabotGetOrgSecretRequestPath

# Operation: create_or_update_organization_secret_dependabot
class DependabotCreateOrUpdateOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to create or update.")
class DependabotCreateOrUpdateOrgSecretRequestBody(StrictModel):
    encrypted_value: str | None = Field(default=None, description="The encrypted secret value, encrypted using LibSodium with the public key from the Get organization public key endpoint. Must be base64-encoded.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
    key_id: str | None = Field(default=None, description="The ID of the public key used to encrypt the secret value.")
    visibility: Literal["all", "private", "selected"] = Field(default=..., description="The visibility scope for the secret. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to restrict access to specific repositories.")
    selected_repository_ids: list[int | str] | None = Field(default=None, description="An array of repository IDs that can access the secret. Only applicable when visibility is set to 'selected'. Manage this list using the related repository selection endpoints.")
class DependabotCreateOrUpdateOrgSecretRequest(StrictModel):
    """Creates or updates an organization secret for Dependabot with an encrypted value. The secret value must be encrypted using LibSodium with the organization's public key before submission."""
    path: DependabotCreateOrUpdateOrgSecretRequestPath
    body: DependabotCreateOrUpdateOrgSecretRequestBody

# Operation: delete_organization_secret_dependabot
class DependabotDeleteOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the Dependabot secret to delete.")
class DependabotDeleteOrgSecretRequest(StrictModel):
    """Deletes a Dependabot secret from an organization by its name. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: DependabotDeleteOrgSecretRequestPath

# Operation: list_organization_secret_repositories_dependabot
class DependabotListSelectedReposForOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the Dependabot secret for which to list authorized repositories.")
class DependabotListSelectedReposForOrgSecretRequest(StrictModel):
    """Lists all repositories that have been granted access to an organization secret when visibility is set to selected. Requires admin:org scope for authentication."""
    path: DependabotListSelectedReposForOrgSecretRequestPath

# Operation: update_organization_secret_repositories_dependabot
class DependabotSetSelectedReposForOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the Dependabot secret to configure repository access for.")
class DependabotSetSelectedReposForOrgSecretRequestBody(StrictModel):
    selected_repository_ids: list[int] = Field(default=..., description="An array of repository IDs that should have access to this organization secret. Only applicable when secret visibility is set to 'selected'. This list completely replaces any previously configured repositories.")
class DependabotSetSelectedReposForOrgSecretRequest(StrictModel):
    """Replace all repositories that can access an organization Dependabot secret. This operation applies only when the secret's visibility is set to 'selected'. Requires admin:org scope."""
    path: DependabotSetSelectedReposForOrgSecretRequestPath
    body: DependabotSetSelectedReposForOrgSecretRequestBody

# Operation: add_repository_to_organization_secret_dependabot
class DependabotAddSelectedRepoToOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the organization secret to grant repository access to.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to add to the organization secret.")
class DependabotAddSelectedRepoToOrgSecretRequest(StrictModel):
    """Grants a repository access to an organization secret when the secret's visibility is restricted to selected repositories. The repository must be granted access before it can use the secret in workflows."""
    path: DependabotAddSelectedRepoToOrgSecretRequestPath

# Operation: remove_repository_from_organization_secret_dependabot
class DependabotRemoveSelectedRepoFromOrgSecretRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the Dependabot secret to modify.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the secret's access list.")
class DependabotRemoveSelectedRepoFromOrgSecretRequest(StrictModel):
    """Remove a repository from an organization Dependabot secret when visibility is set to selected repositories. Requires admin:org scope for authentication."""
    path: DependabotRemoveSelectedRepoFromOrgSecretRequestPath

# Operation: list_docker_migration_conflicts
class PackagesListDockerMigrationConflictingPackagesForOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization whose conflicting packages should be listed.")
class PackagesListDockerMigrationConflictingPackagesForOrganizationRequest(StrictModel):
    """Retrieves all packages in an organization that encountered conflicts during Docker migration and are readable by the requesting user. Requires `read:packages` OAuth scope."""
    path: PackagesListDockerMigrationConflictingPackagesForOrganizationRequestPath

# Operation: list_organization_events
class ActivityListPublicOrgEventsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The lookup is case-insensitive.")
class ActivityListPublicOrgEventsRequest(StrictModel):
    """Retrieve a list of public events for an organization. Note: This API is not optimized for real-time use cases and may have latency ranging from 30 seconds to 6 hours depending on the time of day."""
    path: ActivityListPublicOrgEventsRequestPath

# Operation: list_failed_invitations
class OrgsListFailedInvitationsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class OrgsListFailedInvitationsRequest(StrictModel):
    """Retrieve a list of failed organization invitations with details about when and why each invitation failed. Each result includes the failure timestamp and reason."""
    path: OrgsListFailedInvitationsRequestPath

# Operation: list_webhooks
class OrgsListWebhooksRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the webhook list to a specific organization.")
class OrgsListWebhooksRequest(StrictModel):
    """Retrieve all webhooks configured for an organization. The authenticated user must be an organization owner, and OAuth tokens require the `admin:org_hook` scope."""
    path: OrgsListWebhooksRequestPath

# Operation: create_webhook
class OrgsCreateWebhookRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class OrgsCreateWebhookRequestBodyConfig(StrictModel):
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The URL endpoint where webhook payloads will be delivered.", json_schema_extra={'format': 'uri'})
    content_type: str | None = Field(default=None, validation_alias="content_type", serialization_alias="content_type", description="The serialization format for webhook payloads. Defaults to 'form' if not specified.")
    secret: str | None = Field(default=None, validation_alias="secret", serialization_alias="secret", description="An optional secret used to generate HMAC signatures for verifying webhook authenticity in delivery headers.")
class OrgsCreateWebhookRequestBody(StrictModel):
    name: str = Field(default=..., description="The webhook type. Must be set to 'web' for standard webhook delivery.")
    active: bool | None = Field(default=None, description="Whether the webhook is active and will send notifications when triggered. Defaults to true.")
    config: OrgsCreateWebhookRequestBodyConfig
class OrgsCreateWebhookRequest(StrictModel):
    """Create a webhook for an organization that delivers JSON payloads to a specified URL. Requires organization owner permissions and appropriate OAuth or personal access token scopes."""
    path: OrgsCreateWebhookRequestPath
    body: OrgsCreateWebhookRequestBody

# Operation: get_organization_webhook
class OrgsGetWebhookRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the webhook lookup.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the X-GitHub-Hook-ID header of webhook delivery payloads.")
class OrgsGetWebhookRequest(StrictModel):
    """Retrieve a specific webhook configured in an organization. Requires organization owner permissions and appropriate OAuth scopes to access webhook details."""
    path: OrgsGetWebhookRequestPath

# Operation: update_webhook
class OrgsUpdateWebhookRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook, found in the X-GitHub-Hook-ID header of webhook deliveries.")
class OrgsUpdateWebhookRequestBodyConfig(StrictModel):
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The URL where webhook payloads will be delivered.", json_schema_extra={'format': 'uri'})
    content_type: str | None = Field(default=None, validation_alias="content_type", serialization_alias="content_type", description="The media type for serializing payloads. Supported values are `json` and `form`. Defaults to `form`.")
    secret: str | None = Field(default=None, validation_alias="secret", serialization_alias="secret", description="An optional secret used to generate HMAC hex digest values for delivery signature headers, enabling payload verification.")
class OrgsUpdateWebhookRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Whether to send notifications when the webhook is triggered. Set to `true` to enable.")
    config: OrgsUpdateWebhookRequestBodyConfig
class OrgsUpdateWebhookRequest(StrictModel):
    """Updates an organization webhook's configuration, including URL, content type, secret, and active status. The secret will be overwritten if provided; you must resubmit the existing secret or set a new one to avoid removal."""
    path: OrgsUpdateWebhookRequestPath
    body: OrgsUpdateWebhookRequestBody

# Operation: delete_webhook
class OrgsDeleteWebhookRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the webhook.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook to delete. This value can be found in the `X-GitHub-Hook-ID` header of webhook delivery events.")
class OrgsDeleteWebhookRequest(StrictModel):
    """Delete a webhook from an organization. The authenticated user must be an organization owner, and the request requires `admin:org_hook` scope."""
    path: OrgsDeleteWebhookRequestPath

# Operation: get_webhook_config_organization
class OrgsGetWebhookConfigForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the webhook configuration lookup.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the X-GitHub-Hook-ID header of webhook delivery payloads.")
class OrgsGetWebhookConfigForOrgRequest(StrictModel):
    """Retrieve the webhook configuration for an organization, including URL, content type, and SSL verification settings. Requires organization owner permissions and appropriate OAuth or personal access token scopes."""
    path: OrgsGetWebhookConfigForOrgRequestPath

# Operation: update_webhook_config
class OrgsUpdateWebhookConfigForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook, found in the X-GitHub-Hook-ID header of webhook deliveries.")
class OrgsUpdateWebhookConfigForOrgRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The URL where webhook payloads will be delivered.", json_schema_extra={'format': 'uri'})
    content_type: str | None = Field(default=None, description="The media type for serializing payloads. Supported values are json and form, with form as the default.")
    secret: str | None = Field(default=None, description="A secret key used to generate HMAC hex digest values for delivery signature headers, enabling payload verification.")
class OrgsUpdateWebhookConfigForOrgRequest(StrictModel):
    """Updates the webhook configuration for an organization, including the delivery URL, payload format, and signature secret. Only organization owners can perform this operation."""
    path: OrgsUpdateWebhookConfigForOrgRequestPath
    body: OrgsUpdateWebhookConfigForOrgRequestBody | None = None

# Operation: list_webhook_deliveries_organization
class OrgsListWebhookDeliveriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the webhook to a specific organization.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the X-GitHub-Hook-ID header of any webhook delivery from this hook.")
class OrgsListWebhookDeliveriesRequest(StrictModel):
    """Retrieve a list of webhook deliveries for an organization webhook. Returns delivery records including status, timestamps, and payload information for debugging webhook integrations."""
    path: OrgsListWebhookDeliveriesRequestPath

# Operation: get_webhook_delivery_organization
class OrgsGetWebhookDeliveryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the webhook.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the X-GitHub-Hook-ID header of any webhook delivery from this hook.")
    delivery_id: str = Field(default=..., description="The unique identifier of the specific webhook delivery to retrieve.", json_schema_extra={'format': 'int64'})
class OrgsGetWebhookDeliveryRequest(StrictModel):
    """Retrieve a specific webhook delivery for an organization webhook. Returns detailed information about a single webhook delivery event, including request and response data."""
    path: OrgsGetWebhookDeliveryRequestPath

# Operation: redeliver_webhook_delivery_organization
class OrgsRedeliverWebhookDeliveryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the webhook.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the X-GitHub-Hook-ID header of any webhook delivery from this hook.")
    delivery_id: str = Field(default=..., description="The unique identifier of the specific webhook delivery to redeliver.", json_schema_extra={'format': 'int64'})
class OrgsRedeliverWebhookDeliveryRequest(StrictModel):
    """Redeliver a previously failed or missed webhook delivery for an organization webhook. Requires organization owner permissions and appropriate OAuth or personal access token scopes."""
    path: OrgsRedeliverWebhookDeliveryRequestPath

# Operation: list_api_request_stats
class ApiInsightsGetSubjectStatsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ApiInsightsGetSubjectStatsRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for statistics. Specify as an ISO 8601 timestamp.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for statistics. Specify as an ISO 8601 timestamp. If not provided, defaults to 30 days before the minimum timestamp.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort order for results.")
    subject_name_substring: str | None = Field(default=None, description="Filter results to subjects whose names contain this substring. The search is case-insensitive.")
class ApiInsightsGetSubjectStatsRequest(StrictModel):
    """Retrieve API request statistics for all subjects (users or GitHub Apps) within an organization during a specified time period. Use this to analyze API usage patterns and identify top consumers."""
    path: ApiInsightsGetSubjectStatsRequestPath
    query: ApiInsightsGetSubjectStatsRequestQuery

# Operation: get_api_summary_stats
class ApiInsightsGetSummaryStatsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization identifier. Organization names are case-insensitive.")
class ApiInsightsGetSummaryStatsRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for statistics retrieval. Specify as an ISO 8601 formatted timestamp.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for statistics retrieval. Specify as an ISO 8601 formatted timestamp. If omitted, defaults to 30 days before the minimum timestamp.")
class ApiInsightsGetSummaryStatsRequest(StrictModel):
    """Retrieve aggregated API request statistics for an organization across all users and applications within a specified time period."""
    path: ApiInsightsGetSummaryStatsRequestPath
    query: ApiInsightsGetSummaryStatsRequestQuery

# Operation: get_api_stats_by_actor
class ApiInsightsGetSummaryStatsByActorRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    actor_type: Literal["installation", "classic_pat", "fine_grained_pat", "oauth_app", "github_app_user_to_server"] = Field(default=..., description="The type of actor making the API requests.")
    actor_id: int = Field(default=..., description="The unique identifier of the actor.")
class ApiInsightsGetSummaryStatsByActorRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for statistics. Use ISO 8601 format.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for statistics. Use ISO 8601 format. If not provided, defaults to 30 days before the minimum timestamp.")
class ApiInsightsGetSummaryStatsByActorRequest(StrictModel):
    """Retrieve API request statistics for a specific actor within an organization over a specified time period. Actors can be GitHub App installations, OAuth apps, or tokens acting on behalf of a user."""
    path: ApiInsightsGetSummaryStatsByActorRequestPath
    query: ApiInsightsGetSummaryStatsByActorRequestQuery

# Operation: get_api_request_stats
class ApiInsightsGetTimeStatsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class ApiInsightsGetTimeStatsRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for statistics retrieval in ISO 8601 format.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for statistics retrieval in ISO 8601 format. Defaults to 30 days before min_timestamp if not provided.")
    timestamp_increment: str = Field(default=..., description="The time interval used to aggregate statistics (e.g., 5m, 10m, 1h). Determines the granularity of the returned data.")
class ApiInsightsGetTimeStatsRequest(StrictModel):
    """Retrieve API request and rate-limit statistics for an organization over a specified time period, broken down by configurable time intervals."""
    path: ApiInsightsGetTimeStatsRequestPath
    query: ApiInsightsGetTimeStatsRequestQuery

# Operation: get_user_api_time_stats
class ApiInsightsGetTimeStatsByUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    user_id: str = Field(default=..., description="The unique identifier of the user for which to retrieve API statistics.")
class ApiInsightsGetTimeStatsByUserRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for querying statistics. Must be in ISO 8601 format.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for querying statistics. Defaults to 30 days before min_timestamp if not provided. Must be in ISO 8601 format.")
    timestamp_increment: str = Field(default=..., description="The time interval used to aggregate statistics in the results (e.g., 5m, 10m, 1h). Determines the granularity of the breakdown.")
class ApiInsightsGetTimeStatsByUserRequest(StrictModel):
    """Retrieve API request and rate-limit statistics for a specific user within an organization over a specified time period, broken down by configurable time increments."""
    path: ApiInsightsGetTimeStatsByUserRequestPath
    query: ApiInsightsGetTimeStatsByUserRequestQuery

# Operation: get_api_request_stats_by_actor
class ApiInsightsGetTimeStatsByActorRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    actor_type: Literal["installation", "classic_pat", "fine_grained_pat", "oauth_app", "github_app_user_to_server"] = Field(default=..., description="The type of actor making the API requests.")
    actor_id: int = Field(default=..., description="The unique identifier of the actor.")
class ApiInsightsGetTimeStatsByActorRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for querying statistics. Must be in ISO 8601 format.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for querying statistics. Defaults to 30 days before min_timestamp if not provided. Must be in ISO 8601 format.")
    timestamp_increment: str = Field(default=..., description="The time interval used to aggregate statistics in the results (e.g., 5m, 10m, 1h). Determines the granularity of the breakdown.")
class ApiInsightsGetTimeStatsByActorRequest(StrictModel):
    """Retrieve API request and rate-limit statistics for a specific actor within an organization over a specified time period. Results can be broken down into configurable time intervals."""
    path: ApiInsightsGetTimeStatsByActorRequestPath
    query: ApiInsightsGetTimeStatsByActorRequestQuery

# Operation: get_user_api_stats_by_access_type
class ApiInsightsGetUserStatsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    user_id: str = Field(default=..., description="The unique identifier of the user whose API statistics should be retrieved.")
class ApiInsightsGetUserStatsRequestQuery(StrictModel):
    min_timestamp: str = Field(default=..., description="The start of the time range for which to retrieve statistics. Must be in ISO 8601 format.")
    max_timestamp: str | None = Field(default=None, description="The end of the time range for which to retrieve statistics. Defaults to 30 days before the current time if not provided. Must be in ISO 8601 format.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort order for results.")
    actor_name_substring: str | None = Field(default=None, description="Filter results to include only records where the actor name contains this substring. The search is case-insensitive.")
class ApiInsightsGetUserStatsRequest(StrictModel):
    """Retrieve API usage statistics for a specific user within an organization, broken down by access type over a specified time period."""
    path: ApiInsightsGetUserStatsRequestPath
    query: ApiInsightsGetUserStatsRequestQuery

# Operation: get_app_organization_installation
class AppsGetOrgInstallationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class AppsGetOrgInstallationRequest(StrictModel):
    """Retrieve the installation details of an authenticated GitHub App within a specific organization. Requires JWT authentication as a GitHub App."""
    path: AppsGetOrgInstallationRequestPath

# Operation: list_app_installations_organization
class OrgsListAppInstallationsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsListAppInstallationsRequest(StrictModel):
    """Lists all GitHub Apps installed in an organization, including those installed on repositories within the organization. The authenticated user must be an organization owner, and requires admin:read scope for OAuth or classic personal access tokens."""
    path: OrgsListAppInstallationsRequestPath

# Operation: get_organization_interaction_restrictions
class InteractionsGetRestrictionsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class InteractionsGetRestrictionsForOrgRequest(StrictModel):
    """Retrieve the current interaction restrictions for an organization, including which types of GitHub users can interact and when the restriction expires. Returns an empty response if no restrictions are active."""
    path: InteractionsGetRestrictionsForOrgRequestPath

# Operation: list_pending_invitations
class OrgsListPendingInvitationsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsListPendingInvitationsRequestQuery(StrictModel):
    role: Literal["all", "admin", "direct_member", "billing_manager", "hiring_manager"] | None = Field(default=None, description="Filter invitations by the member role they were invited as.")
    invitation_source: Literal["all", "member", "scim"] | None = Field(default=None, description="Filter invitations by their source (member-initiated or SCIM-provisioned).")
class OrgsListPendingInvitationsRequest(StrictModel):
    """Retrieve all pending organization invitations with optional filtering by member role or invitation source. The response includes role information (direct_member, admin, billing_manager, or hiring_manager) and login details, which may be null for non-GitHub members."""
    path: OrgsListPendingInvitationsRequestPath
    query: OrgsListPendingInvitationsRequestQuery | None = None

# Operation: invite_organization_member
class OrgsCreateInvitationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class OrgsCreateInvitationRequestBody(StrictModel):
    role: Literal["admin", "direct_member", "billing_manager", "reinstate"] | None = Field(default=None, description="The role to assign to the invited member. Use 'admin' for full administrative access, 'direct_member' for standard membership, 'billing_manager' for billing-only access, or 'reinstate' to restore a previously held role.")
    team_ids: list[int] | None = Field(default=None, description="An array of team IDs to automatically add the invited member to upon acceptance. The order of IDs is not significant.")
class OrgsCreateInvitationRequest(StrictModel):
    """Invite a person to join an organization by their GitHub user ID or email address. Only organization owners can create invitations. Note that this operation triggers notifications and is subject to secondary rate limiting."""
    path: OrgsCreateInvitationRequestPath
    body: OrgsCreateInvitationRequestBody | None = None

# Operation: cancel_invitation
class OrgsCancelInvitationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    invitation_id: int = Field(default=..., description="The unique identifier of the invitation to cancel.")
class OrgsCancelInvitationRequest(StrictModel):
    """Cancel a pending organization invitation. The authenticated user must be an organization owner to perform this action. This operation triggers notifications to relevant users."""
    path: OrgsCancelInvitationRequestPath

# Operation: list_invitation_teams
class OrgsListInvitationTeamsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    invitation_id: int = Field(default=..., description="The unique identifier of the invitation to retrieve associated teams for.")
class OrgsListInvitationTeamsRequest(StrictModel):
    """Retrieve all teams associated with an organization invitation. The authenticated user must be an organization owner to view invitation details."""
    path: OrgsListInvitationTeamsRequestPath

# Operation: list_issue_fields
class OrgsListIssueFieldsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsListIssueFieldsRequest(StrictModel):
    """Retrieves all issue fields configured for an organization. Requires read:org scope for OAuth app tokens and personal access tokens (classic)."""
    path: OrgsListIssueFieldsRequestPath

# Operation: create_issue_field
class OrgsCreateIssueFieldRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class OrgsCreateIssueFieldRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the issue field.")
    description: str | None = Field(default=None, description="A description of the issue field's purpose and usage.")
    data_type: Literal["text", "date", "single_select", "number"] = Field(default=..., description="The data type that determines what kind of values this field can store.")
    visibility: Literal["organization_members_only", "all"] | None = Field(default=None, description="Controls who can see this field. Defaults to `organization_members_only` if not specified.")
    options: list[OrgsCreateIssueFieldBodyOptionsItem] | None = Field(default=None, description="An array of predefined options for single select fields. Required when `data_type` is `single_select`. Each option should be a distinct value.")
class OrgsCreateIssueFieldRequest(StrictModel):
    """Creates a new custom issue field for an organization. The authenticated user must be an organization administrator with the `admin:org` scope."""
    path: OrgsCreateIssueFieldRequestPath
    body: OrgsCreateIssueFieldRequestBody

# Operation: delete_issue_field
class OrgsDeleteIssueFieldRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    issue_field_id: int = Field(default=..., description="The unique identifier of the issue field to delete.")
class OrgsDeleteIssueFieldRequest(StrictModel):
    """Deletes a custom issue field from an organization. The authenticated user must be an organization administrator with the `admin:org` scope to perform this action."""
    path: OrgsDeleteIssueFieldRequestPath

# Operation: list_issue_types
class OrgsListIssueTypesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The lookup is case-insensitive.")
class OrgsListIssueTypesRequest(StrictModel):
    """Retrieves all issue types configured for a specified organization. Requires read:org scope for OAuth app tokens and personal access tokens (classic)."""
    path: OrgsListIssueTypesRequestPath

# Operation: create_issue_type
class OrgsCreateIssueTypeRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsCreateIssueTypeRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the issue type to create.")
    is_enabled: bool = Field(default=..., description="Whether the issue type is enabled and available for use at the organization level.")
    description: str | None = Field(default=None, description="An optional description explaining the purpose or usage of the issue type.")
    color: Literal["gray", "blue", "green", "yellow", "orange", "red", "pink", "purple"] | None = Field(default=None, description="An optional color label for visual identification of the issue type.")
class OrgsCreateIssueTypeRequest(StrictModel):
    """Create a new issue type for an organization. The authenticated user must be an organization administrator with the `admin:org` scope to use this endpoint."""
    path: OrgsCreateIssueTypeRequestPath
    body: OrgsCreateIssueTypeRequestBody

# Operation: delete_issue_type
class OrgsDeleteIssueTypeRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    issue_type_id: int = Field(default=..., description="The unique identifier of the issue type to delete.")
class OrgsDeleteIssueTypeRequest(StrictModel):
    """Deletes an issue type from an organization. The authenticated user must be an organization administrator with the `admin:org` scope to perform this action."""
    path: OrgsDeleteIssueTypeRequestPath

# Operation: list_organization_issues
class IssuesListForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class IssuesListForOrgRequestQuery(StrictModel):
    filter_: Literal["assigned", "created", "mentioned", "subscribed", "repos", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter issues by type of involvement: assigned to you, created by you, mentioning you, subscribed to, or all visible issues.")
    state: Literal["open", "closed", "all"] | None = Field(default=None, description="Filter issues by their current state: open, closed, or all states.")
    labels: str | None = Field(default=None, description="Filter by one or more labels using comma-separated values.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter by issue type name.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order.")
    since: str | None = Field(default=None, description="Only return issues last updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class IssuesListForOrgRequest(StrictModel):
    """List issues and pull requests in an organization that are assigned to the authenticated user. Note that GitHub's REST API treats pull requests as issues; use the `pull_request` key to distinguish them."""
    path: IssuesListForOrgRequestPath
    query: IssuesListForOrgRequestQuery | None = None

# Operation: list_organization_members
class OrgsListMembersRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class OrgsListMembersRequestQuery(StrictModel):
    filter_: Literal["2fa_disabled", "2fa_insecure", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter members by two-factor authentication status. Use '2fa_disabled' to show members without 2FA enabled, '2fa_insecure' to show members with insecure 2FA methods, or 'all' for no filtering. Only available to organization owners.")
    role: Literal["all", "admin", "member"] | None = Field(default=None, description="Filter members by their role within the organization.")
class OrgsListMembersRequest(StrictModel):
    """Retrieve all members of an organization. Authenticated members can see both public and concealed members, while others see only public members. Results can be filtered by security status or role."""
    path: OrgsListMembersRequestPath
    query: OrgsListMembersRequestQuery | None = None

# Operation: check_organization_membership
class OrgsCheckMembershipForUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub username handle to check for membership.")
class OrgsCheckMembershipForUserRequest(StrictModel):
    """Verify whether a user is a member of an organization, including both public and private membership status."""
    path: OrgsCheckMembershipForUserRequestPath

# Operation: list_organization_member_codespaces
class CodespacesGetCodespacesForUserInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle for the organization member.")
class CodespacesGetCodespacesForUserInOrgRequest(StrictModel):
    """Lists all codespaces that a member of an organization has for repositories within that organization. Requires admin:org scope for authentication."""
    path: CodespacesGetCodespacesForUserInOrgRequestPath

# Operation: delete_codespace_from_organization
class CodespacesDeleteFromOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle whose codespace will be deleted.")
    codespace_name: str = Field(default=..., description="The name of the codespace to delete.")
class CodespacesDeleteFromOrganizationRequest(StrictModel):
    """Delete a user's codespace from the organization. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: CodespacesDeleteFromOrganizationRequestPath

# Operation: stop_codespace
class CodespacesStopInOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle.")
    codespace_name: str = Field(default=..., description="The name of the codespace to stop.")
class CodespacesStopInOrganizationRequest(StrictModel):
    """Stop a running codespace for an organization member. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: CodespacesStopInOrganizationRequestPath

# Operation: get_copilot_seat_details
class CopilotGetCopilotSeatDetailsForUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the GitHub organization.")
    username: str = Field(default=..., description="The GitHub user account handle. Identifies the organization member whose Copilot seat details should be retrieved.")
class CopilotGetCopilotSeatDetailsForUserRequest(StrictModel):
    """Retrieve GitHub Copilot seat assignment details for an organization member, including their most recent activity data. Only organization owners can access this information."""
    path: CopilotGetCopilotSeatDetailsForUserRequestPath

# Operation: get_organization_membership
class OrgsGetMembershipForUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
    username: str = Field(default=..., description="The GitHub username (handle) of the user whose membership to retrieve.")
class OrgsGetMembershipForUserRequest(StrictModel):
    """Retrieve a user's membership status within an organization. The authenticated user must be an organization member to access this information. The response includes the membership state (active, pending, etc.) to identify the user's current status."""
    path: OrgsGetMembershipForUserRequestPath

# Operation: set_organization_membership
class OrgsSetMembershipForUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    username: str = Field(default=..., description="The GitHub user account handle to add or update in the organization.")
class OrgsSetMembershipForUserRequestBody(StrictModel):
    role: Literal["admin", "member"] | None = Field(default=None, description="The role to assign the user in the organization. Use 'admin' to make the user an organization owner, or 'member' for a non-owner role.")
class OrgsSetMembershipForUserRequest(StrictModel):
    """Set or update a user's membership in an organization. Only organization owners can add members or modify roles. New members receive an invitation email and have pending status until acceptance."""
    path: OrgsSetMembershipForUserRequestPath
    body: OrgsSetMembershipForUserRequestBody | None = None

# Operation: remove_organization_membership
class OrgsRemoveMembershipForUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    username: str = Field(default=..., description="The GitHub username handle for the user whose membership will be removed.")
class OrgsRemoveMembershipForUserRequest(StrictModel):
    """Remove a user's membership from an organization. The authenticated user must be an organization owner. This action removes active members or cancels pending invitations, and the affected user receives an email notification."""
    path: OrgsRemoveMembershipForUserRequestPath

# Operation: list_organization_migrations
class MigrationsListForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class MigrationsListForOrgRequest(StrictModel):
    """Retrieve the most recent migrations for an organization, including both exports (startable via REST API) and imports (read-only). Repository details are only included for export migrations."""
    path: MigrationsListForOrgRequestPath

# Operation: get_migration_status
class MigrationsGetStatusForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    migration_id: int = Field(default=..., description="The unique identifier of the migration to check status for.")
class MigrationsGetStatusForOrgRequest(StrictModel):
    """Retrieve the current status of an organization migration. Returns the migration state (pending, exporting, exported, or failed) and associated metadata."""
    path: MigrationsGetStatusForOrgRequestPath

# Operation: download_migration_archive
class MigrationsDownloadArchiveForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    migration_id: int = Field(default=..., description="The unique identifier of the migration. Used to specify which migration archive to download.")
class MigrationsDownloadArchiveForOrgRequest(StrictModel):
    """Downloads the migration archive for an organization. Returns a URL to access the exported migration data."""
    path: MigrationsDownloadArchiveForOrgRequestPath

# Operation: delete_migration_archive
class MigrationsDeleteArchiveForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    migration_id: int = Field(default=..., description="The unique identifier of the migration whose archive should be deleted.")
class MigrationsDeleteArchiveForOrgRequest(StrictModel):
    """Deletes a previous migration archive for an organization. Migration archives are automatically deleted after seven days, but can be manually removed earlier using this operation."""
    path: MigrationsDeleteArchiveForOrgRequestPath

# Operation: unlock_migration_repository
class MigrationsUnlockRepoForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    migration_id: int = Field(default=..., description="The unique identifier of the migration.")
    repo_name: str = Field(default=..., description="The name of the repository to unlock.")
class MigrationsUnlockRepoForOrgRequest(StrictModel):
    """Unlock a repository that was locked during an organization migration. After unlocking, you can delete the repository when migration is complete and the source data is no longer needed."""
    path: MigrationsUnlockRepoForOrgRequestPath

# Operation: list_migration_repositories
class MigrationsListReposForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
    migration_id: int = Field(default=..., description="The unique identifier of the migration. Used to specify which organization migration to retrieve repositories for.")
class MigrationsListReposForOrgRequest(StrictModel):
    """List all repositories included in an organization migration. This retrieves the complete set of repositories that are part of the specified migration for the organization."""
    path: MigrationsListReposForOrgRequestPath

# Operation: list_organization_roles
class OrgsListOrgRolesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class OrgsListOrgRolesRequest(StrictModel):
    """Lists all organization roles available in the specified organization. Requires administrator access or fine-grained `read_organization_custom_org_role` permission."""
    path: OrgsListOrgRolesRequestPath

# Operation: revoke_team_organization_roles
class OrgsRevokeAllOrgRolesTeamRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier for the team from which to remove all organization roles.")
class OrgsRevokeAllOrgRolesTeamRequest(StrictModel):
    """Remove all organization roles assigned to a team. The authenticated user must be an organization administrator to perform this action."""
    path: OrgsRevokeAllOrgRolesTeamRequestPath

# Operation: assign_organization_role_to_team
class OrgsAssignTeamToOrgRoleRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier of the team to assign the role to.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role to assign to the team.")
class OrgsAssignTeamToOrgRoleRequest(StrictModel):
    """Assigns an organization role to a team within an organization. The authenticated user must be an administrator for the organization to perform this action."""
    path: OrgsAssignTeamToOrgRoleRequestPath

# Operation: remove_organization_role_from_team
class OrgsRevokeOrgRoleTeamRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    team_slug: str = Field(default=..., description="The slug of the team name.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role to remove from the team.")
class OrgsRevokeOrgRoleTeamRequest(StrictModel):
    """Remove an organization role from a team. The authenticated user must be an administrator for the organization, and the request requires the `admin:org` scope."""
    path: OrgsRevokeOrgRoleTeamRequestPath

# Operation: revoke_all_organization_roles_from_user
class OrgsRevokeAllOrgRolesUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The GitHub organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub username handle for the user whose organization roles will be revoked.")
class OrgsRevokeAllOrgRolesUserRequest(StrictModel):
    """Remove all organization roles assigned to a user. The authenticated user must be an organization administrator to perform this action."""
    path: OrgsRevokeAllOrgRolesUserRequestPath

# Operation: assign_organization_role_to_user
class OrgsAssignUserToOrgRoleRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
    username: str = Field(default=..., description="The GitHub username of the user to assign the role to.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role to assign to the user.")
class OrgsAssignUserToOrgRoleRequest(StrictModel):
    """Assigns an organization role to a user within an organization. The authenticated user must be an administrator of the organization to perform this action."""
    path: OrgsAssignUserToOrgRoleRequestPath

# Operation: revoke_organization_role_from_user
class OrgsRevokeOrgRoleUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle from which to remove the organization role.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role to remove from the user.")
class OrgsRevokeOrgRoleUserRequest(StrictModel):
    """Remove an organization role from a user. The authenticated user must be an organization administrator to perform this action."""
    path: OrgsRevokeOrgRoleUserRequestPath

# Operation: get_organization_role
class OrgsGetOrgRoleRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role to retrieve.")
class OrgsGetOrgRoleRequest(StrictModel):
    """Retrieve a specific organization role by its unique identifier. Requires administrator access or the fine-grained `read_organization_custom_org_role` permission."""
    path: OrgsGetOrgRoleRequestPath

# Operation: list_organization_role_teams
class OrgsListOrgRoleTeamsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role.")
class OrgsListOrgRoleTeamsRequest(StrictModel):
    """Lists all teams assigned to a specific organization role. Requires administrator privileges for the organization."""
    path: OrgsListOrgRoleTeamsRequestPath

# Operation: list_organization_role_users
class OrgsListOrgRoleUsersRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    role_id: int = Field(default=..., description="The unique identifier of the organization role.")
class OrgsListOrgRoleUsersRequest(StrictModel):
    """Lists organization members assigned to a specific organization role. Requires administrator privileges for the organization."""
    path: OrgsListOrgRoleUsersRequestPath

# Operation: list_outside_collaborators
class OrgsListOutsideCollaboratorsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class OrgsListOutsideCollaboratorsRequestQuery(StrictModel):
    filter_: Literal["2fa_disabled", "2fa_insecure", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter outside collaborators by two-factor authentication status. Use '2fa_disabled' to show only those without 2FA enabled, '2fa_insecure' to show only those with insecure 2FA methods, or 'all' to show all outside collaborators.")
class OrgsListOutsideCollaboratorsRequest(StrictModel):
    """List all outside collaborators for an organization, with optional filtering by two-factor authentication status. Outside collaborators are users who have access to organization repositories but are not members of the organization."""
    path: OrgsListOutsideCollaboratorsRequestPath
    query: OrgsListOutsideCollaboratorsRequestQuery | None = None

# Operation: convert_member_to_outside_collaborator
class OrgsConvertMemberToOutsideCollaboratorRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle to convert.")
class OrgsConvertMemberToOutsideCollaboratorRequestBody(StrictModel):
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="When true, the request executes asynchronously and returns a 202 status code when the job is queued.")
class OrgsConvertMemberToOutsideCollaboratorRequest(StrictModel):
    """Convert an organization member to an outside collaborator, restricting their access to only repositories their team membership allows. The user will no longer be an organization member."""
    path: OrgsConvertMemberToOutsideCollaboratorRequestPath
    body: OrgsConvertMemberToOutsideCollaboratorRequestBody | None = None

# Operation: remove_outside_collaborator
class OrgsRemoveOutsideCollaboratorRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    username: str = Field(default=..., description="The GitHub username handle for the outside collaborator to remove.")
class OrgsRemoveOutsideCollaboratorRequest(StrictModel):
    """Remove an outside collaborator from an organization, which automatically revokes their access to all organization repositories."""
    path: OrgsRemoveOutsideCollaboratorRequestPath

# Operation: list_organization_packages
class PackagesListPackagesForOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class PackagesListPackagesForOrganizationRequestQuery(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type to filter by. Gradle packages use `maven`, Docker images in the Container registry use `container`, and `docker` finds images in the legacy Docker registry.")
    visibility: Literal["public", "private", "internal"] | None = Field(default=None, description="Filter results by package visibility level. The `internal` visibility is only supported for registries with granular permissions; for other ecosystems it is treated as `private`.")
class PackagesListPackagesForOrganizationRequest(StrictModel):
    """List all packages in an organization that are readable by the authenticated user. Requires `read:packages` scope for OAuth apps and personal access tokens."""
    path: PackagesListPackagesForOrganizationRequestPath
    query: PackagesListPackagesForOrganizationRequestQuery

# Operation: get_organization_package
class PackagesGetPackageForOrganizationRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use `maven`, container images pushed to ghcr.io use `container`, and `docker` finds images in the legacy Docker registry (docker.pkg.github.com).")
    package_name: str = Field(default=..., description="The name of the package to retrieve.")
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class PackagesGetPackageForOrganizationRequest(StrictModel):
    """Retrieve a specific package from an organization's registry. Requires `read:packages` scope for authentication."""
    path: PackagesGetPackageForOrganizationRequestPath

# Operation: delete_organization_package
class PackagesDeletePackageForOrgRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use 'maven', Docker images pushed to ghcr.io use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to delete.")
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class PackagesDeletePackageForOrgRequest(StrictModel):
    """Permanently delete an entire package from an organization. Public packages with more than 5,000 downloads cannot be deleted; contact GitHub support in such cases."""
    path: PackagesDeletePackageForOrgRequestPath

# Operation: restore_organization_package
class PackagesRestorePackageForOrgRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package type to restore. Different registries support different types: npm, maven, and rubygems are language-specific registries; docker and container are image registries; nuget is for .NET packages.")
    package_name: str = Field(default=..., description="The name of the package to restore.")
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class PackagesRestorePackageForOrgRequest(StrictModel):
    """Restore a deleted package in an organization. The package must have been deleted within the last 30 days and the same package namespace and version must still be available."""
    path: PackagesRestorePackageForOrgRequestPath

# Operation: list_organization_package_versions
class PackagesGetAllPackageVersionsForPackageOwnedByOrgRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package type (e.g., npm, maven, docker, container). Docker images in GitHub's Container registry use 'container'; use 'docker' to find images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to retrieve versions for.")
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class PackagesGetAllPackageVersionsForPackageOwnedByOrgRequestQuery(StrictModel):
    state: Literal["active", "deleted"] | None = Field(default=None, description="Filter versions by state: active for current versions or deleted for removed versions.")
class PackagesGetAllPackageVersionsForPackageOwnedByOrgRequest(StrictModel):
    """Retrieve all versions of a package owned by an organization. Requires `read:packages` scope for authentication."""
    path: PackagesGetAllPackageVersionsForPackageOwnedByOrgRequestPath
    query: PackagesGetAllPackageVersionsForPackageOwnedByOrgRequestQuery | None = None

# Operation: get_organization_package_version
class PackagesGetPackageVersionForOrganizationRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package type determines which registry to query. Maven packages are used in Gradle registries, while container images can be pushed to GitHub's Container registry (ghcr.io) or Docker registry (docker.pkg.github.com).")
    package_name: str = Field(default=..., description="The name of the package to retrieve. Package names are case-sensitive identifiers within the registry.")
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    package_version_id: int = Field(default=..., description="The unique numeric identifier for the specific package version to retrieve.")
class PackagesGetPackageVersionForOrganizationRequest(StrictModel):
    """Retrieve a specific package version from an organization's package registry. Requires `read:packages` scope for authentication."""
    path: PackagesGetPackageVersionForOrganizationRequestPath

# Operation: delete_package_version
class PackagesDeletePackageVersionForOrgRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use 'maven', Docker images pushed to ghcr.io use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to delete a version from.")
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    package_version_id: int = Field(default=..., description="The unique identifier of the package version to delete.")
class PackagesDeletePackageVersionForOrgRequest(StrictModel):
    """Delete a specific package version from an organization's package registry. Note that public packages with over 5,000 downloads cannot be deleted; contact GitHub support in such cases."""
    path: PackagesDeletePackageVersionForOrgRequestPath

# Operation: restore_package_version
class PackagesRestorePackageVersionForOrgRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The type of package registry. Gradle packages use 'maven', container images use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to restore.")
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    package_version_id: int = Field(default=..., description="The unique identifier of the package version to restore.")
class PackagesRestorePackageVersionForOrgRequest(StrictModel):
    """Restore a deleted package version in an organization. The package must have been deleted within the last 30 days and the same package namespace and version must still be available."""
    path: PackagesRestorePackageVersionForOrgRequestPath

# Operation: list_pat_grant_requests
class OrgsListPatGrantRequestsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsListPatGrantRequestsRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort results by.")
    permission: str | None = Field(default=None, description="Filter results by the specific permission required by the token request.")
    token_id: list[str] | None = Field(default=None, description="Filter results by one or more token IDs. Accepts up to 50 IDs as a comma-separated array.", max_length=50)
class OrgsListPatGrantRequestsRequest(StrictModel):
    """Lists pending requests from organization members to access organization resources using fine-grained personal access tokens. Only GitHub Apps can use this endpoint."""
    path: OrgsListPatGrantRequestsRequestPath
    query: OrgsListPatGrantRequestsRequestQuery | None = None

# Operation: review_pat_grant_requests
class OrgsReviewPatGrantRequestsInBulkRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsReviewPatGrantRequestsInBulkRequestBody(StrictModel):
    pat_request_ids: list[int] | None = Field(default=None, description="Unique identifiers of the personal access token requests to review. Accepts between 1 and 100 request IDs.", min_length=1, max_length=100)
    action: Literal["approve", "deny"] = Field(default=..., description="The action to apply to all specified requests: approve to grant access or deny to reject access.")
    reason: str | None = Field(default=None, description="Optional reason for the approval or denial decision. Maximum 1024 characters.", max_length=1024)
class OrgsReviewPatGrantRequestsInBulkRequest(StrictModel):
    """Review and approve or deny multiple pending requests for fine-grained personal access token access to organization resources. Only GitHub Apps can use this endpoint."""
    path: OrgsReviewPatGrantRequestsInBulkRequestPath
    body: OrgsReviewPatGrantRequestsInBulkRequestBody

# Operation: review_pat_grant_request
class OrgsReviewPatGrantRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    pat_request_id: int = Field(default=..., description="The unique identifier of the personal access token request to review.")
class OrgsReviewPatGrantRequestBody(StrictModel):
    action: Literal["approve", "deny"] = Field(default=..., description="The action to take on the request: approve to grant access or deny to reject it.")
    reason: str | None = Field(default=None, description="Optional reason for the approval or denial decision. Maximum 1024 characters.", max_length=1024)
class OrgsReviewPatGrantRequest(StrictModel):
    """Review and approve or deny a pending request for fine-grained personal access token access to organization resources. Only GitHub Apps can use this endpoint."""
    path: OrgsReviewPatGrantRequestPath
    body: OrgsReviewPatGrantRequestBody

# Operation: list_pat_request_repositories
class OrgsListPatGrantRequestRepositoriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    pat_request_id: int = Field(default=..., description="The unique identifier of the fine-grained personal access token request.")
class OrgsListPatGrantRequestRepositoriesRequest(StrictModel):
    """Lists the repositories that a fine-grained personal access token request is requesting access to. Only GitHub Apps can use this endpoint."""
    path: OrgsListPatGrantRequestRepositoriesRequestPath

# Operation: list_organization_pat_grants
class OrgsListPatGrantsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class OrgsListPatGrantsRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort the results by.")
    permission: str | None = Field(default=None, description="Filter results by the specific permission granted to the token.")
    token_id: list[str] | None = Field(default=None, description="Filter results by one or more token IDs. Provide as a comma-separated list of numeric token identifiers.", max_length=50)
class OrgsListPatGrantsRequest(StrictModel):
    """Lists fine-grained personal access tokens owned by organization members that have been approved to access organization resources. Only GitHub Apps can use this endpoint."""
    path: OrgsListPatGrantsRequestPath
    query: OrgsListPatGrantsRequestQuery | None = None

# Operation: revoke_organization_pat_access
class OrgsUpdatePatAccessesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsUpdatePatAccessesRequestBody(StrictModel):
    action: Literal["revoke"] = Field(default=..., description="The action to apply to the fine-grained personal access tokens.")
    pat_ids: list[int] = Field(default=..., description="The IDs of the fine-grained personal access tokens to revoke. Accepts 1 to 100 token IDs per request.", min_length=1, max_length=100)
class OrgsUpdatePatAccessesRequest(StrictModel):
    """Revoke organization members' access to organization resources via fine-grained personal access tokens. This operation is restricted to GitHub Apps and supports revoking access for multiple tokens in a single request."""
    path: OrgsUpdatePatAccessesRequestPath
    body: OrgsUpdatePatAccessesRequestBody

# Operation: revoke_org_pat_access
class OrgsUpdatePatAccessRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    pat_id: int = Field(default=..., description="The unique identifier of the fine-grained personal access token to revoke.")
class OrgsUpdatePatAccessRequestBody(StrictModel):
    action: Literal["revoke"] = Field(default=..., description="The action to apply to the fine-grained personal access token.")
class OrgsUpdatePatAccessRequest(StrictModel):
    """Revoke a fine-grained personal access token's access to organization resources. Only GitHub Apps can use this endpoint."""
    path: OrgsUpdatePatAccessRequestPath
    body: OrgsUpdatePatAccessRequestBody

# Operation: list_pat_repositories
class OrgsListPatGrantRepositoriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    pat_id: int = Field(default=..., description="The unique identifier of the fine-grained personal access token.")
class OrgsListPatGrantRepositoriesRequest(StrictModel):
    """Lists all repositories that a fine-grained personal access token has access to within an organization. This endpoint is only available to GitHub Apps."""
    path: OrgsListPatGrantRepositoriesRequestPath

# Operation: list_organization_private_registries
class PrivateRegistriesListOrgPrivateRegistriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the private registries query.")
class PrivateRegistriesListOrgPrivateRegistriesRequest(StrictModel):
    """Retrieve all private registry configurations for an organization. Encrypted credential values are not included in the response. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: PrivateRegistriesListOrgPrivateRegistriesRequestPath

# Operation: create_organization_private_registry
class PrivateRegistriesCreateOrgPrivateRegistryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class PrivateRegistriesCreateOrgPrivateRegistryRequestBody(StrictModel):
    registry_type: Literal["maven_repository", "nuget_feed", "goproxy_server", "npm_registry", "rubygems_server", "cargo_registry", "composer_repository", "docker_registry", "git_source", "helm_registry", "hex_organization", "hex_repository", "pub_repository", "python_index", "terraform_registry"] = Field(default=..., description="The type of package registry being configured.")
    url: str = Field(default=..., description="The URL endpoint of the private registry.", json_schema_extra={'format': 'uri'})
    replaces_base: bool | None = Field(default=None, description="Whether this registry should replace the base public registry. When true, Dependabot uses only this registry without fallback to public registries. When false (default), Dependabot uses this registry for scoped packages and may fall back to public registries for others.")
    encrypted_value: str = Field(default=..., description="The encrypted secret value generated using LibSodium with the organization's public key. Must be base64-encoded.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
    key_id: str = Field(default=..., description="The ID of the public key used to encrypt the secret value.")
    visibility: Literal["all", "private", "selected"] = Field(default=..., description="The access scope for the private registry. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to restrict access to specific repositories.")
    selected_repository_ids: list[int] | None = Field(default=None, description="Array of repository IDs that can access this private registry. Required only when visibility is set to 'selected'. Omit this field when visibility is 'all' or 'private'.")
class PrivateRegistriesCreateOrgPrivateRegistryRequest(StrictModel):
    """Creates a private registry configuration for an organization with encrypted credentials. The encrypted secret must be generated using LibSodium with the public key retrieved from the organization's private registries endpoint."""
    path: PrivateRegistriesCreateOrgPrivateRegistryRequestPath
    body: PrivateRegistriesCreateOrgPrivateRegistryRequestBody

# Operation: get_private_registry_public_key
class PrivateRegistriesGetOrgPublicKeyRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class PrivateRegistriesGetOrgPublicKeyRequest(StrictModel):
    """Retrieves the public key for an organization's private registries, which is required to encrypt secrets before creating or updating them. Requires `admin:org` OAuth scope or personal access token (classic)."""
    path: PrivateRegistriesGetOrgPublicKeyRequestPath

# Operation: get_private_registry
class PrivateRegistriesGetOrgPrivateRegistryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the private registry secret to retrieve.")
class PrivateRegistriesGetOrgPrivateRegistryRequest(StrictModel):
    """Retrieve the configuration details of a private registry for an organization, excluding its encrypted credential value. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: PrivateRegistriesGetOrgPrivateRegistryRequestPath

# Operation: update_organization_private_registry
class PrivateRegistriesUpdateOrgPrivateRegistryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    secret_name: str = Field(default=..., description="The name of the private registry secret to update.")
class PrivateRegistriesUpdateOrgPrivateRegistryRequestBody(StrictModel):
    registry_type: Literal["maven_repository", "nuget_feed", "goproxy_server", "npm_registry", "rubygems_server", "cargo_registry", "composer_repository", "docker_registry", "git_source", "helm_registry", "hex_organization", "hex_repository", "pub_repository", "python_index", "terraform_registry"] | None = Field(default=None, description="The type of package registry being configured.")
    url: str | None = Field(default=None, description="The URL endpoint of the private registry.", json_schema_extra={'format': 'uri'})
    replaces_base: bool | None = Field(default=None, description="When true, this registry replaces the default public registry and Dependabot will not fall back to public sources. When false (default), Dependabot uses this registry for scoped packages but may fall back to public registries for others.")
    key_id: str | None = Field(default=None, description="The ID of the encryption key used to encrypt the secret value.")
    visibility: Literal["all", "private", "selected"] | None = Field(default=None, description="Controls which organization repositories can access this private registry. Use 'all' for all repositories, 'private' for private repositories only, or 'selected' to specify individual repositories.")
    selected_repository_ids: list[int] | None = Field(default=None, description="Array of repository IDs that can access this private registry. Only provide this when visibility is set to 'selected'; omit for 'all' or 'private' visibility.")
    encrypted_value: str | None = Field(default=None, description="The value for your secret, encrypted with [LibSodium](https://libsodium.gitbook.io/doc/bindings_for_other_languages) using the public key retrieved from the [Get private registries public key for an organization](https://docs.github.com/rest/private-registries/organization-configurations#get-private-registries-public-key-for-an-organization) endpoint.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
class PrivateRegistriesUpdateOrgPrivateRegistryRequest(StrictModel):
    """Updates a private registry configuration for an organization, allowing you to manage Dependabot's access to private package repositories. Requires encrypting sensitive credentials using LibSodium before submission."""
    path: PrivateRegistriesUpdateOrgPrivateRegistryRequestPath
    body: PrivateRegistriesUpdateOrgPrivateRegistryRequestBody | None = None

# Operation: delete_org_private_registry
class PrivateRegistriesDeleteOrgPrivateRegistryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the private registry secret to delete.")
class PrivateRegistriesDeleteOrgPrivateRegistryRequest(StrictModel):
    """Delete a private registry configuration for an organization. Requires `admin:org` scope for OAuth apps and personal access tokens (classic)."""
    path: PrivateRegistriesDeleteOrgPrivateRegistryRequestPath

# Operation: list_organization_projects
class ProjectsListForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ProjectsListForOrgRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="Filter results to projects of a specified type.")
class ProjectsListForOrgRequest(StrictModel):
    """Retrieve all projects owned by an organization that are accessible to the authenticated user. Results can be filtered by project type using the optional query parameter."""
    path: ProjectsListForOrgRequestPath
    query: ProjectsListForOrgRequestQuery | None = None

# Operation: get_organization_project
class ProjectsGetForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The unique numeric identifier for the project within the organization.")
    org: str = Field(default=..., description="The name of the organization that owns the project. Organization names are case-insensitive.")
class ProjectsGetForOrgRequest(StrictModel):
    """Retrieve a specific project owned by an organization using its project number. This operation fetches detailed information about a single organization-level project."""
    path: ProjectsGetForOrgRequestPath

# Operation: create_draft_item
class ProjectsCreateDraftItemForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    project_number: int = Field(default=..., description="The project number that uniquely identifies the project within the organization.")
class ProjectsCreateDraftItemForOrgRequestBody(StrictModel):
    """Details of the draft item to create in the project."""
    title: str = Field(default=..., description="The title of the draft issue item. This is the primary heading for the draft.")
    body: str | None = Field(default=None, description="The body content of the draft issue item. Supports markdown formatting for rich text content.")
class ProjectsCreateDraftItemForOrgRequest(StrictModel):
    """Create a draft issue item in an organization-owned project. Draft items can be converted to full issues later."""
    path: ProjectsCreateDraftItemForOrgRequestPath
    body: ProjectsCreateDraftItemForOrgRequestBody

# Operation: list_project_fields
class ProjectsListFieldsForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The numeric identifier of the project. This uniquely identifies the project within the organization.")
    org: str = Field(default=..., description="The name of the organization that owns the project. Organization names are case-insensitive.")
class ProjectsListFieldsForOrgRequest(StrictModel):
    """Retrieve all fields configured for a specific organization-owned project. Fields define the custom properties and metadata available for project items."""
    path: ProjectsListFieldsForOrgRequestPath

# Operation: add_project_field
class ProjectsAddFieldForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project number that uniquely identifies the project within the organization.")
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class ProjectsAddFieldForOrgRequestBody(StrictModel):
    body: ProjectsAddFieldForOrgBodyV0 | ProjectsAddFieldForOrgBodyV1 | ProjectsAddFieldForOrgBodyV2 | ProjectsAddFieldForOrgBodyV3 = Field(default=..., description="Field configuration object specifying the field name, data type, and type-specific options. Supported data types include text, number, date, single_select, and iteration.", examples=[{'name': 'Team notes', 'data_type': 'text'}, {'name': 'Story points', 'data_type': 'number'}, {'name': 'Due date', 'data_type': 'date'}, {'name': 'Priority', 'data_type': 'single_select', 'single_select_options': [{'name': {'raw': 'Low', 'html': 'Low'}, 'color': 'GREEN', 'description': {'raw': 'Low priority items', 'html': 'Low priority items'}}, {'name': {'raw': 'Medium', 'html': 'Medium'}, 'color': 'YELLOW', 'description': {'raw': 'Medium priority items', 'html': 'Medium priority items'}}, {'name': {'raw': 'High', 'html': 'High'}, 'color': 'RED', 'description': {'raw': 'High priority items', 'html': 'High priority items'}}]}, {'name': 'Sprint', 'data_type': 'iteration', 'iteration_configuration': {'start_day': 1, 'duration': 14, 'iterations': [{'title': {'raw': 'Sprint 1', 'html': 'Sprint 1'}, 'start_date': '2022-07-01', 'duration': 14}, {'title': {'raw': 'Sprint 2', 'html': 'Sprint 2'}, 'start_date': '2022-07-15', 'duration': 14}]}}])
class ProjectsAddFieldForOrgRequest(StrictModel):
    """Add a custom field to an organization-owned project. Fields can be of various types including text, number, date, single select, and iteration to support project tracking and management."""
    path: ProjectsAddFieldForOrgRequestPath
    body: ProjectsAddFieldForOrgRequestBody

# Operation: get_project_field
class ProjectsGetFieldForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier within the organization.")
    field_id: int = Field(default=..., description="The unique identifier of the field to retrieve.")
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
class ProjectsGetFieldForOrgRequest(StrictModel):
    """Retrieve a specific field from an organization-owned project. Fields define custom properties and data types for project items."""
    path: ProjectsGetFieldForOrgRequestPath

# Operation: list_project_items
class ProjectsListItemsForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier.")
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ProjectsListItemsForOrgRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="Search query to filter items by their properties and values.")
    fields: str | list[str] | None = Field(default=None, description="Comma-separated or repeated field IDs to include in results. If not specified, only the title field is returned.")
class ProjectsListItemsForOrgRequest(StrictModel):
    """List all items in an organization-owned project. Retrieve project items with optional filtering by search query and field selection."""
    path: ProjectsListItemsForOrgRequestPath
    query: ProjectsListItemsForOrgRequestQuery | None = None

# Operation: add_item_to_project
class ProjectsAddItemForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    project_number: int = Field(default=..., description="The project's unique number identifier within the organization.")
class ProjectsAddItemForOrgRequestBody(StrictModel):
    """Details of the item to add to the project. You can specify either the unique ID or the repository owner, name, and issue/PR number."""
    type_: Literal["Issue", "PullRequest"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of item being added to the project.")
class ProjectsAddItemForOrgRequest(StrictModel):
    """Add an issue or pull request to an organization's project. This operation allows you to associate existing GitHub items with a specific project for tracking and organization purposes."""
    path: ProjectsAddItemForOrgRequestPath
    body: ProjectsAddItemForOrgRequestBody

# Operation: get_project_item
class ProjectsGetOrgItemRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier.")
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    item_id: int = Field(default=..., description="The unique identifier of the project item to retrieve.")
class ProjectsGetOrgItemRequestQuery(StrictModel):
    fields: str | list[str] | None = Field(default=None, description="Comma-separated or repeated field IDs to include in the response. If not specified, only the title field is returned.")
class ProjectsGetOrgItemRequest(StrictModel):
    """Retrieve a specific item from an organization-owned project. Returns the item's details, including selected fields or the title field by default."""
    path: ProjectsGetOrgItemRequestPath
    query: ProjectsGetOrgItemRequestQuery | None = None

# Operation: update_project_item
class ProjectsUpdateItemForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier within the organization.")
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    item_id: int = Field(default=..., description="The unique identifier of the project item to update.")
class ProjectsUpdateItemForOrgRequestBody(StrictModel):
    """Field updates to apply to the project item. Only text, number, date, single select, and iteration fields are supported."""
    fields: list[ProjectsUpdateItemForOrgBodyFieldsItem] = Field(default=..., description="An ordered list of field updates to apply to the item. Each entry specifies a field and its new value.")
class ProjectsUpdateItemForOrgRequest(StrictModel):
    """Update a specific item in an organization-owned project by applying field changes. Modify item properties such as status, assignees, or custom fields."""
    path: ProjectsUpdateItemForOrgRequestPath
    body: ProjectsUpdateItemForOrgRequestBody

# Operation: delete_project_item
class ProjectsDeleteItemForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier within the organization.")
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    item_id: int = Field(default=..., description="The unique identifier of the project item to delete.")
class ProjectsDeleteItemForOrgRequest(StrictModel):
    """Delete a specific item from an organization-owned project. This operation permanently removes the item from the project."""
    path: ProjectsDeleteItemForOrgRequestPath

# Operation: create_project_view
class ProjectsCreateViewForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    project_number: int = Field(default=..., description="The project's number identifier.")
class ProjectsCreateViewForOrgRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the view.")
    layout: Literal["table", "board", "roadmap"] = Field(default=..., description="The layout type that determines how project items are displayed.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter query to control which items appear in the view. Use standard project filtering syntax to narrow results by status, type, assignee, and other criteria.")
    visible_fields: list[int] | None = Field(default=None, description="Optional array of field IDs to display in the view. Not applicable for roadmap layouts. If omitted, default visible fields will be used. Field order in the array determines display order.")
class ProjectsCreateViewForOrgRequest(StrictModel):
    """Create a new view in an organization-owned project to customize how items are displayed and filtered. Views support different layouts (table, board, roadmap) and can include optional filtering and field visibility settings."""
    path: ProjectsCreateViewForOrgRequestPath
    body: ProjectsCreateViewForOrgRequestBody

# Operation: list_project_view_items
class ProjectsListViewItemsForOrgRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's number that identifies which project to query.")
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    view_number: int = Field(default=..., description="The number that identifies the project view within the project.")
class ProjectsListViewItemsForOrgRequestQuery(StrictModel):
    fields: str | list[str] | None = Field(default=None, description="Limit results to specific fields by their IDs. If not specified, only the title field will be returned. Accepts multiple field IDs as a comma-separated list or repeated query parameters.")
class ProjectsListViewItemsForOrgRequest(StrictModel):
    """List items in an organization project view with the view's saved filters applied. Returns project items matching the specified view's configuration."""
    path: ProjectsListViewItemsForOrgRequestPath
    query: ProjectsListViewItemsForOrgRequestQuery | None = None

# Operation: list_organization_custom_property_definitions
class OrgsCustomPropertiesForReposGetOrganizationDefinitionsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the custom property definitions.")
class OrgsCustomPropertiesForReposGetOrganizationDefinitionsRequest(StrictModel):
    """Retrieve all custom property definitions configured for an organization. Organization members can access these property schemas to understand available custom properties."""
    path: OrgsCustomPropertiesForReposGetOrganizationDefinitionsRequestPath

# Operation: get_organization_custom_property
class OrgsCustomPropertiesForReposGetOrganizationDefinitionRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the custom property lookup.")
    custom_property_name: str = Field(default=..., description="The name of the custom property to retrieve. Must match an existing custom property defined for the organization.")
class OrgsCustomPropertiesForReposGetOrganizationDefinitionRequest(StrictModel):
    """Retrieve a custom property definition for an organization. Organization members can access these property definitions to understand custom metadata configured for the organization."""
    path: OrgsCustomPropertiesForReposGetOrganizationDefinitionRequestPath

# Operation: list_organization_repository_custom_properties
class OrgsCustomPropertiesForReposGetOrganizationValuesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The lookup is case-insensitive.")
class OrgsCustomPropertiesForReposGetOrganizationValuesRequestQuery(StrictModel):
    repository_query: str | None = Field(default=None, description="Search query to filter repositories by keywords and qualifiers. Supports the same search syntax as the GitHub web interface for repository discovery and filtering.")
class OrgsCustomPropertiesForReposGetOrganizationValuesRequest(StrictModel):
    """Retrieve all repositories in an organization along with their custom property values. Organization members can access this information to view how custom properties are applied across repositories."""
    path: OrgsCustomPropertiesForReposGetOrganizationValuesRequestPath
    query: OrgsCustomPropertiesForReposGetOrganizationValuesRequestQuery | None = None

# Operation: batch_update_repository_custom_properties
class OrgsCustomPropertiesForReposCreateOrUpdateOrganizationValuesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the repositories.")
class OrgsCustomPropertiesForReposCreateOrUpdateOrganizationValuesRequestBody(StrictModel):
    repository_names: list[str] = Field(default=..., description="The names of repositories to update. Each repository must belong to the organization. Order is not significant.", min_length=1, max_length=30)
    properties: list[CustomPropertyValue] = Field(default=..., description="Custom properties and their values to apply to the repositories. Each property entry specifies a property name and its value. Use null to remove or unset a property value from the repositories.")
class OrgsCustomPropertiesForReposCreateOrUpdateOrganizationValuesRequest(StrictModel):
    """Update custom property values for multiple repositories in an organization. Apply the same custom property values across up to 30 repositories in a single batch operation, with support for unsetting properties using null values."""
    path: OrgsCustomPropertiesForReposCreateOrUpdateOrganizationValuesRequestPath
    body: OrgsCustomPropertiesForReposCreateOrUpdateOrganizationValuesRequestBody

# Operation: list_organization_public_members
class OrgsListPublicMembersRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The lookup is case-insensitive.")
class OrgsListPublicMembersRequest(StrictModel):
    """List all members of an organization whose membership is publicly visible. Organization members can choose whether their membership is public or private."""
    path: OrgsListPublicMembersRequestPath

# Operation: check_public_organization_membership
class OrgsCheckPublicMembershipForUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    username: str = Field(default=..., description="The GitHub username handle to check for public membership in the organization.")
class OrgsCheckPublicMembershipForUserRequest(StrictModel):
    """Verify whether a user is a public member of the specified organization. Public membership is visible to anyone, unlike concealed membership."""
    path: OrgsCheckPublicMembershipForUserRequestPath

# Operation: publicize_organization_membership
class OrgsSetPublicMembershipForAuthenticatedUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
    username: str = Field(default=..., description="The GitHub username of the authenticated user whose membership will be publicized.")
class OrgsSetPublicMembershipForAuthenticatedUserRequest(StrictModel):
    """Publicize your own membership in an organization. This makes your membership visible to others, and can only be performed by the authenticated user for their own membership."""
    path: OrgsSetPublicMembershipForAuthenticatedUserRequestPath

# Operation: remove_public_organization_membership
class OrgsRemovePublicMembershipForAuthenticatedUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
    username: str = Field(default=..., description="The GitHub username of the account whose public membership should be removed.")
class OrgsRemovePublicMembershipForAuthenticatedUserRequest(StrictModel):
    """Remove your public membership from an organization. This action makes your membership private unless the organization enforces public visibility by default."""
    path: OrgsRemovePublicMembershipForAuthenticatedUserRequestPath

# Operation: list_organization_repositories
class ReposListForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class ReposListForOrgRequestQuery(StrictModel):
    type_: Literal["all", "public", "private", "forks", "sources", "member"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filters repositories by type. Use 'all' to include all repository types, 'public' for publicly accessible repositories, 'private' for private repositories, 'forks' for forked repositories, 'sources' for original repositories, or 'member' for repositories the authenticated user is a member of.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort order for results. Use 'asc' for ascending order or 'desc' for descending order. Defaults to 'asc' when sorting by full name, otherwise 'desc'.")
class ReposListForOrgRequest(StrictModel):
    """Retrieves repositories for the specified organization. Supports filtering by repository type and sorting results in ascending or descending order."""
    path: ReposListForOrgRequestPath
    query: ReposListForOrgRequestQuery | None = None

# Operation: create_organization_repository
class ReposCreateInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name where the repository will be created. Organization names are case-insensitive.")
class ReposCreateInOrgRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the new repository.")
    description: str | None = Field(default=None, description="A short description of the repository's purpose or content.")
    homepage: str | None = Field(default=None, description="A URL with more information about the repository, such as project documentation or homepage.")
    visibility: Literal["public", "private"] | None = Field(default=None, description="The visibility level of the repository, determining who can access it.")
    has_issues: bool | None = Field(default=None, description="Enable or disable GitHub Issues for this repository.")
    has_projects: bool | None = Field(default=None, description="Enable or disable GitHub Projects for this repository. Note: If the organization has disabled repository projects, this defaults to false and passing true will return an error.")
    has_wiki: bool | None = Field(default=None, description="Enable or disable the wiki feature for this repository.")
    is_template: bool | None = Field(default=None, description="Make this repository available as a template that others can use to generate new repositories.")
    team_id: int | None = Field(default=None, description="The ID of the team that will be granted access to this repository. Only valid when creating a repository in an organization.")
    auto_init: bool | None = Field(default=None, description="Create an initial commit with an empty README file to initialize the repository.")
    gitignore_template: str | None = Field(default=None, description="Apply a .gitignore template for the specified language or platform. Use the template name without the file extension (e.g., 'Haskell', 'Python').")
    license_template: str | None = Field(default=None, description="Apply an open source license template to the repository. Use the license keyword identifier (e.g., 'mit', 'mpl-2.0', 'apache-2.0').")
    allow_squash_merge: bool | None = Field(default=None, description="Allow pull requests to be merged using the squash-merge strategy.")
    allow_merge_commit: bool | None = Field(default=None, description="Allow pull requests to be merged using a merge commit strategy.")
    allow_rebase_merge: bool | None = Field(default=None, description="Allow pull requests to be merged using the rebase-merge strategy.")
    allow_auto_merge: bool | None = Field(default=None, description="Allow pull requests to be automatically merged when all required conditions are met.")
    delete_branch_on_merge: bool | None = Field(default=None, description="Automatically delete the head branch when a pull request is merged. Only organization owners can set this to true.")
    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"] | None = Field(default=None, description="The default title format for squash merge commits. Required when using squash_merge_commit_message.")
    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"] | None = Field(default=None, description="The default message content for squash merge commits, determining whether to use the pull request body, branch commit messages, or a blank message.")
    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"] | None = Field(default=None, description="The default title format for merge commits. Required when using merge_commit_message.")
    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"] | None = Field(default=None, description="The default message content for merge commits, determining whether to use the pull request title, body, or a blank message.")
    custom_properties: dict[str, Any] | None = Field(default=None, description="Custom properties for the repository as key-value pairs, where keys are custom property names and values are their corresponding values.")
class ReposCreateInOrgRequest(StrictModel):
    """Creates a new repository in the specified organization. The authenticated user must be a member of the organization with appropriate OAuth scopes (`public_repo` or `repo` for public repositories, `repo` for private repositories)."""
    path: ReposCreateInOrgRequestPath
    body: ReposCreateInOrgRequestBody

# Operation: list_organization_rulesets
class ReposGetOrgRulesetsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class ReposGetOrgRulesetsRequestQuery(StrictModel):
    targets: str | None = Field(default=None, description="Filter rulesets by target types using a comma-separated list. Only rulesets applying to the specified targets will be returned.")
class ReposGetOrgRulesetsRequest(StrictModel):
    """Retrieve all repository rulesets configured for an organization. Optionally filter rulesets by their target types (branch, tag, push, etc.)."""
    path: ReposGetOrgRulesetsRequestPath
    query: ReposGetOrgRulesetsRequestQuery | None = None

# Operation: list_organization_rule_suites
class ReposGetOrgRuleSuitesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class ReposGetOrgRuleSuitesRequestQuery(StrictModel):
    repository_name: str | None = Field(default=None, description="Filter results to a specific repository by name.")
    time_period: Literal["hour", "day", "week", "month"] | None = Field(default=None, description="Filter results by time period. Use 'hour' for the past 24 hours, 'day' for the past 24 hours, 'week' for the past 7 days, or 'month' for the past 30 days.")
    actor_name: str | None = Field(default=None, description="Filter results to rule evaluations triggered by a specific GitHub user account handle.")
    rule_suite_result: Literal["pass", "fail", "bypass", "all"] | None = Field(default=None, description="Filter results by rule suite outcome. Use 'pass' for successful evaluations, 'fail' for failed evaluations, 'bypass' for bypassed evaluations, or 'all' to include all outcomes.")
class ReposGetOrgRuleSuitesRequest(StrictModel):
    """Lists suites of rule evaluations at the organization level to view insights and compliance results for repository rulesets. Filter by repository, time period, actor, or result status."""
    path: ReposGetOrgRuleSuitesRequestPath
    query: ReposGetOrgRuleSuitesRequestQuery | None = None

# Operation: get_organization_rule_suite
class ReposGetOrgRuleSuiteRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    rule_suite_id: int = Field(default=..., description="The unique identifier of the rule suite result. Retrieve this ID from the organization or repository rule suites list endpoints.")
class ReposGetOrgRuleSuiteRequest(StrictModel):
    """Retrieve detailed information about a specific rule suite evaluation within an organization. Use this to view insights and results from ruleset evaluations applied across your organization's repositories."""
    path: ReposGetOrgRuleSuiteRequestPath

# Operation: get_organization_ruleset
class ReposGetOrgRulesetRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset to retrieve.")
class ReposGetOrgRulesetRequest(StrictModel):
    """Retrieve a specific repository ruleset for an organization. Note that the bypass_actors property is only returned if the requester has write access to the ruleset."""
    path: ReposGetOrgRulesetRequestPath

# Operation: delete_organization_ruleset
class ReposDeleteOrgRulesetRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset to delete.")
class ReposDeleteOrgRulesetRequest(StrictModel):
    """Delete a repository ruleset for an organization. This removes the ruleset and all its associated rules from the organization."""
    path: ReposDeleteOrgRulesetRequestPath

# Operation: list_ruleset_history
class OrgsGetOrgRulesetHistoryRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset.")
class OrgsGetOrgRulesetHistoryRequest(StrictModel):
    """Retrieve the complete history of changes for an organization ruleset, including all modifications and their timestamps."""
    path: OrgsGetOrgRulesetHistoryRequestPath

# Operation: get_ruleset_version
class OrgsGetOrgRulesetVersionRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Organization names are case-insensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset.")
    version_id: int = Field(default=..., description="The unique identifier of the ruleset version to retrieve.")
class OrgsGetOrgRulesetVersionRequest(StrictModel):
    """Retrieve a specific version of an organization ruleset. Use this to view the configuration and rules that were active at a particular point in the ruleset's history."""
    path: OrgsGetOrgRulesetVersionRequestPath

# Operation: list_secret_scanning_alerts
class SecretScanningListAlertsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class SecretScanningListAlertsForOrgRequestQuery(StrictModel):
    state: Literal["open", "resolved"] | None = Field(default=None, description="Filter alerts by their current state.")
    secret_type: str | None = Field(default=None, description="Filter by one or more secret types using comma-separated values. Supports both default secret patterns and generic token names.")
    resolution: str | None = Field(default=None, description="Filter by one or more resolution statuses using comma-separated values.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for the results.")
    validity: str | None = Field(default=None, description="Filter by validity status using comma-separated values. Indicates whether a secret is currently active, inactive, or of unknown status.")
    is_publicly_leaked: bool | None = Field(default=None, description="When true, only returns alerts that have been publicly leaked.")
    is_multi_repo: bool | None = Field(default=None, description="When true, only returns alerts that appear across multiple repositories.")
    hide_secret: bool | None = Field(default=None, description="When true, redacts literal secret values from the response results.")
class SecretScanningListAlertsForOrgRequest(StrictModel):
    """Lists secret scanning alerts for an organization across eligible repositories, ordered from newest to oldest. The authenticated user must be an administrator or security manager for the organization."""
    path: SecretScanningListAlertsForOrgRequestPath
    query: SecretScanningListAlertsForOrgRequestQuery | None = None

# Operation: list_secret_scanning_patterns
class SecretScanningListOrgPatternConfigsRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier used to scope the pattern configurations to a specific organization.")
class SecretScanningListOrgPatternConfigsRequest(StrictModel):
    """Lists all secret scanning pattern configurations for an organization. These patterns define custom rules used to detect secrets during scanning."""
    path: SecretScanningListOrgPatternConfigsRequestPath

# Operation: list_organization_security_advisories
class SecurityAdvisoriesListOrgRepositoryAdvisoriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class SecurityAdvisoriesListOrgRepositoryAdvisoriesRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for the results.")
    state: Literal["triage", "draft", "published", "closed"] | None = Field(default=None, description="Filter advisories by their current state. Only advisories matching the specified state will be returned.")
class SecurityAdvisoriesListOrgRepositoryAdvisoriesRequest(StrictModel):
    """Retrieve all repository security advisories for an organization. The authenticated user must be an owner or security manager to access this endpoint."""
    path: SecurityAdvisoriesListOrgRepositoryAdvisoriesRequestPath
    query: SecurityAdvisoriesListOrgRepositoryAdvisoriesRequestQuery | None = None

# Operation: list_immutable_release_repositories
class OrgsGetImmutableReleasesSettingsRepositoriesRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
class OrgsGetImmutableReleasesSettingsRepositoriesRequest(StrictModel):
    """List all repositories in an organization that have been selected for immutable releases enforcement. Requires admin:org scope."""
    path: OrgsGetImmutableReleasesSettingsRepositoriesRequestPath

# Operation: enable_repository_immutable_releases
class OrgsEnableSelectedRepositoryImmutableReleasesOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to enable for immutable releases.")
class OrgsEnableSelectedRepositoryImmutableReleasesOrganizationRequest(StrictModel):
    """Adds a repository to the organization's list of selected repositories enforced for immutable releases. This endpoint requires the organization's immutable releases policy to be configured for selected repositories."""
    path: OrgsEnableSelectedRepositoryImmutableReleasesOrganizationRequestPath

# Operation: remove_repository_from_immutable_releases
class OrgsDisableSelectedRepositoryImmutableReleasesOrganizationRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from immutable releases enforcement.")
class OrgsDisableSelectedRepositoryImmutableReleasesOrganizationRequest(StrictModel):
    """Remove a repository from the organization's immutable releases enforcement list. This endpoint is only available when the organization's immutable releases policy is configured to enforce selected repositories."""
    path: OrgsDisableSelectedRepositoryImmutableReleasesOrganizationRequestPath

# Operation: list_network_configurations
class HostedComputeListNetworkConfigurationsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization.")
class HostedComputeListNetworkConfigurationsForOrgRequest(StrictModel):
    """Retrieve all hosted compute network configurations for an organization. Requires `read:network_configurations` scope."""
    path: HostedComputeListNetworkConfigurationsForOrgRequestPath

# Operation: get_network_configuration
class HostedComputeGetNetworkConfigurationForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    network_configuration_id: str = Field(default=..., description="The unique identifier of the hosted compute network configuration to retrieve.")
class HostedComputeGetNetworkConfigurationForOrgRequest(StrictModel):
    """Retrieves a specific hosted compute network configuration for an organization. Requires `read:network_configurations` OAuth scope or personal access token (classic)."""
    path: HostedComputeGetNetworkConfigurationForOrgRequestPath

# Operation: update_network_configuration
class HostedComputeUpdateNetworkConfigurationForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    network_configuration_id: str = Field(default=..., description="The unique identifier of the hosted compute network configuration to update.")
class HostedComputeUpdateNetworkConfigurationForOrgRequestBody(StrictModel):
    compute_service: Literal["none", "actions"] | None = Field(default=None, description="The hosted compute service to use for this network configuration.")
    network_settings_ids: list[str] | None = Field(default=None, description="A list of network settings resource identifiers to associate with this configuration. Exactly one identifier must be provided if specified.", min_length=0, max_length=1)
class HostedComputeUpdateNetworkConfigurationForOrgRequest(StrictModel):
    """Updates a hosted compute network configuration for an organization. Requires the `write:network_configurations` OAuth scope."""
    path: HostedComputeUpdateNetworkConfigurationForOrgRequestPath
    body: HostedComputeUpdateNetworkConfigurationForOrgRequestBody | None = None

# Operation: delete_network_configuration
class HostedComputeDeleteNetworkConfigurationFromOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the network configuration.")
    network_configuration_id: str = Field(default=..., description="The unique identifier of the hosted compute network configuration to delete.")
class HostedComputeDeleteNetworkConfigurationFromOrgRequest(StrictModel):
    """Deletes a hosted compute network configuration from an organization. Requires the `write:network_configurations` OAuth scope."""
    path: HostedComputeDeleteNetworkConfigurationFromOrgRequestPath

# Operation: get_network_settings
class HostedComputeGetNetworkSettingsForOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the network settings.")
    network_settings_id: str = Field(default=..., description="The unique identifier of the hosted compute network settings resource to retrieve.")
class HostedComputeGetNetworkSettingsForOrgRequest(StrictModel):
    """Retrieve a hosted compute network settings resource for an organization. Requires `read:network_configurations` OAuth scope."""
    path: HostedComputeGetNetworkSettingsForOrgRequestPath

# Operation: get_team_copilot_metrics
class CopilotCopilotMetricsForTeamRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive). Used to identify which organization's Copilot metrics to retrieve.")
    team_slug: str = Field(default=..., description="The team slug (URL-friendly identifier). Used to specify which team within the organization to retrieve metrics for.")
class CopilotCopilotMetricsForTeamRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Start date for the metrics query in ISO 8601 format. Limits results to metrics from this date onward. Maximum lookback is 100 days ago.")
    until: str | None = Field(default=None, description="End date for the metrics query in ISO 8601 format. Limits results to metrics up to this date. Must not precede the since date if both are provided.")
class CopilotCopilotMetricsForTeamRequest(StrictModel):
    """Retrieve aggregated GitHub Copilot usage metrics for a team over a specified date range. Returns metrics for up to 100 days of historical data, with results only available for days when the team had five or more active Copilot license holders."""
    path: CopilotCopilotMetricsForTeamRequestPath
    query: CopilotCopilotMetricsForTeamRequestQuery | None = None

# Operation: list_teams
class TeamsListRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
class TeamsListRequestQuery(StrictModel):
    team_type: Literal["all", "enterprise", "organization"] | None = Field(default=None, description="Filter team results by their type. Use 'all' to include all teams, 'enterprise' for enterprise-managed teams, or 'organization' for organization-managed teams.")
class TeamsListRequest(StrictModel):
    """Retrieve all teams in an organization that are visible to the authenticated user. Optionally filter results by team type (all, enterprise, or organization)."""
    path: TeamsListRequestPath
    query: TeamsListRequestQuery | None = None

# Operation: create_team
class TeamsCreateRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
class TeamsCreateRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the team.")
    description: str | None = Field(default=None, description="A brief description of the team's purpose or focus.")
    maintainers: list[str] | None = Field(default=None, description="GitHub usernames of organization members to designate as team maintainers. Order is not significant.")
    repo_names: list[str] | None = Field(default=None, description="Full repository names (format: organization-name/repository-name) to add the team to. Order is not significant.")
    privacy: Literal["secret", "closed"] | None = Field(default=None, description="The privacy level for the team. For non-nested teams: 'secret' restricts visibility to organization owners and team members, 'closed' is visible to all organization members. For parent or child teams: only 'closed' is available.")
    notification_setting: Literal["notifications_enabled", "notifications_disabled"] | None = Field(default=None, description="Whether team members receive notifications when the team is mentioned. 'notifications_enabled' sends notifications, 'notifications_disabled' suppresses them.")
    permission: Literal["pull", "push"] | None = Field(default=None, description="The default permission level for new repositories added to the team when no specific permission is provided.")
    parent_team_id: int | None = Field(default=None, description="The team ID to set as the parent team, creating a nested team hierarchy.")
class TeamsCreateRequest(StrictModel):
    """Create a new team within an organization. The authenticated user must be a member or owner of the organization, and will automatically become a team maintainer."""
    path: TeamsCreateRequestPath
    body: TeamsCreateRequestBody

# Operation: get_team
class TeamsGetByNameRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. This parameter is case-insensitive.")
    team_slug: str = Field(default=..., description="The slug of the team name. This is a URL-friendly identifier created by converting the team name to lowercase and replacing spaces with hyphens.")
class TeamsGetByNameRequest(StrictModel):
    """Retrieve a team by its slug within an organization. The team slug is a URL-friendly identifier derived from the team name by converting to lowercase and replacing spaces with hyphens."""
    path: TeamsGetByNameRequestPath

# Operation: update_team
class TeamsUpdateInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier for the team name.")
class TeamsUpdateInOrgRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The description of the team.")
    privacy: Literal["secret", "closed"] | None = Field(default=None, description="The privacy level for the team. For non-nested teams, choose between secret (visible only to owners and members) or closed (visible to all organization members). For nested teams, only closed is allowed for parent teams.")
    notification_setting: Literal["notifications_enabled", "notifications_disabled"] | None = Field(default=None, description="Whether team members receive notifications when the team is @mentioned. Choose notifications_enabled to send notifications or notifications_disabled to disable them.")
    permission: Literal["pull", "push", "admin"] | None = Field(default=None, description="The default permission level for new repositories added to the team when no permission is explicitly specified.")
    parent_team_id: int | None = Field(default=None, description="The ID of a team to set as the parent team, establishing a nested team hierarchy.")
class TeamsUpdateInOrgRequest(StrictModel):
    """Update an organization team's settings including name, description, privacy level, and notification preferences. The authenticated user must be an organization owner or team maintainer."""
    path: TeamsUpdateInOrgRequestPath
    body: TeamsUpdateInOrgRequestBody | None = None

# Operation: delete_team
class TeamsDeleteInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the organization that owns the team.")
    team_slug: str = Field(default=..., description="The slug of the team name. A URL-friendly identifier for the team within the organization.")
class TeamsDeleteInOrgRequest(StrictModel):
    """Delete a team from an organization. The authenticated user must be an organization owner or team maintainer. Deleting a parent team will also delete all of its child teams."""
    path: TeamsDeleteInOrgRequestPath

# Operation: list_team_invitations
class TeamsListPendingInvitationsInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier for the team name.")
class TeamsListPendingInvitationsInOrgRequest(StrictModel):
    """List all pending invitations for a team within an organization. Returns invitation details including the invitee's login (null if not a GitHub member) and their assigned role."""
    path: TeamsListPendingInvitationsInOrgRequestPath

# Operation: list_team_members
class TeamsListMembersInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier for the team name.")
class TeamsListMembersInOrgRequestQuery(StrictModel):
    role: Literal["member", "maintainer", "all"] | None = Field(default=None, description="Filter members by their role within the team.")
class TeamsListMembersInOrgRequest(StrictModel):
    """List all members of a team in an organization, including members from child teams. The team must be visible to the authenticated user."""
    path: TeamsListMembersInOrgRequestPath
    query: TeamsListMembersInOrgRequestQuery | None = None

# Operation: get_team_membership
class TeamsGetMembershipForUserInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the GitHub organization.")
    team_slug: str = Field(default=..., description="The URL-friendly slug identifier for the team within the organization.")
    username: str = Field(default=..., description="The GitHub username handle for the user whose team membership is being retrieved.")
class TeamsGetMembershipForUserInOrgRequest(StrictModel):
    """Retrieve a user's membership status and role within a specific team. The response includes the membership state and the user's role, with organization owners shown as maintainers."""
    path: TeamsGetMembershipForUserInOrgRequestPath

# Operation: add_or_update_team_membership
class TeamsAddOrUpdateMembershipForUserInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name (case-insensitive).")
    team_slug: str = Field(default=..., description="The slug identifier for the team.")
    username: str = Field(default=..., description="The GitHub username handle for the user being added or updated.")
class TeamsAddOrUpdateMembershipForUserInOrgRequestBody(StrictModel):
    role: Literal["member", "maintainer"] | None = Field(default=None, description="The role to assign the user within the team.")
class TeamsAddOrUpdateMembershipForUserInOrgRequest(StrictModel):
    """Add an organization member to a team or update their existing team role. An authenticated organization owner or team maintainer can manage team membership, with automatic email invitations sent to non-members."""
    path: TeamsAddOrUpdateMembershipForUserInOrgRequestPath
    body: TeamsAddOrUpdateMembershipForUserInOrgRequestBody | None = None

# Operation: remove_team_member_org
class TeamsRemoveMembershipForUserInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive identifier for the GitHub organization.")
    team_slug: str = Field(default=..., description="The slug of the team name. This is the URL-friendly identifier for the team within the organization.")
    username: str = Field(default=..., description="The GitHub username handle for the user whose team membership will be removed.")
class TeamsRemoveMembershipForUserInOrgRequest(StrictModel):
    """Remove a user's membership from a team. The authenticated user must have admin permissions to the team or be an organization owner. This action does not delete the user account, only removes their team membership."""
    path: TeamsRemoveMembershipForUserInOrgRequestPath

# Operation: list_team_repositories
class TeamsListReposInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
    team_slug: str = Field(default=..., description="The URL-friendly slug identifier for the team name within the organization.")
class TeamsListReposInOrgRequest(StrictModel):
    """Lists all repositories that are visible to the authenticated user and associated with a specific team within an organization. This includes repositories the team has access to through various permission levels."""
    path: TeamsListReposInOrgRequestPath

# Operation: verify_team_repository_permissions
class TeamsCheckPermissionsForRepoInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug of the team name. Case-insensitive.")
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class TeamsCheckPermissionsForRepoInOrgRequest(StrictModel):
    """Verify whether a team has a specific permission level for a repository, including permissions inherited through parent teams. Returns repository details if the team has access, or 404 if the team lacks permission or lacks read access to a private repository."""
    path: TeamsCheckPermissionsForRepoInOrgRequestPath

# Operation: set_team_repository_permission
class TeamsAddOrUpdateRepoPermissionsInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier for the team within the organization.")
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class TeamsAddOrUpdateRepoPermissionsInOrgRequestBody(StrictModel):
    permission: str | None = Field(default=None, description="The permission level to grant the team on this repository. If not specified, the team's existing permission will be used. Accepts standard permission levels or custom repository role names defined by the organization.")
class TeamsAddOrUpdateRepoPermissionsInOrgRequest(StrictModel):
    """Grant or update a team's permission level on a repository owned by the organization. The authenticated user must have admin access to the repository and visibility of the team."""
    path: TeamsAddOrUpdateRepoPermissionsInOrgRequestPath
    body: TeamsAddOrUpdateRepoPermissionsInOrgRequestBody | None = None

# Operation: remove_repository_from_team
class TeamsRemoveRepoInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. Case-insensitive.")
    team_slug: str = Field(default=..., description="The slug identifier for the team name. Case-insensitive.")
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class TeamsRemoveRepoInOrgRequest(StrictModel):
    """Remove a repository from a team within an organization. This action does not delete the repository, only removes the team's access to it. Requires organization owner, team maintainer, or admin access to the repository."""
    path: TeamsRemoveRepoInOrgRequestPath

# Operation: list_child_teams
class TeamsListChildInOrgRequestPath(StrictModel):
    org: str = Field(default=..., description="The organization name. The name is not case sensitive.")
    team_slug: str = Field(default=..., description="The slug of the team name, used to identify the parent team whose child teams should be listed.")
class TeamsListChildInOrgRequest(StrictModel):
    """Lists all child teams nested under a specified team within an organization. This operation retrieves the direct child teams only, not grandchild teams."""
    path: TeamsListChildInOrgRequestPath

# Operation: get_repository
class ReposGetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposGetRequest(StrictModel):
    """Retrieve detailed information about a specific repository, including fork relationships and security settings. Admin or security manager permissions are required to view security and analysis data."""
    path: ReposGetRequestPath

# Operation: update_repository
class ReposUpdateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ReposUpdateRequestBodySecurityAndAnalysisSecretScanningDelegatedBypassOptions(StrictModel):
    reviewers: list[ReposUpdateBodySecurityAndAnalysisSecretScanningDelegatedBypassOptionsReviewersItem] | None = Field(default=None, validation_alias="reviewers", serialization_alias="reviewers", description="List of users who can bypass secret scanning reviews. If omitted, existing reviewers remain unchanged.")
class ReposUpdateRequestBodySecurityAndAnalysis(StrictModel):
    secret_scanning_delegated_bypass_options: ReposUpdateRequestBodySecurityAndAnalysisSecretScanningDelegatedBypassOptions | None = None
class ReposUpdateRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A short description of the repository.")
    homepage: str | None = Field(default=None, description="A URL with more information about the repository.")
    visibility: Literal["public", "private"] | None = Field(default=None, description="The visibility level of the repository.")
    has_issues: bool | None = Field(default=None, description="Enable or disable issues for this repository.")
    has_projects: bool | None = Field(default=None, description="Enable or disable projects for this repository. Note: Defaults to false if the organization has disabled repository projects.")
    has_wiki: bool | None = Field(default=None, description="Enable or disable the wiki for this repository.")
    is_template: bool | None = Field(default=None, description="Make this repository available as a template for others to use.")
    default_branch: str | None = Field(default=None, description="The default branch for this repository.")
    allow_squash_merge: bool | None = Field(default=None, description="Allow squash-merging of pull requests.")
    allow_merge_commit: bool | None = Field(default=None, description="Allow merge commits when merging pull requests.")
    allow_rebase_merge: bool | None = Field(default=None, description="Allow rebase-merging of pull requests.")
    allow_auto_merge: bool | None = Field(default=None, description="Allow auto-merge on pull requests.")
    delete_branch_on_merge: bool | None = Field(default=None, description="Automatically delete head branches when pull requests are merged.")
    allow_update_branch: bool | None = Field(default=None, description="Allow pull request head branches to be updated even if behind the base branch and not required to be up to date before merging.")
    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"] | None = Field(default=None, description="The default title format for squash merge commits. Required when using squash_merge_commit_message.")
    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"] | None = Field(default=None, description="The default message content for squash merge commits.")
    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"] | None = Field(default=None, description="The default title format for merge commits. Required when using merge_commit_message.")
    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"] | None = Field(default=None, description="The default message content for merge commits.")
    archived: bool | None = Field(default=None, description="Archive or unarchive this repository.")
    allow_forking: bool | None = Field(default=None, description="Allow private forks of this repository.")
    web_commit_signoff_required: bool | None = Field(default=None, description="Require contributors to sign off on web-based commits.")
    security_and_analysis: ReposUpdateRequestBodySecurityAndAnalysis | None = None
class ReposUpdateRequest(StrictModel):
    """Update repository settings including visibility, features, merge strategies, and metadata. Note: Use the dedicated endpoint to manage repository topics."""
    path: ReposUpdateRequestPath
    body: ReposUpdateRequestBody | None = None

# Operation: delete_repository
class ReposDeleteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposDeleteRequest(StrictModel):
    """Permanently delete a repository. Requires admin access to the repository, and organization owners may restrict this action for organization-owned repositories."""
    path: ReposDeleteRequestPath

# Operation: list_artifacts
class ActionsListArtifactsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsListArtifactsForRepoRequest(StrictModel):
    """Lists all artifacts for a repository. Anyone with read access can use this endpoint; OAuth apps and personal access tokens need the `repo` scope for private repositories."""
    path: ActionsListArtifactsForRepoRequestPath

# Operation: get_artifact
class ActionsGetArtifactRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    artifact_id: int = Field(default=..., description="The unique identifier of the artifact to retrieve.")
class ActionsGetArtifactRequest(StrictModel):
    """Retrieve a specific artifact from a workflow run. Accessible to anyone with read access to the repository; private repositories require the `repo` scope for OAuth tokens and personal access tokens."""
    path: ActionsGetArtifactRequestPath

# Operation: delete_artifact
class ActionsDeleteArtifactRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    artifact_id: int = Field(default=..., description="The unique identifier of the artifact to delete.")
class ActionsDeleteArtifactRequest(StrictModel):
    """Permanently delete a workflow artifact from a repository. Requires `repo` scope authentication."""
    path: ActionsDeleteArtifactRequestPath

# Operation: download_artifact
class ActionsDownloadArtifactRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    artifact_id: int = Field(default=..., description="The unique identifier of the artifact to download.")
    archive_format: str = Field(default=..., description="The archive format for the downloaded artifact. Must be `zip`.")
class ActionsDownloadArtifactRequest(StrictModel):
    """Download a repository artifact as a ZIP archive. Returns a redirect URL in the response header that expires after 1 minute."""
    path: ActionsDownloadArtifactRequestPath

# Operation: get_cache_retention_limit
class ActionsGetActionsCacheRetentionLimitForRepositoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActionsGetActionsCacheRetentionLimitForRepositoryRequest(StrictModel):
    """Retrieves the GitHub Actions cache retention limit for a repository, which determines how long cached artifacts are retained before automatic eviction due to age or size constraints."""
    path: ActionsGetActionsCacheRetentionLimitForRepositoryRequestPath

# Operation: get_actions_cache_storage_limit_repository
class ActionsGetActionsCacheStorageLimitForRepositoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the .git extension. The name is not case sensitive.")
class ActionsGetActionsCacheStorageLimitForRepositoryRequest(StrictModel):
    """Retrieve the GitHub Actions cache storage limit for a repository, which determines the maximum size of caches before eviction occurs. Requires admin:repository scope."""
    path: ActionsGetActionsCacheStorageLimitForRepositoryRequestPath

# Operation: get_actions_cache_usage
class ActionsGetActionsCacheUsageRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActionsGetActionsCacheUsageRequest(StrictModel):
    """Retrieve GitHub Actions cache usage statistics for a repository. Data is refreshed approximately every 5 minutes, so values may take at least 5 minutes to reflect recent changes."""
    path: ActionsGetActionsCacheUsageRequestPath

# Operation: list_caches
class ActionsGetActionsCacheListRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsGetActionsCacheListRequestQuery(StrictModel):
    key: str | None = Field(default=None, description="Filter caches by an explicit key or key prefix to narrow results to specific cache entries.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort the results by.")
class ActionsGetActionsCacheListRequest(StrictModel):
    """Lists all GitHub Actions caches for a repository. Requires `repo` scope authentication to access cache metadata and management information."""
    path: ActionsGetActionsCacheListRequestPath
    query: ActionsGetActionsCacheListRequestQuery | None = None

# Operation: delete_actions_cache_by_key
class ActionsDeleteActionsCacheByKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsDeleteActionsCacheByKeyRequestQuery(StrictModel):
    key: str = Field(default=..., description="A cache key used to identify and delete matching caches. All caches with this key will be deleted unless filtered by a Git ref.")
class ActionsDeleteActionsCacheByKeyRequest(StrictModel):
    """Delete GitHub Actions caches for a repository by cache key. Optionally restrict deletions to caches matching both the provided key and a specific Git ref."""
    path: ActionsDeleteActionsCacheByKeyRequestPath
    query: ActionsDeleteActionsCacheByKeyRequestQuery

# Operation: delete_actions_cache
class ActionsDeleteActionsCacheByIdRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    cache_id: int = Field(default=..., description="The unique identifier of the GitHub Actions cache to delete.")
class ActionsDeleteActionsCacheByIdRequest(StrictModel):
    """Delete a GitHub Actions cache for a repository by its cache ID. Requires `repo` scope authentication."""
    path: ActionsDeleteActionsCacheByIdRequestPath

# Operation: get_workflow_job
class ActionsGetJobForWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    job_id: int = Field(default=..., description="The unique identifier of the job to retrieve.")
class ActionsGetJobForWorkflowRunRequest(StrictModel):
    """Retrieve details for a specific job within a workflow run. Anyone with read access to the repository can use this endpoint."""
    path: ActionsGetJobForWorkflowRunRequestPath

# Operation: get_workflow_job_logs
class ActionsDownloadJobLogsForWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    job_id: int = Field(default=..., description="The unique identifier of the job to retrieve logs for.")
class ActionsDownloadJobLogsForWorkflowRunRequest(StrictModel):
    """Retrieve a download URL for workflow job logs as plain text. The returned redirect URL expires after 1 minute and is found in the `Location` response header."""
    path: ActionsDownloadJobLogsForWorkflowRunRequestPath

# Operation: rerun_workflow_job
class ActionsReRunJobForWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    job_id: int = Field(default=..., description="The unique identifier of the job to re-run.")
class ActionsReRunJobForWorkflowRunRequestBody(StrictModel):
    enable_debug_logging: bool | None = Field(default=None, description="Whether to enable debug logging for the re-run.")
class ActionsReRunJobForWorkflowRunRequest(StrictModel):
    """Re-run a job and its dependent jobs in a workflow run. Requires `repo` scope for OAuth apps and personal access tokens (classic)."""
    path: ActionsReRunJobForWorkflowRunRequestPath
    body: ActionsReRunJobForWorkflowRunRequestBody | None = None

# Operation: get_oidc_subject_claim_customization
class ActionsGetCustomOidcSubClaimForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActionsGetCustomOidcSubClaimForRepoRequest(StrictModel):
    """Retrieve the customization template for an OpenID Connect (OIDC) subject claim in a repository. This template defines how the OIDC subject claim is formatted for GitHub Actions workflows."""
    path: ActionsGetCustomOidcSubClaimForRepoRequestPath

# Operation: list_organization_secrets_available_to_repository
class ActionsListRepoOrganizationSecretsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActionsListRepoOrganizationSecretsRequest(StrictModel):
    """Retrieve all organization secrets shared with a repository, displaying metadata without revealing encrypted values. Requires collaborator access to the repository."""
    path: ActionsListRepoOrganizationSecretsRequestPath

# Operation: list_organization_variables_shared
class ActionsListRepoOrganizationVariablesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ActionsListRepoOrganizationVariablesRequest(StrictModel):
    """Retrieve all organization variables that are shared with a specific repository. Requires collaborator access to the repository."""
    path: ActionsListRepoOrganizationVariablesRequestPath

# Operation: list_runners
class ActionsListSelfHostedRunnersForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsListSelfHostedRunnersForRepoRequest(StrictModel):
    """Lists all self-hosted runners configured in a repository. Requires admin access to the repository."""
    path: ActionsListSelfHostedRunnersForRepoRequestPath

# Operation: list_runner_downloads
class ActionsListRunnerApplicationsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActionsListRunnerApplicationsForRepoRequest(StrictModel):
    """Lists available runner application binaries that can be downloaded and executed for a repository. Requires admin access to the repository."""
    path: ActionsListRunnerApplicationsForRepoRequestPath

# Operation: generate_runner_removal_token_repository
class ActionsCreateRemoveTokenForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsCreateRemoveTokenForRepoRequest(StrictModel):
    """Generate a removal token for a self-hosted runner in a repository. The token expires after one hour and can be used with the config script to remove the runner."""
    path: ActionsCreateRemoveTokenForRepoRequestPath

# Operation: get_runner_repo
class ActionsGetSelfHostedRunnerForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to retrieve.")
class ActionsGetSelfHostedRunnerForRepoRequest(StrictModel):
    """Retrieve details for a specific self-hosted runner configured in a repository. Requires admin access to the repository."""
    path: ActionsGetSelfHostedRunnerForRepoRequestPath

# Operation: remove_runner_from_repository
class ActionsDeleteSelfHostedRunnerFromRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to remove.")
class ActionsDeleteSelfHostedRunnerFromRepoRequest(StrictModel):
    """Permanently remove a self-hosted runner from a repository. Use this endpoint when the runner machine no longer exists or you need to completely deregister it from the repository."""
    path: ActionsDeleteSelfHostedRunnerFromRepoRequestPath

# Operation: list_runner_labels_for_repo
class ActionsListLabelsForSelfHostedRunnerForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner.")
class ActionsListLabelsForSelfHostedRunnerForRepoRequest(StrictModel):
    """Retrieve all labels assigned to a self-hosted runner in a repository. Requires admin access to the repository."""
    path: ActionsListLabelsForSelfHostedRunnerForRepoRequestPath

# Operation: add_labels_to_runner_for_repo
class ActionsAddCustomLabelsToSelfHostedRunnerForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to add labels to.")
class ActionsAddCustomLabelsToSelfHostedRunnerForRepoRequestBody(StrictModel):
    labels: list[str] = Field(default=..., description="An array of custom label names to add to the runner. Each label is a string identifier.", min_length=1, max_length=100)
class ActionsAddCustomLabelsToSelfHostedRunnerForRepoRequest(StrictModel):
    """Add custom labels to a self-hosted runner in a repository. Requires admin access to the organization and `repo` scope for authentication."""
    path: ActionsAddCustomLabelsToSelfHostedRunnerForRepoRequestPath
    body: ActionsAddCustomLabelsToSelfHostedRunnerForRepoRequestBody

# Operation: update_runner_labels_repo
class ActionsSetCustomLabelsForSelfHostedRunnerForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner to update.")
class ActionsSetCustomLabelsForSelfHostedRunnerForRepoRequestBody(StrictModel):
    labels: list[str] = Field(default=..., description="An array of custom label names to assign to the runner. Pass an empty array to remove all custom labels. Labels are unordered.", min_length=0, max_length=100)
class ActionsSetCustomLabelsForSelfHostedRunnerForRepoRequest(StrictModel):
    """Replace all custom labels for a self-hosted runner in a repository. Requires admin access to the repository and appropriate OAuth or personal access token permissions."""
    path: ActionsSetCustomLabelsForSelfHostedRunnerForRepoRequestPath
    body: ActionsSetCustomLabelsForSelfHostedRunnerForRepoRequestBody

# Operation: remove_all_custom_labels_from_runner_for_repo
class ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner.")
class ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForRepoRequest(StrictModel):
    """Remove all custom labels from a self-hosted runner in a repository, returning only the read-only labels that remain. Requires admin access to the repository."""
    path: ActionsRemoveAllCustomLabelsFromSelfHostedRunnerForRepoRequestPath

# Operation: remove_runner_label
class ActionsRemoveCustomLabelFromSelfHostedRunnerForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    runner_id: int = Field(default=..., description="The unique identifier of the self-hosted runner.")
    name: str = Field(default=..., description="The name of the custom label to remove from the runner.")
class ActionsRemoveCustomLabelFromSelfHostedRunnerForRepoRequest(StrictModel):
    """Remove a custom label from a self-hosted runner in a repository. Returns the remaining labels after removal. Requires admin access to the repository."""
    path: ActionsRemoveCustomLabelFromSelfHostedRunnerForRepoRequestPath

# Operation: list_workflow_runs
class ActionsListWorkflowRunsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ActionsListWorkflowRunsForRepoRequestQuery(StrictModel):
    actor: str | None = Field(default=None, description="Filter results to workflow runs created by a specific user. Use the login name of the user who created the associated push or check suite.")
    branch: str | None = Field(default=None, description="Filter results to workflow runs associated with a specific branch. Use the branch name from the push event.")
    created: str | None = Field(default=None, description="Filter results to workflow runs created within a specified date-time range using GitHub search syntax (e.g., `>2023-01-01`, `2023-01-01..2023-12-31`).", json_schema_extra={'format': 'date-time'})
    exclude_pull_requests: bool | None = Field(default=None, description="Exclude pull request workflow runs from the response when set to true.")
    check_suite_id: int | None = Field(default=None, description="Filter results to workflow runs associated with a specific check suite ID.")
    head_sha: str | None = Field(default=None, description="Filter results to workflow runs associated with a specific commit SHA.")
class ActionsListWorkflowRunsForRepoRequest(StrictModel):
    """Retrieve all workflow runs for a repository with optional filtering by actor, branch, date range, and other criteria. Anyone with read access can use this endpoint; up to 1,000 results are returned per search when using certain filter parameters."""
    path: ActionsListWorkflowRunsForRepoRequestPath
    query: ActionsListWorkflowRunsForRepoRequestQuery | None = None

# Operation: get_workflow_run
class ActionsGetWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run.")
class ActionsGetWorkflowRunRequestQuery(StrictModel):
    exclude_pull_requests: bool | None = Field(default=None, description="If true, pull requests are omitted from the response as an empty array.")
class ActionsGetWorkflowRunRequest(StrictModel):
    """Retrieve details about a specific workflow run in a repository. Anyone with read access can use this endpoint."""
    path: ActionsGetWorkflowRunRequestPath
    query: ActionsGetWorkflowRunRequestQuery | None = None

# Operation: delete_workflow_run
class ActionsDeleteWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to delete.")
class ActionsDeleteWorkflowRunRequest(StrictModel):
    """Delete a specific workflow run from a repository. Requires write access to the repository; private repositories need the `repo` scope for OAuth tokens and personal access tokens (classic)."""
    path: ActionsDeleteWorkflowRunRequestPath

# Operation: list_workflow_run_approvals
class ActionsGetReviewsForRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to retrieve approvals for.")
class ActionsGetReviewsForRunRequest(StrictModel):
    """Retrieve the review and approval history for a specific workflow run. Anyone with read access to the repository can use this endpoint."""
    path: ActionsGetReviewsForRunRequestPath

# Operation: approve_workflow_run
class ActionsApproveWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to approve.")
class ActionsApproveWorkflowRunRequest(StrictModel):
    """Approve a workflow run for a pull request from a public fork of a first-time contributor. This allows the workflow to proceed after security review. Requires `repo` scope authentication."""
    path: ActionsApproveWorkflowRunRequestPath

# Operation: list_workflow_run_artifacts
class ActionsListWorkflowRunArtifactsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run.")
class ActionsListWorkflowRunArtifactsRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort the results by.")
class ActionsListWorkflowRunArtifactsRequest(StrictModel):
    """Lists all artifacts generated by a specific workflow run. Requires read access to the repository."""
    path: ActionsListWorkflowRunArtifactsRequestPath
    query: ActionsListWorkflowRunArtifactsRequestQuery | None = None

# Operation: get_workflow_run_attempt
class ActionsGetWorkflowRunAttemptRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run.")
    attempt_number: int = Field(default=..., description="The attempt number of the workflow run.")
class ActionsGetWorkflowRunAttemptRequestQuery(StrictModel):
    exclude_pull_requests: bool | None = Field(default=None, description="If true, pull requests are omitted from the response as an empty array.")
class ActionsGetWorkflowRunAttemptRequest(StrictModel):
    """Retrieve details about a specific workflow run attempt. Anyone with read access to the repository can use this endpoint."""
    path: ActionsGetWorkflowRunAttemptRequestPath
    query: ActionsGetWorkflowRunAttemptRequestQuery | None = None

# Operation: list_workflow_run_attempt_jobs
class ActionsListJobsForWorkflowRunAttemptRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run.")
    attempt_number: int = Field(default=..., description="The attempt number of the workflow run, used to identify a specific retry or re-run of the workflow.")
class ActionsListJobsForWorkflowRunAttemptRequest(StrictModel):
    """Lists all jobs for a specific workflow run attempt. Use this endpoint to retrieve job details and status for a particular attempt of a workflow run."""
    path: ActionsListJobsForWorkflowRunAttemptRequestPath

# Operation: download_workflow_run_attempt_logs
class ActionsDownloadWorkflowRunAttemptLogsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run.")
    attempt_number: int = Field(default=..., description="The attempt number of the workflow run, indicating which retry or re-run of the workflow to retrieve logs for.")
class ActionsDownloadWorkflowRunAttemptLogsRequest(StrictModel):
    """Retrieves a redirect URL to download an archive of log files for a specific workflow run attempt. The download link expires after 1 minute, so check the `Location` response header for the actual download URL."""
    path: ActionsDownloadWorkflowRunAttemptLogsRequestPath

# Operation: cancel_workflow_run
class ActionsCancelWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to cancel.")
class ActionsCancelWorkflowRunRequest(StrictModel):
    """Cancel an in-progress workflow run by its unique identifier. Requires `repo` scope authorization."""
    path: ActionsCancelWorkflowRunRequestPath

# Operation: review_deployment_protection_rule
class ActionsReviewCustomGatesForRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to review protection rules for.")
class ActionsReviewCustomGatesForRunRequestBody(StrictModel):
    environment_name: str = Field(default=..., description="The name of the environment for which to approve or reject the deployment protection rule.")
    comment: str | None = Field(default=None, description="Optional comment to associate with the deployment protection rule review. Required if state is not provided.")
    state: Literal["approved", "rejected"] | None = Field(default=None, description="The decision for the deployment protection rule: approve to allow deployment or reject to block it.")
class ActionsReviewCustomGatesForRunRequest(StrictModel):
    """Approve or reject custom deployment protection rules for a workflow run. This allows GitHub Apps to review their own deployment protection rules before allowing a workflow to proceed to a specified environment."""
    path: ActionsReviewCustomGatesForRunRequestPath
    body: ActionsReviewCustomGatesForRunRequestBody

# Operation: force_cancel_workflow_run
class ActionsForceCancelWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to force cancel.")
class ActionsForceCancelWorkflowRunRequest(StrictModel):
    """Force cancel a workflow run, bypassing conditions like `always()` that would normally allow execution to continue. Use this only when the standard cancel endpoint is unresponsive."""
    path: ActionsForceCancelWorkflowRunRequestPath

# Operation: list_workflow_run_jobs
class ActionsListJobsForWorkflowRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to retrieve jobs for.")
class ActionsListJobsForWorkflowRunRequestQuery(StrictModel):
    filter_: Literal["latest", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter jobs by execution recency. Use `latest` to return jobs from the most recent execution, or `all` to return jobs from all historical executions of the workflow run.")
class ActionsListJobsForWorkflowRunRequest(StrictModel):
    """Retrieve all jobs associated with a specific workflow run, with optional filtering to show only the latest execution or all historical executions. Requires read access to the repository."""
    path: ActionsListJobsForWorkflowRunRequestPath
    query: ActionsListJobsForWorkflowRunRequestQuery | None = None

# Operation: get_workflow_run_logs_download_url
class ActionsDownloadWorkflowRunLogsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the .git extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to download logs for.")
class ActionsDownloadWorkflowRunLogsRequest(StrictModel):
    """Retrieves a temporary download URL for workflow run logs archive. The returned redirect URL expires after 1 minute and is found in the Location response header."""
    path: ActionsDownloadWorkflowRunLogsRequestPath

# Operation: delete_workflow_run_logs
class ActionsDeleteWorkflowRunLogsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run whose logs should be deleted.")
class ActionsDeleteWorkflowRunLogsRequest(StrictModel):
    """Permanently delete all logs associated with a specific workflow run. Requires `repo` scope authentication."""
    path: ActionsDeleteWorkflowRunLogsRequestPath

# Operation: list_pending_deployments
class ActionsGetPendingDeploymentsForRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to retrieve pending deployments for.")
class ActionsGetPendingDeploymentsForRunRequest(StrictModel):
    """Retrieve all deployment environments for a workflow run that are awaiting protection rule approval. This endpoint helps identify which deployments are blocked and require manual or automated approval to proceed."""
    path: ActionsGetPendingDeploymentsForRunRequestPath

# Operation: review_pending_deployments
class ActionsReviewPendingDeploymentsForRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to review pending deployments for.")
class ActionsReviewPendingDeploymentsForRunRequestBody(StrictModel):
    environment_ids: list[int] = Field(default=..., description="The list of environment IDs to approve or reject. Order is not significant. Each ID must be a valid environment identifier.")
    state: Literal["approved", "rejected"] = Field(default=..., description="Whether to approve or reject deployment to the specified environments.")
    comment: str = Field(default=..., description="A comment to accompany the deployment review, providing context for the approval or rejection decision.")
class ActionsReviewPendingDeploymentsForRunRequest(StrictModel):
    """Approve or reject pending deployments awaiting reviewer approval for a workflow run. Required reviewers with repository access can use this endpoint to gate deployments to specified environments."""
    path: ActionsReviewPendingDeploymentsForRunRequestPath
    body: ActionsReviewPendingDeploymentsForRunRequestBody

# Operation: rerun_workflow
class ActionsReRunWorkflowRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to re-run.")
class ActionsReRunWorkflowRequestBody(StrictModel):
    enable_debug_logging: bool | None = Field(default=None, description="Enable debug logging for the workflow re-run to capture additional diagnostic information.")
class ActionsReRunWorkflowRequest(StrictModel):
    """Re-run a workflow by its run ID. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: ActionsReRunWorkflowRequestPath
    body: ActionsReRunWorkflowRequestBody | None = None

# Operation: rerun_workflow_failed_jobs
class ActionsReRunWorkflowFailedJobsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to re-run failed jobs from.")
class ActionsReRunWorkflowFailedJobsRequestBody(StrictModel):
    enable_debug_logging: bool | None = Field(default=None, description="Whether to enable debug logging for the re-run.")
class ActionsReRunWorkflowFailedJobsRequest(StrictModel):
    """Re-run all failed jobs and their dependent jobs in a workflow run. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: ActionsReRunWorkflowFailedJobsRequestPath
    body: ActionsReRunWorkflowFailedJobsRequestBody | None = None

# Operation: get_workflow_run_usage
class ActionsGetWorkflowRunUsageRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    run_id: int = Field(default=..., description="The unique identifier of the workflow run to retrieve usage metrics for.")
class ActionsGetWorkflowRunUsageRequest(StrictModel):
    """Retrieve billable minutes and total execution time for a specific workflow run. This endpoint is deprecated and will be shut down; refer to GitHub's official announcement for migration guidance."""
    path: ActionsGetWorkflowRunUsageRequestPath

# Operation: list_repository_secrets
class ActionsListRepoSecretsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ActionsListRepoSecretsRequest(StrictModel):
    """Retrieve all secrets configured in a repository without exposing their encrypted values. Requires collaborator access to the repository."""
    path: ActionsListRepoSecretsRequestPath

# Operation: get_repository_public_key
class ActionsGetRepoPublicKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsGetRepoPublicKeyRequest(StrictModel):
    """Retrieves the public key for a repository, which is required to encrypt secrets before creating or updating them. Read access to the repository is sufficient to use this endpoint."""
    path: ActionsGetRepoPublicKeyRequestPath

# Operation: get_repository_secret
class ActionsGetRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class ActionsGetRepoSecretRequest(StrictModel):
    """Retrieve metadata for a specific repository secret without exposing its encrypted value. Requires collaborator access to the repository."""
    path: ActionsGetRepoSecretRequestPath

# Operation: delete_repository_secret
class ActionsDeleteRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository, excluding the `.git` extension. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to delete.")
class ActionsDeleteRepoSecretRequest(StrictModel):
    """Delete a secret from a repository by name. Requires collaborator access and appropriate authentication scope."""
    path: ActionsDeleteRepoSecretRequestPath

# Operation: list_repository_variables
class ActionsListRepoVariablesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
class ActionsListRepoVariablesRequest(StrictModel):
    """Retrieve all variables configured for a repository. Authenticated users must have collaborator access to read variables."""
    path: ActionsListRepoVariablesRequestPath

# Operation: create_repository_variable
class ActionsCreateRepoVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ActionsCreateRepoVariableRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the variable. Used as the identifier for referencing this variable in workflows.")
    value: str = Field(default=..., description="The value assigned to the variable. This is the data that will be available in GitHub Actions workflows.")
class ActionsCreateRepoVariableRequest(StrictModel):
    """Create a repository variable for use in GitHub Actions workflows. Requires collaborator access to the repository."""
    path: ActionsCreateRepoVariableRequestPath
    body: ActionsCreateRepoVariableRequestBody

# Operation: get_repository_variable
class ActionsGetRepoVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    name: str = Field(default=..., description="The name of the variable to retrieve.")
class ActionsGetRepoVariableRequest(StrictModel):
    """Retrieve a specific variable from a repository. The authenticated user must have collaborator access to the repository."""
    path: ActionsGetRepoVariableRequestPath

# Operation: update_repository_variable
class ActionsUpdateRepoVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    name: str = Field(default=..., description="The name of the variable to update.")
class ActionsUpdateRepoVariableRequestBody(StrictModel):
    value: str | None = Field(default=None, description="The new value for the variable.")
class ActionsUpdateRepoVariableRequest(StrictModel):
    """Update a repository variable that can be referenced in GitHub Actions workflows. Requires collaborator access to the repository."""
    path: ActionsUpdateRepoVariableRequestPath
    body: ActionsUpdateRepoVariableRequestBody | None = None

# Operation: delete_repository_variable
class ActionsDeleteRepoVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    name: str = Field(default=..., description="The name of the variable to delete.")
class ActionsDeleteRepoVariableRequest(StrictModel):
    """Delete a repository variable by name. Requires collaborator access to the repository and appropriate OAuth or personal access token permissions."""
    path: ActionsDeleteRepoVariableRequestPath

# Operation: list_workflows
class ActionsListRepoWorkflowsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActionsListRepoWorkflowsRequest(StrictModel):
    """Lists all workflows in a repository. Anyone with read access can use this endpoint; private repositories require the `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: ActionsListRepoWorkflowsRequestPath

# Operation: get_workflow
class ActionsGetWorkflowRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    workflow_id: str = Field(default=..., description="The ID of the workflow or the workflow file name (e.g., `main.yaml`). Accepts integer ID or string file name.")
class ActionsGetWorkflowRequest(StrictModel):
    """Retrieve a specific workflow by its ID or file name. Anyone with read access to the repository can use this endpoint."""
    path: ActionsGetWorkflowRequestPath

# Operation: disable_workflow
class ActionsDisableWorkflowRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    workflow_id: str = Field(default=..., description="The ID of the workflow or the workflow file name as a string identifier.")
class ActionsDisableWorkflowRequest(StrictModel):
    """Disable a workflow and set its state to `disabled_manually`. You can reference the workflow by its ID or file name (e.g., `main.yaml`)."""
    path: ActionsDisableWorkflowRequestPath

# Operation: trigger_workflow
class ActionsCreateWorkflowDispatchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    workflow_id: str = Field(default=..., description="The ID of the workflow. You can also pass the workflow file name as a string.")
class ActionsCreateWorkflowDispatchRequestBody(StrictModel):
    ref: str = Field(default=..., description="The git reference (branch or tag name) where the workflow should run.")
    inputs: dict[str, Any] | None = Field(default=None, description="Input keys and values configured in the workflow file. Maximum of 25 properties. Default values from the workflow file are used if inputs are omitted.", max_length=25)
    return_run_details: bool | None = Field(default=None, description="Whether the response should include the workflow run ID and URLs.")
class ActionsCreateWorkflowDispatchRequest(StrictModel):
    """Manually trigger a GitHub Actions workflow run by dispatching a workflow_dispatch event. The workflow must be configured to respond to workflow_dispatch events, and you can optionally provide input values that are defined in the workflow file."""
    path: ActionsCreateWorkflowDispatchRequestPath
    body: ActionsCreateWorkflowDispatchRequestBody

# Operation: enable_workflow
class ActionsEnableWorkflowRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the .git extension. The name is case-insensitive.")
    workflow_id: str = Field(default=..., description="The workflow identifier, which can be either the numeric ID or the workflow file name (e.g., main.yaml).")
class ActionsEnableWorkflowRequest(StrictModel):
    """Activates a workflow by setting its state to active. You can reference the workflow by its ID or file name (e.g., main.yaml)."""
    path: ActionsEnableWorkflowRequestPath

# Operation: list_workflow_runs_for_workflow
class ActionsListWorkflowRunsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    workflow_id: str = Field(default=..., description="The ID of the workflow or the workflow file name (e.g., `main.yaml`). Accepts both string and integer formats.")
class ActionsListWorkflowRunsRequestQuery(StrictModel):
    actor: str | None = Field(default=None, description="Filter results to show workflow runs created by a specific user. Use the login name of the user who created the associated push.")
    branch: str | None = Field(default=None, description="Filter results to show workflow runs associated with a specific branch. Use the branch name from the push event.")
    created: str | None = Field(default=None, description="Filter results to show workflow runs created within a specified date-time range. Use standard search syntax for date queries.", json_schema_extra={'format': 'date-time'})
    exclude_pull_requests: bool | None = Field(default=None, description="If true, pull request workflow runs are excluded from the response.")
    check_suite_id: int | None = Field(default=None, description="Filter results to show workflow runs associated with a specific check suite ID.")
    head_sha: str | None = Field(default=None, description="Filter results to show only workflow runs associated with the specified commit SHA.")
class ActionsListWorkflowRunsRequest(StrictModel):
    """List all workflow runs for a specific workflow in a repository. You can filter results by actor, branch, date range, and other criteria to narrow down the results."""
    path: ActionsListWorkflowRunsRequestPath
    query: ActionsListWorkflowRunsRequestQuery | None = None

# Operation: list_repository_activities
class ReposListActivitiesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ReposListActivitiesRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort order for results.")
    actor: str | None = Field(default=None, description="Filter activities by the GitHub username of the user who performed the action.")
    time_period: Literal["day", "week", "month", "quarter", "year"] | None = Field(default=None, description="Filter activities by the time window in which they occurred (e.g., `day` for the past 24 hours, `week` for the past 7 days).")
    activity_type: Literal["push", "force_push", "branch_creation", "branch_deletion", "pr_merge", "merge_queue_merge"] | None = Field(default=None, description="Filter activities by type (e.g., `force_push` to show only force pushes, `pr_merge` to show pull request merges).")
class ReposListActivitiesRequest(StrictModel):
    """Retrieve a detailed history of repository changes including pushes, merges, force pushes, and branch modifications, with associations to commits and users. Use filters to narrow results by actor, time period, or activity type."""
    path: ReposListActivitiesRequestPath
    query: ReposListActivitiesRequestQuery | None = None

# Operation: list_assignees
class IssuesListAssigneesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class IssuesListAssigneesRequest(StrictModel):
    """Retrieves the list of available assignees for issues and pull requests in a repository. Use this to discover which users can be assigned to work items."""
    path: IssuesListAssigneesRequestPath

# Operation: verify_assignee_permission
class IssuesCheckUserCanBeAssignedRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    assignee: str = Field(default=..., description="The username of the user to check for assignment permission.")
class IssuesCheckUserCanBeAssignedRequest(StrictModel):
    """Verify whether a user has permission to be assigned to issues in a repository. Returns a 204 status if the user can be assigned, or 404 if they cannot."""
    path: IssuesCheckUserCanBeAssignedRequestPath

# Operation: create_attestation
class ReposCreateAttestationRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposCreateAttestationRequestBodyBundle(StrictModel):
    media_type: str | None = Field(default=None, validation_alias="mediaType", serialization_alias="mediaType", description="The media type that specifies the format of the attestation payload being submitted.")
    verification_material: dict[str, Any] | None = Field(default=None, validation_alias="verificationMaterial", serialization_alias="verificationMaterial", description="The verification material containing cryptographic proof and supporting evidence for the attestation.")
    dsse_envelope: dict[str, Any] | None = Field(default=None, validation_alias="dsseEnvelope", serialization_alias="dsseEnvelope", description="The DSSE (Dead Simple Signing Envelope) containing the signed attestation statement and signature.")
class ReposCreateAttestationRequestBody(StrictModel):
    bundle: ReposCreateAttestationRequestBodyBundle | None = None
class ReposCreateAttestationRequest(StrictModel):
    """Store an artifact attestation and associate it with a repository. The authenticated user must have write permission to the repository and, if using a fine-grained access token, the `attestations:write` permission is required."""
    path: ReposCreateAttestationRequestPath
    body: ReposCreateAttestationRequestBody | None = None

# Operation: list_attestations
class ReposListAttestationsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    subject_digest: str = Field(default=..., description="The attestation subject's SHA256 digest in the format `sha256:HEX_DIGEST`.")
class ReposListAttestationsRequestQuery(StrictModel):
    predicate_type: str | None = Field(default=None, description="Optional filter to retrieve attestations matching a specific predicate type. Supports standard types like provenance and sbom, or custom freeform text for user-defined predicates.")
class ReposListAttestationsRequest(StrictModel):
    """Retrieve artifact attestations for a given subject digest in a repository. The authenticated user must have read access to the repository and the `attestations:read` permission when using fine-grained access tokens. Attestations should be cryptographically verified using GitHub CLI before relying on them for security decisions."""
    path: ReposListAttestationsRequestPath
    query: ReposListAttestationsRequestQuery | None = None

# Operation: list_autolinks
class ReposListAutolinksRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposListAutolinksRequest(StrictModel):
    """Retrieve all autolinks configured for a repository. This operation is only available to repository administrators and returns autolink configurations that automatically convert references to external URLs."""
    path: ReposListAutolinksRequestPath

# Operation: create_autolink
class ReposCreateAutolinkRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposCreateAutolinkRequestBody(StrictModel):
    key_prefix: str = Field(default=..., description="The prefix that triggers autolink generation when found in issues, pull requests, or commits. The prefix is appended by certain characters to create the link.")
    url_template: str = Field(default=..., description="The URL template for the generated link. Must contain `<num>` as a placeholder for the reference number, which matches alphanumeric or numeric characters depending on the `is_alphanumeric` setting.")
    is_alphanumeric: bool | None = Field(default=None, description="Whether the autolink matches alphanumeric characters (A-Z case-insensitive, 0-9, and hyphen) or only numeric characters.")
class ReposCreateAutolinkRequest(StrictModel):
    """Create an autolink reference for a repository to automatically generate links when a key prefix is found in issues, pull requests, or commits. Requires admin access to the repository."""
    path: ReposCreateAutolinkRequestPath
    body: ReposCreateAutolinkRequestBody

# Operation: get_autolink
class ReposGetAutolinkRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    autolink_id: int = Field(default=..., description="The unique identifier of the autolink to retrieve.")
class ReposGetAutolinkRequest(StrictModel):
    """Retrieve a specific autolink reference configured for a repository by its unique identifier. Only repository administrators can access autolink information."""
    path: ReposGetAutolinkRequestPath

# Operation: delete_autolink
class ReposDeleteAutolinkRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    autolink_id: int = Field(default=..., description="The unique identifier of the autolink to delete.")
class ReposDeleteAutolinkRequest(StrictModel):
    """Delete an autolink reference from a repository by its unique identifier. Only repository administrators can perform this action."""
    path: ReposDeleteAutolinkRequestPath

# Operation: get_automated_security_fixes_status
class ReposCheckAutomatedSecurityFixesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ReposCheckAutomatedSecurityFixesRequest(StrictModel):
    """Retrieve the Dependabot security updates configuration status for a repository. Returns whether security updates are enabled, disabled, or paused. Requires admin read access to the repository."""
    path: ReposCheckAutomatedSecurityFixesRequestPath

# Operation: enable_automated_security_fixes
class ReposEnableAutomatedSecurityFixesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposEnableAutomatedSecurityFixesRequest(StrictModel):
    """Enable Dependabot security updates for a repository to automatically detect and fix vulnerable dependencies. The authenticated user must have admin access to the repository."""
    path: ReposEnableAutomatedSecurityFixesRequestPath

# Operation: disable_automated_security_fixes
class ReposDisableAutomatedSecurityFixesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposDisableAutomatedSecurityFixesRequest(StrictModel):
    """Disable Dependabot security updates for a repository. The authenticated user must have admin access to the repository."""
    path: ReposDisableAutomatedSecurityFixesRequestPath

# Operation: list_branches
class ReposListBranchesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListBranchesRequestQuery(StrictModel):
    protected: bool | None = Field(default=None, description="Filter branches by protection status. Set to `true` to return only branches protected by branch protections or rulesets, or `false` to return only unprotected branches. Omit to return all branches.")
class ReposListBranchesRequest(StrictModel):
    """Retrieve a list of branches in a repository, with optional filtering by protection status. Use the protected parameter to filter for branches with active branch protections or rulesets."""
    path: ReposListBranchesRequestPath
    query: ReposListBranchesRequestQuery | None = None

# Operation: get_branch
class ReposGetBranchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard-based branch queries.")
class ReposGetBranchRequest(StrictModel):
    """Retrieve detailed information about a specific branch in a repository, including its commit reference and protection status."""
    path: ReposGetBranchRequestPath

# Operation: get_branch_protection
class ReposGetBranchProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard branch name queries.")
class ReposGetBranchProtectionRequest(StrictModel):
    """Retrieve branch protection rules for a specific branch. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposGetBranchProtectionRequestPath

# Operation: configure_branch_protection
class ReposUpdateBranchProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The branch name to protect. Wildcard characters are not supported; use GraphQL API for pattern-based protection.")
class ReposUpdateBranchProtectionRequestBodyRequiredStatusChecks(StrictModel):
    strict: bool = Field(default=..., validation_alias="strict", serialization_alias="strict", description="Require branches to be up to date with the base branch before merging.")
    checks: list[ReposUpdateBranchProtectionBodyRequiredStatusChecksChecksItem] | None = Field(default=None, validation_alias="checks", serialization_alias="checks", description="List of status checks that must pass before merging. Order is not significant.")
class ReposUpdateBranchProtectionRequestBodyRequiredPullRequestReviewsDismissalRestrictions(StrictModel):
    users: list[str] | None = Field(default=None, validation_alias="users", serialization_alias="users", description="User logins with permission to dismiss pull request reviews. Order is not significant.")
    teams: list[str] | None = Field(default=None, validation_alias="teams", serialization_alias="teams", description="Team slugs with permission to dismiss pull request reviews. Order is not significant.")
    apps: list[str] | None = Field(default=None, validation_alias="apps", serialization_alias="apps", description="App slugs with permission to dismiss pull request reviews. Order is not significant.")
class ReposUpdateBranchProtectionRequestBodyRequiredPullRequestReviewsBypassPullRequestAllowances(StrictModel):
    users: list[str] | None = Field(default=None, validation_alias="users", serialization_alias="users", description="User logins allowed to bypass pull request review requirements. Order is not significant.")
    teams: list[str] | None = Field(default=None, validation_alias="teams", serialization_alias="teams", description="Team slugs allowed to bypass pull request review requirements. Order is not significant.")
    apps: list[str] | None = Field(default=None, validation_alias="apps", serialization_alias="apps", description="App slugs allowed to bypass pull request review requirements. Order is not significant.")
class ReposUpdateBranchProtectionRequestBodyRequiredPullRequestReviews(StrictModel):
    dismiss_stale_reviews: bool | None = Field(default=None, validation_alias="dismiss_stale_reviews", serialization_alias="dismiss_stale_reviews", description="Automatically dismiss approving reviews when new commits are pushed.")
    require_code_owner_reviews: bool | None = Field(default=None, validation_alias="require_code_owner_reviews", serialization_alias="require_code_owner_reviews", description="Require code owners to review pull requests before merging.")
    required_approving_review_count: int | None = Field(default=None, validation_alias="required_approving_review_count", serialization_alias="required_approving_review_count", description="Number of reviewers required to approve pull requests. Valid range is 0 to 6, where 0 means no reviewer approval required.")
    require_last_push_approval: bool | None = Field(default=None, validation_alias="require_last_push_approval", serialization_alias="require_last_push_approval", description="Require the most recent push to be approved by someone other than the person who pushed it.")
    dismissal_restrictions: ReposUpdateBranchProtectionRequestBodyRequiredPullRequestReviewsDismissalRestrictions | None = None
    bypass_pull_request_allowances: ReposUpdateBranchProtectionRequestBodyRequiredPullRequestReviewsBypassPullRequestAllowances | None = None
class ReposUpdateBranchProtectionRequestBodyRestrictions(StrictModel):
    users: list[str] = Field(default=..., validation_alias="users", serialization_alias="users", description="User logins with push access to the branch. Order is not significant.")
    teams: list[str] = Field(default=..., validation_alias="teams", serialization_alias="teams", description="Team slugs with push access to the branch. Order is not significant.")
    apps: list[str] | None = Field(default=None, validation_alias="apps", serialization_alias="apps", description="App slugs with push access to the branch. Order is not significant.")
class ReposUpdateBranchProtectionRequestBody(StrictModel):
    enforce_admins: bool | None = Field(default=..., description="Enforce all configured restrictions for administrators. Set to `true` to apply required status checks to admins, or `null` to disable enforcement.")
    required_linear_history: bool | None = Field(default=None, description="Enforce a linear commit history by preventing merge commits. Requires squash or rebase merging to be enabled.")
    allow_force_pushes: bool | None = Field(default=None, description="Allow force pushes to the protected branch for users with write access. Set to `null` to block force pushes.")
    allow_deletions: bool | None = Field(default=None, description="Allow deletion of the protected branch by users with write access.")
    block_creations: bool | None = Field(default=None, description="Block creation of new branches when push restrictions are enabled, unless the push is from an authorized user, team, or app.")
    required_conversation_resolution: bool | None = Field(default=None, description="Require all conversations on code to be resolved before merging pull requests.")
    lock_branch: bool | None = Field(default=None, description="Set the branch as read-only, preventing all pushes. Users cannot push to a locked branch.")
    allow_fork_syncing: bool | None = Field(default=None, description="Allow users to pull changes from upstream when the branch is locked, enabling fork synchronization.")
    required_status_checks: ReposUpdateBranchProtectionRequestBodyRequiredStatusChecks
    required_pull_request_reviews: ReposUpdateBranchProtectionRequestBodyRequiredPullRequestReviews | None = None
    restrictions: ReposUpdateBranchProtectionRequestBodyRestrictions
class ReposUpdateBranchProtectionRequest(StrictModel):
    """Configure comprehensive protection rules for a repository branch, including status checks, pull request reviews, push restrictions, and merge requirements. Requires admin or owner permissions."""
    path: ReposUpdateBranchProtectionRequestPath
    body: ReposUpdateBranchProtectionRequestBody

# Operation: remove_branch_protection
class ReposDeleteBranchProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to remove protection from. Cannot contain wildcard characters; use the GraphQL API for wildcard branch names.")
class ReposDeleteBranchProtectionRequest(StrictModel):
    """Remove branch protection rules from a specified branch. Branch protection is available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposDeleteBranchProtectionRequestPath

# Operation: get_branch_admin_protection
class ReposGetAdminBranchProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard branch name queries.")
class ReposGetAdminBranchProtectionRequest(StrictModel):
    """Retrieve whether admin enforcement is enabled for a protected branch. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, Team, Enterprise Cloud, and Enterprise Server."""
    path: ReposGetAdminBranchProtectionRequestPath

# Operation: enforce_admin_branch_protection
class ReposSetAdminBranchProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to enforce admin protection on. Cannot contain wildcard characters; use the GraphQL API for wildcard branch names.")
class ReposSetAdminBranchProtectionRequest(StrictModel):
    """Enforce admin branch protection on a protected branch, requiring administrators to follow branch protection rules. This action requires admin or owner permissions and branch protection to be already enabled."""
    path: ReposSetAdminBranchProtectionRequestPath

# Operation: disable_admin_branch_protection
class ReposDeleteAdminBranchProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The name of the branch to modify. Cannot contain wildcard characters.")
class ReposDeleteAdminBranchProtectionRequest(StrictModel):
    """Disable admin enforcement on a protected branch. Requires admin or owner permissions and branch protection must already be enabled."""
    path: ReposDeleteAdminBranchProtectionRequestPath

# Operation: check_branch_signature_protection
class ReposGetCommitSignatureProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The name of the branch to check for signature protection requirements. Cannot contain wildcard characters.")
class ReposGetCommitSignatureProtectionRequest(StrictModel):
    """Check whether a branch requires signed commits. Returns the signature protection status for a protected branch when you have admin or owner permissions to the repository."""
    path: ReposGetCommitSignatureProtectionRequestPath

# Operation: disable_branch_signature_protection
class ReposDeleteCommitSignatureProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use GraphQL API for wildcard branch names.")
class ReposDeleteCommitSignatureProtectionRequest(StrictModel):
    """Disable required commit signature protection on a branch. Requires admin or owner permissions to the repository and branch protection must already be enabled."""
    path: ReposDeleteCommitSignatureProtectionRequestPath

# Operation: get_branch_status_checks_protection
class ReposGetStatusChecksProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard branch name queries.")
class ReposGetStatusChecksProtectionRequest(StrictModel):
    """Retrieve the required status checks protection rules for a branch. Status checks must pass before pull requests can be merged into the protected branch."""
    path: ReposGetStatusChecksProtectionRequestPath

# Operation: disable_branch_status_check_protection
class ReposRemoveStatusCheckProtectionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to remove status check protection from. Cannot contain wildcard characters; use the GraphQL API for wildcard branch names.")
class ReposRemoveStatusCheckProtectionRequest(StrictModel):
    """Remove status check protection requirements from a branch. This allows commits to be merged without passing required status checks. Status check protection is available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposRemoveStatusCheckProtectionRequestPath

# Operation: list_status_check_contexts
class ReposGetAllStatusCheckContextsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to retrieve status check contexts for. Cannot contain wildcard characters; use GraphQL API for wildcard support.")
class ReposGetAllStatusCheckContextsRequest(StrictModel):
    """Retrieve all required status check contexts for a protected branch. Status checks must pass before merging is allowed on the specified branch."""
    path: ReposGetAllStatusCheckContextsRequestPath

# Operation: remove_branch_protection_status_check_contexts
class ReposRemoveStatusCheckContextsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters. To use wildcard characters in branch names, use the GraphQL API.")
class ReposRemoveStatusCheckContextsRequestBody(StrictModel):
    body: ReposRemoveStatusCheckContextsBodyV0 | list[str] | None = Field(default=None, description="An array of status check context strings to remove from the branch's required status checks. Each context identifies a specific status check (e.g., a CI/CD service).", examples=[{'contexts': ['continuous-integration/jenkins']}])
class ReposRemoveStatusCheckContextsRequest(StrictModel):
    """Remove specific status check contexts from a protected branch's required status checks. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposRemoveStatusCheckContextsRequestPath
    body: ReposRemoveStatusCheckContextsRequestBody | None = None

# Operation: list_branch_access_restrictions
class ReposGetAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use GraphQL API for wildcard support.")
class ReposGetAccessRestrictionsRequest(StrictModel):
    """List users, teams, and apps with access to a protected branch. Access restrictions are only available for organization-owned repositories."""
    path: ReposGetAccessRestrictionsRequestPath

# Operation: remove_branch_protection_restrictions
class ReposDeleteAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to remove restrictions from. Cannot contain wildcard characters; use the GraphQL API for wildcard branch names.")
class ReposDeleteAccessRestrictionsRequest(StrictModel):
    """Remove access restrictions from a protected branch, allowing anyone with push access to the repository to push to this branch. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposDeleteAccessRestrictionsRequestPath

# Operation: list_apps_with_protected_branch_access
class ReposGetAppsWithAccessToProtectedBranchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard branch name queries.")
class ReposGetAppsWithAccessToProtectedBranchRequest(StrictModel):
    """Lists the GitHub Apps that have push access to a protected branch. Only GitHub Apps installed on the repository with write access to repository contents can be authorized on a protected branch."""
    path: ReposGetAppsWithAccessToProtectedBranchRequestPath

# Operation: update_branch_protection_app_restrictions
class ReposSetAppAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard branch names.")
class ReposSetAppAccessRestrictionsRequestBody(StrictModel):
    apps: list[str] = Field(default=..., description="The GitHub Apps that have push access to this branch, specified using the slugified version of each app name. The total number of users, apps, and teams combined cannot exceed 100 items.")
class ReposSetAppAccessRestrictionsRequest(StrictModel):
    """Replace the list of GitHub Apps with push access to a protected branch. This operation removes all previously authorized apps and grants push access only to the newly specified apps. Only GitHub Apps installed on the repository with write access to repository contents can be authorized."""
    path: ReposSetAppAccessRestrictionsRequestPath
    body: ReposSetAppAccessRestrictionsRequestBody

# Operation: revoke_app_branch_push_access
class ReposRemoveAppAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The branch name. Wildcard characters are not supported; use GraphQL API for wildcard branch operations.")
class ReposRemoveAppAccessRestrictionsRequestBody(StrictModel):
    apps: list[str] = Field(default=..., description="Array of GitHub App slugified names to revoke push access from. The combined total of users, apps, and teams cannot exceed 100 items. Order is not significant.")
class ReposRemoveAppAccessRestrictionsRequest(StrictModel):
    """Revoke push access permissions for GitHub Apps on a protected branch. This operation removes the ability of specified apps to push to the branch; only apps installed on the repository with write access can be managed."""
    path: ReposRemoveAppAccessRestrictionsRequestPath
    body: ReposRemoveAppAccessRestrictionsRequestBody

# Operation: list_teams_with_branch_access
class ReposGetTeamsWithAccessToProtectedBranchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard branch name queries.")
class ReposGetTeamsWithAccessToProtectedBranchRequest(StrictModel):
    """List teams with push access to a protected branch, including child teams. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposGetTeamsWithAccessToProtectedBranchRequestPath

# Operation: grant_team_branch_push_access
class ReposAddTeamAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to restrict. Cannot contain wildcard characters; use the GraphQL API for wildcard branch names.")
class ReposAddTeamAccessRestrictionsRequestBody(StrictModel):
    body: ReposAddTeamAccessRestrictionsBodyV0 | list[str] | None = Field(default=None, description="List of team slugs to grant push access to this branch. Teams can include child teams.", examples=[{'teams': ['justice-league']}])
class ReposAddTeamAccessRestrictionsRequest(StrictModel):
    """Grant specified teams push access to a protected branch. This operation allows you to add team-level access restrictions, including child teams, to control who can push to the branch."""
    path: ReposAddTeamAccessRestrictionsRequestPath
    body: ReposAddTeamAccessRestrictionsRequestBody | None = None

# Operation: replace_branch_protection_team_restrictions
class ReposSetTeamAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to protect. Cannot contain wildcard characters; use GraphQL API for wildcard support.")
class ReposSetTeamAccessRestrictionsRequestBody(StrictModel):
    body: ReposSetTeamAccessRestrictionsBodyV0 | list[str] | None = Field(default=None, description="Array of team slugs to grant push access to the protected branch. Replaces all existing team restrictions.", examples=[{'teams': ['justice-league']}])
class ReposSetTeamAccessRestrictionsRequest(StrictModel):
    """Replace the list of teams with push access to a protected branch. This operation removes all previously granted team access and applies the new team list, including child teams."""
    path: ReposSetTeamAccessRestrictionsRequestPath
    body: ReposSetTeamAccessRestrictionsRequestBody | None = None

# Operation: revoke_team_branch_push_access
class ReposRemoveTeamAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to modify protection restrictions for. Cannot contain wildcard characters.")
class ReposRemoveTeamAccessRestrictionsRequestBody(StrictModel):
    body: ReposRemoveTeamAccessRestrictionsBodyV0 | list[str] | None = Field(default=None, description="List of team slugs to remove push access from the branch.", examples=[{'teams': ['octocats']}])
class ReposRemoveTeamAccessRestrictionsRequest(StrictModel):
    """Revoke a team's ability to push to a protected branch. This removes push access for the specified team and its child teams. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposRemoveTeamAccessRestrictionsRequestPath
    body: ReposRemoveTeamAccessRestrictionsRequestBody | None = None

# Operation: list_branch_protection_users
class ReposGetUsersWithAccessToProtectedBranchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters; use the GraphQL API for wildcard support.")
class ReposGetUsersWithAccessToProtectedBranchRequest(StrictModel):
    """List users with push access to a protected branch. Protected branches are available in public repositories with GitHub Free and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server."""
    path: ReposGetUsersWithAccessToProtectedBranchRequestPath

# Operation: grant_user_push_access
class ReposAddUserAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The name of the branch. Cannot contain wildcard characters.")
class ReposAddUserAccessRestrictionsRequestBody(StrictModel):
    users: list[str] = Field(default=..., description="List of usernames to grant push access. Order is not significant. The combined total of users, apps, and teams cannot exceed 100 items.")
class ReposAddUserAccessRestrictionsRequest(StrictModel):
    """Grant push access to specified users on a protected branch. The total number of users, apps, and teams combined cannot exceed 100 items."""
    path: ReposAddUserAccessRestrictionsRequestPath
    body: ReposAddUserAccessRestrictionsRequestBody

# Operation: revoke_user_branch_access
class ReposRemoveUserAccessRestrictionsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    branch: str = Field(default=..., description="The name of the branch to modify protection restrictions for. Cannot contain wildcard characters.")
class ReposRemoveUserAccessRestrictionsRequestBody(StrictModel):
    users: list[str] = Field(default=..., description="Array of usernames to revoke push access from. The combined total of users, apps, and teams cannot exceed 100 items.")
class ReposRemoveUserAccessRestrictionsRequest(StrictModel):
    """Revoke push access to a protected branch for specified users. This operation removes the ability for one or more users to push commits to the branch."""
    path: ReposRemoveUserAccessRestrictionsRequestPath
    body: ReposRemoveUserAccessRestrictionsRequestBody

# Operation: rename_branch
class ReposRenameBranchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The current name of the branch. Cannot contain wildcard characters.")
class ReposRenameBranchRequestBody(StrictModel):
    new_name: str = Field(default=..., description="The new name for the branch.")
class ReposRenameBranchRequest(StrictModel):
    """Rename a branch in a repository. The authenticated user must have push access to the branch, and admin/owner permissions if renaming the default branch. Note that the rename process may take time to complete in the background."""
    path: ReposRenameBranchRequestPath
    body: ReposRenameBranchRequestBody

# Operation: create_check_run
class ChecksCreateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ChecksCreateRequestBody(StrictModel):
    body: ChecksCreateBodyV0 | ChecksCreateBodyV1 = Field(default=..., description="Check run configuration including the commit SHA, status, conclusion, output details with annotations and images, and optional actions. Supports both in-progress and completed states.", examples=[{'name': 'mighty_readme', 'head_sha': 'ce587453ced02b1526dfb4cb910479d431683101', 'status': 'in_progress', 'external_id': '42', 'started_at': '2018-05-04T01:14:52Z', 'output': {'title': 'Mighty Readme report', 'summary': '', 'text': ''}}, {'name': 'mighty_readme', 'head_sha': 'ce587453ced02b1526dfb4cb910479d431683101', 'status': 'completed', 'started_at': '2017-11-30T19:39:10Z', 'conclusion': 'success', 'completed_at': '2017-11-30T19:49:10Z', 'output': {'title': 'Mighty Readme report', 'summary': 'There are 0 failures, 2 warnings, and 1 notices.', 'text': 'You may have some misspelled words on lines 2 and 4. You also may want to add a section in your README about how to install your app.', 'annotations': [{'path': 'README.md', 'annotation_level': 'warning', 'title': 'Spell Checker', 'message': "Check your spelling for 'banaas'.", 'raw_details': "Do you mean 'bananas' or 'banana'?", 'start_line': 2, 'end_line': 2}, {'path': 'README.md', 'annotation_level': 'warning', 'title': 'Spell Checker', 'message': "Check your spelling for 'aples'", 'raw_details': "Do you mean 'apples' or 'Naples'", 'start_line': 4, 'end_line': 4}], 'images': [{'alt': 'Super bananas', 'image_url': 'http://example.com/images/42'}]}, 'actions': [{'label': 'Fix', 'identifier': 'fix_errors', 'description': 'Allow us to fix these errors for you'}]}])
class ChecksCreateRequest(StrictModel):
    """Creates a new check run for a specific commit in a repository. Requires a GitHub App and enforces a limit of 1000 check runs with the same name per check suite."""
    path: ChecksCreateRequestPath
    body: ChecksCreateRequestBody

# Operation: get_check_run
class ChecksGetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_run_id: int = Field(default=..., description="The unique identifier of the check run to retrieve.")
class ChecksGetRequest(StrictModel):
    """Retrieve a single check run by its unique identifier. Returns detailed information about the check run's status, conclusion, and associated metadata."""
    path: ChecksGetRequestPath

# Operation: update_check_run
class ChecksUpdateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_run_id: int = Field(default=..., description="The unique identifier of the check run to update.")
class ChecksUpdateRequestBody(StrictModel):
    body: ChecksUpdateBodyV0 | ChecksUpdateBodyV1 = Field(default=..., description="The check run update payload containing status, conclusion, output details, and optional annotations. Supports structured output with title, summary, text, and file-level annotations with severity levels.", examples=[{'name': 'mighty_readme', 'started_at': '2018-05-04T01:14:52Z', 'status': 'completed', 'conclusion': 'success', 'completed_at': '2018-05-04T01:14:52Z', 'output': {'title': 'Mighty Readme report', 'summary': 'There are 0 failures, 2 warnings, and 1 notices.', 'text': 'You may have some misspelled words on lines 2 and 4. You also may want to add a section in your README about how to install your app.', 'annotations': [{'path': 'README.md', 'annotation_level': 'warning', 'title': 'Spell Checker', 'message': "Check your spelling for 'banaas'.", 'raw_details': "Do you mean 'bananas' or 'banana'?", 'start_line': 2, 'end_line': 2}, {'path': 'README.md', 'annotation_level': 'warning', 'title': 'Spell Checker', 'message': "Check your spelling for 'aples'", 'raw_details': "Do you mean 'apples' or 'Naples'", 'start_line': 4, 'end_line': 4}], 'images': [{'alt': 'Super bananas', 'image_url': 'http://example.com/images/42'}]}}])
class ChecksUpdateRequest(StrictModel):
    """Update the status, conclusion, and output details of a check run for a specific commit. This allows you to report test results, annotations, and other check metadata back to GitHub."""
    path: ChecksUpdateRequestPath
    body: ChecksUpdateRequestBody

# Operation: list_check_run_annotations
class ChecksListAnnotationsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_run_id: int = Field(default=..., description="The unique identifier of the check run for which to retrieve annotations.")
class ChecksListAnnotationsRequest(StrictModel):
    """Lists all annotations for a specific check run. Requires `repo` scope for private repositories when using OAuth app tokens or personal access tokens (classic)."""
    path: ChecksListAnnotationsRequestPath

# Operation: trigger_check_run_recheck
class ChecksRerequestRunRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_run_id: int = Field(default=..., description="The unique identifier of the check run to recheck.")
class ChecksRerequestRunRequest(StrictModel):
    """Trigger a recheck of an existing check run without requiring new code to be pushed. This action resets the associated check suite status to queued and clears its conclusion, allowing GitHub Apps to decide whether to update the check run via the update endpoint."""
    path: ChecksRerequestRunRequestPath

# Operation: create_check_suite
class ChecksCreateSuiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ChecksCreateSuiteRequestBody(StrictModel):
    head_sha: str = Field(default=..., description="The commit SHA (hash) that identifies the head commit for which to create the check suite.")
class ChecksCreateSuiteRequest(StrictModel):
    """Manually create a check suite for a repository commit. Use this endpoint only when automatic check suite creation has been disabled via repository preferences."""
    path: ChecksCreateSuiteRequestPath
    body: ChecksCreateSuiteRequestBody

# Operation: get_check_suite
class ChecksGetSuiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_suite_id: int = Field(default=..., description="The unique identifier of the check suite to retrieve.")
class ChecksGetSuiteRequest(StrictModel):
    """Retrieve a single check suite by its unique identifier. Returns detailed information about the check suite including its status, conclusion, and associated check runs."""
    path: ChecksGetSuiteRequestPath

# Operation: list_check_runs
class ChecksListForSuiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_suite_id: int = Field(default=..., description="The unique identifier of the check suite to retrieve check runs from.")
class ChecksListForSuiteRequestQuery(StrictModel):
    check_name: str | None = Field(default=None, description="Filter results to return only check runs with the specified name.")
    filter_: Literal["latest", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter check runs by their completion status. Use `latest` to return only the most recent check runs, or `all` to return all check runs.")
class ChecksListForSuiteRequest(StrictModel):
    """Lists all check runs for a specific check suite. Use this to retrieve detailed results of checks that ran as part of a suite."""
    path: ChecksListForSuiteRequestPath
    query: ChecksListForSuiteRequestQuery | None = None

# Operation: rerun_check_suite
class ChecksRerequestSuiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    check_suite_id: int = Field(default=..., description="The unique identifier of the check suite to rerun.")
class ChecksRerequestSuiteRequest(StrictModel):
    """Rerun a check suite without pushing new code to the repository. This triggers the check_suite webhook event with the `rerequested` action, resetting the suite's status to `queued` and clearing its conclusion."""
    path: ChecksRerequestSuiteRequestPath

# Operation: list_code_scanning_alerts_repository
class CodeScanningListAlertsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class CodeScanningListAlertsForRepoRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort the results by.")
    state: Literal["open", "closed", "dismissed", "fixed"] | None = Field(default=None, description="Filter alerts by their current state. Only alerts matching the specified state will be returned.")
    assignees: str | None = Field(default=None, description="Filter alerts by assignees using a comma-separated list of user handles. Use `*` to include alerts with at least one assignee or `none` to include alerts with no assignees.")
class CodeScanningListAlertsForRepoRequest(StrictModel):
    """Lists code scanning alerts for a repository, including details of the most recent instance on the default branch or specified Git reference. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningListAlertsForRepoRequestPath
    query: CodeScanningListAlertsForRepoRequestQuery | None = None

# Operation: get_code_scanning_alert
class CodeScanningGetAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class CodeScanningGetAlertRequest(StrictModel):
    """Retrieve a specific code scanning alert by its number. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningGetAlertRequestPath

# Operation: update_code_scanning_alert
class CodeScanningUpdateAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class CodeScanningUpdateAlertRequestBody(StrictModel):
    state: Literal["open", "dismissed"] | None = Field(default=None, description="The desired state of the code scanning alert. When set to `dismissed`, you must provide a `dismissed_reason`.")
    dismissed_reason: Literal["false positive", "won't fix", "used in tests"] | None = Field(default=None, description="The reason for dismissing the alert. Required when `state` is set to `dismissed`.")
    dismissed_comment: str | None = Field(default=None, description="An optional comment explaining the dismissal decision, up to 280 characters.", max_length=280)
    create_request: bool | None = Field(default=None, description="If `true`, attempt to create an alert dismissal request alongside the status update.")
    assignees: list[str] | None = Field(default=None, description="A list of users to assign to the alert. Provide an empty array to unassign all previous assignees.")
class CodeScanningUpdateAlertRequest(StrictModel):
    """Update the status and metadata of a code scanning alert, including dismissal state, reason, and assignees. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningUpdateAlertRequestPath
    body: CodeScanningUpdateAlertRequestBody | None = None

# Operation: get_autofix_status
class CodeScanningGetAutofixRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class CodeScanningGetAutofixRequest(StrictModel):
    """Retrieve the status and description of an autofix for a code scanning alert. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningGetAutofixRequestPath

# Operation: create_code_scanning_autofix
class CodeScanningCreateAutofixRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class CodeScanningCreateAutofixRequest(StrictModel):
    """Initiates autofix generation for a code scanning alert. Returns 202 Accepted if a new autofix is being created, or 200 OK if one already exists for the alert."""
    path: CodeScanningCreateAutofixRequestPath

# Operation: commit_code_scanning_autofix
class CodeScanningCommitAutofixRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class CodeScanningCommitAutofixRequestBody(StrictModel):
    target_ref: str | None = Field(default=None, description="The Git reference (branch name) where the autofix commit will be created. The branch must already exist.")
    message: str | None = Field(default=None, description="Custom commit message for the autofix. If not provided, a default message will be used.")
class CodeScanningCommitAutofixRequest(StrictModel):
    """Commits an autofix for a code scanning alert to a specified branch. Returns a 201 Created response if the autofix is successfully committed."""
    path: CodeScanningCommitAutofixRequestPath
    body: CodeScanningCommitAutofixRequestBody | None = None

# Operation: list_code_scanning_alert_instances
class CodeScanningListAlertInstancesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class CodeScanningListAlertInstancesRequest(StrictModel):
    """Lists all instances of a specified code scanning alert within a repository. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningListAlertInstancesRequestPath

# Operation: list_code_scanning_analyses
class CodeScanningListRecentAnalysesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class CodeScanningListRecentAnalysesRequestQuery(StrictModel):
    sarif_id: str | None = Field(default=None, description="Filter analyses to those belonging to a specific SARIF upload batch.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for the analyses list.")
class CodeScanningListRecentAnalysesRequest(StrictModel):
    """Retrieve code scanning analyses for a repository, ordered by most recent first. Results are paginated with 30 analyses per page by default."""
    path: CodeScanningListRecentAnalysesRequestPath
    query: CodeScanningListRecentAnalysesRequestQuery | None = None

# Operation: get_code_scanning_analysis
class CodeScanningGetAnalysisRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    analysis_id: int = Field(default=..., description="The unique identifier of the code scanning analysis to retrieve, as returned from the list analyses operation.")
class CodeScanningGetAnalysisRequest(StrictModel):
    """Retrieve a specific code scanning analysis for a repository, including details about the scan results, tool used, and alert counts. Supports SARIF format output for detailed analysis data."""
    path: CodeScanningGetAnalysisRequestPath

# Operation: delete_code_scanning_analysis
class CodeScanningDeleteAnalysisRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    analysis_id: int = Field(default=..., description="The ID of the analysis to delete, as returned from the list code scanning analyses operation.")
class CodeScanningDeleteAnalysisRequestQuery(StrictModel):
    confirm_delete: str | None = Field(default=None, description="Set to `true` to allow deletion of the final analysis in a set. Required when deleting the last analysis to prevent accidental loss of historical alert data.")
class CodeScanningDeleteAnalysisRequest(StrictModel):
    """Delete a code scanning analysis from a repository. Only the most recent analysis in a set (determined by unique ref, tool, and category combinations) can be deleted. Use the returned URLs to delete subsequent analyses in the set or confirm deletion of the final analysis."""
    path: CodeScanningDeleteAnalysisRequestPath
    query: CodeScanningDeleteAnalysisRequestQuery | None = None

# Operation: list_codeql_databases
class CodeScanningListCodeqlDatabasesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class CodeScanningListCodeqlDatabasesRequest(StrictModel):
    """Lists all CodeQL databases available in a repository. Requires `repo` scope for private repositories or `public_repo` scope for public repositories."""
    path: CodeScanningListCodeqlDatabasesRequestPath

# Operation: get_codeql_database
class CodeScanningGetCodeqlDatabaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the .git extension. Case-insensitive.")
    language: str = Field(default=..., description="The programming language for which to retrieve the CodeQL database.")
class CodeScanningGetCodeqlDatabaseRequest(StrictModel):
    """Retrieve a CodeQL database for a specific language in a repository. Returns JSON metadata by default; set Accept header to application/zip to download the binary database file."""
    path: CodeScanningGetCodeqlDatabaseRequestPath

# Operation: delete_codeql_database
class CodeScanningDeleteCodeqlDatabaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    language: str = Field(default=..., description="The programming language of the CodeQL database to delete.")
class CodeScanningDeleteCodeqlDatabaseRequest(StrictModel):
    """Delete a CodeQL database for a specific language from a repository. Requires `repo` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningDeleteCodeqlDatabaseRequestPath

# Operation: create_variant_analysis
class CodeScanningCreateVariantAnalysisRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class CodeScanningCreateVariantAnalysisRequestBody(StrictModel):
    language: Literal["actions", "cpp", "csharp", "go", "java", "javascript", "python", "ruby", "rust", "swift"] = Field(default=..., description="The programming language targeted by the CodeQL query.")
    query_pack: str = Field(default=..., description="A Base64-encoded tarball containing a CodeQL query and all its dependencies.")
class CodeScanningCreateVariantAnalysisRequest(StrictModel):
    """Create a new CodeQL variant analysis to run a CodeQL query against one or more repositories. The analysis will execute within the specified controller repository using GitHub Actions workflows and store results there."""
    path: CodeScanningCreateVariantAnalysisRequestPath
    body: CodeScanningCreateVariantAnalysisRequestBody

# Operation: get_variant_analysis
class CodeScanningGetVariantAnalysisRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    codeql_variant_analysis_id: int = Field(default=..., description="The unique identifier of the CodeQL variant analysis to retrieve.")
class CodeScanningGetVariantAnalysisRequest(StrictModel):
    """Retrieve the summary of a CodeQL variant analysis by its unique identifier. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningGetVariantAnalysisRequestPath

# Operation: get_variant_analysis_repository_status
class CodeScanningGetVariantAnalysisRepoTaskRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the controller repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the controller repository.")
    codeql_variant_analysis_id: int = Field(default=..., description="The unique identifier of the CodeQL variant analysis.")
    repo_owner: str = Field(default=..., description="The account owner of the repository being analyzed in the variant analysis. Case-insensitive.")
    repo_name: str = Field(default=..., description="The name of the repository being analyzed in the variant analysis.")
class CodeScanningGetVariantAnalysisRepoTaskRequest(StrictModel):
    """Retrieve the analysis status and results of a specific repository within a CodeQL variant analysis. Requires `security_events` scope for private/public repositories or `public_repo` scope for public repositories only."""
    path: CodeScanningGetVariantAnalysisRepoTaskRequestPath

# Operation: get_code_scanning_default_setup
class CodeScanningGetDefaultSetupRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class CodeScanningGetDefaultSetupRequest(StrictModel):
    """Retrieves the default setup configuration for code scanning in a repository. Requires `repo` scope for private repositories or `public_repo` scope for public repositories."""
    path: CodeScanningGetDefaultSetupRequestPath

# Operation: upload_sarif
class CodeScanningUploadSarifRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository.")
    repo: str = Field(default=..., description="The name of the repository (without the .git extension).")
class CodeScanningUploadSarifRequestBody(StrictModel):
    commit_sha: str = Field(default=..., description="The 40-character SHA hash of the commit associated with this analysis.", min_length=40, max_length=40, pattern='^[0-9a-fA-F]+$')
    ref: str = Field(default=..., description="The full Git reference where results will be associated. Use refs/heads/<branch> for branches, refs/tags/<tag> for tags, or refs/pull/<number>/merge or refs/pull/<number>/head for pull requests.", pattern='^refs/(heads|tags|pull)/.*$')
    sarif: str = Field(default=..., description="The SARIF file compressed with gzip and encoded as Base64. Compress your SARIF file first, then encode the binary output to Base64 format.")
    checkout_uri: str | None = Field(default=None, description="The base directory used during analysis (as it appears in the SARIF file). Used to convert absolute file paths to repository-relative paths for accurate alert mapping.", json_schema_extra={'format': 'uri'})
    validate_: bool | None = Field(default=None, validation_alias="validate", serialization_alias="validate", description="Whether to validate the SARIF file against code scanning specifications. Useful for integrators to verify correct rendering before production use.")
class CodeScanningUploadSarifRequest(StrictModel):
    """Upload SARIF-formatted code scanning analysis results to a repository. Results can be mapped to pull requests for check annotations or to branches for the Security tab, with automatic prioritization when data exceeds platform limits."""
    path: CodeScanningUploadSarifRequestPath
    body: CodeScanningUploadSarifRequestBody

# Operation: get_sarif_upload
class CodeScanningGetSarifRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    sarif_id: str = Field(default=..., description="The unique identifier of the SARIF upload, obtained when the SARIF file was initially uploaded.")
class CodeScanningGetSarifRequest(StrictModel):
    """Retrieve details about a SARIF upload including its processing status and the URL to access the uploaded analysis results. Use this to check the status of a code scanning analysis that was previously uploaded."""
    path: CodeScanningGetSarifRequestPath

# Operation: get_repository_code_security_configuration
class CodeSecurityGetConfigurationForRepositoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class CodeSecurityGetConfigurationForRepositoryRequest(StrictModel):
    """Retrieve the code security configuration that manages a repository's security settings. The authenticated user must be an administrator or security manager for the organization."""
    path: CodeSecurityGetConfigurationForRepositoryRequestPath

# Operation: list_codeowners_errors
class ReposCodeownersErrorsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposCodeownersErrorsRequest(StrictModel):
    """List any syntax errors detected in the repository's CODEOWNERS file. Use this to validate CODEOWNERS syntax and identify issues that need correction."""
    path: ReposCodeownersErrorsRequestPath

# Operation: list_codespaces_in_repository
class CodespacesListInRepositoryForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class CodespacesListInRepositoryForAuthenticatedUserRequest(StrictModel):
    """Lists all codespaces associated with a specified repository for the authenticated user. Requires the `codespace` scope for OAuth app tokens and personal access tokens (classic)."""
    path: CodespacesListInRepositoryForAuthenticatedUserRequestPath

# Operation: create_codespace
class CodespacesCreateWithRepoForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class CodespacesCreateWithRepoForAuthenticatedUserRequestBody(StrictModel):
    geo: Literal["EuropeWest", "SoutheastAsia", "UsEast", "UsWest"] | None = Field(default=None, description="The geographic region where the codespace will be hosted. If not specified, the region is determined by the user's IP address.")
    machine: str | None = Field(default=None, description="The machine type to use for this codespace, determining compute resources and performance characteristics.")
    devcontainer_path: str | None = Field(default=None, description="Path to the devcontainer.json configuration file within the repository to use for this codespace.")
    multi_repo_permissions_opt_out: bool | None = Field(default=None, description="Whether to opt out of authorizing permissions requested in the devcontainer.json configuration.")
    working_directory: str | None = Field(default=None, description="The default working directory to open when the codespace starts.")
    idle_timeout_minutes: int | None = Field(default=None, description="Time in minutes before the codespace automatically stops due to inactivity.")
    display_name: str | None = Field(default=None, description="A human-readable display name for this codespace.")
    retention_period_minutes: int | None = Field(default=None, description="Duration in minutes after the codespace becomes idle before it is automatically deleted. Must be between 0 and 43200 minutes (30 days).")
class CodespacesCreateWithRepoForAuthenticatedUserRequest(StrictModel):
    """Create a new codespace in a repository for the authenticated user. Requires the `codespace` OAuth scope or personal access token (classic) scope."""
    path: CodespacesCreateWithRepoForAuthenticatedUserRequestPath
    body: CodespacesCreateWithRepoForAuthenticatedUserRequestBody | None = None

# Operation: list_devcontainers
class CodespacesListDevcontainersInRepositoryForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the .git extension. The name is case-insensitive.")
class CodespacesListDevcontainersInRepositoryForAuthenticatedUserRequest(StrictModel):
    """Lists all devcontainer.json configuration files in a repository that are accessible to the authenticated user. These configurations define the development environment setup for codespaces created from this repository."""
    path: CodespacesListDevcontainersInRepositoryForAuthenticatedUserRequestPath

# Operation: list_codespace_machines
class CodespacesRepoMachinesForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class CodespacesRepoMachinesForAuthenticatedUserRequest(StrictModel):
    """List the machine types available for a repository based on its configuration. Use this to determine which machine specifications can be used when creating or updating a codespace for the repository."""
    path: CodespacesRepoMachinesForAuthenticatedUserRequestPath

# Operation: get_codespace_defaults
class CodespacesPreFlightWithRepoForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class CodespacesPreFlightWithRepoForAuthenticatedUserRequest(StrictModel):
    """Retrieve the default configuration attributes for creating a new codespace in a repository. This includes machine types, regions, and other preset values based on the repository's codespace settings."""
    path: CodespacesPreFlightWithRepoForAuthenticatedUserRequestPath

# Operation: list_codespace_secrets
class CodespacesListRepoSecretsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class CodespacesListRepoSecretsRequest(StrictModel):
    """Lists all development environment secrets available in a repository without revealing their encrypted values. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: CodespacesListRepoSecretsRequestPath

# Operation: get_codespace_public_key
class CodespacesGetRepoPublicKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class CodespacesGetRepoPublicKeyRequest(StrictModel):
    """Retrieve the public key for a repository, which is required to encrypt secrets before creating or updating them in Codespaces. For private repositories, the request requires the `repo` scope."""
    path: CodespacesGetRepoPublicKeyRequestPath

# Operation: get_codespace_secret
class CodespacesGetRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class CodespacesGetRepoSecretRequest(StrictModel):
    """Retrieve a repository development environment secret without revealing its encrypted value. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: CodespacesGetRepoSecretRequestPath

# Operation: create_or_update_codespace_secret_repository
class CodespacesCreateOrUpdateRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to create or update.")
class CodespacesCreateOrUpdateRepoSecretRequestBody(StrictModel):
    encrypted_value: str | None = Field(default=None, description="The encrypted value for the secret. Must be encrypted using LibSodium with the public key retrieved from the Get repository public key endpoint. The encrypted value must be base64-encoded.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
    key_id: str | None = Field(default=None, description="The ID of the public key used to encrypt the secret. Retrieve this from the Get repository public key endpoint.")
class CodespacesCreateOrUpdateRepoSecretRequest(StrictModel):
    """Create or update an encrypted repository secret for GitHub Codespaces. The secret value must be encrypted using LibSodium with the repository's public key before submission."""
    path: CodespacesCreateOrUpdateRepoSecretRequestPath
    body: CodespacesCreateOrUpdateRepoSecretRequestBody | None = None

# Operation: delete_codespace_secret
class CodespacesDeleteRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to delete.")
class CodespacesDeleteRepoSecretRequest(StrictModel):
    """Delete a development environment secret from a repository. Requires repository admin access and the `repo` OAuth scope."""
    path: CodespacesDeleteRepoSecretRequestPath

# Operation: list_collaborators
class ReposListCollaboratorsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListCollaboratorsRequestQuery(StrictModel):
    affiliation: Literal["outside", "direct", "all"] | None = Field(default=None, description="Filter collaborators by their affiliation type. Use 'outside' for external collaborators only, 'direct' for all collaborators regardless of organization membership, or 'all' to include all visible collaborators.")
    permission: Literal["pull", "triage", "push", "maintain", "admin"] | None = Field(default=None, description="Filter collaborators by the permissions they have on the repository. If not specified, all collaborators are returned regardless of permission level.")
class ReposListCollaboratorsRequest(StrictModel):
    """List all collaborators on a repository, including outside collaborators, organization members, and team members. The authenticated user must have write, maintain, or admin privileges to use this endpoint."""
    path: ReposListCollaboratorsRequestPath
    query: ReposListCollaboratorsRequestQuery | None = None

# Operation: verify_repository_collaborator
class ReposCheckCollaboratorRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    username: str = Field(default=..., description="The GitHub username to check for collaborator access. The name is not case sensitive.")
class ReposCheckCollaboratorRequest(StrictModel):
    """Verify whether a user has collaborator access to a repository. For organization-owned repositories, this includes outside collaborators, direct organization members, members with team-based access, and owners."""
    path: ReposCheckCollaboratorRequestPath

# Operation: add_collaborator
class ReposAddCollaboratorRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    username: str = Field(default=..., description="The GitHub user account handle to add as a collaborator.")
class ReposAddCollaboratorRequestBody(StrictModel):
    permission: str | None = Field(default=None, description="The permission level to grant the collaborator. Valid values are `pull`, `triage`, `push`, `maintain`, `admin`, or a custom repository role name if defined by the organization. Only applicable to organization-owned repositories.")
class ReposAddCollaboratorRequest(StrictModel):
    """Add a user to a repository with a specified permission level. The user will receive an invitation notification that they must accept or decline, unless they are an Enterprise Managed User who will be automatically added."""
    path: ReposAddCollaboratorRequestPath
    body: ReposAddCollaboratorRequestBody | None = None

# Operation: remove_collaborator
class ReposRemoveCollaboratorRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    username: str = Field(default=..., description="The GitHub user account handle to remove as a collaborator.")
class ReposRemoveCollaboratorRequest(StrictModel):
    """Remove a collaborator from a repository. The authenticated user must be a repository administrator or the target user being removed. This action cancels pending invitations, unassigns the user from issues, removes project access, and has cascading effects on forks."""
    path: ReposRemoveCollaboratorRequestPath

# Operation: get_collaborator_permission
class ReposGetCollaboratorPermissionLevelRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    username: str = Field(default=..., description="The GitHub username handle for the collaborator whose permissions you want to check.")
class ReposGetCollaboratorPermissionLevelRequest(StrictModel):
    """Retrieve the repository permission level and role assigned to a collaborator. Returns the highest permission across all sources (repository, team, organization, and enterprise grants)."""
    path: ReposGetCollaboratorPermissionLevelRequestPath

# Operation: list_commit_comments
class ReposListCommitCommentsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListCommitCommentsForRepoRequest(StrictModel):
    """Retrieve all commit comments for a repository, ordered by ascending ID. Supports multiple content formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: ReposListCommitCommentsForRepoRequestPath

# Operation: get_commit_comment
class ReposGetCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the commit comment.", json_schema_extra={'format': 'int64'})
class ReposGetCommitCommentRequest(StrictModel):
    """Retrieve a specific commit comment by its ID. Supports multiple response formats including raw markdown, plain text, HTML, or a combination of all three representations."""
    path: ReposGetCommitCommentRequestPath

# Operation: update_commit_comment
class ReposUpdateCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the commit comment to update.", json_schema_extra={'format': 'int64'})
class ReposUpdateCommitCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The new contents of the comment. Supports markdown formatting.")
class ReposUpdateCommitCommentRequest(StrictModel):
    """Update the contents of a commit comment. Supports multiple response formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: ReposUpdateCommitCommentRequestPath
    body: ReposUpdateCommitCommentRequestBody

# Operation: delete_commit_comment
class ReposDeleteCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the commit comment to delete.", json_schema_extra={'format': 'int64'})
class ReposDeleteCommitCommentRequest(StrictModel):
    """Delete a commit comment from a repository. This permanently removes the specified comment from a commit."""
    path: ReposDeleteCommitCommentRequestPath

# Operation: list_commit_comment_reactions
class ReactionsListForCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the commit comment.", json_schema_extra={'format': 'int64'})
class ReactionsListForCommitCommentRequestQuery(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] | None = Field(default=None, description="Filter results to a single reaction type. Omit this parameter to list all reactions to the commit comment.")
class ReactionsListForCommitCommentRequest(StrictModel):
    """List all reactions or filter by a specific reaction type for a commit comment. Reactions allow users to express sentiment on commit comments using emoji."""
    path: ReactionsListForCommitCommentRequestPath
    query: ReactionsListForCommitCommentRequestQuery | None = None

# Operation: add_commit_comment_reaction
class ReactionsCreateForCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the commit comment to react to.", json_schema_extra={'format': 'int64'})
class ReactionsCreateForCommitCommentRequestBody(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] = Field(default=..., description="The emoji reaction type to add to the commit comment.")
class ReactionsCreateForCommitCommentRequest(StrictModel):
    """Add an emoji reaction to a commit comment. Returns HTTP 200 if the reaction type was already added by the authenticated user."""
    path: ReactionsCreateForCommitCommentRequestPath
    body: ReactionsCreateForCommitCommentRequestBody

# Operation: remove_commit_comment_reaction
class ReactionsDeleteForCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. This is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository, without the `.git` extension. This is case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the commit comment from which to remove the reaction.", json_schema_extra={'format': 'int64'})
    reaction_id: int = Field(default=..., description="The unique identifier of the reaction to remove.")
class ReactionsDeleteForCommitCommentRequest(StrictModel):
    """Remove a reaction from a commit comment. This operation deletes a specific reaction that was previously added to a commit comment."""
    path: ReactionsDeleteForCommitCommentRequestPath

# Operation: list_commits
class ReposListCommitsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposListCommitsRequestQuery(StrictModel):
    sha: str | None = Field(default=None, description="SHA or branch name to start listing commits from. Defaults to the repository's default branch if not specified.")
    author: str | None = Field(default=None, description="Filter commits by the GitHub username or email address of the commit author.")
    committer: str | None = Field(default=None, description="Filter commits by the GitHub username or email address of the commit committer.")
    since: str | None = Field(default=None, description="Only return commits that were last updated after this timestamp. Must be between 1970-01-01 and 2099-12-31.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="Only return commits before this timestamp. Must be between 1970-01-01 and 2099-12-31.", json_schema_extra={'format': 'date-time'})
class ReposListCommitsRequest(StrictModel):
    """Retrieve a list of commits from a repository, with optional filtering by author, committer, or date range. The response includes signature verification details for each commit."""
    path: ReposListCommitsRequestPath
    query: ReposListCommitsRequestQuery | None = None

# Operation: list_branches_for_commit
class ReposListBranchesForHeadCommitRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    commit_sha: str = Field(default=..., description="The SHA (commit hash) to find as the HEAD of branches.")
class ReposListBranchesForHeadCommitRequest(StrictModel):
    """List all branches where the given commit SHA is the HEAD (latest commit). Available for public repositories with GitHub Free and in public/private repositories with GitHub Pro or higher plans."""
    path: ReposListBranchesForHeadCommitRequestPath

# Operation: list_commit_comments_by_sha
class ReposListCommentsForCommitRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    commit_sha: str = Field(default=..., description="The commit SHA identifier for which to retrieve comments.")
class ReposListCommentsForCommitRequest(StrictModel):
    """Retrieve all comments for a specific commit in a repository. Supports multiple content formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: ReposListCommentsForCommitRequestPath

# Operation: create_commit_comment
class ReposCreateCommitCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    commit_sha: str = Field(default=..., description="The commit SHA identifier to comment on.")
class ReposCreateCommitCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The comment text content. Supports markdown formatting.")
    position: int | None = Field(default=None, description="Optional line index in the diff to attach the comment to. If omitted, the comment is added to the general commit discussion.")
class ReposCreateCommitCommentRequest(StrictModel):
    """Add a comment to a specific commit in a repository. This endpoint triggers notifications and is subject to secondary rate limiting when used rapidly."""
    path: ReposCreateCommitCommentRequestPath
    body: ReposCreateCommitCommentRequestBody

# Operation: list_pull_requests_for_commit
class ReposListPullRequestsAssociatedWithCommitRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    commit_sha: str = Field(default=..., description="The SHA of the commit, or alternatively a branch name to list pull requests associated with that branch.")
class ReposListPullRequestsAssociatedWithCommitRequest(StrictModel):
    """List pull requests associated with a commit. Returns the merged pull request that introduced the commit to the default branch, or both merged and open pull requests if the commit is not in the default branch. You can also use a branch name as the commit_sha parameter to list pull requests associated with that branch."""
    path: ReposListPullRequestsAssociatedWithCommitRequestPath

# Operation: get_commit
class ReposGetCommitRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ref: str = Field(default=..., description="The commit reference to retrieve. Can be a commit SHA, branch name (prefixed with `heads/`), or tag name (prefixed with `tags/`). Refer to Git References documentation for valid reference formats.")
class ReposGetCommitRequest(StrictModel):
    """Retrieve detailed information about a specific commit, including file changes, diff, or patch data. Requires read access to the repository."""
    path: ReposGetCommitRequestPath

# Operation: list_check_runs_for_ref
class ChecksListForRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    ref: str = Field(default=..., description="The commit reference to query. Can be a commit SHA, branch name (format: `heads/BRANCH_NAME`), or tag name (format: `tags/TAG_NAME`).")
class ChecksListForRefRequestQuery(StrictModel):
    check_name: str | None = Field(default=None, description="Filters results to return only check runs with the specified name.")
    filter_: Literal["latest", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters check runs by completion status. Use `latest` for the most recent check runs or `all` to include all check runs.")
class ChecksListForRefRequest(StrictModel):
    """Lists check runs for a commit reference (SHA, branch, or tag). The endpoint returns up to 1000 most recent check runs; use check suite endpoints for comprehensive iteration."""
    path: ChecksListForRefRequestPath
    query: ChecksListForRefRequestQuery | None = None

# Operation: list_check_suites
class ChecksListSuitesForRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ref: str = Field(default=..., description="The commit reference to list check suites for. Can be a commit SHA, branch name (prefixed with `heads/`), or tag name (prefixed with `tags/`).")
class ChecksListSuitesForRefRequestQuery(StrictModel):
    check_name: str | None = Field(default=None, description="Filters results to return only check suites with the specified name.")
class ChecksListSuitesForRefRequest(StrictModel):
    """Lists all check suites for a commit reference (SHA, branch, or tag). The ref can be a commit SHA, branch name with `heads/` prefix, or tag name with `tags/` prefix."""
    path: ChecksListSuitesForRefRequestPath
    query: ChecksListSuitesForRefRequestQuery | None = None

# Operation: get_commit_status
class ReposGetCombinedStatusForRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    ref: str = Field(default=..., description="The commit reference to check status for. Can be a commit SHA, branch name (prefixed with `heads/`), or tag name (prefixed with `tags/`).")
class ReposGetCombinedStatusForRefRequest(StrictModel):
    """Retrieve the combined status for a commit reference. Users with pull access can view an aggregated status across all contexts for a given SHA, branch, or tag, with an overall state indicating success, pending, or failure."""
    path: ReposGetCombinedStatusForRefRequestPath

# Operation: list_commit_statuses
class ReposListCommitStatusesForRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    ref: str = Field(default=..., description="The commit reference to query statuses for. Can be a commit SHA, branch name (prefixed with `heads/`), or tag name (prefixed with `tags/`).")
class ReposListCommitStatusesForRefRequest(StrictModel):
    """Retrieve commit statuses for a given reference in reverse chronological order, with the latest status appearing first. Requires pull access to the repository."""
    path: ReposListCommitStatusesForRefRequestPath

# Operation: get_repository_community_profile
class ReposGetCommunityProfileMetricsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetCommunityProfileMetricsRequest(StrictModel):
    """Retrieve community health metrics for a repository, including health score, documentation presence, code of conduct, license, and standard community files. The repository cannot be a fork."""
    path: ReposGetCommunityProfileMetricsRequestPath

# Operation: compare_commits
class ReposCompareCommitsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    basehead: str = Field(default=..., description="The base and head references to compare, specified as `BASE...HEAD` where both are branch names in the repository. To compare across repositories in the same network, use the format `USERNAME:BASE...USERNAME:HEAD`.")
class ReposCompareCommitsRequest(StrictModel):
    """Compare two commits to identify differences between them. Supports comparing branches, tags, and commit SHAs within the same repository or across repositories in the same network, returning a chronologically ordered list of commits and changed files."""
    path: ReposCompareCommitsRequestPath

# Operation: get_repository_content
class ReposGetContentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    path: str = Field(default=..., description="The file or directory path within the repository. Omit to retrieve the root directory contents.")
class ReposGetContentRequest(StrictModel):
    """Retrieve the contents of a file or directory in a repository. Supports multiple response formats including raw file content, HTML rendering, and structured object format. Directories return up to 1,000 items; use the Git Trees API for larger directories."""
    path: ReposGetContentRequestPath

# Operation: create_or_update_file
class ReposCreateOrUpdateFileContentsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    path: str = Field(default=..., description="The file path within the repository where the file will be created or updated.")
class ReposCreateOrUpdateFileContentsRequestBodyCommitter(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the committer. Required; omitting will result in a 422 error.")
    email: str = Field(default=..., validation_alias="email", serialization_alias="email", description="The email address of the committer. Required; omitting will result in a 422 error.")
class ReposCreateOrUpdateFileContentsRequestBodyAuthor(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the author. Required; omitting will result in a 422 error.")
    email: str = Field(default=..., validation_alias="email", serialization_alias="email", description="The email address of the author. Required; omitting will result in a 422 error.")
class ReposCreateOrUpdateFileContentsRequestBody(StrictModel):
    message: str = Field(default=..., description="The commit message describing the change.")
    content: str = Field(default=..., description="The new file content encoded in Base64 format.")
    sha: str | None = Field(default=None, description="The blob SHA of the file being replaced. Required when updating an existing file; omit when creating a new file.")
    branch: str | None = Field(default=None, description="The branch name where the file will be created or updated. Defaults to the repository's default branch if not specified.")
    committer: ReposCreateOrUpdateFileContentsRequestBodyCommitter
    author: ReposCreateOrUpdateFileContentsRequestBodyAuthor
class ReposCreateOrUpdateFileContentsRequest(StrictModel):
    """Create a new file or update an existing file in a repository. Note: Do not use this endpoint in parallel with the delete file endpoint, as concurrent requests will conflict."""
    path: ReposCreateOrUpdateFileContentsRequestPath
    body: ReposCreateOrUpdateFileContentsRequestBody

# Operation: delete_file
class ReposDeleteFileRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    path: str = Field(default=..., description="The file path within the repository to delete.")
class ReposDeleteFileRequestBodyCommitter(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the committer. Required if committer information is provided; must be paired with committer email.")
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The email address of the committer. Required if committer information is provided; must be paired with committer name.")
class ReposDeleteFileRequestBody(StrictModel):
    message: str = Field(default=..., description="The commit message describing the deletion.")
    sha: str = Field(default=..., description="The blob SHA of the file being deleted. Used to prevent concurrent modification conflicts.")
    branch: str | None = Field(default=None, description="The branch name where the file will be deleted. If not specified, defaults to the repository's default branch.")
    committer: ReposDeleteFileRequestBodyCommitter | None = None
class ReposDeleteFileRequest(StrictModel):
    """Delete a file from a repository by providing the file path and commit SHA. The authenticated user or specified committer information will be used for the commit."""
    path: ReposDeleteFileRequestPath
    body: ReposDeleteFileRequestBody

# Operation: list_contributors
class ReposListContributorsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListContributorsRequestQuery(StrictModel):
    anon: str | None = Field(default=None, description="Include anonymous contributors (those without associated GitHub user accounts) in the results.")
class ReposListContributorsRequest(StrictModel):
    """Retrieves a list of contributors to a repository, sorted by commit count in descending order. Contributor data may be cached and up to a few hours old, and only the first 500 email addresses are linked to GitHub user accounts."""
    path: ReposListContributorsRequestPath
    query: ReposListContributorsRequestQuery | None = None

# Operation: list_dependabot_alerts_repository
class DependabotListAlertsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class DependabotListAlertsForRepoRequestQuery(StrictModel):
    state: str | None = Field(default=None, description="Filter alerts by one or more states. Specify as comma-separated values to return only alerts matching these states.")
    ecosystem: str | None = Field(default=None, description="Filter alerts by one or more package ecosystems. Specify as comma-separated values to return only alerts for these ecosystems.")
    package: str | None = Field(default=None, description="Filter alerts by one or more package names. Specify as comma-separated values to return only alerts for these packages.")
    manifest: str | None = Field(default=None, description="Filter alerts by one or more manifest file paths. Specify as comma-separated values to return only alerts for these manifests.")
    epss_percentage: str | None = Field(default=None, description="Filter alerts by CVE Exploit Prediction Scoring System (EPSS) percentage. Supports exact values, comparison operators (>, <, >=, <=), or ranges (e.g., 0.5..0.9) with values from 0.0 to 1.0.")
    has: str | list[Literal["patch"]] | None = Field(default=None, description="Filter alerts based on specific attributes. Multiple filters can be combined to match alerts with all specified attributes. Currently supports `patch` to filter for alerts with available patches.")
    scope: Literal["development", "runtime"] | None = Field(default=None, description="Filter alerts by dependency scope within the project.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order.")
class DependabotListAlertsForRepoRequest(StrictModel):
    """Retrieve Dependabot security alerts for a repository with optional filtering by state, ecosystem, package, and vulnerability metrics. Requires `security_events` scope or `public_repo` scope for public repositories."""
    path: DependabotListAlertsForRepoRequestPath
    query: DependabotListAlertsForRepoRequestQuery | None = None

# Operation: get_dependabot_alert
class DependabotGetAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies a Dependabot alert in its repository.\nYou can find this at the end of the URL for a Dependabot alert within GitHub,\nor in `number` fields in the response from the\n`GET /repos/{owner}/{repo}/dependabot/alerts` operation.")
class DependabotGetAlertRequest(StrictModel):
    """Retrieve a specific Dependabot security alert for a repository. Requires `security_events` scope for OAuth apps and personal access tokens, or `public_repo` scope for public repositories only."""
    path: DependabotGetAlertRequestPath

# Operation: update_dependabot_alert
class DependabotUpdateAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies a Dependabot alert in its repository.\nYou can find this at the end of the URL for a Dependabot alert within GitHub,\nor in `number` fields in the response from the\n`GET /repos/{owner}/{repo}/dependabot/alerts` operation.")
class DependabotUpdateAlertRequestBody(StrictModel):
    state: Literal["dismissed", "open"] | None = Field(default=None, description="The state of the Dependabot alert. When setting to `dismissed`, a `dismissed_reason` must be provided.")
    dismissed_reason: Literal["fix_started", "inaccurate", "no_bandwidth", "not_used", "tolerable_risk"] | None = Field(default=None, description="A reason for dismissing the alert. Required when `state` is set to `dismissed`.")
    dismissed_comment: str | None = Field(default=None, description="An optional comment associated with dismissing the alert. Maximum 280 characters.", max_length=280)
    assignees: list[str] | None = Field(default=None, description="GitHub usernames to assign to this alert. Pass one or more logins to replace the current assignees, or an empty array to clear all assignees.")
class DependabotUpdateAlertRequest(StrictModel):
    """Update the state, dismissal reason, and assignees of a Dependabot security alert. The authenticated user must have access to security alerts for the repository."""
    path: DependabotUpdateAlertRequestPath
    body: DependabotUpdateAlertRequestBody | None = None

# Operation: list_dependabot_secrets
class DependabotListRepoSecretsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class DependabotListRepoSecretsRequest(StrictModel):
    """Lists all Dependabot secrets configured for a repository without revealing their encrypted values. Requires `repo` scope for OAuth apps and personal access tokens (classic)."""
    path: DependabotListRepoSecretsRequestPath

# Operation: get_dependabot_public_key
class DependabotGetRepoPublicKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class DependabotGetRepoPublicKeyRequest(StrictModel):
    """Retrieves the public key for a repository, which is required to encrypt secrets before creating or updating Dependabot secrets. This endpoint is accessible to anyone with read access to the repository."""
    path: DependabotGetRepoPublicKeyRequestPath

# Operation: get_dependabot_secret
class DependabotGetRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the Dependabot secret to retrieve.")
class DependabotGetRepoSecretRequest(StrictModel):
    """Retrieve a single Dependabot repository secret without revealing its encrypted value. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: DependabotGetRepoSecretRequestPath

# Operation: create_or_update_dependabot_secret
class DependabotCreateOrUpdateRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    secret_name: str = Field(default=..., description="The name of the secret to create or update.")
class DependabotCreateOrUpdateRepoSecretRequestBody(StrictModel):
    key_id: str | None = Field(default=None, description="The ID of the public key used to encrypt the secret. If not provided, the default key for the repository will be used.")
    encrypted_value: str | None = Field(default=None, description="Value for your secret, encrypted with [LibSodium](https://libsodium.gitbook.io/doc/bindings_for_other_languages) using the public key retrieved from the [Get a repository public key](https://docs.github.com/rest/dependabot/secrets#get-a-repository-public-key) endpoint.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
class DependabotCreateOrUpdateRepoSecretRequest(StrictModel):
    """Create or update a repository secret for Dependabot with an encrypted value. The secret must be encrypted using LibSodium before submission."""
    path: DependabotCreateOrUpdateRepoSecretRequestPath
    body: DependabotCreateOrUpdateRepoSecretRequestBody | None = None

# Operation: delete_dependabot_secret
class DependabotDeleteRepoSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    secret_name: str = Field(default=..., description="The name of the Dependabot secret to delete.")
class DependabotDeleteRepoSecretRequest(StrictModel):
    """Delete a Dependabot secret from a repository by its name. Requires `repo` scope authentication."""
    path: DependabotDeleteRepoSecretRequestPath

# Operation: compare_dependency_changes
class DependencyGraphDiffRangeRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    basehead: str = Field(default=..., description="The base and head Git revisions to compare, specified in the format `{base}...{head}`. Git revisions are resolved to commit SHAs, and named revisions (like branch names) are resolved to their corresponding HEAD commits with an appropriate merge base determined automatically.")
class DependencyGraphDiffRangeRequest(StrictModel):
    """Retrieve a detailed diff of dependency changes between two commits by analyzing modifications to dependency manifests. This helps identify what dependencies were added, removed, or updated between specified Git revisions."""
    path: DependencyGraphDiffRangeRequestPath

# Operation: export_sbom
class DependencyGraphExportSbomRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class DependencyGraphExportSbomRequest(StrictModel):
    """Export the software bill of materials (SBOM) for a repository in SPDX JSON format. This provides a comprehensive inventory of all dependencies and components used in the project."""
    path: DependencyGraphExportSbomRequestPath

# Operation: submit_dependency_snapshot
class DependencyGraphCreateRepositorySnapshotRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class DependencyGraphCreateRepositorySnapshotRequestBodyDetector(StrictModel):
    version: str = Field(default=..., validation_alias="version", serialization_alias="version", description="The version of the dependency detector tool that generated this snapshot.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the dependency detector tool used to generate this snapshot.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The URL or documentation link for the detector tool used.")
class DependencyGraphCreateRepositorySnapshotRequestBodyJob(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="A unique external identifier for this detection job run.")
    correlator: str = Field(default=..., validation_alias="correlator", serialization_alias="correlator", description="A key that groups snapshots submitted over time for the same detector and workflow. Only the latest snapshot for each correlator-detector combination is used for dependency calculation. Should uniquely identify a detection run wave, such as combining workflow name and job name in CI/CD systems.")
class DependencyGraphCreateRepositorySnapshotRequestBody(StrictModel):
    version: int = Field(default=..., description="The version number of the snapshot submission format being used.")
    sha: str = Field(default=..., description="The commit SHA associated with this dependency snapshot.", min_length=40, max_length=40)
    ref: str = Field(default=..., description="The repository branch reference that triggered this snapshot. Must be a full ref path.", pattern='^refs/')
    metadata: dict[str, str | float | bool] | None = Field(default=None, description="Optional user-defined metadata for storing domain-specific information. Limited to 8 keys with scalar values.", max_length=8)
    manifests: dict[str, Manifest] | None = Field(default=None, description="Optional collection of package manifests representing detected dependencies, organized by logical groups or declaration files.")
    scanned: str = Field(default=..., description="The timestamp when the dependency snapshot was scanned.", json_schema_extra={'format': 'date-time'})
    detector: DependencyGraphCreateRepositorySnapshotRequestBodyDetector
    job: DependencyGraphCreateRepositorySnapshotRequestBodyJob
class DependencyGraphCreateRepositorySnapshotRequest(StrictModel):
    """Submit a snapshot of a repository's dependencies for a specific commit. This enables dependency tracking and vulnerability analysis by recording the detected dependencies at a point in time."""
    path: DependencyGraphCreateRepositorySnapshotRequestPath
    body: DependencyGraphCreateRepositorySnapshotRequestBody

# Operation: list_deployments
class ReposListDeploymentsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposListDeploymentsRequestQuery(StrictModel):
    sha: str | None = Field(default=None, description="Filter deployments by the commit SHA recorded at creation time.")
    task: str | None = Field(default=None, description="Filter deployments by task name (e.g., `deploy` or `deploy:migrations`).")
    environment: str | None = Field(default=None, description="Filter deployments by the target environment name (e.g., `staging` or `production`).")
class ReposListDeploymentsRequest(StrictModel):
    """Retrieve a list of deployments for a repository with optional filtering by commit SHA, task name, or target environment."""
    path: ReposListDeploymentsRequestPath
    query: ReposListDeploymentsRequestQuery | None = None

# Operation: create_deployment
class ReposCreateDeploymentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository.")
    repo: str = Field(default=..., description="The name of the repository (without the .git extension).")
class ReposCreateDeploymentRequestBody(StrictModel):
    ref: str = Field(default=..., description="The ref to deploy, which can be a branch name, tag, or commit SHA.")
    task: str | None = Field(default=None, description="The task to execute during deployment, such as deploy or deploy:migrations.")
    auto_merge: bool | None = Field(default=None, description="Whether to automatically merge the default branch into the requested ref if it's behind.")
    required_contexts: list[str] | None = Field(default=None, description="An array of commit status context names that must be in success state before deployment. Omit to verify all contexts, or pass an empty array to bypass checks entirely.")
    payload: dict[str, Any] | str | None = Field(default=None, description="A JSON object containing extra information for the deployment system, such as configuration or metadata.")
    environment: str | None = Field(default=None, description="The target deployment environment name, such as production, staging, or qa.")
    description: str | None = Field(default=None, description="A short description of the deployment.")
    transient_environment: bool | None = Field(default=None, description="Whether the environment is temporary and will no longer exist after the deployment completes.")
    production_environment: bool | None = Field(default=None, description="Whether the environment is directly used by end-users. Defaults to true for production environments, false otherwise.")
class ReposCreateDeploymentRequest(StrictModel):
    """Create a deployment for a repository ref (branch, tag, or SHA) to a specified environment. Supports automatic merging, commit status verification, and custom deployment payloads."""
    path: ReposCreateDeploymentRequestPath
    body: ReposCreateDeploymentRequestBody

# Operation: get_deployment
class ReposGetDeploymentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    deployment_id: int = Field(default=..., description="The unique identifier of the deployment to retrieve.")
class ReposGetDeploymentRequest(StrictModel):
    """Retrieve detailed information about a specific deployment in a repository. Returns the deployment's current status, environment, and associated metadata."""
    path: ReposGetDeploymentRequestPath

# Operation: delete_deployment
class ReposDeleteDeploymentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    deployment_id: int = Field(default=..., description="The unique identifier of the deployment to delete.")
class ReposDeleteDeploymentRequest(StrictModel):
    """Delete a deployment from a repository. You can delete any deployment if the repository has only one, but can only delete inactive deployments if multiple exist. To deactivate a deployment, create a new active deployment or add a non-successful deployment status to the current one."""
    path: ReposDeleteDeploymentRequestPath

# Operation: list_deployment_statuses
class ReposListDeploymentStatusesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    deployment_id: int = Field(default=..., description="The unique identifier of the deployment for which to retrieve statuses.")
class ReposListDeploymentStatusesRequest(StrictModel):
    """Retrieve all deployment statuses for a specific deployment. Users with pull access can view the status history and details of a deployment."""
    path: ReposListDeploymentStatusesRequestPath

# Operation: create_deployment_status
class ReposCreateDeploymentStatusRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    deployment_id: int = Field(default=..., description="The unique identifier of the deployment for which to create a status.")
class ReposCreateDeploymentStatusRequestBody(StrictModel):
    state: Literal["error", "failure", "inactive", "in_progress", "queued", "pending", "success"] = Field(default=..., description="The state of the deployment status. When set to `inactive` on a transient deployment, it will be displayed as `destroyed` in GitHub.")
    log_url: str | None = Field(default=None, description="The full URL of the deployment's output logs. This parameter replaces `target_url` and is the recommended field to use.")
    description: str | None = Field(default=None, description="A short description of the deployment status. Maximum length is 140 characters.")
    environment: str | None = Field(default=None, description="Name of the target deployment environment (e.g., `production`, `staging`, `qa`). If not specified, the environment from the previous deployment status or the deployment itself will be used.")
    environment_url: str | None = Field(default=None, description="The URL for accessing the deployed environment.")
    auto_inactive: bool | None = Field(default=None, description="When true, automatically marks all prior successful non-transient, non-production environment deployments with the same repository and environment name as inactive.")
class ReposCreateDeploymentStatusRequest(StrictModel):
    """Create a deployment status for a given deployment. Users with push access can report the progress and outcome of a deployment by setting its state, environment, and associated metadata."""
    path: ReposCreateDeploymentStatusRequestPath
    body: ReposCreateDeploymentStatusRequestBody

# Operation: get_deployment_status
class ReposGetDeploymentStatusRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    deployment_id: int = Field(default=..., description="The unique identifier of the deployment for which to retrieve the status.")
    status_id: int = Field(default=..., description="The unique identifier of the specific deployment status to retrieve.")
class ReposGetDeploymentStatusRequest(StrictModel):
    """Retrieve a specific deployment status for a deployment. Users with pull access can view deployment status details to monitor deployment progress and outcomes."""
    path: ReposGetDeploymentStatusRequestPath

# Operation: list_environments
class ReposGetAllEnvironmentsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
class ReposGetAllEnvironmentsRequest(StrictModel):
    """List all environments configured for a repository. Accessible to anyone with read access; private repositories require the `repo` scope for OAuth apps and personal access tokens."""
    path: ReposGetAllEnvironmentsRequestPath

# Operation: get_environment
class ReposGetEnvironmentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with forward slashes replaced by `%2F`.")
class ReposGetEnvironmentRequest(StrictModel):
    """Retrieve detailed information about a specific deployment environment in a repository. Requires read access to the repository; use the `repo` OAuth scope for private repositories."""
    path: ReposGetEnvironmentRequestPath

# Operation: configure_environment
class ReposCreateOrUpdateEnvironmentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
class ReposCreateOrUpdateEnvironmentRequestBodyDeploymentBranchPolicy(StrictModel):
    protected_branches: bool = Field(default=..., validation_alias="protected_branches", serialization_alias="protected_branches", description="Whether only branches with branch protection rules can deploy to this environment. If true, `custom_branch_policies` must be false.")
    custom_branch_policies: bool = Field(default=..., validation_alias="custom_branch_policies", serialization_alias="custom_branch_policies", description="Whether only branches matching specified name patterns can deploy to this environment. If true, `protected_branches` must be false.")
class ReposCreateOrUpdateEnvironmentRequestBody(StrictModel):
    wait_timer: int | None = Field(default=None, description="The number of minutes to delay a job after it is initially triggered. Must be an integer between 0 and 43,200 (30 days).")
    prevent_self_review: bool | None = Field(default=None, description="Whether to prevent the user who created the job from approving their own job.")
    reviewers: list[ReposCreateOrUpdateEnvironmentBodyReviewersItem] | None = Field(default=None, description="The people or teams that may review and approve jobs referencing this environment. You can specify up to six users or teams, each requiring at least read access to the repository. Only one reviewer needs to approve for the job to proceed.")
    deployment_branch_policy: ReposCreateOrUpdateEnvironmentRequestBodyDeploymentBranchPolicy
class ReposCreateOrUpdateEnvironmentRequest(StrictModel):
    """Create or update a deployment environment with protection rules, including required reviewers and branch policies. This controls which branches can deploy and who must approve deployments to this environment."""
    path: ReposCreateOrUpdateEnvironmentRequestPath
    body: ReposCreateOrUpdateEnvironmentRequestBody

# Operation: delete_environment
class ReposDeleteAnEnvironmentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with forward slashes replaced by `%2F`.")
class ReposDeleteAnEnvironmentRequest(StrictModel):
    """Delete a deployment environment from a repository. Requires `repo` scope authentication via OAuth app token or personal access token (classic)."""
    path: ReposDeleteAnEnvironmentRequestPath

# Operation: list_deployment_branch_policies
class ReposListDeploymentBranchPoliciesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with slashes replaced by `%2F`.")
class ReposListDeploymentBranchPoliciesRequest(StrictModel):
    """Lists all deployment branch policies configured for a specific environment in a repository. This endpoint allows you to view which branches are authorized to deploy to the environment."""
    path: ReposListDeploymentBranchPoliciesRequestPath

# Operation: create_deployment_branch_policy
class ReposCreateDeploymentBranchPolicyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
class ReposCreateDeploymentBranchPolicyRequestBody(StrictModel):
    name: str = Field(default=..., description="The name pattern that branches or tags must match to deploy to the environment. Wildcard characters do not match `/`. Use patterns like `release/*/*` to match branches beginning with `release/` and containing an additional single slash. See Ruby File.fnmatch documentation for pattern matching syntax.")
    type_: Literal["branch", "tag"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Whether this policy targets a branch or tag.")
class ReposCreateDeploymentBranchPolicyRequest(StrictModel):
    """Creates a deployment branch or tag policy for an environment, controlling which branches or tags are allowed to deploy. Requires `repo` scope for OAuth apps and personal access tokens."""
    path: ReposCreateDeploymentBranchPolicyRequestPath
    body: ReposCreateDeploymentBranchPolicyRequestBody

# Operation: get_deployment_branch_policy
class ReposGetDeploymentBranchPolicyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with slashes replaced by `%2F`.")
    branch_policy_id: int = Field(default=..., description="The unique identifier of the branch policy to retrieve.")
class ReposGetDeploymentBranchPolicyRequest(StrictModel):
    """Retrieve a specific deployment branch or tag policy for a repository environment. This endpoint allows anyone with read access to view policy details that control which branches or tags can be deployed to the environment."""
    path: ReposGetDeploymentBranchPolicyRequestPath

# Operation: update_deployment_branch_policy
class ReposUpdateDeploymentBranchPolicyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
    branch_policy_id: int = Field(default=..., description="The unique identifier of the branch policy to update.")
class ReposUpdateDeploymentBranchPolicyRequestBody(StrictModel):
    name: str = Field(default=..., description="The name pattern that branches must match to deploy to the environment. Wildcard characters do not match `/`. Use patterns like `release/*/*` to match branches beginning with `release/` and containing an additional single slash. Refer to Ruby File.fnmatch syntax for pattern matching rules.")
class ReposUpdateDeploymentBranchPolicyRequest(StrictModel):
    """Update a deployment branch or tag policy for a specific environment. This allows you to modify the branch name pattern that controls which branches can deploy to the environment."""
    path: ReposUpdateDeploymentBranchPolicyRequestPath
    body: ReposUpdateDeploymentBranchPolicyRequestBody

# Operation: delete_deployment_branch_policy
class ReposDeleteDeploymentBranchPolicyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
    branch_policy_id: int = Field(default=..., description="The unique identifier of the branch policy to delete.")
class ReposDeleteDeploymentBranchPolicyRequest(StrictModel):
    """Delete a deployment branch or tag policy for an environment. This removes restrictions on which branches or tags can be deployed to the specified environment."""
    path: ReposDeleteDeploymentBranchPolicyRequestPath

# Operation: list_deployment_protection_rules
class ReposGetAllDeploymentProtectionRulesRequestPath(StrictModel):
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with slashes replaced by %2F.")
    repo: str = Field(default=..., description="The name of the repository without the .git extension. The name is case-insensitive.")
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
class ReposGetAllDeploymentProtectionRulesRequest(StrictModel):
    """Retrieve all custom deployment protection rules enabled for a specific environment. Anyone with read access to the repository can use this endpoint to view deployment safeguards."""
    path: ReposGetAllDeploymentProtectionRulesRequestPath

# Operation: list_deployment_rule_integrations
class ReposListCustomDeploymentRuleIntegrationsRequestPath(StrictModel):
    environment_name: str = Field(default=..., description="The name of the environment. URL encode special characters, such as replacing forward slashes with `%2F`.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
class ReposListCustomDeploymentRuleIntegrationsRequest(StrictModel):
    """Retrieve all custom deployment protection rule integrations available for a specific environment. The authenticated user must have admin or owner permissions on the repository."""
    path: ReposListCustomDeploymentRuleIntegrationsRequestPath

# Operation: get_deployment_protection_rule
class ReposGetCustomDeploymentProtectionRuleRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced with `%2F`.")
    protection_rule_id: int = Field(default=..., description="The unique identifier of the deployment protection rule.")
class ReposGetCustomDeploymentProtectionRuleRequest(StrictModel):
    """Retrieve a custom deployment protection rule for a specific environment. Anyone with read access to the repository can use this endpoint."""
    path: ReposGetCustomDeploymentProtectionRuleRequestPath

# Operation: disable_deployment_protection_rule
class ReposDisableDeploymentProtectionRuleRequestPath(StrictModel):
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by %2F.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    protection_rule_id: int = Field(default=..., description="The unique identifier of the protection rule to disable.")
class ReposDisableDeploymentProtectionRuleRequest(StrictModel):
    """Disable a custom deployment protection rule for an environment. The authenticated user must have admin or owner permissions to the repository."""
    path: ReposDisableDeploymentProtectionRuleRequestPath

# Operation: list_environment_secrets
class ActionsListEnvironmentSecretsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    environment_name: str = Field(default=..., description="The environment name. Must be URL encoded, with forward slashes replaced by `%2F`.")
class ActionsListEnvironmentSecretsRequest(StrictModel):
    """Retrieve all secrets configured for a specific environment without exposing their encrypted values. Requires collaborator access to the repository."""
    path: ActionsListEnvironmentSecretsRequestPath

# Operation: get_environment_public_key
class ActionsGetEnvironmentPublicKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
class ActionsGetEnvironmentPublicKeyRequest(StrictModel):
    """Retrieve the public key for an environment, which is required to encrypt environment secrets before creation or updates. This endpoint is accessible to anyone with read access to the repository."""
    path: ActionsGetEnvironmentPublicKeyRequestPath

# Operation: get_environment_secret
class ActionsGetEnvironmentSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class ActionsGetEnvironmentSecretRequest(StrictModel):
    """Retrieve a single environment secret without revealing its encrypted value. Requires collaborator access to the repository."""
    path: ActionsGetEnvironmentSecretRequestPath

# Operation: delete_environment_secret
class ActionsDeleteEnvironmentSecretRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
    secret_name: str = Field(default=..., description="The name of the secret to delete from the environment.")
class ActionsDeleteEnvironmentSecretRequest(StrictModel):
    """Delete a secret from a repository environment by name. Requires collaborator access and the `repo` OAuth scope."""
    path: ActionsDeleteEnvironmentSecretRequestPath

# Operation: list_environment_variables
class ActionsListEnvironmentVariablesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with slashes replaced by `%2F`.")
class ActionsListEnvironmentVariablesRequest(StrictModel):
    """Retrieve all environment variables for a specific repository environment. Requires collaborator access to the repository."""
    path: ActionsListEnvironmentVariablesRequestPath

# Operation: create_environment_variable
class ActionsCreateEnvironmentVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
class ActionsCreateEnvironmentVariableRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the variable to create in the environment.")
    value: str = Field(default=..., description="The value assigned to the environment variable.")
class ActionsCreateEnvironmentVariableRequest(StrictModel):
    """Create an environment variable in a GitHub Actions workflow environment. Authenticated users must have collaborator access to the repository."""
    path: ActionsCreateEnvironmentVariableRequestPath
    body: ActionsCreateEnvironmentVariableRequestBody

# Operation: get_environment_variable
class ActionsGetEnvironmentVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    environment_name: str = Field(default=..., description="The name of the environment. The name must be URL encoded, with slashes replaced by `%2F`.")
    name: str = Field(default=..., description="The name of the variable to retrieve.")
class ActionsGetEnvironmentVariableRequest(StrictModel):
    """Retrieve a specific environment variable from a repository environment. Requires collaborator access to the repository."""
    path: ActionsGetEnvironmentVariableRequestPath

# Operation: update_environment_variable
class ActionsUpdateEnvironmentVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    name: str = Field(default=..., description="The name of the environment variable to update.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with slashes replaced by `%2F`.")
class ActionsUpdateEnvironmentVariableRequestBody(StrictModel):
    value: str | None = Field(default=None, description="The new value for the environment variable.")
class ActionsUpdateEnvironmentVariableRequest(StrictModel):
    """Update an environment variable in a GitHub Actions workflow environment. Requires collaborator access to the repository."""
    path: ActionsUpdateEnvironmentVariableRequestPath
    body: ActionsUpdateEnvironmentVariableRequestBody | None = None

# Operation: delete_environment_variable
class ActionsDeleteEnvironmentVariableRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    name: str = Field(default=..., description="The name of the environment variable to delete.")
    environment_name: str = Field(default=..., description="The name of the environment. Must be URL encoded, with slashes replaced by `%2F`.")
class ActionsDeleteEnvironmentVariableRequest(StrictModel):
    """Delete an environment variable from a repository environment by name. Requires collaborator access to the repository and appropriate OAuth or personal access token permissions."""
    path: ActionsDeleteEnvironmentVariableRequestPath

# Operation: list_repository_events
class ActivityListRepoEventsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActivityListRepoEventsRequest(StrictModel):
    """Retrieve a list of events that have occurred in a repository. Note: This API is not optimized for real-time use cases and may have latency ranging from 30 seconds to 6 hours depending on time of day."""
    path: ActivityListRepoEventsRequestPath

# Operation: list_repository_forks
class ReposListForksRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposListForksRequest(StrictModel):
    """Retrieve a list of all forks created from a specified repository. This operation returns fork metadata for the given repository."""
    path: ReposListForksRequestPath

# Operation: fork_repository
class ReposCreateForkRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposCreateForkRequestBody(StrictModel):
    organization: str | None = Field(default=None, description="The organization name to fork the repository into. If not specified, the fork is created under the authenticated user's account.")
    default_branch_only: bool | None = Field(default=None, description="When enabled, fork only the default branch instead of all branches.")
class ReposCreateForkRequest(StrictModel):
    """Create a fork of a repository for the authenticated user. The fork operation is asynchronous and may take a short time before git objects are accessible."""
    path: ReposCreateForkRequestPath
    body: ReposCreateForkRequestBody | None = None

# Operation: create_blob
class GitCreateBlobRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class GitCreateBlobRequestBody(StrictModel):
    content: str = Field(default=..., description="The content to store in the blob object.")
    encoding: str | None = Field(default=None, description="The encoding format for the content. Determines how the content string is interpreted before storage.")
class GitCreateBlobRequest(StrictModel):
    """Create a new blob object in a repository with specified content. The blob is stored in the Git object database and can be referenced by its SHA-1 hash."""
    path: GitCreateBlobRequestPath
    body: GitCreateBlobRequestBody

# Operation: get_blob
class GitGetBlobRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    file_sha: str = Field(default=..., description="The SHA hash identifier of the blob object to retrieve.")
class GitGetBlobRequest(StrictModel):
    """Retrieve a blob object from a repository by its SHA hash. The blob content is returned as Base64 encoded by default, with support for raw data retrieval via custom media types. Supports blobs up to 100 megabytes in size."""
    path: GitGetBlobRequestPath

# Operation: create_commit
class GitCreateCommitRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class GitCreateCommitRequestBodyAuthor(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the author (or committer) of the commit")
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The email of the author (or committer) of the commit")
class GitCreateCommitRequestBody(StrictModel):
    message: str = Field(default=..., description="The commit message describing the changes in this commit.")
    tree: str = Field(default=..., description="The SHA of the tree object that this commit points to, representing the repository state at this commit.")
    parents: list[str] | None = Field(default=None, description="Array of parent commit SHAs. If omitted or empty, creates a root commit. For a single parent, provide an array with one SHA; for merge commits, provide multiple SHAs in order.")
    signature: str | None = Field(default=None, description="An ASCII-armored detached PGP signature over the commit object. GitHub adds this to the commit's `gpgsig` header for signature verification. Requires a pre-generated valid PGP signature.")
    author: GitCreateCommitRequestBodyAuthor | None = None
class GitCreateCommitRequest(StrictModel):
    """Creates a new Git commit object with the specified tree and parent commits. The response includes signature verification details if applicable."""
    path: GitCreateCommitRequestPath
    body: GitCreateCommitRequestBody

# Operation: get_commit_object
class GitGetCommitRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    commit_sha: str = Field(default=..., description="The SHA (Secure Hash Algorithm) identifier of the commit to retrieve.")
class GitGetCommitRequest(StrictModel):
    """Retrieve a Git commit object by its SHA hash. Returns commit metadata including author, committer, message, tree, parents, and GPG signature verification details."""
    path: GitGetCommitRequestPath

# Operation: list_git_refs
class GitListMatchingRefsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ref: str = Field(default=..., description="The Git reference pattern to match. Use `heads/<branch_name>` for branches and `tags/<tag_name>` for tags. If the exact ref doesn't exist, all refs starting with the pattern will be returned. Omit this parameter to retrieve all references in the repository.")
class GitListMatchingRefsRequest(StrictModel):
    """List Git references matching a specified pattern. Returns branches, tags, notes, stashes, and other references from the repository's Git database that match the provided ref pattern."""
    path: GitListMatchingRefsRequestPath

# Operation: get_git_reference
class GitGetRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    ref: str = Field(default=..., description="The Git reference to retrieve, formatted as `heads/<branch name>` for branches or `tags/<tag name>` for tags.")
class GitGetRefRequest(StrictModel):
    """Retrieve a single Git reference (branch or tag) from the repository's Git database. The reference must be formatted as `heads/<branch name>` for branches or `tags/<tag name>` for tags; returns 404 if the reference does not exist."""
    path: GitGetRefRequestPath

# Operation: create_git_ref
class GitCreateRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class GitCreateRefRequestBody(StrictModel):
    ref: str = Field(default=..., description="The fully qualified reference name (e.g., `refs/heads/main`, `refs/tags/v1.0`). Must start with 'refs' and contain at least two slashes, otherwise the request will be rejected.")
    sha: str = Field(default=..., description="The SHA-1 commit hash that this reference should point to. The commit must exist in the repository.")
class GitCreateRefRequest(StrictModel):
    """Creates a new reference (branch, tag, or other ref) in a repository. The repository must have at least one commit; empty repositories cannot have references created."""
    path: GitCreateRefRequestPath
    body: GitCreateRefRequestBody

# Operation: update_git_ref
class GitUpdateRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ref: str = Field(default=..., description="The Git reference to update, such as a branch name (e.g., `heads/main`) or tag. See Git References documentation for valid reference formats.")
class GitUpdateRefRequestBody(StrictModel):
    sha: str = Field(default=..., description="The SHA1 commit hash to set this reference to point at.")
    force: bool | None = Field(default=None, description="Force the update without safety checks. When false or omitted, the operation will only succeed if it's a fast-forward update, preventing accidental overwrites.")
class GitUpdateRefRequest(StrictModel):
    """Update a Git reference to point to a new commit SHA. This operation allows you to move branches, tags, or other references to different commits, with optional force-push capability to override safety checks."""
    path: GitUpdateRefRequestPath
    body: GitUpdateRefRequestBody

# Operation: delete_git_ref
class GitDeleteRefRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ref: str = Field(default=..., description="The Git reference to delete, such as a branch or tag (e.g., `heads/feature-a` for branches or `tags/v1.0` for tags).")
class GitDeleteRefRequest(StrictModel):
    """Deletes a specified Git reference from the repository. This operation removes branches, tags, or other Git references permanently."""
    path: GitDeleteRefRequestPath

# Operation: create_tag
class GitCreateTagRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class GitCreateTagRequestBodyTagger(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the author who created the tag.")
    email: str = Field(default=..., validation_alias="email", serialization_alias="email", description="The email address of the author who created the tag.")
class GitCreateTagRequestBody(StrictModel):
    tag: str = Field(default=..., description="The tag's name, typically a version identifier.")
    message: str = Field(default=..., description="The message content for the annotated tag.")
    object_: str = Field(default=..., validation_alias="object", serialization_alias="object", description="The SHA hash of the Git object (commit, tree, or blob) that this tag references.")
    type_: Literal["commit", "tree", "blob"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of Git object being tagged.")
    tagger: GitCreateTagRequestBodyTagger
class GitCreateTagRequest(StrictModel):
    """Create an annotated tag object in a repository. Note that this creates the tag object itself; you must separately create a reference (refs/tags/[tag]) to make the tag accessible in Git. For lightweight tags, only the reference creation is needed."""
    path: GitCreateTagRequestPath
    body: GitCreateTagRequestBody

# Operation: get_tag
class GitGetTagRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    tag_sha: str = Field(default=..., description="The SHA (commit hash) of the tag object to retrieve.")
class GitGetTagRequest(StrictModel):
    """Retrieve a specific Git tag object by its SHA. Returns tag metadata including signature verification details to validate the authenticity of the tag."""
    path: GitGetTagRequestPath

# Operation: create_tree
class GitCreateTreeRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class GitCreateTreeRequestBody(StrictModel):
    tree: list[GitCreateTreeBodyTreeItem] = Field(default=..., description="Array of tree entry objects defining the file structure. Each entry specifies a file path, Unix file mode, object type (blob or tree), and Git object SHA. Entries are processed in order and will overwrite base_tree entries with matching paths.")
    base_tree: str | None = Field(default=None, description="The SHA1 of an existing Git tree to use as the base. New entries will be merged with the base tree, with matching paths overwritten. If omitted, the tree is created from only the provided entries, and any files not included will be marked as deleted in subsequent commits.")
class GitCreateTreeRequest(StrictModel):
    """Create a new Git tree object with specified file structure, optionally based on an existing tree. Tree entries can add, modify, or delete files; use the returned tree SHA to create commits and update branch references."""
    path: GitCreateTreeRequestPath
    body: GitCreateTreeRequestBody

# Operation: fetch_tree
class GitGetTreeRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    tree_sha: str = Field(default=..., description="The SHA1 value or ref (branch or tag) name identifying the tree to retrieve.")
class GitGetTreeRequestQuery(StrictModel):
    recursive: str | None = Field(default=None, description="Enable recursive retrieval of all objects and subtrees referenced by the specified tree. Any value (including '0', '1', 'true', 'false') enables recursion; omit to disable.")
class GitGetTreeRequest(StrictModel):
    """Retrieve a Git tree object by its SHA1 value or ref name. Optionally fetch the tree recursively to include all referenced objects and subtrees, with a limit of 100,000 entries and 7 MB maximum size."""
    path: GitGetTreeRequestPath
    query: GitGetTreeRequestQuery | None = None

# Operation: list_webhooks_repository
class ReposListWebhooksRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
class ReposListWebhooksRequest(StrictModel):
    """Retrieves all webhooks configured for a repository. The last response field may be null if no deliveries have occurred within the past 30 days."""
    path: ReposListWebhooksRequestPath

# Operation: create_webhook_repository
class ReposCreateWebhookRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposCreateWebhookRequestBodyConfig(StrictModel):
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="The URL endpoint where webhook payloads will be delivered.", json_schema_extra={'format': 'uri'})
    content_type: str | None = Field(default=None, validation_alias="content_type", serialization_alias="content_type", description="The media type format for serializing webhook payloads. Defaults to `form` if not specified.")
    secret: str | None = Field(default=None, validation_alias="secret", serialization_alias="secret", description="A secret string used to generate HMAC hex digest signatures for authenticating webhook delivery headers. Enhances security by allowing verification that payloads originated from GitHub.")
class ReposCreateWebhookRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Whether the webhook is active and will send notifications when triggered. Defaults to `true`.")
    config: ReposCreateWebhookRequestBodyConfig | None = None
class ReposCreateWebhookRequest(StrictModel):
    """Create a webhook for a repository to receive HTTP POST notifications when repository events occur. Each webhook must have a unique configuration, though multiple webhooks can share the same configuration if their event subscriptions do not overlap."""
    path: ReposCreateWebhookRequestPath
    body: ReposCreateWebhookRequestBody | None = None

# Operation: get_webhook
class ReposGetWebhookRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. You can find this value in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposGetWebhookRequest(StrictModel):
    """Retrieve a webhook configured in a repository by its unique identifier. Returns the complete webhook configuration including URL, events, and delivery settings."""
    path: ReposGetWebhookRequestPath

# Operation: update_webhook_repository
class ReposUpdateWebhookRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. You can find this value in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposUpdateWebhookRequestBodyConfig(StrictModel):
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="The URL to which webhook payloads will be delivered.", json_schema_extra={'format': 'uri'})
    content_type: str | None = Field(default=None, validation_alias="content_type", serialization_alias="content_type", description="The media type used to serialize payloads. Supported values are `json` and `form`, with `form` as the default.")
    secret: str | None = Field(default=None, validation_alias="secret", serialization_alias="secret", description="A secret used as the key to generate HMAC hex digest values for delivery signature headers. If previously set, you must provide the same secret or a new one to avoid removal.")
class ReposUpdateWebhookRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Determines if notifications are sent when the webhook is triggered. Set to `true` to enable notifications.")
    config: ReposUpdateWebhookRequestBodyConfig | None = None
class ReposUpdateWebhookRequest(StrictModel):
    """Updates an existing webhook in a repository. When updating, you must provide the same secret if one was previously set, or provide a new secret; otherwise the secret will be removed."""
    path: ReposUpdateWebhookRequestPath
    body: ReposUpdateWebhookRequestBody | None = None

# Operation: delete_webhook_repository
class ReposDeleteWebhookRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. You can find this value in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposDeleteWebhookRequest(StrictModel):
    """Delete a webhook from a repository. The authenticated user must be a repository owner or have admin access to perform this action."""
    path: ReposDeleteWebhookRequestPath

# Operation: get_webhook_config_repository
class ReposGetWebhookConfigForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. You can find this value in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposGetWebhookConfigForRepoRequest(StrictModel):
    """Retrieve the webhook configuration for a repository, including URL, content type, and custom headers. Use this to inspect webhook delivery settings without fetching the full webhook object."""
    path: ReposGetWebhookConfigForRepoRequestPath

# Operation: update_webhook_config_repository
class ReposUpdateWebhookConfigForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. You can find this value in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposUpdateWebhookConfigForRepoRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The URL to which the webhook payloads will be delivered.", json_schema_extra={'format': 'uri'})
    content_type: str | None = Field(default=None, description="The media type used to serialize the payloads. Supported values are `json` and `form`, with `form` as the default.")
    secret: str | None = Field(default=None, description="If provided, the secret will be used as the key to generate the HMAC hex digest value for delivery signature headers.")
class ReposUpdateWebhookConfigForRepoRequest(StrictModel):
    """Updates the webhook configuration for a repository, including the delivery URL, payload format, and signature secret. Use this endpoint to modify webhook settings; for changes to active state or event subscriptions, use the update webhook endpoint instead."""
    path: ReposUpdateWebhookConfigForRepoRequestPath
    body: ReposUpdateWebhookConfigForRepoRequestBody | None = None

# Operation: list_webhook_deliveries
class ReposListWebhookDeliveriesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the `X-GitHub-Hook-ID` header of any webhook delivery from this hook.")
class ReposListWebhookDeliveriesRequest(StrictModel):
    """Retrieve a list of all webhook deliveries for a specific repository webhook. Each delivery record includes the payload, response status, and timing information."""
    path: ReposListWebhookDeliveriesRequestPath

# Operation: get_webhook_delivery
class ReposGetWebhookDeliveryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the `X-GitHub-Hook-ID` header of a webhook delivery.")
    delivery_id: str = Field(default=..., description="The unique identifier of the specific webhook delivery to retrieve.", json_schema_extra={'format': 'int64'})
class ReposGetWebhookDeliveryRequest(StrictModel):
    """Retrieve a specific delivery record for a repository webhook. This returns detailed information about a webhook event that was sent to a configured endpoint."""
    path: ReposGetWebhookDeliveryRequestPath

# Operation: redeliver_webhook_delivery
class ReposRedeliverWebhookDeliveryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the `X-GitHub-Hook-ID` header of a webhook delivery.")
    delivery_id: str = Field(default=..., description="The unique identifier of the webhook delivery to redeliver.", json_schema_extra={'format': 'int64'})
class ReposRedeliverWebhookDeliveryRequest(StrictModel):
    """Redeliver a previously failed or missed webhook delivery for a repository webhook. This allows you to retry sending a webhook payload to its configured endpoint."""
    path: ReposRedeliverWebhookDeliveryRequestPath

# Operation: trigger_webhook_ping
class ReposPingWebhookRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. This value can be found in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposPingWebhookRequest(StrictModel):
    """Trigger a ping event to be sent to a repository webhook. This is useful for testing webhook connectivity and verifying that the webhook endpoint is responding correctly."""
    path: ReposPingWebhookRequestPath

# Operation: trigger_webhook_test
class ReposTestPushWebhookRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    hook_id: int = Field(default=..., description="The unique identifier of the webhook. You can find this value in the `X-GitHub-Hook-ID` header of a webhook delivery.")
class ReposTestPushWebhookRequest(StrictModel):
    """Trigger a test delivery of a repository webhook using the latest push event. The webhook must be subscribed to push events; otherwise, the server responds with 204 and no test payload is sent."""
    path: ReposTestPushWebhookRequestPath

# Operation: get_immutable_releases
class ReposCheckImmutableReleasesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposCheckImmutableReleasesRequest(StrictModel):
    """Retrieve the immutable releases configuration for a repository, including whether immutability is enabled and if it's being enforced by the repository owner. Requires admin read access to the repository."""
    path: ReposCheckImmutableReleasesRequestPath

# Operation: get_app_installation_repository
class AppsGetRepoInstallationRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository account. This is case-insensitive and can be either a user or organization name.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. This is case-insensitive.")
class AppsGetRepoInstallationRequest(StrictModel):
    """Retrieve the installation information for a GitHub App in a specific repository. This endpoint requires JWT authentication and returns details about whether the app is installed for a user or organization account."""
    path: AppsGetRepoInstallationRequestPath

# Operation: get_repository_interaction_restrictions
class InteractionsGetRestrictionsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class InteractionsGetRestrictionsForRepoRequest(StrictModel):
    """Retrieve the current interaction restrictions for a repository, including which user types can interact and when the restriction expires. Returns an empty response if no restrictions are active."""
    path: InteractionsGetRestrictionsForRepoRequestPath

# Operation: remove_interaction_restrictions
class InteractionsRemoveRestrictionsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class InteractionsRemoveRestrictionsForRepoRequest(StrictModel):
    """Remove all interaction restrictions from a repository. Requires owner or admin access. Note: If interaction limits are set at the user or organization level, you will receive a 409 Conflict response and cannot modify restrictions for individual repositories."""
    path: InteractionsRemoveRestrictionsForRepoRequestPath

# Operation: list_repository_invitations
class ReposListInvitationsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposListInvitationsRequest(StrictModel):
    """List all open repository invitations for a repository. Requires admin access to the repository."""
    path: ReposListInvitationsRequestPath

# Operation: update_repository_invitation
class ReposUpdateInvitationRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    invitation_id: int = Field(default=..., description="The unique identifier of the invitation to update.")
class ReposUpdateInvitationRequestBody(StrictModel):
    permissions: Literal["read", "write", "maintain", "triage", "admin"] | None = Field(default=None, description="The permissions level to grant the invited user on the repository.")
class ReposUpdateInvitationRequest(StrictModel):
    """Update the permissions for an existing repository invitation. Allows you to modify the access level that will be granted to the invited user."""
    path: ReposUpdateInvitationRequestPath
    body: ReposUpdateInvitationRequestBody | None = None

# Operation: delete_repository_invitation
class ReposDeleteInvitationRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    invitation_id: int = Field(default=..., description="The unique identifier of the invitation to delete.")
class ReposDeleteInvitationRequest(StrictModel):
    """Delete a pending repository invitation by its unique identifier. This removes access that was previously offered to a user or team."""
    path: ReposDeleteInvitationRequestPath

# Operation: list_issues_repository
class IssuesListForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class IssuesListForRepoRequestQuery(StrictModel):
    milestone: str | None = Field(default=None, description="Filter by milestone. Pass a milestone number, `*` for any milestone, or `none` for issues without milestones.")
    state: Literal["open", "closed", "all"] | None = Field(default=None, description="Filter by issue state.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter by issue type. Pass a type name, `*` for any type, or `none` for issues without a type.")
    creator: str | None = Field(default=None, description="Filter to issues created by a specific user.")
    mentioned: str | None = Field(default=None, description="Filter to issues that mention a specific user.")
    labels: str | None = Field(default=None, description="Filter by labels. Provide as comma-separated label names.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results.")
    since: str | None = Field(default=None, description="Only return issues last updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class IssuesListForRepoRequest(StrictModel):
    """List issues in a repository, including pull requests. By default, only open issues are returned. Use filters to narrow results by milestone, state, creator, labels, and other criteria."""
    path: IssuesListForRepoRequestPath
    query: IssuesListForRepoRequestQuery | None = None

# Operation: create_issue
class IssuesCreateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class IssuesCreateRequestBody(StrictModel):
    title: str = Field(default=..., description="The title of the issue. Accepts string or integer values.")
    body: str | None = Field(default=None, description="The contents of the issue in markdown format.")
    milestone: str | None = Field(default=None, description="The milestone to associate with this issue. Accepts string or integer identifier.")
    labels: list[IssuesCreateBodyLabelsItem] | None = Field(default=None, description="Labels to associate with this issue. Only users with push access can set labels; they are silently dropped for other users. Provide as an array of label names.")
    assignees: list[str] | None = Field(default=None, description="GitHub usernames to assign to this issue. Only users with push access can set assignees; they are silently dropped for other users. Provide as an array of login handles.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The issue type to associate with this issue. Only users with push access can set the type; it is silently dropped for other users.")
class IssuesCreateRequest(StrictModel):
    """Create a new issue in a repository. Any user with pull access can create issues, though labels, assignees, and type can only be set by users with push access."""
    path: IssuesCreateRequestPath
    body: IssuesCreateRequestBody

# Operation: list_issue_comments_for_repository
class IssuesListCommentsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class IssuesListCommentsForRepoRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results. Only applies when used with a sort parameter.")
    since: str | None = Field(default=None, description="Only return comments that were last updated after this timestamp. Specify in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class IssuesListCommentsForRepoRequest(StrictModel):
    """List all comments on issues and pull requests for a repository. Comments are ordered by ID in ascending order by default, with support for filtering by update time and sort direction."""
    path: IssuesListCommentsForRepoRequestPath
    query: IssuesListCommentsForRepoRequestQuery | None = None

# Operation: get_issue_comment
class IssuesGetCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to retrieve.", json_schema_extra={'format': 'int64'})
class IssuesGetCommentRequest(StrictModel):
    """Retrieve a specific comment from an issue or pull request. Supports multiple content formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: IssuesGetCommentRequestPath

# Operation: update_issue_comment
class IssuesUpdateCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to update.", json_schema_extra={'format': 'int64'})
class IssuesUpdateCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The new content for the comment. Supports markdown formatting.")
class IssuesUpdateCommentRequest(StrictModel):
    """Update the content of an existing comment on an issue or pull request. Supports multiple response formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: IssuesUpdateCommentRequestPath
    body: IssuesUpdateCommentRequestBody

# Operation: delete_issue_comment
class IssuesDeleteCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to delete.", json_schema_extra={'format': 'int64'})
class IssuesDeleteCommentRequest(StrictModel):
    """Delete a comment from an issue or pull request. This operation permanently removes the specified comment and cannot be undone."""
    path: IssuesDeleteCommentRequestPath

# Operation: pin_issue_comment
class IssuesPinCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to pin.", json_schema_extra={'format': 'int64'})
class IssuesPinCommentRequest(StrictModel):
    """Pin a comment on an issue to highlight it for visibility. Pinned comments appear at the top of the issue's comment section."""
    path: IssuesPinCommentRequestPath

# Operation: unpin_issue_comment
class IssuesUnpinCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment to unpin.", json_schema_extra={'format': 'int64'})
class IssuesUnpinCommentRequest(StrictModel):
    """Unpin a comment from an issue. This removes the pinned status from a previously pinned issue comment."""
    path: IssuesUnpinCommentRequestPath

# Operation: list_comment_reactions
class ReactionsListForIssueCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment.", json_schema_extra={'format': 'int64'})
class ReactionsListForIssueCommentRequestQuery(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] | None = Field(default=None, description="Filter results to a specific reaction type. Omit to list all reactions to the comment.")
class ReactionsListForIssueCommentRequest(StrictModel):
    """List all reactions or filter by a specific reaction type for an issue comment. Reactions include thumbs up/down, laugh, confused, heart, hooray, rocket, and eyes."""
    path: ReactionsListForIssueCommentRequestPath
    query: ReactionsListForIssueCommentRequestQuery | None = None

# Operation: add_issue_comment_reaction
class ReactionsCreateForIssueCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the issue comment to react to.", json_schema_extra={'format': 'int64'})
class ReactionsCreateForIssueCommentRequestBody(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] = Field(default=..., description="The reaction emoji type to add to the comment. Choose from the supported reaction types.")
class ReactionsCreateForIssueCommentRequest(StrictModel):
    """Add a reaction emoji to an issue comment. Returns HTTP 200 if the reaction type was already added by the authenticated user."""
    path: ReactionsCreateForIssueCommentRequestPath
    body: ReactionsCreateForIssueCommentRequestBody

# Operation: remove_issue_comment_reaction
class ReactionsDeleteForIssueCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. This is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository, without the `.git` extension. This is case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the comment from which to remove the reaction.", json_schema_extra={'format': 'int64'})
    reaction_id: int = Field(default=..., description="The unique identifier of the reaction to remove.")
class ReactionsDeleteForIssueCommentRequest(StrictModel):
    """Remove a reaction from an issue comment. This operation deletes a specific reaction that was previously added to a comment."""
    path: ReactionsDeleteForIssueCommentRequestPath

# Operation: list_issue_events
class IssuesListEventsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class IssuesListEventsForRepoRequest(StrictModel):
    """Retrieves all events that have occurred for issues in a repository, including creation, modification, and state change events."""
    path: IssuesListEventsForRepoRequestPath

# Operation: get_issue_event
class IssuesGetEventRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    event_id: int = Field(default=..., description="The unique identifier of the issue event to retrieve.")
class IssuesGetEventRequest(StrictModel):
    """Retrieve a specific issue event by its event ID. This returns detailed information about a single event that occurred on an issue, such as comments, state changes, or assignments."""
    path: IssuesGetEventRequestPath

# Operation: get_issue
class IssuesGetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue within the repository.")
class IssuesGetRequest(StrictModel):
    """Retrieve a specific issue or pull request by its number. Returns a 301 redirect if the issue was transferred, 404 if inaccessible, or 410 if deleted from an accessible repository."""
    path: IssuesGetRequestPath

# Operation: update_issue
class IssuesUpdateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class IssuesUpdateRequestBody(StrictModel):
    body: str | None = Field(default=None, description="The contents of the issue body. Supports markdown formatting.")
    state: Literal["open", "closed"] | None = Field(default=None, description="The open or closed state of the issue.")
    state_reason: Literal["completed", "not_planned", "duplicate", "reopened"] | None = Field(default=None, description="The reason for the state change. Only used when the `state` parameter is changed.")
    milestone: str | None = Field(default=None, description="The milestone to associate with this issue. Accepts either a milestone ID (integer) or milestone title (string).")
    labels: list[IssuesUpdateBodyLabelsItem] | None = Field(default=None, description="Labels to associate with this issue. Pass one or more labels to replace the existing set. Send an empty array to clear all labels. Only users with push access can set labels; changes are silently dropped without push access.")
    assignees: list[str] | None = Field(default=None, description="Usernames to assign to this issue. Pass one or more user logins to replace the existing assignees. Send an empty array to clear all assignees. Only users with push access can set assignees; changes are silently dropped without push access.")
    issue_field_values: list[IssuesUpdateBodyIssueFieldValuesItem] | None = Field(default=None, description="An array of issue field values to set on this issue. Each entry must include the field ID and the value to set. Only users with push access can set field values.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The name of the issue type to associate with this issue. Pass `null` to remove the current issue type. Only users with push access can set the type; changes are silently dropped without push access.")
class IssuesUpdateRequest(StrictModel):
    """Update an issue in a repository. Issue owners and users with push access or Triage role can modify issue properties including title, body, state, labels, assignees, and other metadata."""
    path: IssuesUpdateRequestPath
    body: IssuesUpdateRequestBody | None = None

# Operation: assign_issue_users
class IssuesAddAssigneesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class IssuesAddAssigneesRequestBody(StrictModel):
    assignees: list[str] | None = Field(default=None, description="Usernames of people to assign to this issue. Only users with push access can add assignees; others are silently ignored. Up to 10 assignees can be added per request.")
class IssuesAddAssigneesRequest(StrictModel):
    """Add up to 10 assignees to an issue. Existing assignees are preserved and new ones are appended to the list."""
    path: IssuesAddAssigneesRequestPath
    body: IssuesAddAssigneesRequestBody | None = None

# Operation: remove_issue_assignees
class IssuesRemoveAssigneesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class IssuesRemoveAssigneesRequestBody(StrictModel):
    assignees: list[str] | None = Field(default=None, description="Usernames of assignees to remove from the issue. Provide as an array of strings representing GitHub usernames.")
class IssuesRemoveAssigneesRequest(StrictModel):
    """Remove one or more assignees from an issue. Only users with push access can remove assignees; other users' removal requests are silently ignored."""
    path: IssuesRemoveAssigneesRequestPath
    body: IssuesRemoveAssigneesRequestBody | None = None

# Operation: verify_issue_assignee
class IssuesCheckUserCanBeAssignedToIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies the specific issue to check assignee permissions for.")
    assignee: str = Field(default=..., description="The username of the user to verify for assignment eligibility to the issue.")
class IssuesCheckUserCanBeAssignedToIssueRequest(StrictModel):
    """Verify whether a user has permission to be assigned to a specific issue. Returns a 204 status if the user can be assigned, or 404 if they cannot."""
    path: IssuesCheckUserCanBeAssignedToIssueRequestPath

# Operation: list_issue_comments
class IssuesListCommentsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class IssuesListCommentsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Only show comments that were last updated after the given time. Specify as an ISO 8601 timestamp.", json_schema_extra={'format': 'date-time'})
class IssuesListCommentsRequest(StrictModel):
    """List all comments on an issue or pull request, ordered by ascending ID. Supports multiple response formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: IssuesListCommentsRequestPath
    query: IssuesListCommentsRequestQuery | None = None

# Operation: add_issue_comment
class IssuesCreateCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue or pull request.")
class IssuesCreateCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The comment text content. Supports markdown formatting.")
class IssuesCreateCommentRequest(StrictModel):
    """Add a comment to an issue or pull request. This action triggers notifications and is subject to secondary rate limiting if used too frequently."""
    path: IssuesCreateCommentRequestPath
    body: IssuesCreateCommentRequestBody

# Operation: list_blocking_issues
class IssuesListDependenciesBlockedByRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number to retrieve blocking dependencies for.")
class IssuesListDependenciesBlockedByRequest(StrictModel):
    """List all issues that are blocking the specified issue. This helps identify dependencies that must be resolved before the current issue can be completed."""
    path: IssuesListDependenciesBlockedByRequestPath

# Operation: mark_issue_blocked_by
class IssuesAddBlockedByDependencyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue that is blocked.")
class IssuesAddBlockedByDependencyRequestBody(StrictModel):
    issue_id: int = Field(default=..., description="The ID of the issue that blocks the current issue. This issue must exist in the same repository.")
class IssuesAddBlockedByDependencyRequest(StrictModel):
    """Mark an issue as blocked by another issue by creating a 'blocked by' dependency relationship. This establishes that the current issue cannot progress until the blocking issue is resolved."""
    path: IssuesAddBlockedByDependencyRequestPath
    body: IssuesAddBlockedByDependencyRequestBody

# Operation: remove_issue_blocking_dependency
class IssuesRemoveDependencyBlockedByRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue from which the blocking dependency will be removed.")
    issue_id: int = Field(default=..., description="The ID of the blocking issue to remove as a dependency.")
class IssuesRemoveDependencyBlockedByRequest(StrictModel):
    """Remove a blocking dependency from an issue. This operation unlinks an issue that was blocking the specified issue, allowing it to proceed independently."""
    path: IssuesRemoveDependencyBlockedByRequestPath

# Operation: list_blocking_dependencies
class IssuesListDependenciesBlockingRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue's blocking dependencies to retrieve.")
class IssuesListDependenciesBlockingRequest(StrictModel):
    """List all issues that are blocked by the specified issue. Use this to understand what work depends on resolving the current issue."""
    path: IssuesListDependenciesBlockingRequestPath

# Operation: list_issue_events_for_issue
class IssuesListEventsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue's events to retrieve.")
class IssuesListEventsRequest(StrictModel):
    """Retrieves a chronological list of all events that have occurred on a specific issue, including comments, state changes, assignments, and other activity."""
    path: IssuesListEventsRequestPath

# Operation: list_issue_labels
class IssuesListLabelsOnIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue within the repository.")
class IssuesListLabelsOnIssueRequest(StrictModel):
    """Retrieves all labels assigned to a specific issue in a repository. Labels are used to categorize and organize issues."""
    path: IssuesListLabelsOnIssueRequestPath

# Operation: add_issue_labels
class IssuesAddLabelsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue within the repository.")
class IssuesAddLabelsRequestBody(StrictModel):
    body: IssuesAddLabelsBodyV0 | list[str] | list[IssuesAddLabelsBodyV2Item] | None = Field(default=None, description="An object containing an array of label names to add to the issue. Each label name should be a string.", examples=[{'labels': ['bug', 'enhancement']}])
class IssuesAddLabelsRequest(StrictModel):
    """Add one or more labels to an issue in a repository. Labels help organize and categorize issues for better tracking and filtering."""
    path: IssuesAddLabelsRequestPath
    body: IssuesAddLabelsRequestBody | None = None

# Operation: replace_issue_labels
class IssuesSetLabelsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue to update labels for.")
class IssuesSetLabelsRequestBody(StrictModel):
    body: IssuesSetLabelsBody | None = Field(default=None, description="An array of label names to assign to the issue. Replaces all existing labels. Can also accept a single label name as a string.")
class IssuesSetLabelsRequest(StrictModel):
    """Replace all labels on an issue with a new set of labels. This operation removes any previously assigned labels and applies only the labels specified in the request."""
    path: IssuesSetLabelsRequestPath
    body: IssuesSetLabelsRequestBody | None = None

# Operation: remove_all_issue_labels
class IssuesRemoveAllLabelsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue within the repository.")
class IssuesRemoveAllLabelsRequest(StrictModel):
    """Remove all labels from a specific issue in a repository. This operation clears any labels currently assigned to the issue."""
    path: IssuesRemoveAllLabelsRequestPath

# Operation: remove_issue_label
class IssuesRemoveLabelRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue to remove the label from.")
    name: str = Field(default=..., description="The name of the label to remove from the issue.")
class IssuesRemoveLabelRequest(StrictModel):
    """Remove a specific label from an issue and return the remaining labels. Returns a 404 error if the label does not exist on the issue."""
    path: IssuesRemoveLabelRequestPath

# Operation: lock_issue
class IssuesLockRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class IssuesLockRequestBody(StrictModel):
    lock_reason: Literal["off-topic", "too heated", "resolved", "spam"] | None = Field(default=None, description="The reason for locking the issue or pull request conversation. Must be one of the predefined reasons.")
class IssuesLockRequest(StrictModel):
    """Lock an issue or pull request conversation to prevent further comments. Requires push access to the repository."""
    path: IssuesLockRequestPath
    body: IssuesLockRequestBody | None = None

# Operation: unlock_issue
class IssuesUnlockRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class IssuesUnlockRequest(StrictModel):
    """Unlock an issue's conversation to allow further discussion. Users with push access can perform this action."""
    path: IssuesUnlockRequestPath

# Operation: get_parent_issue
class IssuesGetParentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The numeric identifier of the sub-issue for which to retrieve the parent issue.")
class IssuesGetParentRequest(StrictModel):
    """Retrieve the parent issue of a sub-issue. Supports multiple content representation formats including raw markdown, plain text, HTML, or combined representations."""
    path: IssuesGetParentRequestPath

# Operation: list_issue_reactions
class ReactionsListForIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class ReactionsListForIssueRequestQuery(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] | None = Field(default=None, description="Filter results to a specific reaction type. Omit this parameter to list all reactions to the issue.")
class ReactionsListForIssueRequest(StrictModel):
    """List all reactions or filter by a specific reaction type for an issue. Reactions allow users to express sentiment on issues using emoji."""
    path: ReactionsListForIssueRequestPath
    query: ReactionsListForIssueRequestQuery | None = None

# Operation: add_issue_reaction
class ReactionsCreateForIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the issue.")
class ReactionsCreateForIssueRequestBody(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] = Field(default=..., description="The emoji reaction type to add to the issue.")
class ReactionsCreateForIssueRequest(StrictModel):
    """Add an emoji reaction to a GitHub issue. Returns HTTP 200 if the reaction type was already added by the authenticated user."""
    path: ReactionsCreateForIssueRequestPath
    body: ReactionsCreateForIssueRequestBody

# Operation: delete_issue_reaction
class ReactionsDeleteForIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue to remove the reaction from.")
    reaction_id: int = Field(default=..., description="The unique identifier of the reaction to delete.")
class ReactionsDeleteForIssueRequest(StrictModel):
    """Remove a reaction from an issue. The authenticated user must have permission to delete the reaction."""
    path: ReactionsDeleteForIssueRequestPath

# Operation: unlink_sub_issue
class IssuesRemoveSubIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the parent issue.")
class IssuesRemoveSubIssueRequestBody(StrictModel):
    sub_issue_id: int = Field(default=..., description="The numeric identifier of the sub-issue to remove from the parent issue.")
class IssuesRemoveSubIssueRequest(StrictModel):
    """Remove a sub-issue relationship from a parent issue. This operation unlinks the sub-issue without deleting it."""
    path: IssuesRemoveSubIssueRequestPath
    body: IssuesRemoveSubIssueRequestBody

# Operation: list_sub_issues
class IssuesListSubIssuesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies the parent issue containing the sub-issues to list.")
class IssuesListSubIssuesRequest(StrictModel):
    """List all sub-issues associated with a parent issue in a repository. Supports multiple content representation formats via custom media types."""
    path: IssuesListSubIssuesRequestPath

# Operation: link_sub_issue
class IssuesAddSubIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    issue_number: int = Field(default=..., description="The number that identifies the parent issue.")
class IssuesAddSubIssueRequestBody(StrictModel):
    sub_issue_id: int = Field(default=..., description="The ID of the sub-issue to link. The sub-issue must belong to the same repository owner as the parent issue.")
    replace_parent: bool | None = Field(default=None, description="When true, replaces the sub-issue's current parent issue with this issue. When false or omitted, the sub-issue is added without removing its existing parent relationship.")
class IssuesAddSubIssueRequest(StrictModel):
    """Link an existing sub-issue to a parent issue in the same repository. Optionally replace the sub-issue's current parent with this issue."""
    path: IssuesAddSubIssueRequestPath
    body: IssuesAddSubIssueRequestBody

# Operation: reorder_sub_issue
class IssuesReprioritizeSubIssueRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner account of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that contains the sub-issue to reorder.")
class IssuesReprioritizeSubIssueRequestBody(StrictModel):
    sub_issue_id: int = Field(default=..., description="The unique identifier of the sub-issue to move to a new position in the parent issue's sub-issue list.")
    before_id: int | None = Field(default=None, description="The id of the sub-issue to be prioritized before (either positional argument after OR before should be specified).")
    after_id: int | None = Field(default=None, description="The id of the sub-issue to be prioritized after (either positional argument after OR before should be specified).")
class IssuesReprioritizeSubIssueRequest(StrictModel):
    """Reorder a sub-issue to a different position within its parent issue's sub-issue list. Use this to change the priority ranking of sub-issues."""
    path: IssuesReprioritizeSubIssueRequestPath
    body: IssuesReprioritizeSubIssueRequestBody

# Operation: list_issue_timeline_events
class IssuesListEventsForTimelineRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue's timeline events to retrieve.")
class IssuesListEventsForTimelineRequest(StrictModel):
    """Retrieve all timeline events for a specific issue, including comments, state changes, and other activity. Timeline events provide a chronological record of all interactions and modifications to an issue."""
    path: IssuesListEventsForTimelineRequestPath

# Operation: list_deploy_keys
class ReposListDeployKeysRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposListDeployKeysRequest(StrictModel):
    """Retrieve all deploy keys for a repository. Deploy keys are SSH keys that grant access to a single repository for automated deployments and CI/CD workflows."""
    path: ReposListDeployKeysRequestPath

# Operation: create_deploy_key
class ReposCreateDeployKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposCreateDeployKeyRequestBody(StrictModel):
    key: str = Field(default=..., description="The public key contents in OpenSSH format.")
    read_only: bool | None = Field(default=None, description="If true, the key will only be able to read repository contents. If false, the key will be able to read and write, granting permissions equivalent to an organization admin or repository collaborator.")
class ReposCreateDeployKeyRequest(StrictModel):
    """Create a read-only or read-write deploy key for a repository. Deploy keys enable secure, key-based access to repository contents without requiring user credentials."""
    path: ReposCreateDeployKeyRequestPath
    body: ReposCreateDeployKeyRequestBody

# Operation: get_deploy_key
class ReposGetDeployKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    key_id: int = Field(default=..., description="The unique identifier of the deploy key to retrieve.")
class ReposGetDeployKeyRequest(StrictModel):
    """Retrieve a specific deploy key for a repository by its unique identifier. Deploy keys are used to grant read or write access to a repository for automated deployments."""
    path: ReposGetDeployKeyRequestPath

# Operation: delete_deploy_key
class ReposDeleteDeployKeyRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    key_id: int = Field(default=..., description="The unique identifier of the deploy key to delete.")
class ReposDeleteDeployKeyRequest(StrictModel):
    """Remove a deploy key from a repository. Deploy keys are immutable, so you must delete and recreate a key to make changes."""
    path: ReposDeleteDeployKeyRequestPath

# Operation: list_labels
class IssuesListLabelsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class IssuesListLabelsForRepoRequest(StrictModel):
    """Retrieves all labels defined for a repository. Labels are used to categorize and organize issues and pull requests."""
    path: IssuesListLabelsForRepoRequestPath

# Operation: create_label
class IssuesCreateLabelRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class IssuesCreateLabelRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the label. Emoji can be added using native emoji or colon-style markup (e.g., `:strawberry:`).")
    color: str | None = Field(default=None, description="The hexadecimal color code for the label, without the leading `#`. Must be a valid hex color value.")
    description: str | None = Field(default=None, description="A short description of the label to provide additional context. Maximum length is 100 characters.")
class IssuesCreateLabelRequest(StrictModel):
    """Create a new label for a repository with a specified name and color. Labels are used to categorize and organize issues and pull requests."""
    path: IssuesCreateLabelRequestPath
    body: IssuesCreateLabelRequestBody

# Operation: get_label
class IssuesGetLabelRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    name: str = Field(default=..., description="The name of the label to retrieve. The name is not case sensitive.")
class IssuesGetLabelRequest(StrictModel):
    """Retrieve a specific label from a repository by its name. Labels are used to categorize and organize issues and pull requests."""
    path: IssuesGetLabelRequestPath

# Operation: update_label
class IssuesUpdateLabelRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    name: str = Field(default=..., description="The current name of the label to update. Case-sensitive.")
class IssuesUpdateLabelRequestBody(StrictModel):
    new_name: str | None = Field(default=None, description="The new name for the label. Supports emoji using native emoji or colon-style markup (e.g., `:strawberry:`).")
    color: str | None = Field(default=None, description="The hexadecimal color code for the label without the leading `#` character.")
    description: str | None = Field(default=None, description="A short description of the label's purpose. Maximum 100 characters.")
class IssuesUpdateLabelRequest(StrictModel):
    """Update an existing repository label by name. Modify the label's name, color, and description in a single request."""
    path: IssuesUpdateLabelRequestPath
    body: IssuesUpdateLabelRequestBody | None = None

# Operation: delete_label
class IssuesDeleteLabelRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    name: str = Field(default=..., description="The name of the label to delete. The name is not case sensitive.")
class IssuesDeleteLabelRequest(StrictModel):
    """Delete a label from a repository by name. This operation permanently removes the label and its associations with any issues or pull requests."""
    path: IssuesDeleteLabelRequestPath

# Operation: list_repository_languages
class ReposListLanguagesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListLanguagesRequest(StrictModel):
    """Retrieves the programming languages used in a repository with the number of bytes of code written in each language. Useful for understanding the technology stack and composition of a project."""
    path: ReposListLanguagesRequestPath

# Operation: get_repository_license
class LicensesGetForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class LicensesGetForRepoRequest(StrictModel):
    """Retrieve the license file contents for a repository. Returns the raw license text or HTML-rendered markup depending on the requested media type."""
    path: LicensesGetForRepoRequestPath

# Operation: sync_fork_with_upstream
class ReposMergeUpstreamRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposMergeUpstreamRequestBody(StrictModel):
    branch: str = Field(default=..., description="The name of the branch to synchronize with the upstream repository.")
class ReposMergeUpstreamRequest(StrictModel):
    """Synchronize a branch in a forked repository with the corresponding upstream branch to keep it current. This operation updates the specified branch to match the upstream repository's state."""
    path: ReposMergeUpstreamRequestPath
    body: ReposMergeUpstreamRequestBody

# Operation: merge_branch
class ReposMergeRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposMergeRequestBody(StrictModel):
    base: str = Field(default=..., description="The name of the base branch that will receive the merged changes.")
    head: str = Field(default=..., description="The head to merge into the base branch. Can be a branch name or a commit SHA1.")
    commit_message: str | None = Field(default=None, description="Optional commit message for the merge commit. If not provided, a default message will be generated automatically.")
class ReposMergeRequest(StrictModel):
    """Merge a head branch or commit into a base branch. This creates a merge commit combining the changes from both branches."""
    path: ReposMergeRequestPath
    body: ReposMergeRequestBody

# Operation: list_milestones
class IssuesListMilestonesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class IssuesListMilestonesRequestQuery(StrictModel):
    state: Literal["open", "closed", "all"] | None = Field(default=None, description="Filter milestones by their current state: open for active milestones, closed for completed ones, or all to include both.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Control the sort order of results: ascending (asc) for oldest first, or descending (desc) for newest first.")
class IssuesListMilestonesRequest(StrictModel):
    """Retrieves a list of milestones for a repository, with options to filter by state and control sort order. Useful for tracking project progress and deadlines."""
    path: IssuesListMilestonesRequestPath
    query: IssuesListMilestonesRequestQuery | None = None

# Operation: create_milestone
class IssuesCreateMilestoneRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class IssuesCreateMilestoneRequestBody(StrictModel):
    title: str = Field(default=..., description="The title of the milestone. This is the primary identifier displayed in the repository.")
    state: Literal["open", "closed"] | None = Field(default=None, description="The state of the milestone, indicating whether it is actively being worked on or completed.")
    description: str | None = Field(default=None, description="A description of the milestone providing additional context about its goals and scope.")
    due_on: str | None = Field(default=None, description="The milestone due date in ISO 8601 format, specifying when the milestone should be completed.", json_schema_extra={'format': 'date-time'})
class IssuesCreateMilestoneRequest(StrictModel):
    """Creates a new milestone in a repository to track progress toward project goals. Milestones help organize issues and pull requests by target dates and objectives."""
    path: IssuesCreateMilestoneRequestPath
    body: IssuesCreateMilestoneRequestBody

# Operation: get_milestone
class IssuesGetMilestoneRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    milestone_number: int = Field(default=..., description="The numeric identifier that uniquely identifies the milestone within the repository.")
class IssuesGetMilestoneRequest(StrictModel):
    """Retrieve a specific milestone from a repository using its milestone number. This operation returns detailed information about the milestone including its title, description, state, and associated dates."""
    path: IssuesGetMilestoneRequestPath

# Operation: update_milestone
class IssuesUpdateMilestoneRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    milestone_number: int = Field(default=..., description="The number that identifies the milestone.")
class IssuesUpdateMilestoneRequestBody(StrictModel):
    state: Literal["open", "closed"] | None = Field(default=None, description="The state of the milestone. Set to `open` to activate the milestone or `closed` to mark it as complete.")
    description: str | None = Field(default=None, description="A description of the milestone. Use this to provide context or details about the milestone's purpose and goals.")
    due_on: str | None = Field(default=None, description="The milestone due date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Set this to establish a target completion date for the milestone.", json_schema_extra={'format': 'date-time'})
class IssuesUpdateMilestoneRequest(StrictModel):
    """Update an existing milestone in a repository. Modify the milestone's state, description, and due date as needed."""
    path: IssuesUpdateMilestoneRequestPath
    body: IssuesUpdateMilestoneRequestBody | None = None

# Operation: delete_milestone
class IssuesDeleteMilestoneRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    milestone_number: int = Field(default=..., description="The numeric identifier of the milestone to delete.")
class IssuesDeleteMilestoneRequest(StrictModel):
    """Permanently delete a milestone from a repository using its milestone number. This action cannot be undone."""
    path: IssuesDeleteMilestoneRequestPath

# Operation: list_milestone_labels
class IssuesListLabelsForMilestoneRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    milestone_number: int = Field(default=..., description="The numeric identifier of the milestone.")
class IssuesListLabelsForMilestoneRequest(StrictModel):
    """Retrieves all labels associated with issues in a specific milestone. Useful for understanding the categorization and tagging of work items within a milestone."""
    path: IssuesListLabelsForMilestoneRequestPath

# Operation: list_notifications_repository
class ActivityListRepoNotificationsForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActivityListRepoNotificationsForAuthenticatedUserRequestQuery(StrictModel):
    all_: bool | None = Field(default=None, validation_alias="all", serialization_alias="all", description="If true, include notifications marked as read. By default, only unread notifications are returned.")
    participating: bool | None = Field(default=None, description="If true, show only notifications where the user is directly participating or mentioned. By default, all notifications are returned.")
    since: str | None = Field(default=None, description="Only return notifications that were last updated after this timestamp. Specify in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class ActivityListRepoNotificationsForAuthenticatedUserRequest(StrictModel):
    """Retrieve all notifications for the authenticated user in a specific repository. Filter by read status, participation level, and update time to focus on relevant notifications."""
    path: ActivityListRepoNotificationsForAuthenticatedUserRequestPath
    query: ActivityListRepoNotificationsForAuthenticatedUserRequestQuery | None = None

# Operation: mark_repository_notifications_as_read
class ActivityMarkRepoNotificationsAsReadRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActivityMarkRepoNotificationsAsReadRequestBody(StrictModel):
    last_read_at: str | None = Field(default=None, description="The timestamp marking the last point notifications were checked. Notifications updated after this time will not be marked as read. If omitted, all notifications are marked as read. Must be in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class ActivityMarkRepoNotificationsAsReadRequest(StrictModel):
    """Mark all notifications in a repository as read for the authenticated user. For large notification volumes, this operation may run asynchronously and return a 202 Accepted status."""
    path: ActivityMarkRepoNotificationsAsReadRequestPath
    body: ActivityMarkRepoNotificationsAsReadRequestBody | None = None

# Operation: get_pages_site
class ReposGetPagesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetPagesRequest(StrictModel):
    """Retrieve information about a GitHub Pages site for a repository. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: ReposGetPagesRequestPath

# Operation: enable_pages_site
class ReposCreatePagesSiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposCreatePagesSiteRequestBodySource(StrictModel):
    branch: str = Field(default=..., validation_alias="branch", serialization_alias="branch", description="The repository branch that contains the source files for publishing the Pages site.")
class ReposCreatePagesSiteRequestBody(StrictModel):
    build_type: Literal["legacy", "workflow"] | None = Field(default=None, description="The build process for the Pages site. Use 'legacy' for traditional Jekyll builds or 'workflow' for GitHub Actions-based builds.")
    source: ReposCreatePagesSiteRequestBodySource
class ReposCreatePagesSiteRequest(StrictModel):
    """Enable and configure a GitHub Pages site for a repository. Requires repository administrator, maintainer, or 'manage GitHub Pages settings' permission."""
    path: ReposCreatePagesSiteRequestPath
    body: ReposCreatePagesSiteRequestBody

# Operation: configure_pages_site
class ReposUpdateInformationAboutPagesSiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ReposUpdateInformationAboutPagesSiteRequestBody(StrictModel):
    cname: str | None = Field(default=None, description="A custom domain for the GitHub Pages site. Pass null to remove an existing custom domain.")
    https_enforced: bool | None = Field(default=None, description="Whether HTTPS should be enforced for the GitHub Pages site.")
    build_type: Literal["legacy", "workflow"] | None = Field(default=None, description="The build process for the GitHub Pages site. Use 'workflow' for custom GitHub Actions builds or 'legacy' for automatic builds on branch pushes.")
class ReposUpdateInformationAboutPagesSiteRequest(StrictModel):
    """Configure GitHub Pages settings for a repository, including custom domain and HTTPS enforcement. Requires repository administrator or maintainer permissions."""
    path: ReposUpdateInformationAboutPagesSiteRequestPath
    body: ReposUpdateInformationAboutPagesSiteRequestBody | None = None

# Operation: delete_pages_site
class ReposDeletePagesSiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposDeletePagesSiteRequest(StrictModel):
    """Delete a GitHub Pages site for a repository. The authenticated user must have repository administrator, maintainer, or 'manage GitHub Pages settings' permissions."""
    path: ReposDeletePagesSiteRequestPath

# Operation: list_pages_builds
class ReposListPagesBuildsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListPagesBuildsRequest(StrictModel):
    """Retrieve a list of all builds for a GitHub Pages site associated with a repository. Requires `repo` scope for OAuth apps and personal access tokens."""
    path: ReposListPagesBuildsRequestPath

# Operation: trigger_pages_build
class ReposRequestPagesBuildRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposRequestPagesBuildRequest(StrictModel):
    """Request a GitHub Pages build from the latest revision on the default branch. This manually triggers a site build without requiring a new commit, useful for diagnosing build warnings and failures."""
    path: ReposRequestPagesBuildRequestPath

# Operation: get_latest_pages_build
class ReposGetLatestPagesBuildRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ReposGetLatestPagesBuildRequest(StrictModel):
    """Retrieves information about the most recent build of a GitHub Pages site for a repository. Requires `repo` scope authorization."""
    path: ReposGetLatestPagesBuildRequestPath

# Operation: get_pages_build
class ReposGetPagesBuildRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    build_id: int = Field(default=..., description="The unique identifier of the GitHub Pages build to retrieve.")
class ReposGetPagesBuildRequest(StrictModel):
    """Retrieve detailed information about a specific GitHub Pages build for a repository. Requires `repo` scope for OAuth app tokens and personal access tokens (classic)."""
    path: ReposGetPagesBuildRequestPath

# Operation: deploy_pages
class ReposCreatePagesDeploymentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposCreatePagesDeploymentRequestBody(StrictModel):
    environment: str | None = Field(default=None, description="The target environment for this GitHub Pages deployment.")
    pages_build_version: str = Field(default=..., description="A unique string that represents the version of the build for this deployment.")
    oidc_token: str = Field(default=..., description="The OIDC token issued by GitHub Actions certifying the origin of the deployment.")
    artifact_url: str | None = Field(default=None, description="The URL of an artifact that contains the .zip or .tar of static assets to deploy. The artifact belongs to the repository. Either `artifact_id` or `artifact_url` are required.")
class ReposCreatePagesDeploymentRequest(StrictModel):
    """Create a GitHub Pages deployment for a repository. The authenticated user must have write permission to the repository."""
    path: ReposCreatePagesDeploymentRequestPath
    body: ReposCreatePagesDeploymentRequestBody

# Operation: get_pages_deployment
class ReposGetPagesDeploymentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pages_deployment_id: str = Field(default=..., description="The ID of the Pages deployment. You can also provide the commit SHA of the deployment.")
class ReposGetPagesDeploymentRequest(StrictModel):
    """Retrieve the current status of a GitHub Pages deployment. The authenticated user must have read permission for the GitHub Pages site."""
    path: ReposGetPagesDeploymentRequestPath

# Operation: cancel_pages_deployment
class ReposCancelPagesDeploymentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pages_deployment_id: str = Field(default=..., description="The ID of the Pages deployment. You can also provide the commit SHA of the deployment.")
class ReposCancelPagesDeploymentRequest(StrictModel):
    """Cancel an active GitHub Pages deployment. The authenticated user must have write permissions for the GitHub Pages site."""
    path: ReposCancelPagesDeploymentRequestPath

# Operation: check_private_vulnerability_reporting
class ReposCheckPrivateVulnerabilityReportingRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposCheckPrivateVulnerabilityReportingRequest(StrictModel):
    """Check whether private vulnerability reporting is enabled for a repository. This setting allows security researchers to report vulnerabilities privately before public disclosure."""
    path: ReposCheckPrivateVulnerabilityReportingRequestPath

# Operation: list_repository_custom_properties
class ReposCustomPropertiesForReposGetRepositoryValuesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposCustomPropertiesForReposGetRepositoryValuesRequest(StrictModel):
    """Retrieve all custom property values set for a repository. This endpoint allows users with read access to view the complete set of custom properties and their values configured for the repository."""
    path: ReposCustomPropertiesForReposGetRepositoryValuesRequestPath

# Operation: set_repository_custom_properties
class ReposCustomPropertiesForReposCreateOrUpdateRepositoryValuesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the .git extension. Case-insensitive.")
class ReposCustomPropertiesForReposCreateOrUpdateRepositoryValuesRequestBody(StrictModel):
    properties: list[CustomPropertyValue] = Field(default=..., description="A list of custom property names and their associated values to apply to the repository. Each property in the list will be created or updated with the specified value.")
class ReposCustomPropertiesForReposCreateOrUpdateRepositoryValuesRequest(StrictModel):
    """Create or update custom property values for a repository. Set property values to null to remove them from the repository."""
    path: ReposCustomPropertiesForReposCreateOrUpdateRepositoryValuesRequestPath
    body: ReposCustomPropertiesForReposCreateOrUpdateRepositoryValuesRequestBody

# Operation: list_pull_requests
class PullsListRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class PullsListRequestQuery(StrictModel):
    state: Literal["open", "closed", "all"] | None = Field(default=None, description="Filter pull requests by their state.")
    head: str | None = Field(default=None, description="Filter pull requests by the head branch. Specify in the format `user:ref-name` or `organization:ref-name` to match the source branch and owner.")
    base: str | None = Field(default=None, description="Filter pull requests by the base branch name. Matches the target branch where pull requests are being merged.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort direction for results. Defaults to descending when sorting by creation date or when no sort is specified.")
class PullsListRequest(StrictModel):
    """Retrieve pull requests from a repository with filtering and sorting options. Supports draft pull requests depending on your GitHub plan and repository visibility."""
    path: PullsListRequestPath
    query: PullsListRequestQuery | None = None

# Operation: create_pull_request
class PullsCreateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class PullsCreateRequestBody(StrictModel):
    head: str = Field(default=..., description="The branch containing your changes. For cross-repository PRs in the same network, use the format `username:branch` to namespace the head branch.")
    head_repo: str | None = Field(default=None, description="The repository where the pull request changes were made. Required for cross-repository PRs when both repositories are owned by the same organization.", json_schema_extra={'format': 'repo.nwo'})
    base: str = Field(default=..., description="The target branch where changes will be merged. Must be an existing branch on the current repository.")
    body: str | None = Field(default=None, description="The pull request description in markdown format.")
    maintainer_can_modify: bool | None = Field(default=None, description="Whether maintainers can modify the pull request branch. Allows maintainers to push commits to your PR branch.")
    draft: bool | None = Field(default=None, description="Whether to create the pull request as a draft. Draft PRs can be marked ready for review later.")
    title: str | None = Field(default=None, description="The title of the new pull request. Required unless `issue` is specified.")
class PullsCreateRequest(StrictModel):
    """Create a pull request to propose changes from a head branch into a base branch. Supports draft pull requests and cross-repository PRs within the same network."""
    path: PullsCreateRequestPath
    body: PullsCreateRequestBody

# Operation: list_pull_request_review_comments_for_repo
class PullsListReviewCommentsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class PullsListReviewCommentsForRepoRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort results. Only applies when used with a sort parameter.")
    since: str | None = Field(default=None, description="Only show results that were last updated after the given time. Specify as an ISO 8601 timestamp.", json_schema_extra={'format': 'date-time'})
class PullsListReviewCommentsForRepoRequest(StrictModel):
    """Lists review comments for all pull requests in a repository, sorted by ID in ascending order by default. Supports multiple content formats including raw markdown, plain text, HTML, or combined representations."""
    path: PullsListReviewCommentsForRepoRequestPath
    query: PullsListReviewCommentsForRepoRequestQuery | None = None

# Operation: get_pull_request_review_comment
class PullsGetReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the review comment to retrieve.", json_schema_extra={'format': 'int64'})
class PullsGetReviewCommentRequest(StrictModel):
    """Retrieve a specific review comment from a pull request. Supports multiple content formats including raw markdown, plain text, HTML, or a combination of all three representations."""
    path: PullsGetReviewCommentRequestPath

# Operation: update_pull_request_review_comment
class PullsUpdateReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the review comment to update.", json_schema_extra={'format': 'int64'})
class PullsUpdateReviewCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The updated text content for the review comment. Supports markdown formatting.")
class PullsUpdateReviewCommentRequest(StrictModel):
    """Update the text content of a review comment on a pull request. Supports multiple response formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: PullsUpdateReviewCommentRequestPath
    body: PullsUpdateReviewCommentRequestBody

# Operation: delete_pull_request_review_comment
class PullsDeleteReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the review comment to delete.", json_schema_extra={'format': 'int64'})
class PullsDeleteReviewCommentRequest(StrictModel):
    """Delete a review comment from a pull request. This permanently removes the specified comment and cannot be undone."""
    path: PullsDeleteReviewCommentRequestPath

# Operation: list_pull_request_review_comment_reactions
class ReactionsListForPullRequestReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the pull request review comment.", json_schema_extra={'format': 'int64'})
class ReactionsListForPullRequestReviewCommentRequestQuery(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] | None = Field(default=None, description="Filter results to show only a specific reaction type. Omit to list all reactions to the pull request review comment.")
class ReactionsListForPullRequestReviewCommentRequest(StrictModel):
    """List all reactions or filter by a specific reaction type for a pull request review comment. Reactions indicate how reviewers feel about specific code feedback."""
    path: ReactionsListForPullRequestReviewCommentRequestPath
    query: ReactionsListForPullRequestReviewCommentRequestQuery | None = None

# Operation: add_reaction_to_pull_request_comment
class ReactionsCreateForPullRequestReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the pull request review comment.", json_schema_extra={'format': 'int64'})
class ReactionsCreateForPullRequestReviewCommentRequestBody(StrictModel):
    content: Literal["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"] = Field(default=..., description="The emoji reaction type to add to the comment.")
class ReactionsCreateForPullRequestReviewCommentRequest(StrictModel):
    """Add an emoji reaction to a pull request review comment. Returns HTTP 200 if the reaction type was already added by the authenticated user."""
    path: ReactionsCreateForPullRequestReviewCommentRequestPath
    body: ReactionsCreateForPullRequestReviewCommentRequestBody

# Operation: remove_pull_request_comment_reaction
class ReactionsDeleteForPullRequestCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    comment_id: int = Field(default=..., description="The unique identifier of the pull request review comment.", json_schema_extra={'format': 'int64'})
    reaction_id: int = Field(default=..., description="The unique identifier of the reaction to remove.")
class ReactionsDeleteForPullRequestCommentRequest(StrictModel):
    """Remove a reaction from a pull request review comment. This operation deletes a specific reaction (emoji) that was previously added to a comment."""
    path: ReactionsDeleteForPullRequestCommentRequestPath

# Operation: get_pull_request
class PullsGetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
class PullsGetRequest(StrictModel):
    """Retrieve detailed information about a specific pull request by its number. Returns comprehensive PR metadata including merge status, commit information, and body content in various formats."""
    path: PullsGetRequestPath

# Operation: update_pull_request
class PullsUpdateRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
class PullsUpdateRequestBody(StrictModel):
    body: str | None = Field(default=None, description="The contents of the pull request body. Supports markdown formatting.")
    state: Literal["open", "closed"] | None = Field(default=None, description="The desired state of the pull request.")
    base: str | None = Field(default=None, description="The name of the branch you want your changes pulled into. This must be an existing branch on the current repository and cannot point to another repository.")
    maintainer_can_modify: bool | None = Field(default=None, description="Indicates whether maintainers can modify the pull request branch.")
class PullsUpdateRequest(StrictModel):
    """Update an existing pull request including its title, description, state, and base branch. Supports draft pull requests and requires write access to the head or source branch."""
    path: PullsUpdateRequestPath
    body: PullsUpdateRequestBody | None = None

# Operation: create_codespace_from_pull_request
class CodespacesCreateWithPrForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request number that identifies which PR to create the codespace from.")
class CodespacesCreateWithPrForAuthenticatedUserRequestBody(StrictModel):
    geo: Literal["EuropeWest", "SoutheastAsia", "UsEast", "UsWest"] | None = Field(default=None, description="The geographic region where the codespace will be hosted. If not specified, the region is automatically assigned based on the requester's IP address.")
    machine: str | None = Field(default=None, description="The machine type to use for this codespace (e.g., standard-2core, premium-4core).")
    devcontainer_path: str | None = Field(default=None, description="Path to the devcontainer.json configuration file within the repository to use for this codespace.")
    multi_repo_permissions_opt_out: bool | None = Field(default=None, description="Whether to opt out of authorizing permissions requested in the devcontainer.json configuration.")
    working_directory: str | None = Field(default=None, description="The working directory path to open when the codespace starts.")
    idle_timeout_minutes: int | None = Field(default=None, description="Time in minutes before the codespace automatically stops due to inactivity.")
    display_name: str | None = Field(default=None, description="A human-readable display name for this codespace.")
    retention_period_minutes: int | None = Field(default=None, description="Duration in minutes after the codespace becomes idle before it is automatically deleted. Must be between 0 and 43200 (30 days).")
class CodespacesCreateWithPrForAuthenticatedUserRequest(StrictModel):
    """Creates a codespace owned by the authenticated user for a specified pull request. Requires the `codespace` OAuth scope or personal access token (classic) scope."""
    path: CodespacesCreateWithPrForAuthenticatedUserRequestPath
    body: CodespacesCreateWithPrForAuthenticatedUserRequestBody | None = None

# Operation: list_pull_request_review_comments
class PullsListReviewCommentsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request identifier number.")
class PullsListReviewCommentsRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The sort direction for results. Only applies when used with a sort parameter.")
    since: str | None = Field(default=None, description="Filter results to show only comments updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class PullsListReviewCommentsRequest(StrictModel):
    """Retrieve all review comments for a pull request, sorted by ID in ascending order by default. Supports multiple content formats including raw markdown, plain text, HTML, or combined representations."""
    path: PullsListReviewCommentsRequestPath
    query: PullsListReviewCommentsRequestQuery | None = None

# Operation: create_pull_request_review_comment
class PullsCreateReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
class PullsCreateReviewCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The text content of the review comment. Supports markdown formatting.")
    commit_id: str = Field(default=..., description="The SHA of the commit to which the comment applies. Using a non-latest commit SHA may cause the comment to become outdated if subsequent commits modify the commented line.")
    path: str = Field(default=..., description="The relative path to the file being commented on within the repository.")
    side: Literal["LEFT", "RIGHT"] | None = Field(default=None, description="In a split diff view, indicates which side of the diff the comment targets. Use LEFT for deletions (shown in red) or RIGHT for additions (shown in green) and unchanged context lines (shown in white).")
    start_line: int | None = Field(default=None, description="The first line number in the pull request diff that a multi-line comment applies to. Required for multi-line comments unless replying to an existing review comment.")
    in_reply_to: int | None = Field(default=None, description="The ID of an existing review comment to reply to. When specified, all other request body parameters except `body` are ignored.")
    subject_type: Literal["line", "file"] | None = Field(default=None, description="The scope level at which the comment is targeted, either at a specific line or for the entire file.")
    line: int | None = Field(default=None, description="**Required unless using `subject_type:file`**. The line of the blob in the pull request diff that the comment applies to. For a multi-line comment, the last line of the range that your comment applies to.")
    position: int | None = Field(default=None, description="**This parameter is closing down. Use `line` instead**. The position in the diff where you want to add a review comment. Note this value is not the same as the line number in the file. The position value equals the number of lines down from the first \"@@\" hunk header in the file you want to add a comment. The line just below the \"@@\" line is position 1, the next line is position 2, and so on. The position in the diff continues to increase through lines of whitespace and additional hunks until the beginning of a new file.")
class PullsCreateReviewCommentRequest(StrictModel):
    """Create a review comment on a specific line or range of lines in a pull request diff. This enables targeted feedback on code changes and triggers notifications to relevant participants."""
    path: PullsCreateReviewCommentRequestPath
    body: PullsCreateReviewCommentRequestBody

# Operation: reply_to_review_comment
class PullsCreateReplyForReviewCommentRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
    comment_id: int = Field(default=..., description="The unique identifier of the top-level review comment to reply to.", json_schema_extra={'format': 'int64'})
class PullsCreateReplyForReviewCommentRequestBody(StrictModel):
    body: str = Field(default=..., description="The text content of the reply, formatted as markdown.")
class PullsCreateReplyForReviewCommentRequest(StrictModel):
    """Create a reply to a top-level review comment on a pull request. Replies to replies are not supported."""
    path: PullsCreateReplyForReviewCommentRequestPath
    body: PullsCreateReplyForReviewCommentRequestBody

# Operation: list_pull_request_commits
class PullsListCommitsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request identifier number.")
class PullsListCommitsRequest(StrictModel):
    """Retrieve the commits included in a pull request, with a maximum of 250 commits returned. For pull requests with more than 250 commits, use the general commits list endpoint instead."""
    path: PullsListCommitsRequestPath

# Operation: list_pull_request_files
class PullsListFilesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The pull request number that identifies which pull request's files to retrieve.")
class PullsListFilesRequest(StrictModel):
    """Lists all files changed in a specified pull request. Returns up to 3000 files with 30 files per page by default."""
    path: PullsListFilesRequestPath

# Operation: check_pull_request_merged
class PullsCheckIfMergedRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request identifier number.")
class PullsCheckIfMergedRequest(StrictModel):
    """Determines whether a pull request has been merged into its base branch. The HTTP status code indicates the merge status; a 204 response means merged, 404 means not merged."""
    path: PullsCheckIfMergedRequestPath

# Operation: merge_pull_request
class PullsMergeRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    pull_number: int = Field(default=..., description="The numeric identifier of the pull request to merge.")
class PullsMergeRequestBody(StrictModel):
    commit_title: str | None = Field(default=None, description="Custom title for the automatic commit message created by the merge.")
    commit_message: str | None = Field(default=None, description="Additional details to append to the automatic commit message.")
    sha: str | None = Field(default=None, description="The commit SHA that the pull request head must match to allow the merge. Used to prevent merging if the branch has been updated since the last check.")
    merge_method: Literal["merge", "squash", "rebase"] | None = Field(default=None, description="The merge strategy to use when combining the pull request with the base branch.")
class PullsMergeRequest(StrictModel):
    """Merge a pull request into its base branch. This operation triggers notifications and is subject to secondary rate limiting; use appropriate delays when merging multiple pull requests."""
    path: PullsMergeRequestPath
    body: PullsMergeRequestBody | None = None

# Operation: list_pull_request_requested_reviewers
class PullsListRequestedReviewersRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request identifier number.")
class PullsListRequestedReviewersRequest(StrictModel):
    """Retrieve all users and teams whose review has been requested for a pull request. Requested reviewers are excluded once they submit a review."""
    path: PullsListRequestedReviewersRequestPath

# Operation: request_pull_request_reviewers
class PullsRequestReviewersRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
class PullsRequestReviewersRequestBody(StrictModel):
    reviewers: list[str] | None = Field(default=None, description="An array of user login names to request as reviewers. Order is not significant.")
    team_reviewers: list[str] | None = Field(default=None, description="An array of team slugs to request as reviewers. Order is not significant.")
class PullsRequestReviewersRequest(StrictModel):
    """Request code reviews for a pull request from specified users and/or teams. This operation triggers notifications and is subject to secondary rate limiting; use judiciously to avoid throttling."""
    path: PullsRequestReviewersRequestPath
    body: PullsRequestReviewersRequestBody | None = None

# Operation: remove_pull_request_reviewers
class PullsRemoveRequestedReviewersRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request number that identifies which pull request to modify.")
class PullsRemoveRequestedReviewersRequestBody(StrictModel):
    reviewers: list[str] = Field(default=..., description="An array of user login names to remove from the review request. Order is not significant.")
    team_reviewers: list[str] | None = Field(default=None, description="An array of team slugs to remove from the review request. Order is not significant.")
class PullsRemoveRequestedReviewersRequest(StrictModel):
    """Remove review requests from a pull request by specifying users and/or teams to be removed. This operation allows you to withdraw review requests that were previously assigned."""
    path: PullsRemoveRequestedReviewersRequestPath
    body: PullsRemoveRequestedReviewersRequestBody

# Operation: list_pull_request_reviews
class PullsListReviewsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    pull_number: int = Field(default=..., description="The numeric identifier of the pull request to retrieve reviews for.")
class PullsListReviewsRequest(StrictModel):
    """Retrieve all reviews for a specified pull request in chronological order. Supports multiple content formats including raw markdown, plain text, HTML, or combined representations."""
    path: PullsListReviewsRequestPath

# Operation: create_pull_request_review
class PullsCreateReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
class PullsCreateReviewRequestBody(StrictModel):
    commit_id: str | None = Field(default=None, description="The SHA of the commit that needs a review. If not specified, defaults to the most recent commit in the pull request. Using an outdated commit SHA may render review comments obsolete if subsequent commits modify the reviewed lines.")
    body: str | None = Field(default=None, description="The body text of the pull request review. Required when the `event` parameter is set to `REQUEST_CHANGES` or `COMMENT`.")
    event: Literal["APPROVE", "REQUEST_CHANGES", "COMMENT"] | None = Field(default=None, description="The review action you want to perform. The review actions include: `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`. By leaving this blank, you set the review action state to `PENDING`, which means you will need to [submit the pull request review](https://docs.github.com/rest/pulls/reviews#submit-a-review-for-a-pull-request) when you are ready.")
    comments: list[dict] | None = Field(default=None, description="Use the following table to specify the location, destination, and contents of the draft review comment.")
class PullsCreateReviewRequest(StrictModel):
    """Create a review on a pull request, optionally with comments on specific lines in the diff. Reviews can be submitted immediately or saved as pending for later submission."""
    path: PullsCreateReviewRequestPath
    body: PullsCreateReviewRequestBody | None = None

# Operation: get_pull_request_review
class PullsGetReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
    review_id: int = Field(default=..., description="The unique identifier of the review to retrieve.")
class PullsGetReviewRequest(StrictModel):
    """Retrieve a specific review for a pull request by its review ID. Supports multiple content formats including raw markdown, plain text, HTML, or a combination of all three representations."""
    path: PullsGetReviewRequestPath

# Operation: update_pull_request_review
class PullsUpdateReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
    review_id: int = Field(default=..., description="The unique identifier of the review to update.")
class PullsUpdateReviewRequestBody(StrictModel):
    body: str = Field(default=..., description="The body text of the pull request review. Supports markdown formatting.")
class PullsUpdateReviewRequest(StrictModel):
    """Update the body text of an existing pull request review. This endpoint allows you to modify the summary comment of a review that has already been submitted."""
    path: PullsUpdateReviewRequestPath
    body: PullsUpdateReviewRequestBody

# Operation: delete_pending_review
class PullsDeletePendingReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
    review_id: int = Field(default=..., description="The unique identifier of the review to delete.")
class PullsDeletePendingReviewRequest(StrictModel):
    """Delete a pending pull request review that has not yet been submitted. Only unsubmitted reviews can be deleted; submitted reviews are permanent and cannot be removed."""
    path: PullsDeletePendingReviewRequestPath

# Operation: list_review_comments
class PullsListCommentsForReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request number that contains the review.")
    review_id: int = Field(default=..., description="The unique identifier of the review whose comments should be listed.")
class PullsListCommentsForReviewRequest(StrictModel):
    """Retrieve all comments made during a specific pull request review. Supports multiple content formats including raw markdown, plain text, HTML, or a combination of all three."""
    path: PullsListCommentsForReviewRequestPath

# Operation: dismiss_pull_request_review
class PullsDismissReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
    review_id: int = Field(default=..., description="The unique identifier of the review to dismiss.")
class PullsDismissReviewRequestBody(StrictModel):
    message: str = Field(default=..., description="The message explaining the reason for dismissing the review.")
class PullsDismissReviewRequest(StrictModel):
    """Dismiss a review on a pull request with an optional message. Requires repository administrator permissions or explicit dismissal rights on protected branches."""
    path: PullsDismissReviewRequestPath
    body: PullsDismissReviewRequestBody

# Operation: submit_pull_request_review
class PullsSubmitReviewRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    pull_number: int = Field(default=..., description="The number that identifies the pull request.")
    review_id: int = Field(default=..., description="The unique identifier of the review to submit.")
class PullsSubmitReviewRequestBody(StrictModel):
    body: str | None = Field(default=None, description="The body text of the pull request review. Optional; can be omitted if the review action is `APPROVE` or `REQUEST_CHANGES`.")
    event: Literal["APPROVE", "REQUEST_CHANGES", "COMMENT"] = Field(default=..., description="The review action to perform on the pull request. Must be one of: `APPROVE` (approve the changes), `REQUEST_CHANGES` (request modifications), or `COMMENT` (provide feedback without approval).")
class PullsSubmitReviewRequest(StrictModel):
    """Submit a pending review for a pull request with an approval, request for changes, or comment action. The review must be finalized with one of the three review actions; submitting without an action will result in an error."""
    path: PullsSubmitReviewRequestPath
    body: PullsSubmitReviewRequestBody

# Operation: sync_pull_request_branch
class PullsUpdateBranchRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
    pull_number: int = Field(default=..., description="The pull request identifier number.")
class PullsUpdateBranchRequest(StrictModel):
    """Synchronize a pull request branch with the latest changes from its base branch by merging the upstream HEAD. Requires write permissions to the head repository when using a GitHub App."""
    path: PullsUpdateBranchRequestPath

# Operation: get_repository_readme
class ReposGetReadmeRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposGetReadmeRequest(StrictModel):
    """Retrieves the preferred README file for a repository. Supports both raw and HTML-rendered formats via custom media types."""
    path: ReposGetReadmeRequestPath

# Operation: get_readme
class ReposGetReadmeInDirectoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    dir_: str = Field(default=..., validation_alias="dir", serialization_alias="dir", description="The directory path within the repository to search for the README file.")
class ReposGetReadmeInDirectoryRequest(StrictModel):
    """Retrieves the README file from a specified directory within a repository. Supports both raw text and rendered HTML formats."""
    path: ReposGetReadmeInDirectoryRequestPath

# Operation: list_releases
class ReposListReleasesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListReleasesRequest(StrictModel):
    """Retrieve a list of published releases for a repository. Draft releases are only visible to users with push access. Regular Git tags without associated releases are not included; use the Repository Tags API for those."""
    path: ReposListReleasesRequestPath

# Operation: create_release
class ReposCreateReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposCreateReleaseRequestBody(StrictModel):
    tag_name: str = Field(default=..., description="The name of the tag to create or use for this release.")
    target_commitish: str | None = Field(default=None, description="The Git commit, branch, or tag from which to create the release tag. Ignored if the tag already exists. Defaults to the repository's default branch.")
    body: str | None = Field(default=None, description="Descriptive text about the release contents and changes.")
    draft: bool | None = Field(default=None, description="Whether to create an unpublished draft release or a published release.")
    prerelease: bool | None = Field(default=None, description="Whether to mark this release as a prerelease or a full release.")
    discussion_category_name: str | None = Field(default=None, description="Category name for an automatically created discussion linked to this release. The category must already exist in the repository.")
    generate_release_notes: bool | None = Field(default=None, description="Whether to automatically generate release name and body from commit history. If a name is provided, it will be used; if body is provided, it will be prepended to auto-generated notes.")
    make_latest: Literal["true", "false", "legacy"] | None = Field(default=None, description="Whether to set this release as the latest for the repository. Drafts and prereleases cannot be marked as latest. Use 'legacy' to determine latest by creation date and semantic version.")
    name: str | None = Field(default=None, description="The name of the release.")
class ReposCreateReleaseRequest(StrictModel):
    """Create a new release for a repository. Users with push access can publish releases, which trigger notifications. Be aware of secondary rate limits when creating releases in rapid succession."""
    path: ReposCreateReleaseRequestPath
    body: ReposCreateReleaseRequestBody

# Operation: download_release_asset
class ReposGetReleaseAssetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the .git extension. The name is not case sensitive.")
    asset_id: int = Field(default=..., description="The unique identifier of the asset to retrieve.")
class ReposGetReleaseAssetRequest(StrictModel):
    """Retrieve metadata and download URL for a specific release asset. Use the browser_download_url for direct downloads or set Accept header to application/octet-stream to stream the binary content directly."""
    path: ReposGetReleaseAssetRequestPath

# Operation: update_release_asset
class ReposUpdateReleaseAssetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    asset_id: int = Field(default=..., description="The unique identifier of the asset to update.")
class ReposUpdateReleaseAssetRequestBody(StrictModel):
    label: str | None = Field(default=None, description="An alternate short description of the asset, displayed in place of the filename.")
    state: str | None = Field(default=None, description="The state of the asset.")
class ReposUpdateReleaseAssetRequest(StrictModel):
    """Update metadata for a release asset in a repository. Users with push access can modify the asset's label and state."""
    path: ReposUpdateReleaseAssetRequestPath
    body: ReposUpdateReleaseAssetRequestBody | None = None

# Operation: delete_release_asset
class ReposDeleteReleaseAssetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    asset_id: int = Field(default=..., description="The unique identifier of the asset to delete.")
class ReposDeleteReleaseAssetRequest(StrictModel):
    """Delete a specific asset from a release. This permanently removes the asset file from the release."""
    path: ReposDeleteReleaseAssetRequestPath

# Operation: generate_release_notes
class ReposGenerateReleaseNotesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGenerateReleaseNotesRequestBody(StrictModel):
    tag_name: str = Field(default=..., description="The tag name for the release. Can be an existing tag or a new one to be created.")
    target_commitish: str | None = Field(default=None, description="The commitish value (branch, commit SHA, or tag) that will be the target for the release's tag. Required only if the tag_name does not reference an existing tag; ignored if the tag already exists.")
    previous_tag_name: str | None = Field(default=None, description="The name of the previous tag to use as the starting point for release notes. Use this to manually specify the range of changes to include in the release notes.")
    configuration_file_path: str | None = Field(default=None, description="Path to a repository file containing release notes configuration settings. If not specified, defaults to `.github/release.yml` or `.github/release.yaml`, falling back to default configuration if neither exists.")
class ReposGenerateReleaseNotesRequest(StrictModel):
    """Generate release notes content including a name and markdown-formatted body describing changes and contributors for a release. The generated notes are temporary and intended for use when creating a new release."""
    path: ReposGenerateReleaseNotesRequestPath
    body: ReposGenerateReleaseNotesRequestBody

# Operation: get_latest_release
class ReposGetLatestReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetLatestReleaseRequest(StrictModel):
    """Retrieve the latest published release for a repository. Returns the most recent non-prerelease, non-draft release, sorted by creation date of the associated commit."""
    path: ReposGetLatestReleaseRequestPath

# Operation: get_release_by_tag
class ReposGetReleaseByTagRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
    tag: str = Field(default=..., description="The tag name identifying the release to retrieve.")
class ReposGetReleaseByTagRequest(StrictModel):
    """Retrieve a published release by its tag name. Returns detailed information about the release including assets, author, and metadata."""
    path: ReposGetReleaseByTagRequestPath

# Operation: get_release
class ReposGetReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release to retrieve.")
class ReposGetReleaseRequest(StrictModel):
    """Retrieve a public release by its unique identifier. Returns release metadata including an upload_url hypermedia resource for managing release assets."""
    path: ReposGetReleaseRequestPath

# Operation: update_release
class ReposUpdateReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release to update.")
class ReposUpdateReleaseRequestBody(StrictModel):
    tag_name: str | None = Field(default=None, description="The name of the tag associated with this release.")
    target_commitish: str | None = Field(default=None, description="The commitish value that determines where the Git tag is created from. Can be any branch or commit SHA. Unused if the Git tag already exists. Defaults to the repository's default branch.")
    body: str | None = Field(default=None, description="Text describing the contents of the tag.")
    draft: bool | None = Field(default=None, description="Set to `true` to mark the release as a draft, or `false` to publish it.")
    prerelease: bool | None = Field(default=None, description="Set to `true` to identify the release as a prerelease, or `false` to identify it as a full release.")
    make_latest: Literal["true", "false", "legacy"] | None = Field(default=None, description="Specifies whether this release should be set as the latest release for the repository. Drafts and prereleases cannot be set as latest. Use `legacy` to determine the latest release based on creation date and semantic version.")
    discussion_category_name: str | None = Field(default=None, description="Category name for creating and linking a discussion to this release. The category must already exist in the repository. Ignored if a discussion is already linked to the release.")
class ReposUpdateReleaseRequest(StrictModel):
    """Update an existing release in a repository. Users with push access can modify release details including tag name, description, draft status, and prerelease designation."""
    path: ReposUpdateReleaseRequestPath
    body: ReposUpdateReleaseRequestBody | None = None

# Operation: delete_release
class ReposDeleteReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release to delete.")
class ReposDeleteReleaseRequest(StrictModel):
    """Delete a release from a repository. Only users with push access to the repository can perform this action."""
    path: ReposDeleteReleaseRequestPath

# Operation: list_release_assets
class ReposListReleaseAssetsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release to retrieve assets from.")
class ReposListReleaseAssetsRequest(StrictModel):
    """Retrieve all assets (files, binaries, archives) attached to a specific release. Assets are downloadable files published with a release."""
    path: ReposListReleaseAssetsRequestPath

# Operation: upload_release_asset
class ReposUploadReleaseAssetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release to which the asset will be uploaded.")
class ReposUploadReleaseAssetRequestQuery(StrictModel):
    name: str = Field(default=..., description="The filename for the asset. GitHub will rename files with special characters, non-alphanumeric characters, or leading/trailing periods. Duplicate filenames will cause an error and require deletion of the existing asset before re-upload.")
    label: str | None = Field(default=None, description="An optional display label for the asset that describes its purpose or contents.")
class ReposUploadReleaseAssetRequestBody(StrictModel):
    body: str | None = Field(default=None, description="The raw binary file data to upload. Set the Content-Type header to the appropriate media type (e.g., application/zip).", json_schema_extra={'format': 'binary'})
class ReposUploadReleaseAssetRequest(StrictModel):
    """Upload a binary asset file to a release. The asset data must be sent as raw binary content in the request body with the appropriate Content-Type header."""
    path: ReposUploadReleaseAssetRequestPath
    query: ReposUploadReleaseAssetRequestQuery
    body: ReposUploadReleaseAssetRequestBody | None = None

# Operation: list_release_reactions
class ReactionsListForReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release for which to list reactions.")
class ReactionsListForReleaseRequestQuery(StrictModel):
    content: Literal["+1", "laugh", "heart", "hooray", "rocket", "eyes"] | None = Field(default=None, description="Filter results to a single reaction type. Omit this parameter to list all reactions to the release.")
class ReactionsListForReleaseRequest(StrictModel):
    """List all reactions or filter by a specific reaction type for a release. Reactions allow users to express sentiment on releases using emoji."""
    path: ReactionsListForReleaseRequestPath
    query: ReactionsListForReleaseRequestQuery | None = None

# Operation: add_release_reaction
class ReactionsCreateForReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release to add a reaction to.")
class ReactionsCreateForReleaseRequestBody(StrictModel):
    content: Literal["+1", "laugh", "heart", "hooray", "rocket", "eyes"] = Field(default=..., description="The emoji reaction type to add to the release.")
class ReactionsCreateForReleaseRequest(StrictModel):
    """Add an emoji reaction to a release. Returns a 200 status if the reaction type was already added by the authenticated user."""
    path: ReactionsCreateForReleaseRequestPath
    body: ReactionsCreateForReleaseRequestBody

# Operation: delete_release_reaction
class ReactionsDeleteForReleaseRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository, without the `.git` extension. The name is case-insensitive.")
    release_id: int = Field(default=..., description="The unique identifier of the release from which to delete the reaction.")
    reaction_id: int = Field(default=..., description="The unique identifier of the reaction to delete.")
class ReactionsDeleteForReleaseRequest(StrictModel):
    """Delete a reaction from a release. This removes the specified reaction emoji that was added to the release."""
    path: ReactionsDeleteForReleaseRequestPath

# Operation: list_branch_rules
class ReposGetBranchRulesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    branch: str = Field(default=..., description="The branch name to retrieve rules for. Wildcard characters are not supported; use the GraphQL API for wildcard matching.")
class ReposGetBranchRulesRequest(StrictModel):
    """Retrieve all active rules that apply to a specified branch. Rules are returned regardless of configuration level (repository or organization) and include only those with active enforcement status."""
    path: ReposGetBranchRulesRequestPath

# Operation: list_rule_suites
class ReposGetRepoRuleSuitesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetRepoRuleSuitesRequestQuery(StrictModel):
    time_period: Literal["hour", "day", "week", "month"] | None = Field(default=None, description="The time period to filter rule suites by. Filters results to evaluations that occurred within the specified window (hour: past 1 hour, day: past 24 hours, week: past 7 days, month: past 30 days).")
    actor_name: str | None = Field(default=None, description="The GitHub user account handle to filter on. When specified, only rule evaluations triggered by this actor will be returned.")
    rule_suite_result: Literal["pass", "fail", "bypass", "all"] | None = Field(default=None, description="The rule suite result status to filter on. When specified, only suites with this result will be returned.")
class ReposGetRepoRuleSuitesRequest(StrictModel):
    """Lists suites of rule evaluations at the repository level. Use this to view insights and audit rule enforcement across your repository."""
    path: ReposGetRepoRuleSuitesRequestPath
    query: ReposGetRepoRuleSuitesRequestQuery | None = None

# Operation: get_rule_suite
class ReposGetRepoRuleSuiteRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
    rule_suite_id: int = Field(default=..., description="The unique identifier of the rule suite result. Retrieve this ID using the list rule suites endpoint for your repository or organization.")
class ReposGetRepoRuleSuiteRequest(StrictModel):
    """Retrieve detailed information about a specific rule suite evaluation result within a repository. Use this to view insights and outcomes from ruleset enforcement."""
    path: ReposGetRepoRuleSuiteRequestPath

# Operation: get_ruleset
class ReposGetRepoRulesetRequestPath(StrictModel):
    owner: str = Field(default=..., description="The owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the .git extension. Case-insensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset to retrieve.")
class ReposGetRepoRulesetRequestQuery(StrictModel):
    includes_parents: bool | None = Field(default=None, description="Whether to include rulesets configured at higher organizational or enterprise levels that apply to this repository.")
class ReposGetRepoRulesetRequest(StrictModel):
    """Retrieve a specific ruleset configured for a repository. The bypass_actors property is only included if you have write access to the ruleset."""
    path: ReposGetRepoRulesetRequestPath
    query: ReposGetRepoRulesetRequestQuery | None = None

# Operation: list_ruleset_history_repository
class ReposGetRepoRulesetHistoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset whose history you want to retrieve.")
class ReposGetRepoRulesetHistoryRequest(StrictModel):
    """Retrieve the complete history of changes for a repository ruleset, including all modifications and their timestamps."""
    path: ReposGetRepoRulesetHistoryRequestPath

# Operation: get_ruleset_version_repository
class ReposGetRepoRulesetVersionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ruleset_id: int = Field(default=..., description="The unique identifier of the ruleset.")
    version_id: int = Field(default=..., description="The unique identifier of the ruleset version to retrieve.")
class ReposGetRepoRulesetVersionRequest(StrictModel):
    """Retrieve a specific version of a repository ruleset to view its configuration and rules at that point in time."""
    path: ReposGetRepoRulesetVersionRequestPath

# Operation: list_secret_scanning_alerts_repository
class SecretScanningListAlertsForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class SecretScanningListAlertsForRepoRequestQuery(StrictModel):
    state: Literal["open", "resolved"] | None = Field(default=None, description="Filter alerts by their current state.")
    secret_type: str | None = Field(default=None, description="Filter by one or more secret types using comma-separated values. Supports both default secret patterns and generic token names.")
    resolution: str | None = Field(default=None, description="Filter by one or more resolution statuses using comma-separated values.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results.")
    validity: str | None = Field(default=None, description="Filter by validity status using comma-separated values. Indicates whether the secret is currently active, inactive, or of unknown status.")
    is_publicly_leaked: bool | None = Field(default=None, description="Filter to include only alerts that have been publicly leaked.")
    is_multi_repo: bool | None = Field(default=None, description="Filter to include only alerts detected across multiple repositories.")
    hide_secret: bool | None = Field(default=None, description="Redact literal secret values from the response for security purposes.")
class SecretScanningListAlertsForRepoRequest(StrictModel):
    """Retrieve secret scanning alerts for a repository, ordered from newest to oldest. Requires administrator access to the repository or owning organization."""
    path: SecretScanningListAlertsForRepoRequestPath
    query: SecretScanningListAlertsForRepoRequestQuery | None = None

# Operation: get_secret_scanning_alert
class SecretScanningGetAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class SecretScanningGetAlertRequestQuery(StrictModel):
    hide_secret: bool | None = Field(default=None, description="Whether to hide literal secrets in the response results.")
class SecretScanningGetAlertRequest(StrictModel):
    """Retrieve a single secret scanning alert detected in a repository. The authenticated user must be an administrator for the repository or owning organization."""
    path: SecretScanningGetAlertRequestPath
    query: SecretScanningGetAlertRequestQuery | None = None

# Operation: update_secret_scanning_alert
class SecretScanningUpdateAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class SecretScanningUpdateAlertRequestBody(StrictModel):
    state: Literal["open", "resolved"] | None = Field(default=None, description="Sets the state of the secret scanning alert. When setting to `resolved`, you must provide a `resolution` reason.")
    resolution: Literal["false_positive", "wont_fix", "revoked", "used_in_tests"] | None = Field(default=None, description="The reason for resolving the alert. Required when `state` is set to `resolved`.")
    resolution_comment: str | None = Field(default=None, description="An optional comment when closing or reopening an alert. Cannot be updated or deleted after creation.")
class SecretScanningUpdateAlertRequest(StrictModel):
    """Update the status of a secret scanning alert in a repository, including resolving it with a reason or assigning it to a user. The authenticated user must be an administrator for the repository or organization."""
    path: SecretScanningUpdateAlertRequestPath
    body: SecretScanningUpdateAlertRequestBody | None = None

# Operation: list_secret_alert_locations
class SecretScanningListLocationsForAlertRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    alert_number: int = Field(default=..., description="The number that identifies an alert. You can find this at the end of the URL for a code scanning alert within GitHub, and in the `number` field in the response from the `GET /repos/{owner}/{repo}/code-scanning/alerts` operation.")
class SecretScanningListLocationsForAlertRequest(StrictModel):
    """Lists all locations where a secret scanning alert has been detected in a repository. Requires administrator access to the repository or owning organization."""
    path: SecretScanningListLocationsForAlertRequestPath

# Operation: bypass_push_protection
class SecretScanningCreatePushProtectionBypassRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class SecretScanningCreatePushProtectionBypassRequestBody(StrictModel):
    reason: Literal["false_positive", "used_in_tests", "will_fix_later"] = Field(default=..., description="The reason for bypassing push protection. Select from predefined reasons that categorize why the secret should be allowed.")
    placeholder_id: str = Field(default=..., description="The ID of the push protection bypass placeholder returned when a secret is push protected.")
class SecretScanningCreatePushProtectionBypassRequest(StrictModel):
    """Create a bypass for a secret that was previously blocked by push protection. The authenticated user must be the original author of the committed secret."""
    path: SecretScanningCreatePushProtectionBypassRequestPath
    body: SecretScanningCreatePushProtectionBypassRequestBody

# Operation: list_secret_scan_history
class SecretScanningGetScanHistoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class SecretScanningGetScanHistoryRequest(StrictModel):
    """Retrieve the latest secret scanning scan history for a repository, including default incremental and backfill scans by type. Requires GitHub Advanced Security and appropriate authentication scopes."""
    path: SecretScanningGetScanHistoryRequestPath

# Operation: list_security_advisories
class SecurityAdvisoriesListRepositoryAdvisoriesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class SecurityAdvisoriesListRepositoryAdvisoriesRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The direction to sort the results by.")
    state: Literal["triage", "draft", "published", "closed"] | None = Field(default=None, description="Filter advisories by their current state. Only advisories matching the specified state will be returned.")
class SecurityAdvisoriesListRepositoryAdvisoriesRequest(StrictModel):
    """Retrieve security advisories for a repository. Authenticated users with appropriate permissions can access both published and unpublished advisories, depending on their role and access level."""
    path: SecurityAdvisoriesListRepositoryAdvisoriesRequestPath
    query: SecurityAdvisoriesListRepositoryAdvisoriesRequestQuery | None = None

# Operation: create_security_advisory
class SecurityAdvisoriesCreateRepositoryAdvisoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class SecurityAdvisoriesCreateRepositoryAdvisoryRequestBody(StrictModel):
    summary: str = Field(default=..., description="A short summary of the advisory.", max_length=1024)
    description: str = Field(default=..., description="A detailed description of what the advisory impacts.", max_length=65535)
    cve_id: str | None = Field(default=None, description="The Common Vulnerabilities and Exposures (CVE) ID for this vulnerability.")
    vulnerabilities: list[SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItem] = Field(default=..., description="An array of products affected by the vulnerability. Each item specifies the package, affected version ranges, and patched versions.")
    cwe_ids: list[str] | None = Field(default=None, description="An array of Common Weakness Enumeration (CWE) IDs that relate to this vulnerability.")
    credits_: list[SecurityAdvisoriesCreateRepositoryAdvisoryBodyCreditsItem] | None = Field(default=None, validation_alias="credits", serialization_alias="credits", description="An array of users to receive credit for their participation in identifying or fixing the security advisory.")
    start_private_fork: bool | None = Field(default=None, description="Whether to create a temporary private fork of the repository to collaborate on a fix.")
    severity: Literal["critical", "high", "medium", "low"] | None = Field(default=None, description="The severity of the advisory. You must choose between setting this field or `cvss_vector_string`.")
class SecurityAdvisoriesCreateRepositoryAdvisoryRequest(StrictModel):
    """Create a new repository security advisory to document and track vulnerabilities. The authenticated user must be a security manager or administrator of the repository."""
    path: SecurityAdvisoriesCreateRepositoryAdvisoryRequestPath
    body: SecurityAdvisoriesCreateRepositoryAdvisoryRequestBody

# Operation: report_security_vulnerability
class SecurityAdvisoriesCreatePrivateVulnerabilityReportRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class SecurityAdvisoriesCreatePrivateVulnerabilityReportRequestBody(StrictModel):
    summary: str = Field(default=..., description="A concise summary of the security vulnerability.", max_length=1024)
    description: str = Field(default=..., description="A detailed explanation of what the vulnerability impacts, including affected components and potential consequences.", max_length=65535)
    vulnerabilities: list[SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItem] | None = Field(default=None, description="An array of products or components affected by the vulnerability. Each item should specify the affected product and version range.")
    cwe_ids: list[str] | None = Field(default=None, description="A list of Common Weakness Enumeration (CWE) IDs that classify the vulnerability type.")
    start_private_fork: bool | None = Field(default=None, description="Whether to create a temporary private fork of the repository to facilitate collaborative fix development.")
class SecurityAdvisoriesCreatePrivateVulnerabilityReportRequest(StrictModel):
    """Privately report a security vulnerability to repository maintainers. This initiates a coordinated disclosure process allowing maintainers to address the issue before public disclosure."""
    path: SecurityAdvisoriesCreatePrivateVulnerabilityReportRequestPath
    body: SecurityAdvisoriesCreatePrivateVulnerabilityReportRequestBody

# Operation: get_security_advisory_repository
class SecurityAdvisoriesGetRepositoryAdvisoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ghsa_id: str = Field(default=..., description="The GitHub Security Advisory (GHSA) identifier that uniquely identifies the security advisory.")
class SecurityAdvisoriesGetRepositoryAdvisoryRequest(StrictModel):
    """Retrieve a repository security advisory by its GitHub Security Advisory (GHSA) identifier. Published advisories on public repositories are accessible to anyone; unpublished advisories require appropriate permissions (security manager, administrator, or collaborator status)."""
    path: SecurityAdvisoriesGetRepositoryAdvisoryRequestPath

# Operation: update_security_advisory
class SecurityAdvisoriesUpdateRepositoryAdvisoryRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    ghsa_id: str = Field(default=..., description="The GitHub Security Advisory (GHSA) identifier of the advisory to update.")
class SecurityAdvisoriesUpdateRepositoryAdvisoryRequestBody(StrictModel):
    summary: str | None = Field(default=None, description="A short summary of the advisory.", max_length=1024)
    description: str | None = Field(default=None, description="A detailed description of what the advisory impacts.", max_length=65535)
    cve_id: str | None = Field(default=None, description="The Common Vulnerabilities and Exposures (CVE) identifier.")
    vulnerabilities: list[SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItem] | None = Field(default=None, description="An array of products affected by the vulnerability detailed in the advisory.")
    cwe_ids: list[str] | None = Field(default=None, description="An array of Common Weakness Enumeration (CWE) identifiers related to the advisory.")
    credits_: list[SecurityAdvisoriesUpdateRepositoryAdvisoryBodyCreditsItem] | None = Field(default=None, validation_alias="credits", serialization_alias="credits", description="An array of users receiving credit for their participation in the security advisory.")
    state: Literal["published", "closed", "draft"] | None = Field(default=None, description="The publication state of the advisory.")
    collaborating_users: list[str] | None = Field(default=None, description="An array of usernames who have been granted write access to the advisory.")
    collaborating_teams: list[str] | None = Field(default=None, description="An array of team slugs which have been granted write access to the advisory.")
class SecurityAdvisoriesUpdateRepositoryAdvisoryRequest(StrictModel):
    """Update a repository security advisory by its GHSA identifier. The authenticated user must be a security manager, administrator, or collaborator on the advisory."""
    path: SecurityAdvisoriesUpdateRepositoryAdvisoryRequestPath
    body: SecurityAdvisoriesUpdateRepositoryAdvisoryRequestBody | None = None

# Operation: request_cve_for_advisory
class SecurityAdvisoriesCreateRepositoryAdvisoryCveRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ghsa_id: str = Field(default=..., description="The GHSA (GitHub Security Advisory) identifier of the advisory for which you are requesting a CVE.")
class SecurityAdvisoriesCreateRepositoryAdvisoryCveRequest(StrictModel):
    """Request a CVE identification number for a repository security advisory. This allows you to obtain an official CVE ID from GitHub for a vulnerability in your public repository."""
    path: SecurityAdvisoriesCreateRepositoryAdvisoryCveRequestPath

# Operation: create_security_advisory_fork
class SecurityAdvisoriesCreateForkRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ghsa_id: str = Field(default=..., description="The GitHub Security Advisory (GHSA) identifier for the vulnerability being addressed.")
class SecurityAdvisoriesCreateForkRequest(StrictModel):
    """Create a temporary private fork to collaborate on fixing a security vulnerability. The fork is created asynchronously and may take up to 5 minutes to become accessible."""
    path: SecurityAdvisoriesCreateForkRequestPath

# Operation: list_stargazers
class ActivityListStargazersForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. Case-insensitive.")
class ActivityListStargazersForRepoRequest(StrictModel):
    """Lists all users who have starred the repository. Supports custom media type to include star creation timestamps."""
    path: ActivityListStargazersForRepoRequestPath

# Operation: get_code_frequency_stats
class ReposGetCodeFrequencyStatsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposGetCodeFrequencyStatsRequest(StrictModel):
    """Retrieve weekly code frequency statistics showing the aggregate number of additions and deletions pushed to a repository. This endpoint is limited to repositories with fewer than 10,000 commits."""
    path: ReposGetCodeFrequencyStatsRequestPath

# Operation: list_commit_activity_stats
class ReposGetCommitActivityStatsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The repository name without the `.git` extension. The name is case-insensitive.")
class ReposGetCommitActivityStatsRequest(StrictModel):
    """Retrieve commit activity statistics for the last year, grouped by week with daily breakdowns starting on Sunday. Useful for analyzing repository contribution patterns and trends."""
    path: ReposGetCommitActivityStatsRequestPath

# Operation: list_contributor_stats
class ReposGetContributorsStatsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposGetContributorsStatsRequest(StrictModel):
    """Retrieve commit activity statistics for all contributors to a repository, including total commits and weekly breakdowns of additions, deletions, and commits. Note: repositories with 10,000+ commits will show 0 for addition and deletion counts."""
    path: ReposGetContributorsStatsRequestPath

# Operation: get_repository_participation_stats
class ReposGetParticipationStatsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetParticipationStatsRequest(StrictModel):
    """Retrieve weekly commit statistics for a repository over the last 52 weeks, showing total commits by the owner and all contributors combined. Data is ordered from oldest to most recent week, with the most recent week spanning from seven days ago to today at UTC midnight."""
    path: ReposGetParticipationStatsRequestPath

# Operation: get_commit_punch_card
class ReposGetPunchCardStatsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetPunchCardStatsRequest(StrictModel):
    """Retrieve hourly commit statistics for each day of the week, showing commit frequency patterns across all hours. Data is organized as arrays containing day number (0-6), hour (0-23), and commit count."""
    path: ReposGetPunchCardStatsRequestPath

# Operation: create_commit_status
class ReposCreateCommitStatusRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
    sha: str = Field(default=..., description="The commit SHA for which to create the status.")
class ReposCreateCommitStatusRequestBody(StrictModel):
    state: Literal["error", "failure", "pending", "success"] = Field(default=..., description="The state of the commit status, indicating the result of the check or build.")
    description: str | None = Field(default=None, description="A short description of the status, providing additional context about the state.")
    context: str | None = Field(default=None, description="A string label to differentiate this status from other systems. Case-insensitive. Defaults to 'default' if not provided.")
class ReposCreateCommitStatusRequest(StrictModel):
    """Create a commit status for a given SHA in a repository. Users with push access can set the status to track build results, checks, or other system states, with a limit of 1000 statuses per SHA and context combination."""
    path: ReposCreateCommitStatusRequestPath
    body: ReposCreateCommitStatusRequestBody

# Operation: list_watchers
class ActivityListWatchersForRepoRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActivityListWatchersForRepoRequest(StrictModel):
    """Lists all users who are watching the specified repository. Watchers receive notifications about repository activity."""
    path: ActivityListWatchersForRepoRequestPath

# Operation: get_repository_subscription
class ActivityGetRepoSubscriptionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActivityGetRepoSubscriptionRequest(StrictModel):
    """Retrieve the authenticated user's subscription status for a repository. Returns subscription details including whether the user is watching, subscribed to notifications, or ignoring the repository."""
    path: ActivityGetRepoSubscriptionRequestPath

# Operation: configure_repository_subscription
class ActivitySetRepoSubscriptionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActivitySetRepoSubscriptionRequestBody(StrictModel):
    subscribed: bool | None = Field(default=None, description="Set to `true` to receive notifications from this repository, or `false` to disable watch notifications.")
    ignored: bool | None = Field(default=None, description="Set to `true` to block all notifications from this repository, or `false` to allow notifications based on other settings.")
class ActivitySetRepoSubscriptionRequest(StrictModel):
    """Configure your notification preferences for a repository by enabling or disabling watch status and notification blocking. Use this to control whether you receive notifications from repository activity."""
    path: ActivitySetRepoSubscriptionRequestPath
    body: ActivitySetRepoSubscriptionRequestBody | None = None

# Operation: unwatch_repository
class ActivityDeleteRepoSubscriptionRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActivityDeleteRepoSubscriptionRequest(StrictModel):
    """Stop watching a repository and remove its subscription. This endpoint only controls watch status; to manage notification preferences, set the repository subscription manually."""
    path: ActivityDeleteRepoSubscriptionRequestPath

# Operation: list_tags
class ReposListTagsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposListTagsRequest(StrictModel):
    """Retrieve all tags for a repository. Tags are typically used to mark specific points in the repository's history, such as release versions."""
    path: ReposListTagsRequestPath

# Operation: download_repository_archive
class ReposDownloadTarballArchiveRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
    ref: str = Field(default=..., description="The git reference to archive, such as a branch name, tag, or commit SHA. If omitted, the repository's default branch will be used.")
class ReposDownloadTarballArchiveRequest(StrictModel):
    """Downloads a tar archive of a repository at a specified reference (branch, tag, or commit). Returns a redirect URL that must be followed to retrieve the actual archive file."""
    path: ReposDownloadTarballArchiveRequestPath

# Operation: list_repository_teams
class ReposListTeamsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposListTeamsRequest(StrictModel):
    """Lists all teams that have access to the specified repository and are visible to the authenticated user. For public repositories, only teams that explicitly added the repository are included."""
    path: ReposListTeamsRequestPath

# Operation: list_repository_topics
class ReposGetAllTopicsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposGetAllTopicsRequest(StrictModel):
    """Retrieve all topics associated with a repository. Topics are labels that help categorize and discover repositories."""
    path: ReposGetAllTopicsRequestPath

# Operation: update_repository_topics
class ReposReplaceAllTopicsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposReplaceAllTopicsRequestBody(StrictModel):
    names: list[str] = Field(default=..., description="An array of topics to set for the repository. Provide one or more topics to replace existing topics, or an empty array to clear all topics. Topics are automatically stored as lowercase.")
class ReposReplaceAllTopicsRequest(StrictModel):
    """Replace all topics associated with a repository. Pass an array of topics to update the repository's topic tags, or send an empty array to remove all topics. Topics are stored as lowercase."""
    path: ReposReplaceAllTopicsRequestPath
    body: ReposReplaceAllTopicsRequestBody

# Operation: list_repository_clones
class ReposGetClonesRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetClonesRequestQuery(StrictModel):
    per: Literal["day", "week"] | None = Field(default=None, description="The time frame to display clone results for.")
class ReposGetClonesRequest(StrictModel):
    """Retrieve the total number of clones and daily or weekly breakdown for a repository over the last 14 days. Timestamps are aligned to UTC midnight at the start of each period, with weeks beginning on Monday."""
    path: ReposGetClonesRequestPath
    query: ReposGetClonesRequestQuery | None = None

# Operation: list_popular_paths
class ReposGetTopPathsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetTopPathsRequest(StrictModel):
    """Retrieve the top 10 most popular content paths for a repository based on traffic data from the last 14 days."""
    path: ReposGetTopPathsRequestPath

# Operation: get_repository_views
class ReposGetViewsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposGetViewsRequestQuery(StrictModel):
    per: Literal["day", "week"] | None = Field(default=None, description="The time frame to display results for. Choose between daily or weekly aggregation.")
class ReposGetViewsRequest(StrictModel):
    """Retrieve the total number of page views and daily or weekly breakdown for a repository over the last 14 days. Timestamps are aligned to UTC midnight at the start of each period, with weeks beginning on Monday."""
    path: ReposGetViewsRequestPath
    query: ReposGetViewsRequestQuery | None = None

# Operation: transfer_repository
class ReposTransferRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. Case-insensitive.")
class ReposTransferRequestBody(StrictModel):
    new_owner: str = Field(default=..., description="The username or organization name that will become the new repository owner.")
    new_name: str | None = Field(default=None, description="Optional new name for the repository after transfer.")
    team_ids: list[int] | None = Field(default=None, description="Optional array of team IDs to add to the repository. Teams can only be added to organization-owned repositories. Order is not significant.")
class ReposTransferRequest(StrictModel):
    """Transfer a repository to a new owner (user or organization). The transfer request requires acceptance by the new owner and proceeds asynchronously, with the original owner retained in the response."""
    path: ReposTransferRequestPath
    body: ReposTransferRequestBody

# Operation: get_vulnerability_alerts_status
class ReposCheckVulnerabilityAlertsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ReposCheckVulnerabilityAlertsRequest(StrictModel):
    """Retrieve the vulnerability alert status for a repository. Returns whether dependency alerts are enabled or disabled. Requires admin read access to the repository."""
    path: ReposCheckVulnerabilityAlertsRequestPath

# Operation: enable_vulnerability_alerts
class ReposEnableVulnerabilityAlertsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposEnableVulnerabilityAlertsRequest(StrictModel):
    """Enable dependency alerts and the dependency graph for a repository to receive security notifications about vulnerable dependencies. The authenticated user must have admin access to the repository."""
    path: ReposEnableVulnerabilityAlertsRequestPath

# Operation: disable_vulnerability_alerts
class ReposDisableVulnerabilityAlertsRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ReposDisableVulnerabilityAlertsRequest(StrictModel):
    """Disables dependency alerts and the dependency graph for a repository. The authenticated user must have admin access to the repository."""
    path: ReposDisableVulnerabilityAlertsRequestPath

# Operation: download_repository_archive_zip
class ReposDownloadZipballArchiveRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. Case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the .git extension. Case-insensitive.")
    ref: str = Field(default=..., description="The git reference (branch, tag, or commit SHA) to archive. If omitted, the repository's default branch will be used.")
class ReposDownloadZipballArchiveRequest(StrictModel):
    """Downloads a repository as a zip archive by following a redirect URL. Omit the ref parameter to use the repository's default branch (usually main). Note: links for private repositories expire after five minutes, and empty repositories return a 404 error."""
    path: ReposDownloadZipballArchiveRequestPath

# Operation: create_repository_from_template
class ReposCreateUsingTemplateRequestPath(StrictModel):
    template_owner: str = Field(default=..., description="The account owner of the template repository. Case-insensitive.")
    template_repo: str = Field(default=..., description="The name of the template repository without the `.git` extension. Case-insensitive.")
class ReposCreateUsingTemplateRequestBody(StrictModel):
    name: str = Field(default=..., description="The name for the new repository being created.")
    description: str | None = Field(default=None, description="A short description of the new repository.")
    include_all_branches: bool | None = Field(default=None, description="Set to true to include the directory structure and files from all branches in the template repository, rather than just the default branch.")
class ReposCreateUsingTemplateRequest(StrictModel):
    """Creates a new repository using an existing repository template. The template repository must have `is_template` set to true, and you must have access to it (ownership or organization membership for private templates)."""
    path: ReposCreateUsingTemplateRequestPath
    body: ReposCreateUsingTemplateRequestBody

# Operation: list_public_repositories
class ReposListPublicRequestQuery(StrictModel):
    since: int | None = Field(default=None, description="Filter results to return only repositories with an ID greater than this value. Use this parameter for pagination by passing the ID of the last repository from the previous page.")
class ReposListPublicRequest(StrictModel):
    """Retrieve all public repositories ordered by creation time. Pagination is controlled exclusively through the `since` parameter to fetch subsequent pages of results."""
    query: ReposListPublicRequestQuery | None = None

# Operation: add_issue_field_values
class IssuesAddIssueFieldValuesRequestPath(StrictModel):
    repository_id: int = Field(default=..., description="The unique identifier of the repository.")
    issue_number: int = Field(default=..., description="The issue number to update with field values.")
class IssuesAddIssueFieldValuesRequestBody(StrictModel):
    issue_field_values: list[IssuesAddIssueFieldValuesBodyIssueFieldValuesItem] | None = Field(default=None, description="An array of field value objects to set on the issue, where each object contains a field ID and its corresponding value. Pass an empty array to clear all existing field values. Supports up to 25 field values per request.", max_length=25)
class IssuesAddIssueFieldValuesRequest(StrictModel):
    """Set custom field values for an issue using organization-level fields defined for the repository. Supports text, single-select, number, and date field types. Requires push access to the repository."""
    path: IssuesAddIssueFieldValuesRequestPath
    body: IssuesAddIssueFieldValuesRequestBody | None = None

# Operation: set_issue_field_values
class IssuesSetIssueFieldValuesRequestPath(StrictModel):
    repository_id: int = Field(default=..., description="The unique identifier of the repository.")
    issue_number: int = Field(default=..., description="The number that identifies the issue within the repository.")
class IssuesSetIssueFieldValuesRequestBody(StrictModel):
    issue_field_values: list[IssuesSetIssueFieldValuesBodyIssueFieldValuesItem] | None = Field(default=None, description="An array of field value objects to set for this issue. Each object must include the field ID and the value to set. All existing field values will be replaced. Values must match the field's data type: text (string), single_select (option name), number (numeric), or date (ISO 8601 format).", max_length=25)
class IssuesSetIssueFieldValuesRequest(StrictModel):
    """Set custom field values for an issue, replacing all existing values. Supports text, single_select, number, and date field types. Requires push access to the repository."""
    path: IssuesSetIssueFieldValuesRequestPath
    body: IssuesSetIssueFieldValuesRequestBody | None = None

# Operation: delete_issue_field_value
class IssuesDeleteIssueFieldValueRequestPath(StrictModel):
    repository_id: int = Field(default=..., description="The unique identifier of the repository containing the issue.")
    issue_number: int = Field(default=..., description="The issue number that identifies which issue to modify.")
    issue_field_id: int = Field(default=..., description="The unique identifier of the custom field whose value should be deleted from the issue.")
class IssuesDeleteIssueFieldValueRequest(StrictModel):
    """Remove a custom field value from an issue. Requires push access to the repository; returns 404 if the field has no value set on the issue."""
    path: IssuesDeleteIssueFieldValueRequestPath

# Operation: search_code
class SearchCodeRequestQuery(StrictModel):
    q: str = Field(default=..., description="Search query containing one or more keywords and qualifiers (e.g., language, repo, in:file). At least one search term is required; qualifiers can filter by language, repository, file path, and other code attributes.")
class SearchCodeRequest(StrictModel):
    """Search for code across repositories by query terms within file contents and paths. Returns up to 100 results per page, limited to the default branch and files under 384 KB."""
    query: SearchCodeRequestQuery

# Operation: search_commits
class SearchCommitsRequestQuery(StrictModel):
    order: Literal["desc", "asc"] | None = Field(default=None, description="Sort order for search results, determining whether results are ordered by highest or lowest match count. Only applies when using the sort parameter.")
    q: str | None = Field(default=None, description="The query contains one or more search keywords and qualifiers. Qualifiers allow you to limit your search to specific areas of GitHub. The REST API supports the same qualifiers as the web interface for GitHub. To learn more about the format of the query, see [Constructing a search query](https://docs.github.com/rest/search/search#constructing-a-search-query). See \"[Searching commits](https://docs.github.com/search-github/searching-on-github/searching-commits)\" for a detailed list of qualifiers.")
class SearchCommitsRequest(StrictModel):
    """Search for commits across a repository using various criteria on the default branch. Returns up to 100 results per page and supports text match metadata for commit messages."""
    query: SearchCommitsRequestQuery | None = None

# Operation: search_issues
class SearchIssuesAndPullRequestsRequestQuery(StrictModel):
    order: Literal["desc", "asc"] | None = Field(default=None, description="Sort order for search results. Use ascending to show lowest match counts first, or descending for highest match counts first. Only applies when results are sorted.")
    q: str | None = Field(default=None, description="The query contains one or more search keywords and qualifiers. Qualifiers allow you to limit your search to specific areas of GitHub. The REST API supports the same qualifiers as the web interface for GitHub. To learn more about the format of the query, see [Constructing a search query](https://docs.github.com/rest/search/search#constructing-a-search-query). See \"[Searching issues and pull requests](https://docs.github.com/search-github/searching-on-github/searching-issues-and-pull-requests)\" for a detailed list of qualifiers.")
class SearchIssuesAndPullRequestsRequest(StrictModel):
    """Search for issues and pull requests across repositories by state, keywords, and labels. Returns up to 100 results per page with optional text match metadata for titles, bodies, and comments."""
    query: SearchIssuesAndPullRequestsRequestQuery | None = None

# Operation: search_labels
class SearchLabelsRequestQuery(StrictModel):
    repository_id: int = Field(default=..., description="The numeric identifier of the repository to search labels within.")
    q: str = Field(default=..., description="The search keywords to match against label names and descriptions. Qualifiers are not supported in this query.")
    order: Literal["desc", "asc"] | None = Field(default=None, description="Determines the sort order of results: highest match count first (desc) or lowest match count first (asc).")
class SearchLabelsRequest(StrictModel):
    """Search for labels in a repository by name or description using keywords. Returns up to 100 results per page, with the best matching labels appearing first."""
    query: SearchLabelsRequestQuery

# Operation: search_repositories
class SearchReposRequestQuery(StrictModel):
    q: str = Field(default=..., description="Search query containing one or more keywords and qualifiers to filter repositories. Qualifiers allow you to limit results by language, stars, forks, creation date, and other repository attributes. Refer to GitHub's search query syntax documentation for supported qualifiers and formatting.")
    order: Literal["desc", "asc"] | None = Field(default=None, description="Sort order for search results. Use 'desc' to return results with the highest match count first, or 'asc' for lowest match count first. This parameter only applies when results are sorted.")
class SearchReposRequest(StrictModel):
    """Search GitHub repositories using keywords and qualifiers to find repositories matching specific criteria. Results are paginated with up to 100 repositories per page."""
    query: SearchReposRequestQuery

# Operation: search_topics
class SearchTopicsRequestQuery(StrictModel):
    q: str = Field(default=..., description="Search query containing one or more keywords and optional qualifiers (e.g., is:featured) to filter results. Qualifiers allow you to limit searches to specific topic attributes like featured status, language, or other criteria supported by GitHub's search interface.")
class SearchTopicsRequest(StrictModel):
    """Search for GitHub topics using keywords and qualifiers to find the best matching results. Results are sorted by relevance and limited to 100 per page."""
    query: SearchTopicsRequestQuery

# Operation: search_users
class SearchUsersRequestQuery(StrictModel):
    order: Literal["desc", "asc"] | None = Field(default=None, description="Sort order for search results based on match relevance. Use 'desc' for highest matches first or 'asc' for lowest matches first. Only applies when results are sorted.")
    q: str | None = Field(default=None, description="The query contains one or more search keywords and qualifiers. Qualifiers allow you to limit your search to specific areas of GitHub. The REST API supports the same qualifiers as the web interface for GitHub. To learn more about the format of the query, see [Constructing a search query](https://docs.github.com/rest/search/search#constructing-a-search-query). See \"[Searching users](https://docs.github.com/search-github/searching-on-github/searching-users)\" for a detailed list of qualifiers.")
class SearchUsersRequest(StrictModel):
    """Search for publicly visible users by various criteria including name, email, repository count, and followers. Returns up to 100 results per page and supports text match metadata for enhanced result highlighting."""
    query: SearchUsersRequestQuery | None = None

# Operation: update_user
class UsersUpdateAuthenticatedRequestBody(StrictModel):
    blog: str | None = Field(default=None, description="The user's blog or personal website URL.")
    twitter_username: str | None = Field(default=None, description="The user's Twitter username.")
    company: str | None = Field(default=None, description="The user's company or organization name.")
    hireable: bool | None = Field(default=None, description="Whether the user is available for hiring.")
    bio: str | None = Field(default=None, description="A short biography or about section for the user's profile.")
class UsersUpdateAuthenticatedRequest(StrictModel):
    """Update the authenticated user's profile information. Note that email privacy settings are always enforced—if your email is private, it will not be displayed publicly regardless of updates."""
    body: UsersUpdateAuthenticatedRequestBody | None = None

# Operation: check_user_blocked
class UsersCheckBlockedRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username handle to check for a blocking relationship.")
class UsersCheckBlockedRequest(StrictModel):
    """Determine if a specific user is blocked by the authenticated user. Returns a 204 status if the user is blocked, or 404 if the user is not blocked or has been identified as spam."""
    path: UsersCheckBlockedRequestPath

# Operation: block_user
class UsersBlockRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username handle of the user to block.")
class UsersBlockRequest(StrictModel):
    """Block a GitHub user to prevent interactions with them. Returns a 204 status on success, or 422 if the authenticated user cannot block the specified user."""
    path: UsersBlockRequestPath

# Operation: unblock_user
class UsersUnblockRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username handle of the user to unblock.")
class UsersUnblockRequest(StrictModel):
    """Unblock a previously blocked user account. Returns a 204 status code on successful completion."""
    path: UsersUnblockRequestPath

# Operation: list_codespaces
class CodespacesListForAuthenticatedUserRequestQuery(StrictModel):
    repository_id: int | None = Field(default=None, description="Filter codespaces to only those associated with a specific repository by its ID.")
class CodespacesListForAuthenticatedUserRequest(StrictModel):
    """Lists all codespaces for the authenticated user. Optionally filter results by a specific repository."""
    query: CodespacesListForAuthenticatedUserRequestQuery | None = None

# Operation: create_codespace_from_pull_request_2
class CodespacesCreateForAuthenticatedUserRequestBody(StrictModel):
    body: CodespacesCreateForAuthenticatedUserBodyV0 | CodespacesCreateForAuthenticatedUserBodyV1 = Field(default=..., description="Configuration for the new codespace, including the target repository or pull request, optional branch/tag reference, and preferred geographic region for the codespace environment.", examples=[{'repository_id': 1, 'ref': 'main', 'geo': 'UsWest'}])
class CodespacesCreateForAuthenticatedUserRequest(StrictModel):
    """Create a new codespace for the authenticated user from a repository or pull request. Requires either a repository ID or pull request reference, but not both."""
    body: CodespacesCreateForAuthenticatedUserRequestBody

# Operation: get_codespace_secret_for_user
class CodespacesGetSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the secret to retrieve.")
class CodespacesGetSecretForAuthenticatedUserRequest(StrictModel):
    """Retrieve a development environment secret available to the authenticated user's codespaces without revealing its encrypted value. Requires Codespaces access and appropriate OAuth or personal access token scopes."""
    path: CodespacesGetSecretForAuthenticatedUserRequestPath

# Operation: create_or_update_codespace_secret
class CodespacesCreateOrUpdateSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the secret to create or update.")
class CodespacesCreateOrUpdateSecretForAuthenticatedUserRequestBody(StrictModel):
    encrypted_value: str | None = Field(default=None, description="The encrypted value of the secret, encrypted using LibSodium with the public key from the Get public key endpoint. Must be base64-encoded.", pattern='^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$')
    key_id: str = Field(default=..., description="The ID of the public key used to encrypt the secret value.")
    selected_repository_ids: list[int | str] | None = Field(default=None, description="An array of repository IDs that can access this secret. Manage repository access separately using the dedicated repository endpoints.")
class CodespacesCreateOrUpdateSecretForAuthenticatedUserRequest(StrictModel):
    """Create or update an encrypted development environment secret for the authenticated user's codespaces. The secret value must be encrypted using LibSodium with a public key retrieved from the public key endpoint."""
    path: CodespacesCreateOrUpdateSecretForAuthenticatedUserRequestPath
    body: CodespacesCreateOrUpdateSecretForAuthenticatedUserRequestBody

# Operation: delete_codespace_secret_for_user
class CodespacesDeleteSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the secret to delete from the user's codespaces.")
class CodespacesDeleteSecretForAuthenticatedUserRequest(StrictModel):
    """Delete a development environment secret for the authenticated user. Removing the secret revokes access from all codespaces that were previously allowed to use it."""
    path: CodespacesDeleteSecretForAuthenticatedUserRequestPath

# Operation: list_repositories_for_secret
class CodespacesListRepositoriesForSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the user secret for which to list authorized repositories.")
class CodespacesListRepositoriesForSecretForAuthenticatedUserRequest(StrictModel):
    """List the repositories that have been granted access to use a user's development environment secret. The authenticated user must have Codespaces access to use this endpoint."""
    path: CodespacesListRepositoriesForSecretForAuthenticatedUserRequestPath

# Operation: update_secret_repositories
class CodespacesSetRepositoriesForSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the user secret to configure repository access for.")
class CodespacesSetRepositoriesForSecretForAuthenticatedUserRequestBody(StrictModel):
    selected_repository_ids: list[int] = Field(default=..., description="An array of repository IDs that will have access to this secret. Provide the complete list of repositories you want to authorize; any repositories not included will be removed from access.")
class CodespacesSetRepositoriesForSecretForAuthenticatedUserRequest(StrictModel):
    """Update which repositories can access a user's development environment secret. This replaces the entire list of authorized repositories for the specified secret."""
    path: CodespacesSetRepositoriesForSecretForAuthenticatedUserRequestPath
    body: CodespacesSetRepositoriesForSecretForAuthenticatedUserRequestBody

# Operation: add_repository_to_codespace_secret
class CodespacesAddRepositoryForSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the Codespaces secret to which the repository will be added.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to add to the secret's accessible repositories.")
class CodespacesAddRepositoryForSecretForAuthenticatedUserRequest(StrictModel):
    """Adds a repository to the list of selected repositories that can access a user's Codespaces development environment secret. The authenticated user must have Codespaces access and appropriate OAuth or personal access token scopes."""
    path: CodespacesAddRepositoryForSecretForAuthenticatedUserRequestPath

# Operation: remove_repository_from_codespace_secret
class CodespacesRemoveRepositoryForSecretForAuthenticatedUserRequestPath(StrictModel):
    secret_name: str = Field(default=..., description="The name of the Codespaces secret to modify.")
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the secret's access list.")
class CodespacesRemoveRepositoryForSecretForAuthenticatedUserRequest(StrictModel):
    """Remove a repository from a user's Codespaces development environment secret. This restricts which repositories can access the specified secret."""
    path: CodespacesRemoveRepositoryForSecretForAuthenticatedUserRequestPath

# Operation: get_codespace
class CodespacesGetForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to retrieve information for.")
class CodespacesGetForAuthenticatedUserRequest(StrictModel):
    """Retrieve detailed information about a specific codespace for the authenticated user. Requires the `codespace` scope for OAuth app tokens and personal access tokens (classic)."""
    path: CodespacesGetForAuthenticatedUserRequestPath

# Operation: update_codespace
class CodespacesUpdateForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to update.")
class CodespacesUpdateForAuthenticatedUserRequestBody(StrictModel):
    machine: str | None = Field(default=None, description="The machine type to transition this codespace to. Changes take effect the next time the codespace is started.")
    display_name: str | None = Field(default=None, description="A display name for the codespace.")
    recent_folders: list[str] | None = Field(default=None, description="An ordered list of folder paths recently opened inside the codespace. Used by clients to determine which folder to load when starting the codespace.")
class CodespacesUpdateForAuthenticatedUserRequest(StrictModel):
    """Update a codespace owned by the authenticated user. You can modify the machine type (applied on next start), display name, and recently opened folders."""
    path: CodespacesUpdateForAuthenticatedUserRequestPath
    body: CodespacesUpdateForAuthenticatedUserRequestBody | None = None

# Operation: delete_codespace
class CodespacesDeleteForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to delete.")
class CodespacesDeleteForAuthenticatedUserRequest(StrictModel):
    """Delete a codespace for the authenticated user. Requires the `codespace` OAuth scope."""
    path: CodespacesDeleteForAuthenticatedUserRequestPath

# Operation: export_codespace
class CodespacesExportForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to export.")
class CodespacesExportForAuthenticatedUserRequest(StrictModel):
    """Initiates an export of a codespace and returns a URL and ID to monitor the export status. Any uncommitted changes will be pushed to the codespace's repository or to a new/existing fork if pushing to the repository is not possible."""
    path: CodespacesExportForAuthenticatedUserRequestPath

# Operation: get_codespace_export_details
class CodespacesGetExportDetailsForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to retrieve export details for.")
    export_id: str = Field(default=..., description="The ID of the export operation to retrieve details for. Use `latest` to get the most recent export.")
class CodespacesGetExportDetailsForAuthenticatedUserRequest(StrictModel):
    """Retrieve detailed information about a codespace export operation. Use this to check the status and details of an exported codespace."""
    path: CodespacesGetExportDetailsForAuthenticatedUserRequestPath

# Operation: list_codespace_machines_available
class CodespacesCodespaceMachinesForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace for which to list available machine types.")
class CodespacesCodespaceMachinesForAuthenticatedUserRequest(StrictModel):
    """List the machine types available for a codespace to transition to. This helps determine which hardware configurations are compatible with the specified codespace."""
    path: CodespacesCodespaceMachinesForAuthenticatedUserRequestPath

# Operation: publish_codespace
class CodespacesPublishForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to publish. The codespace must be unpublished (not already associated with a repository).")
class CodespacesPublishForAuthenticatedUserRequest(StrictModel):
    """Publish an unpublished codespace by creating a new repository and associating it with the codespace. The codespace's token will have write permissions to the new repository, enabling you to push changes."""
    path: CodespacesPublishForAuthenticatedUserRequestPath

# Operation: start_codespace
class CodespacesStartForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to start.")
class CodespacesStartForAuthenticatedUserRequest(StrictModel):
    """Start a codespace for the authenticated user. Requires the `codespace` OAuth scope."""
    path: CodespacesStartForAuthenticatedUserRequestPath

# Operation: stop_codespace_authenticated
class CodespacesStopForAuthenticatedUserRequestPath(StrictModel):
    codespace_name: str = Field(default=..., description="The name of the codespace to stop.")
class CodespacesStopForAuthenticatedUserRequest(StrictModel):
    """Stop a running codespace for the authenticated user. Requires the `codespace` OAuth scope."""
    path: CodespacesStopForAuthenticatedUserRequestPath

# Operation: set_primary_email_visibility
class UsersSetPrimaryEmailVisibilityForAuthenticatedUserRequestBody(StrictModel):
    visibility: Literal["public", "private"] = Field(default=..., description="Controls whether your primary email address is publicly visible or kept private.")
class UsersSetPrimaryEmailVisibilityForAuthenticatedUserRequest(StrictModel):
    """Configure the visibility setting for your primary email address. Choose whether your primary email is publicly visible or private."""
    body: UsersSetPrimaryEmailVisibilityForAuthenticatedUserRequestBody

# Operation: add_email
class UsersAddEmailForAuthenticatedUserRequestBody(StrictModel):
    body: UsersAddEmailForAuthenticatedUserBody | None = Field(default=None, description="A list of email addresses to add to the user's account. Accepts either an object with an `emails` array or a scalar email string.")
class UsersAddEmailForAuthenticatedUserRequest(StrictModel):
    """Add one or more email addresses to the authenticated user's account. Requires the `user` scope for OAuth app tokens and personal access tokens (classic)."""
    body: UsersAddEmailForAuthenticatedUserRequestBody | None = None

# Operation: delete_email
class UsersDeleteEmailForAuthenticatedUserRequestBody(StrictModel):
    body: UsersDeleteEmailForAuthenticatedUserBody | None = Field(default=None, description="Object containing one or more email addresses to delete from the account. At least one email address is required. Accepts either an object with an `emails` key containing an array of addresses, or a single email address, or an array of email addresses.")
class UsersDeleteEmailForAuthenticatedUserRequest(StrictModel):
    """Remove one or more email addresses from the authenticated user's GitHub account. Requires the `user` scope for OAuth app tokens and personal access tokens (classic)."""
    body: UsersDeleteEmailForAuthenticatedUserRequestBody | None = None

# Operation: check_user_is_followed
class UsersCheckPersonIsFollowedByAuthenticatedRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username to check if it is being followed by the authenticated user.")
class UsersCheckPersonIsFollowedByAuthenticatedRequest(StrictModel):
    """Verify whether the authenticated user is following a specific GitHub user account. Returns true if the user is followed, false otherwise."""
    path: UsersCheckPersonIsFollowedByAuthenticatedRequestPath

# Operation: follow_user
class UsersFollowRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username of the account to follow.")
class UsersFollowRequest(StrictModel):
    """Follow a GitHub user account. Requires the `user:follow` scope for OAuth app tokens and personal access tokens (classic)."""
    path: UsersFollowRequestPath

# Operation: unfollow_user
class UsersUnfollowRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username handle to unfollow.")
class UsersUnfollowRequest(StrictModel):
    """Unfollow a GitHub user. Requires the `user:follow` scope for OAuth app tokens and personal access tokens (classic)."""
    path: UsersUnfollowRequestPath

# Operation: add_gpg_key
class UsersCreateGpgKeyForAuthenticatedUserRequestBody(StrictModel):
    armored_public_key: str = Field(default=..., description="A GPG public key in ASCII-armored format. This is the exported public key block that begins with '-----BEGIN PGP PUBLIC KEY BLOCK-----' and ends with '-----END PGP PUBLIC KEY BLOCK-----'.")
class UsersCreateGpgKeyForAuthenticatedUserRequest(StrictModel):
    """Add a GPG key to the authenticated user's GitHub account. Requires the `write:gpg_key` scope for OAuth apps and personal access tokens (classic)."""
    body: UsersCreateGpgKeyForAuthenticatedUserRequestBody

# Operation: get_gpg_key
class UsersGetGpgKeyForAuthenticatedUserRequestPath(StrictModel):
    gpg_key_id: int = Field(default=..., description="The unique identifier of the GPG key to retrieve.")
class UsersGetGpgKeyForAuthenticatedUserRequest(StrictModel):
    """Retrieve detailed information about a specific GPG key for the authenticated user. Requires the `read:gpg_key` scope for OAuth apps and personal access tokens (classic)."""
    path: UsersGetGpgKeyForAuthenticatedUserRequestPath

# Operation: delete_gpg_key
class UsersDeleteGpgKeyForAuthenticatedUserRequestPath(StrictModel):
    gpg_key_id: int = Field(default=..., description="The unique identifier of the GPG key to delete.")
class UsersDeleteGpgKeyForAuthenticatedUserRequest(StrictModel):
    """Remove a GPG key from the authenticated user's GitHub account. Requires `admin:gpg_key` scope for OAuth apps and personal access tokens (classic)."""
    path: UsersDeleteGpgKeyForAuthenticatedUserRequestPath

# Operation: add_repository_to_installation
class AppsAddRepoToInstallationForAuthenticatedUserRequestPath(StrictModel):
    installation_id: int = Field(default=..., description="The unique identifier of the installation to which the repository will be added.", examples=[1])
    repository_id: int = Field(default=..., description="The unique identifier of the repository to add to the installation.")
class AppsAddRepoToInstallationForAuthenticatedUserRequest(StrictModel):
    """Add a single repository to an app installation. The authenticated user must have admin access to the repository."""
    path: AppsAddRepoToInstallationForAuthenticatedUserRequestPath

# Operation: remove_repository_from_app_installation
class AppsRemoveRepoFromInstallationForAuthenticatedUserRequestPath(StrictModel):
    installation_id: int = Field(default=..., description="The unique identifier of the app installation from which to remove the repository.", examples=[1])
    repository_id: int = Field(default=..., description="The unique identifier of the repository to remove from the installation.")
class AppsRemoveRepoFromInstallationForAuthenticatedUserRequest(StrictModel):
    """Remove a single repository from an app installation. The authenticated user must have admin access to the repository, and the installation must have repository selection set to 'selected'."""
    path: AppsRemoveRepoFromInstallationForAuthenticatedUserRequestPath

# Operation: list_issues_assigned
class IssuesListForAuthenticatedUserRequestQuery(StrictModel):
    filter_: Literal["assigned", "created", "mentioned", "subscribed", "repos", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter issues by type of involvement: assigned to you, created by you, mentioning you, subscribed to, or all visible issues.")
    state: Literal["open", "closed", "all"] | None = Field(default=None, description="Filter issues by their current state: open, closed, or all states.")
    labels: str | None = Field(default=None, description="Filter by one or more labels. Provide as comma-separated label names to match issues with any of the specified labels.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results, either ascending or descending by the sort field.")
    since: str | None = Field(default=None, description="Only return issues updated after this timestamp. Provide in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class IssuesListForAuthenticatedUserRequest(StrictModel):
    """Retrieve issues assigned to the authenticated user across owned and member repositories. Note that pull requests are included in results and can be identified by the `pull_request` key."""
    query: IssuesListForAuthenticatedUserRequestQuery | None = None

# Operation: add_ssh_key
class UsersCreatePublicSshKeyForAuthenticatedUserRequestBody(StrictModel):
    key: str = Field(default=..., description="The public SSH key to add to your GitHub account. Must be in a valid SSH key format (RSA, DSS, ED25519, or ECDSA).", pattern='^ssh-(rsa|dss|ed25519) |^ecdsa-sha2-nistp(256|384|521) ')
class UsersCreatePublicSshKeyForAuthenticatedUserRequest(StrictModel):
    """Add a public SSH key to the authenticated user's GitHub account. Requires the `write:public_key` OAuth scope or personal access token permission."""
    body: UsersCreatePublicSshKeyForAuthenticatedUserRequestBody

# Operation: get_ssh_key
class UsersGetPublicSshKeyForAuthenticatedUserRequestPath(StrictModel):
    key_id: int = Field(default=..., description="The unique identifier of the SSH key to retrieve.")
class UsersGetPublicSshKeyForAuthenticatedUserRequest(StrictModel):
    """Retrieve detailed information about a specific public SSH key for the authenticated user. Requires the `read:public_key` scope."""
    path: UsersGetPublicSshKeyForAuthenticatedUserRequestPath

# Operation: delete_ssh_key
class UsersDeletePublicSshKeyForAuthenticatedUserRequestPath(StrictModel):
    key_id: int = Field(default=..., description="The unique identifier of the SSH key to delete.")
class UsersDeletePublicSshKeyForAuthenticatedUserRequest(StrictModel):
    """Remove a public SSH key from the authenticated user's GitHub account. Requires `admin:public_key` scope for OAuth apps and personal access tokens (classic)."""
    path: UsersDeletePublicSshKeyForAuthenticatedUserRequestPath

# Operation: list_organization_memberships
class OrgsListMembershipsForAuthenticatedUserRequestQuery(StrictModel):
    state: Literal["active", "pending"] | None = Field(default=None, description="Filter memberships by their current state. Returns both active and pending memberships if not specified.")
class OrgsListMembershipsForAuthenticatedUserRequest(StrictModel):
    """Retrieve all organization memberships for the authenticated user. Returns both active and pending memberships by default, or filter by membership state."""
    query: OrgsListMembershipsForAuthenticatedUserRequestQuery | None = None

# Operation: get_organization_membership_authenticated
class OrgsGetMembershipForAuthenticatedUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
class OrgsGetMembershipForAuthenticatedUserRequest(StrictModel):
    """Retrieve the authenticated user's membership status in a specified organization. Returns membership details if the user is an active or pending member, otherwise returns a 404 error."""
    path: OrgsGetMembershipForAuthenticatedUserRequestPath

# Operation: activate_organization_membership
class OrgsUpdateMembershipForAuthenticatedUserRequestPath(StrictModel):
    org: str = Field(default=..., description="The name of the organization. Organization names are case-insensitive.")
class OrgsUpdateMembershipForAuthenticatedUserRequestBody(StrictModel):
    state: Literal["active"] = Field(default=..., description="The desired membership state. Only active membership status is supported.")
class OrgsUpdateMembershipForAuthenticatedUserRequest(StrictModel):
    """Activate an organization membership for the authenticated user by converting a pending invitation to active status. The user must have a pending invitation from the organization to perform this action."""
    path: OrgsUpdateMembershipForAuthenticatedUserRequestPath
    body: OrgsUpdateMembershipForAuthenticatedUserRequestBody

# Operation: get_migration_status_user
class MigrationsGetStatusForAuthenticatedUserRequestPath(StrictModel):
    migration_id: int = Field(default=..., description="The unique identifier of the migration to retrieve status for.")
class MigrationsGetStatusForAuthenticatedUserRequest(StrictModel):
    """Retrieves the current status of a user migration by its unique identifier. The response includes the migration state (pending, exporting, exported, or failed) and can be used to track progress or determine when the migration archive is ready for download."""
    path: MigrationsGetStatusForAuthenticatedUserRequestPath

# Operation: download_migration_archive_user
class MigrationsGetArchiveForAuthenticatedUserRequestPath(StrictModel):
    migration_id: int = Field(default=..., description="The unique identifier of the migration for which to retrieve the archive.")
class MigrationsGetArchiveForAuthenticatedUserRequest(StrictModel):
    """Download a user migration archive as a tar.gz file containing repository data, metadata, and attachments. The archive includes JSON files for various GitHub objects and Git repository data."""
    path: MigrationsGetArchiveForAuthenticatedUserRequestPath

# Operation: delete_migration_archive_user
class MigrationsDeleteArchiveForAuthenticatedUserRequestPath(StrictModel):
    migration_id: int = Field(default=..., description="The unique identifier of the migration whose archive should be deleted.")
class MigrationsDeleteArchiveForAuthenticatedUserRequest(StrictModel):
    """Delete a user migration archive for a completed migration. Downloadable archives are automatically deleted after seven days, but you can manually remove them earlier. Migration metadata remains available even after the archive is deleted."""
    path: MigrationsDeleteArchiveForAuthenticatedUserRequestPath

# Operation: unlock_migration_repository_user
class MigrationsUnlockRepoForAuthenticatedUserRequestPath(StrictModel):
    migration_id: int = Field(default=..., description="The unique identifier of the migration that locked the repository.")
    repo_name: str = Field(default=..., description="The name of the repository to unlock.")
class MigrationsUnlockRepoForAuthenticatedUserRequest(StrictModel):
    """Unlock a repository that was locked during a user migration. After migration completes, unlock repositories to resume normal usage or delete them if no longer needed."""
    path: MigrationsUnlockRepoForAuthenticatedUserRequestPath

# Operation: list_migration_repositories_user
class MigrationsListReposForAuthenticatedUserRequestPath(StrictModel):
    migration_id: int = Field(default=..., description="The unique identifier of the migration for which to retrieve associated repositories.")
class MigrationsListReposForAuthenticatedUserRequest(StrictModel):
    """Lists all repositories associated with a specific user migration. Use this to retrieve the repositories that were migrated as part of a migration operation."""
    path: MigrationsListReposForAuthenticatedUserRequestPath

# Operation: list_packages
class PackagesListPackagesForAuthenticatedUserRequestQuery(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type to filter by. Gradle packages use `maven`, container images pushed to ghcr.io use `container`, and `docker` finds images in the legacy Docker registry even if migrated to Container registry.")
    visibility: Literal["public", "private", "internal"] | None = Field(default=None, description="Filter results by package visibility level. The `internal` visibility is only supported for registries with granular permissions; for other ecosystems it is treated as `private`.")
class PackagesListPackagesForAuthenticatedUserRequest(StrictModel):
    """List all packages owned by the authenticated user within their namespace. Requires `read:packages` scope for OAuth apps and personal access tokens."""
    query: PackagesListPackagesForAuthenticatedUserRequestQuery

# Operation: get_package
class PackagesGetPackageForAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use `maven`, Docker images pushed to GitHub Container Registry use `container`, and `docker` retrieves images from the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to retrieve.")
class PackagesGetPackageForAuthenticatedUserRequest(StrictModel):
    """Retrieve a specific package owned by the authenticated user. Requires `read:packages` scope for OAuth apps and personal access tokens."""
    path: PackagesGetPackageForAuthenticatedUserRequestPath

# Operation: delete_package
class PackagesDeletePackageForAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package type to delete. Gradle packages use 'maven', Docker images pushed to ghcr.io use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to delete.")
class PackagesDeletePackageForAuthenticatedUserRequest(StrictModel):
    """Delete a package owned by the authenticated user. Public packages with more than 5,000 downloads cannot be deleted; contact GitHub support in such cases."""
    path: PackagesDeletePackageForAuthenticatedUserRequestPath

# Operation: restore_package
class PackagesRestorePackageForAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The type of package to restore. Gradle packages use 'maven', container images use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to restore.")
class PackagesRestorePackageForAuthenticatedUserRequest(StrictModel):
    """Restore a deleted package owned by the authenticated user. The package must have been deleted within the last 30 days and the same package namespace and version must still be available."""
    path: PackagesRestorePackageForAuthenticatedUserRequestPath

# Operation: list_package_versions
class PackagesGetAllPackageVersionsForPackageOwnedByAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use `maven`, Docker images pushed to GitHub Container Registry use `container`, and `docker` finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to retrieve versions for.")
class PackagesGetAllPackageVersionsForPackageOwnedByAuthenticatedUserRequestQuery(StrictModel):
    state: Literal["active", "deleted"] | None = Field(default=None, description="Filter package versions by their lifecycle state. Use `active` for current versions or `deleted` for removed versions.")
class PackagesGetAllPackageVersionsForPackageOwnedByAuthenticatedUserRequest(StrictModel):
    """Retrieve all versions of a package owned by the authenticated user. Requires `read:packages` OAuth scope or personal access token (classic) with appropriate permissions."""
    path: PackagesGetAllPackageVersionsForPackageOwnedByAuthenticatedUserRequestPath
    query: PackagesGetAllPackageVersionsForPackageOwnedByAuthenticatedUserRequestQuery | None = None

# Operation: get_package_version
class PackagesGetPackageVersionForAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use `maven`, Docker images pushed to ghcr.io use `container`, and `docker` retrieves images from the legacy Docker registry (docker.pkg.github.com).")
    package_name: str = Field(default=..., description="The name of the package to retrieve.")
    package_version_id: int = Field(default=..., description="The unique numeric identifier of the package version.")
class PackagesGetPackageVersionForAuthenticatedUserRequest(StrictModel):
    """Retrieve a specific package version owned by the authenticated user. Requires `read:packages` scope for OAuth apps and personal access tokens."""
    path: PackagesGetPackageVersionForAuthenticatedUserRequestPath

# Operation: delete_package_version_authenticated
class PackagesDeletePackageVersionForAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package type (e.g., npm, maven, docker). Gradle packages use 'maven', and Container registry images use 'container'.")
    package_name: str = Field(default=..., description="The name of the package to delete a version from.")
    package_version_id: int = Field(default=..., description="The unique identifier of the package version to delete.")
class PackagesDeletePackageVersionForAuthenticatedUserRequest(StrictModel):
    """Delete a specific package version owned by the authenticated user. Public packages with more than 5,000 downloads cannot be deleted; contact GitHub support in such cases."""
    path: PackagesDeletePackageVersionForAuthenticatedUserRequestPath

# Operation: restore_package_version_for_authenticated_user
class PackagesRestorePackageVersionForAuthenticatedUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The type of package registry (npm, Maven, RubyGems, Docker, NuGet, or Container).")
    package_name: str = Field(default=..., description="The name of the package to restore.")
    package_version_id: int = Field(default=..., description="The unique identifier of the package version to restore.")
class PackagesRestorePackageVersionForAuthenticatedUserRequest(StrictModel):
    """Restore a deleted package version for the authenticated user. The package must have been deleted within the last 30 days and the same package namespace and version must still be available."""
    path: PackagesRestorePackageVersionForAuthenticatedUserRequestPath

# Operation: list_repositories
class ReposListForAuthenticatedUserRequestQuery(StrictModel):
    visibility: Literal["all", "public", "private"] | None = Field(default=None, description="Filter repositories by visibility level. Defaults to all repositories regardless of visibility.")
    affiliation: str | None = Field(default=None, description="Filter repositories by the authenticated user's relationship to them. Accepts a comma-separated list of values: owner (owned by user), collaborator (user added as collaborator), or organization_member (accessible through organization membership). Defaults to all three types.")
    type_: Literal["all", "owner", "public", "private", "member"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter repositories by type. Cannot be used together with visibility or affiliation parameters. Defaults to all repository types.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results. Defaults to ascending when sorting by full_name, otherwise descending.")
    since: str | None = Field(default=None, description="Return only repositories updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class ReposListForAuthenticatedUserRequest(StrictModel):
    """List repositories accessible to the authenticated user, including owned repositories, collaborations, and organization memberships. Filter and sort results by visibility, affiliation, type, and update time."""
    query: ReposListForAuthenticatedUserRequestQuery | None = None

# Operation: create_repository
class ReposCreateForAuthenticatedUserRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the repository. This is a required identifier for the repository.")
    description: str | None = Field(default=None, description="A short description of the repository to help others understand its purpose.")
    homepage: str | None = Field(default=None, description="A URL with more information about the repository, such as project documentation or homepage.")
    has_issues: bool | None = Field(default=None, description="Whether issues are enabled for the repository, allowing users to report bugs and request features.")
    has_projects: bool | None = Field(default=None, description="Whether projects are enabled for the repository, allowing project board management.")
    has_wiki: bool | None = Field(default=None, description="Whether the wiki is enabled for the repository, allowing collaborative documentation.")
    has_discussions: bool | None = Field(default=None, description="Whether discussions are enabled for the repository, allowing community conversations.")
    team_id: int | None = Field(default=None, description="The ID of the team that will be granted access to this repository. Only valid when creating a repository in an organization.")
    auto_init: bool | None = Field(default=None, description="Whether the repository is initialized with a minimal README file upon creation.")
    gitignore_template: str | None = Field(default=None, description="The desired language or platform for the .gitignore template to be applied to the repository.")
    license_template: str | None = Field(default=None, description="The license keyword of the open source license to apply to this repository.")
    allow_squash_merge: bool | None = Field(default=None, description="Whether to allow squash merges for pull requests, combining all commits into a single commit.")
    allow_merge_commit: bool | None = Field(default=None, description="Whether to allow merge commits for pull requests, preserving the full commit history.")
    allow_rebase_merge: bool | None = Field(default=None, description="Whether to allow rebase merges for pull requests, replaying commits on top of the base branch.")
    allow_auto_merge: bool | None = Field(default=None, description="Whether to allow auto-merge to be used on pull requests, automatically merging when conditions are met.")
    delete_branch_on_merge: bool | None = Field(default=None, description="Whether to delete head branches when pull requests are merged, keeping the repository clean.")
    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"] | None = Field(default=None, description="The default title format for squash merge commits. Use `PR_TITLE` to default to the pull request's title, or `COMMIT_OR_PR_TITLE` to default to the commit's title (if only one commit) or the pull request's title (when more than one commit).")
    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"] | None = Field(default=None, description="The default message format for squash merge commits. Use `PR_BODY` for the pull request's body, `COMMIT_MESSAGES` for the branch's commit messages, or `BLANK` for a blank message.")
    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"] | None = Field(default=None, description="The default title format for merge commits. Use `PR_TITLE` to default to the pull request's title, or `MERGE_MESSAGE` for the classic merge message format.")
    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"] | None = Field(default=None, description="The default message format for merge commits. Use `PR_BODY` for the pull request's body, `PR_TITLE` for the pull request's title, or `BLANK` for a blank message.")
    is_template: bool | None = Field(default=None, description="Whether this repository acts as a template that can be used to generate new repositories.")
class ReposCreateForAuthenticatedUserRequest(StrictModel):
    """Create a new repository for the authenticated user. Requires `public_repo` or `repo` scope for public repositories, and `repo` scope for private repositories."""
    body: ReposCreateForAuthenticatedUserRequestBody

# Operation: accept_repository_invitation
class ReposAcceptInvitationForAuthenticatedUserRequestPath(StrictModel):
    invitation_id: int = Field(default=..., description="The unique identifier of the repository invitation to accept.")
class ReposAcceptInvitationForAuthenticatedUserRequest(StrictModel):
    """Accept a repository invitation for the authenticated user. This action confirms the user's intent to join the repository and grants them access based on the invitation's permissions."""
    path: ReposAcceptInvitationForAuthenticatedUserRequestPath

# Operation: decline_repository_invitation
class ReposDeclineInvitationForAuthenticatedUserRequestPath(StrictModel):
    invitation_id: int = Field(default=..., description="The unique identifier of the repository invitation to decline.")
class ReposDeclineInvitationForAuthenticatedUserRequest(StrictModel):
    """Decline a repository invitation for the authenticated user. This removes the invitation and prevents the user from accessing the repository."""
    path: ReposDeclineInvitationForAuthenticatedUserRequestPath

# Operation: add_social_accounts
class UsersAddSocialAccountForAuthenticatedUserRequestBody(StrictModel):
    account_urls: list[str] = Field(default=..., description="Array of complete URLs for the social media profiles to add. Each URL should point to a valid social media profile.")
class UsersAddSocialAccountForAuthenticatedUserRequest(StrictModel):
    """Add one or more social media accounts to the authenticated user's profile. Requires the `user` scope for OAuth app tokens and personal access tokens (classic)."""
    body: UsersAddSocialAccountForAuthenticatedUserRequestBody

# Operation: delete_social_accounts
class UsersDeleteSocialAccountForAuthenticatedUserRequestBody(StrictModel):
    account_urls: list[str] = Field(default=..., description="Array of complete URLs for the social media profiles to delete. Each URL should point to the full profile address on the respective social platform.")
class UsersDeleteSocialAccountForAuthenticatedUserRequest(StrictModel):
    """Remove one or more social media accounts from the authenticated user's profile. Requires the `user` OAuth scope."""
    body: UsersDeleteSocialAccountForAuthenticatedUserRequestBody

# Operation: list_starred_repositories
class ActivityListReposStarredByAuthenticatedUserRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for the results. Use ascending to show oldest stars first, or descending to show newest stars first.")
class ActivityListReposStarredByAuthenticatedUserRequest(StrictModel):
    """Retrieve a list of repositories that the authenticated user has starred. Results can be sorted in ascending or descending order by star creation timestamp."""
    query: ActivityListReposStarredByAuthenticatedUserRequestQuery | None = None

# Operation: check_repository_starred
class ActivityCheckRepoIsStarredByAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActivityCheckRepoIsStarredByAuthenticatedUserRequest(StrictModel):
    """Check whether the authenticated user has starred a specific repository. Returns a 204 status if starred, 404 if not."""
    path: ActivityCheckRepoIsStarredByAuthenticatedUserRequestPath

# Operation: star_repository
class ActivityStarRepoForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is not case sensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is not case sensitive.")
class ActivityStarRepoForAuthenticatedUserRequest(StrictModel):
    """Star a repository for the authenticated user. This action marks the repository as starred and adds it to the user's starred list."""
    path: ActivityStarRepoForAuthenticatedUserRequestPath

# Operation: unstar_repository
class ActivityUnstarRepoForAuthenticatedUserRequestPath(StrictModel):
    owner: str = Field(default=..., description="The account owner of the repository. The name is case-insensitive.")
    repo: str = Field(default=..., description="The name of the repository without the `.git` extension. The name is case-insensitive.")
class ActivityUnstarRepoForAuthenticatedUserRequest(StrictModel):
    """Remove a starred repository from the authenticated user's starred list. The repository must have been previously starred by the user."""
    path: ActivityUnstarRepoForAuthenticatedUserRequestPath

# Operation: get_user
class UsersGetByIdRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique numeric identifier for the GitHub user account. This ID is durable and does not change even if the user's login name changes.")
class UsersGetByIdRequest(StrictModel):
    """Retrieve publicly available information about a GitHub user by their account ID. Returns user profile data including name, bio, location, and publicly visible email address if set."""
    path: UsersGetByIdRequestPath

# Operation: create_draft_item_user
class ProjectsCreateDraftItemForAuthenticatedUserRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user who owns the project.")
    project_number: int = Field(default=..., description="The project's number, which uniquely identifies the project within the user's account.")
class ProjectsCreateDraftItemForAuthenticatedUserRequestBody(StrictModel):
    """Details of the draft item to create in the project."""
    title: str = Field(default=..., description="The title of the draft issue item. This is the primary heading for the draft.")
    body: str | None = Field(default=None, description="The body content of the draft issue item. This field provides additional details and context for the draft.")
class ProjectsCreateDraftItemForAuthenticatedUserRequest(StrictModel):
    """Create a draft issue item in a user-owned project. Draft items allow you to prepare issues before formally adding them to the project."""
    path: ProjectsCreateDraftItemForAuthenticatedUserRequestPath
    body: ProjectsCreateDraftItemForAuthenticatedUserRequestBody

# Operation: list_users
class UsersListRequestQuery(StrictModel):
    since: int | None = Field(default=None, description="Filter results to return only users with an ID greater than this value. Use this parameter for pagination by passing the ID of the last user from the previous page.")
class UsersListRequest(StrictModel):
    """Retrieve all users in signup order, including personal and organization accounts. Pagination is controlled exclusively through the `since` parameter using Link headers for subsequent pages."""
    query: UsersListRequestQuery | None = None

# Operation: create_project_view_user
class ProjectsCreateViewForUserRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user who owns the project.")
    project_number: int = Field(default=..., description="The project's number identifier.")
class ProjectsCreateViewForUserRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new view.")
    layout: Literal["table", "board", "roadmap"] = Field(default=..., description="The layout type that determines how project items are displayed.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter query to control which items appear in the view. Use filter syntax to match issues, pull requests, and other project items by status, labels, assignees, and other criteria.")
    visible_fields: list[int] | None = Field(default=None, description="Optional array of field IDs to display in the view. Not applicable for roadmap layouts. If omitted, default visible fields will be used for table and board layouts.")
class ProjectsCreateViewForUserRequest(StrictModel):
    """Create a new view in a user-owned project to customize how items are displayed and filtered. Views support different layouts (table, board, roadmap) and can be configured with filters and visible fields."""
    path: ProjectsCreateViewForUserRequestPath
    body: ProjectsCreateViewForUserRequestBody

# Operation: get_user_by_username
class UsersGetByUsernameRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username handle to look up. Case-insensitive identifier for the user account.")
class UsersGetByUsernameRequest(StrictModel):
    """Retrieve publicly available information about a GitHub user account. Returns profile data including public email if set, with access restrictions for Enterprise Managed Users."""
    path: UsersGetByUsernameRequestPath

# Operation: list_attestations_by_digests_user
class UsersListAttestationsBulkRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose attestations should be retrieved.")
class UsersListAttestationsBulkRequestBody(StrictModel):
    subject_digests: list[str] = Field(default=..., description="List of subject digests to fetch attestations for. Each digest identifies an artifact for which attestations are requested.", min_length=1, max_length=1024)
    predicate_type: str | None = Field(default=None, description="Optional filter to retrieve only attestations matching a specific predicate type. Supports standard types (provenance, sbom, release) or custom freeform text values.")
class UsersListAttestationsBulkRequest(StrictModel):
    """Retrieve artifact attestations for a user across multiple subject digests. Results are filtered based on the authenticated user's repository permissions and require the `attestations:read` permission for fine-grained access tokens."""
    path: UsersListAttestationsBulkRequestPath
    body: UsersListAttestationsBulkRequestBody

# Operation: delete_attestations_user
class UsersDeleteAttestationsBulkRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub user account handle whose attestations will be deleted.")
class UsersDeleteAttestationsBulkRequestBody(StrictModel):
    body: UsersDeleteAttestationsBulkBodyV0 | UsersDeleteAttestationsBulkBodyV1 = Field(default=..., description="Request payload containing deletion criteria. Provide either an array of subject digests (in format algorithm:hexvalue) or an array of attestation IDs, but not both.", examples=[{'subject_digests': ['sha256:abc123', 'sha512:def456']}, {'attestation_ids': [111, 222]}])
class UsersDeleteAttestationsBulkRequest(StrictModel):
    """Remove artifact attestations in bulk for a GitHub user by specifying either subject digests or attestation IDs. Exactly one of these criteria must be provided."""
    path: UsersDeleteAttestationsBulkRequestPath
    body: UsersDeleteAttestationsBulkRequestBody

# Operation: delete_attestation_by_subject_digest_user
class UsersDeleteAttestationsBySubjectDigestRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) of the account whose attestation should be deleted.")
    subject_digest: str = Field(default=..., description="The subject digest that uniquely identifies the attestation to delete.")
class UsersDeleteAttestationsBySubjectDigestRequest(StrictModel):
    """Delete an artifact attestation for a GitHub user by its subject digest. This removes the attestation record associated with the specified digest."""
    path: UsersDeleteAttestationsBySubjectDigestRequestPath

# Operation: delete_attestation_user
class UsersDeleteAttestationsByIdRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) of the account that owns the repository containing the attestation.")
    attestation_id: int = Field(default=..., description="The unique identifier of the attestation to delete.")
class UsersDeleteAttestationsByIdRequest(StrictModel):
    """Delete an artifact attestation by ID that is associated with a repository owned by a user. This operation removes the attestation record permanently."""
    path: UsersDeleteAttestationsByIdRequestPath

# Operation: list_attestations_user
class UsersListAttestationsRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub user account handle whose repositories will be searched for attestations.")
    subject_digest: str = Field(default=..., description="The cryptographic digest identifying the artifact subject for which to retrieve attestations.")
class UsersListAttestationsRequestQuery(StrictModel):
    predicate_type: str | None = Field(default=None, description="Filter attestations by predicate type to narrow results to specific attestation categories or custom types.")
class UsersListAttestationsRequest(StrictModel):
    """Retrieve artifact attestations for a specific subject digest across repositories owned by a user. Results are filtered based on the authenticated user's repository access permissions and require cryptographic verification before use."""
    path: UsersListAttestationsRequestPath
    query: UsersListAttestationsRequestQuery | None = None

# Operation: list_user_events
class ActivityListEventsForAuthenticatedUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose events should be listed.")
class ActivityListEventsForAuthenticatedUserRequest(StrictModel):
    """List events for a GitHub user. If authenticated as the specified user, private events are included; otherwise only public events are returned. Note: This API is not optimized for real-time use cases and may have latency of 30 seconds to 6 hours depending on time of day."""
    path: ActivityListEventsForAuthenticatedUserRequestPath

# Operation: list_organization_events_for_user
class ActivityListOrgEventsForAuthenticatedUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose organization events should be retrieved. The authenticated user must have access to view this user's organization dashboard.")
    org: str = Field(default=..., description="The organization name to filter events for. Organization names are case-insensitive.")
class ActivityListOrgEventsForAuthenticatedUserRequest(StrictModel):
    """Retrieve organization events for the authenticated user. This endpoint provides the user's organization dashboard view and requires authentication as the specified user."""
    path: ActivityListOrgEventsForAuthenticatedUserRequestPath

# Operation: list_user_public_events
class ActivityListPublicEventsForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) for the user whose public events you want to retrieve.")
class ActivityListPublicEventsForUserRequest(StrictModel):
    """Retrieve a list of public events for a GitHub user. Note: This API is not optimized for real-time use cases and may have event latency ranging from 30 seconds to 6 hours depending on the time of day."""
    path: ActivityListPublicEventsForUserRequestPath

# Operation: list_followers_by_username
class UsersListFollowersForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose followers you want to retrieve.")
class UsersListFollowersForUserRequest(StrictModel):
    """Retrieves a list of users who are following the specified GitHub user account."""
    path: UsersListFollowersForUserRequestPath

# Operation: list_following
class UsersListFollowingForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) of the user whose following list should be retrieved.")
class UsersListFollowingForUserRequest(StrictModel):
    """Retrieves the list of users that a specified GitHub user follows. This provides insight into the accounts and projects a user is interested in tracking."""
    path: UsersListFollowingForUserRequestPath

# Operation: check_user_following
class UsersCheckFollowingForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username of the user whose following list will be checked.")
    target_user: str = Field(default=..., description="The GitHub username of the target user to check if they are being followed.")
class UsersCheckFollowingForUserRequest(StrictModel):
    """Determine whether a specific user follows another user on GitHub. Returns true if the follower relationship exists, false otherwise."""
    path: UsersCheckFollowingForUserRequestPath

# Operation: list_user_gists
class GistsListForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose gists should be listed.")
class GistsListForUserRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Filter results to show only gists last updated after this timestamp in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class GistsListForUserRequest(StrictModel):
    """Retrieve all public gists created by a specified GitHub user. Results can be filtered to show only gists updated after a given timestamp."""
    path: GistsListForUserRequestPath
    query: GistsListForUserRequestQuery | None = None

# Operation: list_gpg_keys_by_username
class UsersListGpgKeysForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose GPG keys should be retrieved.")
class UsersListGpgKeysForUserRequest(StrictModel):
    """Retrieve all GPG keys associated with a GitHub user account. This information is publicly accessible."""
    path: UsersListGpgKeysForUserRequestPath

# Operation: get_user_hovercard
class UsersGetContextForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username handle for the user whose hovercard information you want to retrieve.")
class UsersGetContextForUserRequestQuery(StrictModel):
    subject_type: Literal["organization", "repository", "issue", "pull_request"] | None = Field(default=None, description="The type of subject context to include in the hovercard response. When specified, must be paired with the corresponding subject_id to provide relationship context.")
    subject_id: str | None = Field(default=None, description="The unique identifier for the subject specified in subject_type. Required when subject_type is provided to establish the contextual relationship.")
class UsersGetContextForUserRequest(StrictModel):
    """Retrieve contextual information about a GitHub user, including their activity related to pull requests, issues, repositories, and organizations. Optionally provide subject context (repository, organization, issue, or pull request) to get more detailed relationship information."""
    path: UsersGetContextForUserRequestPath
    query: UsersGetContextForUserRequestQuery | None = None

# Operation: get_user_installation
class AppsGetUserInstallationRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) for which to retrieve the app installation information.")
class AppsGetUserInstallationRequest(StrictModel):
    """Retrieve the authenticated GitHub App's installation information for a specific user. Requires JWT authentication as a GitHub App."""
    path: AppsGetUserInstallationRequestPath

# Operation: list_public_keys
class UsersListPublicKeysForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose public keys should be retrieved.")
class UsersListPublicKeysForUserRequest(StrictModel):
    """Retrieves all verified public SSH keys for a GitHub user. This endpoint is publicly accessible and does not require authentication."""
    path: UsersListPublicKeysForUserRequestPath

# Operation: list_user_organizations
class OrgsListForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) for the user whose public organization memberships you want to retrieve.")
class OrgsListForUserRequest(StrictModel):
    """List public organization memberships for a specified GitHub user. This operation only returns public memberships; use the authenticated user organizations endpoint to retrieve both public and private memberships for the current user."""
    path: OrgsListForUserRequestPath

# Operation: list_user_packages
class PackagesListPackagesForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose packages to list.")
class PackagesListPackagesForUserRequestQuery(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type to filter by. Gradle packages use `maven`, Docker images in the Container registry use `container`, and `docker` finds images in the legacy Docker registry.")
    visibility: Literal["public", "private", "internal"] | None = Field(default=None, description="Filter results by package visibility level. The `internal` visibility is only supported for registries with granular permissions; for other ecosystems it is treated as `private`.")
class PackagesListPackagesForUserRequest(StrictModel):
    """Retrieve all packages in a user's namespace that the requesting user has access to. Requires `read:packages` OAuth scope or personal access token (classic)."""
    path: PackagesListPackagesForUserRequestPath
    query: PackagesListPackagesForUserRequestQuery

# Operation: get_package_public
class PackagesGetPackageForUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use `maven`, Docker images pushed to GitHub Container Registry use `container`, and `docker` retrieves images from the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to retrieve.")
    username: str = Field(default=..., description="The GitHub username of the package owner.")
class PackagesGetPackageForUserRequest(StrictModel):
    """Retrieve metadata for a specific package owned by a user. Requires `read:packages` scope for OAuth app tokens or personal access tokens (classic)."""
    path: PackagesGetPackageForUserRequestPath

# Operation: delete_user_package
class PackagesDeletePackageForUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. Gradle packages use 'maven', Docker images pushed to ghcr.io use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to delete.")
    username: str = Field(default=..., description="The GitHub username of the package owner.")
class PackagesDeletePackageForUserRequest(StrictModel):
    """Delete an entire package for a user. Public packages with more than 5,000 downloads cannot be deleted; contact GitHub support in such cases. Admin permissions are required for registries with granular permissions."""
    path: PackagesDeletePackageForUserRequestPath

# Operation: restore_package_for_user
class PackagesRestorePackageForUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. GitHub's Gradle registry uses 'maven', Container registry uses 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to restore.")
    username: str = Field(default=..., description="The GitHub username of the package owner.")
class PackagesRestorePackageForUserRequest(StrictModel):
    """Restore a deleted package for a user. The package must have been deleted within the last 30 days and the same package namespace and version must still be available and not reused."""
    path: PackagesRestorePackageForUserRequestPath

# Operation: list_package_versions_public
class PackagesGetAllPackageVersionsForPackageOwnedByUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package ecosystem type. Gradle packages use `maven`, Docker images pushed to GitHub Container Registry use `container`, and `docker` finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to retrieve versions for.")
    username: str = Field(default=..., description="The GitHub username of the package owner.")
class PackagesGetAllPackageVersionsForPackageOwnedByUserRequest(StrictModel):
    """Retrieve all versions of a public package owned by a specified user. Requires `read:packages` OAuth scope or personal access token (classic)."""
    path: PackagesGetAllPackageVersionsForPackageOwnedByUserRequestPath

# Operation: get_package_version_public
class PackagesGetPackageVersionForUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package ecosystem type. Gradle packages use `maven`, Docker images pushed to ghcr.io use `container`, and `docker` retrieves images from the legacy Docker registry (docker.pkg.github.com).")
    package_name: str = Field(default=..., description="The name of the package to retrieve.")
    package_version_id: int = Field(default=..., description="The unique numeric identifier for the specific package version.")
    username: str = Field(default=..., description="The GitHub username of the package owner.")
class PackagesGetPackageVersionForUserRequest(StrictModel):
    """Retrieve a specific version of a public package owned by a user. Requires `read:packages` OAuth scope or personal access token (classic)."""
    path: PackagesGetPackageVersionForUserRequestPath

# Operation: delete_package_version_user
class PackagesDeletePackageVersionForUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The package registry type. GitHub's Gradle registry uses 'maven', Container registry uses 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to delete a version from.")
    username: str = Field(default=..., description="The GitHub username of the account that owns the package.")
    package_version_id: int = Field(default=..., description="The unique identifier of the package version to delete.")
class PackagesDeletePackageVersionForUserRequest(StrictModel):
    """Delete a specific package version for a user account. Public packages with more than 5,000 downloads cannot be deleted; contact GitHub support for assistance in such cases."""
    path: PackagesDeletePackageVersionForUserRequestPath

# Operation: restore_package_version_for_user
class PackagesRestorePackageVersionForUserRequestPath(StrictModel):
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"] = Field(default=..., description="The type of package registry. Gradle packages use 'maven', Docker images pushed to GitHub's Container registry use 'container', and 'docker' finds images in the legacy Docker registry.")
    package_name: str = Field(default=..., description="The name of the package to restore.")
    username: str = Field(default=..., description="The GitHub username of the package owner.")
    package_version_id: int = Field(default=..., description="The unique identifier of the package version to restore.")
class PackagesRestorePackageVersionForUserRequest(StrictModel):
    """Restore a deleted package version for a user. The package must have been deleted within the last 30 days and the same package namespace and version must still be available."""
    path: PackagesRestorePackageVersionForUserRequestPath

# Operation: list_user_projects
class ProjectsListForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose projects should be listed.")
class ProjectsListForUserRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="Filter results to include only projects of a specified type.")
class ProjectsListForUserRequest(StrictModel):
    """Retrieve all projects owned by a specific GitHub user that are accessible to the authenticated user. Optionally filter results by project type."""
    path: ProjectsListForUserRequestPath
    query: ProjectsListForUserRequestQuery | None = None

# Operation: get_user_project
class ProjectsGetForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The unique numeric identifier for the project within the user's project collection.")
    username: str = Field(default=..., description="The GitHub username (handle) of the user who owns the project.")
class ProjectsGetForUserRequest(StrictModel):
    """Retrieve a specific project owned by a GitHub user. Returns detailed information about the project identified by its number."""
    path: ProjectsGetForUserRequestPath

# Operation: list_project_fields_user
class ProjectsListFieldsForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The numeric identifier of the GitHub Projects (V2) board.")
    username: str = Field(default=..., description="The GitHub username of the project owner.")
class ProjectsListFieldsForUserRequest(StrictModel):
    """Retrieve all fields configured for a specific user-owned GitHub Projects (V2) board. Fields define the custom properties and metadata available for tracking issues and pull requests within the project."""
    path: ProjectsListFieldsForUserRequestPath

# Operation: add_project_field_user
class ProjectsAddFieldForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username of the project owner.")
    project_number: int = Field(default=..., description="The numeric identifier of the project.")
class ProjectsAddFieldForUserRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the field to create.")
    data_type: Literal["date", "iteration", "number", "single_select", "text"] = Field(default=..., description="The data type for the field. Single select fields require at least one option to be provided via single_select_options.")
    single_select_options: list[Any] | None = Field(default=None, description="The list of options available for single select fields. Required when data_type is 'single_select'. Each option should be provided as a distinct item in the array.")
    iteration_configuration: ProjectsAddFieldForUserBodyIterationConfiguration | None = Field(default=None, description="Configuration settings for iteration fields, such as duration and start date. Required when data_type is 'iteration'.")
class ProjectsAddFieldForUserRequest(StrictModel):
    """Add a new field to a user-owned GitHub project. The field can be of various types including text, number, date, iteration, or single select with configurable options."""
    path: ProjectsAddFieldForUserRequestPath
    body: ProjectsAddFieldForUserRequestBody

# Operation: get_project_field_user
class ProjectsGetFieldForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier within the user's account.")
    field_id: int = Field(default=..., description="The unique identifier of the field to retrieve from the project.")
    username: str = Field(default=..., description="The GitHub username (handle) of the account that owns the project.")
class ProjectsGetFieldForUserRequest(StrictModel):
    """Retrieve a specific field from a user-owned GitHub Projects (V2) board. Fields define custom properties and metadata for project items."""
    path: ProjectsGetFieldForUserRequestPath

# Operation: list_project_items_user
class ProjectsListItemsForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The numeric identifier for the project.")
    username: str = Field(default=..., description="The GitHub username of the project owner.")
class ProjectsListItemsForUserRequestQuery(StrictModel):
    q: str | None = Field(default=None, description="Filter items using a search query. Supports the same filtering syntax as GitHub Projects views.")
    fields: str | list[str] | None = Field(default=None, description="Restrict results to specific fields by their IDs. When omitted, only the title field is returned. Accepts multiple field IDs as comma-separated values or repeated query parameters.")
class ProjectsListItemsForUserRequest(StrictModel):
    """List all items in a user-owned project. Retrieve project items with optional filtering by search query and field selection."""
    path: ProjectsListItemsForUserRequestPath
    query: ProjectsListItemsForUserRequestQuery | None = None

# Operation: add_item_to_project_user
class ProjectsAddItemForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username of the project owner.")
    project_number: int = Field(default=..., description="The project's unique number identifier.")
class ProjectsAddItemForUserRequestBody(StrictModel):
    """Details of the item to add to the project. You can specify either the unique ID or the repository owner, name, and issue/PR number."""
    type_: Literal["Issue", "PullRequest"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of item being added to the project.")
class ProjectsAddItemForUserRequest(StrictModel):
    """Add an issue or pull request to a user-owned project. The item will be added to the specified project by its number."""
    path: ProjectsAddItemForUserRequestPath
    body: ProjectsAddItemForUserRequestBody

# Operation: get_project_item_user
class ProjectsGetUserItemRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier.")
    username: str = Field(default=..., description="The GitHub username of the project owner.")
    item_id: int = Field(default=..., description="The unique identifier of the project item to retrieve.")
class ProjectsGetUserItemRequestQuery(StrictModel):
    fields: str | list[str] | None = Field(default=None, description="Comma-separated or repeated field IDs to include in the response. If not specified, only the title field is returned.")
class ProjectsGetUserItemRequest(StrictModel):
    """Retrieve a specific item from a user-owned project. Returns the item's details including selected fields or the title field by default."""
    path: ProjectsGetUserItemRequestPath
    query: ProjectsGetUserItemRequestQuery | None = None

# Operation: update_project_item_user
class ProjectsUpdateItemForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project's unique number identifier.")
    username: str = Field(default=..., description="The GitHub username or handle of the account that owns the project.")
    item_id: int = Field(default=..., description="The unique identifier of the project item to update.")
class ProjectsUpdateItemForUserRequestBody(StrictModel):
    """Field updates to apply to the project item. Only text, number, date, single select, and iteration fields are supported."""
    fields: list[ProjectsUpdateItemForUserBodyFieldsItem] = Field(default=..., description="An array of field updates to apply to the item. Each entry specifies a field and its new value.")
class ProjectsUpdateItemForUserRequest(StrictModel):
    """Update a specific item in a user-owned project by applying field changes. Allows modification of item properties within a GitHub Projects V2 board."""
    path: ProjectsUpdateItemForUserRequestPath
    body: ProjectsUpdateItemForUserRequestBody

# Operation: delete_project_item_user
class ProjectsDeleteItemForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The project number that identifies which project to modify. This is a unique numeric identifier for the project.")
    username: str = Field(default=..., description="The GitHub username of the account that owns the project. This is the handle used to identify the user account.")
    item_id: int = Field(default=..., description="The unique numeric identifier of the project item to delete. This identifies which specific item within the project should be removed.")
class ProjectsDeleteItemForUserRequest(StrictModel):
    """Delete a specific item from a user's project. This operation removes the item permanently from the project."""
    path: ProjectsDeleteItemForUserRequestPath

# Operation: list_project_view_items_user
class ProjectsListViewItemsForUserRequestPath(StrictModel):
    project_number: int = Field(default=..., description="The numeric identifier for the project.")
    username: str = Field(default=..., description="The GitHub username or account handle.")
    view_number: int = Field(default=..., description="The numeric identifier for the project view.")
class ProjectsListViewItemsForUserRequestQuery(StrictModel):
    fields: str | list[str] | None = Field(default=None, description="Restrict results to specific fields by their IDs. When omitted, only the title field is returned. Accepts multiple field IDs as comma-separated values or repeated query parameters.")
class ProjectsListViewItemsForUserRequest(StrictModel):
    """List items in a user's project view with the view's saved filters applied. Returns project items matching the specified view's configuration."""
    path: ProjectsListViewItemsForUserRequestPath
    query: ProjectsListViewItemsForUserRequestQuery | None = None

# Operation: list_received_events
class ActivityListReceivedEventsForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose received events should be listed.")
class ActivityListReceivedEventsForUserRequest(StrictModel):
    """Retrieve events received by a user through watching repositories and following other users. Private events are visible only to the authenticated user; otherwise only public events are returned. Note: This API is not real-time; event latency can range from 30 seconds to 6 hours depending on time of day."""
    path: ActivityListReceivedEventsForUserRequestPath

# Operation: list_user_public_received_events
class ActivityListReceivedPublicEventsForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) for the user account whose received public events should be listed.")
class ActivityListReceivedPublicEventsForUserRequest(StrictModel):
    """Retrieve a list of public events received by a GitHub user. Note: This API is not optimized for real-time use cases and may have event latency ranging from 30 seconds to 6 hours depending on time of day."""
    path: ActivityListReceivedPublicEventsForUserRequestPath

# Operation: list_user_repositories
class ReposListForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose repositories should be listed.")
class ReposListForUserRequestQuery(StrictModel):
    type_: Literal["all", "owner", "member"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter repositories by type. Use 'owner' to show only repositories owned by the user, 'member' for repositories where the user is a collaborator, or 'all' for both.")
    direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for the results. Use 'asc' for ascending order or 'desc' for descending order.")
class ReposListForUserRequest(StrictModel):
    """Lists public repositories for a specified GitHub user. Results can be filtered by repository type and sorted in ascending or descending order."""
    path: ReposListForUserRequestPath
    query: ReposListForUserRequestQuery | None = None

# Operation: get_premium_request_usage_report_user
class BillingGetGithubBillingPremiumRequestUsageReportUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username for which to retrieve the premium request usage report.")
class BillingGetGithubBillingPremiumRequestUsageReportUserRequestQuery(StrictModel):
    year: int | None = Field(default=None, description="Filter results to a specific year. Must be a four-digit year value. If not specified, defaults to the current year.")
    month: int | None = Field(default=None, description="Filter results to a specific month within the year. Must be a value between 1 and 12. If not specified, defaults to the current month.")
    day: int | None = Field(default=None, description="Filter results to a specific day within the month. Must be a value between 1 and 31. If not specified, defaults to the current day.")
    model: str | None = Field(default=None, description="Filter results by AI model name. The filter is case-insensitive.")
    product: str | None = Field(default=None, description="Filter results by product name. The filter is case-insensitive.")
class BillingGetGithubBillingPremiumRequestUsageReportUserRequest(StrictModel):
    """Retrieve a premium request usage report for a GitHub user, with optional filtering by time period, model, or product. Only data from the past 24 months is available."""
    path: BillingGetGithubBillingPremiumRequestUsageReportUserRequestPath
    query: BillingGetGithubBillingPremiumRequestUsageReportUserRequestQuery | None = None

# Operation: get_billing_usage_report
class BillingGetGithubBillingUsageReportUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username for which to retrieve the billing usage report.")
class BillingGetGithubBillingUsageReportUserRequestQuery(StrictModel):
    year: int | None = Field(default=None, description="Filter results to a specific year. Specify as a four-digit integer representing the year (e.g., 2025). Defaults to the current year if not provided.")
    month: int | None = Field(default=None, description="Filter results to a specific month within the year. Specify as an integer between 1 and 12. Only applies when year is specified or defaults to the current year.")
    day: int | None = Field(default=None, description="Filter results to a specific day within the month. Specify as an integer between 1 and 31. Only applies when month is specified or defaults to the current year and month.")
class BillingGetGithubBillingUsageReportUserRequest(StrictModel):
    """Retrieve a billing usage report for a GitHub user, optionally filtered by year, month, or day. This endpoint is only available to users with access to the enhanced billing platform."""
    path: BillingGetGithubBillingUsageReportUserRequestPath
    query: BillingGetGithubBillingUsageReportUserRequestQuery | None = None

# Operation: get_billing_usage_summary_user
class BillingGetGithubBillingUsageSummaryReportUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username for the account to retrieve billing usage for.")
class BillingGetGithubBillingUsageSummaryReportUserRequestQuery(StrictModel):
    year: int | None = Field(default=None, description="Filter results to a specific year. Specify as a four-digit year value. Defaults to the current year if not provided.")
    month: int | None = Field(default=None, description="Filter results to a specific month within the year. Specify as an integer between 1 and 12. Defaults to the current month if not provided.")
    day: int | None = Field(default=None, description="Filter results to a specific day within the month. Specify as an integer between 1 and 31. Defaults to the current day if not provided.")
    product: str | None = Field(default=None, description="Filter results by product name. The product name is case-insensitive.")
    sku: str | None = Field(default=None, description="Filter results by SKU (stock keeping unit) identifier.")
class BillingGetGithubBillingUsageSummaryReportUserRequest(StrictModel):
    """Retrieve a summary report of billing usage for a GitHub user account. Only data from the past 24 months is accessible via this endpoint."""
    path: BillingGetGithubBillingUsageSummaryReportUserRequestPath
    query: BillingGetGithubBillingUsageSummaryReportUserRequestQuery | None = None

# Operation: list_social_accounts_public
class UsersListSocialAccountsForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username (handle) for the user whose social accounts should be retrieved.")
class UsersListSocialAccountsForUserRequest(StrictModel):
    """Retrieves all social media accounts associated with a GitHub user. This endpoint is publicly accessible and requires only the username."""
    path: UsersListSocialAccountsForUserRequestPath

# Operation: list_ssh_signing_keys_for_user
class UsersListSshSigningKeysForUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose SSH signing keys should be retrieved.")
class UsersListSshSigningKeysForUserRequest(StrictModel):
    """Retrieve all SSH signing keys associated with a GitHub user account. This operation is publicly accessible and does not require authentication."""
    path: UsersListSshSigningKeysForUserRequestPath

# Operation: list_starred_repositories_by_user
class ActivityListReposStarredByUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose starred repositories should be listed.")
class ActivityListReposStarredByUserRequestQuery(StrictModel):
    direction: Literal["asc", "desc"] | None = Field(default=None, description="The order in which to sort the starred repositories.")
class ActivityListReposStarredByUserRequest(StrictModel):
    """Retrieve repositories that a user has starred. Supports sorting by creation timestamp when using the star+json media type."""
    path: ActivityListReposStarredByUserRequestPath
    query: ActivityListReposStarredByUserRequestQuery | None = None

# Operation: list_watched_repositories_by_user
class ActivityListReposWatchedByUserRequestPath(StrictModel):
    username: str = Field(default=..., description="The GitHub username whose watched repositories should be listed.")
class ActivityListReposWatchedByUserRequest(StrictModel):
    """Retrieves a list of repositories that a user is watching. Watched repositories allow users to receive notifications about activity without being a collaborator."""
    path: ActivityListReposWatchedByUserRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AppPermissions(PermissiveModel):
    """The permissions granted to the user access token."""
    actions: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for GitHub Actions workflows, workflow runs, and artifacts.")
    administration: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for repository creation, deletion, settings, teams, and collaborators creation.")
    checks: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for checks on code.")
    codespaces: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to create, edit, delete, and list Codespaces.")
    contents: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for repository contents, commits, branches, downloads, releases, and merges.")
    dependabot_secrets: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage Dependabot secrets.")
    deployments: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for deployments and deployment statuses.")
    environments: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for managing repository environments.")
    issues: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for issues and related comments, assignees, labels, and milestones.")
    metadata: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to search repositories, list collaborators, and access repository metadata.")
    packages: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for packages published to GitHub Packages.")
    pages: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to retrieve Pages statuses, configuration, and builds, as well as create new builds.")
    pull_requests: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for pull requests and related comments, assignees, labels, milestones, and merges.")
    repository_custom_properties: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and edit custom properties for a repository, when allowed by the property.")
    repository_hooks: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage the post-receive hooks for a repository.")
    repository_projects: Literal["read", "write", "admin"] | None = Field(None, description="The level of permission to grant the access token to manage repository projects, columns, and cards.")
    secret_scanning_alerts: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage secret scanning alerts.")
    secrets: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage repository secrets.")
    security_events: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage security events like code scanning alerts.")
    single_file: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage just a single file.")
    statuses: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for commit statuses.")
    vulnerability_alerts: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage Dependabot alerts.")
    workflows: Literal["write"] | None = Field(None, description="The level of permission to grant the access token to update GitHub Actions workflow files.")
    members: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for organization teams and members.")
    organization_administration: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage access to an organization.")
    organization_custom_roles: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for custom repository roles management.")
    organization_custom_org_roles: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for custom organization roles management.")
    organization_custom_properties: Literal["read", "write", "admin"] | None = Field(None, description="The level of permission to grant the access token for custom property management.")
    organization_copilot_seat_management: Literal["write"] | None = Field(None, description="The level of permission to grant the access token for managing access to GitHub Copilot for members of an organization with a Copilot Business subscription. This property is in public preview and is subject to change.")
    organization_announcement_banners: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage announcement banners for an organization.")
    organization_events: Literal["read"] | None = Field(None, description="The level of permission to grant the access token to view events triggered by an activity in an organization.")
    organization_hooks: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage the post-receive hooks for an organization.")
    organization_personal_access_tokens: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for viewing and managing fine-grained personal access token requests to an organization.")
    organization_personal_access_token_requests: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for viewing and managing fine-grained personal access tokens that have been approved by an organization.")
    organization_plan: Literal["read"] | None = Field(None, description="The level of permission to grant the access token for viewing an organization's plan.")
    organization_projects: Literal["read", "write", "admin"] | None = Field(None, description="The level of permission to grant the access token to manage organization projects and projects public preview (where available).")
    organization_packages: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token for organization packages published to GitHub Packages.")
    organization_secrets: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage organization secrets.")
    organization_self_hosted_runners: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage GitHub Actions self-hosted runners available to an organization.")
    organization_user_blocking: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage users blocked by the organization.")
    team_discussions: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage team discussions and related comments.")
    email_addresses: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage the email addresses belonging to a user.")
    followers: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage the followers belonging to a user.")
    git_ssh_keys: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to manage git SSH keys.")
    gpg_keys: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage GPG keys belonging to a user.")
    interaction_limits: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to view and manage interaction limits on a repository.")
    profile: Literal["write"] | None = Field(None, description="The level of permission to grant the access token to manage the profile settings belonging to a user.")
    starring: Literal["read", "write"] | None = Field(None, description="The level of permission to grant the access token to list and manage repositories a user is starring.")

class CampaignsCreateCampaignBodyCodeScanningAlertsItem(StrictModel):
    repository_id: int = Field(..., description="The repository id")
    alert_numbers: list[int] = Field(..., description="The alert numbers", min_length=1)

class ChecksCreateBodyV0(PermissiveModel):
    status: Literal["completed"]

class ChecksCreateBodyV1(PermissiveModel):
    status: Literal["queued", "in_progress"] | None = None

class ChecksUpdateBodyV0(PermissiveModel):
    status: Literal["completed"] | None = None

class ChecksUpdateBodyV1(PermissiveModel):
    status: Literal["queued", "in_progress"] | None = None

class CodeOfConduct(PermissiveModel):
    """Code Of Conduct"""
    key: str
    name: str
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    body: str | None = None
    html_url: str | None = Field(..., json_schema_extra={'format': 'uri'})

class CodeSecurityUpdateConfigurationBodySecretScanningDelegatedBypassOptionsReviewersItem(PermissiveModel):
    reviewer_id: int = Field(..., description="The ID of the team or role selected as a bypass reviewer")
    reviewer_type: Literal["TEAM", "ROLE"] = Field(..., description="The type of the bypass reviewer")

class CodespacesCreateForAuthenticatedUserBodyV0(PermissiveModel):
    repository_id: int = Field(..., description="Repository id for this codespace")
    ref: str | None = Field(None, description="Git ref (typically a branch name) for this codespace")
    location: str | None = Field(None, description="The requested location for a new codespace. Best efforts are made to respect this upon creation. Assigned by IP if not provided.")
    geo: Literal["EuropeWest", "SoutheastAsia", "UsEast", "UsWest"] | None = Field(None, description="The geographic area for this codespace. If not specified, the value is assigned by IP. This property replaces `location`, which is closing down.")
    client_ip: str | None = Field(None, description="IP for location auto-detection when proxying a request")
    machine: str | None = Field(None, description="Machine type to use for this codespace")
    devcontainer_path: str | None = Field(None, description="Path to devcontainer.json config to use for this codespace")
    multi_repo_permissions_opt_out: bool | None = Field(None, description="Whether to authorize requested permissions from devcontainer.json")
    working_directory: str | None = Field(None, description="Working directory for this codespace")
    idle_timeout_minutes: int | None = Field(None, description="Time in minutes before codespace stops from inactivity")
    display_name: str | None = Field(None, description="Display name for this codespace")
    retention_period_minutes: int | None = Field(None, description="Duration in minutes after codespace has gone idle in which it will be deleted. Must be integer minutes between 0 and 43200 (30 days).")

class CodespacesCreateForAuthenticatedUserBodyV1PullRequest(PermissiveModel):
    """Pull request number for this codespace"""
    pull_request_number: int = Field(..., description="Pull request number")
    repository_id: int = Field(..., description="Repository id for this codespace")

class CodespacesCreateForAuthenticatedUserBodyV1(PermissiveModel):
    pull_request: CodespacesCreateForAuthenticatedUserBodyV1PullRequest = Field(..., description="Pull request number for this codespace")
    location: str | None = Field(None, description="The requested location for a new codespace. Best efforts are made to respect this upon creation. Assigned by IP if not provided.")
    geo: Literal["EuropeWest", "SoutheastAsia", "UsEast", "UsWest"] | None = Field(None, description="The geographic area for this codespace. If not specified, the value is assigned by IP. This property replaces `location`, which is closing down.")
    machine: str | None = Field(None, description="Machine type to use for this codespace")
    devcontainer_path: str | None = Field(None, description="Path to devcontainer.json config to use for this codespace")
    working_directory: str | None = Field(None, description="Working directory for this codespace")
    idle_timeout_minutes: int | None = Field(None, description="Time in minutes before codespace stops from inactivity")

class Contributor(PermissiveModel):
    """Contributor"""
    login: str | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id")
    node_id: str | None = None
    avatar_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    gravatar_id: str | None = None
    url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    html_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    followers_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    following_url: str | None = None
    gists_url: str | None = None
    starred_url: str | None = None
    subscriptions_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    organizations_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    repos_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    events_url: str | None = None
    received_events_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    site_admin: bool | None = None
    contributions: int
    email: str | None = None
    name: str | None = None
    user_view_type: str | None = None

class CustomPropertyValue(PermissiveModel):
    """Custom property name and associated value"""
    property_name: str = Field(..., description="The name of the property")
    value: str | list[str] | None = Field(..., description="The value assigned to the property")

class Enterprise(PermissiveModel):
    """An enterprise on GitHub."""
    description: str | None = Field(None, description="A short description of the enterprise.")
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    website_url: str | None = Field(None, description="The enterprise's website URL.", json_schema_extra={'format': 'uri'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the enterprise")
    node_id: str
    name: str = Field(..., description="The name of the enterprise.")
    slug: str = Field(..., description="The slug url identifier for the enterprise.")
    created_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    avatar_url: str = Field(..., json_schema_extra={'format': 'uri'})

class GistsCreateBodyFilesValue(PermissiveModel):
    content: str = Field(..., description="Content of the file")

class GistsUpdateBodyFilesValue(PermissiveModel):
    content: str | None = Field(None, description="The new content of the file.")
    filename: str | None = Field(None, description="The new filename for the file.")

class GitCreateTreeBodyTreeItem(PermissiveModel):
    path: str | None = Field(None, description="The file referenced in the tree.")
    mode: Literal["100644", "100755", "040000", "160000", "120000"] | None = Field(None, description="The file mode; one of `100644` for file (blob), `100755` for executable (blob), `040000` for subdirectory (tree), `160000` for submodule (commit), or `120000` for a blob that specifies the path of a symlink.")
    type_: Literal["blob", "tree", "commit"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Either `blob`, `tree`, or `commit`.")
    sha: str | None = Field(None, description="The SHA1 checksum ID of the object in the tree. Also called `tree.sha`. If the value is `null` then the file will be deleted.  \n  \n**Note:** Use either `tree.sha` or `content` to specify the contents of the entry. Using both `tree.sha` and `content` will return an error.")
    content: str | None = Field(None, description="The content you want this file to have. GitHub will write this blob out and use that SHA for this entry. Use either this, or `tree.sha`.  \n  \n**Note:** Use either `tree.sha` or `content` to specify the contents of the entry. Using both `tree.sha` and `content` will return an error.")

class HookResponse(PermissiveModel):
    code: int | None = Field(...)
    status: str | None = Field(...)
    message: str | None = Field(...)

class IssueDependenciesSummary(PermissiveModel):
    blocked_by: int
    blocking: int
    total_blocked_by: int
    total_blocking: int

class IssueFieldValueSingleSelectOption(PermissiveModel):
    """Details about the selected option (only present for single_select fields)"""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for the option.", json_schema_extra={'format': 'int64'})
    name: str = Field(..., description="The name of the option")
    color: str = Field(..., description="The color of the option")

class IssueFieldValue(PermissiveModel):
    """A value assigned to an issue field"""
    issue_field_id: int = Field(..., description="Unique identifier for the issue field.", json_schema_extra={'format': 'int64'})
    node_id: str
    data_type: Literal["text", "single_select", "number", "date"] = Field(..., description="The data type of the issue field")
    value: str | float | int | None = Field(..., description="The value of the issue field")
    single_select_option: IssueFieldValueSingleSelectOption | None = Field(None, description="Details about the selected option (only present for single_select fields)")

class IssueLabelsItemV1(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str | None = None
    url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    name: str | None = None
    description: str | None = None
    color: str | None = None
    default: bool | None = None

class IssuePullRequest(PermissiveModel):
    merged_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    diff_url: str | None = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str | None = Field(..., json_schema_extra={'format': 'uri'})
    patch_url: str | None = Field(..., json_schema_extra={'format': 'uri'})
    url: str | None = Field(..., json_schema_extra={'format': 'uri'})

class IssueType(PermissiveModel):
    """The type of issue."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier of the issue type.")
    node_id: str = Field(..., description="The node identifier of the issue type.")
    name: str = Field(..., description="The name of the issue type.")
    description: str | None = Field(..., description="The description of the issue type.")
    color: Literal["gray", "blue", "green", "yellow", "orange", "red", "pink", "purple"] | None = Field(None, description="The color of the issue type.")
    created_at: str | None = Field(None, description="The time the issue type created.", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, description="The time the issue type last updated.", json_schema_extra={'format': 'date-time'})
    is_enabled: bool | None = Field(None, description="The enabled state of the issue type.")

class IssuesAddIssueFieldValuesBodyIssueFieldValuesItem(StrictModel):
    field_id: int = Field(..., description="The ID of the issue field to set")
    value: str | float = Field(..., description="The value to set for the field. The type depends on the field's data type:\n- For text fields: provide a string value\n- For single_select fields: provide the option name as a string (must match an existing option)\n- For number fields: provide a numeric value\n- For date fields: provide an ISO 8601 date string")

class IssuesAddLabelsBodyV0(PermissiveModel):
    labels: list[str] | None = Field(None, description="The names of the labels to add to the issue's existing labels. You can pass an empty array to remove all labels. Alternatively, you can pass a single label as a `string` or an `array` of labels directly, but GitHub recommends passing an object with the `labels` key. You can also replace all of the labels for an issue. For more information, see \"[Set labels for an issue](https://docs.github.com/rest/issues/labels#set-labels-for-an-issue).\"", min_length=1)

class IssuesAddLabelsBodyV2Item(PermissiveModel):
    name: str

class IssuesCreateBodyLabelsItem(PermissiveModel):
    """Also accepts scalar shorthand."""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    description: str | None = None
    color: str | None = None

class IssuesSetIssueFieldValuesBodyIssueFieldValuesItem(StrictModel):
    field_id: int = Field(..., description="The ID of the issue field to set")
    value: str | float = Field(..., description="The value to set for the field. The type depends on the field's data type:\n- For text fields: provide a string value\n- For single_select fields: provide the option name as a string (must match an existing option)\n- For number fields: provide a numeric value\n- For date fields: provide an ISO 8601 date string")

class IssuesSetLabelsBody(PermissiveModel):
    """Also accepts scalar shorthand."""
    labels: list[str] | None = Field(None, description="The names of the labels to set for the issue. The labels you set replace any existing labels. You can pass an empty array to remove all labels. Alternatively, you can pass a single label as a `string` or an `array` of labels directly, but GitHub recommends passing an object with the `labels` key. You can also add labels to the existing labels for an issue. For more information, see \"[Add labels to an issue](https://docs.github.com/rest/issues/labels#add-labels-to-an-issue).\"", min_length=1)

class IssuesUpdateBodyIssueFieldValuesItem(StrictModel):
    field_id: int = Field(..., description="The ID of the issue field to set")
    value: str = Field(..., description="The value to set for the field Also accepts: number.")

class IssuesUpdateBodyLabelsItem(PermissiveModel):
    """Also accepts scalar shorthand."""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    description: str | None = None
    color: str | None = None

class Key(PermissiveModel):
    """Key"""
    key: str
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    url: str
    title: str
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    verified: bool
    read_only: bool
    last_used: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class Link(PermissiveModel):
    """Hypermedia Link"""
    href: str

class ManifestFile(StrictModel):
    source_location: str | None = Field(None, description="The path of the manifest file relative to the root of the Git repository.")

class Metadata(RootModel[dict[str, str | float | bool]]):
    pass

class Dependency(StrictModel):
    package_url: str | None = Field(None, description="Package-url (PURL) of dependency. See https://github.com/package-url/purl-spec for more details.", pattern="^pkg")
    metadata: Metadata | None = None
    relationship: Literal["direct", "indirect"] | None = Field(None, description="A notation of whether a dependency is requested directly by this manifest or is a dependency of another dependency.")
    scope: Literal["runtime", "development"] | None = Field(None, description="A notation of whether the dependency is required for the primary build artifact (runtime) or is only used for development. Future versions of this specification may allow for more granular scopes.")
    dependencies: list[str] | None = Field(None, description="Array of package-url (PURLs) of direct child dependencies.")

class Manifest(StrictModel):
    name: str = Field(..., description="The name of the manifest.")
    file_: ManifestFile | None = Field(None, validation_alias="file", serialization_alias="file")
    metadata: Metadata | None = None
    resolved: dict[str, Dependency] | None = Field(None, description="A collection of resolved package dependencies.")

class NullableIntegrationPermissions(PermissiveModel):
    """The set of permissions for the GitHub app"""
    issues: str | None = None
    checks: str | None = None
    metadata: str | None = None
    contents: str | None = None
    deployments: str | None = None

class NullableLicenseSimple(PermissiveModel):
    """License Simple"""
    key: str
    name: str
    url: str | None = Field(..., json_schema_extra={'format': 'uri'})
    spdx_id: str | None = Field(...)
    node_id: str
    html_url: str | None = Field(None, json_schema_extra={'format': 'uri'})

class NullableMinimalRepositoryLicense(PermissiveModel):
    key: str | None = None
    name: str | None = None
    spdx_id: str | None = None
    url: str | None = None
    node_id: str | None = None

class NullableMinimalRepositoryPermissions(PermissiveModel):
    admin: bool | None = None
    maintain: bool | None = None
    push: bool | None = None
    triage: bool | None = None
    pull: bool | None = None

class NullableSimpleUser(PermissiveModel):
    """A GitHub user."""
    name: str | None = None
    email: str | None = None
    login: str
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str
    avatar_url: str = Field(..., json_schema_extra={'format': 'uri'})
    gravatar_id: str | None = Field(...)
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    followers_url: str = Field(..., json_schema_extra={'format': 'uri'})
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str = Field(..., json_schema_extra={'format': 'uri'})
    organizations_url: str = Field(..., json_schema_extra={'format': 'uri'})
    repos_url: str = Field(..., json_schema_extra={'format': 'uri'})
    events_url: str
    received_events_url: str = Field(..., json_schema_extra={'format': 'uri'})
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    site_admin: bool
    starred_at: str | None = None
    user_view_type: str | None = None

class NullableMilestone(PermissiveModel):
    """A collection of related issues and pull requests."""
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    labels_url: str = Field(..., json_schema_extra={'format': 'uri'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id")
    node_id: str
    number: int = Field(..., description="The number of the milestone.")
    state: Literal["open", "closed"] = Field(..., description="The state of the milestone.")
    title: str = Field(..., description="The title of the milestone.")
    description: str | None = Field(...)
    creator: NullableSimpleUser
    open_issues: int
    closed_issues: int
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    closed_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    due_on: str | None = Field(..., json_schema_extra={'format': 'date-time'})

class NullableTeamSimple(PermissiveModel):
    """Groups of organization members that gives permissions on specified repositories."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the team")
    node_id: str
    url: str = Field(..., description="URL for the team", json_schema_extra={'format': 'uri'})
    members_url: str
    name: str = Field(..., description="Name of the team")
    description: str | None = Field(..., description="Description of the team")
    permission: str = Field(..., description="Permission that the team will have for its repositories")
    privacy: str | None = Field(None, description="The level of privacy this team should have")
    notification_setting: str | None = Field(None, description="The notification setting the team has set")
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    repositories_url: str = Field(..., json_schema_extra={'format': 'uri'})
    slug: str
    ldap_dn: str | None = Field(None, description="Distinguished Name (DN) that team maps to within LDAP environment")

class OrgsCreateIssueFieldBodyOptionsItem(PermissiveModel):
    name: str = Field(..., description="Name of the option.")
    description: str | None = Field(None, description="Description of the option.")
    color: Literal["gray", "blue", "green", "yellow", "orange", "red", "pink", "purple"] = Field(..., description="Color for the option.")
    priority: int = Field(..., description="Priority of the option for ordering.")

class OrgsDeleteAttestationsBulkBodyV0(PermissiveModel):
    subject_digests: list[str] = Field(..., description="List of subject digests associated with the artifact attestations to delete.", min_length=1, max_length=1024)

class OrgsDeleteAttestationsBulkBodyV1(PermissiveModel):
    attestation_ids: list[int] = Field(..., description="List of unique IDs associated with the artifact attestations to delete.", min_length=1, max_length=1024)

class OrgsSetClusterDeploymentRecordsBodyDeploymentsItem(PermissiveModel):
    name: str = Field(..., description="The name of the artifact. Note that if multiple deployments have identical 'digest' parameter values,\nthe name parameter must also be identical across all entries.\n", min_length=1, max_length=256)
    digest: str = Field(..., description="The hex encoded digest of the artifact. Note that if multiple deployments have identical 'digest' parameter values,\nthe name and version parameters must also be identical across all entries.\n", min_length=71, max_length=71, pattern="^sha256:[a-f0-9]{64}$")
    version: str | None = Field(None, description="The artifact version. Note that if multiple deployments have identical 'digest' parameter values,\nthe version parameter must also be identical across all entries.\n", max_length=100)
    status: Literal["deployed", "decommissioned"] | None = Field('deployed', description="The deployment status of the artifact.")
    deployment_name: str = Field(..., description="The unique identifier for the deployment represented by the new record. To accommodate differing\ncontainers and namespaces within a record set, the following format is recommended:\n{namespaceName}-{deploymentName}-{containerName}.\nThe deployment_name must be unique across all entries in the deployments array.\n", min_length=1, max_length=256)
    github_repository: str | None = Field(None, description="The name of the GitHub repository associated with the artifact. This should be used\nwhen there are no provenance attestations available for the artifact. The repository\nmust belong to the organization specified in the path parameter.\n\nIf a provenance attestation is available for the artifact, the API will use\nthe repository information from the attestation instead of this parameter.", max_length=100, pattern="^[A-Za-z0-9.\\-_]+$")
    tags: dict[str, str] | None = Field(None, description="Key-value pairs to tag the deployment record.")
    runtime_risks: Annotated[list[Literal["critical-resource", "internet-exposed", "lateral-movement", "sensitive-data"]], AfterValidator(_check_unique_items)] | None = Field(None, description="A list of runtime risks associated with the deployment.", max_length=4)

class ProjectsAddFieldForOrgBodyV0(StrictModel):
    issue_field_id: int = Field(..., description="The ID of the IssueField to create the field for.")

class ProjectsAddFieldForOrgBodyV1(StrictModel):
    name: str = Field(..., description="The name of the field.")
    data_type: Literal["text", "number", "date"] = Field(..., description="The field's data type.")

class ProjectsAddFieldForOrgBodyV2(StrictModel):
    name: str = Field(..., description="The name of the field.")
    data_type: Literal["single_select"] = Field(..., description="The field's data type.")
    single_select_options: list[Any] = Field(..., description="The options available for single select fields. At least one option must be provided when creating a single select field.")

class ProjectsAddFieldForOrgBodyV3IterationConfigurationIterationsItem(StrictModel):
    title: str | None = Field(None, description="The title of the iteration.")
    start_date: str | None = Field(None, description="The start date of the iteration.", json_schema_extra={'format': 'date'})
    duration: int | None = Field(None, description="The duration of the iteration in days.")

class ProjectsAddFieldForOrgBodyV3IterationConfiguration(PermissiveModel):
    """The configuration for iteration fields."""
    start_date: str | None = Field(None, description="The start date of the first iteration.", json_schema_extra={'format': 'date'})
    duration: int | None = Field(None, description="The default duration for iterations in days. Individual iterations can override this value.")
    iterations: list[ProjectsAddFieldForOrgBodyV3IterationConfigurationIterationsItem] | None = Field(None, description="Zero or more iterations for the field.")

class ProjectsAddFieldForOrgBodyV3(StrictModel):
    name: str = Field(..., description="The name of the field.")
    data_type: Literal["iteration"] = Field(..., description="The field's data type.")
    iteration_configuration: ProjectsAddFieldForOrgBodyV3IterationConfiguration = Field(..., description="The configuration for iteration fields.")

class ProjectsAddFieldForUserBodyIterationConfigurationIterationsItem(StrictModel):
    title: str | None = Field(None, description="The title of the iteration.")
    start_date: str | None = Field(None, description="The start date of the iteration.", json_schema_extra={'format': 'date'})
    duration: int | None = Field(None, description="The duration of the iteration in days.")

class ProjectsAddFieldForUserBodyIterationConfiguration(PermissiveModel):
    """The configuration for iteration fields."""
    start_date: str | None = Field(None, description="The start date of the first iteration.", json_schema_extra={'format': 'date'})
    duration: int | None = Field(None, description="The default duration for iterations in days. Individual iterations can override this value.")
    iterations: list[ProjectsAddFieldForUserBodyIterationConfigurationIterationsItem] | None = Field(None, description="Zero or more iterations for the field.")

class ProjectsUpdateItemForOrgBodyFieldsItem(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the project field to update.")
    value: str | float | None = Field(..., description="The new value for the field:\n- For text, number, and date fields, provide the new value directly.\n- For single select and iteration fields, provide the ID of the option or iteration.\n- To clear the field, set this to null.")

class ProjectsUpdateItemForUserBodyFieldsItem(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the project field to update.")
    value: str | float | None = Field(..., description="The new value for the field:\n- For text, number, and date fields, provide the new value directly.\n- For single select and iteration fields, provide the ID of the option or iteration.\n- To clear the field, set this to null.")

class PullRequestLabelsItem(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str
    url: str
    name: str
    description: str | None = Field(...)
    color: str
    default: bool

class PullRequestLinks(PermissiveModel):
    comments: Link
    commits: Link
    statuses: Link
    html: Link
    issue: Link
    review_comments: Link
    review_comment: Link
    self: Link

class ReactionRollup(PermissiveModel):
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    total_count: int
    plus_one: int = Field(..., validation_alias="+1", serialization_alias="+1")
    minus_one: int = Field(..., validation_alias="-1", serialization_alias="-1")
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int

class ReposAddTeamAccessRestrictionsBodyV0(PermissiveModel):
    teams: list[str] = Field(..., description="The slug values for teams")

class ReposRemoveStatusCheckContextsBodyV0(PermissiveModel):
    contexts: list[str] = Field(..., description="The name of the status checks")

class ReposRemoveTeamAccessRestrictionsBodyV0(PermissiveModel):
    teams: list[str] = Field(..., description="The slug values for teams")

class ReposSetTeamAccessRestrictionsBodyV0(PermissiveModel):
    teams: list[str] = Field(..., description="The slug values for teams")

class ReposUpdateBodySecurityAndAnalysisSecretScanningDelegatedBypassOptionsReviewersItem(PermissiveModel):
    reviewer_id: int = Field(..., description="The ID of the team or role selected as a bypass reviewer")
    reviewer_type: Literal["TEAM", "ROLE"] = Field(..., description="The type of the bypass reviewer")

class ReposUpdateBranchProtectionBodyRequiredStatusChecksChecksItem(PermissiveModel):
    context: str = Field(..., description="The name of the required check")
    app_id: int | None = Field(None, description="The ID of the GitHub App that must provide this check. Omit this field to automatically select the GitHub App that has recently provided this check, or any app if it was not set by a GitHub App. Pass -1 to explicitly allow any app to set the status.")

class RepositoryCodeSearchIndexStatus(PermissiveModel):
    """The status of the code search index for this repository"""
    lexical_search_ok: bool | None = None
    lexical_commit_sha: str | None = None

class RepositoryPermissions(PermissiveModel):
    admin: bool
    pull: bool
    triage: bool | None = None
    push: bool
    maintain: bool | None = None

class SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItemPackage(PermissiveModel):
    """The name of the package affected by the vulnerability."""
    ecosystem: Literal["rubygems", "npm", "pip", "maven", "nuget", "composer", "go", "rust", "erlang", "actions", "pub", "other", "swift"] = Field(..., description="The package's language or package management ecosystem.")
    name: str | None = Field(None, description="The unique package name within its ecosystem.")

class SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItem(StrictModel):
    package: SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItemPackage = Field(..., description="The name of the package affected by the vulnerability.")
    vulnerable_version_range: str | None = Field(None, description="The range of the package versions affected by the vulnerability.")
    patched_versions: str | None = Field(None, description="The package version(s) that resolve the vulnerability.")
    vulnerable_functions: list[str] | None = Field(None, description="The functions in the package that are affected.")

class SecurityAdvisoriesCreateRepositoryAdvisoryBodyCreditsItem(StrictModel):
    login: str = Field(..., description="The username of the user credited.")
    type_: Literal["analyst", "finder", "reporter", "coordinator", "remediation_developer", "remediation_reviewer", "remediation_verifier", "tool", "sponsor", "other"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of credit the user is receiving.")

class SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItemPackage(PermissiveModel):
    """The name of the package affected by the vulnerability."""
    ecosystem: Literal["rubygems", "npm", "pip", "maven", "nuget", "composer", "go", "rust", "erlang", "actions", "pub", "other", "swift"] = Field(..., description="The package's language or package management ecosystem.")
    name: str | None = Field(None, description="The unique package name within its ecosystem.")

class SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItem(StrictModel):
    package: SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItemPackage = Field(..., description="The name of the package affected by the vulnerability.")
    vulnerable_version_range: str | None = Field(None, description="The range of the package versions affected by the vulnerability.")
    patched_versions: str | None = Field(None, description="The package version(s) that resolve the vulnerability.")
    vulnerable_functions: list[str] | None = Field(None, description="The functions in the package that are affected.")

class SecurityAdvisoriesUpdateRepositoryAdvisoryBodyCreditsItem(StrictModel):
    login: str = Field(..., description="The username of the user credited.")
    type_: Literal["analyst", "finder", "reporter", "coordinator", "remediation_developer", "remediation_reviewer", "remediation_verifier", "tool", "sponsor", "other"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of credit the user is receiving.")

class SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItemPackage(PermissiveModel):
    """The name of the package affected by the vulnerability."""
    ecosystem: Literal["rubygems", "npm", "pip", "maven", "nuget", "composer", "go", "rust", "erlang", "actions", "pub", "other", "swift"] = Field(..., description="The package's language or package management ecosystem.")
    name: str | None = Field(None, description="The unique package name within its ecosystem.")

class SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItem(StrictModel):
    package: SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItemPackage = Field(..., description="The name of the package affected by the vulnerability.")
    vulnerable_version_range: str | None = Field(None, description="The range of the package versions affected by the vulnerability.")
    patched_versions: str | None = Field(None, description="The package version(s) that resolve the vulnerability.")
    vulnerable_functions: list[str] | None = Field(None, description="The functions in the package that are affected.")

class SecurityAndAnalysisAdvancedSecurity(PermissiveModel):
    """Enable or disable GitHub Advanced Security for the repository.

For standalone Code Scanning or Secret Protection products, this parameter cannot be used.
"""
    status: Literal["enabled", "disabled"] | None = None

class SecurityAndAnalysisCodeSecurity(PermissiveModel):
    status: Literal["enabled", "disabled"] | None = None

class SecurityAndAnalysisDependabotSecurityUpdates(PermissiveModel):
    """Enable or disable Dependabot security updates for the repository."""
    status: Literal["enabled", "disabled"] | None = Field(None, description="The enablement status of Dependabot security updates for the repository.")

class SecurityAndAnalysisSecretScanning(PermissiveModel):
    status: Literal["enabled", "disabled"] | None = None

class SecurityAndAnalysisSecretScanningAiDetection(PermissiveModel):
    status: Literal["enabled", "disabled"] | None = None

class SecurityAndAnalysisSecretScanningNonProviderPatterns(PermissiveModel):
    status: Literal["enabled", "disabled"] | None = None

class SecurityAndAnalysisSecretScanningPushProtection(PermissiveModel):
    status: Literal["enabled", "disabled"] | None = None

class SecurityAndAnalysis(PermissiveModel):
    advanced_security: SecurityAndAnalysisAdvancedSecurity | None = Field(None, description="Enable or disable GitHub Advanced Security for the repository.\n\nFor standalone Code Scanning or Secret Protection products, this parameter cannot be used.\n")
    code_security: SecurityAndAnalysisCodeSecurity | None = None
    dependabot_security_updates: SecurityAndAnalysisDependabotSecurityUpdates | None = Field(None, description="Enable or disable Dependabot security updates for the repository.")
    secret_scanning: SecurityAndAnalysisSecretScanning | None = None
    secret_scanning_push_protection: SecurityAndAnalysisSecretScanningPushProtection | None = None
    secret_scanning_non_provider_patterns: SecurityAndAnalysisSecretScanningNonProviderPatterns | None = None
    secret_scanning_ai_detection: SecurityAndAnalysisSecretScanningAiDetection | None = None

class SimpleClassroomOrganization(PermissiveModel):
    """A GitHub organization."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id")
    login: str
    node_id: str
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    name: str | None = Field(...)
    avatar_url: str

class Classroom(PermissiveModel):
    """A GitHub Classroom classroom"""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the classroom.")
    name: str = Field(..., description="The name of the classroom.")
    archived: bool = Field(..., description="Whether classroom is archived.")
    organization: SimpleClassroomOrganization
    url: str = Field(..., description="The URL of the classroom on GitHub Classroom.")

class SimpleUser(PermissiveModel):
    """A GitHub user."""
    name: str | None = None
    email: str | None = None
    login: str
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str
    avatar_url: str = Field(..., json_schema_extra={'format': 'uri'})
    gravatar_id: str | None = Field(...)
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    followers_url: str = Field(..., json_schema_extra={'format': 'uri'})
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str = Field(..., json_schema_extra={'format': 'uri'})
    organizations_url: str = Field(..., json_schema_extra={'format': 'uri'})
    repos_url: str = Field(..., json_schema_extra={'format': 'uri'})
    events_url: str
    received_events_url: str = Field(..., json_schema_extra={'format': 'uri'})
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    site_admin: bool
    starred_at: str | None = None
    user_view_type: str | None = None

class AutoMerge(PermissiveModel):
    """The status of auto merging a pull request."""
    enabled_by: SimpleUser
    merge_method: Literal["merge", "squash", "rebase"] = Field(..., description="The merge method to use.")
    commit_title: str = Field(..., description="Title for the merge commit message.")
    commit_message: str = Field(..., description="Commit message for the merge commit.")

class NullableIntegration(PermissiveModel):
    """GitHub apps are a new way to extend GitHub. They can be installed directly on organizations and user accounts and granted access to specific repositories. They come with granular permissions and built-in webhooks. GitHub apps are first class actors within GitHub."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the GitHub app")
    slug: str | None = Field(None, description="The slug name of the GitHub app")
    node_id: str
    client_id: str | None = None
    owner: SimpleUser | Enterprise
    name: str = Field(..., description="The name of the GitHub app")
    description: str | None = Field(...)
    external_url: str = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    permissions: dict[str, str] = Field(..., description="The set of permissions for the GitHub app")
    events: list[str] = Field(..., description="The list of events for the GitHub app. Note that the `installation_target`, `security_advisory`, and `meta` events are not included because they are global events and not specific to an installation.")
    installations_count: int | None = Field(None, description="The number of installations associated with the GitHub app. Only returned when the integration is requesting details about itself.")

class Deployment(PermissiveModel):
    """A request for a specific ref(branch,sha,tag) to be deployed"""
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the deployment", json_schema_extra={'format': 'int64'})
    node_id: str
    sha: str
    ref: str = Field(..., description="The ref to deploy. This can be a branch, tag, or sha.")
    task: str = Field(..., description="Parameter to specify a task to execute")
    payload: dict[str, Any] | str
    original_environment: str | None = None
    environment: str = Field(..., description="Name for the target deployment environment.")
    description: str | None = Field(...)
    creator: NullableSimpleUser
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    statuses_url: str = Field(..., json_schema_extra={'format': 'uri'})
    repository_url: str = Field(..., json_schema_extra={'format': 'uri'})
    transient_environment: bool | None = Field(None, description="Specifies if the given environment is will no longer exist at some point in the future. Default: false.")
    production_environment: bool | None = Field(None, description="Specifies if the given environment is one that end-users directly interact with. Default: false.")
    performed_via_github_app: NullableIntegration | None = None

class NullableMinimalRepository(PermissiveModel):
    """Minimal Repository"""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str
    name: str
    full_name: str
    owner: SimpleUser
    private: bool
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    description: str | None = Field(...)
    fork: bool
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str = Field(..., json_schema_extra={'format': 'uri'})
    deployments_url: str = Field(..., json_schema_extra={'format': 'uri'})
    downloads_url: str = Field(..., json_schema_extra={'format': 'uri'})
    events_url: str = Field(..., json_schema_extra={'format': 'uri'})
    forks_url: str = Field(..., json_schema_extra={'format': 'uri'})
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str | None = None
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str = Field(..., json_schema_extra={'format': 'uri'})
    merges_url: str = Field(..., json_schema_extra={'format': 'uri'})
    milestones_url: str
    notifications_url: str
    pulls_url: str
    releases_url: str
    ssh_url: str | None = None
    stargazers_url: str = Field(..., json_schema_extra={'format': 'uri'})
    statuses_url: str
    subscribers_url: str = Field(..., json_schema_extra={'format': 'uri'})
    subscription_url: str = Field(..., json_schema_extra={'format': 'uri'})
    tags_url: str = Field(..., json_schema_extra={'format': 'uri'})
    teams_url: str = Field(..., json_schema_extra={'format': 'uri'})
    trees_url: str
    clone_url: str | None = None
    mirror_url: str | None = None
    hooks_url: str = Field(..., json_schema_extra={'format': 'uri'})
    svn_url: str | None = None
    homepage: str | None = None
    language: str | None = None
    forks_count: int | None = None
    stargazers_count: int | None = None
    watchers_count: int | None = None
    size: int | None = Field(None, description="The size of the repository, in kilobytes. Size is calculated hourly. When a repository is initially created, the size is 0.")
    default_branch: str | None = None
    open_issues_count: int | None = None
    is_template: bool | None = None
    topics: list[str] | None = None
    has_issues: bool | None = None
    has_projects: bool | None = None
    has_wiki: bool | None = None
    has_pages: bool | None = None
    has_downloads: bool | None = None
    has_discussions: bool | None = None
    archived: bool | None = None
    disabled: bool | None = None
    visibility: str | None = None
    pushed_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    created_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    permissions: NullableMinimalRepositoryPermissions | None = None
    role_name: str | None = None
    temp_clone_token: str | None = None
    delete_branch_on_merge: bool | None = None
    subscribers_count: int | None = None
    network_count: int | None = None
    code_of_conduct: CodeOfConduct | None = None
    license_: NullableMinimalRepositoryLicense | None = Field(None, validation_alias="license", serialization_alias="license")
    forks: int | None = None
    open_issues: int | None = None
    watchers: int | None = None
    allow_forking: bool | None = None
    web_commit_signoff_required: bool | None = None
    security_and_analysis: SecurityAndAnalysis | None = None
    custom_properties: dict[str, Any] | None = Field(None, description="The custom properties that were defined for the repository. The keys are the custom property names, and the values are the corresponding custom property values.")

class Package(PermissiveModel):
    """A software package"""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the package.")
    name: str = Field(..., description="The name of the package.")
    package_type: Literal["npm", "maven", "rubygems", "docker", "nuget", "container"]
    url: str
    html_url: str
    version_count: int = Field(..., description="The number of versions of the package.")
    visibility: Literal["private", "public"]
    owner: NullableSimpleUser | None = None
    repository: NullableMinimalRepository | None = None
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})

class Repository(PermissiveModel):
    """A repository on GitHub."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the repository", json_schema_extra={'format': 'int64'})
    node_id: str
    name: str = Field(..., description="The name of the repository.")
    full_name: str
    license_: NullableLicenseSimple = Field(..., validation_alias="license", serialization_alias="license")
    forks: int
    permissions: RepositoryPermissions | None = None
    owner: SimpleUser
    private: bool = Field(..., description="Whether the repository is private or public.")
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    description: str | None = Field(...)
    fork: bool
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str = Field(..., json_schema_extra={'format': 'uri'})
    deployments_url: str = Field(..., json_schema_extra={'format': 'uri'})
    downloads_url: str = Field(..., json_schema_extra={'format': 'uri'})
    events_url: str = Field(..., json_schema_extra={'format': 'uri'})
    forks_url: str = Field(..., json_schema_extra={'format': 'uri'})
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str = Field(..., json_schema_extra={'format': 'uri'})
    merges_url: str = Field(..., json_schema_extra={'format': 'uri'})
    milestones_url: str
    notifications_url: str
    pulls_url: str
    releases_url: str
    ssh_url: str
    stargazers_url: str = Field(..., json_schema_extra={'format': 'uri'})
    statuses_url: str
    subscribers_url: str = Field(..., json_schema_extra={'format': 'uri'})
    subscription_url: str = Field(..., json_schema_extra={'format': 'uri'})
    tags_url: str = Field(..., json_schema_extra={'format': 'uri'})
    teams_url: str = Field(..., json_schema_extra={'format': 'uri'})
    trees_url: str
    clone_url: str
    mirror_url: str | None = Field(..., json_schema_extra={'format': 'uri'})
    hooks_url: str = Field(..., json_schema_extra={'format': 'uri'})
    svn_url: str = Field(..., json_schema_extra={'format': 'uri'})
    homepage: str | None = Field(..., json_schema_extra={'format': 'uri'})
    language: str | None = Field(...)
    forks_count: int
    stargazers_count: int
    watchers_count: int
    size: int = Field(..., description="The size of the repository, in kilobytes. Size is calculated hourly. When a repository is initially created, the size is 0.")
    default_branch: str = Field(..., description="The default branch of the repository.")
    open_issues_count: int
    is_template: bool | None = Field(False, description="Whether this repository acts as a template that can be used to generate new repositories.")
    topics: list[str] | None = None
    has_issues: bool = Field(..., description="Whether issues are enabled.")
    has_projects: bool = Field(..., description="Whether projects are enabled.")
    has_wiki: bool = Field(..., description="Whether the wiki is enabled.")
    has_pages: bool
    has_downloads: bool = Field(..., description="Whether downloads are enabled.")
    has_discussions: bool | None = Field(False, description="Whether discussions are enabled.")
    archived: bool = Field(..., description="Whether the repository is archived.")
    disabled: bool = Field(..., description="Returns whether or not this repository disabled.")
    visibility: str | None = Field('public', description="The repository visibility: public, private, or internal.")
    pushed_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    created_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    allow_rebase_merge: bool | None = Field(True, description="Whether to allow rebase merges for pull requests.")
    temp_clone_token: str | None = None
    allow_squash_merge: bool | None = Field(True, description="Whether to allow squash merges for pull requests.")
    allow_auto_merge: bool | None = Field(False, description="Whether to allow Auto-merge to be used on pull requests.")
    delete_branch_on_merge: bool | None = Field(False, description="Whether to delete head branches when pull requests are merged")
    allow_update_branch: bool | None = Field(False, description="Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to be up to date before merging.")
    use_squash_pr_title_as_default: bool | None = Field(False, description="Whether a squash merge commit can use the pull request title as default. **This property is closing down. Please use `squash_merge_commit_title` instead.")
    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"] | None = Field(None, description="The default value for a squash merge commit title:\n\n- `PR_TITLE` - default to the pull request's title.\n- `COMMIT_OR_PR_TITLE` - default to the commit's title (if only one commit) or the pull request's title (when more than one commit).")
    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"] | None = Field(None, description="The default value for a squash merge commit message:\n\n- `PR_BODY` - default to the pull request's body.\n- `COMMIT_MESSAGES` - default to the branch's commit messages.\n- `BLANK` - default to a blank commit message.")
    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"] | None = Field(None, description="The default value for a merge commit title.\n\n- `PR_TITLE` - default to the pull request's title.\n- `MERGE_MESSAGE` - default to the classic title for a merge message (e.g., Merge pull request #123 from branch-name).")
    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"] | None = Field(None, description="The default value for a merge commit message.\n\n- `PR_TITLE` - default to the pull request's title.\n- `PR_BODY` - default to the pull request's body.\n- `BLANK` - default to a blank commit message.")
    allow_merge_commit: bool | None = Field(True, description="Whether to allow merge commits for pull requests.")
    allow_forking: bool | None = Field(None, description="Whether to allow forking this repo")
    web_commit_signoff_required: bool | None = Field(False, description="Whether to require contributors to sign off on web-based commits")
    open_issues: int
    watchers: int
    master_branch: str | None = None
    starred_at: str | None = None
    anonymous_access_enabled: bool | None = Field(None, description="Whether anonymous git access is enabled for this repository")
    code_search_index_status: RepositoryCodeSearchIndexStatus | None = Field(None, description="The status of the code search index for this repository")

class Migration(PermissiveModel):
    """A migration."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    owner: NullableSimpleUser
    guid: str
    state: str
    lock_repositories: bool
    exclude_metadata: bool
    exclude_git_data: bool
    exclude_attachments: bool
    exclude_releases: bool
    exclude_owner_projects: bool
    org_metadata_only: bool
    repositories: list[Repository] = Field(..., description="The repositories included in the migration. Only returned for export migrations.")
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    node_id: str
    archive_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    exclude: list[str] | None = Field(None, description="Exclude related items from being returned in the response in order to improve performance of the request. The array can include any of: `\"repositories\"`.")

class PullRequestBase(PermissiveModel):
    label: str
    ref: str
    repo: Repository
    sha: str
    user: SimpleUser

class PullRequestHead(PermissiveModel):
    label: str
    ref: str
    repo: Repository
    sha: str
    user: SimpleUser

class Status(PermissiveModel):
    """The status of a commit."""
    url: str
    avatar_url: str | None = Field(...)
    id_: int = Field(..., validation_alias="id", serialization_alias="id")
    node_id: str
    state: str
    description: str | None = Field(...)
    target_url: str | None = Field(...)
    context: str
    created_at: str
    updated_at: str
    creator: NullableSimpleUser

class SubIssuesSummary(PermissiveModel):
    total: int
    completed: int
    percent_completed: int

class Issue(PermissiveModel):
    """Issues are a great way to keep track of tasks, enhancements, and bugs for your projects."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str
    url: str = Field(..., description="URL for the issue", json_schema_extra={'format': 'uri'})
    repository_url: str = Field(..., json_schema_extra={'format': 'uri'})
    labels_url: str
    comments_url: str = Field(..., json_schema_extra={'format': 'uri'})
    events_url: str = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    number: int = Field(..., description="Number uniquely identifying the issue within its repository")
    state: str = Field(..., description="State of the issue; either 'open' or 'closed'")
    state_reason: Literal["completed", "reopened", "not_planned", "duplicate"] | None = Field(None, description="The reason for the current state")
    title: str = Field(..., description="Title of the issue")
    body: str | None = Field(None, description="Contents of the issue")
    user: NullableSimpleUser
    labels: list[str | IssueLabelsItemV1] = Field(..., description="Labels to associate with this issue; pass one or more label names to replace the set of labels on this issue; send an empty array to clear all labels from the issue; note that the labels are silently dropped for users without push access to the repository")
    assignee: NullableSimpleUser
    assignees: list[SimpleUser] | None = None
    milestone: NullableMilestone
    locked: bool
    active_lock_reason: str | None = None
    comments: int
    pull_request: IssuePullRequest | None = None
    closed_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    draft: bool | None = None
    closed_by: NullableSimpleUser | None = None
    body_html: str | None = None
    body_text: str | None = None
    timeline_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    type_: IssueType | None = Field(None, validation_alias="type", serialization_alias="type")
    repository: Repository | None = None
    performed_via_github_app: NullableIntegration | None = None
    author_association: Literal["COLLABORATOR", "CONTRIBUTOR", "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR", "MANNEQUIN", "MEMBER", "NONE", "OWNER"] | None = None
    reactions: ReactionRollup | None = None
    sub_issues_summary: SubIssuesSummary | None = None
    parent_issue_url: str | None = Field(None, description="URL to get the parent issue of this issue, if it is a sub-issue", json_schema_extra={'format': 'uri'})
    issue_dependencies_summary: IssueDependenciesSummary | None = None
    issue_field_values: list[IssueFieldValue] | None = None

class TeamPermissions(PermissiveModel):
    pull: bool
    triage: bool
    push: bool
    maintain: bool
    admin: bool

class Team(PermissiveModel):
    """Groups of organization members that gives permissions on specified repositories."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id")
    node_id: str
    name: str
    slug: str
    description: str | None = Field(...)
    privacy: str | None = None
    notification_setting: str | None = None
    permission: str
    permissions: TeamPermissions | None = None
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    members_url: str
    repositories_url: str = Field(..., json_schema_extra={'format': 'uri'})
    parent: NullableTeamSimple

class ReposCreateOrUpdateEnvironmentBodyReviewersItem(PermissiveModel):
    type_: Literal["User", "Team"] | None = Field(None, validation_alias="type", serialization_alias="type")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The id of the user or team who can review the deployment")

class TeamSimple(PermissiveModel):
    """Groups of organization members that gives permissions on specified repositories."""
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the team")
    node_id: str
    url: str = Field(..., description="URL for the team", json_schema_extra={'format': 'uri'})
    members_url: str
    name: str = Field(..., description="Name of the team")
    description: str | None = Field(..., description="Description of the team")
    permission: str = Field(..., description="Permission that the team will have for its repositories")
    privacy: str | None = Field(None, description="The level of privacy this team should have")
    notification_setting: str | None = Field(None, description="The notification setting the team has set")
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    repositories_url: str = Field(..., json_schema_extra={'format': 'uri'})
    slug: str
    ldap_dn: str | None = Field(None, description="Distinguished Name (DN) that team maps to within LDAP environment")

class PullRequest(PermissiveModel):
    """Pull requests let you tell others about changes you've pushed to a repository on GitHub. Once a pull request is sent, interested parties can review the set of changes, discuss potential modifications, and even push follow-up commits if necessary."""
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    node_id: str
    html_url: str = Field(..., json_schema_extra={'format': 'uri'})
    diff_url: str = Field(..., json_schema_extra={'format': 'uri'})
    patch_url: str = Field(..., json_schema_extra={'format': 'uri'})
    issue_url: str = Field(..., json_schema_extra={'format': 'uri'})
    commits_url: str = Field(..., json_schema_extra={'format': 'uri'})
    review_comments_url: str = Field(..., json_schema_extra={'format': 'uri'})
    review_comment_url: str
    comments_url: str = Field(..., json_schema_extra={'format': 'uri'})
    statuses_url: str = Field(..., json_schema_extra={'format': 'uri'})
    number: int = Field(..., description="Number uniquely identifying the pull request within its repository.")
    state: Literal["open", "closed"] = Field(..., description="State of this Pull Request. Either `open` or `closed`.")
    locked: bool
    title: str = Field(..., description="The title of the pull request.")
    user: SimpleUser
    body: str | None = Field(...)
    labels: list[PullRequestLabelsItem]
    milestone: NullableMilestone
    active_lock_reason: str | None = None
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    closed_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    merged_at: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    merge_commit_sha: str | None = Field(...)
    assignee: NullableSimpleUser
    assignees: list[SimpleUser] | None = None
    requested_reviewers: list[SimpleUser] | None = None
    requested_teams: list[TeamSimple] | None = None
    head: PullRequestHead
    base: PullRequestBase
    links: PullRequestLinks = Field(..., validation_alias="_links", serialization_alias="_links")
    author_association: Literal["COLLABORATOR", "CONTRIBUTOR", "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR", "MANNEQUIN", "MEMBER", "NONE", "OWNER"]
    auto_merge: AutoMerge
    draft: bool | None = Field(None, description="Indicates whether or not the pull request is a draft.")
    merged: bool
    mergeable: bool | None = Field(...)
    rebaseable: bool | None = None
    mergeable_state: str
    merged_by: NullableSimpleUser
    comments: int
    review_comments: int
    maintainer_can_modify: bool = Field(..., description="Indicates whether maintainers can modify the pull request.")
    commits: int
    additions: int
    deletions: int
    changed_files: int

class UsersAddEmailForAuthenticatedUserBody(PermissiveModel):
    """Also accepts scalar shorthand."""
    emails: list[str] = Field(..., description="Adds one or more email addresses to your GitHub account. Must contain at least one email address. **Note:** Alternatively, you can pass a single email address or an `array` of emails addresses directly, but we recommend that you pass an object using the `emails` key.", min_length=1)

class UsersDeleteAttestationsBulkBodyV0(PermissiveModel):
    subject_digests: list[str] = Field(..., description="List of subject digests associated with the artifact attestations to delete.", min_length=1, max_length=1024)

class UsersDeleteAttestationsBulkBodyV1(PermissiveModel):
    attestation_ids: list[int] = Field(..., description="List of unique IDs associated with the artifact attestations to delete.", min_length=1, max_length=1024)

class UsersDeleteEmailForAuthenticatedUserBody(PermissiveModel):
    """Deletes one or more email addresses from your GitHub account. Must contain at least one email address. **Note:** Alternatively, you can pass a single email address or an `array` of emails addresses directly, but we recommend that you pass an object using the `emails` key."""
    emails: list[str] = Field(..., description="Email addresses associated with the GitHub user account.", min_length=1)

class WebhookConfig(PermissiveModel):
    """Configuration object of the webhook"""
    url: str | None = None
    content_type: str | None = None
    secret: str | None = None
    insecure_ssl: str | float | None = None

class Hook(PermissiveModel):
    """Webhooks for repositories."""
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the webhook.")
    name: str = Field(..., description="The name of a valid service, use 'web' for a webhook.")
    active: bool = Field(..., description="Determines whether the hook is actually triggered on pushes.")
    events: list[str] = Field(..., description="Determines what events the hook is triggered for. Default: ['push'].")
    config: WebhookConfig
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    url: str = Field(..., json_schema_extra={'format': 'uri'})
    test_url: str = Field(..., json_schema_extra={'format': 'uri'})
    ping_url: str = Field(..., json_schema_extra={'format': 'uri'})
    deliveries_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    last_response: HookResponse


# Rebuild models to resolve forward references (required for circular refs)
AppPermissions.model_rebuild()
AutoMerge.model_rebuild()
CampaignsCreateCampaignBodyCodeScanningAlertsItem.model_rebuild()
ChecksCreateBodyV0.model_rebuild()
ChecksCreateBodyV1.model_rebuild()
ChecksUpdateBodyV0.model_rebuild()
ChecksUpdateBodyV1.model_rebuild()
Classroom.model_rebuild()
CodeOfConduct.model_rebuild()
CodeSecurityUpdateConfigurationBodySecretScanningDelegatedBypassOptionsReviewersItem.model_rebuild()
CodespacesCreateForAuthenticatedUserBodyV0.model_rebuild()
CodespacesCreateForAuthenticatedUserBodyV1.model_rebuild()
CodespacesCreateForAuthenticatedUserBodyV1PullRequest.model_rebuild()
Contributor.model_rebuild()
CustomPropertyValue.model_rebuild()
Dependency.model_rebuild()
Deployment.model_rebuild()
Enterprise.model_rebuild()
GistsCreateBodyFilesValue.model_rebuild()
GistsUpdateBodyFilesValue.model_rebuild()
GitCreateTreeBodyTreeItem.model_rebuild()
Hook.model_rebuild()
HookResponse.model_rebuild()
Issue.model_rebuild()
IssueDependenciesSummary.model_rebuild()
IssueFieldValue.model_rebuild()
IssueFieldValueSingleSelectOption.model_rebuild()
IssueLabelsItemV1.model_rebuild()
IssuePullRequest.model_rebuild()
IssuesAddIssueFieldValuesBodyIssueFieldValuesItem.model_rebuild()
IssuesAddLabelsBodyV0.model_rebuild()
IssuesAddLabelsBodyV2Item.model_rebuild()
IssuesCreateBodyLabelsItem.model_rebuild()
IssuesSetIssueFieldValuesBodyIssueFieldValuesItem.model_rebuild()
IssuesSetLabelsBody.model_rebuild()
IssuesUpdateBodyIssueFieldValuesItem.model_rebuild()
IssuesUpdateBodyLabelsItem.model_rebuild()
IssueType.model_rebuild()
Key.model_rebuild()
Link.model_rebuild()
Manifest.model_rebuild()
ManifestFile.model_rebuild()
Metadata.model_rebuild()
Migration.model_rebuild()
NullableIntegration.model_rebuild()
NullableIntegrationPermissions.model_rebuild()
NullableLicenseSimple.model_rebuild()
NullableMilestone.model_rebuild()
NullableMinimalRepository.model_rebuild()
NullableMinimalRepositoryLicense.model_rebuild()
NullableMinimalRepositoryPermissions.model_rebuild()
NullableSimpleUser.model_rebuild()
NullableTeamSimple.model_rebuild()
OrgsCreateIssueFieldBodyOptionsItem.model_rebuild()
OrgsDeleteAttestationsBulkBodyV0.model_rebuild()
OrgsDeleteAttestationsBulkBodyV1.model_rebuild()
OrgsSetClusterDeploymentRecordsBodyDeploymentsItem.model_rebuild()
Package.model_rebuild()
ProjectsAddFieldForOrgBodyV0.model_rebuild()
ProjectsAddFieldForOrgBodyV1.model_rebuild()
ProjectsAddFieldForOrgBodyV2.model_rebuild()
ProjectsAddFieldForOrgBodyV3.model_rebuild()
ProjectsAddFieldForOrgBodyV3IterationConfiguration.model_rebuild()
ProjectsAddFieldForOrgBodyV3IterationConfigurationIterationsItem.model_rebuild()
ProjectsAddFieldForUserBodyIterationConfiguration.model_rebuild()
ProjectsAddFieldForUserBodyIterationConfigurationIterationsItem.model_rebuild()
ProjectsUpdateItemForOrgBodyFieldsItem.model_rebuild()
ProjectsUpdateItemForUserBodyFieldsItem.model_rebuild()
PullRequest.model_rebuild()
PullRequestBase.model_rebuild()
PullRequestHead.model_rebuild()
PullRequestLabelsItem.model_rebuild()
PullRequestLinks.model_rebuild()
ReactionRollup.model_rebuild()
ReposAddTeamAccessRestrictionsBodyV0.model_rebuild()
ReposCreateOrUpdateEnvironmentBodyReviewersItem.model_rebuild()
Repository.model_rebuild()
RepositoryCodeSearchIndexStatus.model_rebuild()
RepositoryPermissions.model_rebuild()
ReposRemoveStatusCheckContextsBodyV0.model_rebuild()
ReposRemoveTeamAccessRestrictionsBodyV0.model_rebuild()
ReposSetTeamAccessRestrictionsBodyV0.model_rebuild()
ReposUpdateBodySecurityAndAnalysisSecretScanningDelegatedBypassOptionsReviewersItem.model_rebuild()
ReposUpdateBranchProtectionBodyRequiredStatusChecksChecksItem.model_rebuild()
SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItem.model_rebuild()
SecurityAdvisoriesCreatePrivateVulnerabilityReportBodyVulnerabilitiesItemPackage.model_rebuild()
SecurityAdvisoriesCreateRepositoryAdvisoryBodyCreditsItem.model_rebuild()
SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItem.model_rebuild()
SecurityAdvisoriesCreateRepositoryAdvisoryBodyVulnerabilitiesItemPackage.model_rebuild()
SecurityAdvisoriesUpdateRepositoryAdvisoryBodyCreditsItem.model_rebuild()
SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItem.model_rebuild()
SecurityAdvisoriesUpdateRepositoryAdvisoryBodyVulnerabilitiesItemPackage.model_rebuild()
SecurityAndAnalysis.model_rebuild()
SecurityAndAnalysisAdvancedSecurity.model_rebuild()
SecurityAndAnalysisCodeSecurity.model_rebuild()
SecurityAndAnalysisDependabotSecurityUpdates.model_rebuild()
SecurityAndAnalysisSecretScanning.model_rebuild()
SecurityAndAnalysisSecretScanningAiDetection.model_rebuild()
SecurityAndAnalysisSecretScanningNonProviderPatterns.model_rebuild()
SecurityAndAnalysisSecretScanningPushProtection.model_rebuild()
SimpleClassroomOrganization.model_rebuild()
SimpleUser.model_rebuild()
Status.model_rebuild()
SubIssuesSummary.model_rebuild()
Team.model_rebuild()
TeamPermissions.model_rebuild()
TeamSimple.model_rebuild()
UsersAddEmailForAuthenticatedUserBody.model_rebuild()
UsersDeleteAttestationsBulkBodyV0.model_rebuild()
UsersDeleteAttestationsBulkBodyV1.model_rebuild()
UsersDeleteEmailForAuthenticatedUserBody.model_rebuild()
WebhookConfig.model_rebuild()

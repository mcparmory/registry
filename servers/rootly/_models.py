"""
Rootly MCP Server - Pydantic Models

Generated: 2026-04-23 21:09:28 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AcknowledgeAlertRequest",
    "AddSubscribersToIncidentRequest",
    "AttachAlertRequest",
    "CancelIncidentRequest",
    "CreateAlertEventRequest",
    "CreateAlertGroupRequest",
    "CreateAlertRequest",
    "CreateAlertsSourceRequest",
    "CreateAlertUrgencyRequest",
    "CreateCatalogEntityPropertyRequest",
    "CreateCatalogEntityRequest",
    "CreateCatalogFieldRequest",
    "CreateCatalogRequest",
    "CreateCauseRequest",
    "CreateCustomFormRequest",
    "CreateDashboardPanelRequest",
    "CreateDashboardRequest",
    "CreateEnvironmentRequest",
    "CreateEscalationLevelPathsRequest",
    "CreateEscalationLevelRequest",
    "CreateEscalationPolicyRequest",
    "CreateFormFieldOptionRequest",
    "CreateFormFieldPlacementRequest",
    "CreateFormFieldPositionRequest",
    "CreateFormFieldRequest",
    "CreateFormSetConditionRequest",
    "CreateFormSetRequest",
    "CreateFunctionalityRequest",
    "CreateHeartbeatRequest",
    "CreateIncidentActionItemRequest",
    "CreateIncidentEventFunctionalityRequest",
    "CreateIncidentEventRequest",
    "CreateIncidentEventServiceRequest",
    "CreateIncidentFeedbackRequest",
    "CreateIncidentFormFieldSelectionRequest",
    "CreateIncidentRequest",
    "CreateIncidentRoleRequest",
    "CreateIncidentRoleTaskRequest",
    "CreateIncidentStatusPageRequest",
    "CreateIncidentTypeRequest",
    "CreateLiveCallRouterRequest",
    "CreateOnCallRoleRequest",
    "CreateOnCallShadowRequest",
    "CreateOverrideShiftRequest",
    "CreatePlaybookRequest",
    "CreatePlaybookTaskRequest",
    "CreatePostmortemTemplateRequest",
    "CreatePulseRequest",
    "CreateRetrospectiveProcessRequest",
    "CreateRetrospectiveStepRequest",
    "CreateScheduleRequest",
    "CreateScheduleRotationActiveDayRequest",
    "CreateScheduleRotationRequest",
    "CreateScheduleRotationUserRequest",
    "CreateServiceRequest",
    "CreateSeverityRequest",
    "CreateStatusPageRequest",
    "CreateTeamRequest",
    "CreateUserEmailAddressRequest",
    "CreateUserPhoneNumberRequest",
    "CreateWorkflowRunRequest",
    "CreateWorkflowTaskRequest",
    "DeleteAlertEventRequest",
    "DeleteAlertGroupRequest",
    "DeleteAlertsSourceRequest",
    "DeleteAlertUrgencyRequest",
    "DeleteAuthorizationRequest",
    "DeleteCatalogEntityPropertyRequest",
    "DeleteCatalogEntityRequest",
    "DeleteCatalogFieldRequest",
    "DeleteCatalogRequest",
    "DeleteCauseRequest",
    "DeleteCustomFormRequest",
    "DeleteDashboardPanelRequest",
    "DeleteDashboardRequest",
    "DeleteEnvironmentRequest",
    "DeleteEscalationLevelRequest",
    "DeleteEscalationPathRequest",
    "DeleteEscalationPolicyRequest",
    "DeleteFormFieldOptionRequest",
    "DeleteFormFieldPlacementConditionRequest",
    "DeleteFormFieldRequest",
    "DeleteFormSetConditionRequest",
    "DeleteFormSetRequest",
    "DeleteFunctionalityRequest",
    "DeleteHeartbeatRequest",
    "DeleteIncidentActionItemRequest",
    "DeleteIncidentEventFunctionalityRequest",
    "DeleteIncidentEventRequest",
    "DeleteIncidentEventServiceRequest",
    "DeleteIncidentRequest",
    "DeleteIncidentRoleRequest",
    "DeleteIncidentRoleTaskRequest",
    "DeleteIncidentStatusPageRequest",
    "DeleteIncidentTypeRequest",
    "DeleteLiveCallRouterRequest",
    "DeleteOnCallRoleRequest",
    "DeleteOnCallShadowRequest",
    "DeleteOverrideShiftRequest",
    "DeletePlaybookRequest",
    "DeletePlaybookTaskRequest",
    "DeletePostmortemTemplateRequest",
    "DeleteRetrospectiveProcessRequest",
    "DeleteRetrospectiveStepRequest",
    "DeleteRoleRequest",
    "DeleteScheduleRequest",
    "DeleteScheduleRotationActiveDayRequest",
    "DeleteScheduleRotationRequest",
    "DeleteScheduleRotationUserRequest",
    "DeleteSecretRequest",
    "DeleteServiceRequest",
    "DeleteSeverityRequest",
    "DeleteStatusPageRequest",
    "DeleteStatusPageTemplateRequest",
    "DeleteTeamRequest",
    "DeleteUserEmailAddressRequest",
    "DeleteUserNotificationRuleRequest",
    "DeleteUserPhoneNumberRequest",
    "DeleteUserRequest",
    "DeleteWebhooksEndpointRequest",
    "DeleteWorkflowGroupRequest",
    "DeleteWorkflowRequest",
    "DeleteWorkflowTaskRequest",
    "DeliverWebhooksDeliveryRequest",
    "DuplicateDashboardPanelRequest",
    "DuplicateDashboardRequest",
    "GeneratePhoneNumberLiveCallRouterRequest",
    "GetAlertEventRequest",
    "GetAlertGroupRequest",
    "GetAlertRequest",
    "GetAlertsSourceRequest",
    "GetAlertUrgencyRequest",
    "GetAuthorizationRequest",
    "GetCatalogEntityPropertyRequest",
    "GetCatalogEntityRequest",
    "GetCatalogFieldRequest",
    "GetCatalogRequest",
    "GetCauseRequest",
    "GetCustomFormRequest",
    "GetDashboardPanelRequest",
    "GetDashboardRequest",
    "GetEnvironmentRequest",
    "GetEscalationLevelRequest",
    "GetEscalationPathRequest",
    "GetEscalationPolicyRequest",
    "GetFormFieldOptionRequest",
    "GetFormFieldPositionRequest",
    "GetFormFieldRequest",
    "GetFormSetConditionRequest",
    "GetFormSetRequest",
    "GetFunctionalityIncidentsChartRequest",
    "GetFunctionalityRequest",
    "GetFunctionalityUptimeChartRequest",
    "GetHeartbeatRequest",
    "GetIncidentActionItemsRequest",
    "GetIncidentEventFunctionalitiesRequest",
    "GetIncidentEventServicesRequest",
    "GetIncidentEventsRequest",
    "GetIncidentFeedbacksRequest",
    "GetIncidentFormFieldSelectionRequest",
    "GetIncidentRequest",
    "GetIncidentRetrospectiveStepRequest",
    "GetIncidentRoleRequest",
    "GetIncidentRoleTaskRequest",
    "GetIncidentStatusPagesRequest",
    "GetIncidentTypeRequest",
    "GetLiveCallRouterRequest",
    "GetOnCallRoleRequest",
    "GetOnCallShadowRequest",
    "GetOverrideShiftRequest",
    "GetPlaybookRequest",
    "GetPlaybookTaskRequest",
    "GetPostmortemTemplateRequest",
    "GetPulseRequest",
    "GetRetrospectiveConfigurationRequest",
    "GetRetrospectiveProcessGroupRequest",
    "GetRetrospectiveProcessGroupStepRequest",
    "GetRetrospectiveProcessRequest",
    "GetRetrospectiveStepRequest",
    "GetRoleRequest",
    "GetScheduleRequest",
    "GetScheduleRotationActiveDayRequest",
    "GetScheduleRotationRequest",
    "GetScheduleRotationUserRequest",
    "GetScheduleShiftsRequest",
    "GetSecretRequest",
    "GetServiceIncidentsChartRequest",
    "GetServiceRequest",
    "GetServiceUptimeChartRequest",
    "GetSeverityRequest",
    "GetStatusPageRequest",
    "GetStatusPageTemplateRequest",
    "GetTeamIncidentsChartRequest",
    "GetTeamRequest",
    "GetUserEmailAddressesRequest",
    "GetUserNotificationRuleRequest",
    "GetUserPhoneNumbersRequest",
    "GetUserRequest",
    "GetWebhooksDeliveryRequest",
    "GetWebhooksEndpointRequest",
    "GetWorkflowFormFieldConditionRequest",
    "GetWorkflowGroupRequest",
    "GetWorkflowRequest",
    "GetWorkflowTaskRequest",
    "ListAlertEventsRequest",
    "ListAlertGroupsRequest",
    "ListAlertsRequest",
    "ListAlertsSourcesRequest",
    "ListAlertUrgenciesRequest",
    "ListAllIncidentActionItemsRequest",
    "ListAuditsRequest",
    "ListCatalogEntitiesRequest",
    "ListCatalogEntityPropertiesRequest",
    "ListCatalogFieldsRequest",
    "ListCatalogsRequest",
    "ListCausesRequest",
    "ListCustomFormsRequest",
    "ListDashboardPanelsRequest",
    "ListDashboardsRequest",
    "ListEnvironmentsRequest",
    "ListEscalationLevelsPathsRequest",
    "ListEscalationLevelsRequest",
    "ListEscalationPathsRequest",
    "ListEscalationPoliciesRequest",
    "ListFormFieldOptionsRequest",
    "ListFormFieldPlacementConditionsRequest",
    "ListFormFieldPlacementsRequest",
    "ListFormFieldPositionsRequest",
    "ListFormFieldsRequest",
    "ListFormSetConditionsRequest",
    "ListFormSetsRequest",
    "ListFunctionalitiesRequest",
    "ListHeartbeatsRequest",
    "ListIncidentActionItemsRequest",
    "ListIncidentAlertsRequest",
    "ListIncidentEventFunctionalitiesRequest",
    "ListIncidentEventServicesRequest",
    "ListIncidentEventsRequest",
    "ListIncidentFeedbacksRequest",
    "ListIncidentFormFieldSelectionsRequest",
    "ListIncidentPostmortemRequest",
    "ListIncidentPostMortemsRequest",
    "ListIncidentRolesRequest",
    "ListIncidentRoleTasksRequest",
    "ListIncidentsRequest",
    "ListIncidentStatusPagesRequest",
    "ListIncidentTypesRequest",
    "ListLiveCallRoutersRequest",
    "ListOnCallRolesRequest",
    "ListOnCallShadowsRequest",
    "ListOverrideShiftsRequest",
    "ListPlaybooksRequest",
    "ListPlaybookTasksRequest",
    "ListPostmortemTemplatesRequest",
    "ListPulsesRequest",
    "ListRetrospectiveConfigurationsRequest",
    "ListRetrospectiveProcessesRequest",
    "ListRetrospectiveProcessGroupsRequest",
    "ListRetrospectiveProcessGroupStepsRequest",
    "ListRetrospectiveStepsRequest",
    "ListRolesRequest",
    "ListScheduleRotationActiveDaysRequest",
    "ListScheduleRotationsRequest",
    "ListScheduleRotationUsersRequest",
    "ListSchedulesRequest",
    "ListServicesRequest",
    "ListSeveritiesRequest",
    "ListShiftsRequest",
    "ListStatusPagesRequest",
    "ListStatusPageTemplatesRequest",
    "ListTeamsRequest",
    "ListUsersRequest",
    "ListWebhooksDeliveriesRequest",
    "ListWebhooksEndpointsRequest",
    "ListWorkflowFormFieldConditionsRequest",
    "ListWorkflowGroupsRequest",
    "ListWorkflowRunsRequest",
    "ListWorkflowTasksRequest",
    "MitigateIncidentRequest",
    "RemoveSubscribersToIncidentRequest",
    "ResolveAlertRequest",
    "ResolveIncidentRequest",
    "RestartIncidentRequest",
    "SetDefaultDashboardRequest",
    "ShowUserEmailAddressRequest",
    "ShowUserPhoneNumberRequest",
    "TriageIncidentRequest",
    "UpdateAlertEventRequest",
    "UpdateAlertGroupRequest",
    "UpdateAlertRequest",
    "UpdateAlertsSourceRequest",
    "UpdateAlertUrgencyRequest",
    "UpdateCatalogEntityPropertyRequest",
    "UpdateCatalogEntityRequest",
    "UpdateCatalogFieldRequest",
    "UpdateCatalogRequest",
    "UpdateCauseRequest",
    "UpdateCustomFormRequest",
    "UpdateDashboardPanelRequest",
    "UpdateDashboardRequest",
    "UpdateEnvironmentRequest",
    "UpdateEscalationLevelRequest",
    "UpdateEscalationPathRequest",
    "UpdateEscalationPolicyRequest",
    "UpdateFormFieldOptionRequest",
    "UpdateFormFieldRequest",
    "UpdateFormSetConditionRequest",
    "UpdateFormSetRequest",
    "UpdateFunctionalityRequest",
    "UpdateHeartbeatRequest",
    "UpdateIncidentActionItemRequest",
    "UpdateIncidentEventFunctionalityRequest",
    "UpdateIncidentEventRequest",
    "UpdateIncidentEventServiceRequest",
    "UpdateIncidentFeedbackRequest",
    "UpdateIncidentPostmortemRequest",
    "UpdateIncidentRequest",
    "UpdateIncidentRetrospectiveStepRequest",
    "UpdateIncidentRoleRequest",
    "UpdateIncidentRoleTaskRequest",
    "UpdateIncidentStatusPageRequest",
    "UpdateIncidentTypeRequest",
    "UpdateLiveCallRouterRequest",
    "UpdateOnCallRoleRequest",
    "UpdateOnCallShadowRequest",
    "UpdateOverrideShiftRequest",
    "UpdatePlaybookRequest",
    "UpdatePlaybookTaskRequest",
    "UpdatePostmortemTemplateRequest",
    "UpdatePulseRequest",
    "UpdateRetrospectiveConfigurationRequest",
    "UpdateRetrospectiveProcessRequest",
    "UpdateRetrospectiveStepRequest",
    "UpdateScheduleRequest",
    "UpdateScheduleRotationActiveDayRequest",
    "UpdateScheduleRotationRequest",
    "UpdateScheduleRotationUserRequest",
    "UpdateSecretRequest",
    "UpdateServiceRequest",
    "UpdateSeverityRequest",
    "UpdateStatusPageRequest",
    "UpdateTeamRequest",
    "UpdateUserEmailAddressRequest",
    "UpdateUserPhoneNumberRequest",
    "UpdateUserRequest",
    "UpdateWebhooksEndpointRequest",
    "UpdateWorkflowGroupRequest",
    "UpdateWorkflowTaskRequest",
    "AddActionItemTaskParams",
    "AddMicrosoftTeamsTabTaskParams",
    "AddRoleTaskParams",
    "AddSlackBookmarkTaskParams",
    "AddTeamTaskParams",
    "AddToTimelineTaskParams",
    "ArchiveMicrosoftTeamsChannelsTaskParams",
    "ArchiveSlackChannelsTaskParams",
    "AttachDatadogDashboardsTaskParams",
    "AutoAssignRoleOpsgenieTaskParams",
    "AutoAssignRolePagerdutyTaskParams",
    "AutoAssignRoleRootlyTaskParams",
    "AutoAssignRoleVictorOpsTaskParams",
    "CallPeopleTaskParams",
    "ChangeSlackChannelPrivacyTaskParams",
    "CreateAirtableTableRecordTaskParams",
    "CreateAlertGroupBodyDataAttributesConditionsItem",
    "CreateAlertGroupBodyDataAttributesTargetsItem",
    "CreateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem",
    "CreateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem",
    "CreateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem",
    "CreateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem",
    "CreateAsanaSubtaskTaskParams",
    "CreateAsanaTaskTaskParams",
    "CreateClickupTaskTaskParams",
    "CreateCodaPageTaskParams",
    "CreateConfluencePageTaskParams",
    "CreateDashboardPanelBodyDataAttributesParamsDatasetsItem",
    "CreateDatadogNotebookTaskParams",
    "CreateDropboxPaperPageTaskParams",
    "CreateEnvironmentBodyDataAttributesSlackAliasesItem",
    "CreateEnvironmentBodyDataAttributesSlackChannelsItem",
    "CreateEscalationLevelBodyDataAttributesNotificationTargetParamsItem",
    "CreateEscalationLevelPathsBodyDataAttributesNotificationTargetParamsItem",
    "CreateFunctionalityBodyDataAttributesSlackAliasesItem",
    "CreateFunctionalityBodyDataAttributesSlackChannelsItem",
    "CreateGithubIssueTaskParams",
    "CreateGitlabIssueTaskParams",
    "CreateGoogleCalendarEventTaskParams",
    "CreateGoogleDocsPageTaskParams",
    "CreateGoogleDocsPermissionsTaskParams",
    "CreateGoogleMeetingTaskParams",
    "CreateGoToMeetingTaskParams",
    "CreateIncidentPostmortemTaskParams",
    "CreateIncidentTaskParams",
    "CreateIncidentTypeBodyDataAttributesSlackAliasesItem",
    "CreateIncidentTypeBodyDataAttributesSlackChannelsItem",
    "CreateJiraIssueTaskParams",
    "CreateJiraSubtaskTaskParams",
    "CreateLinearIssueCommentTaskParams",
    "CreateLinearIssueTaskParams",
    "CreateLinearSubtaskIssueTaskParams",
    "CreateLiveCallRouterBodyDataAttributesPagingTargetsItem",
    "CreateMicrosoftTeamsChannelTaskParams",
    "CreateMicrosoftTeamsMeetingTaskParams",
    "CreateMotionTaskTaskParams",
    "CreateNotionPageTaskParams",
    "CreateOpsgenieAlertTaskParams",
    "CreateOutlookEventTaskParams",
    "CreatePagerdutyStatusUpdateTaskParams",
    "CreatePagertreeAlertTaskParams",
    "CreateQuipPageTaskParams",
    "CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0",
    "CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1",
    "CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2",
    "CreateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem",
    "CreateScheduleRotationBodyDataAttributesActiveTimeAttributesItem",
    "CreateScheduleRotationBodyDataAttributesScheduleRotationableAttributes",
    "CreateServiceBodyDataAttributesSlackAliasesItem",
    "CreateServiceBodyDataAttributesSlackChannelsItem",
    "CreateServiceNowIncidentTaskParams",
    "CreateSeverityBodyDataAttributesSlackAliasesItem",
    "CreateSeverityBodyDataAttributesSlackChannelsItem",
    "CreateSharepointPageTaskParams",
    "CreateShortcutStoryTaskParams",
    "CreateShortcutTaskTaskParams",
    "CreateSlackChannelTaskParams",
    "CreateTeamBodyDataAttributesSlackAliasesItem",
    "CreateTeamBodyDataAttributesSlackChannelsItem",
    "CreateTrelloCardTaskParams",
    "CreateWebexMeetingTaskParams",
    "CreateWorkflowRunBodyDataAttributesV0",
    "CreateWorkflowRunBodyDataAttributesV1",
    "CreateWorkflowRunBodyDataAttributesV2",
    "CreateWorkflowRunBodyDataAttributesV3",
    "CreateWorkflowRunBodyDataAttributesV4",
    "CreateWorkflowRunBodyDataAttributesV5",
    "CreateZendeskJiraLinkTaskParams",
    "CreateZendeskTicketTaskParams",
    "CreateZoomMeetingTaskParams",
    "GeniusCreateAnthropicChatCompletionTaskParams",
    "GeniusCreateGoogleGeminiChatCompletionTaskParams",
    "GeniusCreateOpenaiChatCompletionTaskParams",
    "GeniusCreateWatsonxChatCompletionTaskParams",
    "GetAlertsTaskParams",
    "GetGithubCommitsTaskParams",
    "GetGitlabCommitsTaskParams",
    "GetPulsesTaskParams",
    "HttpClientTaskParams",
    "InviteToMicrosoftTeamsChannelTaskParams",
    "InviteToSlackChannelOpsgenieTaskParams",
    "InviteToSlackChannelPagerdutyTaskParams",
    "InviteToSlackChannelRootlyTaskParams",
    "InviteToSlackChannelTaskParams",
    "InviteToSlackChannelVictorOpsTaskParams",
    "PageOpsgenieOnCallRespondersTaskParams",
    "PagePagerdutyOnCallRespondersTaskParams",
    "PageRootlyOnCallRespondersTaskParams",
    "PageVictorOpsOnCallRespondersTaskParams",
    "PrintTaskParams",
    "PublishIncidentTaskParams",
    "RedisClientTaskParams",
    "RemoveGoogleDocsPermissionsTaskParams",
    "RenameMicrosoftTeamsChannelTaskParams",
    "RenameSlackChannelTaskParams",
    "RunCommandHerokuTaskParams",
    "SendDashboardReportTaskParams",
    "SendEmailTaskParams",
    "SendMicrosoftTeamsBlocksTaskParams",
    "SendMicrosoftTeamsMessageTaskParams",
    "SendSlackBlocksTaskParams",
    "SendSlackMessageTaskParams",
    "SendSmsTaskParams",
    "SendWhatsappMessageTaskParams",
    "SnapshotDatadogGraphTaskParams",
    "SnapshotGrafanaDashboardTaskParams",
    "SnapshotLookerLookTaskParams",
    "SnapshotNewRelicGraphTaskParams",
    "TriggerWorkflowTaskParams",
    "TweetTwitterMessageTaskParams",
    "UpdateActionItemTaskParams",
    "UpdateAirtableTableRecordTaskParams",
    "UpdateAlertGroupBodyDataAttributesConditionsItem",
    "UpdateAlertGroupBodyDataAttributesTargetsItem",
    "UpdateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem",
    "UpdateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem",
    "UpdateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem",
    "UpdateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem",
    "UpdateAsanaTaskTaskParams",
    "UpdateAttachedAlertsTaskParams",
    "UpdateClickupTaskTaskParams",
    "UpdateCodaPageTaskParams",
    "UpdateDashboardPanelBodyDataAttributesParamsDatasetsItem",
    "UpdateEnvironmentBodyDataAttributesSlackAliasesItem",
    "UpdateEnvironmentBodyDataAttributesSlackChannelsItem",
    "UpdateEscalationLevelBodyDataAttributesNotificationTargetParamsItem",
    "UpdateEscalationPathBodyDataAttributesRulesItemV0",
    "UpdateEscalationPathBodyDataAttributesRulesItemV1",
    "UpdateEscalationPathBodyDataAttributesRulesItemV2",
    "UpdateEscalationPathBodyDataAttributesTimeRestrictionsItem",
    "UpdateFunctionalityBodyDataAttributesSlackAliasesItem",
    "UpdateFunctionalityBodyDataAttributesSlackChannelsItem",
    "UpdateGithubIssueTaskParams",
    "UpdateGitlabIssueTaskParams",
    "UpdateGoogleCalendarEventTaskParams",
    "UpdateGoogleDocsPageTaskParams",
    "UpdateIncidentPostmortemTaskParams",
    "UpdateIncidentStatusTimestampTaskParams",
    "UpdateIncidentTaskParams",
    "UpdateIncidentTypeBodyDataAttributesSlackAliasesItem",
    "UpdateIncidentTypeBodyDataAttributesSlackChannelsItem",
    "UpdateJiraIssueTaskParams",
    "UpdateLinearIssueTaskParams",
    "UpdateLiveCallRouterBodyDataAttributesPagingTargetsItem",
    "UpdateMotionTaskTaskParams",
    "UpdateNotionPageTaskParams",
    "UpdateOpsgenieAlertTaskParams",
    "UpdateOpsgenieIncidentTaskParams",
    "UpdatePagerdutyIncidentTaskParams",
    "UpdatePagertreeAlertTaskParams",
    "UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0",
    "UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1",
    "UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2",
    "UpdateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem",
    "UpdateScheduleRotationBodyDataAttributesActiveTimeAttributesItem",
    "UpdateScheduleRotationBodyDataAttributesScheduleRotationableAttributes",
    "UpdateServiceBodyDataAttributesSlackAliasesItem",
    "UpdateServiceBodyDataAttributesSlackChannelsItem",
    "UpdateServiceNowIncidentTaskParams",
    "UpdateSeverityBodyDataAttributesSlackAliasesItem",
    "UpdateSeverityBodyDataAttributesSlackChannelsItem",
    "UpdateShortcutStoryTaskParams",
    "UpdateShortcutTaskTaskParams",
    "UpdateSlackChannelTopicTaskParams",
    "UpdateStatusTaskParams",
    "UpdateTeamBodyDataAttributesSlackAliasesItem",
    "UpdateTeamBodyDataAttributesSlackChannelsItem",
    "UpdateTrelloCardTaskParams",
    "UpdateVictorOpsIncidentTaskParams",
    "UpdateZendeskTicketTaskParams",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_alert_events
class ListAlertEventsRequestPath(StrictModel):
    alert_id: str = Field(default=..., description="The unique identifier of the alert for which to retrieve events.")
class ListAlertEventsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., actor, metadata). Reduces need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of events to return per page. Adjust to balance response size and number of requests needed.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter results by event kind (e.g., created, updated, resolved). Narrows results to specific event types.")
    filter_action: str | None = Field(default=None, validation_alias="filter[action]", serialization_alias="filter[action]", description="Filter results by action type (e.g., triggered, acknowledged, dismissed). Narrows results to specific actions performed on the alert.")
class ListAlertEventsRequest(StrictModel):
    """Retrieve a paginated list of events associated with a specific alert, with optional filtering by event kind and action type."""
    path: ListAlertEventsRequestPath
    query: ListAlertEventsRequestQuery | None = None

# Operation: create_alert_event
class CreateAlertEventRequestPath(StrictModel):
    alert_id: str = Field(default=..., description="The unique identifier of the alert to which this event will be attached.")
class CreateAlertEventRequestBodyDataAttributes(StrictModel):
    kind: Literal["note"] = Field(default=..., validation_alias="kind", serialization_alias="kind", description="The type of event content being added. Must be 'note' to indicate this is a note-type event.")
    user_id: int | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="The user ID of the person creating this note. If not provided, the event will be created without an explicit author attribution.")
    details: str = Field(default=..., validation_alias="details", serialization_alias="details", description="The text content of the note being added to the alert. This message will be stored as part of the alert's event history.")
class CreateAlertEventRequestBodyData(StrictModel):
    type_: Literal["alert_events"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category of event being created. Must be 'alert_events' to classify this as an alert event.")
    attributes: CreateAlertEventRequestBodyDataAttributes
class CreateAlertEventRequestBody(StrictModel):
    data: CreateAlertEventRequestBodyData
class CreateAlertEventRequest(StrictModel):
    """Creates a new note event attached to an alert. This allows adding contextual notes or updates to track alert activity and history."""
    path: CreateAlertEventRequestPath
    body: CreateAlertEventRequestBody

# Operation: get_alert_event
class GetAlertEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert event to retrieve.")
class GetAlertEventRequest(StrictModel):
    """Retrieves a specific alert event by its unique identifier. Use this to fetch detailed information about a single alert event."""
    path: GetAlertEventRequestPath

# Operation: update_alert_event
class UpdateAlertEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert event to update.")
class UpdateAlertEventRequestBodyDataAttributes(StrictModel):
    user_id: int | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="The user ID of the person authoring the note. Optional if the note is being added by the system or current authenticated user.")
    details: str = Field(default=..., validation_alias="details", serialization_alias="details", description="The text content of the note to add or update for this alert event.")
class UpdateAlertEventRequestBodyData(StrictModel):
    type_: Literal["alert_events"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'alert_events' to identify this as an alert event resource.")
    attributes: UpdateAlertEventRequestBodyDataAttributes
class UpdateAlertEventRequestBody(StrictModel):
    data: UpdateAlertEventRequestBodyData
class UpdateAlertEventRequest(StrictModel):
    """Update a specific alert event by adding or modifying a note. Requires the alert event ID, resource type identifier, and note content."""
    path: UpdateAlertEventRequestPath
    body: UpdateAlertEventRequestBody

# Operation: delete_alert_event
class DeleteAlertEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert event to delete.")
class DeleteAlertEventRequest(StrictModel):
    """Permanently deletes a specific alert event by its unique identifier. This action cannot be undone."""
    path: DeleteAlertEventRequestPath

# Operation: list_alert_groups
class ListAlertGroupsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., rules, notifications). Omit to return only alert group core data.")
class ListAlertGroupsRequest(StrictModel):
    """Retrieve a list of all alert groups. Use the include parameter to expand related resources in the response."""
    query: ListAlertGroupsRequestQuery | None = None

# Operation: create_alert_group
class CreateAlertGroupRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the alert group used for identification and display purposes.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional description explaining the purpose or context of the alert group.")
    time_window: int | None = Field(default=None, validation_alias="time_window", serialization_alias="time_window", description="The duration in seconds that an alert group remains open and continues accepting new matching alerts before closing.")
    targets: list[CreateAlertGroupBodyDataAttributesTargetsItem] = Field(default=..., validation_alias="targets", serialization_alias="targets", description="An array of target destinations where alerts in this group will be routed or delivered. Specify targets as an ordered list of destination objects or identifiers.")
    group_by_alert_title: Literal[1, 0] | None = Field(default=None, validation_alias="group_by_alert_title", serialization_alias="group_by_alert_title", description="Set to 1 to group alerts by their title, or 0 to disable title-based grouping. Alerts with identical titles will be consolidated together.")
    group_by_alert_urgency: Literal[1, 0] | None = Field(default=None, validation_alias="group_by_alert_urgency", serialization_alias="group_by_alert_urgency", description="Set to 1 to group alerts by their urgency level, or 0 to disable urgency-based grouping. Alerts with matching urgency will be consolidated together.")
    condition_type: Literal["all", "any"] | None = Field(default=None, validation_alias="condition_type", serialization_alias="condition_type", description="Determines the matching logic for conditions: use 'all' to require all conditions to match, or 'any' to group alerts when at least one condition matches.")
    conditions: list[CreateAlertGroupBodyDataAttributesConditionsItem] | None = Field(default=None, validation_alias="conditions", serialization_alias="conditions", description="An array of condition objects that define which alerts should be included in this group. Each condition specifies a field and value to match against incoming alerts.")
class CreateAlertGroupRequestBodyData(StrictModel):
    type_: Literal["alert_groups"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'alert_groups' to specify this is an alert group resource.")
    attributes: CreateAlertGroupRequestBodyDataAttributes
class CreateAlertGroupRequestBody(StrictModel):
    data: CreateAlertGroupRequestBodyData
class CreateAlertGroupRequest(StrictModel):
    """Creates a new alert group to automatically organize and correlate incoming alerts based on specified criteria. Alert groups help reduce noise by bundling related alerts together within a configurable time window."""
    body: CreateAlertGroupRequestBody

# Operation: get_alert_group
class GetAlertGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert group to retrieve.")
class GetAlertGroupRequest(StrictModel):
    """Retrieves a specific alert group by its unique identifier. Use this operation to fetch detailed information about a single alert group."""
    path: GetAlertGroupRequestPath

# Operation: update_alert_group
class UpdateAlertGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert group to update.")
class UpdateAlertGroupRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the alert group's purpose and scope.")
    time_window: int | None = Field(default=None, validation_alias="time_window", serialization_alias="time_window", description="The duration in seconds that an alert group remains open to accept new alerts before closing.")
    targets: list[UpdateAlertGroupBodyDataAttributesTargetsItem] | None = Field(default=None, validation_alias="targets", serialization_alias="targets", description="An array of notification targets (e.g., email addresses, webhook URLs, or team identifiers) where alerts in this group should be sent.")
    group_by_alert_title: Literal[1, 0] | None = Field(default=None, validation_alias="group_by_alert_title", serialization_alias="group_by_alert_title", description="Enable grouping of alerts by their title; set to 1 to enable or 0 to disable.")
    group_by_alert_urgency: Literal[1, 0] | None = Field(default=None, validation_alias="group_by_alert_urgency", serialization_alias="group_by_alert_urgency", description="Enable grouping of alerts by their urgency level; set to 1 to enable or 0 to disable.")
    condition_type: Literal["all", "any"] | None = Field(default=None, validation_alias="condition_type", serialization_alias="condition_type", description="Determines whether alerts must match ALL specified conditions or ANY of them to be grouped together.")
    conditions: list[UpdateAlertGroupBodyDataAttributesConditionsItem] | None = Field(default=None, validation_alias="conditions", serialization_alias="conditions", description="An array of matching conditions that define which alerts should be grouped together; each condition specifies a field and value to match against incoming alerts.")
class UpdateAlertGroupRequestBodyData(StrictModel):
    type_: Literal["alert_groups"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'alert_groups'.")
    attributes: UpdateAlertGroupRequestBodyDataAttributes | None = None
class UpdateAlertGroupRequestBody(StrictModel):
    data: UpdateAlertGroupRequestBodyData
class UpdateAlertGroupRequest(StrictModel):
    """Update an existing alert group's configuration, including grouping rules, time window, description, and notification targets."""
    path: UpdateAlertGroupRequestPath
    body: UpdateAlertGroupRequestBody

# Operation: delete_alert_group
class DeleteAlertGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert group to delete.")
class DeleteAlertGroupRequest(StrictModel):
    """Permanently delete a specific alert group by its unique identifier. This action cannot be undone."""
    path: DeleteAlertGroupRequestPath

# Operation: list_alert_urgencies
class ListAlertUrgenciesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., alerts, rules). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results per page. Adjust to balance between response size and number of requests needed.")
    sort: str | None = Field(default=None, description="Sort results by one or more fields using comma-separated values. Prefix field names with a minus sign (-) for descending order (e.g., -created_at,name).")
class ListAlertUrgenciesRequest(StrictModel):
    """Retrieve a paginated list of alert urgency levels. Use this to understand the available urgency classifications for alerts in your system."""
    query: ListAlertUrgenciesRequestQuery | None = None

# Operation: create_alert_urgency
class CreateAlertUrgencyRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for this alert urgency level (e.g., 'Critical', 'High', 'Medium', 'Low').")
    description: str = Field(default=..., validation_alias="description", serialization_alias="description", description="A detailed explanation of when this alert urgency level should be used and what it represents.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this alert urgency relative to others, with lower numbers appearing first. Optional; if not provided, the system will assign a default position.")
class CreateAlertUrgencyRequestBodyData(StrictModel):
    type_: Literal["alert_urgencies"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, must be set to 'alert_urgencies' to specify the resource being created.")
    attributes: CreateAlertUrgencyRequestBodyDataAttributes
class CreateAlertUrgencyRequestBody(StrictModel):
    data: CreateAlertUrgencyRequestBodyData
class CreateAlertUrgencyRequest(StrictModel):
    """Creates a new alert urgency level that can be assigned to alerts. Alert urgencies help categorize and prioritize alerts based on their importance."""
    body: CreateAlertUrgencyRequestBody

# Operation: get_alert_urgency
class GetAlertUrgencyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert urgency to retrieve.")
class GetAlertUrgencyRequest(StrictModel):
    """Retrieves a specific alert urgency configuration by its unique identifier. Use this to fetch details about how urgent a particular alert level is classified."""
    path: GetAlertUrgencyRequestPath

# Operation: update_alert_urgency
class UpdateAlertUrgencyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert urgency to update.")
class UpdateAlertUrgencyRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of what this alert urgency level represents and when it should be used.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this alert urgency relative to others, used for sorting in user interfaces.")
class UpdateAlertUrgencyRequestBodyData(StrictModel):
    type_: Literal["alert_urgencies"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'alert_urgencies' to specify this is an alert urgency resource.")
    attributes: UpdateAlertUrgencyRequestBodyDataAttributes | None = None
class UpdateAlertUrgencyRequestBody(StrictModel):
    data: UpdateAlertUrgencyRequestBodyData
class UpdateAlertUrgencyRequest(StrictModel):
    """Update the properties of a specific alert urgency level, including its description and display position."""
    path: UpdateAlertUrgencyRequestPath
    body: UpdateAlertUrgencyRequestBody

# Operation: delete_alert_urgency
class DeleteAlertUrgencyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert urgency to delete.")
class DeleteAlertUrgencyRequest(StrictModel):
    """Delete a specific alert urgency by its unique identifier. This operation permanently removes the alert urgency configuration from the system."""
    path: DeleteAlertUrgencyRequestPath

# Operation: list_alert_sources
class ListAlertsSourcesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., configuration details, metadata).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of alert sources to return per page. Defines the maximum results in each paginated response.")
    filter_statuses: str | None = Field(default=None, validation_alias="filter[statuses]", serialization_alias="filter[statuses]", description="Comma-separated list of alert source statuses to filter by (e.g., active, inactive, disabled).")
    filter_source_types: str | None = Field(default=None, validation_alias="filter[source_types]", serialization_alias="filter[source_types]", description="Comma-separated list of source types to filter by (e.g., webhook, email, api, monitoring_tool).")
    sort: str | None = Field(default=None, description="Field name and direction to sort results by, formatted as field_name or field_name:asc/desc (e.g., created_at:desc).")
class ListAlertsSourcesRequest(StrictModel):
    """Retrieve a paginated list of alert sources with optional filtering by status and source type, and customizable sorting."""
    query: ListAlertsSourcesRequestQuery | None = None

# Operation: create_alert_source
class CreateAlertsSourceRequestBodyDataAttributesAlertTemplateAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A short title displayed for alerts originating from this source.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation of the alert source's purpose and configuration.")
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL link to the external system or dashboard where the alert originated, providing context and traceability.")
class CreateAlertsSourceRequestBodyDataAttributesSourceableAttributes(StrictModel):
    auto_resolve: bool | None = Field(default=None, validation_alias="auto_resolve", serialization_alias="auto_resolve", description="Enable automatic resolution of alerts when conditions defined in field_mappings_attributes are met. Set to true to automatically close alerts based on payload matching.")
    resolve_state: str | None = Field(default=None, validation_alias="resolve_state", serialization_alias="resolve_state", description="The expected value in the alert payload that indicates an alert should be resolved. This value is extracted using the JSON path specified in field_mappings_attributes and compared to determine if auto-resolution should trigger.")
    accept_threaded_emails: bool | None = Field(default=None, validation_alias="accept_threaded_emails", serialization_alias="accept_threaded_emails", description="Set to false to reject email alerts that are part of a threaded conversation. By default, threaded emails are accepted.")
    field_mappings_attributes: list[CreateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem] | None = Field(default=None, validation_alias="field_mappings_attributes", serialization_alias="field_mappings_attributes", description="An ordered list of field mapping rules that extract data from alert payloads and define conditions for auto-resolving alerts. Each mapping specifies how to identify and match alerts for resolution.")
class CreateAlertsSourceRequestBodyDataAttributesResolutionRuleAttributes(StrictModel):
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Set to true to activate the auto-resolution rule. When false, the rule is defined but not applied to incoming alerts.")
    condition_type: Literal["all", "any"] | None = Field(default=None, validation_alias="condition_type", serialization_alias="condition_type", description="Determines how multiple conditions are evaluated: 'all' requires all conditions to be true, 'any' requires at least one condition to be true.")
    identifier_matchable_type: Literal["AlertField"] | None = Field(default=None, validation_alias="identifier_matchable_type", serialization_alias="identifier_matchable_type", description="The type of object being referenced for alert identification. Currently supports 'AlertField' to reference a predefined alert field.")
    identifier_matchable_id: str | None = Field(default=None, validation_alias="identifier_matchable_id", serialization_alias="identifier_matchable_id", description="The unique identifier of the object specified in identifier_matchable_type. When the type is 'AlertField', this is the ID of the alert field used for matching.")
    identifier_reference_kind: Literal["payload", "alert_field"] | None = Field(default=None, validation_alias="identifier_reference_kind", serialization_alias="identifier_reference_kind", description="Specifies where the identifier value comes from: 'payload' extracts it directly from the alert JSON, 'alert_field' references a predefined alert field.")
    identifier_json_path: str | None = Field(default=None, validation_alias="identifier_json_path", serialization_alias="identifier_json_path", description="A JSON path expression (e.g., $.alert.id or $.incident.key) that extracts the unique identifier from the alert payload. This identifier is used to correlate triggered alerts with their corresponding resolve alerts.")
    identifier_value_regex: str | None = Field(default=None, validation_alias="identifier_value_regex", serialization_alias="identifier_value_regex", description="A regular expression pattern with capture groups to extract a specific portion of the identifier string. Use this to refine the identifier when the full extracted value contains extra characters.")
    conditions_attributes: list[CreateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem] | None = Field(default=None, validation_alias="conditions_attributes", serialization_alias="conditions_attributes", description="An ordered list of conditions that must be evaluated to determine if an alert qualifies for auto-resolution. Conditions are combined using the logic specified in condition_type.")
class CreateAlertsSourceRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for this alert source to identify it in your system.")
    source_type: Literal["email", "app_dynamics", "catchpoint", "datadog", "alertmanager", "google_cloud", "grafana", "sentry", "generic_webhook", "cloud_watch", "checkly", "azure", "new_relic", "splunk", "chronosphere", "app_optics", "bug_snag", "honeycomb", "monte_carlo", "nagios", "prtg"] | None = Field(default=None, validation_alias="source_type", serialization_alias="source_type", description="The monitoring or alerting platform this source integrates with, such as Datadog, Grafana, PagerDuty, or a generic webhook. Choose from supported integrations like email, app_dynamics, catchpoint, datadog, alertmanager, google_cloud, grafana, sentry, generic_webhook, cloud_watch, checkly, azure, new_relic, splunk, chronosphere, app_optics, bug_snag, honeycomb, monte_carlo, nagios, or prtg.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The default urgency level assigned to alerts from this source. Specify the urgency ID to set baseline severity for incoming alerts.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="One or more team IDs that will own and manage this alert source. Ownership determines who can modify the source configuration and handle its alerts.")
    alert_source_urgency_rules_attributes: list[CreateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem] | None = Field(default=None, validation_alias="alert_source_urgency_rules_attributes", serialization_alias="alert_source_urgency_rules_attributes", description="An ordered list of rules that automatically assign urgency levels to alerts based on conditions evaluated against the alert payload. Rules are evaluated in sequence; the first matching rule determines the alert's urgency.")
    alert_source_fields_attributes: list[CreateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem] | None = Field(default=None, validation_alias="alert_source_fields_attributes", serialization_alias="alert_source_fields_attributes", description="An ordered list of custom alert fields to be created and associated with this alert source. These fields can be used for field mappings, urgency rules, and alert enrichment.")
    alert_template_attributes: CreateAlertsSourceRequestBodyDataAttributesAlertTemplateAttributes | None = None
    sourceable_attributes: CreateAlertsSourceRequestBodyDataAttributesSourceableAttributes | None = None
    resolution_rule_attributes: CreateAlertsSourceRequestBodyDataAttributesResolutionRuleAttributes | None = None
class CreateAlertsSourceRequestBodyData(StrictModel):
    type_: Literal["alert_sources"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'alert_sources'.")
    attributes: CreateAlertsSourceRequestBodyDataAttributes
class CreateAlertsSourceRequestBody(StrictModel):
    data: CreateAlertsSourceRequestBodyData
class CreateAlertsSourceRequest(StrictModel):
    """Creates a new alert source to receive and process alerts from external monitoring systems. Configure the source type, auto-resolution rules, field mappings, and ownership to integrate alerts into your incident management workflow."""
    body: CreateAlertsSourceRequestBody

# Operation: get_alert_source
class GetAlertsSourceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert source to retrieve.")
class GetAlertsSourceRequest(StrictModel):
    """Retrieves a specific alert source by its unique identifier. Use this to fetch detailed configuration and settings for a particular alert source."""
    path: GetAlertsSourceRequestPath

# Operation: update_alert_source
class UpdateAlertsSourceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert source to update.")
class UpdateAlertsSourceRequestBodyDataAttributesAlertTemplateAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A human-readable name for the alert source.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation of the alert source's purpose and configuration.")
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="The external URL where alerts from this source can be viewed or managed in the originating system.")
class UpdateAlertsSourceRequestBodyDataAttributesSourceableAttributes(StrictModel):
    auto_resolve: bool | None = Field(default=None, validation_alias="auto_resolve", serialization_alias="auto_resolve", description="Enable automatic resolution of alerts when matching resolve conditions are detected in incoming alert payloads.")
    resolve_state: str | None = Field(default=None, validation_alias="resolve_state", serialization_alias="resolve_state", description="The expected value in the alert payload that indicates an alert should be resolved. This value is extracted using the JSON path specified in field mappings.")
    accept_threaded_emails: bool | None = Field(default=None, validation_alias="accept_threaded_emails", serialization_alias="accept_threaded_emails", description="Set to false to reject email alerts that are part of threaded conversations; set to true to accept them.")
    field_mappings_attributes: list[UpdateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem] | None = Field(default=None, validation_alias="field_mappings_attributes", serialization_alias="field_mappings_attributes", description="Array of field mapping rules that define how to extract values from alert payloads for matching, resolution, and identifier extraction.")
class UpdateAlertsSourceRequestBodyDataAttributesResolutionRuleAttributes(StrictModel):
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Set to true to enable the auto-resolution rule; set to false to disable it.")
    condition_type: Literal["all", "any"] | None = Field(default=None, validation_alias="condition_type", serialization_alias="condition_type", description="Determines how multiple conditions are evaluated: 'all' requires all conditions to be true, 'any' requires at least one condition to be true.")
    identifier_json_path: str | None = Field(default=None, validation_alias="identifier_json_path", serialization_alias="identifier_json_path", description="A JSON path expression used to extract the unique identifier from alert payloads for matching triggered alerts with their corresponding resolve alerts.")
    identifier_value_regex: str | None = Field(default=None, validation_alias="identifier_value_regex", serialization_alias="identifier_value_regex", description="A regex pattern with capture groups to extract a specific portion of the identifier value for more precise matching.")
    identifier_matchable_type: Literal["AlertField"] | None = Field(default=None, validation_alias="identifier_matchable_type", serialization_alias="identifier_matchable_type", description="The type of object being referenced for identifier matching; currently supports 'AlertField'.")
    identifier_matchable_id: str | None = Field(default=None, validation_alias="identifier_matchable_id", serialization_alias="identifier_matchable_id", description="The ID of the referenced object. When identifier_matchable_type is 'AlertField', this is the ID of the alert field definition.")
    identifier_reference_kind: Literal["payload", "alert_field"] | None = Field(default=None, validation_alias="identifier_reference_kind", serialization_alias="identifier_reference_kind", description="Specifies whether the identifier is extracted from the raw alert payload or from a predefined alert field: 'payload' for direct JSON extraction, 'alert_field' for field-based extraction.")
    conditions_attributes: list[UpdateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem] | None = Field(default=None, validation_alias="conditions_attributes", serialization_alias="conditions_attributes", description="Array of conditions that must be satisfied for auto-resolution to trigger. Each condition specifies a field, operator, and expected value.")
class UpdateAlertsSourceRequestBodyDataAttributes(StrictModel):
    source_type: Literal["email", "app_dynamics", "catchpoint", "datadog", "alertmanager", "google_cloud", "grafana", "sentry", "generic_webhook", "cloud_watch", "checkly", "azure", "new_relic", "splunk", "chronosphere", "app_optics", "bug_snag", "honeycomb", "monte_carlo", "nagios", "prtg"] | None = Field(default=None, validation_alias="source_type", serialization_alias="source_type", description="The integration type for this alert source. Choose from supported platforms including email, monitoring tools (Datadog, New Relic, Grafana), cloud providers (AWS CloudWatch, Azure, Google Cloud), and webhook-based integrations.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The ID of the default urgency level to assign to alerts from this source when no urgency rules apply.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="List of team IDs that will have ownership and management permissions for this alert source.")
    alert_source_urgency_rules_attributes: list[UpdateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem] | None = Field(default=None, validation_alias="alert_source_urgency_rules_attributes", serialization_alias="alert_source_urgency_rules_attributes", description="Array of urgency assignment rules that automatically set alert urgency based on conditions extracted from the alert payload. Rules are evaluated in order.")
    alert_source_fields_attributes: list[UpdateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem] | None = Field(default=None, validation_alias="alert_source_fields_attributes", serialization_alias="alert_source_fields_attributes", description="Array of custom alert fields to be created or associated with this alert source for enhanced alert enrichment and filtering.")
    alert_template_attributes: UpdateAlertsSourceRequestBodyDataAttributesAlertTemplateAttributes | None = None
    sourceable_attributes: UpdateAlertsSourceRequestBodyDataAttributesSourceableAttributes | None = None
    resolution_rule_attributes: UpdateAlertsSourceRequestBodyDataAttributesResolutionRuleAttributes | None = None
class UpdateAlertsSourceRequestBodyData(StrictModel):
    type_: Literal["alert_sources"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'alert_sources'.")
    attributes: UpdateAlertsSourceRequestBodyDataAttributes | None = None
class UpdateAlertsSourceRequestBody(StrictModel):
    data: UpdateAlertsSourceRequestBodyData
class UpdateAlertsSourceRequest(StrictModel):
    """Update an existing alert source configuration, including its type, routing rules, auto-resolution settings, and field mappings. This operation allows you to modify how alerts are ingested, processed, and automatically resolved."""
    path: UpdateAlertsSourceRequestPath
    body: UpdateAlertsSourceRequestBody

# Operation: delete_alert_source
class DeleteAlertsSourceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert source to delete.")
class DeleteAlertsSourceRequest(StrictModel):
    """Permanently delete a specific alert source by its unique identifier. This action cannot be undone."""
    path: DeleteAlertsSourceRequestPath

# Operation: list_incident_alerts
class ListIncidentAlertsRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which to retrieve alerts.")
class ListIncidentAlertsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., incident details, source metadata).")
    filter_source: str | None = Field(default=None, validation_alias="filter[source]", serialization_alias="filter[source]", description="Filter alerts by their source system or origin (e.g., monitoring tool, integration name).")
    filter_groups: str | None = Field(default=None, validation_alias="filter[groups]", serialization_alias="filter[groups]", description="Filter alerts by one or more group identifiers. Specify as comma-separated values to match alerts in any of the specified groups.")
    filter_labels: str | None = Field(default=None, validation_alias="filter[labels]", serialization_alias="filter[labels]", description="Filter alerts by one or more label keys or key-value pairs. Specify as comma-separated values to match alerts with any of the specified labels.")
    filter_started_at__gte: str | None = Field(default=None, validation_alias="filter[started_at][gte]", serialization_alias="filter[started_at][gte]", description="Filter alerts by start time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that started at or after this time.")
    filter_started_at__lte: str | None = Field(default=None, validation_alias="filter[started_at][lte]", serialization_alias="filter[started_at][lte]", description="Filter alerts by start time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that started at or before this time.")
    filter_ended_at__gte: str | None = Field(default=None, validation_alias="filter[ended_at][gte]", serialization_alias="filter[ended_at][gte]", description="Filter alerts by end time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that ended at or after this time.")
    filter_ended_at__lte: str | None = Field(default=None, validation_alias="filter[ended_at][lte]", serialization_alias="filter[ended_at][lte]", description="Filter alerts by end time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that ended at or before this time.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page size to retrieve specific result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of alerts to return per page. Adjust to control result set size for pagination.")
class ListIncidentAlertsRequest(StrictModel):
    """Retrieve a paginated list of alerts associated with a specific incident. Supports filtering by source, groups, labels, and time ranges to narrow results."""
    path: ListIncidentAlertsRequestPath
    query: ListIncidentAlertsRequestQuery | None = None

# Operation: attach_alerts_to_incident
class AttachAlertRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident to which alerts will be attached.")
class AttachAlertRequestBodyDataAttributes(StrictModel):
    alert_ids: list[str] = Field(default=..., validation_alias="alert_ids", serialization_alias="alert_ids", description="An array of alert identifiers to attach to the incident. Each ID references an existing alert that will be linked to this incident.")
class AttachAlertRequestBodyData(StrictModel):
    type_: Literal["alerts"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type being attached, which must be 'alerts' to specify that alert resources are being linked to this incident.")
    attributes: AttachAlertRequestBodyDataAttributes
class AttachAlertRequestBody(StrictModel):
    data: AttachAlertRequestBodyData
class AttachAlertRequest(StrictModel):
    """Attach one or more alerts to an incident. This operation links existing alerts to an incident record for consolidated monitoring and tracking."""
    path: AttachAlertRequestPath
    body: AttachAlertRequestBody

# Operation: list_alerts
class ListAlertsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of fields to include in the response. Specify which alert properties should be returned to optimize payload size.")
    filter_status: str | None = Field(default=None, validation_alias="filter[status]", serialization_alias="filter[status]", description="Filter alerts by their current status (e.g., active, resolved, acknowledged). Only alerts matching the specified status will be returned.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use this to navigate through multiple pages of results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of alerts to return per page. Controls the size of each paginated response.")
class ListAlertsRequest(StrictModel):
    """Retrieve a paginated list of alerts with optional filtering by status and field inclusion. Use this to monitor and review all alerts in the system."""
    query: ListAlertsRequestQuery | None = None

# Operation: create_alert
class CreateAlertRequestBodyDataAttributes(StrictModel):
    noise: Literal["noise", "not_noise"] | None = Field(default=None, validation_alias="noise", serialization_alias="noise", description="Marks whether the alert should be classified as noise or legitimate; use 'noise' to suppress or 'not_noise' to treat as actionable.")
    source: Literal["rootly", "manual", "api", "web", "slack", "email", "workflow", "live_call_routing", "pagerduty", "opsgenie", "victorops", "pagertree", "datadog", "nobl9", "zendesk", "asana", "clickup", "sentry", "rollbar", "jira", "honeycomb", "service_now", "linear", "grafana", "alertmanager", "google_cloud", "generic_webhook", "cloud_watch", "azure", "splunk", "chronosphere", "app_optics", "bug_snag", "monte_carlo", "nagios", "prtg", "catchpoint", "app_dynamics", "checkly", "new_relic", "gitlab"] = Field(default=..., validation_alias="source", serialization_alias="source", description="The origin system or channel that generated the alert, such as monitoring tools (Datadog, Grafana, New Relic), incident platforms (PagerDuty, OpsGenie), ticketing systems (Jira, Linear), or manual/API entry.")
    status: Literal["open", "triggered"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The alert state; 'open' for active alerts or 'triggered' for alerts that have fired. Only available if your organization has Rootly On-Call enabled.")
    summary: str = Field(default=..., validation_alias="summary", serialization_alias="summary", description="A brief, descriptive title for the alert that summarizes the incident or issue.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Extended details about the alert, providing context beyond the summary.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="IDs of services to associate with this alert. Automatically populated if On-Call is enabled and the notification target is a service.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="IDs of groups to associate with this alert. Automatically populated if On-Call is enabled and the notification target is a group.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="IDs of environments where this alert applies, such as production, staging, or development.")
    ended_at: str | None = Field(default=None, validation_alias="ended_at", serialization_alias="ended_at", description="The date and time when the alert resolved or ended, in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="An external identifier to correlate this alert with systems outside Rootly, enabling deduplication and cross-system tracking.")
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL linking to the external system or dashboard where the alert originated or can be viewed.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The ID of the alert urgency level, determining priority and escalation behavior.")
    notification_target_type: Literal["User", "Group", "EscalationPolicy", "Service"] | None = Field(default=None, validation_alias="notification_target_type", serialization_alias="notification_target_type", description="The type of on-call target to notify: a user, group, escalation policy, or service. Only available if your organization has Rootly On-Call enabled.")
    notification_target_id: str | None = Field(default=None, validation_alias="notification_target_id", serialization_alias="notification_target_id", description="The identifier of the specific on-call target (user, group, escalation policy, or service) to notify. Only available if your organization has Rootly On-Call enabled.")
    data: dict[str, Any] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="A flexible object for storing additional custom metadata or attributes associated with the alert.")
class CreateAlertRequestBodyData(StrictModel):
    type_: Literal["alerts"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The alert type; must be 'alerts' to indicate this is an alert resource.")
    attributes: CreateAlertRequestBodyDataAttributes
class CreateAlertRequestBody(StrictModel):
    data: CreateAlertRequestBodyData
class CreateAlertRequest(StrictModel):
    """Creates a new alert in the system with details about the incident source, status, and affected services. Automatically associates the alert with services or groups if On-Call is enabled and a notification target is specified."""
    body: CreateAlertRequestBody

# Operation: get_alert
class GetAlertRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert to retrieve.")
class GetAlertRequest(StrictModel):
    """Retrieves a specific alert by its unique identifier. Use this operation to fetch detailed information about a single alert."""
    path: GetAlertRequestPath

# Operation: update_alert
class UpdateAlertRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert to update.")
class UpdateAlertRequestBodyDataAttributes(StrictModel):
    noise: Literal["noise", "not_noise"] | None = Field(default=None, validation_alias="noise", serialization_alias="noise", description="Mark the alert as noise or not noise to help filter false positives and relevant alerts.")
    source: Literal["rootly", "manual", "api", "web", "slack", "email", "workflow", "live_call_routing", "pagerduty", "opsgenie", "victorops", "pagertree", "datadog", "nobl9", "zendesk", "asana", "clickup", "sentry", "rollbar", "jira", "honeycomb", "service_now", "linear", "grafana", "alertmanager", "google_cloud", "generic_webhook", "cloud_watch", "azure", "splunk", "chronosphere", "app_optics", "bug_snag", "monte_carlo", "nagios", "prtg", "catchpoint", "app_dynamics", "checkly", "new_relic", "gitlab"] | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The originating system or channel that generated the alert, such as monitoring tools (Datadog, Grafana, New Relic), incident platforms (PagerDuty, OpsGenie), or internal sources (manual, API, web, Slack).")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief title or headline summarizing the alert's primary issue.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Detailed information about the alert, including context, symptoms, or troubleshooting steps.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="List of service identifiers to associate with this alert, linking it to specific services or applications.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="List of group identifiers to associate with this alert, linking it to specific teams or organizational groups.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="List of environment identifiers to associate with this alert, such as production, staging, or development.")
    ended_at: str | None = Field(default=None, validation_alias="ended_at", serialization_alias="ended_at", description="The date and time when the alert should be marked as resolved or ended, in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="An external identifier from the source system, useful for tracking and deduplication across integrations.")
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL pointing to the original alert or related resource in the source system for quick reference.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The identifier of the alert urgency level, determining the priority and severity classification of the alert.")
    data: dict[str, Any] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Custom metadata or additional structured data associated with the alert for extensibility and integration purposes.")
class UpdateAlertRequestBodyData(StrictModel):
    attributes: UpdateAlertRequestBodyDataAttributes | None = None
class UpdateAlertRequestBody(StrictModel):
    data: UpdateAlertRequestBodyData | None = None
class UpdateAlertRequest(StrictModel):
    """Update an existing alert with new metadata, classifications, or associations. Modify alert properties such as noise status, summary, description, urgency, and linked resources."""
    path: UpdateAlertRequestPath
    body: UpdateAlertRequestBody | None = None

# Operation: acknowledge_alert
class AcknowledgeAlertRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert to acknowledge.")
class AcknowledgeAlertRequest(StrictModel):
    """Marks a specific alert as acknowledged, indicating that it has been reviewed and noted by the user."""
    path: AcknowledgeAlertRequestPath

# Operation: resolve_alert
class ResolveAlertRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the alert to resolve.")
class ResolveAlertRequestBodyDataAttributes(StrictModel):
    resolution_message: str | None = Field(default=None, validation_alias="resolution_message", serialization_alias="resolution_message", description="Optional explanation describing how or why the alert was resolved.")
    resolve_related_incidents: bool | None = Field(default=None, validation_alias="resolve_related_incidents", serialization_alias="resolve_related_incidents", description="When true, resolves all incidents associated with this alert in addition to the alert itself.")
class ResolveAlertRequestBodyData(StrictModel):
    attributes: ResolveAlertRequestBodyDataAttributes | None = None
class ResolveAlertRequestBody(StrictModel):
    data: ResolveAlertRequestBodyData | None = None
class ResolveAlertRequest(StrictModel):
    """Resolves a specific alert and optionally its associated incidents. Use this operation to mark an alert as resolved with an optional explanation of how it was addressed."""
    path: ResolveAlertRequestPath
    body: ResolveAlertRequestBody | None = None

# Operation: list_audits
class ListAuditsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., user details, API key information).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use with page[size] to control result set boundaries.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of audit records to return per page. Determines the maximum results in each paginated response.")
    filter_user_id: str | None = Field(default=None, validation_alias="filter[user_id]", serialization_alias="filter[user_id]", description="Filter results to audits performed by a specific user ID.")
    filter_api_key_id: str | None = Field(default=None, validation_alias="filter[api_key_id]", serialization_alias="filter[api_key_id]", description="Filter results to audits associated with a specific API key ID.")
    filter_source: str | None = Field(default=None, validation_alias="filter[source]", serialization_alias="filter[source]", description="Filter results by the source of the audit action (e.g., api, dashboard, webhook).")
    filter_item_type: str | None = Field(default=None, validation_alias="filter[item_type]", serialization_alias="filter[item_type]", description="Filter results by the type of item that was audited (e.g., user, api_key, organization).")
    sort: str | None = Field(default=None, description="Sort results by a specified field in ascending or descending order (format: field or -field for descending).")
class ListAuditsRequest(StrictModel):
    """Retrieve a paginated list of audit logs with optional filtering by user, API key, source, or item type, and configurable sorting."""
    query: ListAuditsRequestQuery | None = None

# Operation: get_authorization
class GetAuthorizationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the authorization to retrieve.")
class GetAuthorizationRequest(StrictModel):
    """Retrieves a specific authorization by its unique identifier. Use this to fetch details about an existing authorization."""
    path: GetAuthorizationRequestPath

# Operation: delete_authorization
class DeleteAuthorizationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the authorization to delete.")
class DeleteAuthorizationRequest(StrictModel):
    """Permanently delete a specific authorization by its unique identifier. This action cannot be undone."""
    path: DeleteAuthorizationRequestPath

# Operation: list_catalog_entities
class ListCatalogEntitiesRequestPath(StrictModel):
    catalog_id: str = Field(default=..., description="The unique identifier of the catalog containing the entities to list.")
class ListCatalogEntitiesRequestQuery(StrictModel):
    include: Literal["catalog", "properties"] | None = Field(default=None, description="Comma-separated list of related data to include in the response. Options are 'catalog' (parent catalog details) and 'properties' (entity properties).")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(default=None, description="Comma-separated list of fields to sort results by. Use 'created_at' or 'updated_at' for chronological sorting, 'position' for custom ordering. Prefix with '-' for descending order (e.g., '-created_at' for newest first).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of entities to return per page. Use with page[number] to control result set size.")
class ListCatalogEntitiesRequest(StrictModel):
    """Retrieve a paginated list of entities within a specific catalog, with optional filtering to include related catalog and property information."""
    path: ListCatalogEntitiesRequestPath
    query: ListCatalogEntitiesRequestQuery | None = None

# Operation: create_catalog_entity
class CreateCatalogEntityRequestPath(StrictModel):
    catalog_id: str = Field(default=..., description="The unique identifier of the catalog where the entity will be created.")
class CreateCatalogEntityRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the catalog entity.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation or summary of the catalog entity's purpose and content.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The default ordering position for this entity when displayed in a list view. Lower values appear first.")
class CreateCatalogEntityRequestBodyData(StrictModel):
    type_: Literal["catalog_entities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type classification for this entity. Must be set to 'catalog_entities'.")
    attributes: CreateCatalogEntityRequestBodyDataAttributes
class CreateCatalogEntityRequestBody(StrictModel):
    data: CreateCatalogEntityRequestBodyData
class CreateCatalogEntityRequest(StrictModel):
    """Creates a new catalog entity with the specified metadata. The entity will be added to the catalog and can be positioned within list displays."""
    path: CreateCatalogEntityRequestPath
    body: CreateCatalogEntityRequestBody

# Operation: get_catalog_entity
class GetCatalogEntityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Catalog Entity to retrieve.")
class GetCatalogEntityRequestQuery(StrictModel):
    include: Literal["catalog", "properties"] | None = Field(default=None, description="Optional comma-separated list of related data to include in the response. Valid options are 'catalog' (to include parent catalog information) and 'properties' (to include entity properties).")
class GetCatalogEntityRequest(StrictModel):
    """Retrieves a specific Catalog Entity by its unique identifier, with optional inclusion of related catalog and properties data."""
    path: GetCatalogEntityRequestPath
    query: GetCatalogEntityRequestQuery | None = None

# Operation: update_catalog_entity
class UpdateCatalogEntityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Catalog Entity to update.")
class UpdateCatalogEntityRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the Catalog Entity. Provides additional context or details about the entity.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The default position (order) in which this item appears when displayed in a list. Lower numbers appear first.")
class UpdateCatalogEntityRequestBodyData(StrictModel):
    type_: Literal["catalog_entities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'catalog_entities' to specify this is a Catalog Entity resource.")
    attributes: UpdateCatalogEntityRequestBodyDataAttributes | None = None
class UpdateCatalogEntityRequestBody(StrictModel):
    data: UpdateCatalogEntityRequestBodyData
class UpdateCatalogEntityRequest(StrictModel):
    """Update an existing Catalog Entity by its unique identifier. Modify the entity's description and display position within catalog lists."""
    path: UpdateCatalogEntityRequestPath
    body: UpdateCatalogEntityRequestBody

# Operation: delete_catalog_entity
class DeleteCatalogEntityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Catalog Entity to delete.")
class DeleteCatalogEntityRequest(StrictModel):
    """Permanently delete a specific Catalog Entity by its unique identifier. This action cannot be undone."""
    path: DeleteCatalogEntityRequestPath

# Operation: list_catalog_entity_properties
class ListCatalogEntityPropertiesRequestPath(StrictModel):
    catalog_entity_id: str = Field(default=..., description="The unique identifier of the catalog entity whose properties you want to list.")
class ListCatalogEntityPropertiesRequestQuery(StrictModel):
    include: Literal["catalog_entity", "catalog_field"] | None = Field(default=None, description="Comma-separated list of related entities to include in the response. Valid options are 'catalog_entity' and 'catalog_field'.")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Field(default=None, description="Comma-separated list of fields to sort results by. Use 'created_at' or 'updated_at' for ascending order, or prefix with '-' for descending order (e.g., '-created_at').")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination (1-indexed). Use with page[size] to retrieve specific result pages.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results per page for pagination. Defines how many properties are returned in each page.")
    filter_catalog_field_id: str | None = Field(default=None, validation_alias="filter[catalog_field_id]", serialization_alias="filter[catalog_field_id]", description="Filter results by catalog field ID to return only properties associated with a specific field.")
    filter_key: str | None = Field(default=None, validation_alias="filter[key]", serialization_alias="filter[key]", description="Filter results by property key to find properties matching a specific key name.")
class ListCatalogEntityPropertiesRequest(StrictModel):
    """Retrieve a paginated list of properties for a specific catalog entity, with optional filtering, sorting, and related entity inclusion."""
    path: ListCatalogEntityPropertiesRequestPath
    query: ListCatalogEntityPropertiesRequestQuery | None = None

# Operation: create_catalog_entity_property
class CreateCatalogEntityPropertyRequestPath(StrictModel):
    catalog_entity_id: str = Field(default=..., description="The unique identifier of the catalog entity to which this property will be added.")
class CreateCatalogEntityPropertyRequestBodyDataAttributes(StrictModel):
    catalog_field_id: str = Field(default=..., validation_alias="catalog_field_id", serialization_alias="catalog_field_id", description="The unique identifier of the catalog field that this property references.")
    key: Literal["text", "catalog_entity"] = Field(default=..., validation_alias="key", serialization_alias="key", description="The property key type, which determines the value format: 'text' for string values or 'catalog_entity' for entity references.")
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The property value, formatted according to the specified key type (plain text for 'text' keys, entity identifier for 'catalog_entity' keys).")
class CreateCatalogEntityPropertyRequestBodyData(StrictModel):
    type_: Literal["catalog_entity_properties"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this operation, which must be 'catalog_entity_properties'.")
    attributes: CreateCatalogEntityPropertyRequestBodyDataAttributes
class CreateCatalogEntityPropertyRequestBody(StrictModel):
    data: CreateCatalogEntityPropertyRequestBodyData
class CreateCatalogEntityPropertyRequest(StrictModel):
    """Creates a new property for a catalog entity, associating a catalog field with a typed value. This establishes a key-value relationship within the catalog entity's property structure."""
    path: CreateCatalogEntityPropertyRequestPath
    body: CreateCatalogEntityPropertyRequestBody

# Operation: get_catalog_entity_property
class GetCatalogEntityPropertyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Catalog Entity Property to retrieve.")
class GetCatalogEntityPropertyRequestQuery(StrictModel):
    include: Literal["catalog_entity", "catalog_field"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Valid options are 'catalog_entity' and 'catalog_field'.")
class GetCatalogEntityPropertyRequest(StrictModel):
    """Retrieves a specific Catalog Entity Property by its unique identifier. Optionally include related Catalog Entity or Catalog Field data in the response."""
    path: GetCatalogEntityPropertyRequestPath
    query: GetCatalogEntityPropertyRequestQuery | None = None

# Operation: update_catalog_entity_property
class UpdateCatalogEntityPropertyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the catalog entity property to update.")
class UpdateCatalogEntityPropertyRequestBodyDataAttributes(StrictModel):
    key: Literal["text", "catalog_entity"] | None = Field(default=None, validation_alias="key", serialization_alias="key", description="The property key type, which determines whether the property stores plain text or references another catalog entity. Valid options are 'text' for string values or 'catalog_entity' for entity references.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The property value to store, formatted according to the specified key type (plain text for 'text' keys, or an entity identifier for 'catalog_entity' keys).")
class UpdateCatalogEntityPropertyRequestBodyData(StrictModel):
    type_: Literal["catalog_entity_properties"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'catalog_entity_properties' to specify the entity being updated.")
    attributes: UpdateCatalogEntityPropertyRequestBodyDataAttributes | None = None
class UpdateCatalogEntityPropertyRequestBody(StrictModel):
    data: UpdateCatalogEntityPropertyRequestBodyData
class UpdateCatalogEntityPropertyRequest(StrictModel):
    """Update a specific catalog entity property by its identifier. Modify the property's key type and associated value to reflect changes in how catalog entities are characterized."""
    path: UpdateCatalogEntityPropertyRequestPath
    body: UpdateCatalogEntityPropertyRequestBody

# Operation: delete_catalog_entity_property
class DeleteCatalogEntityPropertyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Catalog Entity Property to delete.")
class DeleteCatalogEntityPropertyRequest(StrictModel):
    """Permanently delete a specific Catalog Entity Property by its unique identifier. This operation removes the property and all associated data."""
    path: DeleteCatalogEntityPropertyRequestPath

# Operation: list_catalog_fields
class ListCatalogFieldsRequestPath(StrictModel):
    catalog_id: str = Field(default=..., description="The unique identifier of the catalog whose fields you want to list.")
class ListCatalogFieldsRequestQuery(StrictModel):
    include: Literal["catalog"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Use 'catalog' to include the parent catalog data.")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(default=None, description="Comma-separated list of fields to sort by. Prefix with a hyphen (e.g., '-created_at') to sort in descending order. Available fields: created_at, updated_at, and position.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination (1-indexed). Use with page[size] to retrieve specific result pages.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results per page for pagination. Use with page[number] to control result set size.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter results by field kind. Specify the desired field type to narrow the returned fields.")
class ListCatalogFieldsRequest(StrictModel):
    """Retrieve a paginated list of fields within a specific catalog. Optionally filter by field kind, include related catalog data, and sort results by creation date, update date, or field position."""
    path: ListCatalogFieldsRequestPath
    query: ListCatalogFieldsRequestQuery | None = None

# Operation: create_catalog_field
class CreateCatalogFieldRequestPath(StrictModel):
    catalog_id: str = Field(default=..., description="The unique identifier of the catalog where the field will be created.")
class CreateCatalogFieldRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the catalog field.")
    kind: Literal["text", "reference"] = Field(default=..., validation_alias="kind", serialization_alias="kind", description="The data type of the field; either 'text' for string values or 'reference' to link to items in another catalog.")
    kind_catalog_id: str | None = Field(default=None, validation_alias="kind_catalog_id", serialization_alias="kind_catalog_id", description="When the field kind is 'reference', specifies which catalog the referenced items must belong to. Required for reference-type fields.")
    multiple: bool | None = Field(default=None, validation_alias="multiple", serialization_alias="multiple", description="If true, the field can store multiple values; if false or omitted, only a single value is allowed.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The default display order of this field in list views; lower numbers appear first.")
class CreateCatalogFieldRequestBodyData(StrictModel):
    type_: Literal["catalog_fields"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'catalog_fields'.")
    attributes: CreateCatalogFieldRequestBodyDataAttributes
class CreateCatalogFieldRequestBody(StrictModel):
    data: CreateCatalogFieldRequestBodyData
class CreateCatalogFieldRequest(StrictModel):
    """Creates a new field within a catalog to define custom attributes for catalog items. Fields can store text values or references to items in other catalogs, and can be configured to accept single or multiple values."""
    path: CreateCatalogFieldRequestPath
    body: CreateCatalogFieldRequestBody

# Operation: get_catalog_field
class GetCatalogFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Catalog Field to retrieve.")
class GetCatalogFieldRequestQuery(StrictModel):
    include: Literal["catalog"] | None = Field(default=None, description="Optional comma-separated list of related resources to include in the response. Specify 'catalog' to include the parent catalog information.")
class GetCatalogFieldRequest(StrictModel):
    """Retrieves a specific Catalog Field by its unique identifier. Optionally include related catalog information in the response."""
    path: GetCatalogFieldRequestPath
    query: GetCatalogFieldRequestQuery | None = None

# Operation: update_catalog_field
class UpdateCatalogFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the catalog field to update.")
class UpdateCatalogFieldRequestBodyDataAttributes(StrictModel):
    slug: str | None = Field(default=None, validation_alias="slug", serialization_alias="slug", description="A URL-friendly identifier for the catalog field used in references and lookups.")
    kind: Literal["text", "reference"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="The data type of the field. Choose 'text' for string values or 'reference' to link to items in another catalog.")
    kind_catalog_id: str | None = Field(default=None, validation_alias="kind_catalog_id", serialization_alias="kind_catalog_id", description="When kind is set to 'reference', specify the catalog ID to restrict field values to items from that catalog.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The default display order position when this field appears in a list view. Lower numbers appear first.")
class UpdateCatalogFieldRequestBodyData(StrictModel):
    type_: Literal["catalog_fields"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'catalog_fields' to specify this is a catalog field resource.")
    attributes: UpdateCatalogFieldRequestBodyDataAttributes | None = None
class UpdateCatalogFieldRequestBody(StrictModel):
    data: UpdateCatalogFieldRequestBodyData
class UpdateCatalogFieldRequest(StrictModel):
    """Update a specific catalog field by its ID. Modify field properties such as slug, kind, associated catalog reference, and display position."""
    path: UpdateCatalogFieldRequestPath
    body: UpdateCatalogFieldRequestBody

# Operation: delete_catalog_field
class DeleteCatalogFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the catalog field to delete.")
class DeleteCatalogFieldRequest(StrictModel):
    """Permanently delete a catalog field by its unique identifier. This action cannot be undone."""
    path: DeleteCatalogFieldRequestPath

# Operation: list_catalogs
class ListCatalogsRequestQuery(StrictModel):
    include: Literal["fields", "entities"] | None = Field(default=None, description="Comma-separated list of related data to include in the response. Choose from 'fields' to include field definitions or 'entities' to include entity information.")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(default=None, description="Comma-separated list of fields to sort results by. Use 'created_at', 'updated_at', or 'position' for ascending order, or prefix with a hyphen (e.g., '-created_at') for descending order.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of catalogs to return per page.")
class ListCatalogsRequest(StrictModel):
    """Retrieve a paginated list of catalogs with optional inclusion of related data and sorting capabilities."""
    query: ListCatalogsRequestQuery | None = None

# Operation: create_catalog
class CreateCatalogRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the catalog. This is the primary identifier users will see when viewing catalogs.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional detailed description of the catalog's purpose or contents.")
    icon: Literal["globe-alt", "server-stack", "users", "user-group", "chart-bar", "shapes", "light-bulb", "cursor-arrow-ripple"] | None = Field(default=None, validation_alias="icon", serialization_alias="icon", description="An optional visual icon to represent the catalog. Choose from predefined icons: globe-alt, server-stack, users, user-group, chart-bar, shapes, light-bulb, or cursor-arrow-ripple.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="An optional numeric position that determines the catalog's order when displayed in lists. Lower numbers appear first.")
class CreateCatalogRequestBodyData(StrictModel):
    type_: Literal["catalogs"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'catalogs' to indicate this is a catalog resource.")
    attributes: CreateCatalogRequestBodyDataAttributes
class CreateCatalogRequestBody(StrictModel):
    data: CreateCatalogRequestBodyData
class CreateCatalogRequest(StrictModel):
    """Creates a new catalog with the specified name, description, and display settings. The catalog will be added to your catalog collection and can be organized with an icon and position."""
    body: CreateCatalogRequestBody

# Operation: get_catalog
class GetCatalogRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the catalog to retrieve.")
class GetCatalogRequest(StrictModel):
    """Retrieves a specific catalog by its unique identifier. Use this operation to fetch detailed information about a catalog."""
    path: GetCatalogRequestPath

# Operation: update_catalog
class UpdateCatalogRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the catalog to update.")
class UpdateCatalogRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the catalog's purpose or contents.")
    icon: Literal["globe-alt", "server-stack", "users", "user-group", "chart-bar", "shapes", "light-bulb", "cursor-arrow-ripple"] | None = Field(default=None, validation_alias="icon", serialization_alias="icon", description="A visual icon representing the catalog. Choose from predefined icon options: globe-alt, server-stack, users, user-group, chart-bar, shapes, light-bulb, or cursor-arrow-ripple.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order position of the catalog when shown in a list. Lower numbers appear first.")
class UpdateCatalogRequestBodyData(StrictModel):
    type_: Literal["catalogs"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be set to 'catalogs' to identify this as a catalog resource.")
    attributes: UpdateCatalogRequestBodyDataAttributes | None = None
class UpdateCatalogRequestBody(StrictModel):
    data: UpdateCatalogRequestBodyData
class UpdateCatalogRequest(StrictModel):
    """Update an existing catalog's metadata including its description, visual icon, and display position. Modify any combination of catalog properties by providing the catalog ID and updated values."""
    path: UpdateCatalogRequestPath
    body: UpdateCatalogRequestBody

# Operation: delete_catalog
class DeleteCatalogRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the catalog to delete.")
class DeleteCatalogRequest(StrictModel):
    """Permanently delete a catalog and all its associated data. This action cannot be undone."""
    path: DeleteCatalogRequestPath

# Operation: list_causes
class ListCausesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., organizations, campaigns). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of causes to return per page. Adjust to balance between response size and number of requests needed.")
class ListCausesRequest(StrictModel):
    """Retrieve a paginated list of all causes. Use pagination parameters to control the number of results and navigate through pages."""
    query: ListCausesRequestQuery | None = None

# Operation: create_cause
class CreateCauseRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the cause. This is a required field that identifies the cause.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional detailed description providing context or additional information about the cause.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="An optional numeric position value that determines the ordering or display sequence of the cause relative to others.")
class CreateCauseRequestBodyData(StrictModel):
    type_: Literal["causes"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'causes' for this operation.")
    attributes: CreateCauseRequestBodyDataAttributes
class CreateCauseRequestBody(StrictModel):
    data: CreateCauseRequestBodyData
class CreateCauseRequest(StrictModel):
    """Creates a new cause with the provided name, description, and optional positioning. The cause type is fixed as 'causes'."""
    body: CreateCauseRequestBody

# Operation: get_cause
class GetCauseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the cause to retrieve.")
class GetCauseRequest(StrictModel):
    """Retrieves a specific cause by its unique identifier. Use this operation to fetch detailed information about a single cause."""
    path: GetCauseRequestPath

# Operation: update_cause
class UpdateCauseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the cause to update.")
class UpdateCauseRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the cause, explaining its purpose or context.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of the cause in a list or sequence, used for sorting or display ordering.")
class UpdateCauseRequestBodyData(StrictModel):
    type_: Literal["causes"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'causes' to specify this is a cause resource.")
    attributes: UpdateCauseRequestBodyDataAttributes | None = None
class UpdateCauseRequestBody(StrictModel):
    data: UpdateCauseRequestBodyData
class UpdateCauseRequest(StrictModel):
    """Update an existing cause by its ID, allowing modification of its description and position in the list."""
    path: UpdateCauseRequestPath
    body: UpdateCauseRequestBody

# Operation: delete_cause
class DeleteCauseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the cause to delete.")
class DeleteCauseRequest(StrictModel):
    """Permanently delete a cause by its unique identifier. This action cannot be undone."""
    path: DeleteCauseRequestPath

# Operation: list_custom_forms
class ListCustomFormsRequestQuery(StrictModel):
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of custom forms to return per page.")
    filter_command: str | None = Field(default=None, validation_alias="filter[command]", serialization_alias="filter[command]", description="Filter custom forms by command type or name.")
    sort: str | None = Field(default=None, description="Sort the results by a specified field in ascending or descending order.")
class ListCustomFormsRequest(StrictModel):
    """Retrieve a paginated list of custom forms with optional filtering and sorting capabilities."""
    query: ListCustomFormsRequestQuery | None = None

# Operation: create_custom_form
class CreateCustomFormRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the custom form; used to identify the form in the UI and logs.")
    slug: str | None = Field(default=None, validation_alias="slug", serialization_alias="slug", description="A URL-friendly identifier for the custom form; use this slug value in form_field.shown or form_field.required to associate specific fields with this form.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional description providing additional context or instructions for the custom form.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the custom form is active and available for use; defaults to false if not specified.")
    command: str = Field(default=..., validation_alias="command", serialization_alias="command", description="The Slack slash command (e.g., '/mycommand') that users invoke to trigger and display this form.")
class CreateCustomFormRequestBodyData(StrictModel):
    type_: Literal["custom_forms"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The form type identifier; must be set to 'custom_forms' to indicate this is a custom form resource.")
    attributes: CreateCustomFormRequestBodyDataAttributes
class CreateCustomFormRequestBody(StrictModel):
    data: CreateCustomFormRequestBodyData
class CreateCustomFormRequest(StrictModel):
    """Creates a new custom form that can be triggered via a Slack command. The form can include custom fields by referencing the form slug in field associations."""
    body: CreateCustomFormRequestBody

# Operation: get_custom_form
class GetCustomFormRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom form to retrieve.")
class GetCustomFormRequest(StrictModel):
    """Retrieves a specific custom form by its unique identifier. Use this operation to fetch the complete details and configuration of a custom form."""
    path: GetCustomFormRequestPath

# Operation: update_custom_form
class UpdateCustomFormRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom form to update.")
class UpdateCustomFormRequestBodyDataAttributes(StrictModel):
    slug: str | None = Field(default=None, validation_alias="slug", serialization_alias="slug", description="A URL-friendly identifier for the custom form. Use this slug value in form_field.shown or form_field.required to associate specific form fields with this custom form.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the custom form's purpose or usage.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the custom form is active and available for use.")
    command: str | None = Field(default=None, validation_alias="command", serialization_alias="command", description="The Slack slash command that triggers this custom form when invoked by users.")
class UpdateCustomFormRequestBodyData(StrictModel):
    type_: Literal["custom_forms"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'custom_forms' to specify this is a custom form resource.")
    attributes: UpdateCustomFormRequestBodyDataAttributes | None = None
class UpdateCustomFormRequestBody(StrictModel):
    data: UpdateCustomFormRequestBodyData
class UpdateCustomFormRequest(StrictModel):
    """Update an existing custom form configuration by its ID. Modify form metadata, slug, description, enabled status, or associated Slack command trigger."""
    path: UpdateCustomFormRequestPath
    body: UpdateCustomFormRequestBody

# Operation: delete_custom_form
class DeleteCustomFormRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom form to delete.")
class DeleteCustomFormRequest(StrictModel):
    """Permanently delete a custom form by its unique identifier. This action cannot be undone."""
    path: DeleteCustomFormRequestPath

# Operation: list_dashboard_panels
class ListDashboardPanelsRequestPath(StrictModel):
    dashboard_id: str = Field(default=..., description="The unique identifier of the dashboard containing the panels to retrieve.")
class ListDashboardPanelsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., metadata, configuration details). Reduces need for additional requests.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of panels to return per page. Adjust to balance response size and number of requests needed.")
class ListDashboardPanelsRequest(StrictModel):
    """Retrieve a paginated list of panels configured within a specific dashboard. Use this to display dashboard contents or manage panel organization."""
    path: ListDashboardPanelsRequestPath
    query: ListDashboardPanelsRequestQuery | None = None

# Operation: create_dashboard_panel
class CreateDashboardPanelRequestPath(StrictModel):
    dashboard_id: str = Field(default=..., description="The unique identifier of the dashboard where the panel will be created.")
class CreateDashboardPanelRequestBodyDataAttributesParamsLegend(StrictModel):
    groups: Literal["all", "charted"] | None = Field(default=None, validation_alias="groups", serialization_alias="groups", description="Controls which data groups are included in the visualization. Use 'all' to include all available groups, or 'charted' to include only groups that are actively charted. Defaults to 'all'.")
class CreateDashboardPanelRequestBodyDataAttributesParamsDatalabels(StrictModel):
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the panel is active and visible on the dashboard. When disabled, the panel is hidden but retained.")
class CreateDashboardPanelRequestBodyDataAttributesParams(StrictModel):
    display: Literal["line_chart", "line_stepped_chart", "column_chart", "stacked_column_chart", "monitoring_chart", "pie_chart", "table", "aggregate_value"] | None = Field(default=None, validation_alias="display", serialization_alias="display", description="The visualization format for the panel. Choose from line charts, stepped line charts, column charts, stacked columns, monitoring charts, pie charts, tables, or aggregate value displays.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable label or explanation for the panel's purpose and content.")
    table_fields: list[str] | None = Field(default=None, validation_alias="table_fields", serialization_alias="table_fields", description="An ordered list of field names to display in table-format panels. Field order in this array determines column order in the rendered table.")
    datasets: list[CreateDashboardPanelBodyDataAttributesParamsDatasetsItem] | None = Field(default=None, validation_alias="datasets", serialization_alias="datasets", description="An array of dataset configurations that define the data sources and metrics to visualize in this panel.")
    legend: CreateDashboardPanelRequestBodyDataAttributesParamsLegend | None = None
    datalabels: CreateDashboardPanelRequestBodyDataAttributesParamsDatalabels | None = None
class CreateDashboardPanelRequestBodyDataAttributesPosition(StrictModel):
    x: float = Field(default=..., validation_alias="x", serialization_alias="x", description="The horizontal grid position (column) where the panel is placed on the dashboard.")
    y: float = Field(default=..., validation_alias="y", serialization_alias="y", description="The vertical grid position (row) where the panel is placed on the dashboard.")
    w: float = Field(default=..., validation_alias="w", serialization_alias="w", description="The width of the panel measured in grid units.")
    h: float = Field(default=..., validation_alias="h", serialization_alias="h", description="The height of the panel measured in grid units.")
class CreateDashboardPanelRequestBodyDataAttributes(StrictModel):
    params: CreateDashboardPanelRequestBodyDataAttributesParams | None = None
    position: CreateDashboardPanelRequestBodyDataAttributesPosition
class CreateDashboardPanelRequestBodyData(StrictModel):
    type_: Literal["dashboard_panels"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for dashboard panels; must be set to 'dashboard_panels'.")
    attributes: CreateDashboardPanelRequestBodyDataAttributes
class CreateDashboardPanelRequestBody(StrictModel):
    data: CreateDashboardPanelRequestBodyData
class CreateDashboardPanelRequest(StrictModel):
    """Creates a new panel on a dashboard with specified visualization type, position, and data configuration. Panels are positioned using grid coordinates and can display various chart types or tables."""
    path: CreateDashboardPanelRequestPath
    body: CreateDashboardPanelRequestBody

# Operation: duplicate_dashboard_panel
class DuplicateDashboardPanelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard panel to duplicate.")
class DuplicateDashboardPanelRequest(StrictModel):
    """Creates a duplicate copy of an existing dashboard panel, preserving its configuration and settings. The duplicated panel is added to the same dashboard as the original."""
    path: DuplicateDashboardPanelRequestPath

# Operation: get_dashboard_panel
class GetDashboardPanelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard panel to retrieve.")
class GetDashboardPanelRequestQuery(StrictModel):
    range_: str | None = Field(default=None, validation_alias="range", serialization_alias="range", description="Optional date range for filtering panel data, specified as two ISO 8601 timestamps separated by the word 'to' (e.g., start timestamp to end timestamp).")
    period: str | None = Field(default=None, description="Optional time period for grouping data within the panel. Valid values are 'day', 'week', or 'month'.")
    time_zone: str | None = Field(default=None, description="Optional time zone identifier to apply when grouping data by the specified period. Use standard IANA time zone names.")
class GetDashboardPanelRequest(StrictModel):
    """Retrieves a specific dashboard panel by its unique identifier, with optional filtering by date range and time-based aggregation."""
    path: GetDashboardPanelRequestPath
    query: GetDashboardPanelRequestQuery | None = None

# Operation: update_dashboard_panel
class UpdateDashboardPanelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard panel to update.")
class UpdateDashboardPanelRequestBodyDataAttributesParamsLegend(StrictModel):
    groups: Literal["all", "charted"] | None = Field(default=None, validation_alias="groups", serialization_alias="groups", description="Controls which data groups to include in the visualization. Use 'all' to include all groups or 'charted' to include only charted groups. Defaults to 'all'.")
class UpdateDashboardPanelRequestBodyDataAttributesParamsDatalabels(StrictModel):
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the panel is active and visible on the dashboard.")
class UpdateDashboardPanelRequestBodyDataAttributesParams(StrictModel):
    display: Literal["line_chart", "line_stepped_chart", "column_chart", "stacked_column_chart", "monitoring_chart", "pie_chart", "table", "aggregate_value"] | None = Field(default=None, validation_alias="display", serialization_alias="display", description="The visualization type for the panel. Choose from line chart, stepped line chart, column chart, stacked column chart, monitoring chart, pie chart, table, or aggregate value display.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the panel's purpose or content.")
    table_fields: list[str] | None = Field(default=None, validation_alias="table_fields", serialization_alias="table_fields", description="An array of field names to display when using table visualization. Order determines column sequence.")
    datasets: list[UpdateDashboardPanelBodyDataAttributesParamsDatasetsItem] | None = Field(default=None, validation_alias="datasets", serialization_alias="datasets", description="An array of dataset configurations that define the data sources and metrics for the panel.")
    legend: UpdateDashboardPanelRequestBodyDataAttributesParamsLegend | None = None
    datalabels: UpdateDashboardPanelRequestBodyDataAttributesParamsDatalabels | None = None
class UpdateDashboardPanelRequestBodyDataAttributesPosition(StrictModel):
    x: float = Field(default=..., validation_alias="x", serialization_alias="x", description="The horizontal position (x-coordinate) of the panel on the dashboard grid.")
    y: float = Field(default=..., validation_alias="y", serialization_alias="y", description="The vertical position (y-coordinate) of the panel on the dashboard grid.")
    w: float = Field(default=..., validation_alias="w", serialization_alias="w", description="The width of the panel on the dashboard grid.")
    h: float = Field(default=..., validation_alias="h", serialization_alias="h", description="The height of the panel on the dashboard grid.")
class UpdateDashboardPanelRequestBodyDataAttributes(StrictModel):
    params: UpdateDashboardPanelRequestBodyDataAttributesParams | None = None
    position: UpdateDashboardPanelRequestBodyDataAttributesPosition
class UpdateDashboardPanelRequestBodyData(StrictModel):
    attributes: UpdateDashboardPanelRequestBodyDataAttributes
class UpdateDashboardPanelRequestBody(StrictModel):
    data: UpdateDashboardPanelRequestBodyData
class UpdateDashboardPanelRequest(StrictModel):
    """Update a dashboard panel's configuration, including its display type, data sources, layout position, and visibility settings."""
    path: UpdateDashboardPanelRequestPath
    body: UpdateDashboardPanelRequestBody

# Operation: delete_dashboard_panel
class DeleteDashboardPanelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard panel to delete.")
class DeleteDashboardPanelRequest(StrictModel):
    """Permanently delete a specific dashboard panel by its unique identifier. This action cannot be undone."""
    path: DeleteDashboardPanelRequestPath

# Operation: list_dashboards
class ListDashboardsRequestQuery(StrictModel):
    include: Literal["panels"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Use 'panels' to include panel data for each dashboard.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to control which dashboards are returned.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of dashboards to return per page. Use with page[number] to paginate through results.")
class ListDashboardsRequest(StrictModel):
    """Retrieve a paginated list of dashboards. Optionally include related panel data for each dashboard."""
    query: ListDashboardsRequestQuery | None = None

# Operation: create_dashboard
class CreateDashboardRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the dashboard that appears in the UI and search results.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional description providing context or details about the dashboard's purpose and contents.")
    owner: Literal["user", "team"] = Field(default=..., validation_alias="owner", serialization_alias="owner", description="Specifies who owns the dashboard: either a 'user' (individual ownership) or 'team' (shared team ownership).")
    public: bool | None = Field(default=None, validation_alias="public", serialization_alias="public", description="When enabled, the dashboard is visible to all users; when disabled, access is restricted to the owner and explicitly granted users.")
    range_: str | None = Field(default=None, validation_alias="range", serialization_alias="range", description="Sets the time window for which dashboard panels display data (e.g., last 7 days, last 30 days). Format as an ISO 8601 duration or relative time expression.")
    auto_refresh: bool | None = Field(default=None, validation_alias="auto_refresh", serialization_alias="auto_refresh", description="When enabled, the dashboard automatically refreshes panel data in the UI at regular intervals without requiring manual refresh.")
    color: Literal["#FCF2CF", "#D7F5E1", "#E9E2FF", "#FAE6E8", "#FAEEE6"] | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hex color code that customizes the dashboard's visual theme. Choose from: light yellow (#FCF2CF), light green (#D7F5E1), light purple (#E9E2FF), light pink (#FAE6E8), or light orange (#FAEEE6).")
    icon: str | None = Field(default=None, validation_alias="icon", serialization_alias="icon", description="An optional emoji icon displayed alongside the dashboard name for quick visual identification.")
    period: Literal["day", "week", "month"] | None = Field(default=None, validation_alias="period", serialization_alias="period", description="Defines the time-based grouping for aggregating panel data: 'day' for daily buckets, 'week' for weekly buckets, or 'month' for monthly buckets.")
class CreateDashboardRequestBodyData(StrictModel):
    type_: Literal["dashboards"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'dashboards' to indicate this is a dashboard resource.")
    attributes: CreateDashboardRequestBodyDataAttributes
class CreateDashboardRequestBody(StrictModel):
    data: CreateDashboardRequestBodyData
class CreateDashboardRequest(StrictModel):
    """Creates a new dashboard with customizable settings for data visualization and sharing. Configure the dashboard's appearance, refresh behavior, and data aggregation period."""
    body: CreateDashboardRequestBody

# Operation: duplicate_dashboard
class DuplicateDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to duplicate.")
class DuplicateDashboardRequest(StrictModel):
    """Creates a copy of an existing dashboard with all its configuration, layout, and widgets. The duplicated dashboard will be a complete independent instance."""
    path: DuplicateDashboardRequestPath

# Operation: set_dashboard_as_default
class SetDefaultDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to set as default.")
class SetDefaultDashboardRequest(StrictModel):
    """Sets the specified dashboard as the default dashboard for the current user. The default dashboard is displayed when the user first accesses the dashboard interface."""
    path: SetDefaultDashboardRequestPath

# Operation: get_dashboard
class GetDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to retrieve.")
class GetDashboardRequestQuery(StrictModel):
    include: Literal["panels"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Supports 'panels' to include dashboard panel definitions.")
class GetDashboardRequest(StrictModel):
    """Retrieves a specific dashboard by its unique identifier. Optionally include related resources such as panels in the response."""
    path: GetDashboardRequestPath
    query: GetDashboardRequestQuery | None = None

# Operation: update_dashboard
class UpdateDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to update.")
class UpdateDashboardRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the dashboard's purpose or content.")
    owner: Literal["user", "team"] | None = Field(default=None, validation_alias="owner", serialization_alias="owner", description="The ownership model of the dashboard: either 'user' for individual ownership or 'team' for shared team ownership.")
    public: bool | None = Field(default=None, validation_alias="public", serialization_alias="public", description="Controls whether the dashboard is publicly accessible or restricted to authorized users.")
    range_: str | None = Field(default=None, validation_alias="range", serialization_alias="range", description="The time window for which dashboard panels display data (e.g., last 7 days, last 30 days).")
    auto_refresh: bool | None = Field(default=None, validation_alias="auto_refresh", serialization_alias="auto_refresh", description="Enables automatic UI updates when new data becomes available, keeping the dashboard current without manual refresh.")
    color: Literal["#FCF2CF", "#D7F5E1", "#E9E2FF", "#FAE6E8", "#FAEEE6"] | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hex color code for the dashboard's visual theme. Choose from: light yellow (#FCF2CF), light green (#D7F5E1), light purple (#E9E2FF), light pink (#FAE6E8), or light orange (#FAEEE6).")
    icon: str | None = Field(default=None, validation_alias="icon", serialization_alias="icon", description="An emoji icon that visually represents the dashboard in navigation and listings.")
    period: Literal["day", "week", "month"] | None = Field(default=None, validation_alias="period", serialization_alias="period", description="The time-based grouping period for aggregating dashboard panel data: 'day' for daily granularity, 'week' for weekly, or 'month' for monthly.")
class UpdateDashboardRequestBodyData(StrictModel):
    attributes: UpdateDashboardRequestBodyDataAttributes | None = None
class UpdateDashboardRequestBody(StrictModel):
    data: UpdateDashboardRequestBodyData | None = None
class UpdateDashboardRequest(StrictModel):
    """Update an existing dashboard's configuration, including its metadata, visibility settings, display preferences, and data refresh behavior."""
    path: UpdateDashboardRequestPath
    body: UpdateDashboardRequestBody | None = None

# Operation: delete_dashboard
class DeleteDashboardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dashboard to delete.")
class DeleteDashboardRequest(StrictModel):
    """Permanently delete a dashboard by its unique identifier. This action cannot be undone."""
    path: DeleteDashboardRequestPath

# Operation: list_environments
class ListEnvironmentsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., metadata, configuration details).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of environments to return per page; controls pagination size.")
    filter_color: str | None = Field(default=None, validation_alias="filter[color]", serialization_alias="filter[color]", description="Filter environments by color attribute; specify the exact color value to match.")
    sort: str | None = Field(default=None, description="Sort results by specified field(s) in ascending or descending order; use format like 'field' or 'field:desc'.")
class ListEnvironmentsRequest(StrictModel):
    """Retrieve a paginated list of environments with optional filtering and sorting capabilities."""
    query: ListEnvironmentsRequestQuery | None = None

# Operation: create_environment
class CreateEnvironmentRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the environment (e.g., 'Production', 'Staging', 'Development').")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional description providing additional context or details about the environment's purpose.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="An optional hex color code (e.g., '#FF5733') for visual identification of the environment in UI displays.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="An optional numeric position value that determines the display order of this environment relative to others.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="An optional list of email addresses that should receive notifications related to this environment. Each entry should be a valid email address.")
    slack_channels: list[CreateEnvironmentBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="An optional list of Slack channel identifiers or names to associate with this environment for automated notifications and alerts.")
    slack_aliases: list[CreateEnvironmentBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="An optional list of Slack user aliases or handles to associate with this environment for direct messaging and notifications.")
class CreateEnvironmentRequestBodyData(StrictModel):
    type_: Literal["environments"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'environments' to specify this is an environment resource.")
    attributes: CreateEnvironmentRequestBodyDataAttributes
class CreateEnvironmentRequestBody(StrictModel):
    data: CreateEnvironmentRequestBodyData
class CreateEnvironmentRequest(StrictModel):
    """Creates a new environment with optional notification and messaging integrations. The environment serves as a deployment or organizational context that can be associated with Slack channels, email notifications, and visual styling."""
    body: CreateEnvironmentRequestBody

# Operation: get_environment
class GetEnvironmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the environment to retrieve.")
class GetEnvironmentRequest(StrictModel):
    """Retrieves a specific environment by its unique identifier. Use this operation to fetch detailed information about a single environment."""
    path: GetEnvironmentRequestPath

# Operation: update_environment
class UpdateEnvironmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the environment to update.")
class UpdateEnvironmentRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the environment's purpose or usage.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hexadecimal color code (e.g., #FF5733) used to visually represent the environment in the UI.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of the environment in lists and dashboards, where lower numbers appear first.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="A list of email addresses that should receive notifications related to this environment.")
    slack_channels: list[UpdateEnvironmentBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="A list of Slack channel identifiers or names to integrate with this environment for notifications and updates.")
    slack_aliases: list[UpdateEnvironmentBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="A list of Slack user aliases or handles to associate with this environment for direct messaging and mentions.")
class UpdateEnvironmentRequestBodyData(StrictModel):
    type_: Literal["environments"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'environments' to identify this as an environment resource.")
    attributes: UpdateEnvironmentRequestBodyDataAttributes | None = None
class UpdateEnvironmentRequestBody(StrictModel):
    data: UpdateEnvironmentRequestBodyData
class UpdateEnvironmentRequest(StrictModel):
    """Update an existing environment's configuration, including its description, visual appearance, notification settings, and associated Slack integrations."""
    path: UpdateEnvironmentRequestPath
    body: UpdateEnvironmentRequestBody

# Operation: delete_environment
class DeleteEnvironmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the environment to delete.")
class DeleteEnvironmentRequest(StrictModel):
    """Permanently delete a specific environment by its unique identifier. This action cannot be undone."""
    path: DeleteEnvironmentRequestPath

# Operation: list_escalation_policies
class ListEscalationPoliciesRequestQuery(StrictModel):
    include: Literal["escalation_policy_levels", "escalation_policy_paths", "groups", "services"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Valid options are escalation_policy_levels (the escalation steps), escalation_policy_paths (the routing paths), groups (associated groups), or services (associated services).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through results when the total count exceeds the page size.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of escalation policies to return per page. Controls the size of each paginated result set.")
class ListEscalationPoliciesRequest(StrictModel):
    """Retrieve a paginated list of escalation policies. Optionally include related resources such as escalation levels, paths, groups, or services to enrich the response."""
    query: ListEscalationPoliciesRequestQuery | None = None

# Operation: create_escalation_policy
class CreateEscalationPolicyRequestBodyDataAttributesBusinessHours(StrictModel):
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="Optional time zone identifier (e.g., 'America/New_York') used to interpret business hours for scheduling escalations during specific times.")
    days: list[Literal["M", "T", "W", "R", "F", "U", "S"]] | None = Field(default=None, validation_alias="days", serialization_alias="days", description="Optional list of business days (e.g., ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']) when this escalation policy is active; used in conjunction with time_zone to restrict escalations to business hours.")
class CreateEscalationPolicyRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the escalation policy used for identification and display purposes.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional detailed description explaining the purpose and scope of this escalation policy.")
    repeat_count: int | None = Field(default=None, validation_alias="repeat_count", serialization_alias="repeat_count", description="The number of escalation cycles to execute before the policy stops escalating; determines how many times responders are notified before manual intervention is required.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="Optional list of group IDs whose alerts will trigger this escalation policy; when any associated group receives an alert, the escalation chain activates.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Optional list of service IDs whose alerts will trigger this escalation policy; when any associated service receives an alert, the escalation chain activates.")
    business_hours: CreateEscalationPolicyRequestBodyDataAttributesBusinessHours | None = None
class CreateEscalationPolicyRequestBodyData(StrictModel):
    type_: Literal["escalation_policies"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'escalation_policies' to indicate this is an escalation policy resource.")
    attributes: CreateEscalationPolicyRequestBodyDataAttributes
class CreateEscalationPolicyRequestBody(StrictModel):
    data: CreateEscalationPolicyRequestBodyData
class CreateEscalationPolicyRequest(StrictModel):
    """Creates a new escalation policy that automatically escalates alerts to additional responders after a specified number of cycles without acknowledgment. The policy can be triggered by alerts from associated groups or services."""
    body: CreateEscalationPolicyRequestBody

# Operation: get_escalation_policy
class GetEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to retrieve.")
class GetEscalationPolicyRequestQuery(StrictModel):
    include: Literal["escalation_policy_levels", "escalation_policy_paths", "groups", "services"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Valid options are escalation_policy_levels, escalation_policy_paths, groups, and services.")
class GetEscalationPolicyRequest(StrictModel):
    """Retrieves a specific escalation policy by its unique identifier. Optionally include related resources such as escalation levels, paths, groups, or services."""
    path: GetEscalationPolicyRequestPath
    query: GetEscalationPolicyRequestQuery | None = None

# Operation: update_escalation_policy
class UpdateEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to update.")
class UpdateEscalationPolicyRequestBodyDataAttributesBusinessHours(StrictModel):
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="The time zone identifier (e.g., 'America/New_York') used to interpret business hours and schedule-based escalation rules.")
    days: list[Literal["M", "T", "W", "R", "F", "U", "S"]] | None = Field(default=None, validation_alias="days", serialization_alias="days", description="List of business days (e.g., 'Monday', 'Tuesday') when this escalation policy is active; days not listed are treated as non-business hours.")
class UpdateEscalationPolicyRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the escalation policy's purpose and behavior.")
    repeat_count: int | None = Field(default=None, validation_alias="repeat_count", serialization_alias="repeat_count", description="The number of times the escalation policy will cycle through its escalation steps before stopping, allowing multiple retry attempts before requiring manual acknowledgment.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="List of group identifiers that will trigger this escalation policy when alerts are routed to them. Order is not significant.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="List of service identifiers that will trigger this escalation policy when alerts are generated for those services. Order is not significant.")
    business_hours: UpdateEscalationPolicyRequestBodyDataAttributesBusinessHours | None = None
class UpdateEscalationPolicyRequestBodyData(StrictModel):
    type_: Literal["escalation_policies"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'escalation_policies' to specify this is an escalation policy resource.")
    attributes: UpdateEscalationPolicyRequestBodyDataAttributes | None = None
class UpdateEscalationPolicyRequestBody(StrictModel):
    data: UpdateEscalationPolicyRequestBodyData
class UpdateEscalationPolicyRequest(StrictModel):
    """Update an existing escalation policy to modify its escalation behavior, associated resources, and scheduling rules. Changes apply to future alert escalations using this policy."""
    path: UpdateEscalationPolicyRequestPath
    body: UpdateEscalationPolicyRequestBody

# Operation: delete_escalation_policy
class DeleteEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to delete.")
class DeleteEscalationPolicyRequest(StrictModel):
    """Permanently delete an escalation policy by its unique identifier. This action cannot be undone and will remove the policy from the system."""
    path: DeleteEscalationPolicyRequestPath

# Operation: list_escalation_levels
class ListEscalationLevelsRequestPath(StrictModel):
    escalation_policy_id: str = Field(default=..., description="The unique identifier of the escalation policy whose levels you want to retrieve.")
class ListEscalationLevelsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., users, schedules). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for paginated results, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of escalation levels to return per page. Adjust to balance response size and number of requests needed.")
class ListEscalationLevelsRequest(StrictModel):
    """Retrieve all escalation levels configured for a specific escalation policy. Escalation levels define the sequence of on-call responders and timing for incident escalation."""
    path: ListEscalationLevelsRequestPath
    query: ListEscalationLevelsRequestQuery | None = None

# Operation: create_escalation_level
class CreateEscalationLevelRequestPath(StrictModel):
    escalation_policy_id: str = Field(default=..., description="The unique identifier of the escalation policy to which this escalation level will be added.")
class CreateEscalationLevelRequestBodyDataAttributes(StrictModel):
    delay: int | None = Field(default=None, validation_alias="delay", serialization_alias="delay", description="The number of minutes to wait before notifying targets at this escalation level. Allows time for lower-level escalations to resolve the alert.")
    position: int = Field(default=..., validation_alias="position", serialization_alias="position", description="The sequential position of this escalation level within the policy (e.g., 1 for first level, 2 for second). Determines the order in which escalation levels are triggered.")
    paging_strategy_configuration_strategy: Literal["default", "random", "cycle", "alert"] | None = Field(default=None, validation_alias="paging_strategy_configuration_strategy", serialization_alias="paging_strategy_configuration_strategy", description="The strategy for distributing notifications among targets at this level. Use 'default' for standard behavior, 'random' to select targets randomly, 'cycle' to rotate through targets, or 'alert' to notify all targets simultaneously.")
    paging_strategy_configuration_schedule_strategy: Literal["on_call_only", "everyone"] | None = Field(default=None, validation_alias="paging_strategy_configuration_schedule_strategy", serialization_alias="paging_strategy_configuration_schedule_strategy", description="Determines which users receive notifications at this level. Use 'on_call_only' to notify only currently on-call users, or 'everyone' to notify all assigned targets regardless of on-call status.")
    notification_target_params: list[CreateEscalationLevelBodyDataAttributesNotificationTargetParamsItem] = Field(default=..., validation_alias="notification_target_params", serialization_alias="notification_target_params", description="Array of notification targets (users, teams, or schedules) to be alerted at this escalation level. Order may be significant depending on the paging strategy selected.")
class CreateEscalationLevelRequestBodyData(StrictModel):
    type_: Literal["escalation_levels"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this escalation level. Must be set to 'escalation_levels'.")
    attributes: CreateEscalationLevelRequestBodyDataAttributes
class CreateEscalationLevelRequestBody(StrictModel):
    data: CreateEscalationLevelRequestBodyData
class CreateEscalationLevelRequest(StrictModel):
    """Creates a new escalation level within an escalation policy to define notification targets and timing for alert escalation. Each level specifies who gets notified and when, with configurable paging strategies."""
    path: CreateEscalationLevelRequestPath
    body: CreateEscalationLevelRequestBody

# Operation: list_escalation_levels_for_escalation_path
class ListEscalationLevelsPathsRequestPath(StrictModel):
    escalation_policy_path_id: str = Field(default=..., description="The unique identifier of the escalation path whose escalation levels you want to retrieve.")
class ListEscalationLevelsPathsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., users, teams, schedules). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of escalation levels to return per page. Adjust to balance response size and number of requests needed.")
class ListEscalationLevelsPathsRequest(StrictModel):
    """Retrieve all escalation levels defined within a specific escalation path. Escalation levels determine the sequence and conditions for notifying responders when an incident requires escalation."""
    path: ListEscalationLevelsPathsRequestPath
    query: ListEscalationLevelsPathsRequestQuery | None = None

# Operation: create_escalation_level_path
class CreateEscalationLevelPathsRequestPath(StrictModel):
    escalation_policy_path_id: str = Field(default=..., description="The unique identifier of the escalation path to which this escalation level will be added.")
class CreateEscalationLevelPathsRequestBodyDataAttributes(StrictModel):
    delay: int | None = Field(default=None, validation_alias="delay", serialization_alias="delay", description="The number of minutes to wait before notifying targets at this escalation level. Allows time for lower-level escalations to resolve the issue.")
    position: int = Field(default=..., validation_alias="position", serialization_alias="position", description="The sequential position of this escalation level within the path (e.g., 1 for first level, 2 for second). Determines the order in which escalation levels are triggered.")
    paging_strategy_configuration_strategy: Literal["default", "random", "cycle", "alert"] | None = Field(default=None, validation_alias="paging_strategy_configuration_strategy", serialization_alias="paging_strategy_configuration_strategy", description="The strategy for selecting which notification targets receive alerts: 'default' uses standard selection, 'random' picks targets randomly, 'cycle' rotates through targets, and 'alert' notifies all targets simultaneously.")
    paging_strategy_configuration_schedule_strategy: Literal["on_call_only", "everyone"] | None = Field(default=None, validation_alias="paging_strategy_configuration_schedule_strategy", serialization_alias="paging_strategy_configuration_schedule_strategy", description="Determines whether notifications are sent only to currently on-call personnel ('on_call_only') or to all configured targets ('everyone').")
    notification_target_params: list[CreateEscalationLevelPathsBodyDataAttributesNotificationTargetParamsItem] = Field(default=..., validation_alias="notification_target_params", serialization_alias="notification_target_params", description="An ordered list of notification targets to alert at this escalation level. Order may affect notification sequence depending on the paging strategy.")
class CreateEscalationLevelPathsRequestBodyData(StrictModel):
    type_: Literal["escalation_levels"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'escalation_levels'.")
    attributes: CreateEscalationLevelPathsRequestBodyDataAttributes
class CreateEscalationLevelPathsRequestBody(StrictModel):
    data: CreateEscalationLevelPathsRequestBodyData
class CreateEscalationLevelPathsRequest(StrictModel):
    """Creates a new escalation level within an escalation path, defining notification targets and timing for the next tier of alert recipients."""
    path: CreateEscalationLevelPathsRequestPath
    body: CreateEscalationLevelPathsRequestBody

# Operation: get_escalation_level
class GetEscalationLevelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation level to retrieve.")
class GetEscalationLevelRequest(StrictModel):
    """Retrieves a specific escalation level by its unique identifier. Use this to fetch details about a particular escalation level configuration."""
    path: GetEscalationLevelRequestPath

# Operation: update_escalation_level
class UpdateEscalationLevelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation level to update.")
class UpdateEscalationLevelRequestBodyDataAttributes(StrictModel):
    delay: int | None = Field(default=None, validation_alias="delay", serialization_alias="delay", description="The number of minutes to wait before notifying targets at this escalation level. Allows time for lower-level escalations to resolve issues before escalating further.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The sequential position of this escalation level within the escalation policy. Lower numbers represent earlier escalation stages.")
    paging_strategy_configuration_strategy: Literal["default", "random", "cycle", "alert"] | None = Field(default=None, validation_alias="paging_strategy_configuration_strategy", serialization_alias="paging_strategy_configuration_strategy", description="The strategy for selecting which notification targets receive alerts: 'default' uses standard ordering, 'random' selects targets randomly, 'cycle' rotates through targets, and 'alert' notifies all targets simultaneously.")
    paging_strategy_configuration_schedule_strategy: Literal["on_call_only", "everyone"] | None = Field(default=None, validation_alias="paging_strategy_configuration_schedule_strategy", serialization_alias="paging_strategy_configuration_schedule_strategy", description="Determines whether notifications are sent only to currently on-call personnel ('on_call_only') or to all configured targets ('everyone').")
    notification_target_params: list[UpdateEscalationLevelBodyDataAttributesNotificationTargetParamsItem] | None = Field(default=None, validation_alias="notification_target_params", serialization_alias="notification_target_params", description="Array of notification target configurations for this escalation level. Each target specifies who should be alerted and how. Order may affect notification sequence depending on the paging strategy.")
class UpdateEscalationLevelRequestBodyData(StrictModel):
    type_: Literal["escalation_levels"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'escalation_levels' to specify this is an escalation level resource.")
    attributes: UpdateEscalationLevelRequestBodyDataAttributes | None = None
class UpdateEscalationLevelRequestBody(StrictModel):
    data: UpdateEscalationLevelRequestBodyData
class UpdateEscalationLevelRequest(StrictModel):
    """Update an existing escalation level within an escalation policy. Modify notification timing, position in the escalation sequence, and paging strategy to control how and when alerts are routed to notification targets."""
    path: UpdateEscalationLevelRequestPath
    body: UpdateEscalationLevelRequestBody

# Operation: delete_escalation_level
class DeleteEscalationLevelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation level to delete.")
class DeleteEscalationLevelRequest(StrictModel):
    """Permanently delete an escalation level by its unique identifier. This action cannot be undone."""
    path: DeleteEscalationLevelRequestPath

# Operation: list_escalation_paths
class ListEscalationPathsRequestPath(StrictModel):
    escalation_policy_id: str = Field(default=..., description="The unique identifier of the escalation policy containing the escalation paths to retrieve.")
class ListEscalationPathsRequestQuery(StrictModel):
    include: Literal["escalation_policy_levels"] | None = Field(default=None, description="Optional comma-separated list of related resources to include in the response. Specify 'escalation_policy_levels' to include the policy levels associated with each escalation path.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, used to retrieve a specific set of results when the total number of escalation paths exceeds the page size.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The maximum number of escalation paths to return per page for pagination purposes.")
class ListEscalationPathsRequest(StrictModel):
    """Retrieve all escalation paths defined within a specific escalation policy. Optionally include related escalation policy level details."""
    path: ListEscalationPathsRequestPath
    query: ListEscalationPathsRequestQuery | None = None

# Operation: get_escalation_path
class GetEscalationPathRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation path to retrieve.")
class GetEscalationPathRequestQuery(StrictModel):
    include: Literal["escalation_policy_levels"] | None = Field(default=None, description="Optional comma-separated list of related resources to include in the response. Supports including escalation_policy_levels to fetch the policy levels associated with this escalation path.")
class GetEscalationPathRequest(StrictModel):
    """Retrieves a specific escalation path by its unique identifier. Optionally include related escalation policy levels in the response."""
    path: GetEscalationPathRequestPath
    query: GetEscalationPathRequestQuery | None = None

# Operation: update_escalation_path
class UpdateEscalationPathRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation path to update.")
class UpdateEscalationPathRequestBodyDataAttributes(StrictModel):
    notification_type: Literal["audible", "quiet"] | None = Field(default=None, validation_alias="notification_type", serialization_alias="notification_type", description="Notification style for this escalation level. Choose 'audible' for sound alerts or 'quiet' for silent notifications. Defaults to 'audible'.")
    default: bool | None = Field(default=None, validation_alias="default", serialization_alias="default", description="Whether this escalation path should be used as the default when no other paths match.")
    match_mode: Literal["match-all-rules", "match-any-rule"] | None = Field(default=None, validation_alias="match_mode", serialization_alias="match_mode", description="Rule matching strategy: 'match-all-rules' requires all conditions to be met, while 'match-any-rule' triggers if any condition matches. Defaults to 'match-all-rules'.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this path within the escalation policy's path sequence.")
    repeat: bool | None = Field(default=None, validation_alias="repeat", serialization_alias="repeat", description="Whether this path should continue repeating until someone acknowledges the alert.")
    repeat_count: int | None = Field(default=None, validation_alias="repeat_count", serialization_alias="repeat_count", description="The maximum number of times this path will execute before stopping, even if unacknowledged.")
    initial_delay: int | None = Field(default=None, validation_alias="initial_delay", serialization_alias="initial_delay", description="Initial delay before escalation begins, specified in minutes. Maximum allowed is 10080 minutes (one week).")
    rules: list[UpdateEscalationPathBodyDataAttributesRulesItemV0 | UpdateEscalationPathBodyDataAttributesRulesItemV1 | UpdateEscalationPathBodyDataAttributesRulesItemV2] | None = Field(default=None, validation_alias="rules", serialization_alias="rules", description="Array of escalation path conditions that determine when this path is triggered. Order and structure depend on the match_mode setting.")
    time_restriction_time_zone: Literal["International Date Line West", "Etc/GMT+12", "American Samoa", "Pacific/Pago_Pago", "Midway Island", "Pacific/Midway", "Hawaii", "Pacific/Honolulu", "Alaska", "America/Juneau", "Pacific Time (US & Canada)", "America/Los_Angeles", "Tijuana", "America/Tijuana", "Arizona", "America/Phoenix", "Mazatlan", "America/Mazatlan", "Mountain Time (US & Canada)", "America/Denver", "Central America", "America/Guatemala", "Central Time (US & Canada)", "America/Chicago", "Chihuahua", "America/Chihuahua", "Guadalajara", "America/Mexico_City", "Mexico City", "Monterrey", "America/Monterrey", "Saskatchewan", "America/Regina", "Bogota", "America/Bogota", "Eastern Time (US & Canada)", "America/New_York", "Indiana (East)", "America/Indiana/Indianapolis", "Lima", "America/Lima", "Quito", "Atlantic Time (Canada)", "America/Halifax", "Caracas", "America/Caracas", "Georgetown", "America/Guyana", "La Paz", "America/La_Paz", "Puerto Rico", "America/Puerto_Rico", "Santiago", "America/Santiago", "Newfoundland", "America/St_Johns", "Brasilia", "America/Sao_Paulo", "Buenos Aires", "America/Argentina/Buenos_Aires", "Montevideo", "America/Montevideo", "Greenland", "America/Godthab", "Mid-Atlantic", "Atlantic/South_Georgia", "Azores", "Atlantic/Azores", "Cape Verde Is.", "Atlantic/Cape_Verde", "Edinburgh", "Europe/London", "Lisbon", "Europe/Lisbon", "London", "Monrovia", "Africa/Monrovia", "UTC", "Etc/UTC", "Amsterdam", "Europe/Amsterdam", "Belgrade", "Europe/Belgrade", "Berlin", "Europe/Berlin", "Bern", "Europe/Zurich", "Bratislava", "Europe/Bratislava", "Brussels", "Europe/Brussels", "Budapest", "Europe/Budapest", "Casablanca", "Africa/Casablanca", "Copenhagen", "Europe/Copenhagen", "Dublin", "Europe/Dublin", "Ljubljana", "Europe/Ljubljana", "Madrid", "Europe/Madrid", "Paris", "Europe/Paris", "Prague", "Europe/Prague", "Rome", "Europe/Rome", "Sarajevo", "Europe/Sarajevo", "Skopje", "Europe/Skopje", "Stockholm", "Europe/Stockholm", "Vienna", "Europe/Vienna", "Warsaw", "Europe/Warsaw", "West Central Africa", "Africa/Algiers", "Zagreb", "Europe/Zagreb", "Zurich", "Athens", "Europe/Athens", "Bucharest", "Europe/Bucharest", "Cairo", "Africa/Cairo", "Harare", "Africa/Harare", "Helsinki", "Europe/Helsinki", "Jerusalem", "Asia/Jerusalem", "Kaliningrad", "Europe/Kaliningrad", "Kyiv", "Europe/Kiev", "Pretoria", "Africa/Johannesburg", "Riga", "Europe/Riga", "Sofia", "Europe/Sofia", "Tallinn", "Europe/Tallinn", "Vilnius", "Europe/Vilnius", "Baghdad", "Asia/Baghdad", "Istanbul", "Europe/Istanbul", "Kuwait", "Asia/Kuwait", "Minsk", "Europe/Minsk", "Moscow", "Europe/Moscow", "Nairobi", "Africa/Nairobi", "Riyadh", "Asia/Riyadh", "St. Petersburg", "Volgograd", "Europe/Volgograd", "Tehran", "Asia/Tehran", "Abu Dhabi", "Asia/Muscat", "Baku", "Asia/Baku", "Muscat", "Samara", "Europe/Samara", "Tbilisi", "Asia/Tbilisi", "Yerevan", "Asia/Yerevan", "Kabul", "Asia/Kabul", "Almaty", "Asia/Almaty", "Astana", "Ekaterinburg", "Asia/Yekaterinburg", "Islamabad", "Asia/Karachi", "Karachi", "Tashkent", "Asia/Tashkent", "Chennai", "Asia/Kolkata", "Kolkata", "Mumbai", "New Delhi", "Sri Jayawardenepura", "Asia/Colombo", "Kathmandu", "Asia/Kathmandu", "Dhaka", "Asia/Dhaka", "Urumqi", "Asia/Urumqi", "Rangoon", "Asia/Rangoon", "Bangkok", "Asia/Bangkok", "Hanoi", "Jakarta", "Asia/Jakarta", "Krasnoyarsk", "Asia/Krasnoyarsk", "Novosibirsk", "Asia/Novosibirsk", "Beijing", "Asia/Shanghai", "Chongqing", "Asia/Chongqing", "Hong Kong", "Asia/Hong_Kong", "Irkutsk", "Asia/Irkutsk", "Kuala Lumpur", "Asia/Kuala_Lumpur", "Perth", "Australia/Perth", "Singapore", "Asia/Singapore", "Taipei", "Asia/Taipei", "Ulaanbaatar", "Asia/Ulaanbaatar", "Osaka", "Asia/Tokyo", "Sapporo", "Seoul", "Asia/Seoul", "Tokyo", "Yakutsk", "Asia/Yakutsk", "Adelaide", "Australia/Adelaide", "Darwin", "Australia/Darwin", "Brisbane", "Australia/Brisbane", "Canberra", "Australia/Canberra", "Guam", "Pacific/Guam", "Hobart", "Australia/Hobart", "Melbourne", "Australia/Melbourne", "Port Moresby", "Pacific/Port_Moresby", "Sydney", "Australia/Sydney", "Vladivostok", "Asia/Vladivostok", "Magadan", "Asia/Magadan", "New Caledonia", "Pacific/Noumea", "Solomon Is.", "Pacific/Guadalcanal", "Srednekolymsk", "Asia/Srednekolymsk", "Auckland", "Pacific/Auckland", "Fiji", "Pacific/Fiji", "Kamchatka", "Asia/Kamchatka", "Marshall Is.", "Pacific/Majuro", "Wellington", "Chatham Is.", "Pacific/Chatham", "Nuku'alofa", "Pacific/Tongatapu", "Samoa", "Pacific/Apia", "Tokelau Is.", "Pacific/Fakaofo"] | None = Field(default=None, validation_alias="time_restriction_time_zone", serialization_alias="time_restriction_time_zone", description="Time zone for evaluating time-based restrictions. Accepts standard IANA time zone identifiers (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo').")
    time_restrictions: list[UpdateEscalationPathBodyDataAttributesTimeRestrictionsItem] | None = Field(default=None, validation_alias="time_restrictions", serialization_alias="time_restrictions", description="Array of time windows during which this escalation path is active. Alerts arriving outside these windows will not follow this path.")
class UpdateEscalationPathRequestBodyData(StrictModel):
    type_: Literal["escalation_paths"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'escalation_paths'.")
    attributes: UpdateEscalationPathRequestBodyDataAttributes | None = None
class UpdateEscalationPathRequestBody(StrictModel):
    data: UpdateEscalationPathRequestBodyData
class UpdateEscalationPathRequest(StrictModel):
    """Update an escalation path configuration by ID, including notification settings, matching rules, repetition behavior, delays, and time-based restrictions."""
    path: UpdateEscalationPathRequestPath
    body: UpdateEscalationPathRequestBody

# Operation: delete_escalation_path
class DeleteEscalationPathRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation path to delete.")
class DeleteEscalationPathRequest(StrictModel):
    """Permanently delete a specific escalation path by its unique identifier. This action cannot be undone."""
    path: DeleteEscalationPathRequestPath

# Operation: list_form_field_options
class ListFormFieldOptionsRequestPath(StrictModel):
    form_field_id: str = Field(default=..., description="The unique identifier of the form field whose options you want to list.")
class ListFormFieldOptionsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., metadata, dependencies). Specify which associations should be populated.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to control which subset of results is returned.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of options to return per page. Controls the maximum number of results in a single response.")
    filter_value: str | None = Field(default=None, validation_alias="filter[value]", serialization_alias="filter[value]", description="Filter options by their display value or label. Supports partial matching to find options containing the specified text.")
    filter_color: str | None = Field(default=None, validation_alias="filter[color]", serialization_alias="filter[color]", description="Filter options by their associated color value. Useful for filtering visually-coded options.")
class ListFormFieldOptionsRequest(StrictModel):
    """Retrieve a paginated list of options available for a specific form field. Use filtering and pagination parameters to narrow results and control response size."""
    path: ListFormFieldOptionsRequestPath
    query: ListFormFieldOptionsRequestQuery | None = None

# Operation: add_form_field_option
class CreateFormFieldOptionRequestPath(StrictModel):
    form_field_id: str = Field(default=..., description="The unique identifier of the form field to which this option will be added.")
class CreateFormFieldOptionRequestBodyDataAttributes(StrictModel):
    form_field_id: str = Field(default=..., validation_alias="form_field_id", serialization_alias="form_field_id", description="The unique identifier of the form field that this option belongs to; must match the form_field_id in the path.")
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The display value or label for this form field option that users will see when selecting from the field.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Optional hex color code to visually distinguish this option in the form interface.")
    default: bool | None = Field(default=None, validation_alias="default", serialization_alias="default", description="Optional flag to designate this option as the default selection for the form field.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="Optional numeric position to control the display order of this option relative to other options in the form field.")
class CreateFormFieldOptionRequestBodyData(StrictModel):
    type_: Literal["form_field_options"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'form_field_options'.")
    attributes: CreateFormFieldOptionRequestBodyDataAttributes
class CreateFormFieldOptionRequestBody(StrictModel):
    data: CreateFormFieldOptionRequestBodyData
class CreateFormFieldOptionRequest(StrictModel):
    """Creates a new option for a form field, allowing you to define selectable values with optional styling and positioning."""
    path: CreateFormFieldOptionRequestPath
    body: CreateFormFieldOptionRequestBody

# Operation: get_form_field_option
class GetFormFieldOptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field option to retrieve.")
class GetFormFieldOptionRequest(StrictModel):
    """Retrieves a specific form field option by its unique identifier. Use this to fetch details about a single option available for a form field."""
    path: GetFormFieldOptionRequestPath

# Operation: update_form_field_option
class UpdateFormFieldOptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field option to update.")
class UpdateFormFieldOptionRequestBodyDataAttributes(StrictModel):
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The display value or label for this form field option.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The hex color code for visual representation of this form field option.")
    default: bool | None = Field(default=None, validation_alias="default", serialization_alias="default", description="Whether this option should be selected by default when the form field is displayed.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this option within the form field's list of options, used to control display order.")
class UpdateFormFieldOptionRequestBodyData(StrictModel):
    type_: Literal["form_field_options"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'form_field_options' to specify the resource being updated.")
    attributes: UpdateFormFieldOptionRequestBodyDataAttributes | None = None
class UpdateFormFieldOptionRequestBody(StrictModel):
    data: UpdateFormFieldOptionRequestBodyData
class UpdateFormFieldOptionRequest(StrictModel):
    """Update a specific form field option by its ID, allowing modification of its display value, color, default status, and position within the form field."""
    path: UpdateFormFieldOptionRequestPath
    body: UpdateFormFieldOptionRequestBody

# Operation: delete_form_field_option
class DeleteFormFieldOptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field option to delete.")
class DeleteFormFieldOptionRequest(StrictModel):
    """Delete a specific form field option by its unique identifier. This operation permanently removes the option from the form field."""
    path: DeleteFormFieldOptionRequestPath

# Operation: list_form_field_placement_conditions
class ListFormFieldPlacementConditionsRequestPath(StrictModel):
    form_field_placement_id: str = Field(default=..., description="The unique identifier of the form field placement whose conditions you want to retrieve.")
class ListFormFieldPlacementConditionsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response for expanded context (e.g., condition details, field metadata).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of conditions to return per page. Adjust this to control the size of each paginated response.")
class ListFormFieldPlacementConditionsRequest(StrictModel):
    """Retrieve a paginated list of conditions associated with a specific form field placement. Conditions define the rules that determine when a form field should be displayed or hidden."""
    path: ListFormFieldPlacementConditionsRequestPath
    query: ListFormFieldPlacementConditionsRequestQuery | None = None

# Operation: delete_form_field_placement_condition
class DeleteFormFieldPlacementConditionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field placement condition to delete.")
class DeleteFormFieldPlacementConditionRequest(StrictModel):
    """Delete a specific form field placement condition by its unique identifier. This removes the condition rule that controls when a form field should be displayed or hidden."""
    path: DeleteFormFieldPlacementConditionRequestPath

# Operation: list_form_field_placements
class ListFormFieldPlacementsRequestPath(StrictModel):
    form_field_id: str = Field(default=..., description="The unique identifier of the form field for which to list placements.")
class ListFormFieldPlacementsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., form, placement_context).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results to return per page.")
class ListFormFieldPlacementsRequest(StrictModel):
    """Retrieve all placements for a specific form field, with support for pagination and optional relationship inclusion."""
    path: ListFormFieldPlacementsRequestPath
    query: ListFormFieldPlacementsRequestQuery | None = None

# Operation: create_form_field_placement
class CreateFormFieldPlacementRequestPath(StrictModel):
    form_field_id: str = Field(default=..., description="The unique identifier of the form field being placed.")
class CreateFormFieldPlacementRequestBodyDataAttributes(StrictModel):
    form_set_id: str = Field(default=..., validation_alias="form_set_id", serialization_alias="form_set_id", description="The unique identifier of the form set that contains this field placement.")
    form: str = Field(default=..., validation_alias="form", serialization_alias="form", description="The unique identifier of the form where this field will be placed.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this field on the form; lower values appear first. If not specified, the field is appended to the end.")
    required: bool | None = Field(default=None, validation_alias="required", serialization_alias="required", description="Whether this field must always be completed on the form, regardless of any conditional logic.")
    required_operator: Literal["and", "or"] | None = Field(default=None, validation_alias="required_operator", serialization_alias="required_operator", description="The logical operator (AND or OR) used when evaluating multiple conditions that determine if this field is required. Use AND when all conditions must be met, or OR when any condition can trigger the requirement.")
    placement_operator: Literal["and", "or"] | None = Field(default=None, validation_alias="placement_operator", serialization_alias="placement_operator", description="The logical operator (AND or OR) used when evaluating multiple conditions that determine if this field should be displayed. Use AND when all conditions must be met, or OR when any condition can trigger visibility.")
class CreateFormFieldPlacementRequestBodyData(StrictModel):
    type_: Literal["form_field_placements"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'form_field_placements' to indicate this is a form field placement resource.")
    attributes: CreateFormFieldPlacementRequestBodyDataAttributes
class CreateFormFieldPlacementRequestBody(StrictModel):
    data: CreateFormFieldPlacementRequestBodyData
class CreateFormFieldPlacementRequest(StrictModel):
    """Creates a new placement of a form field within a specific form and form set. This establishes where and how a field appears on a form, including its position, requirement status, and conditional logic rules."""
    path: CreateFormFieldPlacementRequestPath
    body: CreateFormFieldPlacementRequestBody

# Operation: list_form_field_positions
class ListFormFieldPositionsRequestPath(StrictModel):
    form_field_id: str = Field(default=..., description="The unique identifier of the form field for which to retrieve positions.")
class ListFormFieldPositionsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., form details, metadata).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of positions to return per page. Defines the maximum number of results in each paginated response.")
    filter_form: str | None = Field(default=None, validation_alias="filter[form]", serialization_alias="filter[form]", description="Filter positions by the form they belong to, specified by form identifier.")
class ListFormFieldPositionsRequest(StrictModel):
    """Retrieve all positions associated with a specific form field. Positions represent locations or instances where the form field appears within forms."""
    path: ListFormFieldPositionsRequestPath
    query: ListFormFieldPositionsRequestQuery | None = None

# Operation: create_form_field_position
class CreateFormFieldPositionRequestPath(StrictModel):
    form_field_id: str = Field(default=..., description="The unique identifier of the form field to position.")
class CreateFormFieldPositionRequestBodyDataAttributes(StrictModel):
    form_field_id: str = Field(default=..., validation_alias="form_field_id", serialization_alias="form_field_id", description="The unique identifier of the form field being positioned. Must match the form_field_id in the path parameter.")
    form: Literal["web_new_incident_form", "web_update_incident_form", "web_incident_post_mortem_form", "web_incident_mitigation_form", "web_incident_resolution_form", "web_incident_cancellation_form", "web_scheduled_incident_form", "web_update_scheduled_incident_form", "incident_post_mortem", "slack_new_incident_form", "slack_update_incident_form", "slack_update_incident_status_form", "slack_incident_mitigation_form", "slack_incident_resolution_form", "slack_incident_cancellation_form", "slack_scheduled_incident_form", "slack_update_scheduled_incident_form"] = Field(default=..., validation_alias="form", serialization_alias="form", description="The target form where this field will be positioned. Choose from web-based forms (new incident, update incident, post-mortem, mitigation, resolution, cancellation, or scheduled incident) or Slack-based forms (with equivalent operations).")
    position: int = Field(default=..., validation_alias="position", serialization_alias="position", description="The numeric position (order) where this field should appear within the selected form. Lower numbers appear first.")
class CreateFormFieldPositionRequestBodyData(StrictModel):
    type_: Literal["form_field_positions"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'form_field_positions'.")
    attributes: CreateFormFieldPositionRequestBodyDataAttributes
class CreateFormFieldPositionRequestBody(StrictModel):
    data: CreateFormFieldPositionRequestBodyData
class CreateFormFieldPositionRequest(StrictModel):
    """Creates a new position assignment for a form field, determining where the field appears within a specific incident management form (web or Slack-based)."""
    path: CreateFormFieldPositionRequestPath
    body: CreateFormFieldPositionRequestBody

# Operation: get_form_field_position
class GetFormFieldPositionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field position to retrieve.")
class GetFormFieldPositionRequest(StrictModel):
    """Retrieves the position and layout details of a specific form field by its unique identifier."""
    path: GetFormFieldPositionRequestPath

# Operation: list_form_fields
class ListFormFieldsRequestQuery(StrictModel):
    include: Literal["options", "positions"] | None = Field(default=None, description="Comma-separated list of related data to include in the response. Valid options are 'options' (field choices/values) and 'positions' (field ordering/layout information).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to retrieve specific result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of form fields to return per page. Use with page[number] to control pagination.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter results by the type or category of form field (e.g., text, checkbox, dropdown).")
    filter_enabled: bool | None = Field(default=None, validation_alias="filter[enabled]", serialization_alias="filter[enabled]", description="Filter results to show only enabled form fields (true) or disabled form fields (false).")
class ListFormFieldsRequest(StrictModel):
    """Retrieve a paginated list of form fields with optional filtering by kind and enabled status. Optionally include related data such as field options or position information."""
    query: ListFormFieldsRequestQuery | None = None

# Operation: create_form_field
class CreateFormFieldRequestBodyDataAttributes(StrictModel):
    kind: Literal["custom", "title", "summary", "mitigation_message", "resolution_message", "severity", "environments", "types", "services", "causes", "functionalities", "teams", "visibility", "mark_as_test", "mark_as_backfilled", "labels", "notify_emails", "trigger_manual_workflows", "show_ongoing_incidents", "attach_alerts", "mark_as_in_triage", "in_triage_at", "started_at", "detected_at", "acknowledged_at", "mitigated_at", "resolved_at", "closed_at", "manual_starting_datetime_field"] = Field(default=..., validation_alias="kind", serialization_alias="kind", description="The category of form field being created. Choose from predefined types like 'custom' for user-defined fields, 'title' and 'summary' for incident metadata, message fields for communication, standard incident attributes (severity, environments, types, services, causes, functionalities, teams, visibility), workflow controls (mark_as_test, mark_as_backfilled, trigger_manual_workflows), triage management (mark_as_in_triage, in_triage_at), or timestamp fields (started_at, detected_at, acknowledged_at, mitigated_at, resolved_at, closed_at, manual_starting_datetime_field).")
    input_kind: Literal["text", "textarea", "select", "multi_select", "date", "datetime", "number", "checkbox", "tags", "rich_text"] | None = Field(default=None, validation_alias="input_kind", serialization_alias="input_kind", description="The UI input control type for this field. Determines how users interact with the field: 'text' for single-line input, 'textarea' for multi-line text, 'select' for dropdown selection, 'multi_select' for multiple choices, 'date' or 'datetime' for temporal values, 'number' for numeric input, 'checkbox' for boolean toggles, 'tags' for comma-separated values, or 'rich_text' for formatted content.")
    value_kind: Literal["inherit", "group", "service", "functionality", "user", "catalog_entity"] | None = Field(default=None, validation_alias="value_kind", serialization_alias="value_kind", description="The semantic type of values this field accepts. Use 'inherit' to derive from context, 'group' for team/group references, 'service' for service catalog items, 'functionality' for functionality references, 'user' for user assignments, or 'catalog_entity' for custom catalog items (requires value_kind_catalog_id).")
    value_kind_catalog_id: str | None = Field(default=None, validation_alias="value_kind_catalog_id", serialization_alias="value_kind_catalog_id", description="The catalog identifier to use when value_kind is set to 'catalog_entity'. Specifies which custom catalog this field's values are sourced from.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the form field. Used in UI labels and incident details.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional explanatory text describing the purpose and usage of this form field.")
    shown: list[str] | None = Field(default=None, validation_alias="shown", serialization_alias="shown", description="Conditions determining when this field is visible in the incident form. Specify as an array of condition objects.")
    required: list[str] | None = Field(default=None, validation_alias="required", serialization_alias="required", description="Conditions determining when this field is required for incident creation or updates. Specify as an array of condition objects.")
    show_on_incident_details: bool | None = Field(default=None, validation_alias="show_on_incident_details", serialization_alias="show_on_incident_details", description="Whether this form field appears in the incident details panel when viewing incident information.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether this form field is active and available for use in incident workflows.")
    default_values: list[str] | None = Field(default=None, validation_alias="default_values", serialization_alias="default_values", description="Pre-populated values for this field when creating new incidents. Specify as an array of values matching the field's value_kind type.")
class CreateFormFieldRequestBodyData(StrictModel):
    type_: Literal["form_fields"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'form_fields' to indicate this is a form field resource.")
    attributes: CreateFormFieldRequestBodyDataAttributes
class CreateFormFieldRequestBody(StrictModel):
    data: CreateFormFieldRequestBodyData
class CreateFormFieldRequest(StrictModel):
    """Creates a new form field for incident management workflows. Form fields define custom data collection, display, and validation rules for incidents."""
    body: CreateFormFieldRequestBody

# Operation: get_form_field
class GetFormFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field to retrieve.")
class GetFormFieldRequestQuery(StrictModel):
    include: Literal["options", "positions"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Supported values are 'options' (field choices/values) and 'positions' (field layout positioning).")
class GetFormFieldRequest(StrictModel):
    """Retrieves a specific form field by its unique identifier, with optional related data expansion."""
    path: GetFormFieldRequestPath
    query: GetFormFieldRequestQuery | None = None

# Operation: update_form_field
class UpdateFormFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field to update.")
class UpdateFormFieldRequestBodyDataAttributes(StrictModel):
    kind: Literal["custom", "title", "summary", "mitigation_message", "resolution_message", "severity", "environments", "types", "services", "causes", "functionalities", "teams", "visibility", "mark_as_test", "mark_as_backfilled", "labels", "notify_emails", "trigger_manual_workflows", "show_ongoing_incidents", "attach_alerts", "mark_as_in_triage", "in_triage_at", "started_at", "detected_at", "acknowledged_at", "mitigated_at", "resolved_at", "closed_at", "manual_starting_datetime_field"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="The category of form field, such as custom fields or predefined incident attributes like severity, environments, teams, timestamps (started_at, resolved_at, etc.), or workflow controls (mark_as_test, trigger_manual_workflows).")
    input_kind: Literal["text", "textarea", "select", "multi_select", "date", "datetime", "number", "checkbox", "tags", "rich_text"] | None = Field(default=None, validation_alias="input_kind", serialization_alias="input_kind", description="The UI input component type for this field, ranging from simple text inputs to complex multi-select dropdowns, date pickers, rich text editors, and checkboxes.")
    value_kind: Literal["inherit", "group", "service", "functionality", "user", "catalog_entity"] | None = Field(default=None, validation_alias="value_kind", serialization_alias="value_kind", description="The data source type for field values, allowing values to be inherited from parent contexts, grouped by organizational units, services, functionalities, users, or custom catalog entities.")
    value_kind_catalog_id: str | None = Field(default=None, validation_alias="value_kind_catalog_id", serialization_alias="value_kind_catalog_id", description="The catalog identifier to reference when value_kind is set to 'catalog_entity', enabling integration with external catalog systems.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable explanation of the form field's purpose and usage.")
    shown: list[str] | None = Field(default=None, validation_alias="shown", serialization_alias="shown", description="An array defining the conditions or contexts in which this form field should be displayed to users.")
    required: list[str] | None = Field(default=None, validation_alias="required", serialization_alias="required", description="An array specifying the conditions under which this form field becomes mandatory for users to complete.")
    show_on_incident_details: bool | None = Field(default=None, validation_alias="show_on_incident_details", serialization_alias="show_on_incident_details", description="Whether this form field should be visible in the incident details panel when viewing incident information.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether this form field is active and available for use in forms.")
    default_values: list[str] | None = Field(default=None, validation_alias="default_values", serialization_alias="default_values", description="An array of default values to pre-populate this form field when no user input is provided.")
class UpdateFormFieldRequestBodyData(StrictModel):
    type_: Literal["form_fields"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'form_fields' to identify this as a form field resource.")
    attributes: UpdateFormFieldRequestBodyDataAttributes | None = None
class UpdateFormFieldRequestBody(StrictModel):
    data: UpdateFormFieldRequestBodyData
class UpdateFormFieldRequest(StrictModel):
    """Update a specific form field configuration by ID, allowing modification of its type, input behavior, display settings, and validation rules."""
    path: UpdateFormFieldRequestPath
    body: UpdateFormFieldRequestBody

# Operation: delete_form_field
class DeleteFormFieldRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field to delete.")
class DeleteFormFieldRequest(StrictModel):
    """Permanently delete a form field by its unique identifier. This action cannot be undone."""
    path: DeleteFormFieldRequestPath

# Operation: list_form_set_conditions
class ListFormSetConditionsRequestPath(StrictModel):
    form_set_id: str = Field(default=..., description="The unique identifier of the form set for which to retrieve conditions.")
class ListFormSetConditionsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response for expanded context.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of conditions to return per page. Determines the batch size for paginated results.")
class ListFormSetConditionsRequest(StrictModel):
    """Retrieve all conditions associated with a specific form set. Conditions define the rules and logic that control form behavior and visibility."""
    path: ListFormSetConditionsRequestPath
    query: ListFormSetConditionsRequestQuery | None = None

# Operation: create_form_set_condition
class CreateFormSetConditionRequestPath(StrictModel):
    form_set_id: str = Field(default=..., description="The unique identifier of the form set to which this condition will be applied.")
class CreateFormSetConditionRequestBodyDataAttributes(StrictModel):
    form_field_id: str = Field(default=..., validation_alias="form_field_id", serialization_alias="form_field_id", description="The unique identifier of the form field that this condition evaluates.")
    comparison: Literal["equal"] = Field(default=..., validation_alias="comparison", serialization_alias="comparison", description="The comparison operator to use when evaluating the condition; currently supports equality checks.")
    values: list[str] = Field(default=..., validation_alias="values", serialization_alias="values", description="An array of values to compare against the form field's value. The condition evaluates to true when the field matches one of these values.")
class CreateFormSetConditionRequestBodyData(StrictModel):
    type_: Literal["form_set_conditions"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'form_set_conditions' to specify this is a form set condition resource.")
    attributes: CreateFormSetConditionRequestBodyDataAttributes
class CreateFormSetConditionRequestBody(StrictModel):
    data: CreateFormSetConditionRequestBodyData
class CreateFormSetConditionRequest(StrictModel):
    """Creates a new conditional rule for a form set that determines when specific form fields should be displayed or processed based on field value comparisons."""
    path: CreateFormSetConditionRequestPath
    body: CreateFormSetConditionRequestBody

# Operation: get_form_set_condition
class GetFormSetConditionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form set condition to retrieve.")
class GetFormSetConditionRequest(StrictModel):
    """Retrieves a specific form set condition by its unique identifier. Use this to fetch the configuration and rules associated with a particular form set condition."""
    path: GetFormSetConditionRequestPath

# Operation: update_form_set_condition
class UpdateFormSetConditionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form set condition to update.")
class UpdateFormSetConditionRequestBodyDataAttributes(StrictModel):
    form_field_id: str | None = Field(default=None, validation_alias="form_field_id", serialization_alias="form_field_id", description="The ID of the form field that this condition evaluates or monitors for triggering the conditional logic.")
    comparison: Literal["equal"] | None = Field(default=None, validation_alias="comparison", serialization_alias="comparison", description="The type of comparison to perform between the form field value and the specified values. Currently supports equality comparison.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="An array of values to compare against the form field's value using the specified comparison operator. The condition is satisfied when the field value matches one of these values.")
class UpdateFormSetConditionRequestBodyData(StrictModel):
    type_: Literal["form_set_conditions"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'form_set_conditions' to specify this is a form set condition resource.")
    attributes: UpdateFormSetConditionRequestBodyDataAttributes | None = None
class UpdateFormSetConditionRequestBody(StrictModel):
    data: UpdateFormSetConditionRequestBodyData
class UpdateFormSetConditionRequest(StrictModel):
    """Update an existing form set condition that controls field visibility or behavior based on specified comparison criteria. This allows modification of which form fields are displayed or enabled based on the values of other fields."""
    path: UpdateFormSetConditionRequestPath
    body: UpdateFormSetConditionRequestBody

# Operation: delete_form_set_condition
class DeleteFormSetConditionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form set condition to delete.")
class DeleteFormSetConditionRequest(StrictModel):
    """Delete a specific form set condition by its unique identifier. This operation permanently removes the condition and cannot be undone."""
    path: DeleteFormSetConditionRequestPath

# Operation: list_form_sets
class ListFormSetsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., forms, metadata). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to control result pagination.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results per page. Adjust this value to balance between response size and number of requests needed.")
    filter_is_default: bool | None = Field(default=None, validation_alias="filter[is_default]", serialization_alias="filter[is_default]", description="Filter results to show only form sets marked as default (true) or non-default (false). Useful for identifying primary form set configurations.")
class ListFormSetsRequest(StrictModel):
    """Retrieve a paginated list of form sets with optional filtering and relationship inclusion. Use this to browse available form sets and their metadata."""
    query: ListFormSetsRequestQuery | None = None

# Operation: create_form_set
class CreateFormSetRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the form set. Used to identify and organize the form set in the system.")
    forms: list[str] = Field(default=..., validation_alias="forms", serialization_alias="forms", description="An ordered list of forms to include in this set. Each item can be either a built-in form identifier (such as web_new_incident_form, slack_update_incident_form, etc.) or the slug of a custom form. The order determines how forms are presented in workflows.")
class CreateFormSetRequestBodyData(StrictModel):
    type_: Literal["form_sets"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'form_sets' to indicate this operation creates a form set resource.")
    attributes: CreateFormSetRequestBodyDataAttributes
class CreateFormSetRequestBody(StrictModel):
    data: CreateFormSetRequestBodyData
class CreateFormSetRequest(StrictModel):
    """Creates a new form set that groups multiple forms together for incident management workflows. Form sets can include built-in incident forms or custom forms to organize how incidents are created, updated, and resolved across web and Slack interfaces."""
    body: CreateFormSetRequestBody

# Operation: get_form_set
class GetFormSetRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form set to retrieve.")
class GetFormSetRequest(StrictModel):
    """Retrieves a specific form set by its unique identifier. Use this operation to fetch the complete configuration and details of a form set."""
    path: GetFormSetRequestPath

# Operation: update_form_set
class UpdateFormSetRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form set to update.")
class UpdateFormSetRequestBodyDataAttributes(StrictModel):
    forms: list[str] | None = Field(default=None, validation_alias="forms", serialization_alias="forms", description="An ordered list of forms to include in this form set. Each form can be a custom form (referenced by its slug) or a built-in form such as web incident forms (web_new_incident_form, web_update_incident_form, etc.) or Slack incident forms (slack_new_incident_form, slack_update_incident_form, etc.). The order of forms in this array determines their presentation sequence.")
class UpdateFormSetRequestBodyData(StrictModel):
    type_: Literal["form_sets"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'form_sets' to specify this is a form set resource.")
    attributes: UpdateFormSetRequestBodyDataAttributes | None = None
class UpdateFormSetRequestBody(StrictModel):
    data: UpdateFormSetRequestBodyData
class UpdateFormSetRequest(StrictModel):
    """Update an existing form set by replacing its configuration, including the forms it contains. Use this to modify which forms are included in a form set for web or Slack incident workflows."""
    path: UpdateFormSetRequestPath
    body: UpdateFormSetRequestBody

# Operation: delete_form_set
class DeleteFormSetRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form set to delete.")
class DeleteFormSetRequest(StrictModel):
    """Permanently delete a form set and all its associated data. This action cannot be undone."""
    path: DeleteFormSetRequestPath

# Operation: list_functionalities
class ListFunctionalitiesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., metadata, relationships).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use with page[size] to control result set boundaries.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results per page. Defines the maximum number of functionalities returned in a single request.")
    filter_backstage_id: str | None = Field(default=None, validation_alias="filter[backstage_id]", serialization_alias="filter[backstage_id]", description="Filter results by Backstage system identifier to return only functionalities associated with a specific Backstage instance.")
    filter_cortex_id: str | None = Field(default=None, validation_alias="filter[cortex_id]", serialization_alias="filter[cortex_id]", description="Filter results by Cortex system identifier to return only functionalities associated with a specific Cortex instance.")
    filter_opslevel_id: str | None = Field(default=None, validation_alias="filter[opslevel_id]", serialization_alias="filter[opslevel_id]", description="Filter results by OpsLevel system identifier to return only functionalities associated with a specific OpsLevel instance.")
    filter_external_id: str | None = Field(default=None, validation_alias="filter[external_id]", serialization_alias="filter[external_id]", description="Filter results by external system identifier to return only functionalities with a matching external reference.")
    sort: str | None = Field(default=None, description="Sort results by specified field(s) in ascending or descending order. Use format: field_name or -field_name for reverse order.")
class ListFunctionalitiesRequest(StrictModel):
    """Retrieve a paginated list of functionalities with optional filtering by external system identifiers and sorting capabilities."""
    query: ListFunctionalitiesRequestQuery | None = None

# Operation: create_functionality
class CreateFunctionalityRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the functionality; used to identify and reference this capability across the system.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Internal description of the functionality; provides context for team members managing this resource.")
    public_description: str | None = Field(default=None, validation_alias="public_description", serialization_alias="public_description", description="Public-facing description of the functionality; visible to external stakeholders and in public documentation.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="Email addresses to notify about functionality updates and incidents; supports multiple recipients as a comma-separated or array format.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for visual identification of the functionality in dashboards and UI components.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="Display order position of the functionality in lists and navigation; lower numbers appear first.")
    backstage_id: str | None = Field(default=None, validation_alias="backstage_id", serialization_alias="backstage_id", description="Backstage entity identifier for integration with Backstage catalog; format is namespace/kind/entity_name.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="External system identifier for cross-platform tracking and correlation with third-party tools.")
    opsgenie_team_id: str | None = Field(default=None, validation_alias="opsgenie_team_id", serialization_alias="opsgenie_team_id", description="Opsgenie team identifier to link this functionality with incident response and on-call management.")
    cortex_id: str | None = Field(default=None, validation_alias="cortex_id", serialization_alias="cortex_id", description="Cortex group identifier for integration with Cortex platform and group-level insights.")
    service_now_ci_sys_id: str | None = Field(default=None, validation_alias="service_now_ci_sys_id", serialization_alias="service_now_ci_sys_id", description="Service Now configuration item system ID for ITSM integration and change management tracking.")
    show_uptime: bool | None = Field(default=None, validation_alias="show_uptime", serialization_alias="show_uptime", description="Enable uptime monitoring and display for this functionality; when enabled, uptime metrics will be calculated and shown.")
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(default=None, validation_alias="show_uptime_last_days", serialization_alias="show_uptime_last_days", description="Time window for uptime calculation in days; valid options are 30, 60, or 90 days, with 60 days as the default.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="Array of environment IDs where this functionality operates; links the functionality to specific deployment environments.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service IDs that implement or depend on this functionality; establishes service-to-functionality relationships.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="Array of team/group IDs with ownership responsibility for this functionality; enables team-based access control and notifications.")
    owner_user_ids: list[int] | None = Field(default=None, validation_alias="owner_user_ids", serialization_alias="owner_user_ids", description="Array of user IDs with individual ownership of this functionality; enables user-level accountability and direct notifications.")
    slack_channels: list[CreateFunctionalityBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="Array of Slack channel identifiers for functionality-related notifications and updates; supports multiple channels for broad communication.")
    slack_aliases: list[CreateFunctionalityBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="Array of Slack aliases or handles to mention in notifications; enables direct user mentions and targeted alerts.")
class CreateFunctionalityRequestBodyData(StrictModel):
    type_: Literal["functionalities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'functionalities' to indicate this is a functionality resource.")
    attributes: CreateFunctionalityRequestBodyDataAttributes
class CreateFunctionalityRequestBody(StrictModel):
    data: CreateFunctionalityRequestBodyData
class CreateFunctionalityRequest(StrictModel):
    """Creates a new functionality with optional integrations to external systems, ownership assignments, and monitoring configurations. Functionalities represent logical business capabilities that can be tracked across services, environments, and teams."""
    body: CreateFunctionalityRequestBody

# Operation: get_functionality
class GetFunctionalityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the functionality to retrieve. This is a required string value that specifies which functionality resource to fetch.")
class GetFunctionalityRequest(StrictModel):
    """Retrieves a specific functionality by its unique identifier. Use this operation to fetch detailed information about a single functionality resource."""
    path: GetFunctionalityRequestPath

# Operation: update_functionality
class UpdateFunctionalityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the functionality to update.")
class UpdateFunctionalityRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Internal description of the functionality for reference and documentation purposes.")
    public_description: str | None = Field(default=None, validation_alias="public_description", serialization_alias="public_description", description="Public-facing description of the functionality visible to external stakeholders and users.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="List of email addresses to receive notifications related to this functionality. Specify as an array of valid email strings.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hexadecimal color code for visual identification of the functionality in UI displays (e.g., #FF5733).")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="Numeric position or order for sorting and displaying the functionality relative to others.")
    backstage_id: str | None = Field(default=None, validation_alias="backstage_id", serialization_alias="backstage_id", description="Backstage entity reference in the format namespace/kind/entity_name to link this functionality to a Backstage catalog entity.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="External identifier for integrating this functionality with third-party systems or external databases.")
    opsgenie_team_id: str | None = Field(default=None, validation_alias="opsgenie_team_id", serialization_alias="opsgenie_team_id", description="Opsgenie team identifier to associate incident response and alerting responsibilities with this functionality.")
    cortex_id: str | None = Field(default=None, validation_alias="cortex_id", serialization_alias="cortex_id", description="Cortex group identifier to link this functionality with Cortex organizational groupings.")
    service_now_ci_sys_id: str | None = Field(default=None, validation_alias="service_now_ci_sys_id", serialization_alias="service_now_ci_sys_id", description="Service Now Configuration Item system ID to establish traceability and integration with Service Now CMDB.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="Array of environment identifiers (e.g., production, staging, development) where this functionality operates or is relevant.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service identifiers that implement or depend on this functionality.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="Array of team/group identifiers designated as owners responsible for this functionality.")
    owner_user_ids: list[int] | None = Field(default=None, validation_alias="owner_user_ids", serialization_alias="owner_user_ids", description="Array of user identifiers designated as individual owners responsible for this functionality.")
    slack_channels: list[UpdateFunctionalityBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="Array of Slack channel identifiers for communication and notifications related to this functionality.")
    slack_aliases: list[UpdateFunctionalityBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="Array of Slack aliases or handles for automated mentions and notifications in Slack workflows.")
class UpdateFunctionalityRequestBodyData(StrictModel):
    type_: Literal["functionalities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'functionalities' to identify this as a functionality resource.")
    attributes: UpdateFunctionalityRequestBodyDataAttributes | None = None
class UpdateFunctionalityRequestBody(StrictModel):
    data: UpdateFunctionalityRequestBodyData
class UpdateFunctionalityRequest(StrictModel):
    """Update an existing functionality with new metadata, associations, and configuration. Modify properties like description, color, position, and linked resources such as services, environments, and owner teams."""
    path: UpdateFunctionalityRequestPath
    body: UpdateFunctionalityRequestBody

# Operation: delete_functionality
class DeleteFunctionalityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the functionality to delete.")
class DeleteFunctionalityRequest(StrictModel):
    """Permanently delete a functionality by its unique identifier. This action cannot be undone."""
    path: DeleteFunctionalityRequestPath

# Operation: get_functionality_incidents_chart
class GetFunctionalityIncidentsChartRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the functionality for which to retrieve incident chart data.")
class GetFunctionalityIncidentsChartRequestQuery(StrictModel):
    period: str = Field(default=..., description="The time period for which to retrieve incident data. Specify the desired time range to filter incidents in the chart (e.g., last 7 days, last month, custom date range).")
class GetFunctionalityIncidentsChartRequest(StrictModel):
    """Retrieve a chart visualization of incidents for a specific functionality over a defined time period. This helps track incident trends and patterns for a given functionality."""
    path: GetFunctionalityIncidentsChartRequestPath
    query: GetFunctionalityIncidentsChartRequestQuery

# Operation: get_functionality_uptime_chart
class GetFunctionalityUptimeChartRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the functionality for which to retrieve the uptime chart.")
class GetFunctionalityUptimeChartRequestQuery(StrictModel):
    period: str | None = Field(default=None, description="The time period for the uptime chart data (e.g., day, week, month, year). If not specified, a default period will be used.")
class GetFunctionalityUptimeChartRequest(StrictModel):
    """Retrieve an uptime chart for a specific functionality, showing availability metrics over a selected time period."""
    path: GetFunctionalityUptimeChartRequestPath
    query: GetFunctionalityUptimeChartRequestQuery | None = None

# Operation: list_workflow_tasks
class ListWorkflowTasksRequestPath(StrictModel):
    workflow_id: str = Field(default=..., description="The unique identifier of the workflow containing the tasks to list.")
class ListWorkflowTasksRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., assignees, dependencies). Reduces need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of tasks to return per page. Adjust to balance between response size and number of requests needed.")
class ListWorkflowTasksRequest(StrictModel):
    """Retrieve a paginated list of tasks within a specific workflow. Use pagination parameters to control result size and navigate through large task sets."""
    path: ListWorkflowTasksRequestPath
    query: ListWorkflowTasksRequestQuery | None = None

# Operation: create_workflow_task
class CreateWorkflowTaskRequestPath(StrictModel):
    workflow_id: str = Field(default=..., description="The unique identifier of the workflow to which this task will be added.")
class CreateWorkflowTaskRequestBodyDataAttributes(StrictModel):
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The sequential position where this task should be placed within the workflow. Tasks are executed in position order.")
    skip_on_failure: bool | None = Field(default=None, validation_alias="skip_on_failure", serialization_alias="skip_on_failure", description="When enabled, the workflow will skip this task if any previous tasks in the workflow have failed, allowing for conditional execution based on upstream success.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Controls whether this task is active and will execute when the workflow runs. Defaults to enabled.")
    task_params: AddActionItemTaskParams | UpdateActionItemTaskParams | AddRoleTaskParams | AddSlackBookmarkTaskParams | AddTeamTaskParams | AddToTimelineTaskParams | ArchiveSlackChannelsTaskParams | AttachDatadogDashboardsTaskParams | AutoAssignRoleOpsgenieTaskParams | AutoAssignRoleRootlyTaskParams | AutoAssignRolePagerdutyTaskParams | UpdatePagerdutyIncidentTaskParams | CreatePagerdutyStatusUpdateTaskParams | CreatePagertreeAlertTaskParams | UpdatePagertreeAlertTaskParams | AutoAssignRoleVictorOpsTaskParams | CallPeopleTaskParams | CreateAirtableTableRecordTaskParams | CreateAsanaSubtaskTaskParams | CreateAsanaTaskTaskParams | CreateConfluencePageTaskParams | CreateDatadogNotebookTaskParams | CreateCodaPageTaskParams | CreateDropboxPaperPageTaskParams | CreateGithubIssueTaskParams | CreateGitlabIssueTaskParams | CreateOutlookEventTaskParams | CreateGoogleCalendarEventTaskParams | UpdateGoogleDocsPageTaskParams | UpdateCodaPageTaskParams | UpdateGoogleCalendarEventTaskParams | CreateSharepointPageTaskParams | CreateGoogleDocsPageTaskParams | CreateGoogleDocsPermissionsTaskParams | RemoveGoogleDocsPermissionsTaskParams | CreateQuipPageTaskParams | CreateGoogleMeetingTaskParams | CreateGoToMeetingTaskParams | CreateIncidentTaskParams | CreateIncidentPostmortemTaskParams | CreateJiraIssueTaskParams | CreateJiraSubtaskTaskParams | CreateLinearIssueTaskParams | CreateLinearSubtaskIssueTaskParams | CreateLinearIssueCommentTaskParams | CreateMicrosoftTeamsMeetingTaskParams | CreateMicrosoftTeamsChannelTaskParams | AddMicrosoftTeamsTabTaskParams | ArchiveMicrosoftTeamsChannelsTaskParams | RenameMicrosoftTeamsChannelTaskParams | InviteToMicrosoftTeamsChannelTaskParams | CreateNotionPageTaskParams | SendMicrosoftTeamsMessageTaskParams | SendMicrosoftTeamsBlocksTaskParams | UpdateNotionPageTaskParams | CreateServiceNowIncidentTaskParams | CreateShortcutStoryTaskParams | CreateShortcutTaskTaskParams | CreateTrelloCardTaskParams | CreateWebexMeetingTaskParams | CreateZendeskTicketTaskParams | CreateZendeskJiraLinkTaskParams | CreateClickupTaskTaskParams | CreateMotionTaskTaskParams | CreateZoomMeetingTaskParams | GetGithubCommitsTaskParams | GetGitlabCommitsTaskParams | GetPulsesTaskParams | GetAlertsTaskParams | HttpClientTaskParams | InviteToSlackChannelOpsgenieTaskParams | InviteToSlackChannelRootlyTaskParams | InviteToSlackChannelPagerdutyTaskParams | InviteToSlackChannelTaskParams | InviteToSlackChannelVictorOpsTaskParams | PageOpsgenieOnCallRespondersTaskParams | CreateOpsgenieAlertTaskParams | UpdateOpsgenieAlertTaskParams | UpdateOpsgenieIncidentTaskParams | PageRootlyOnCallRespondersTaskParams | PagePagerdutyOnCallRespondersTaskParams | PageVictorOpsOnCallRespondersTaskParams | UpdateVictorOpsIncidentTaskParams | PrintTaskParams | PublishIncidentTaskParams | RedisClientTaskParams | RenameSlackChannelTaskParams | ChangeSlackChannelPrivacyTaskParams | RunCommandHerokuTaskParams | SendEmailTaskParams | SendDashboardReportTaskParams | CreateSlackChannelTaskParams | SendSlackMessageTaskParams | SendSmsTaskParams | SendWhatsappMessageTaskParams | SnapshotDatadogGraphTaskParams | SnapshotGrafanaDashboardTaskParams | SnapshotLookerLookTaskParams | SnapshotNewRelicGraphTaskParams | TweetTwitterMessageTaskParams | UpdateAirtableTableRecordTaskParams | UpdateAsanaTaskTaskParams | UpdateGithubIssueTaskParams | UpdateGitlabIssueTaskParams | UpdateIncidentTaskParams | UpdateIncidentPostmortemTaskParams | UpdateJiraIssueTaskParams | UpdateLinearIssueTaskParams | UpdateServiceNowIncidentTaskParams | UpdateShortcutStoryTaskParams | UpdateShortcutTaskTaskParams | UpdateSlackChannelTopicTaskParams | UpdateStatusTaskParams | UpdateIncidentStatusTimestampTaskParams | UpdateTrelloCardTaskParams | UpdateClickupTaskTaskParams | UpdateMotionTaskTaskParams | UpdateZendeskTicketTaskParams | UpdateAttachedAlertsTaskParams | TriggerWorkflowTaskParams | SendSlackBlocksTaskParams | GeniusCreateOpenaiChatCompletionTaskParams | GeniusCreateWatsonxChatCompletionTaskParams | GeniusCreateGoogleGeminiChatCompletionTaskParams | GeniusCreateAnthropicChatCompletionTaskParams = Field(default=..., validation_alias="task_params", serialization_alias="task_params", description="Configuration parameters specific to this task's type and behavior. Structure and required fields depend on the task implementation.")
class CreateWorkflowTaskRequestBodyData(StrictModel):
    type_: Literal["workflow_tasks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this operation, which must be set to 'workflow_tasks'.")
    attributes: CreateWorkflowTaskRequestBodyDataAttributes
class CreateWorkflowTaskRequestBody(StrictModel):
    data: CreateWorkflowTaskRequestBodyData
class CreateWorkflowTaskRequest(StrictModel):
    """Creates a new task within a workflow. The task can be positioned in the workflow sequence and configured with execution behavior settings like failure handling and enable/disable status."""
    path: CreateWorkflowTaskRequestPath
    body: CreateWorkflowTaskRequestBody

# Operation: get_workflow_task
class GetWorkflowTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow task to retrieve.")
class GetWorkflowTaskRequest(StrictModel):
    """Retrieves a specific workflow task by its unique identifier. Use this to fetch detailed information about a single task within a workflow."""
    path: GetWorkflowTaskRequestPath

# Operation: update_workflow_task
class UpdateWorkflowTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow task to update.")
class UpdateWorkflowTaskRequestBodyDataAttributes(StrictModel):
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The execution order position of this task within the workflow. Lower positions execute first.")
    skip_on_failure: bool | None = Field(default=None, validation_alias="skip_on_failure", serialization_alias="skip_on_failure", description="When enabled, the workflow will skip this task and continue to the next one if any failures occur during execution.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Controls whether this task is active in the workflow. Disabled tasks are skipped during execution. Defaults to true (enabled).")
    task_params: AddActionItemTaskParams | UpdateActionItemTaskParams | AddRoleTaskParams | AddSlackBookmarkTaskParams | AddTeamTaskParams | AddToTimelineTaskParams | ArchiveSlackChannelsTaskParams | AttachDatadogDashboardsTaskParams | AutoAssignRoleOpsgenieTaskParams | AutoAssignRoleRootlyTaskParams | AutoAssignRolePagerdutyTaskParams | UpdatePagerdutyIncidentTaskParams | CreatePagerdutyStatusUpdateTaskParams | CreatePagertreeAlertTaskParams | UpdatePagertreeAlertTaskParams | AutoAssignRoleVictorOpsTaskParams | CallPeopleTaskParams | CreateAirtableTableRecordTaskParams | CreateAsanaSubtaskTaskParams | CreateAsanaTaskTaskParams | CreateConfluencePageTaskParams | CreateDatadogNotebookTaskParams | CreateCodaPageTaskParams | CreateDropboxPaperPageTaskParams | CreateGithubIssueTaskParams | CreateGitlabIssueTaskParams | CreateOutlookEventTaskParams | CreateGoogleCalendarEventTaskParams | UpdateGoogleDocsPageTaskParams | UpdateCodaPageTaskParams | UpdateGoogleCalendarEventTaskParams | CreateSharepointPageTaskParams | CreateGoogleDocsPageTaskParams | CreateGoogleDocsPermissionsTaskParams | RemoveGoogleDocsPermissionsTaskParams | CreateQuipPageTaskParams | CreateGoogleMeetingTaskParams | CreateGoToMeetingTaskParams | CreateIncidentTaskParams | CreateIncidentPostmortemTaskParams | CreateJiraIssueTaskParams | CreateJiraSubtaskTaskParams | CreateLinearIssueTaskParams | CreateLinearSubtaskIssueTaskParams | CreateLinearIssueCommentTaskParams | CreateMicrosoftTeamsMeetingTaskParams | CreateMicrosoftTeamsChannelTaskParams | AddMicrosoftTeamsTabTaskParams | ArchiveMicrosoftTeamsChannelsTaskParams | RenameMicrosoftTeamsChannelTaskParams | InviteToMicrosoftTeamsChannelTaskParams | CreateNotionPageTaskParams | SendMicrosoftTeamsMessageTaskParams | SendMicrosoftTeamsBlocksTaskParams | UpdateNotionPageTaskParams | CreateServiceNowIncidentTaskParams | CreateShortcutStoryTaskParams | CreateShortcutTaskTaskParams | CreateTrelloCardTaskParams | CreateWebexMeetingTaskParams | CreateZendeskTicketTaskParams | CreateZendeskJiraLinkTaskParams | CreateClickupTaskTaskParams | CreateMotionTaskTaskParams | CreateZoomMeetingTaskParams | GetGithubCommitsTaskParams | GetGitlabCommitsTaskParams | GetPulsesTaskParams | GetAlertsTaskParams | HttpClientTaskParams | InviteToSlackChannelOpsgenieTaskParams | InviteToSlackChannelRootlyTaskParams | InviteToSlackChannelPagerdutyTaskParams | InviteToSlackChannelTaskParams | InviteToSlackChannelVictorOpsTaskParams | PageOpsgenieOnCallRespondersTaskParams | CreateOpsgenieAlertTaskParams | UpdateOpsgenieAlertTaskParams | UpdateOpsgenieIncidentTaskParams | PageRootlyOnCallRespondersTaskParams | PagePagerdutyOnCallRespondersTaskParams | PageVictorOpsOnCallRespondersTaskParams | UpdateVictorOpsIncidentTaskParams | PrintTaskParams | PublishIncidentTaskParams | RedisClientTaskParams | RenameSlackChannelTaskParams | ChangeSlackChannelPrivacyTaskParams | RunCommandHerokuTaskParams | SendEmailTaskParams | SendDashboardReportTaskParams | CreateSlackChannelTaskParams | SendSlackMessageTaskParams | SendSmsTaskParams | SendWhatsappMessageTaskParams | SnapshotDatadogGraphTaskParams | SnapshotGrafanaDashboardTaskParams | SnapshotLookerLookTaskParams | SnapshotNewRelicGraphTaskParams | TweetTwitterMessageTaskParams | UpdateAirtableTableRecordTaskParams | UpdateAsanaTaskTaskParams | UpdateGithubIssueTaskParams | UpdateGitlabIssueTaskParams | UpdateIncidentTaskParams | UpdateIncidentPostmortemTaskParams | UpdateJiraIssueTaskParams | UpdateLinearIssueTaskParams | UpdateServiceNowIncidentTaskParams | UpdateShortcutStoryTaskParams | UpdateShortcutTaskTaskParams | UpdateSlackChannelTopicTaskParams | UpdateStatusTaskParams | UpdateIncidentStatusTimestampTaskParams | UpdateTrelloCardTaskParams | UpdateClickupTaskTaskParams | UpdateMotionTaskTaskParams | UpdateZendeskTicketTaskParams | UpdateAttachedAlertsTaskParams | TriggerWorkflowTaskParams | SendSlackBlocksTaskParams | GeniusCreateOpenaiChatCompletionTaskParams | GeniusCreateWatsonxChatCompletionTaskParams | GeniusCreateGoogleGeminiChatCompletionTaskParams | GeniusCreateAnthropicChatCompletionTaskParams | None = Field(default=None, validation_alias="task_params", serialization_alias="task_params", description="Task-specific configuration parameters. Structure and content depend on the task type being configured.")
class UpdateWorkflowTaskRequestBodyData(StrictModel):
    type_: Literal["workflow_tasks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'workflow_tasks' to specify this is a workflow task resource.")
    attributes: UpdateWorkflowTaskRequestBodyDataAttributes | None = None
class UpdateWorkflowTaskRequestBody(StrictModel):
    data: UpdateWorkflowTaskRequestBodyData
class UpdateWorkflowTaskRequest(StrictModel):
    """Update a specific workflow task configuration by its ID. Modify task properties such as execution position, failure handling behavior, enabled status, and task-specific parameters."""
    path: UpdateWorkflowTaskRequestPath
    body: UpdateWorkflowTaskRequestBody

# Operation: delete_workflow_task
class DeleteWorkflowTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow task to delete.")
class DeleteWorkflowTaskRequest(StrictModel):
    """Permanently delete a specific workflow task by its unique identifier. This action cannot be undone."""
    path: DeleteWorkflowTaskRequestPath

# Operation: list_workflow_form_field_conditions
class ListWorkflowFormFieldConditionsRequestPath(StrictModel):
    workflow_id: str = Field(default=..., description="The unique identifier of the workflow for which to retrieve form field conditions.")
class ListWorkflowFormFieldConditionsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., field references, condition rules). Specify which associations should be populated to reduce additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results to return per page. Adjust this to control the size of each paginated response.")
class ListWorkflowFormFieldConditionsRequest(StrictModel):
    """Retrieve all form field conditions configured for a specific workflow. Form field conditions define rules that control the visibility, requirement status, or behavior of form fields based on other field values."""
    path: ListWorkflowFormFieldConditionsRequestPath
    query: ListWorkflowFormFieldConditionsRequestQuery | None = None

# Operation: get_workflow_form_field_condition
class GetWorkflowFormFieldConditionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow form field condition to retrieve.")
class GetWorkflowFormFieldConditionRequest(StrictModel):
    """Retrieves a specific workflow form field condition by its unique identifier. Use this to fetch the details of a condition that controls the visibility or behavior of a form field within a workflow."""
    path: GetWorkflowFormFieldConditionRequestPath

# Operation: list_workflow_groups
class ListWorkflowGroupsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related fields to include in the response for expanded context (e.g., metadata, configuration details).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of workflow groups to return per page. Adjust to control result set size for pagination.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter results by workflow group kind or type. Specify the exact kind value to narrow results.")
    filter_expanded: bool | None = Field(default=None, validation_alias="filter[expanded]", serialization_alias="filter[expanded]", description="Filter results by expansion state. Set to true to show only expanded groups, or false for collapsed groups.")
    filter_position: int | None = Field(default=None, validation_alias="filter[position]", serialization_alias="filter[position]", description="Filter results by position or order index. Useful for retrieving groups at specific positions in a sequence.")
class ListWorkflowGroupsRequest(StrictModel):
    """Retrieve a paginated list of workflow groups with optional filtering by kind, expansion state, and position. Use this to discover available workflow groups and their configurations."""
    query: ListWorkflowGroupsRequestQuery | None = None

# Operation: get_workflow_group
class GetWorkflowGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow group to retrieve.")
class GetWorkflowGroupRequest(StrictModel):
    """Retrieves a specific workflow group by its unique identifier. Use this operation to fetch detailed information about a workflow group configuration."""
    path: GetWorkflowGroupRequestPath

# Operation: update_workflow_group
class UpdateWorkflowGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow group to update.")
class UpdateWorkflowGroupRequestBodyDataAttributes(StrictModel):
    kind: Literal["simple", "incident", "post_mortem", "action_item", "pulse", "alert"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="The category or classification of the workflow group. Choose from: simple, incident, post_mortem, action_item, pulse, or alert.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description explaining the purpose or contents of the workflow group.")
    icon: str | None = Field(default=None, validation_alias="icon", serialization_alias="icon", description="An emoji character displayed as a visual indicator next to the workflow group name.")
    expanded: bool | None = Field(default=None, validation_alias="expanded", serialization_alias="expanded", description="A boolean flag indicating whether the workflow group should be displayed in an expanded (true) or collapsed (false) state.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of the workflow group relative to other groups, where lower numbers appear first.")
class UpdateWorkflowGroupRequestBodyData(StrictModel):
    type_: Literal["workflow_groups"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'workflow_groups' to specify this is a workflow group resource.")
    attributes: UpdateWorkflowGroupRequestBodyDataAttributes | None = None
class UpdateWorkflowGroupRequestBody(StrictModel):
    data: UpdateWorkflowGroupRequestBodyData
class UpdateWorkflowGroupRequest(StrictModel):
    """Update a specific workflow group's configuration, including its kind, description, icon, expanded state, and position. Changes are applied to the workflow group identified by the provided id."""
    path: UpdateWorkflowGroupRequestPath
    body: UpdateWorkflowGroupRequestBody

# Operation: delete_workflow_group
class DeleteWorkflowGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow group to delete.")
class DeleteWorkflowGroupRequest(StrictModel):
    """Permanently delete a workflow group and all its associated data by its unique identifier. This action cannot be undone."""
    path: DeleteWorkflowGroupRequestPath

# Operation: list_workflow_runs
class ListWorkflowRunsRequestPath(StrictModel):
    workflow_id: str = Field(default=..., description="The unique identifier of the workflow for which to list runs.")
class ListWorkflowRunsRequestQuery(StrictModel):
    include: Literal["genius_task_runs"] | None = Field(default=None, description="Optional comma-separated list of related data to include in the response. Use 'genius_task_runs' to include detailed task execution information for each workflow run.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of workflow runs to return per page. Adjust this to control the size of each paginated response.")
class ListWorkflowRunsRequest(StrictModel):
    """Retrieve a paginated list of workflow runs for a specified workflow. Optionally include related task run data to get detailed execution information."""
    path: ListWorkflowRunsRequestPath
    query: ListWorkflowRunsRequestQuery | None = None

# Operation: create_workflow_run
class CreateWorkflowRunRequestPath(StrictModel):
    workflow_id: str = Field(default=..., description="The unique identifier of the workflow for which to create a run.")
class CreateWorkflowRunRequestBodyData(StrictModel):
    type_: Literal["workflow_runs"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'workflow_runs' to specify the type of object being created.")
    attributes: CreateWorkflowRunBodyDataAttributesV0 | CreateWorkflowRunBodyDataAttributesV1 | CreateWorkflowRunBodyDataAttributesV2 | CreateWorkflowRunBodyDataAttributesV3 | CreateWorkflowRunBodyDataAttributesV4 | CreateWorkflowRunBodyDataAttributesV5 = Field(default=..., validation_alias="attributes", serialization_alias="attributes", description="An object containing the workflow run configuration and execution parameters, such as input variables, scheduling options, or runtime settings.")
class CreateWorkflowRunRequestBody(StrictModel):
    data: CreateWorkflowRunRequestBodyData
class CreateWorkflowRunRequest(StrictModel):
    """Initiates a new workflow run for the specified workflow. This creates an execution instance with the provided configuration and attributes."""
    path: CreateWorkflowRunRequestPath
    body: CreateWorkflowRunRequestBody

# Operation: get_workflow
class GetWorkflowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow to retrieve.")
class GetWorkflowRequestQuery(StrictModel):
    include: Literal["form_field_conditions", "genius_tasks", "genius_workflow_runs"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Valid options are form_field_conditions, genius_tasks, and genius_workflow_runs.")
class GetWorkflowRequest(StrictModel):
    """Retrieves a specific workflow by its unique identifier. Optionally include related data such as form field conditions, genius tasks, or workflow run history."""
    path: GetWorkflowRequestPath
    query: GetWorkflowRequestQuery | None = None

# Operation: delete_workflow
class DeleteWorkflowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow to delete.")
class DeleteWorkflowRequest(StrictModel):
    """Permanently delete a workflow by its unique identifier. This action cannot be undone."""
    path: DeleteWorkflowRequestPath

# Operation: list_heartbeats
class ListHeartbeatsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., metadata, details). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of heartbeats to return per page. Adjust to balance between response size and number of requests needed.")
class ListHeartbeatsRequest(StrictModel):
    """Retrieve a paginated list of heartbeats. Use pagination parameters to control the number of results and navigate through pages."""
    query: ListHeartbeatsRequestQuery | None = None

# Operation: create_heartbeat
class CreateHeartbeatRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the heartbeat to identify it in the system.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional detailed description providing additional context about the heartbeat's purpose or monitoring scope.")
    alert_summary: str = Field(default=..., validation_alias="alert_summary", serialization_alias="alert_summary", description="A summary message that will be included in alerts triggered when the heartbeat fails to renew within the specified interval.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="Optional identifier for the urgency level assigned to alerts triggered by heartbeat expiration. If not specified, a default urgency level is used.")
    interval: int = Field(default=..., validation_alias="interval", serialization_alias="interval", description="The numeric duration value that, combined with interval_unit, defines how frequently the heartbeat must be renewed to remain active.")
    interval_unit: Literal["seconds", "minutes", "hours"] = Field(default=..., validation_alias="interval_unit", serialization_alias="interval_unit", description="The unit of time for the interval duration; must be one of: seconds, minutes, or hours.")
    notification_target_id: str = Field(default=..., validation_alias="notification_target_id", serialization_alias="notification_target_id", description="The identifier of the recipient (user, group, service, or escalation policy) that will receive alerts when the heartbeat expires.")
    notification_target_type: Literal["User", "Group", "Service", "EscalationPolicy"] = Field(default=..., validation_alias="notification_target_type", serialization_alias="notification_target_type", description="The type of notification target; must be one of: User, Group, Service, or EscalationPolicy.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Optional boolean flag to enable or disable alert triggering when the heartbeat expires. Defaults to true if not specified.")
class CreateHeartbeatRequestBodyData(StrictModel):
    type_: Literal["heartbeats"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'heartbeats' to indicate this is a heartbeat resource.")
    attributes: CreateHeartbeatRequestBodyDataAttributes
class CreateHeartbeatRequestBody(StrictModel):
    data: CreateHeartbeatRequestBodyData
class CreateHeartbeatRequest(StrictModel):
    """Creates a new heartbeat to monitor system health and trigger alerts when the heartbeat expires. Heartbeats are periodic signals that must be renewed; if not received within the specified interval, alerts are sent to the configured notification target."""
    body: CreateHeartbeatRequestBody

# Operation: get_heartbeat
class GetHeartbeatRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the heartbeat to retrieve.")
class GetHeartbeatRequest(StrictModel):
    """Retrieves a specific heartbeat record by its unique identifier. Use this to fetch details about a particular heartbeat event or status check."""
    path: GetHeartbeatRequestPath

# Operation: update_heartbeat
class UpdateHeartbeatRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the heartbeat to update.")
class UpdateHeartbeatRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the heartbeat's purpose or monitoring context.")
    alert_summary: str | None = Field(default=None, validation_alias="alert_summary", serialization_alias="alert_summary", description="A brief summary of the alerts that will be triggered when this heartbeat expires or fails.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The urgency level ID assigned to alerts triggered by heartbeat expiration, determining priority and escalation behavior.")
    interval: int | None = Field(default=None, validation_alias="interval", serialization_alias="interval", description="The numeric interval value that, combined with interval_unit, defines how frequently the heartbeat should be received.")
    interval_unit: Literal["seconds", "minutes", "hours"] | None = Field(default=None, validation_alias="interval_unit", serialization_alias="interval_unit", description="The time unit for the heartbeat interval. Valid options are seconds, minutes, or hours.")
    notification_target_id: str | None = Field(default=None, validation_alias="notification_target_id", serialization_alias="notification_target_id", description="The ID of the user, group, service, or escalation policy that should receive notifications when the heartbeat expires.")
    notification_target_type: Literal["User", "Group", "Service", "EscalationPolicy"] | None = Field(default=None, validation_alias="notification_target_type", serialization_alias="notification_target_type", description="The type of notification target. Must be one of: User, Group, Service, or EscalationPolicy.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether alerts should be triggered when this heartbeat expires. Set to false to temporarily disable alerting without removing the heartbeat configuration.")
class UpdateHeartbeatRequestBodyData(StrictModel):
    type_: Literal["heartbeats"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'heartbeats' to identify this as a heartbeat resource.")
    attributes: UpdateHeartbeatRequestBodyDataAttributes | None = None
class UpdateHeartbeatRequestBody(StrictModel):
    data: UpdateHeartbeatRequestBodyData
class UpdateHeartbeatRequest(StrictModel):
    """Update an existing heartbeat configuration by ID. Modify monitoring intervals, alert settings, and notification targets for a specific heartbeat."""
    path: UpdateHeartbeatRequestPath
    body: UpdateHeartbeatRequestBody

# Operation: delete_heartbeat
class DeleteHeartbeatRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the heartbeat to delete.")
class DeleteHeartbeatRequest(StrictModel):
    """Permanently delete a heartbeat record by its unique identifier. This action cannot be undone."""
    path: DeleteHeartbeatRequestPath

# Operation: list_incident_action_items
class ListIncidentActionItemsRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which to retrieve action items.")
class ListIncidentActionItemsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., assignee details, timestamps). Specify which fields or nested objects should be populated.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of action items to return per page. Adjust this to control the size of each paginated response.")
class ListIncidentActionItemsRequest(StrictModel):
    """Retrieve a paginated list of action items associated with a specific incident. Use this to view all tasks and follow-ups that need to be completed for incident resolution."""
    path: ListIncidentActionItemsRequestPath
    query: ListIncidentActionItemsRequestQuery | None = None

# Operation: create_incident_action_item
class CreateIncidentActionItemRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident to which this action item belongs.")
class CreateIncidentActionItemRequestBodyDataAttributes(StrictModel):
    summary: str = Field(default=..., validation_alias="summary", serialization_alias="summary", description="A brief title or headline for the action item that summarizes what needs to be done.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Additional details or context about the action item, providing more information beyond the summary.")
    kind: Literal["task", "follow_up"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="Categorizes the action item as either a task (work to be completed) or a follow-up (item to revisit or check on).")
    assigned_to_user_id: int | None = Field(default=None, validation_alias="assigned_to_user_id", serialization_alias="assigned_to_user_id", description="The user ID of the person responsible for completing this action item.")
    assigned_to_group_ids: list[str] | None = Field(default=None, validation_alias="assigned_to_group_ids", serialization_alias="assigned_to_group_ids", description="A list of group IDs to assign this action item to; multiple groups can be assigned simultaneously.")
    priority: Literal["high", "medium", "low"] | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="The urgency level of the action item: high, medium, or low priority.")
    status: Literal["open", "in_progress", "cancelled", "done"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current state of the action item: open (not started), in_progress (actively being worked on), cancelled (no longer needed), or done (completed).")
    due_date: str | None = Field(default=None, validation_alias="due_date", serialization_alias="due_date", description="The target completion date for the action item in ISO 8601 format (YYYY-MM-DD).")
    jira_issue_key: str | None = Field(default=None, validation_alias="jira_issue_key", serialization_alias="jira_issue_key", description="An optional reference to a Jira issue key for integration with Jira tracking systems.")
class CreateIncidentActionItemRequestBodyData(StrictModel):
    type_: Literal["incident_action_items"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'incident_action_items'.")
    attributes: CreateIncidentActionItemRequestBodyDataAttributes
class CreateIncidentActionItemRequestBody(StrictModel):
    data: CreateIncidentActionItemRequestBodyData
class CreateIncidentActionItemRequest(StrictModel):
    """Creates a new action item associated with an incident to track tasks or follow-ups that need to be completed. Action items can be assigned to users or groups, prioritized, and tracked through their lifecycle."""
    path: CreateIncidentActionItemRequestPath
    body: CreateIncidentActionItemRequestBody

# Operation: get_incident_action_item
class GetIncidentActionItemsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident action item to retrieve.")
class GetIncidentActionItemsRequest(StrictModel):
    """Retrieves a specific incident action item by its unique identifier. Use this to fetch details about a single action item associated with an incident."""
    path: GetIncidentActionItemsRequestPath

# Operation: update_incident_action_item
class UpdateIncidentActionItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the action item to update.")
class UpdateIncidentActionItemRequestBodyDataAttributes(StrictModel):
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief title or headline for the action item.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Detailed information about the action item and what needs to be done.")
    kind: Literal["task", "follow_up"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="Categorizes the action item as either a 'task' (work to be completed) or 'follow_up' (follow-up activity).")
    assigned_to_user_id: int | None = Field(default=None, validation_alias="assigned_to_user_id", serialization_alias="assigned_to_user_id", description="The ID of the user to assign this action item to. Only one user can be assigned.")
    assigned_to_group_ids: list[str] | None = Field(default=None, validation_alias="assigned_to_group_ids", serialization_alias="assigned_to_group_ids", description="A list of group IDs to assign this action item to. Multiple groups can be assigned simultaneously.")
    priority: Literal["high", "medium", "low"] | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="The urgency level of the action item: 'high', 'medium', or 'low'.")
    status: Literal["open", "in_progress", "cancelled", "done"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current state of the action item: 'open' (not started), 'in_progress' (actively being worked on), 'cancelled' (abandoned), or 'done' (completed).")
    due_date: str | None = Field(default=None, validation_alias="due_date", serialization_alias="due_date", description="The target completion date for the action item in ISO 8601 format (YYYY-MM-DD).")
    jira_issue_key: str | None = Field(default=None, validation_alias="jira_issue_key", serialization_alias="jira_issue_key", description="The Jira issue key to link this action item to an external Jira ticket (e.g., 'PROJ-123').")
class UpdateIncidentActionItemRequestBodyData(StrictModel):
    type_: Literal["incident_action_items"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be 'incident_action_items'.")
    attributes: UpdateIncidentActionItemRequestBodyDataAttributes | None = None
class UpdateIncidentActionItemRequestBody(StrictModel):
    data: UpdateIncidentActionItemRequestBodyData
class UpdateIncidentActionItemRequest(StrictModel):
    """Update a specific incident action item by its ID. Modify properties such as summary, description, assignment, priority, status, due date, and Jira integration."""
    path: UpdateIncidentActionItemRequestPath
    body: UpdateIncidentActionItemRequestBody

# Operation: delete_incident_action_item
class DeleteIncidentActionItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident action item to delete.")
class DeleteIncidentActionItemRequest(StrictModel):
    """Permanently delete a specific incident action item by its unique identifier. This operation removes the action item record from the system."""
    path: DeleteIncidentActionItemRequestPath

# Operation: list_action_items
class ListAllIncidentActionItemsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., incident, assignee). Reduces the need for follow-up requests.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of action items to return per page. Adjust to balance response size and number of requests needed.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter results by action item kind or type (e.g., investigation, remediation, follow-up).")
    filter_priority: str | None = Field(default=None, validation_alias="filter[priority]", serialization_alias="filter[priority]", description="Filter results by priority level (e.g., critical, high, medium, low).")
    filter_status: str | None = Field(default=None, validation_alias="filter[status]", serialization_alias="filter[status]", description="Filter results by action item status (e.g., open, in_progress, completed, cancelled).")
    filter_incident_status: str | None = Field(default=None, validation_alias="filter[incident_status]", serialization_alias="filter[incident_status]", description="Filter results by the status of the associated incident (e.g., investigating, resolved, monitoring).")
    sort: str | None = Field(default=None, description="Sort results by a specified field and direction (e.g., created_at:desc, priority:asc). Consult API documentation for sortable fields.")
class ListAllIncidentActionItemsRequest(StrictModel):
    """Retrieve all action items for your organization with optional filtering by kind, priority, status, and incident status. Supports pagination and relationship inclusion."""
    query: ListAllIncidentActionItemsRequestQuery | None = None

# Operation: list_incident_event_functionalities
class ListIncidentEventFunctionalitiesRequestPath(StrictModel):
    incident_event_id: str = Field(default=..., description="The unique identifier of the incident event for which to list associated functionalities.")
class ListIncidentEventFunctionalitiesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response for expanded context.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of functionalities to return per page. Adjust this value to control result batch size.")
class ListIncidentEventFunctionalitiesRequest(StrictModel):
    """Retrieve a list of functionalities associated with a specific incident event. Use pagination parameters to control result size and navigation."""
    path: ListIncidentEventFunctionalitiesRequestPath
    query: ListIncidentEventFunctionalitiesRequestQuery | None = None

# Operation: add_functionality_to_incident_event
class CreateIncidentEventFunctionalityRequestPath(StrictModel):
    incident_event_id: str = Field(default=..., description="The unique identifier of the incident event to which the functionality will be added.")
class CreateIncidentEventFunctionalityRequestBodyDataAttributes(StrictModel):
    incident_event_id: str = Field(default=..., validation_alias="incident_event_id", serialization_alias="incident_event_id", description="The unique identifier of the incident event being referenced in the request body (must match the incident_event_id in the path).")
    functionality_id: str = Field(default=..., validation_alias="functionality_id", serialization_alias="functionality_id", description="The unique identifier of the functionality being associated with this incident event.")
    status: Literal["operational", "partial_outage", "major_outage"] = Field(default=..., validation_alias="status", serialization_alias="status", description="The current operational status of the affected functionality. Must be one of: operational (functioning normally), partial_outage (degraded performance), or major_outage (completely unavailable).")
class CreateIncidentEventFunctionalityRequestBodyData(StrictModel):
    type_: Literal["incident_event_functionalities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incident_event_functionalities' to indicate this is an incident event functionality resource.")
    attributes: CreateIncidentEventFunctionalityRequestBodyDataAttributes
class CreateIncidentEventFunctionalityRequestBody(StrictModel):
    data: CreateIncidentEventFunctionalityRequestBodyData
class CreateIncidentEventFunctionalityRequest(StrictModel):
    """Associates a functionality with an incident event and sets its operational status. Use this to track which functionalities are affected by an incident and their current impact level."""
    path: CreateIncidentEventFunctionalityRequestPath
    body: CreateIncidentEventFunctionalityRequestBody

# Operation: get_incident_event_functionality
class GetIncidentEventFunctionalitiesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event functionality to retrieve.")
class GetIncidentEventFunctionalitiesRequest(StrictModel):
    """Retrieves a specific incident event functionality by its unique identifier. Use this to fetch detailed information about a particular functionality associated with incident events."""
    path: GetIncidentEventFunctionalitiesRequestPath

# Operation: update_incident_event_functionality
class UpdateIncidentEventFunctionalityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event functionality to update.")
class UpdateIncidentEventFunctionalityRequestBodyDataAttributes(StrictModel):
    status: Literal["operational", "partial_outage", "major_outage"] = Field(default=..., validation_alias="status", serialization_alias="status", description="The current operational status of the affected functionality. Must be one of: 'operational' (fully functional), 'partial_outage' (degraded service), or 'major_outage' (service unavailable).")
class UpdateIncidentEventFunctionalityRequestBodyData(StrictModel):
    type_: Literal["incident_event_functionalities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incident_event_functionalities' to specify the type of resource being updated.")
    attributes: UpdateIncidentEventFunctionalityRequestBodyDataAttributes
class UpdateIncidentEventFunctionalityRequestBody(StrictModel):
    data: UpdateIncidentEventFunctionalityRequestBodyData
class UpdateIncidentEventFunctionalityRequest(StrictModel):
    """Update the status of a specific incident event functionality. Use this to report changes in the operational status of affected services or features during an incident."""
    path: UpdateIncidentEventFunctionalityRequestPath
    body: UpdateIncidentEventFunctionalityRequestBody

# Operation: delete_incident_event_functionality
class DeleteIncidentEventFunctionalityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event functionality to delete.")
class DeleteIncidentEventFunctionalityRequest(StrictModel):
    """Permanently delete a specific incident event functionality by its unique identifier. This action cannot be undone."""
    path: DeleteIncidentEventFunctionalityRequestPath

# Operation: list_incident_event_services
class ListIncidentEventServicesRequestPath(StrictModel):
    incident_event_id: str = Field(default=..., description="The unique identifier of the incident event for which to list associated services.")
class ListIncidentEventServicesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., service details, metadata). Specify which associations to expand for richer context.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of services to return per page. Adjust this value to control result set size for pagination.")
class ListIncidentEventServicesRequest(StrictModel):
    """Retrieve a list of services associated with a specific incident event. Use pagination parameters to control result set size and navigation."""
    path: ListIncidentEventServicesRequestPath
    query: ListIncidentEventServicesRequestQuery | None = None

# Operation: add_service_to_incident_event
class CreateIncidentEventServiceRequestPath(StrictModel):
    incident_event_id: str = Field(default=..., description="The unique identifier of the incident event to which the service will be added.")
class CreateIncidentEventServiceRequestBodyDataAttributes(StrictModel):
    incident_event_id: str = Field(default=..., validation_alias="incident_event_id", serialization_alias="incident_event_id", description="The unique identifier of the incident event being referenced in the request body (must match the incident_event_id in the path).")
    service_id: str = Field(default=..., validation_alias="service_id", serialization_alias="service_id", description="The unique identifier of the service to be associated with this incident event.")
    status: Literal["operational", "partial_outage", "major_outage"] = Field(default=..., validation_alias="status", serialization_alias="status", description="The operational status of the affected service. Must be one of: operational (service functioning normally), partial_outage (service experiencing degraded performance), or major_outage (service unavailable).")
class CreateIncidentEventServiceRequestBodyData(StrictModel):
    type_: Literal["incident_event_services"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incident_event_services' to indicate this is an incident event service resource.")
    attributes: CreateIncidentEventServiceRequestBodyDataAttributes
class CreateIncidentEventServiceRequestBody(StrictModel):
    data: CreateIncidentEventServiceRequestBodyData
class CreateIncidentEventServiceRequest(StrictModel):
    """Associates a service with an incident event and sets its operational status. Use this to track which services are affected by an incident and their current status."""
    path: CreateIncidentEventServiceRequestPath
    body: CreateIncidentEventServiceRequestBody

# Operation: get_incident_event_service
class GetIncidentEventServicesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event service to retrieve.")
class GetIncidentEventServicesRequest(StrictModel):
    """Retrieves a specific incident event service by its unique identifier. Use this to fetch detailed information about a single incident event service."""
    path: GetIncidentEventServicesRequestPath

# Operation: update_incident_event_service_status
class UpdateIncidentEventServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event service to update.")
class UpdateIncidentEventServiceRequestBodyDataAttributes(StrictModel):
    status: Literal["operational", "partial_outage", "major_outage"] = Field(default=..., validation_alias="status", serialization_alias="status", description="The current operational status of the affected service. Choose from: operational (service running normally), partial_outage (service degraded or partially unavailable), or major_outage (service completely unavailable).")
class UpdateIncidentEventServiceRequestBodyData(StrictModel):
    type_: Literal["incident_event_services"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incident_event_services' to specify the type of resource being updated.")
    attributes: UpdateIncidentEventServiceRequestBodyDataAttributes
class UpdateIncidentEventServiceRequestBody(StrictModel):
    data: UpdateIncidentEventServiceRequestBodyData
class UpdateIncidentEventServiceRequest(StrictModel):
    """Update the operational status of a specific incident event service. Use this to reflect the current impact level of a service during an incident."""
    path: UpdateIncidentEventServiceRequestPath
    body: UpdateIncidentEventServiceRequestBody

# Operation: delete_incident_event_service
class DeleteIncidentEventServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event service to delete.")
class DeleteIncidentEventServiceRequest(StrictModel):
    """Permanently delete a specific incident event service by its unique identifier. This action cannot be undone."""
    path: DeleteIncidentEventServiceRequestPath

# Operation: list_incident_events
class ListIncidentEventsRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which to retrieve events.")
class ListIncidentEventsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., user details, attachments). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of events to return per page. Adjust to balance response size and number of requests needed.")
class ListIncidentEventsRequest(StrictModel):
    """Retrieve a paginated list of events associated with a specific incident. Events are ordered chronologically and may include status changes, assignments, comments, and other incident activity."""
    path: ListIncidentEventsRequestPath
    query: ListIncidentEventsRequestQuery | None = None

# Operation: create_incident_event
class CreateIncidentEventRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident to which this event belongs.")
class CreateIncidentEventRequestBodyDataAttributes(StrictModel):
    event: str = Field(default=..., validation_alias="event", serialization_alias="event", description="A concise summary or description of what occurred in this incident event.")
    visibility: Literal["internal", "external"] | None = Field(default=None, validation_alias="visibility", serialization_alias="visibility", description="Controls who can view this event. Set to 'internal' for team-only visibility or 'external' to include external stakeholders. Defaults to internal if not specified.")
class CreateIncidentEventRequestBodyData(StrictModel):
    type_: Literal["incident_events"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of event being created. Must be set to 'incident_events' to classify this as an incident event record.")
    attributes: CreateIncidentEventRequestBodyDataAttributes
class CreateIncidentEventRequestBody(StrictModel):
    data: CreateIncidentEventRequestBodyData
class CreateIncidentEventRequest(StrictModel):
    """Creates a new event record for an incident, capturing event details with optional visibility control. Use this to log incident updates, status changes, or other significant incident occurrences."""
    path: CreateIncidentEventRequestPath
    body: CreateIncidentEventRequestBody

# Operation: get_incident_event
class GetIncidentEventsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event to retrieve.")
class GetIncidentEventsRequest(StrictModel):
    """Retrieves a specific incident event by its unique identifier. Use this to fetch detailed information about a single incident event."""
    path: GetIncidentEventsRequestPath

# Operation: update_incident_event
class UpdateIncidentEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event to update.")
class UpdateIncidentEventRequestBodyDataAttributes(StrictModel):
    event: str | None = Field(default=None, validation_alias="event", serialization_alias="event", description="A brief summary or title describing the incident event.")
    visibility: Literal["internal", "external"] | None = Field(default=None, validation_alias="visibility", serialization_alias="visibility", description="Controls who can view this incident event. Set to 'internal' for restricted visibility or 'external' for broader access.")
class UpdateIncidentEventRequestBodyData(StrictModel):
    type_: Literal["incident_events"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'incident_events' to identify this as an incident event resource.")
    attributes: UpdateIncidentEventRequestBodyDataAttributes | None = None
class UpdateIncidentEventRequestBody(StrictModel):
    data: UpdateIncidentEventRequestBodyData
class UpdateIncidentEventRequest(StrictModel):
    """Update a specific incident event by its ID. Modify the event summary and/or visibility settings for an existing incident event."""
    path: UpdateIncidentEventRequestPath
    body: UpdateIncidentEventRequestBody

# Operation: delete_incident_event
class DeleteIncidentEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident event to delete.")
class DeleteIncidentEventRequest(StrictModel):
    """Permanently delete a specific incident event by its unique identifier. This action cannot be undone."""
    path: DeleteIncidentEventRequestPath

# Operation: list_incident_feedbacks
class ListIncidentFeedbacksRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which to retrieve feedbacks.")
class ListIncidentFeedbacksRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., user details, metadata). Specify which associations should be expanded in the results.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for paginated results, starting from page 1. Use this to navigate through multiple pages of feedbacks.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The maximum number of feedback records to return per page. Controls the size of each paginated result set.")
class ListIncidentFeedbacksRequest(StrictModel):
    """Retrieve a paginated list of feedback entries associated with a specific incident. Use pagination parameters to control result size and navigate through feedback records."""
    path: ListIncidentFeedbacksRequestPath
    query: ListIncidentFeedbacksRequestQuery | None = None

# Operation: create_incident_feedback
class CreateIncidentFeedbackRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which feedback is being submitted.")
class CreateIncidentFeedbackRequestBodyDataAttributes(StrictModel):
    feedback: str = Field(default=..., validation_alias="feedback", serialization_alias="feedback", description="The feedback content describing the user's comments or observations about the incident.")
    rating: Literal[4, 3, 2, 1, 0] = Field(default=..., validation_alias="rating", serialization_alias="rating", description="A numeric rating for the incident on a scale of 0 to 4, where 0 is the lowest and 4 is the highest.")
    anonymous: bool | None = Field(default=None, validation_alias="anonymous", serialization_alias="anonymous", description="Whether the feedback should be submitted anonymously, hiding the identity of the person providing it.")
class CreateIncidentFeedbackRequestBodyData(StrictModel):
    type_: Literal["incident_feedbacks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of feedback being submitted. Must be set to 'incident_feedbacks' to classify this as incident feedback.")
    attributes: CreateIncidentFeedbackRequestBodyDataAttributes
class CreateIncidentFeedbackRequestBody(StrictModel):
    data: CreateIncidentFeedbackRequestBodyData
class CreateIncidentFeedbackRequest(StrictModel):
    """Submit feedback for an incident with a rating and optional anonymity. This allows users to provide structured feedback on incident handling and resolution."""
    path: CreateIncidentFeedbackRequestPath
    body: CreateIncidentFeedbackRequestBody

# Operation: get_incident_feedback
class GetIncidentFeedbacksRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident feedback to retrieve.")
class GetIncidentFeedbacksRequest(StrictModel):
    """Retrieves a specific incident feedback by its unique identifier. Use this to fetch detailed information about a single feedback entry associated with an incident."""
    path: GetIncidentFeedbacksRequestPath

# Operation: update_incident_feedback
class UpdateIncidentFeedbackRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident feedback to update.")
class UpdateIncidentFeedbackRequestBodyDataAttributes(StrictModel):
    feedback: str | None = Field(default=None, validation_alias="feedback", serialization_alias="feedback", description="The feedback text or comment describing the incident experience. Optional field that can be updated independently.")
    rating: Literal[4, 3, 2, 1, 0] | None = Field(default=None, validation_alias="rating", serialization_alias="rating", description="A numeric rating for the incident feedback on a scale from 0 to 4, where 0 is the lowest and 4 is the highest. Optional field that can be updated independently.")
    anonymous: bool | None = Field(default=None, validation_alias="anonymous", serialization_alias="anonymous", description="A boolean flag indicating whether the feedback should be submitted anonymously. When true, the feedback is not attributed to a specific user. Optional field that can be updated independently.")
class UpdateIncidentFeedbackRequestBodyData(StrictModel):
    type_: Literal["incident_feedbacks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'incident_feedbacks' to specify this is an incident feedback resource.")
    attributes: UpdateIncidentFeedbackRequestBodyDataAttributes | None = None
class UpdateIncidentFeedbackRequestBody(StrictModel):
    data: UpdateIncidentFeedbackRequestBodyData
class UpdateIncidentFeedbackRequest(StrictModel):
    """Update an existing incident feedback record by its ID. Modify the feedback text, rating, or anonymity status of a previously submitted incident feedback."""
    path: UpdateIncidentFeedbackRequestPath
    body: UpdateIncidentFeedbackRequestBody

# Operation: list_incident_form_field_selections
class ListIncidentFormFieldSelectionsRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which to retrieve form field selections.")
class ListIncidentFormFieldSelectionsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., field definitions, metadata). Specify which associations should be populated.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results to return per page. Defines the maximum number of form field selections in each paginated response.")
class ListIncidentFormFieldSelectionsRequest(StrictModel):
    """Retrieve all form field selections associated with a specific incident. This lists the custom form fields and their selected values for the incident."""
    path: ListIncidentFormFieldSelectionsRequestPath
    query: ListIncidentFormFieldSelectionsRequestQuery | None = None

# Operation: create_incident_form_field_selection
class CreateIncidentFormFieldSelectionRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident to which this form field selection will be added.")
class CreateIncidentFormFieldSelectionRequestBodyDataAttributes(StrictModel):
    incident_id: str = Field(default=..., validation_alias="incident_id", serialization_alias="incident_id", description="The incident ID associated with this form field selection; must match the incident_id in the URL path.")
    form_field_id: str = Field(default=..., validation_alias="form_field_id", serialization_alias="form_field_id", description="The ID of the custom form field being configured for this incident.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The text value to assign to this form field selection; used for text-based custom fields.")
    selected_catalog_entity_ids: list[str] | None = Field(default=None, validation_alias="selected_catalog_entity_ids", serialization_alias="selected_catalog_entity_ids", description="An array of catalog entity IDs to associate with this form field selection; order may be significant depending on field configuration.")
    selected_group_ids: list[str] | None = Field(default=None, validation_alias="selected_group_ids", serialization_alias="selected_group_ids", description="An array of group IDs to associate with this form field selection; order may be significant depending on field configuration.")
    selected_option_ids: list[str] | None = Field(default=None, validation_alias="selected_option_ids", serialization_alias="selected_option_ids", description="An array of custom field option IDs to associate with this form field selection; order may be significant depending on field configuration.")
    selected_service_ids: list[str] | None = Field(default=None, validation_alias="selected_service_ids", serialization_alias="selected_service_ids", description="An array of service IDs to associate with this form field selection; order may be significant depending on field configuration.")
    selected_functionality_ids: list[str] | None = Field(default=None, validation_alias="selected_functionality_ids", serialization_alias="selected_functionality_ids", description="An array of functionality IDs to associate with this form field selection; order may be significant depending on field configuration.")
    selected_user_ids: list[int] | None = Field(default=None, validation_alias="selected_user_ids", serialization_alias="selected_user_ids", description="An array of user IDs to associate with this form field selection; order may be significant depending on field configuration.")
class CreateIncidentFormFieldSelectionRequestBodyData(StrictModel):
    type_: Literal["incident_form_field_selections"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'incident_form_field_selections'.")
    attributes: CreateIncidentFormFieldSelectionRequestBodyDataAttributes
class CreateIncidentFormFieldSelectionRequestBody(StrictModel):
    data: CreateIncidentFormFieldSelectionRequestBodyData
class CreateIncidentFormFieldSelectionRequest(StrictModel):
    """Creates a new form field selection for an incident, allowing you to assign values to custom fields such as text inputs, catalog entities, groups, options, services, functionalities, or users."""
    path: CreateIncidentFormFieldSelectionRequestPath
    body: CreateIncidentFormFieldSelectionRequestBody

# Operation: get_incident_form_field_selection
class GetIncidentFormFieldSelectionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident form field selection to retrieve.")
class GetIncidentFormFieldSelectionRequest(StrictModel):
    """Retrieves a specific incident form field selection by its unique identifier. Use this to fetch configuration details for how form fields are selected and displayed in incident reports."""
    path: GetIncidentFormFieldSelectionRequestPath

# Operation: list_incident_post_mortems
class ListIncidentPostMortemsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., incident details, user information).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of post-mortems to return per page.")
    filter_status: str | None = Field(default=None, validation_alias="filter[status]", serialization_alias="filter[status]", description="Filter results by post-mortem status (e.g., draft, published, archived).")
    filter_type: str | None = Field(default=None, validation_alias="filter[type]", serialization_alias="filter[type]", description="Filter results by incident type classification.")
    filter_user_id: int | None = Field(default=None, validation_alias="filter[user_id]", serialization_alias="filter[user_id]", description="Filter results to post-mortems created by a specific user ID.")
    filter_started_at__gte: str | None = Field(default=None, validation_alias="filter[started_at][gte]", serialization_alias="filter[started_at][gte]", description="Filter to post-mortems with incident start time greater than or equal to this timestamp (ISO 8601 format).")
    filter_started_at__lte: str | None = Field(default=None, validation_alias="filter[started_at][lte]", serialization_alias="filter[started_at][lte]", description="Filter to post-mortems with incident start time less than or equal to this timestamp (ISO 8601 format).")
    filter_mitigated_at__gte: str | None = Field(default=None, validation_alias="filter[mitigated_at][gte]", serialization_alias="filter[mitigated_at][gte]", description="Filter to post-mortems with mitigation time greater than or equal to this timestamp (ISO 8601 format).")
    filter_mitigated_at__lte: str | None = Field(default=None, validation_alias="filter[mitigated_at][lte]", serialization_alias="filter[mitigated_at][lte]", description="Filter to post-mortems with mitigation time less than or equal to this timestamp (ISO 8601 format).")
    filter_resolved_at__gte: str | None = Field(default=None, validation_alias="filter[resolved_at][gte]", serialization_alias="filter[resolved_at][gte]", description="Filter to post-mortems with resolution time greater than or equal to this timestamp (ISO 8601 format).")
    filter_resolved_at__lte: str | None = Field(default=None, validation_alias="filter[resolved_at][lte]", serialization_alias="filter[resolved_at][lte]", description="Filter to post-mortems with resolution time less than or equal to this timestamp (ISO 8601 format).")
    sort: str | None = Field(default=None, description="Sort results by a specified field in ascending or descending order (e.g., created_at, status).")
class ListIncidentPostMortemsRequest(StrictModel):
    """Retrieve a paginated list of incident post-mortems (retrospectives) with optional filtering by status, type, user, and date ranges, plus sorting capabilities."""
    query: ListIncidentPostMortemsRequestQuery | None = None

# Operation: get_incident_postmortem
class ListIncidentPostmortemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident postmortem to retrieve.")
class ListIncidentPostmortemRequest(StrictModel):
    """Retrieves a detailed incident postmortem (retrospective) by its unique identifier. Use this to access the analysis and findings from a completed incident investigation."""
    path: ListIncidentPostmortemRequestPath

# Operation: update_incident_postmortem
class UpdateIncidentPostmortemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident postmortem to update.")
class UpdateIncidentPostmortemRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The title or heading of the incident postmortem document.")
    status: Literal["draft", "published"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The publication state of the postmortem; either 'draft' for work-in-progress or 'published' for finalized versions.")
    show_timeline: bool | None = Field(default=None, validation_alias="show_timeline", serialization_alias="show_timeline", description="Whether to display the timeline of events in the postmortem.")
    show_timeline_trail: bool | None = Field(default=None, validation_alias="show_timeline_trail", serialization_alias="show_timeline_trail", description="Whether to include trail events (audit/change history) in the timeline view.")
    show_timeline_genius: bool | None = Field(default=None, validation_alias="show_timeline_genius", serialization_alias="show_timeline_genius", description="Whether to include workflow or automation events in the timeline view.")
    show_timeline_tasks: bool | None = Field(default=None, validation_alias="show_timeline_tasks", serialization_alias="show_timeline_tasks", description="Whether to include task entries in the timeline view.")
    show_timeline_action_items: bool | None = Field(default=None, validation_alias="show_timeline_action_items", serialization_alias="show_timeline_action_items", description="Whether to include action items and follow-ups in the timeline view.")
    show_groups_impacted: bool | None = Field(default=None, validation_alias="show_groups_impacted", serialization_alias="show_groups_impacted", description="Whether to display information about affected groups or services in the postmortem.")
    show_alerts_attached: bool | None = Field(default=None, validation_alias="show_alerts_attached", serialization_alias="show_alerts_attached", description="Whether to display alerts that were attached to or triggered during the incident.")
    show_action_items: bool | None = Field(default=None, validation_alias="show_action_items", serialization_alias="show_action_items", description="Whether to include action items and follow-up tasks in the postmortem document.")
    cause_ids: list[str] | None = Field(default=None, validation_alias="cause_ids", serialization_alias="cause_ids", description="A list of cause identifiers to associate with this incident postmortem, linking root causes to the incident.")
class UpdateIncidentPostmortemRequestBodyData(StrictModel):
    type_: Literal["incident_post_mortems"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'incident_post_mortems'.")
    attributes: UpdateIncidentPostmortemRequestBodyDataAttributes | None = None
class UpdateIncidentPostmortemRequestBody(StrictModel):
    data: UpdateIncidentPostmortemRequestBodyData
class UpdateIncidentPostmortemRequest(StrictModel):
    """Update an incident postmortem document by ID, allowing modifications to its content, visibility settings, and associated metadata. Use this to refine postmortem details, change publication status, or adjust which timeline elements and impact information are displayed."""
    path: UpdateIncidentPostmortemRequestPath
    body: UpdateIncidentPostmortemRequestBody

# Operation: get_incident_retrospective_step
class GetIncidentRetrospectiveStepRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident retrospective step to retrieve.")
class GetIncidentRetrospectiveStepRequest(StrictModel):
    """Retrieves a specific incident retrospective step by its unique identifier. Use this to fetch details about a particular step within an incident retrospective."""
    path: GetIncidentRetrospectiveStepRequestPath

# Operation: update_incident_retrospective_step
class UpdateIncidentRetrospectiveStepRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident retrospective step to update.")
class UpdateIncidentRetrospectiveStepRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The name or title of the retrospective step.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the retrospective step and its purpose.")
    due_date: str | None = Field(default=None, validation_alias="due_date", serialization_alias="due_date", description="The target completion date for this step, specified in ISO 8601 format.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this step within the retrospective sequence, where lower numbers appear first.")
    skippable: bool | None = Field(default=None, validation_alias="skippable", serialization_alias="skippable", description="Whether this step can be skipped during the retrospective process without blocking completion.")
    status: Literal["todo", "in_progress", "completed", "skipped"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current state of the step: 'todo' (not started), 'in_progress' (actively being worked on), 'completed' (finished), or 'skipped' (bypassed).")
class UpdateIncidentRetrospectiveStepRequestBodyData(StrictModel):
    type_: Literal["incident_retrospective_steps"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'incident_retrospective_steps' to specify the entity being updated.")
    attributes: UpdateIncidentRetrospectiveStepRequestBodyDataAttributes | None = None
class UpdateIncidentRetrospectiveStepRequestBody(StrictModel):
    data: UpdateIncidentRetrospectiveStepRequestBodyData
class UpdateIncidentRetrospectiveStepRequest(StrictModel):
    """Update a specific incident retrospective step within an incident retrospective. Modify step details such as title, description, due date, position, and completion status."""
    path: UpdateIncidentRetrospectiveStepRequestPath
    body: UpdateIncidentRetrospectiveStepRequestBody

# Operation: list_incident_role_tasks
class ListIncidentRoleTasksRequestPath(StrictModel):
    incident_role_id: str = Field(default=..., description="The unique identifier of the incident role for which to list associated tasks.")
class ListIncidentRoleTasksRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., assignees, status details). Reduces need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of tasks to return per page. Adjust to balance response size and number of requests needed.")
class ListIncidentRoleTasksRequest(StrictModel):
    """Retrieve all tasks assigned to a specific incident role. Use pagination to control result size and offset."""
    path: ListIncidentRoleTasksRequestPath
    query: ListIncidentRoleTasksRequestQuery | None = None

# Operation: create_incident_role_task
class CreateIncidentRoleTaskRequestPath(StrictModel):
    incident_role_id: str = Field(default=..., description="The unique identifier of the incident role to which this task will be assigned.")
class CreateIncidentRoleTaskRequestBodyDataAttributes(StrictModel):
    task: str = Field(default=..., validation_alias="task", serialization_alias="task", description="A concise title or description of the work to be completed as part of this incident role task.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Additional context or details about the task, including any relevant background information or acceptance criteria.")
    priority: Literal["high", "medium", "low"] | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="The urgency level of the task. Choose from high, medium, or low priority to help with task sequencing and resource allocation.")
class CreateIncidentRoleTaskRequestBodyData(StrictModel):
    type_: Literal["incident_role_tasks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for incident role tasks. Must be set to 'incident_role_tasks'.")
    attributes: CreateIncidentRoleTaskRequestBodyDataAttributes
class CreateIncidentRoleTaskRequestBody(StrictModel):
    data: CreateIncidentRoleTaskRequestBodyData
class CreateIncidentRoleTaskRequest(StrictModel):
    """Creates a new task within an incident role to track specific work items. Tasks help organize and prioritize actions needed to resolve the incident."""
    path: CreateIncidentRoleTaskRequestPath
    body: CreateIncidentRoleTaskRequestBody

# Operation: get_incident_role_task
class GetIncidentRoleTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident role task to retrieve.")
class GetIncidentRoleTaskRequest(StrictModel):
    """Retrieves a specific incident role task by its unique identifier. Use this to fetch details about a particular task assigned to a role within an incident."""
    path: GetIncidentRoleTaskRequestPath

# Operation: update_incident_role_task
class UpdateIncidentRoleTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident role task to update.")
class UpdateIncidentRoleTaskRequestBodyDataAttributes(StrictModel):
    task: str | None = Field(default=None, validation_alias="task", serialization_alias="task", description="The task name or title for the incident role task.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description providing context and information about the incident role task.")
    priority: Literal["high", "medium", "low"] | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="The priority level for the incident role task: 'high' for urgent items, 'medium' for standard priority, or 'low' for non-urgent items.")
class UpdateIncidentRoleTaskRequestBodyData(StrictModel):
    type_: Literal["incident_role_tasks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'incident_role_tasks' to specify the resource being updated.")
    attributes: UpdateIncidentRoleTaskRequestBodyDataAttributes | None = None
class UpdateIncidentRoleTaskRequestBody(StrictModel):
    data: UpdateIncidentRoleTaskRequestBodyData
class UpdateIncidentRoleTaskRequest(StrictModel):
    """Update an existing incident role task by its ID, allowing modification of task details, description, and priority level."""
    path: UpdateIncidentRoleTaskRequestPath
    body: UpdateIncidentRoleTaskRequestBody

# Operation: delete_incident_role_task
class DeleteIncidentRoleTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident role task to delete.")
class DeleteIncidentRoleTaskRequest(StrictModel):
    """Permanently delete a specific incident role task by its unique identifier. This action cannot be undone."""
    path: DeleteIncidentRoleTaskRequestPath

# Operation: list_incident_roles
class ListIncidentRolesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., permissions, metadata). Specify which associations should be populated alongside each role.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve when paginating through results. Use with page[size] to control pagination.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of incident roles to return per page. Adjust this value to control the size of each paginated response.")
    filter_enabled: bool | None = Field(default=None, validation_alias="filter[enabled]", serialization_alias="filter[enabled]", description="Filter results to show only enabled or disabled incident roles. Set to true for active roles only, or false for inactive roles.")
    sort: str | None = Field(default=None, description="Sort the results by one or more fields (e.g., name, created_at). Prefix field names with a minus sign (-) to sort in descending order.")
class ListIncidentRolesRequest(StrictModel):
    """Retrieve a paginated list of incident roles with optional filtering and sorting capabilities. Use this to view all available roles that can be assigned during incident management."""
    query: ListIncidentRolesRequestQuery | None = None

# Operation: create_incident_role
class CreateIncidentRoleRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the incident role (e.g., 'Incident Commander', 'Communications Lead'). Used to identify the role throughout the incident management system.")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief summary of the incident role's purpose and key responsibilities.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the incident role, including specific duties, authority levels, and escalation procedures.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this role in the incident role hierarchy or display order. Lower numbers typically appear first in lists.")
    optional: bool | None = Field(default=None, validation_alias="optional", serialization_alias="optional", description="Whether this role is optional during incident response. When true, incidents can proceed without assigning someone to this role.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether this role is currently active and available for assignment. Disabled roles cannot be assigned to new incidents.")
    allow_multi_user_assignment: bool | None = Field(default=None, validation_alias="allow_multi_user_assignment", serialization_alias="allow_multi_user_assignment", description="Whether multiple team members can be simultaneously assigned to this role during a single incident. When false, only one person can hold the role at a time.")
class CreateIncidentRoleRequestBodyData(StrictModel):
    type_: Literal["incident_roles"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'incident_roles' to specify this is an incident role resource.")
    attributes: CreateIncidentRoleRequestBodyDataAttributes
class CreateIncidentRoleRequestBody(StrictModel):
    data: CreateIncidentRoleRequestBodyData
class CreateIncidentRoleRequest(StrictModel):
    """Creates a new incident role that can be assigned to team members during incident response. Incident roles define responsibilities and permissions within the incident management workflow."""
    body: CreateIncidentRoleRequestBody

# Operation: get_incident_role
class GetIncidentRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident role to retrieve.")
class GetIncidentRoleRequest(StrictModel):
    """Retrieves a specific incident role by its unique identifier. Use this to fetch detailed information about a particular incident role."""
    path: GetIncidentRoleRequestPath

# Operation: update_incident_role
class UpdateIncidentRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident role to update.")
class UpdateIncidentRoleRequestBodyDataAttributes(StrictModel):
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief summary or title for the incident role.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the incident role's purpose and responsibilities.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this incident role relative to others, used for sorting in user interfaces.")
    optional: bool | None = Field(default=None, validation_alias="optional", serialization_alias="optional", description="Whether this incident role is optional or required when assigning roles to incidents.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether this incident role is currently active and available for use.")
    allow_multi_user_assignment: bool | None = Field(default=None, validation_alias="allow_multi_user_assignment", serialization_alias="allow_multi_user_assignment", description="Whether multiple users can be assigned to this incident role simultaneously.")
class UpdateIncidentRoleRequestBodyData(StrictModel):
    type_: Literal["incident_roles"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incident_roles'.")
    attributes: UpdateIncidentRoleRequestBodyDataAttributes | None = None
class UpdateIncidentRoleRequestBody(StrictModel):
    data: UpdateIncidentRoleRequestBodyData
class UpdateIncidentRoleRequest(StrictModel):
    """Update an existing incident role by its ID, allowing modification of its summary, description, position, and assignment settings."""
    path: UpdateIncidentRoleRequestPath
    body: UpdateIncidentRoleRequestBody

# Operation: delete_incident_role
class DeleteIncidentRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident role to delete.")
class DeleteIncidentRoleRequest(StrictModel):
    """Permanently delete an incident role by its unique identifier. This action cannot be undone."""
    path: DeleteIncidentRoleRequestPath

# Operation: list_incident_status_page_events
class ListIncidentStatusPagesRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which to retrieve status page events.")
class ListIncidentStatusPagesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., incident details, status page information). Specify which associations to expand for richer context.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through results when there are many events.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of events to return per page. Adjust this to control the size of each paginated response.")
class ListIncidentStatusPagesRequest(StrictModel):
    """Retrieve a paginated list of status page events associated with a specific incident. Use this to track all status updates and communications that were published for an incident."""
    path: ListIncidentStatusPagesRequestPath
    query: ListIncidentStatusPagesRequestQuery | None = None

# Operation: create_incident_status_page_event
class CreateIncidentStatusPageRequestPath(StrictModel):
    incident_id: str = Field(default=..., description="The unique identifier of the incident for which you are creating a status page event.")
class CreateIncidentStatusPageRequestBodyDataAttributes(StrictModel):
    event: str = Field(default=..., validation_alias="event", serialization_alias="event", description="A brief summary describing the incident event (e.g., 'Service degradation detected', 'Issue resolved').")
    status_page_id: str | None = Field(default=None, validation_alias="status_page_id", serialization_alias="status_page_id", description="The unique identifier of the status page where this event should be posted. If omitted, the event may be posted to a default status page or require specification elsewhere.")
    status: Literal["investigating", "identified", "monitoring", "resolved", "scheduled", "in_progress", "verifying", "completed"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current status of the incident event. Valid values indicate progression through the incident lifecycle: 'investigating' (initial assessment), 'identified' (root cause found), 'monitoring' (watching for stability), 'resolved' (issue fixed), 'scheduled' (planned maintenance), 'in_progress' (work underway), 'verifying' (confirming fix), or 'completed' (maintenance finished).")
    notify_subscribers: bool | None = Field(default=None, validation_alias="notify_subscribers", serialization_alias="notify_subscribers", description="When enabled, sends notifications to all subscribers of the status page(s) about this incident event. Defaults to false.")
    should_tweet: bool | None = Field(default=None, validation_alias="should_tweet", serialization_alias="should_tweet", description="When enabled on Statuspage.io integrated pages, automatically publishes a tweet announcing this incident update. Defaults to false.")
class CreateIncidentStatusPageRequestBodyData(StrictModel):
    type_: Literal["incident_status_page_events"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of resource being created; must be set to 'incident_status_page_events'.")
    attributes: CreateIncidentStatusPageRequestBodyDataAttributes
class CreateIncidentStatusPageRequestBody(StrictModel):
    data: CreateIncidentStatusPageRequestBodyData
class CreateIncidentStatusPageRequest(StrictModel):
    """Creates a new event for an incident on a status page, allowing you to post updates about incident status to subscribers and optionally publish to social media."""
    path: CreateIncidentStatusPageRequestPath
    body: CreateIncidentStatusPageRequestBody

# Operation: get_incident_status_page_event
class GetIncidentStatusPagesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident status page event to retrieve.")
class GetIncidentStatusPagesRequest(StrictModel):
    """Retrieves a specific incident status page event by its unique identifier. Use this to fetch detailed information about a particular status page event associated with an incident."""
    path: GetIncidentStatusPagesRequestPath

# Operation: update_incident_status_page_event
class UpdateIncidentStatusPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident status page event to update.")
class UpdateIncidentStatusPageRequestBodyDataAttributes(StrictModel):
    event: str | None = Field(default=None, validation_alias="event", serialization_alias="event", description="A brief summary describing the incident event (e.g., 'Database connection timeout', 'Service degradation resolved').")
    status_page_id: str | None = Field(default=None, validation_alias="status_page_id", serialization_alias="status_page_id", description="The unique identifier of the status page where this event should be posted or updated.")
    status: Literal["investigating", "identified", "monitoring", "resolved", "scheduled", "in_progress", "verifying", "completed"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current phase of the incident: 'investigating' (initial assessment), 'identified' (root cause found), 'monitoring' (fix in progress), 'resolved' (issue fixed), 'scheduled' (planned maintenance), 'in_progress' (maintenance underway), 'verifying' (validating fix), or 'completed' (maintenance finished).")
    notify_subscribers: bool | None = Field(default=None, validation_alias="notify_subscribers", serialization_alias="notify_subscribers", description="When enabled, sends notifications to all subscribers of the status page(s) about this incident update. Defaults to false.")
    should_tweet: bool | None = Field(default=None, validation_alias="should_tweet", serialization_alias="should_tweet", description="When enabled on Statuspage.io integrated pages, automatically publishes a tweet announcing this incident update. Defaults to false.")
class UpdateIncidentStatusPageRequestBodyData(StrictModel):
    type_: Literal["incident_status_page_events"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'incident_status_page_events' to specify the event resource being updated.")
    attributes: UpdateIncidentStatusPageRequestBodyDataAttributes | None = None
class UpdateIncidentStatusPageRequestBody(StrictModel):
    data: UpdateIncidentStatusPageRequestBodyData
class UpdateIncidentStatusPageRequest(StrictModel):
    """Update a specific incident status page event to modify its summary, status, and notification settings. Use this to track incident progression through investigation, identification, monitoring, and resolution phases."""
    path: UpdateIncidentStatusPageRequestPath
    body: UpdateIncidentStatusPageRequestBody

# Operation: delete_status_page_event
class DeleteIncidentStatusPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page event to delete.")
class DeleteIncidentStatusPageRequest(StrictModel):
    """Delete a specific incident status page event. This removes the event record from the status page."""
    path: DeleteIncidentStatusPageRequestPath

# Operation: list_incident_types
class ListIncidentTypesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related fields to include in the response (e.g., metadata, categories). Specify which associations should be expanded in the returned incident type objects.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to control result set boundaries.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of incident types to return per page. Defines the maximum number of results in each paginated response.")
    filter_color: str | None = Field(default=None, validation_alias="filter[color]", serialization_alias="filter[color]", description="Filter incident types by color value. Specify the exact color identifier or name to narrow results to matching incident types.")
    sort: str | None = Field(default=None, description="Comma-separated list of fields to sort by, with optional direction indicators (e.g., 'name,-created_at'). Controls the order of returned incident types.")
class ListIncidentTypesRequest(StrictModel):
    """Retrieve a paginated list of incident types, optionally filtered by color and sorted by specified fields."""
    query: ListIncidentTypesRequestQuery | None = None

# Operation: create_incident_type
class CreateIncidentTypeRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the incident type; used to identify and reference this type throughout the system.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation of the incident type's purpose and usage; helps users understand when to apply this type.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hexadecimal color code (e.g., #FF5733) used to visually distinguish this incident type in the UI.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this incident type relative to others; lower numbers appear first in lists and menus.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="A list of email addresses that will receive notifications when incidents of this type are created or updated.")
    slack_channels: list[CreateIncidentTypeBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="A list of Slack channel identifiers or names where incident notifications will be posted for this type.")
    slack_aliases: list[CreateIncidentTypeBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="A list of Slack aliases or shortcuts that can be used to quickly reference or create incidents of this type.")
class CreateIncidentTypeRequestBodyData(StrictModel):
    type_: Literal["incident_types"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'incident_types' to specify this is an incident type resource.")
    attributes: CreateIncidentTypeRequestBodyDataAttributes
class CreateIncidentTypeRequestBody(StrictModel):
    data: CreateIncidentTypeRequestBodyData
class CreateIncidentTypeRequest(StrictModel):
    """Creates a new incident type that can be used to categorize and manage incidents. Incident types support custom naming, visual styling, notifications, and Slack integration."""
    body: CreateIncidentTypeRequestBody

# Operation: get_incident_type
class GetIncidentTypeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident type to retrieve.")
class GetIncidentTypeRequest(StrictModel):
    """Retrieves a specific incident type by its unique identifier. Use this to fetch detailed information about a particular incident type configuration."""
    path: GetIncidentTypeRequestPath

# Operation: update_incident_type
class UpdateIncidentTypeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident type to update.")
class UpdateIncidentTypeRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the incident type and its purpose.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The hex color code used to visually represent this incident type in the UI.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this incident type in lists and menus, where lower numbers appear first.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="A list of email addresses that should receive notifications when incidents of this type are created or updated.")
    slack_channels: list[UpdateIncidentTypeBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="A list of Slack channel identifiers or names where incident notifications should be posted.")
    slack_aliases: list[UpdateIncidentTypeBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="A list of Slack user aliases or handles to mention or notify when incidents of this type occur.")
class UpdateIncidentTypeRequestBodyData(StrictModel):
    type_: Literal["incident_types"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incident_types'.")
    attributes: UpdateIncidentTypeRequestBodyDataAttributes | None = None
class UpdateIncidentTypeRequestBody(StrictModel):
    data: UpdateIncidentTypeRequestBodyData
class UpdateIncidentTypeRequest(StrictModel):
    """Update an existing incident type by its ID, allowing modification of its display properties, notification settings, and associated Slack integrations."""
    path: UpdateIncidentTypeRequestPath
    body: UpdateIncidentTypeRequestBody

# Operation: delete_incident_type
class DeleteIncidentTypeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident type to delete.")
class DeleteIncidentTypeRequest(StrictModel):
    """Permanently delete an incident type by its unique identifier. This action cannot be undone and will remove the incident type from the system."""
    path: DeleteIncidentTypeRequestPath

# Operation: list_incidents
class ListIncidentsRequestQuery(StrictModel):
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination (1-indexed). Use with page[size] to retrieve specific result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of incidents per page. Determines the size of each paginated result set.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter by incident kind (e.g., alert, event, anomaly). Narrows results to specific incident types.")
    filter_status: str | None = Field(default=None, validation_alias="filter[status]", serialization_alias="filter[status]", description="Filter by incident status (e.g., open, acknowledged, resolved, closed). Returns incidents matching the specified status.")
    filter_private: str | None = Field(default=None, validation_alias="filter[private]", serialization_alias="filter[private]", description="Filter by privacy setting. Use to show only private or public incidents.")
    filter_user_id: int | None = Field(default=None, validation_alias="filter[user_id]", serialization_alias="filter[user_id]", description="Filter by user ID. Returns incidents assigned to or created by the specified user.")
    filter_severity_id: str | None = Field(default=None, validation_alias="filter[severity_id]", serialization_alias="filter[severity_id]", description="Filter by severity ID. Narrows results to incidents with the specified severity level.")
    filter_labels: str | None = Field(default=None, validation_alias="filter[labels]", serialization_alias="filter[labels]", description="Filter by labels. Comma-separated list of label identifiers to match incidents with those labels.")
    filter_type_ids: str | None = Field(default=None, validation_alias="filter[type_ids]", serialization_alias="filter[type_ids]", description="Filter by incident type IDs. Comma-separated list of type identifiers to match specific incident types.")
    filter_environment_ids: str | None = Field(default=None, validation_alias="filter[environment_ids]", serialization_alias="filter[environment_ids]", description="Filter by environment IDs. Comma-separated list of environment identifiers (e.g., production, staging).")
    filter_functionality_ids: str | None = Field(default=None, validation_alias="filter[functionality_ids]", serialization_alias="filter[functionality_ids]", description="Filter by functionality IDs. Comma-separated list of functionality identifiers affected by incidents.")
    filter_service_ids: str | None = Field(default=None, validation_alias="filter[service_ids]", serialization_alias="filter[service_ids]", description="Filter by service IDs. Comma-separated list of service identifiers to match incidents affecting those services.")
    filter_team_ids: str | None = Field(default=None, validation_alias="filter[team_ids]", serialization_alias="filter[team_ids]", description="Filter by team IDs. Comma-separated list of team identifiers responsible for or assigned to incidents.")
    filter_cause_ids: str | None = Field(default=None, validation_alias="filter[cause_ids]", serialization_alias="filter[cause_ids]", description="Filter by cause IDs. Comma-separated list of cause identifiers to match incidents with those root causes.")
    filter_custom_field_selected_option_ids: str | None = Field(default=None, validation_alias="filter[custom_field_selected_option_ids]", serialization_alias="filter[custom_field_selected_option_ids]", description="Filter by custom field selected option IDs. Comma-separated list of custom field option identifiers.")
    filter_updated_at__gt: str | None = Field(default=None, validation_alias="filter[updated_at][gt]", serialization_alias="filter[updated_at][gt]", description="Filter incidents updated after this timestamp (ISO 8601 format). Exclusive lower bound.")
    filter_updated_at__gte: str | None = Field(default=None, validation_alias="filter[updated_at][gte]", serialization_alias="filter[updated_at][gte]", description="Filter incidents updated on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_updated_at__lt: str | None = Field(default=None, validation_alias="filter[updated_at][lt]", serialization_alias="filter[updated_at][lt]", description="Filter incidents updated before this timestamp (ISO 8601 format). Exclusive upper bound.")
    filter_updated_at__lte: str | None = Field(default=None, validation_alias="filter[updated_at][lte]", serialization_alias="filter[updated_at][lte]", description="Filter incidents updated on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_started_at__gte: str | None = Field(default=None, validation_alias="filter[started_at][gte]", serialization_alias="filter[started_at][gte]", description="Filter incidents that started on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_started_at__lte: str | None = Field(default=None, validation_alias="filter[started_at][lte]", serialization_alias="filter[started_at][lte]", description="Filter incidents that started on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_detected_at__gt: str | None = Field(default=None, validation_alias="filter[detected_at][gt]", serialization_alias="filter[detected_at][gt]", description="Filter incidents detected after this timestamp (ISO 8601 format). Exclusive lower bound.")
    filter_detected_at__gte: str | None = Field(default=None, validation_alias="filter[detected_at][gte]", serialization_alias="filter[detected_at][gte]", description="Filter incidents detected on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_detected_at__lt: str | None = Field(default=None, validation_alias="filter[detected_at][lt]", serialization_alias="filter[detected_at][lt]", description="Filter incidents detected before this timestamp (ISO 8601 format). Exclusive upper bound.")
    filter_detected_at__lte: str | None = Field(default=None, validation_alias="filter[detected_at][lte]", serialization_alias="filter[detected_at][lte]", description="Filter incidents detected on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_acknowledged_at__gt: str | None = Field(default=None, validation_alias="filter[acknowledged_at][gt]", serialization_alias="filter[acknowledged_at][gt]", description="Filter incidents acknowledged after this timestamp (ISO 8601 format). Exclusive lower bound.")
    filter_acknowledged_at__gte: str | None = Field(default=None, validation_alias="filter[acknowledged_at][gte]", serialization_alias="filter[acknowledged_at][gte]", description="Filter incidents acknowledged on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_acknowledged_at__lt: str | None = Field(default=None, validation_alias="filter[acknowledged_at][lt]", serialization_alias="filter[acknowledged_at][lt]", description="Filter incidents acknowledged before this timestamp (ISO 8601 format). Exclusive upper bound.")
    filter_acknowledged_at__lte: str | None = Field(default=None, validation_alias="filter[acknowledged_at][lte]", serialization_alias="filter[acknowledged_at][lte]", description="Filter incidents acknowledged on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_mitigated_at__gte: str | None = Field(default=None, validation_alias="filter[mitigated_at][gte]", serialization_alias="filter[mitigated_at][gte]", description="Filter incidents mitigated on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_mitigated_at__lte: str | None = Field(default=None, validation_alias="filter[mitigated_at][lte]", serialization_alias="filter[mitigated_at][lte]", description="Filter incidents mitigated on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_resolved_at__gte: str | None = Field(default=None, validation_alias="filter[resolved_at][gte]", serialization_alias="filter[resolved_at][gte]", description="Filter incidents resolved on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_resolved_at__lte: str | None = Field(default=None, validation_alias="filter[resolved_at][lte]", serialization_alias="filter[resolved_at][lte]", description="Filter incidents resolved on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_closed_at__gt: str | None = Field(default=None, validation_alias="filter[closed_at][gt]", serialization_alias="filter[closed_at][gt]", description="Filter incidents closed after this timestamp (ISO 8601 format). Exclusive lower bound.")
    filter_closed_at__gte: str | None = Field(default=None, validation_alias="filter[closed_at][gte]", serialization_alias="filter[closed_at][gte]", description="Filter incidents closed on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_closed_at__lt: str | None = Field(default=None, validation_alias="filter[closed_at][lt]", serialization_alias="filter[closed_at][lt]", description="Filter incidents closed before this timestamp (ISO 8601 format). Exclusive upper bound.")
    filter_closed_at__lte: str | None = Field(default=None, validation_alias="filter[closed_at][lte]", serialization_alias="filter[closed_at][lte]", description="Filter incidents closed on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    filter_in_triage_at__gt: str | None = Field(default=None, validation_alias="filter[in_triage_at][gt]", serialization_alias="filter[in_triage_at][gt]", description="Filter incidents entered triage after this timestamp (ISO 8601 format). Exclusive lower bound.")
    filter_in_triage_at__gte: str | None = Field(default=None, validation_alias="filter[in_triage_at][gte]", serialization_alias="filter[in_triage_at][gte]", description="Filter incidents entered triage on or after this timestamp (ISO 8601 format). Inclusive lower bound.")
    filter_in_triage_at__lt: str | None = Field(default=None, validation_alias="filter[in_triage_at][lt]", serialization_alias="filter[in_triage_at][lt]", description="Filter incidents entered triage before this timestamp (ISO 8601 format). Exclusive upper bound.")
    filter_in_triage_at__lte: str | None = Field(default=None, validation_alias="filter[in_triage_at][lte]", serialization_alias="filter[in_triage_at][lte]", description="Filter incidents entered triage on or before this timestamp (ISO 8601 format). Inclusive upper bound.")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Field(default=None, description="Sort results by one or more fields. Prefix with hyphen (-) for descending order. Valid fields: created_at, updated_at.")
    include: Literal["sub_statuses", "causes", "subscribers", "roles", "slack_messages", "environments", "incident_types", "services", "functionalities", "groups", "events", "action_items", "custom_field_selections", "feedbacks", "incident_post_mortem"] | None = Field(default=None, description="Include related resources in the response. Comma-separated list of resources: sub_statuses, causes, subscribers, roles, slack_messages, environments, incident_types, services, functionalities, groups, events, action_items, custom_field_selections, feedbacks, incident_post_mortem.")
class ListIncidentsRequest(StrictModel):
    """Retrieve a paginated list of incidents with advanced filtering by status, severity, team, service, and temporal ranges. Supports sorting and inclusion of related resources like causes, subscribers, and post-mortems."""
    query: ListIncidentsRequestQuery | None = None

# Operation: create_incident
class CreateIncidentRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A human-readable title for the incident. If omitted, the system will automatically generate one.")
    kind: Literal["test", "test_sub", "example", "example_sub", "normal", "normal_sub", "backfilled", "scheduled"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="Classifies the incident type. Defaults to 'normal'. Use 'test' or 'test_sub' for testing, 'example' or 'example_sub' for examples, 'backfilled' for historical incidents, or 'scheduled' for maintenance windows.")
    parent_incident_id: str | None = Field(default=None, validation_alias="parent_incident_id", serialization_alias="parent_incident_id", description="The ID of a parent incident if this incident is a sub-incident or related to another incident.")
    duplicate_incident_id: str | None = Field(default=None, validation_alias="duplicate_incident_id", serialization_alias="duplicate_incident_id", description="The ID of an incident this one duplicates, used to link duplicate incidents together.")
    private: bool | None = Field(default=None, validation_alias="private", serialization_alias="private", description="Marks the incident as private, restricting visibility. This setting is permanent and cannot be changed after creation.")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A detailed summary or description of the incident.")
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="The user ID of the incident creator. Defaults to the user associated with the API key if not specified.")
    severity_id: str | None = Field(default=None, validation_alias="severity_id", serialization_alias="severity_id", description="The ID of the severity level to assign to the incident (e.g., critical, high, medium, low).")
    public_title: str | None = Field(default=None, validation_alias="public_title", serialization_alias="public_title", description="A public-facing title for the incident, separate from the internal title.")
    alert_ids: list[str] | None = Field(default=None, validation_alias="alert_ids", serialization_alias="alert_ids", description="An array of alert IDs to associate with this incident.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="An array of environment IDs (e.g., production, staging) to associate with this incident.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="An array of incident type IDs to categorize this incident.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="An array of service IDs affected by or related to this incident.")
    functionality_ids: list[str] | None = Field(default=None, validation_alias="functionality_ids", serialization_alias="functionality_ids", description="An array of functionality IDs representing features or components impacted by this incident.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="An array of team IDs to assign ownership or visibility of this incident.")
    cause_ids: list[str] | None = Field(default=None, validation_alias="cause_ids", serialization_alias="cause_ids", description="An array of cause IDs to identify root causes associated with this incident.")
    slack_channel_archived: bool | None = Field(default=None, validation_alias="slack_channel_archived", serialization_alias="slack_channel_archived", description="Indicates whether the associated Slack channel for this incident has been archived.")
    google_drive_parent_id: str | None = Field(default=None, validation_alias="google_drive_parent_id", serialization_alias="google_drive_parent_id", description="The Google Drive folder ID where incident-related documents should be stored.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="An array of email addresses to notify about this incident creation.")
    status: Literal["in_triage", "started", "detected", "acknowledged", "mitigated", "resolved", "closed", "cancelled", "scheduled", "in_progress", "completed"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current status of the incident. Use 'detected' or 'acknowledged' for active incidents, 'mitigated' or 'resolved' for recovery states, 'closed' for finalized incidents, or 'scheduled' for planned maintenance.")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="A URL linking to external incident details, logs, or related resources.")
    scheduled_for: str | None = Field(default=None, validation_alias="scheduled_for", serialization_alias="scheduled_for", description="The start date and time for a scheduled maintenance incident. Use ISO 8601 format.")
    scheduled_until: str | None = Field(default=None, validation_alias="scheduled_until", serialization_alias="scheduled_until", description="The end date and time for a scheduled maintenance incident. Use ISO 8601 format.")
class CreateIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'incidents' to create an incident.")
    attributes: CreateIncidentRequestBodyDataAttributes | None = None
class CreateIncidentRequestBody(StrictModel):
    data: CreateIncidentRequestBodyData
class CreateIncidentRequest(StrictModel):
    """Creates a new incident with optional metadata including severity, services, teams, and related resources. Automatically generates a title if not provided and defaults to non-private status."""
    body: CreateIncidentRequestBody

# Operation: get_incident
class GetIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to retrieve.")
class GetIncidentRequestQuery(StrictModel):
    include: Literal["sub_statuses", "causes", "subscribers", "roles", "slack_messages", "environments", "incident_types", "services", "functionalities", "groups", "events", "action_items", "custom_field_selections", "feedbacks", "incident_post_mortem"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Valid options include sub_statuses, causes, subscribers, roles, slack_messages, environments, incident_types, services, functionalities, groups, events, action_items, custom_field_selections, feedbacks, and incident_post_mortem.")
class GetIncidentRequest(StrictModel):
    """Retrieves a specific incident by its unique identifier. Optionally include related data such as sub-statuses, causes, subscribers, roles, and other associated resources."""
    path: GetIncidentRequestPath
    query: GetIncidentRequestQuery | None = None

# Operation: update_incident
class UpdateIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to update.")
class UpdateIncidentRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A human-readable title for the incident.")
    kind: Literal["test", "test_sub", "example", "example_sub", "normal", "normal_sub", "backfilled", "scheduled"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="The classification of the incident. Options include test incidents, examples, normal incidents, backfilled historical incidents, and scheduled maintenance. Defaults to 'normal'.")
    parent_incident_id: str | None = Field(default=None, validation_alias="parent_incident_id", serialization_alias="parent_incident_id", description="The ID of a parent incident if this incident is a sub-incident or child of another incident.")
    duplicate_incident_id: str | None = Field(default=None, validation_alias="duplicate_incident_id", serialization_alias="duplicate_incident_id", description="The ID of another incident if this incident is a duplicate of an existing incident.")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A detailed summary or description of the incident.")
    status: Literal["in_triage", "started", "detected", "acknowledged", "mitigated", "resolved", "closed", "cancelled", "scheduled", "in_progress", "completed"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current status of the incident. Valid statuses include triage, detection, acknowledgment, mitigation, resolution, closure, and cancellation states, as well as scheduled maintenance states.")
    private: bool | None = Field(default=None, validation_alias="private", serialization_alias="private", description="Mark the incident as private. Once set to private, this cannot be reverted. Defaults to false.")
    severity_id: str | None = Field(default=None, validation_alias="severity_id", serialization_alias="severity_id", description="The ID of the severity level to assign to the incident.")
    public_title: str | None = Field(default=None, validation_alias="public_title", serialization_alias="public_title", description="A public-facing title for the incident, separate from the internal title.")
    alert_ids: list[str] | None = Field(default=None, validation_alias="alert_ids", serialization_alias="alert_ids", description="A list of alert IDs to associate with this incident.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="A list of environment IDs where this incident occurred or is relevant.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="A list of incident type IDs to categorize this incident.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="A list of service IDs affected by or related to this incident.")
    functionality_ids: list[str] | None = Field(default=None, validation_alias="functionality_ids", serialization_alias="functionality_ids", description="A list of functionality IDs impacted by this incident.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="A list of team IDs to assign or associate with this incident.")
    cause_ids: list[str] | None = Field(default=None, validation_alias="cause_ids", serialization_alias="cause_ids", description="A list of cause IDs that contributed to or explain this incident.")
    slack_channel_archived: bool | None = Field(default=None, validation_alias="slack_channel_archived", serialization_alias="slack_channel_archived", description="Indicates whether the associated Slack channel for this incident has been archived.")
    google_drive_parent_id: str | None = Field(default=None, validation_alias="google_drive_parent_id", serialization_alias="google_drive_parent_id", description="The Google Drive folder ID to use as the parent location for incident-related documents.")
    scheduled_for: str | None = Field(default=None, validation_alias="scheduled_for", serialization_alias="scheduled_for", description="The start date and time for a scheduled maintenance incident. Use ISO 8601 format.")
    scheduled_until: str | None = Field(default=None, validation_alias="scheduled_until", serialization_alias="scheduled_until", description="The end date and time for a scheduled maintenance incident. Use ISO 8601 format.")
class UpdateIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'incidents' for this operation.")
    attributes: UpdateIncidentRequestBodyDataAttributes | None = None
class UpdateIncidentRequestBody(StrictModel):
    data: UpdateIncidentRequestBodyData
class UpdateIncidentRequest(StrictModel):
    """Update an existing incident with new details, status, severity, relationships, and metadata. Supports status transitions, severity assignment, linking to related incidents, and attaching resources like alerts, services, and teams."""
    path: UpdateIncidentRequestPath
    body: UpdateIncidentRequestBody

# Operation: delete_incident
class DeleteIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to delete.")
class DeleteIncidentRequest(StrictModel):
    """Permanently delete a specific incident by its unique identifier. This action cannot be undone."""
    path: DeleteIncidentRequestPath

# Operation: mitigate_incident
class MitigateIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to mitigate.")
class MitigateIncidentRequestBodyDataAttributes(StrictModel):
    mitigation_message: str | None = Field(default=None, validation_alias="mitigation_message", serialization_alias="mitigation_message", description="A brief explanation of how the incident was mitigated or resolved. This provides context for other team members reviewing the incident history.")
class MitigateIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be set to 'incidents' to specify that this operation applies to incident resources.")
    attributes: MitigateIncidentRequestBodyDataAttributes | None = None
class MitigateIncidentRequestBody(StrictModel):
    data: MitigateIncidentRequestBodyData
class MitigateIncidentRequest(StrictModel):
    """Mark a specific incident as mitigated by providing its ID and documenting how the incident was resolved. This updates the incident's status to reflect that mitigation actions have been taken."""
    path: MitigateIncidentRequestPath
    body: MitigateIncidentRequestBody

# Operation: resolve_incident
class ResolveIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to resolve.")
class ResolveIncidentRequestBodyDataAttributes(StrictModel):
    resolution_message: str | None = Field(default=None, validation_alias="resolution_message", serialization_alias="resolution_message", description="Optional explanation describing the resolution steps taken or outcome of the incident resolution.")
class ResolveIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'incidents' to specify this operation targets incident resources.")
    attributes: ResolveIncidentRequestBodyDataAttributes | None = None
class ResolveIncidentRequestBody(StrictModel):
    data: ResolveIncidentRequestBodyData
class ResolveIncidentRequest(StrictModel):
    """Mark a specific incident as resolved. Optionally provide details about how the incident was resolved."""
    path: ResolveIncidentRequestPath
    body: ResolveIncidentRequestBody

# Operation: cancel_incident
class CancelIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to cancel.")
class CancelIncidentRequestBodyDataAttributes(StrictModel):
    cancellation_message: str | None = Field(default=None, validation_alias="cancellation_message", serialization_alias="cancellation_message", description="An optional message explaining why the incident was cancelled.")
class CancelIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'incidents' to specify that this operation applies to incident resources.")
    attributes: CancelIncidentRequestBodyDataAttributes | None = None
class CancelIncidentRequestBody(StrictModel):
    data: CancelIncidentRequestBodyData
class CancelIncidentRequest(StrictModel):
    """Cancel a specific incident by its ID. Optionally provide a cancellation message to document the reason for cancellation."""
    path: CancelIncidentRequestPath
    body: CancelIncidentRequestBody

# Operation: update_incident_to_triage
class TriageIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to transition into triage state.")
class TriageIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'incidents' to specify this operation applies to incident resources.")
class TriageIncidentRequestBody(StrictModel):
    data: TriageIncidentRequestBodyData
class TriageIncidentRequest(StrictModel):
    """Move a specific incident into triage state for initial assessment and categorization. This operation marks the incident as requiring triage review."""
    path: TriageIncidentRequestPath
    body: TriageIncidentRequestBody

# Operation: restart_incident
class RestartIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to restart.")
class RestartIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be set to 'incidents' to specify the target resource category.")
class RestartIncidentRequestBody(StrictModel):
    data: RestartIncidentRequestBodyData
class RestartIncidentRequest(StrictModel):
    """Restart a specific incident to resume its lifecycle and processing. This operation reactivates an incident by its unique identifier."""
    path: RestartIncidentRequestPath
    body: RestartIncidentRequestBody

# Operation: add_subscribers_to_incident
class AddSubscribersToIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to which subscribers will be added.")
class AddSubscribersToIncidentRequestBodyDataAttributes(StrictModel):
    user_ids: list[str] | None = Field(default=None, validation_alias="user_ids", serialization_alias="user_ids", description="Array of user IDs to add as subscribers to the incident. Users are identified by their unique identifiers.")
    remove_users_with_no_private_incident_access: bool | None = Field(default=None, validation_alias="remove_users_with_no_private_incident_access", serialization_alias="remove_users_with_no_private_incident_access", description="When enabled, automatically removes any users from the subscriber list who lack read permissions for private incidents. Defaults to false, allowing all specified users to be added regardless of private incident access.")
class AddSubscribersToIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'incidents' for this operation.")
    attributes: AddSubscribersToIncidentRequestBodyDataAttributes | None = None
class AddSubscribersToIncidentRequestBody(StrictModel):
    data: AddSubscribersToIncidentRequestBodyData
class AddSubscribersToIncidentRequest(StrictModel):
    """Add one or more users as subscribers to an incident, with optional enforcement of private incident access permissions. Subscribers receive notifications about incident updates."""
    path: AddSubscribersToIncidentRequestPath
    body: AddSubscribersToIncidentRequestBody

# Operation: remove_subscribers_from_incident
class RemoveSubscribersToIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident from which subscribers will be removed.")
class RemoveSubscribersToIncidentRequestBodyDataAttributes(StrictModel):
    user_ids: list[str] | None = Field(default=None, validation_alias="user_ids", serialization_alias="user_ids", description="Array of user IDs to remove from the incident's subscriber list. If not provided, only users without private incident access will be removed (if that option is enabled).")
    remove_users_with_no_private_incident_access: bool | None = Field(default=None, validation_alias="remove_users_with_no_private_incident_access", serialization_alias="remove_users_with_no_private_incident_access", description="When enabled, automatically removes any users who lack read permissions for private incidents from the subscriber list. Defaults to false.")
class RemoveSubscribersToIncidentRequestBodyData(StrictModel):
    type_: Literal["incidents"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'incidents' for this operation.")
    attributes: RemoveSubscribersToIncidentRequestBodyDataAttributes | None = None
class RemoveSubscribersToIncidentRequestBody(StrictModel):
    data: RemoveSubscribersToIncidentRequestBodyData
class RemoveSubscribersToIncidentRequest(StrictModel):
    """Remove one or more subscribers from an incident. You can specify individual users to remove or automatically remove users lacking read permissions for private incidents."""
    path: RemoveSubscribersToIncidentRequestPath
    body: RemoveSubscribersToIncidentRequestBody

# Operation: list_live_call_routers
class ListLiveCallRoutersRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., nested objects or associations).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results to return per page.")
    sort: str | None = Field(default=None, description="Comma-separated list of fields to sort by, with optional direction prefix (e.g., 'name,-created_at' for ascending name and descending creation date).")
class ListLiveCallRoutersRequest(StrictModel):
    """Retrieve a paginated list of live call routers with optional filtering and sorting capabilities."""
    query: ListLiveCallRoutersRequestQuery | None = None

# Operation: create_live_call_router
class CreateLiveCallRouterRequestBodyDataAttributesEscalationPolicyTriggerParams(StrictModel):
    type_: Literal["service", "group", "escalation_policy"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The target type for escalation notifications: 'service' (PagerDuty service), 'group' (team/group), or 'escalation_policy' (escalation policy).")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification target (service, group, or escalation policy) for call routing.")
class CreateLiveCallRouterRequestBodyDataAttributes(StrictModel):
    kind: Literal["voicemail", "live"] = Field(default=..., validation_alias="kind", serialization_alias="kind", description="The operational mode of the router: 'live' for direct call handling or 'voicemail' for voicemail-only setup.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the live call router is active and operational.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for the live call router.")
    country_code: Literal["AU", "CA", "NL", "NZ", "GB", "US"] = Field(default=..., validation_alias="country_code", serialization_alias="country_code", description="The country where the phone number is registered: AU (Australia), CA (Canada), NL (Netherlands), NZ (New Zealand), GB (United Kingdom), or US (United States).")
    phone_type: Literal["local", "toll_free", "mobile"] = Field(default=..., validation_alias="phone_type", serialization_alias="phone_type", description="The phone number category: 'local' (geographic area code), 'toll_free' (no charge to caller), or 'mobile' (cellular number).")
    phone_number: str = Field(default=..., validation_alias="phone_number", serialization_alias="phone_number", description="The phone number to register for this router. Generate a number using the generate_phone_number API before providing it here.")
    voicemail_greeting: str | None = Field(default=None, validation_alias="voicemail_greeting", serialization_alias="voicemail_greeting", description="Optional greeting message played when callers reach the voicemail system.")
    caller_greeting: str | None = Field(default=None, validation_alias="caller_greeting", serialization_alias="caller_greeting", description="Optional greeting message played when callers first connect to the live call router.")
    waiting_music_url: Literal["https://storage.rootly.com/twilio/voicemail/ClockworkWaltz.mp3", "https://storage.rootly.com/twilio/voicemail/ith_brahms-116-4.mp3", "https://storage.rootly.com/twilio/voicemail/Mellotroniac_-_Flight_Of_Young_Hearts_Flute.mp3", "https://storage.rootly.com/twilio/voicemail/BusyStrings.mp3", "https://storage.rootly.com/twilio/voicemail/oldDog_-_endless_goodbye_%28instr.%29.mp3", "https://storage.rootly.com/twilio/voicemail/MARKOVICHAMP-Borghestral.mp3", "https://storage.rootly.com/twilio/voicemail/ith_chopin-15-2.mp3"] | None = Field(default=None, validation_alias="waiting_music_url", serialization_alias="waiting_music_url", description="Optional background music URL played while callers wait. Choose from predefined Rootly-hosted audio tracks.")
    sent_to_voicemail_delay: int | None = Field(default=None, validation_alias="sent_to_voicemail_delay", serialization_alias="sent_to_voicemail_delay", description="Optional delay in seconds before an unanswered call is automatically redirected to voicemail.")
    should_redirect_to_voicemail_on_no_answer: bool | None = Field(default=None, validation_alias="should_redirect_to_voicemail_on_no_answer", serialization_alias="should_redirect_to_voicemail_on_no_answer", description="When enabled, prompts the caller to choose between leaving a voicemail or waiting to connect with a live person.")
    escalation_level_delay_in_seconds: int | None = Field(default=None, validation_alias="escalation_level_delay_in_seconds", serialization_alias="escalation_level_delay_in_seconds", description="Optional override for the delay (in seconds) between escalation levels when routing through an escalation policy.")
    should_auto_resolve_alert_on_call_end: bool | None = Field(default=None, validation_alias="should_auto_resolve_alert_on_call_end", serialization_alias="should_auto_resolve_alert_on_call_end", description="When enabled, automatically resolves the associated alert when the call ends.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="Optional alert urgency level used in escalation paths to determine priority and who to page.")
    calling_tree_prompt: str | None = Field(default=None, validation_alias="calling_tree_prompt", serialization_alias="calling_tree_prompt", description="Optional audio instructions or prompts that callers hear, guiding them to select routing options when this router is configured as a phone tree.")
    paging_targets: list[CreateLiveCallRouterBodyDataAttributesPagingTargetsItem] | None = Field(default=None, validation_alias="paging_targets", serialization_alias="paging_targets", description="Optional list of paging targets (services, groups, or escalation policies) that callers can select from when this router functions as a phone tree.")
    escalation_policy_trigger_params: CreateLiveCallRouterRequestBodyDataAttributesEscalationPolicyTriggerParams
class CreateLiveCallRouterRequestBodyData(StrictModel):
    type_: Literal["live_call_routers"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'live_call_routers'.")
    attributes: CreateLiveCallRouterRequestBodyDataAttributes
class CreateLiveCallRouterRequestBody(StrictModel):
    data: CreateLiveCallRouterRequestBodyData
class CreateLiveCallRouterRequest(StrictModel):
    """Creates a new Live Call Router to handle incoming calls with configurable routing, voicemail, and escalation options. The router can be set up as a live call handler or voicemail system with optional phone tree capabilities."""
    body: CreateLiveCallRouterRequestBody

# Operation: generate_phone_number_for_live_call_router
class GeneratePhoneNumberLiveCallRouterRequestQuery(StrictModel):
    country_code: Literal["AU", "CA", "NL", "NZ", "GB", "US"] = Field(default=..., description="The country where the phone number will be allocated. Supported countries are Australia, Canada, Netherlands, New Zealand, United Kingdom, and United States.")
    phone_type: Literal["local", "toll_free", "mobile"] = Field(default=..., description="The type of phone number to generate: local (geographic area code), toll_free (caller pays no charges), or mobile (cellular number).")
class GeneratePhoneNumberLiveCallRouterRequest(StrictModel):
    """Generates a dedicated phone number for routing incoming calls through Live Call Router. The phone number is allocated based on the specified country and type."""
    query: GeneratePhoneNumberLiveCallRouterRequestQuery

# Operation: get_live_call_router
class GetLiveCallRouterRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Live Call Router to retrieve.")
class GetLiveCallRouterRequest(StrictModel):
    """Retrieves a specific Live Call Router configuration by its unique identifier. Use this to fetch details about a configured call routing rule."""
    path: GetLiveCallRouterRequestPath

# Operation: update_live_call_router
class UpdateLiveCallRouterRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Live Call Router to update.")
class UpdateLiveCallRouterRequestBodyDataAttributesEscalationPolicyTriggerParams(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification target (Service, Group, or Escalation Policy) that will receive escalation alerts.")
    type_: Literal["Service", "Group", "EscalationPolicy"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category of the notification target: 'Service' for a specific service, 'Group' for a team or group, or 'EscalationPolicy' for an escalation policy.")
class UpdateLiveCallRouterRequestBodyDataAttributes(StrictModel):
    kind: Literal["voicemail", "live"] | None = Field(default=None, validation_alias="kind", serialization_alias="kind", description="The operational mode of the router: 'voicemail' for voicemail-only handling or 'live' for live call routing.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the Live Call Router is active and accepting calls.")
    country_code: Literal["AU", "CA", "NL", "NZ", "GB", "US"] | None = Field(default=None, validation_alias="country_code", serialization_alias="country_code", description="The country where the phone number is registered: AU (Australia), CA (Canada), NL (Netherlands), NZ (New Zealand), GB (United Kingdom), or US (United States).")
    phone_type: Literal["local", "toll_free", "mobile"] | None = Field(default=None, validation_alias="phone_type", serialization_alias="phone_type", description="The phone number type: 'local' for regional numbers, 'toll_free' for toll-free numbers, or 'mobile' for mobile numbers.")
    voicemail_greeting: str | None = Field(default=None, validation_alias="voicemail_greeting", serialization_alias="voicemail_greeting", description="The audio message played when callers reach the voicemail system.")
    caller_greeting: str | None = Field(default=None, validation_alias="caller_greeting", serialization_alias="caller_greeting", description="The greeting message played to callers when they first connect to the router.")
    waiting_music_url: Literal["https://storage.rootly.com/twilio/voicemail/ClockworkWaltz.mp3", "https://storage.rootly.com/twilio/voicemail/ith_brahms-116-4.mp3", "https://storage.rootly.com/twilio/voicemail/Mellotroniac_-_Flight_Of_Young_Hearts_Flute.mp3", "https://storage.rootly.com/twilio/voicemail/BusyStrings.mp3", "https://storage.rootly.com/twilio/voicemail/oldDog_-_endless_goodbye_%28instr.%29.mp3", "https://storage.rootly.com/twilio/voicemail/MARKOVICHAMP-Borghestral.mp3", "https://storage.rootly.com/twilio/voicemail/ith_chopin-15-2.mp3"] | None = Field(default=None, validation_alias="waiting_music_url", serialization_alias="waiting_music_url", description="The URL of the background music played while callers wait in queue; must be one of the predefined Rootly-hosted audio tracks.")
    sent_to_voicemail_delay: int | None = Field(default=None, validation_alias="sent_to_voicemail_delay", serialization_alias="sent_to_voicemail_delay", description="The number of seconds to wait before automatically redirecting a caller to voicemail if no one answers.")
    should_redirect_to_voicemail_on_no_answer: bool | None = Field(default=None, validation_alias="should_redirect_to_voicemail_on_no_answer", serialization_alias="should_redirect_to_voicemail_on_no_answer", description="When enabled, prompts the caller to choose between leaving a voicemail or waiting to connect with a live representative.")
    escalation_level_delay_in_seconds: int | None = Field(default=None, validation_alias="escalation_level_delay_in_seconds", serialization_alias="escalation_level_delay_in_seconds", description="The delay in seconds between escalation levels, overriding the default escalation policy timing.")
    should_auto_resolve_alert_on_call_end: bool | None = Field(default=None, validation_alias="should_auto_resolve_alert_on_call_end", serialization_alias="should_auto_resolve_alert_on_call_end", description="When enabled, automatically resolves the associated alert when the call ends.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The identifier of the alert urgency level used to determine escalation routing and who receives page notifications.")
    calling_tree_prompt: str | None = Field(default=None, validation_alias="calling_tree_prompt", serialization_alias="calling_tree_prompt", description="The audio instructions or prompt that callers hear when calling this number, guiding them to select routing options in a phone tree configuration.")
    paging_targets: list[UpdateLiveCallRouterBodyDataAttributesPagingTargetsItem] | None = Field(default=None, validation_alias="paging_targets", serialization_alias="paging_targets", description="An ordered list of targets (Services, Groups, or Escalation Policies) that callers can select from when this router is configured as a phone tree; order determines the sequence presented to callers.")
    escalation_policy_trigger_params: UpdateLiveCallRouterRequestBodyDataAttributesEscalationPolicyTriggerParams
class UpdateLiveCallRouterRequestBodyData(StrictModel):
    type_: Literal["live_call_routers"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be 'live_call_routers'.")
    attributes: UpdateLiveCallRouterRequestBodyDataAttributes
class UpdateLiveCallRouterRequestBody(StrictModel):
    data: UpdateLiveCallRouterRequestBodyData
class UpdateLiveCallRouterRequest(StrictModel):
    """Update the configuration of a Live Call Router, including routing behavior, greetings, escalation policies, and call handling preferences."""
    path: UpdateLiveCallRouterRequestPath
    body: UpdateLiveCallRouterRequestBody

# Operation: delete_live_call_router
class DeleteLiveCallRouterRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Live Call Router to delete.")
class DeleteLiveCallRouterRequest(StrictModel):
    """Permanently delete a Live Call Router by its unique identifier. This action cannot be undone."""
    path: DeleteLiveCallRouterRequestPath

# Operation: list_on_call_roles
class ListOnCallRolesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., users, schedules). Reduces the need for additional API calls by embedding associated data.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve when paginating through results. Use with page[size] to navigate large datasets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of on-call roles to return per page. Controls the size of each paginated response.")
    sort: str | None = Field(default=None, description="Sort the results by one or more fields in ascending or descending order. Specify field names with optional +/- prefix to control sort direction (e.g., name, -created_at).")
class ListOnCallRolesRequest(StrictModel):
    """Retrieve a paginated list of on-call roles configured in the system. Use pagination parameters to control result size and navigation through the dataset."""
    query: ListOnCallRolesRequestQuery | None = None

# Operation: create_on_call_role
class CreateOnCallRoleRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The human-readable name for the On-Call Role; used for display and identification throughout the system.")
    slug: str | None = Field(default=None, validation_alias="slug", serialization_alias="slug", description="A URL-friendly identifier for the role; if not provided, it will be auto-generated from the role name.")
    system_role: str = Field(default=..., validation_alias="system_role", serialization_alias="system_role", description="The role classification that determines editability and behavior; user and custom type roles are editable, while system-defined roles have restricted modification.")
    alert_sources_permissions: list[Literal["create", "update", "delete"]] | None = Field(default=None, validation_alias="alert_sources_permissions", serialization_alias="alert_sources_permissions", description="Array of permission objects controlling access to alert sources; each entry specifies allowed actions on alert source resources.")
    alert_urgency_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="alert_urgency_permissions", serialization_alias="alert_urgency_permissions", description="Array of permission objects controlling access to alert urgency levels; each entry specifies allowed actions on urgency classifications.")
    alerts_permissions: list[Literal["create", "update", "read"]] | None = Field(default=None, validation_alias="alerts_permissions", serialization_alias="alerts_permissions", description="Array of permission objects controlling access to alerts; each entry specifies allowed actions such as view, acknowledge, or resolve.")
    api_keys_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="api_keys_permissions", serialization_alias="api_keys_permissions", description="Array of permission objects controlling access to API keys; each entry specifies allowed actions for creating, viewing, or revoking keys.")
    audits_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="audits_permissions", serialization_alias="audits_permissions", description="Array of permission objects controlling access to audit logs; each entry specifies allowed actions for viewing system activity records.")
    contacts_permissions: list[Literal["read"]] | None = Field(default=None, validation_alias="contacts_permissions", serialization_alias="contacts_permissions", description="Array of permission objects controlling access to contacts; each entry specifies allowed actions for managing contact information.")
    escalation_policies_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="escalation_policies_permissions", serialization_alias="escalation_policies_permissions", description="Array of permission objects controlling access to escalation policies; each entry specifies allowed actions for creating and modifying escalation rules.")
    groups_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="groups_permissions", serialization_alias="groups_permissions", description="Array of permission objects controlling access to groups; each entry specifies allowed actions for managing group membership and settings.")
    heartbeats_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="heartbeats_permissions", serialization_alias="heartbeats_permissions", description="Array of permission objects controlling access to heartbeats; each entry specifies allowed actions for monitoring and managing heartbeat checks.")
    integrations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="integrations_permissions", serialization_alias="integrations_permissions", description="Array of permission objects controlling access to integrations; each entry specifies allowed actions for connecting external tools and services.")
    invitations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="invitations_permissions", serialization_alias="invitations_permissions", description="Array of permission objects controlling access to invitations; each entry specifies allowed actions for sending and managing user invitations.")
    live_call_routing_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="live_call_routing_permissions", serialization_alias="live_call_routing_permissions", description="Array of permission objects controlling access to live call routing; each entry specifies allowed actions for configuring call routing rules.")
    schedule_override_permissions: list[Literal["create", "update"]] | None = Field(default=None, validation_alias="schedule_override_permissions", serialization_alias="schedule_override_permissions", description="Array of permission objects controlling access to schedule overrides; each entry specifies allowed actions for creating temporary schedule modifications.")
    schedules_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="schedules_permissions", serialization_alias="schedules_permissions", description="Array of permission objects controlling access to schedules; each entry specifies allowed actions for creating, viewing, and modifying on-call schedules.")
    services_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="services_permissions", serialization_alias="services_permissions", description="Array of permission objects controlling access to services; each entry specifies allowed actions for managing service configurations.")
    webhooks_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="webhooks_permissions", serialization_alias="webhooks_permissions", description="Array of permission objects controlling access to webhooks; each entry specifies allowed actions for creating and managing webhook integrations.")
    workflows_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="workflows_permissions", serialization_alias="workflows_permissions", description="Array of permission objects controlling access to workflows; each entry specifies allowed actions for creating and managing automation workflows.")
class CreateOnCallRoleRequestBodyData(StrictModel):
    type_: Literal["on_call_roles"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'on_call_roles' to specify this is an On-Call Role resource.")
    attributes: CreateOnCallRoleRequestBodyDataAttributes
class CreateOnCallRoleRequestBody(StrictModel):
    data: CreateOnCallRoleRequestBodyData
class CreateOnCallRoleRequest(StrictModel):
    """Creates a new On-Call Role with specified permissions across various operational domains. Define the role name, system type, and granular access controls for alerts, schedules, integrations, and other resources."""
    body: CreateOnCallRoleRequestBody

# Operation: get_on_call_role
class GetOnCallRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the On-Call Role to retrieve.")
class GetOnCallRoleRequest(StrictModel):
    """Retrieves a specific On-Call Role by its unique identifier. Use this to fetch detailed information about a particular on-call role configuration."""
    path: GetOnCallRoleRequestPath

# Operation: update_on_call_role
class UpdateOnCallRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the On-Call Role to update.")
class UpdateOnCallRoleRequestBodyDataAttributes(StrictModel):
    slug: str | None = Field(default=None, validation_alias="slug", serialization_alias="slug", description="A URL-friendly identifier for the role used in API paths and references.")
    system_role: str | None = Field(default=None, validation_alias="system_role", serialization_alias="system_role", description="The classification of the role (e.g., user, custom); only user and custom type roles can be modified.")
    alert_sources_permissions: list[Literal["create", "update", "delete"]] | None = Field(default=None, validation_alias="alert_sources_permissions", serialization_alias="alert_sources_permissions", description="Array of permission strings defining access levels for alert sources.")
    alert_urgency_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="alert_urgency_permissions", serialization_alias="alert_urgency_permissions", description="Array of permission strings defining access levels for alert urgency levels.")
    alerts_permissions: list[Literal["create", "update", "read"]] | None = Field(default=None, validation_alias="alerts_permissions", serialization_alias="alerts_permissions", description="Array of permission strings defining access levels for alerts.")
    api_keys_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="api_keys_permissions", serialization_alias="api_keys_permissions", description="Array of permission strings defining access levels for API keys.")
    audits_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="audits_permissions", serialization_alias="audits_permissions", description="Array of permission strings defining access levels for audit logs.")
    contacts_permissions: list[Literal["read"]] | None = Field(default=None, validation_alias="contacts_permissions", serialization_alias="contacts_permissions", description="Array of permission strings defining access levels for contacts.")
    escalation_policies_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="escalation_policies_permissions", serialization_alias="escalation_policies_permissions", description="Array of permission strings defining access levels for escalation policies.")
    groups_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="groups_permissions", serialization_alias="groups_permissions", description="Array of permission strings defining access levels for groups.")
    heartbeats_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="heartbeats_permissions", serialization_alias="heartbeats_permissions", description="Array of permission strings defining access levels for heartbeats.")
    integrations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="integrations_permissions", serialization_alias="integrations_permissions", description="Array of permission strings defining access levels for integrations.")
    invitations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="invitations_permissions", serialization_alias="invitations_permissions", description="Array of permission strings defining access levels for invitations.")
    live_call_routing_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="live_call_routing_permissions", serialization_alias="live_call_routing_permissions", description="Array of permission strings defining access levels for live call routing.")
    schedule_override_permissions: list[Literal["create", "update"]] | None = Field(default=None, validation_alias="schedule_override_permissions", serialization_alias="schedule_override_permissions", description="Array of permission strings defining access levels for schedule overrides.")
    schedules_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="schedules_permissions", serialization_alias="schedules_permissions", description="Array of permission strings defining access levels for schedules.")
    services_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="services_permissions", serialization_alias="services_permissions", description="Array of permission strings defining access levels for services.")
    webhooks_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="webhooks_permissions", serialization_alias="webhooks_permissions", description="Array of permission strings defining access levels for webhooks.")
    workflows_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(default=None, validation_alias="workflows_permissions", serialization_alias="workflows_permissions", description="Array of permission strings defining access levels for workflows.")
class UpdateOnCallRoleRequestBodyData(StrictModel):
    type_: Literal["on_call_roles"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'on_call_roles'.")
    attributes: UpdateOnCallRoleRequestBodyDataAttributes | None = None
class UpdateOnCallRoleRequestBody(StrictModel):
    data: UpdateOnCallRoleRequestBodyData
class UpdateOnCallRoleRequest(StrictModel):
    """Update an existing On-Call Role with new configuration, including slug, system role type, and granular permissions across alert sources, contacts, schedules, and other resources."""
    path: UpdateOnCallRoleRequestPath
    body: UpdateOnCallRoleRequestBody

# Operation: delete_on_call_role
class DeleteOnCallRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the On-Call Role to delete.")
class DeleteOnCallRoleRequest(StrictModel):
    """Permanently delete a specific On-Call Role by its unique identifier. This action cannot be undone."""
    path: DeleteOnCallRoleRequestPath

# Operation: list_on_call_shadows
class ListOnCallShadowsRequestPath(StrictModel):
    schedule_id: str = Field(default=..., description="The unique identifier of the schedule for which to retrieve shadow shifts.")
class ListOnCallShadowsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., user details, shift metadata). Specify which associations to expand for richer context.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of shadow shifts to return per page. Adjust this value to control result set size for pagination.")
class ListOnCallShadowsRequest(StrictModel):
    """Retrieve all shadow shifts assigned to a specific on-call schedule. Shadow shifts represent secondary coverage or training assignments that run parallel to primary on-call shifts."""
    path: ListOnCallShadowsRequestPath
    query: ListOnCallShadowsRequestQuery | None = None

# Operation: create_on_call_shadow
class CreateOnCallShadowRequestPath(StrictModel):
    schedule_id: str = Field(default=..., description="The unique identifier of the schedule to which this shadow configuration belongs.")
class CreateOnCallShadowRequestBodyDataAttributes(StrictModel):
    shadowable_type: Literal["User", "Schedule"] = Field(default=..., validation_alias="shadowable_type", serialization_alias="shadowable_type", description="The type of entity being shadowed: either 'User' to shadow a specific person or 'Schedule' to shadow an entire schedule.")
    shadowable_id: str = Field(default=..., validation_alias="shadowable_id", serialization_alias="shadowable_id", description="The unique identifier of the user or schedule being shadowed, corresponding to the shadowable_type selected.")
    shadow_user_id: int = Field(default=..., validation_alias="shadow_user_id", serialization_alias="shadow_user_id", description="The unique identifier of the user who will be shadowing and to whom the shadow shift belongs.")
    starts_at: str = Field(default=..., validation_alias="starts_at", serialization_alias="starts_at", description="The start date and time for the shadow shift in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    ends_at: str = Field(default=..., validation_alias="ends_at", serialization_alias="ends_at", description="The end date and time for the shadow shift in ISO 8601 format; must be after the start time.", json_schema_extra={'format': 'date-time'})
class CreateOnCallShadowRequestBodyData(StrictModel):
    type_: Literal["on_call_shadows"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type for this operation; must be set to 'on_call_shadows'.")
    attributes: CreateOnCallShadowRequestBodyDataAttributes
class CreateOnCallShadowRequestBody(StrictModel):
    data: CreateOnCallShadowRequestBodyData
class CreateOnCallShadowRequest(StrictModel):
    """Creates a new on-call shadow configuration that allows a designated user to shadow either another user or an entire schedule during a specified time period."""
    path: CreateOnCallShadowRequestPath
    body: CreateOnCallShadowRequestBody

# Operation: get_on_call_shadow
class GetOnCallShadowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the On Call Shadow configuration to retrieve.")
class GetOnCallShadowRequest(StrictModel):
    """Retrieves a specific On Call Shadow configuration by its unique identifier. Use this to fetch details about an on-call shadow setup, including its rules and associated personnel."""
    path: GetOnCallShadowRequestPath

# Operation: update_on_call_shadow
class UpdateOnCallShadowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the on-call shadow configuration to update.")
class UpdateOnCallShadowRequestBodyDataAttributes(StrictModel):
    schedule_id: str | None = Field(default=None, validation_alias="schedule_id", serialization_alias="schedule_id", description="The ID of the schedule that this shadow shift is associated with.")
    shadowable_type: Literal["User", "Schedule"] | None = Field(default=None, validation_alias="shadowable_type", serialization_alias="shadowable_type", description="The type of resource being shadowed: either a 'User' (individual team member) or a 'Schedule' (shift schedule).")
    shadowable_id: str | None = Field(default=None, validation_alias="shadowable_id", serialization_alias="shadowable_id", description="The ID of the user or schedule that is being shadowed, depending on the shadowable_type specified.")
    shadow_user_id: int | None = Field(default=None, validation_alias="shadow_user_id", serialization_alias="shadow_user_id", description="The ID of the user who is performing the shadow shift and observing the on-call duties.")
    starts_at: str | None = Field(default=None, validation_alias="starts_at", serialization_alias="starts_at", description="The start date and time of the shadow shift in ISO 8601 format (e.g., 2024-01-15T09:00:00Z).", json_schema_extra={'format': 'date-time'})
    ends_at: str | None = Field(default=None, validation_alias="ends_at", serialization_alias="ends_at", description="The end date and time of the shadow shift in ISO 8601 format (e.g., 2024-01-15T17:00:00Z).", json_schema_extra={'format': 'date-time'})
class UpdateOnCallShadowRequestBodyData(StrictModel):
    type_: Literal["on_call_shadows"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'on_call_shadows' to specify this is an on-call shadow resource.")
    attributes: UpdateOnCallShadowRequestBodyDataAttributes | None = None
class UpdateOnCallShadowRequestBody(StrictModel):
    data: UpdateOnCallShadowRequestBodyData
class UpdateOnCallShadowRequest(StrictModel):
    """Update an existing on-call shadow configuration to modify shadowing assignments, time windows, or the user being shadowed. This allows adjustments to shadow shift details such as the shadowed user or schedule, shadow participant, and shift timing."""
    path: UpdateOnCallShadowRequestPath
    body: UpdateOnCallShadowRequestBody

# Operation: delete_on_call_shadow
class DeleteOnCallShadowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the on-call shadow configuration to delete.")
class DeleteOnCallShadowRequest(StrictModel):
    """Remove a specific on-call shadow configuration by its unique identifier. This operation permanently deletes the shadow configuration and its associated settings."""
    path: DeleteOnCallShadowRequestPath

# Operation: list_override_shifts
class ListOverrideShiftsRequestPath(StrictModel):
    schedule_id: str = Field(default=..., description="The unique identifier of the schedule containing the override shifts to retrieve.")
class ListOverrideShiftsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., user details, shift metadata). Specify which associations should be populated.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of override shifts to return per page. Controls the batch size of results returned in each request.")
class ListOverrideShiftsRequest(StrictModel):
    """Retrieve a paginated list of override shifts for a specific schedule. Override shifts represent temporary changes or substitutions to the standard schedule."""
    path: ListOverrideShiftsRequestPath
    query: ListOverrideShiftsRequestQuery | None = None

# Operation: create_override_shift
class CreateOverrideShiftRequestPath(StrictModel):
    schedule_id: str = Field(default=..., description="The unique identifier of the schedule in which the override shift will be created.")
class CreateOverrideShiftRequestBodyDataAttributes(StrictModel):
    starts_at: str = Field(default=..., validation_alias="starts_at", serialization_alias="starts_at", description="The start date and time of the override shift in ISO 8601 format (e.g., 2024-01-15T09:00:00Z).", json_schema_extra={'format': 'date-time'})
    ends_at: str = Field(default=..., validation_alias="ends_at", serialization_alias="ends_at", description="The end date and time of the override shift in ISO 8601 format (e.g., 2024-01-15T17:00:00Z). Must be after the start time.", json_schema_extra={'format': 'date-time'})
    user_id: int = Field(default=..., validation_alias="user_id", serialization_alias="user_id", description="The numeric identifier of the user who will be assigned to this override shift.")
class CreateOverrideShiftRequestBodyData(StrictModel):
    type_: Literal["shifts"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type for this operation, which must be 'shifts' to indicate an override shift resource.")
    attributes: CreateOverrideShiftRequestBodyDataAttributes
class CreateOverrideShiftRequestBody(StrictModel):
    data: CreateOverrideShiftRequestBodyData
class CreateOverrideShiftRequest(StrictModel):
    """Creates a new override shift for a user within a specified schedule, allowing temporary assignment changes during a defined time period."""
    path: CreateOverrideShiftRequestPath
    body: CreateOverrideShiftRequestBody

# Operation: get_override_shift
class GetOverrideShiftRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the override shift to retrieve.")
class GetOverrideShiftRequest(StrictModel):
    """Retrieves a specific override shift by its unique identifier. Use this to fetch details about a single override shift record."""
    path: GetOverrideShiftRequestPath

# Operation: update_override_shift
class UpdateOverrideShiftRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the override shift to update.")
class UpdateOverrideShiftRequestBodyDataAttributes(StrictModel):
    user_id: int = Field(default=..., validation_alias="user_id", serialization_alias="user_id", description="The user ID associated with this override shift, identifying which user the shift override applies to.")
class UpdateOverrideShiftRequestBodyData(StrictModel):
    type_: Literal["shifts"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'shifts' to indicate this operation applies to shift override resources.")
    attributes: UpdateOverrideShiftRequestBodyDataAttributes
class UpdateOverrideShiftRequestBody(StrictModel):
    data: UpdateOverrideShiftRequestBodyData
class UpdateOverrideShiftRequest(StrictModel):
    """Update an existing override shift by its unique identifier. Allows modification of shift override details for a specific user."""
    path: UpdateOverrideShiftRequestPath
    body: UpdateOverrideShiftRequestBody

# Operation: delete_override_shift
class DeleteOverrideShiftRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the override shift to delete. This must be a valid override shift ID that exists in the system.")
class DeleteOverrideShiftRequest(StrictModel):
    """Remove a specific override shift from the system by its unique identifier. This operation permanently deletes the override shift record."""
    path: DeleteOverrideShiftRequestPath

# Operation: list_playbook_tasks
class ListPlaybookTasksRequestPath(StrictModel):
    playbook_id: str = Field(default=..., description="The unique identifier of the playbook for which to retrieve tasks.")
class ListPlaybookTasksRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., task details, execution history). Specify which associations to expand for richer context.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve when paginating through results. Use with page[size] to navigate large task lists.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of tasks to return per page. Controls the batch size of results returned in each request.")
class ListPlaybookTasksRequest(StrictModel):
    """Retrieve a paginated list of tasks associated with a specific playbook. Use pagination parameters to control result size and navigate through task collections."""
    path: ListPlaybookTasksRequestPath
    query: ListPlaybookTasksRequestQuery | None = None

# Operation: create_playbook_task
class CreatePlaybookTaskRequestPath(StrictModel):
    playbook_id: str = Field(default=..., description="The unique identifier of the playbook to which this task will be added.")
class CreatePlaybookTaskRequestBodyDataAttributes(StrictModel):
    task: str = Field(default=..., validation_alias="task", serialization_alias="task", description="The name or title of the task to be created.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional detailed description providing context or instructions for the task.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="An optional numeric position to control the task's order within the playbook's task sequence. If not specified, the task will be appended to the end.")
class CreatePlaybookTaskRequestBodyData(StrictModel):
    type_: Literal["playbook_tasks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this operation, which must be set to 'playbook_tasks'.")
    attributes: CreatePlaybookTaskRequestBodyDataAttributes
class CreatePlaybookTaskRequestBody(StrictModel):
    data: CreatePlaybookTaskRequestBodyData
class CreatePlaybookTaskRequest(StrictModel):
    """Creates a new task within a playbook. The task will be added to the specified playbook and can be positioned within the task sequence."""
    path: CreatePlaybookTaskRequestPath
    body: CreatePlaybookTaskRequestBody

# Operation: get_playbook_task
class GetPlaybookTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the playbook task to retrieve.")
class GetPlaybookTaskRequest(StrictModel):
    """Retrieves a specific playbook task by its unique identifier. Use this to fetch detailed information about a single task within a playbook."""
    path: GetPlaybookTaskRequestPath

# Operation: update_playbook_task
class UpdatePlaybookTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the playbook task to update.")
class UpdatePlaybookTaskRequestBodyDataAttributes(StrictModel):
    task: str | None = Field(default=None, validation_alias="task", serialization_alias="task", description="The name or title of the task to be executed within the playbook.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation of what the task does and any relevant context for execution.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The execution order of this task within the playbook, where lower numbers execute first.")
class UpdatePlaybookTaskRequestBodyData(StrictModel):
    type_: Literal["playbook_tasks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'playbook_tasks' to specify the resource being updated.")
    attributes: UpdatePlaybookTaskRequestBodyDataAttributes | None = None
class UpdatePlaybookTaskRequestBody(StrictModel):
    data: UpdatePlaybookTaskRequestBodyData
class UpdatePlaybookTaskRequest(StrictModel):
    """Update a specific playbook task within a playbook by its ID. Modify task details such as the task name, description, or execution position."""
    path: UpdatePlaybookTaskRequestPath
    body: UpdatePlaybookTaskRequestBody

# Operation: delete_playbook_task
class DeletePlaybookTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the playbook task to delete.")
class DeletePlaybookTaskRequest(StrictModel):
    """Permanently delete a specific playbook task by its unique identifier. This action cannot be undone."""
    path: DeletePlaybookTaskRequestPath

# Operation: list_playbooks
class ListPlaybooksRequestQuery(StrictModel):
    include: Literal["severities", "environments", "services", "functionalities", "groups", "causes", "incident_types"] | None = Field(default=None, description="Comma-separated list of related entities to include in the response. Valid options are: severities, environments, services, functionalities, groups, causes, or incident_types.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination (1-indexed). Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of playbooks to return per page. Use with page[number] to control result set size.")
class ListPlaybooksRequest(StrictModel):
    """Retrieve a paginated list of playbooks with optional related metadata. Use include parameter to enrich results with associated severities, environments, services, functionalities, groups, causes, or incident types."""
    query: ListPlaybooksRequestQuery | None = None

# Operation: create_playbook
class CreatePlaybookRequestBodyDataAttributes(StrictModel):
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="The name of the playbook; used as the primary identifier in lists and displays.")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief overview or description of the playbook's purpose and scope.")
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL pointing to external documentation or resources related to this playbook.")
    severity_ids: list[str] | None = Field(default=None, validation_alias="severity_ids", serialization_alias="severity_ids", description="Array of Severity IDs to associate with this playbook; determines which severity levels this playbook applies to.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="Array of Environment IDs to associate with this playbook; specifies which environments (e.g., production, staging) this playbook is relevant for.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of Service IDs to associate with this playbook; links the playbook to specific services it addresses.")
    functionality_ids: list[str] | None = Field(default=None, validation_alias="functionality_ids", serialization_alias="functionality_ids", description="Array of Functionality IDs to associate with this playbook; categorizes the playbook by the functional areas it covers.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="Array of Team IDs to associate with this playbook; designates which teams own or are responsible for executing this playbook.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="Array of Incident Type IDs to associate with this playbook; specifies which incident types this playbook provides guidance for.")
class CreatePlaybookRequestBodyData(StrictModel):
    type_: Literal["playbooks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'playbooks' to indicate this is a playbook resource.")
    attributes: CreatePlaybookRequestBodyDataAttributes
class CreatePlaybookRequestBody(StrictModel):
    data: CreatePlaybookRequestBodyData
class CreatePlaybookRequest(StrictModel):
    """Creates a new playbook with metadata and associations. Playbooks can be linked to severities, environments, services, functionalities, teams, and incident types for contextual organization."""
    body: CreatePlaybookRequestBody

# Operation: get_playbook
class GetPlaybookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the playbook to retrieve.")
class GetPlaybookRequestQuery(StrictModel):
    include: Literal["severities", "environments", "services", "functionalities", "groups", "causes", "incident_types"] | None = Field(default=None, description="Comma-separated list of related entities to include in the response. Valid options are: severities, environments, services, functionalities, groups, causes, and incident_types.")
class GetPlaybookRequest(StrictModel):
    """Retrieves a specific playbook by its unique identifier, with optional related data expansion."""
    path: GetPlaybookRequestPath
    query: GetPlaybookRequestQuery | None = None

# Operation: update_playbook
class UpdatePlaybookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the playbook to update.")
class UpdatePlaybookRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The display name or title of the playbook.")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief overview or description of the playbook's purpose and scope.")
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL pointing to external documentation or resources related to this playbook.")
    severity_ids: list[str] | None = Field(default=None, validation_alias="severity_ids", serialization_alias="severity_ids", description="An array of Severity IDs to associate with this playbook, determining the severity levels it applies to.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="An array of Environment IDs to associate with this playbook, specifying which environments it applies to.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="An array of Service IDs to associate with this playbook, linking it to specific services.")
    functionality_ids: list[str] | None = Field(default=None, validation_alias="functionality_ids", serialization_alias="functionality_ids", description="An array of Functionality IDs to associate with this playbook, defining which functionalities it covers.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="An array of Team IDs to associate with this playbook, specifying which teams own or are responsible for it.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="An array of Incident Type IDs to associate with this playbook, indicating which incident types trigger or use this playbook.")
class UpdatePlaybookRequestBodyData(StrictModel):
    type_: Literal["playbooks"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'playbooks'.")
    attributes: UpdatePlaybookRequestBodyDataAttributes | None = None
class UpdatePlaybookRequestBody(StrictModel):
    data: UpdatePlaybookRequestBodyData
class UpdatePlaybookRequest(StrictModel):
    """Update an existing playbook with new metadata, associations, and configuration. Modify the playbook's title, summary, external reference, and linked resources such as severity levels, environments, services, functionalities, teams, and incident types."""
    path: UpdatePlaybookRequestPath
    body: UpdatePlaybookRequestBody

# Operation: delete_playbook
class DeletePlaybookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the playbook to delete.")
class DeletePlaybookRequest(StrictModel):
    """Permanently delete a playbook by its unique identifier. This action cannot be undone."""
    path: DeletePlaybookRequestPath

# Operation: list_postmortem_templates
class ListPostmortemTemplatesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related fields to include in the response (e.g., metadata, tags). Specify which additional data should be populated alongside each template.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve when paginating through results. Use with page[size] to control which set of templates is returned.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of templates to return per page. Determines the size of each paginated result set.")
class ListPostmortemTemplatesRequest(StrictModel):
    """Retrieve a paginated list of retrospective (post-mortem) templates available in the system. Use pagination parameters to control which templates are returned."""
    query: ListPostmortemTemplatesRequestQuery | None = None

# Operation: create_postmortem_template
class CreatePostmortemTemplateRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for the postmortem template that identifies its purpose or use case.")
    default: bool | None = Field(default=None, validation_alias="default", serialization_alias="default", description="When enabled, this template will be automatically selected as the default option when creating or editing postmortems.")
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The template content that defines the postmortem structure and sections. Supports Liquid template syntax for dynamic variable substitution.")
    format_: Literal["html", "markdown"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The markup format of the template content, either HTML or Markdown. Defaults to HTML if not specified.")
class CreatePostmortemTemplateRequestBodyData(StrictModel):
    type_: Literal["post_mortem_templates"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, must be set to 'post_mortem_templates' to specify this is a postmortem template resource.")
    attributes: CreatePostmortemTemplateRequestBodyDataAttributes
class CreatePostmortemTemplateRequestBody(StrictModel):
    data: CreatePostmortemTemplateRequestBodyData
class CreatePostmortemTemplateRequest(StrictModel):
    """Creates a new postmortem template that can be used as a standardized format for retrospectives. Supports Liquid template syntax for dynamic content and can be set as the default template for postmortem editing."""
    body: CreatePostmortemTemplateRequestBody

# Operation: get_postmortem_template
class GetPostmortemTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the postmortem template to retrieve.")
class GetPostmortemTemplateRequest(StrictModel):
    """Retrieves a specific postmortem (retrospective) template by its unique identifier. Use this to fetch template details for viewing or further processing."""
    path: GetPostmortemTemplateRequestPath

# Operation: update_postmortem_template
class UpdatePostmortemTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the postmortem template to update.")
class UpdatePostmortemTemplateRequestBodyDataAttributes(StrictModel):
    default: bool | None = Field(default=None, validation_alias="default", serialization_alias="default", description="Whether this template should be selected by default when creating or editing a postmortem.")
    content: str | None = Field(default=None, validation_alias="content", serialization_alias="content", description="The postmortem template content. Supports Liquid template syntax for dynamic content generation.")
    format_: Literal["html", "markdown"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The markup format of the template content. Accepts either HTML or Markdown; defaults to HTML if not specified.")
class UpdatePostmortemTemplateRequestBodyData(StrictModel):
    type_: Literal["post_mortem_templates"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'post_mortem_templates' to specify this is a postmortem template resource.")
    attributes: UpdatePostmortemTemplateRequestBodyDataAttributes | None = None
class UpdatePostmortemTemplateRequestBody(StrictModel):
    data: UpdatePostmortemTemplateRequestBodyData
class UpdatePostmortemTemplateRequest(StrictModel):
    """Update an existing postmortem/retrospective template by ID. Modify the template content, format, and default status for use in postmortem creation and editing."""
    path: UpdatePostmortemTemplateRequestPath
    body: UpdatePostmortemTemplateRequestBody

# Operation: delete_postmortem_template
class DeletePostmortemTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective template to delete.")
class DeletePostmortemTemplateRequest(StrictModel):
    """Permanently delete a specific retrospective template by its unique identifier. This action cannot be undone."""
    path: DeletePostmortemTemplateRequestPath

# Operation: list_pulses
class ListPulsesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related fields to include in the response (e.g., source details, label metadata). Specify which associations should be expanded in each pulse record.")
    filter_source: str | None = Field(default=None, validation_alias="filter[source]", serialization_alias="filter[source]", description="Filter pulses by their source identifier or name. Returns only pulses originating from the specified source.")
    filter_labels: str | None = Field(default=None, validation_alias="filter[labels]", serialization_alias="filter[labels]", description="Filter pulses by one or more labels. Specify as comma-separated values to match pulses tagged with any of the provided labels.")
    filter_refs: str | None = Field(default=None, validation_alias="filter[refs]", serialization_alias="filter[refs]", description="Filter pulses by one or more reference identifiers. Specify as comma-separated values to match pulses linked to any of the provided references.")
    filter_started_at__gte: str | None = Field(default=None, validation_alias="filter[started_at][gte]", serialization_alias="filter[started_at][gte]", description="Filter pulses by start time (greater than or equal). Specify as an ISO 8601 timestamp to include only pulses that started on or after this time.")
    filter_started_at__lte: str | None = Field(default=None, validation_alias="filter[started_at][lte]", serialization_alias="filter[started_at][lte]", description="Filter pulses by start time (less than or equal). Specify as an ISO 8601 timestamp to include only pulses that started on or before this time.")
    filter_ended_at__gte: str | None = Field(default=None, validation_alias="filter[ended_at][gte]", serialization_alias="filter[ended_at][gte]", description="Filter pulses by end time (greater than or equal). Specify as an ISO 8601 timestamp to include only pulses that ended on or after this time.")
    filter_ended_at__lte: str | None = Field(default=None, validation_alias="filter[ended_at][lte]", serialization_alias="filter[ended_at][lte]", description="Filter pulses by end time (less than or equal). Specify as an ISO 8601 timestamp to include only pulses that ended on or before this time.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve in the paginated result set. Use with page[size] to navigate through results. Defaults to the first page if not specified.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of pulses to return per page. Controls the size of each paginated batch. Adjust based on your performance and data needs.")
class ListPulsesRequest(StrictModel):
    """Retrieve a paginated list of pulses with optional filtering by source, labels, references, and time ranges. Use this to query pulse events across your system with flexible filtering and pagination controls."""
    query: ListPulsesRequestQuery | None = None

# Operation: create_pulse
class CreatePulseRequestBodyDataAttributes(StrictModel):
    source: str | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The origin system or service that generated this pulse (e.g., 'k8s' for Kubernetes, 'datadog', 'pagerduty'). Helps identify the pulse source for filtering and correlation.")
    summary: str = Field(default=..., validation_alias="summary", serialization_alias="summary", description="A brief, human-readable title describing the pulse event. This is the primary display name for the pulse.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service identifiers to associate with this pulse. Services linked to a pulse will receive or display this event. Order is not significant.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="Array of environment identifiers to associate with this pulse (e.g., 'production', 'staging'). Helps scope the pulse to specific deployment environments. Order is not significant.")
    ended_at: str | None = Field(default=None, validation_alias="ended_at", serialization_alias="ended_at", description="The timestamp when the pulse event ended or resolved, in ISO 8601 format. Omit if the pulse is ongoing.", json_schema_extra={'format': 'date-time'})
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL pointing to additional details or the source system's record of this pulse. Useful for linking to incident reports, deployment logs, or monitoring dashboards.")
    data: dict[str, Any] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="A JSON object containing custom or additional metadata about the pulse. Structure and content are flexible and depend on the pulse source and use case.")
class CreatePulseRequestBodyData(StrictModel):
    type_: Literal["pulses"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The pulse type identifier. Must be set to 'pulses' to indicate this is a pulse event.")
    attributes: CreatePulseRequestBodyDataAttributes
class CreatePulseRequestBody(StrictModel):
    data: CreatePulseRequestBodyData
class CreatePulseRequest(StrictModel):
    """Creates a new pulse event to track system incidents, deployments, or other notable occurrences. Pulses can be associated with services and environments, and may include additional metadata and external references."""
    body: CreatePulseRequestBody

# Operation: get_pulse
class GetPulseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the pulse to retrieve.")
class GetPulseRequest(StrictModel):
    """Retrieves a specific pulse by its unique identifier. Use this operation to fetch detailed information about a single pulse."""
    path: GetPulseRequestPath

# Operation: update_pulse
class UpdatePulseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the pulse to update.")
class UpdatePulseRequestBodyDataAttributes(StrictModel):
    source: str | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The origin or system that generated this pulse (e.g., 'k8s' for Kubernetes).")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A brief, human-readable summary describing the pulse event or status.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service identifiers to associate with this pulse. Order is not significant. Each item should be a valid service ID string.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="Array of environment identifiers to associate with this pulse. Order is not significant. Each item should be a valid environment ID string.")
    ended_at: str | None = Field(default=None, validation_alias="ended_at", serialization_alias="ended_at", description="The date and time when the pulse ended or was resolved, specified in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    external_url: str | None = Field(default=None, validation_alias="external_url", serialization_alias="external_url", description="A URL pointing to external resources or systems related to this pulse for additional context or details.")
    data: dict[str, Any] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="A flexible object for storing additional custom data or metadata associated with the pulse.")
class UpdatePulseRequestBodyData(StrictModel):
    attributes: UpdatePulseRequestBodyDataAttributes | None = None
class UpdatePulseRequestBody(StrictModel):
    data: UpdatePulseRequestBodyData | None = None
class UpdatePulseRequest(StrictModel):
    """Update an existing pulse with new metadata, service/environment associations, status, or custom data. Allows modification of pulse properties such as summary, source, associated services and environments, completion status, and additional contextual information."""
    path: UpdatePulseRequestPath
    body: UpdatePulseRequestBody | None = None

# Operation: list_retrospective_configurations
class ListRetrospectiveConfigurationsRequestQuery(StrictModel):
    include: Literal["severities", "groups", "incident_types"] | None = Field(default=None, description="Comma-separated list of related data to include in the response. Valid options are severities, groups, or incident_types. Omit this parameter to return only core configuration data.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of configurations to return per page. Use with page[number] to control pagination.")
    filter_kind: str | None = Field(default=None, validation_alias="filter[kind]", serialization_alias="filter[kind]", description="Filter configurations by kind. Specify the configuration kind value to narrow results to a specific type.")
class ListRetrospectiveConfigurationsRequest(StrictModel):
    """Retrieve a paginated list of retrospective configurations with optional related data. Use filtering and inclusion parameters to customize the results returned."""
    query: ListRetrospectiveConfigurationsRequestQuery | None = None

# Operation: get_retrospective_configuration
class GetRetrospectiveConfigurationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective configuration to retrieve.")
class GetRetrospectiveConfigurationRequestQuery(StrictModel):
    include: Literal["severities", "groups", "incident_types"] | None = Field(default=None, description="Optional comma-separated list of related entities to include in the response. Valid options are severities, groups, or incident_types.")
class GetRetrospectiveConfigurationRequest(StrictModel):
    """Retrieves a specific retrospective configuration by its unique identifier, with optional related data inclusion."""
    path: GetRetrospectiveConfigurationRequestPath
    query: GetRetrospectiveConfigurationRequestQuery | None = None

# Operation: update_retrospective_configuration
class UpdateRetrospectiveConfigurationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective configuration to update.")
class UpdateRetrospectiveConfigurationRequestBodyDataAttributes(StrictModel):
    severity_ids: list[str] | None = Field(default=None, validation_alias="severity_ids", serialization_alias="severity_ids", description="An array of severity IDs to associate with this retrospective configuration. Incidents matching any of these severity levels will be subject to this configuration's retrospective rules.")
    group_ids: list[str] | None = Field(default=None, validation_alias="group_ids", serialization_alias="group_ids", description="An array of team IDs to associate with this retrospective configuration. Incidents assigned to any of these teams will be subject to this configuration's retrospective rules.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="An array of incident type IDs to associate with this retrospective configuration. Incidents classified as any of these types will be subject to this configuration's retrospective rules.")
class UpdateRetrospectiveConfigurationRequestBodyData(StrictModel):
    type_: Literal["retrospective_configurations"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'retrospective_configurations' to specify the resource being updated.")
    attributes: UpdateRetrospectiveConfigurationRequestBodyDataAttributes | None = None
class UpdateRetrospectiveConfigurationRequestBody(StrictModel):
    data: UpdateRetrospectiveConfigurationRequestBodyData
class UpdateRetrospectiveConfigurationRequest(StrictModel):
    """Update an existing retrospective configuration by modifying its associated severities, teams, and incident types. This operation allows you to refine which incidents trigger retrospectives based on their severity level, assigned team, and incident classification."""
    path: UpdateRetrospectiveConfigurationRequestPath
    body: UpdateRetrospectiveConfigurationRequestBody

# Operation: list_retrospective_process_group_steps
class ListRetrospectiveProcessGroupStepsRequestPath(StrictModel):
    retrospective_process_group_id: str = Field(default=..., description="The unique identifier of the retrospective process group whose steps you want to list.")
class ListRetrospectiveProcessGroupStepsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., nested objects or associations).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of steps to return per page. Adjust this value along with page[number] to control result set size.")
    filter_retrospective_step_id: str | None = Field(default=None, validation_alias="filter[retrospective_step_id]", serialization_alias="filter[retrospective_step_id]", description="Filter results by retrospective step ID. Accepts a single step identifier to narrow the list to matching steps.")
class ListRetrospectiveProcessGroupStepsRequest(StrictModel):
    """Retrieve a paginated list of steps within a specific retrospective process group. Use filtering and inclusion options to customize the results."""
    path: ListRetrospectiveProcessGroupStepsRequestPath
    query: ListRetrospectiveProcessGroupStepsRequestQuery | None = None

# Operation: get_retrospective_process_group_step
class GetRetrospectiveProcessGroupStepRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective process group step to retrieve.")
class GetRetrospectiveProcessGroupStepRequest(StrictModel):
    """Retrieves a specific retrospective process group step by its unique identifier. Use this to fetch detailed information about a single step within a retrospective process group."""
    path: GetRetrospectiveProcessGroupStepRequestPath

# Operation: list_retrospective_process_groups
class ListRetrospectiveProcessGroupsRequestPath(StrictModel):
    retrospective_process_id: str = Field(default=..., description="The unique identifier of the retrospective process containing the groups to list.")
class ListRetrospectiveProcessGroupsRequestQuery(StrictModel):
    include: Literal["retrospective_process_group_steps"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Use 'retrospective_process_group_steps' to embed step details within each group.")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(default=None, description="Comma-separated list of fields to sort results by. Prefix with hyphen (e.g., '-created_at') for descending order. Available fields: created_at, updated_at, and position.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination (1-indexed). Use with page[size] to retrieve specific result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results per page for pagination. Determines how many groups are returned in each page.")
    filter_sub_status_id: str | None = Field(default=None, validation_alias="filter[sub_status_id]", serialization_alias="filter[sub_status_id]", description="Filter results by a specific sub-status identifier to return only groups matching that sub-status.")
class ListRetrospectiveProcessGroupsRequest(StrictModel):
    """Retrieve all groups within a specific retrospective process. Supports filtering, sorting, and optional inclusion of nested group steps."""
    path: ListRetrospectiveProcessGroupsRequestPath
    query: ListRetrospectiveProcessGroupsRequestQuery | None = None

# Operation: get_retrospective_process_group
class GetRetrospectiveProcessGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Retrospective Process Group to retrieve.")
class GetRetrospectiveProcessGroupRequestQuery(StrictModel):
    include: Literal["retrospective_process_group_steps"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Use 'retrospective_process_group_steps' to include the process group's associated steps.")
class GetRetrospectiveProcessGroupRequest(StrictModel):
    """Retrieves a specific Retrospective Process Group by its unique identifier. Optionally include related process group steps in the response."""
    path: GetRetrospectiveProcessGroupRequestPath
    query: GetRetrospectiveProcessGroupRequestQuery | None = None

# Operation: list_retrospective_processes
class ListRetrospectiveProcessesRequestQuery(StrictModel):
    include: Literal["retrospective_steps", "severities", "incident_types", "groups"] | None = Field(default=None, description="Comma-separated list of related entities to include in the response. Valid options are: retrospective_steps, severities, incident_types, and groups. Omit this parameter to return only core retrospective process data.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through result sets when combined with page size.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of retrospective processes to return per page. Use this to control result set size for pagination.")
class ListRetrospectiveProcessesRequest(StrictModel):
    """Retrieve a paginated list of retrospective processes with optional related data. Use the include parameter to expand the response with associated retrospective steps, severity levels, incident types, or groups."""
    query: ListRetrospectiveProcessesRequestQuery | None = None

# Operation: create_retrospective_process
class CreateRetrospectiveProcessRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for the retrospective process that will be displayed in your team's workflow.")
    copy_from: str = Field(default=..., validation_alias="copy_from", serialization_alias="copy_from", description="The source for retrospective steps: either the ID of an existing retrospective process to copy steps from, or the literal value 'starter_template' to use a pre-configured template of standard retrospective steps.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="An optional detailed description of the retrospective process's purpose, scope, or any special instructions for participants.")
    retrospective_process_matching_criteria: CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0 | CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1 | CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2 | None = Field(default=None, validation_alias="retrospective_process_matching_criteria", serialization_alias="retrospective_process_matching_criteria", description="Optional criteria object used to automatically match and assign retrospective processes to relevant teams, projects, or other entities based on specified conditions.")
class CreateRetrospectiveProcessRequestBodyData(StrictModel):
    type_: Literal["retrospective_processes"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'retrospective_processes' to indicate this operation creates a retrospective process resource.")
    attributes: CreateRetrospectiveProcessRequestBodyDataAttributes
class CreateRetrospectiveProcessRequestBody(StrictModel):
    data: CreateRetrospectiveProcessRequestBodyData
class CreateRetrospectiveProcessRequest(StrictModel):
    """Creates a new retrospective process with optional configuration for copying steps from an existing process or starter template. Use this to set up a structured retrospective workflow for your team."""
    body: CreateRetrospectiveProcessRequestBody

# Operation: get_retrospective_process
class GetRetrospectiveProcessRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective process to retrieve.")
class GetRetrospectiveProcessRequestQuery(StrictModel):
    include: Literal["retrospective_steps", "severities", "incident_types", "groups"] | None = Field(default=None, description="Comma-separated list of related entities to include in the response. Valid options are retrospective_steps, severities, incident_types, and groups.")
class GetRetrospectiveProcessRequest(StrictModel):
    """Retrieves a specific retrospective process by its unique identifier, with optional related data expansion."""
    path: GetRetrospectiveProcessRequestPath
    query: GetRetrospectiveProcessRequestQuery | None = None

# Operation: update_retrospective_process
class UpdateRetrospectiveProcessRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective process to update.")
class UpdateRetrospectiveProcessRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the retrospective process, explaining its purpose and scope.")
    retrospective_process_matching_criteria: UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0 | UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1 | UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2 | None = Field(default=None, validation_alias="retrospective_process_matching_criteria", serialization_alias="retrospective_process_matching_criteria", description="Criteria object that defines the matching rules for identifying which retrospectives belong to this process. Specifies conditions such as team, project, or time-based filters.")
class UpdateRetrospectiveProcessRequestBodyData(StrictModel):
    type_: Literal["retrospective_processes"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'retrospective_processes' to specify the entity being updated.")
    attributes: UpdateRetrospectiveProcessRequestBodyDataAttributes | None = None
class UpdateRetrospectiveProcessRequestBody(StrictModel):
    data: UpdateRetrospectiveProcessRequestBodyData
class UpdateRetrospectiveProcessRequest(StrictModel):
    """Updates an existing retrospective process with new configuration details. Allows modification of the process description and matching criteria to refine how retrospectives are identified and organized."""
    path: UpdateRetrospectiveProcessRequestPath
    body: UpdateRetrospectiveProcessRequestBody

# Operation: delete_retrospective_process
class DeleteRetrospectiveProcessRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective process to delete.")
class DeleteRetrospectiveProcessRequest(StrictModel):
    """Permanently delete a retrospective process and all associated data by its unique identifier."""
    path: DeleteRetrospectiveProcessRequestPath

# Operation: list_retrospective_steps
class ListRetrospectiveStepsRequestPath(StrictModel):
    retrospective_process_id: str = Field(default=..., description="The unique identifier of the retrospective process containing the steps to retrieve.")
class ListRetrospectiveStepsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., participants, feedback, outcomes). Reduces need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of retrospective steps to return per page. Adjust to balance response size and number of requests needed.")
    sort: str | None = Field(default=None, description="Sort results by specified field(s) in ascending or descending order. Use format: field_name or -field_name for reverse order (e.g., created_at or -created_at).")
class ListRetrospectiveStepsRequest(StrictModel):
    """Retrieve a paginated list of retrospective steps for a specific retrospective process. Use pagination and sorting parameters to customize the results."""
    path: ListRetrospectiveStepsRequestPath
    query: ListRetrospectiveStepsRequestQuery | None = None

# Operation: create_retrospective_step
class CreateRetrospectiveStepRequestPath(StrictModel):
    retrospective_process_id: str = Field(default=..., description="The unique identifier of the retrospective process to which this step belongs.")
class CreateRetrospectiveStepRequestBodyDataAttributes(StrictModel):
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="The display name for this retrospective step.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Additional context or instructions for participants about what to do during this step.")
    due_after_days: int | None = Field(default=None, validation_alias="due_after_days", serialization_alias="due_after_days", description="Number of days after the retrospective starts when this step becomes due. Helps schedule step progression over time.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this step within the retrospective process sequence. Lower numbers appear first.")
    skippable: bool | None = Field(default=None, validation_alias="skippable", serialization_alias="skippable", description="Whether participants can skip this step if needed. When true, the step can be bypassed; when false, it must be completed.")
class CreateRetrospectiveStepRequestBodyData(StrictModel):
    type_: Literal["retrospective_steps"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this operation, which must be set to 'retrospective_steps'.")
    attributes: CreateRetrospectiveStepRequestBodyDataAttributes
class CreateRetrospectiveStepRequestBody(StrictModel):
    data: CreateRetrospectiveStepRequestBodyData
class CreateRetrospectiveStepRequest(StrictModel):
    """Creates a new step within a retrospective process. Steps define discrete phases or activities that guide the retrospective workflow."""
    path: CreateRetrospectiveStepRequestPath
    body: CreateRetrospectiveStepRequestBody

# Operation: get_retrospective_step
class GetRetrospectiveStepRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective step to retrieve.")
class GetRetrospectiveStepRequest(StrictModel):
    """Retrieves a specific retrospective step by its unique identifier. Use this to fetch details about a single retrospective step within a retrospective."""
    path: GetRetrospectiveStepRequestPath

# Operation: update_retrospective_step
class UpdateRetrospectiveStepRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective step to update.")
class UpdateRetrospectiveStepRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The display name or title of the retrospective step.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation of the retrospective step's purpose and content.")
    due_after_days: int | None = Field(default=None, validation_alias="due_after_days", serialization_alias="due_after_days", description="The number of days after retrospective creation when this step becomes due.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this step within the retrospective sequence, determining its display order.")
    skippable: bool | None = Field(default=None, validation_alias="skippable", serialization_alias="skippable", description="Whether participants can skip this step during the retrospective process.")
class UpdateRetrospectiveStepRequestBodyData(StrictModel):
    type_: Literal["retrospective_steps"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'retrospective_steps' to specify the entity being updated.")
    attributes: UpdateRetrospectiveStepRequestBodyDataAttributes | None = None
class UpdateRetrospectiveStepRequestBody(StrictModel):
    data: UpdateRetrospectiveStepRequestBodyData
class UpdateRetrospectiveStepRequest(StrictModel):
    """Update a specific retrospective step by its ID. Modify step details such as title, description, timing, position, and skippability to refine your retrospective workflow."""
    path: UpdateRetrospectiveStepRequestPath
    body: UpdateRetrospectiveStepRequestBody

# Operation: delete_retrospective_step
class DeleteRetrospectiveStepRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the retrospective step to delete.")
class DeleteRetrospectiveStepRequest(StrictModel):
    """Permanently delete a retrospective step by its unique identifier. This action cannot be undone."""
    path: DeleteRetrospectiveStepRequestPath

# Operation: list_roles
class ListRolesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., permissions, users). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for paginated results, starting from 1. Use with page[size] to control pagination.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of roles to return per page. Adjust this value to balance between response size and number of requests needed.")
    sort: str | None = Field(default=None, description="Sort the results by one or more fields using a comma-separated list. Prefix field names with a minus sign (-) to sort in descending order (e.g., -created_at,name).")
class ListRolesRequest(StrictModel):
    """Retrieve a paginated list of all available roles in the system. Supports filtering, sorting, and customizable pagination."""
    query: ListRolesRequestQuery | None = None

# Operation: get_role
class GetRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the role to retrieve.")
class GetRoleRequest(StrictModel):
    """Retrieves a specific role by its unique identifier. Use this operation to fetch detailed information about a role."""
    path: GetRoleRequestPath

# Operation: delete_role
class DeleteRoleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the role to delete.")
class DeleteRoleRequest(StrictModel):
    """Permanently delete a role by its unique identifier. This action removes the role and its associated permissions from the system."""
    path: DeleteRoleRequestPath

# Operation: list_schedule_rotation_active_days
class ListScheduleRotationActiveDaysRequestPath(StrictModel):
    schedule_rotation_id: str = Field(default=..., description="The unique identifier of the schedule rotation for which to list active days.")
class ListScheduleRotationActiveDaysRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., schedule, users). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of active days to return per page. Adjust to balance response size and number of requests needed.")
class ListScheduleRotationActiveDaysRequest(StrictModel):
    """Retrieve a paginated list of active days for a specific schedule rotation. Active days define when the rotation is in effect."""
    path: ListScheduleRotationActiveDaysRequestPath
    query: ListScheduleRotationActiveDaysRequestQuery | None = None

# Operation: add_active_day_to_schedule_rotation
class CreateScheduleRotationActiveDayRequestPath(StrictModel):
    schedule_rotation_id: str = Field(default=..., description="The unique identifier of the schedule rotation to which the active day will be added.")
class CreateScheduleRotationActiveDayRequestBodyDataAttributes(StrictModel):
    day_name: Literal["S", "M", "T", "W", "R", "F", "U"] = Field(default=..., validation_alias="day_name", serialization_alias="day_name", description="The day of the week for which active times are being configured. Use single-letter abbreviations: S (Sunday), M (Monday), T (Tuesday), W (Wednesday), R (Thursday), F (Friday), or U (Sunday alternate).")
    active_time_attributes: list[CreateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem] = Field(default=..., validation_alias="active_time_attributes", serialization_alias="active_time_attributes", description="An ordered array of active time periods for the specified day. Each item defines a time window when the schedule rotation is active. Order matters and determines the sequence of active periods throughout the day.")
class CreateScheduleRotationActiveDayRequestBodyData(StrictModel):
    type_: Literal["schedule_rotation_active_days"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'schedule_rotation_active_days' to indicate this is a schedule rotation active day resource.")
    attributes: CreateScheduleRotationActiveDayRequestBodyDataAttributes
class CreateScheduleRotationActiveDayRequestBody(StrictModel):
    data: CreateScheduleRotationActiveDayRequestBodyData
class CreateScheduleRotationActiveDayRequest(StrictModel):
    """Adds an active day with specified time slots to a schedule rotation. This defines when the rotation is active for a particular day of the week."""
    path: CreateScheduleRotationActiveDayRequestPath
    body: CreateScheduleRotationActiveDayRequestBody

# Operation: get_schedule_rotation_active_day
class GetScheduleRotationActiveDayRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation active day to retrieve.")
class GetScheduleRotationActiveDayRequest(StrictModel):
    """Retrieves a specific schedule rotation active day by its unique identifier. Use this to fetch details about a particular day within a schedule rotation."""
    path: GetScheduleRotationActiveDayRequestPath

# Operation: update_schedule_rotation_active_day
class UpdateScheduleRotationActiveDayRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation active day record to update.")
class UpdateScheduleRotationActiveDayRequestBodyDataAttributes(StrictModel):
    day_name: Literal["S", "M", "T", "W", "R", "F", "U"] | None = Field(default=None, validation_alias="day_name", serialization_alias="day_name", description="The day of the week for which active times apply, using single-letter abbreviations: S (Sunday), M (Monday), T (Tuesday), W (Wednesday), R (Thursday), F (Friday), or U (Sunday alternate).")
    active_time_attributes: list[UpdateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem] | None = Field(default=None, validation_alias="active_time_attributes", serialization_alias="active_time_attributes", description="An ordered array of active time period objects that define when the schedule rotation is active on the specified day. Each item configures a time window with start and end times.")
class UpdateScheduleRotationActiveDayRequestBodyData(StrictModel):
    type_: Literal["schedule_rotation_active_days"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'schedule_rotation_active_days' to specify the type of object being updated.")
    attributes: UpdateScheduleRotationActiveDayRequestBodyDataAttributes | None = None
class UpdateScheduleRotationActiveDayRequestBody(StrictModel):
    data: UpdateScheduleRotationActiveDayRequestBodyData
class UpdateScheduleRotationActiveDayRequest(StrictModel):
    """Update the active times for a specific day within a schedule rotation. Modify which day of the week is active and configure the active time periods for that day."""
    path: UpdateScheduleRotationActiveDayRequestPath
    body: UpdateScheduleRotationActiveDayRequestBody

# Operation: delete_schedule_rotation_active_day
class DeleteScheduleRotationActiveDayRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation active day to delete.")
class DeleteScheduleRotationActiveDayRequest(StrictModel):
    """Remove a specific schedule rotation active day from the system. This operation permanently deletes the identified active day configuration."""
    path: DeleteScheduleRotationActiveDayRequestPath

# Operation: list_schedule_rotation_users
class ListScheduleRotationUsersRequestPath(StrictModel):
    schedule_rotation_id: str = Field(default=..., description="The unique identifier of the schedule rotation for which to list assigned users.")
class ListScheduleRotationUsersRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., user details, rotation metadata). Specify which associations to expand for richer response data.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through result sets when the total exceeds the page size.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of users to return per page. Adjust this to control the size of each paginated response.")
class ListScheduleRotationUsersRequest(StrictModel):
    """Retrieve a paginated list of users assigned to a specific schedule rotation. Use this to view all participants in a rotation schedule with optional filtering and pagination controls."""
    path: ListScheduleRotationUsersRequestPath
    query: ListScheduleRotationUsersRequestQuery | None = None

# Operation: add_user_to_schedule_rotation
class CreateScheduleRotationUserRequestPath(StrictModel):
    schedule_rotation_id: str = Field(default=..., description="The unique identifier of the schedule rotation to which the user will be added.")
class CreateScheduleRotationUserRequestBodyDataAttributes(StrictModel):
    user_id: int = Field(default=..., validation_alias="user_id", serialization_alias="user_id", description="The unique identifier of the user to add to the schedule rotation.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The position where the user should be placed in the rotation sequence. If not specified, the user will be added at the end of the rotation.")
class CreateScheduleRotationUserRequestBodyData(StrictModel):
    attributes: CreateScheduleRotationUserRequestBodyDataAttributes
class CreateScheduleRotationUserRequestBody(StrictModel):
    data: CreateScheduleRotationUserRequestBodyData
class CreateScheduleRotationUserRequest(StrictModel):
    """Adds a user to an existing schedule rotation, optionally specifying their position in the rotation order."""
    path: CreateScheduleRotationUserRequestPath
    body: CreateScheduleRotationUserRequestBody

# Operation: get_schedule_rotation_user
class GetScheduleRotationUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation user to retrieve.")
class GetScheduleRotationUserRequest(StrictModel):
    """Retrieves a specific schedule rotation user by their unique identifier. Use this to fetch details about an individual user assigned to a schedule rotation."""
    path: GetScheduleRotationUserRequestPath

# Operation: update_schedule_rotation_user
class UpdateScheduleRotationUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation user record to update.")
class UpdateScheduleRotationUserRequestBodyDataAttributes(StrictModel):
    user_id: int | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="The ID of the user to assign to this rotation slot.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The sequential position of this user within the rotation order, determining when they are scheduled.")
class UpdateScheduleRotationUserRequestBodyData(StrictModel):
    type_: Literal["schedule_rotation_users"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'schedule_rotation_users' to specify the target resource type.")
    attributes: UpdateScheduleRotationUserRequestBodyDataAttributes | None = None
class UpdateScheduleRotationUserRequestBody(StrictModel):
    data: UpdateScheduleRotationUserRequestBodyData
class UpdateScheduleRotationUserRequest(StrictModel):
    """Update a specific user's position and assignment within a schedule rotation by their unique identifier."""
    path: UpdateScheduleRotationUserRequestPath
    body: UpdateScheduleRotationUserRequestBody

# Operation: delete_schedule_rotation_user
class DeleteScheduleRotationUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation user to delete.")
class DeleteScheduleRotationUserRequest(StrictModel):
    """Remove a schedule rotation user from the system by their unique identifier. This operation permanently deletes the specified schedule rotation user record."""
    path: DeleteScheduleRotationUserRequestPath

# Operation: list_schedule_rotations
class ListScheduleRotationsRequestPath(StrictModel):
    schedule_id: str = Field(default=..., description="The unique identifier of the schedule for which to list rotations.")
class ListScheduleRotationsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., users, shifts). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for paginated results, starting from 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of rotations to return per page. Adjust to balance response size and number of requests needed.")
    sort: str | None = Field(default=None, description="Sort results by specified field(s) in ascending or descending order. Use format: field_name or -field_name for descending order.")
class ListScheduleRotationsRequest(StrictModel):
    """Retrieve a paginated list of schedule rotations for a specific schedule. Use pagination and sorting parameters to customize the results."""
    path: ListScheduleRotationsRequestPath
    query: ListScheduleRotationsRequestQuery | None = None

# Operation: create_schedule_rotation
class CreateScheduleRotationRequestPath(StrictModel):
    schedule_id: str = Field(default=..., description="The unique identifier of the schedule to which this rotation will be added.")
class CreateScheduleRotationRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A human-readable name for this schedule rotation.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this rotation within the schedule's rotation sequence; determines the order in which rotations are applied.")
    schedule_rotationable_type: Literal["ScheduleDailyRotation", "ScheduleWeeklyRotation", "ScheduleBiweeklyRotation", "ScheduleMonthlyRotation", "ScheduleCustomRotation"] = Field(default=..., validation_alias="schedule_rotationable_type", serialization_alias="schedule_rotationable_type", description="The rotation pattern type: daily, weekly, biweekly, monthly, or custom. This determines how the rotation cycles through team members.")
    active_days: list[Literal["S", "M", "T", "W", "R", "F", "U"]] | None = Field(default=None, validation_alias="active_days", serialization_alias="active_days", description="An array of days when this rotation is active; typically specified as day-of-week identifiers or date values depending on the rotation type.")
    active_time_attributes: list[CreateScheduleRotationBodyDataAttributesActiveTimeAttributesItem] | None = Field(default=None, validation_alias="active_time_attributes", serialization_alias="active_time_attributes", description="An array of time windows during which this rotation applies; each entry defines when on-call coverage is active for this rotation.")
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="The IANA time zone name (e.g., 'America/New_York', 'Europe/London') used to interpret active times and rotation schedules; defaults to UTC if not specified.")
    schedule_rotationable_attributes: CreateScheduleRotationBodyDataAttributesScheduleRotationableAttributes = Field(default=..., validation_alias="schedule_rotationable_attributes", serialization_alias="schedule_rotationable_attributes", description="Configuration object containing rotation-specific parameters; structure varies based on the selected rotation type (e.g., interval length for custom rotations, day-of-month for monthly rotations).")
class CreateScheduleRotationRequestBodyData(StrictModel):
    type_: Literal["schedule_rotations"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'schedule_rotations'.")
    attributes: CreateScheduleRotationRequestBodyDataAttributes
class CreateScheduleRotationRequestBody(StrictModel):
    data: CreateScheduleRotationRequestBodyData
class CreateScheduleRotationRequest(StrictModel):
    """Creates a new schedule rotation within a schedule, defining how on-call shifts rotate across team members. Specify the rotation type (daily, weekly, biweekly, monthly, or custom), active times, and rotation-specific configuration."""
    path: CreateScheduleRotationRequestPath
    body: CreateScheduleRotationRequestBody

# Operation: get_schedule_rotation
class GetScheduleRotationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation to retrieve.")
class GetScheduleRotationRequest(StrictModel):
    """Retrieves a specific schedule rotation by its unique identifier. Use this to fetch details about a particular rotation configuration."""
    path: GetScheduleRotationRequestPath

# Operation: update_schedule_rotation
class UpdateScheduleRotationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation to update.")
class UpdateScheduleRotationRequestBodyDataAttributes(StrictModel):
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The ordinal position of this schedule rotation in the sequence, used to determine rotation order.")
    schedule_rotationable_type: Literal["ScheduleDailyRotation", "ScheduleWeeklyRotation", "ScheduleBiweeklyRotation", "ScheduleMonthlyRotation", "ScheduleCustomRotation"] = Field(default=..., validation_alias="schedule_rotationable_type", serialization_alias="schedule_rotationable_type", description="The rotation pattern type: daily, weekly, biweekly, monthly, or custom rotation schedules.")
    active_days: list[Literal["S", "M", "T", "W", "R", "F", "U"]] | None = Field(default=None, validation_alias="active_days", serialization_alias="active_days", description="An array of days when the rotation is active. Order and format depend on the selected rotation type.")
    active_time_attributes: list[UpdateScheduleRotationBodyDataAttributesActiveTimeAttributesItem] | None = Field(default=None, validation_alias="active_time_attributes", serialization_alias="active_time_attributes", description="An array of time window objects defining when the rotation applies each day, including start and end times.")
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="The IANA timezone identifier for interpreting all times in this rotation (defaults to Etc/UTC if not specified).")
    schedule_rotationable_attributes: UpdateScheduleRotationBodyDataAttributesScheduleRotationableAttributes | None = Field(default=None, validation_alias="schedule_rotationable_attributes", serialization_alias="schedule_rotationable_attributes", description="Configuration object containing rotation-specific parameters that vary based on the selected rotation type.")
class UpdateScheduleRotationRequestBodyData(StrictModel):
    type_: Literal["schedule_rotations"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'schedule_rotations' to specify this is a schedule rotation resource.")
    attributes: UpdateScheduleRotationRequestBodyDataAttributes
class UpdateScheduleRotationRequestBody(StrictModel):
    data: UpdateScheduleRotationRequestBodyData
class UpdateScheduleRotationRequest(StrictModel):
    """Update an existing schedule rotation configuration, including its rotation type, active days, time windows, and timezone settings."""
    path: UpdateScheduleRotationRequestPath
    body: UpdateScheduleRotationRequestBody

# Operation: delete_schedule_rotation
class DeleteScheduleRotationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule rotation to delete.")
class DeleteScheduleRotationRequest(StrictModel):
    """Permanently delete a schedule rotation by its unique identifier. This action cannot be undone."""
    path: DeleteScheduleRotationRequestPath

# Operation: list_schedules
class ListSchedulesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related fields to include in the response, such as associated resources or metadata.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve when paginating through results, starting from page 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of schedules to return per page. Adjust this value to control the size of each paginated response.")
class ListSchedulesRequest(StrictModel):
    """Retrieve a paginated list of schedules. Use pagination parameters to control the number of results and navigate through pages."""
    query: ListSchedulesRequestQuery | None = None

# Operation: create_schedule
class CreateScheduleRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the schedule; used to identify the schedule in the system.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional details about the schedule's purpose, scope, or other contextual information.")
    all_time_coverage: bool | None = Field(default=None, validation_alias="all_time_coverage", serialization_alias="all_time_coverage", description="When enabled, indicates the schedule provides continuous 24/7 coverage; when disabled, coverage is limited to specified time periods.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="List of team IDs that will own and manage this schedule; teams can have shared ownership of a single schedule.")
    owner_user_id: int | None = Field(default=None, validation_alias="owner_user_id", serialization_alias="owner_user_id", description="The numeric ID of the user who owns this schedule; takes precedence over team ownership if both are specified.")
class CreateScheduleRequestBodyData(StrictModel):
    type_: Literal["schedules"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'schedules' to indicate this is a schedule resource.")
    attributes: CreateScheduleRequestBodyDataAttributes
class CreateScheduleRequestBody(StrictModel):
    data: CreateScheduleRequestBodyData
class CreateScheduleRequest(StrictModel):
    """Creates a new schedule with specified coverage settings and ownership. Use this to set up on-call schedules with optional 24/7 coverage and team or user ownership."""
    body: CreateScheduleRequestBody

# Operation: get_schedule
class GetScheduleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to retrieve.")
class GetScheduleRequest(StrictModel):
    """Retrieves a specific schedule by its unique identifier. Use this operation to fetch detailed information about a schedule."""
    path: GetScheduleRequestPath

# Operation: update_schedule
class UpdateScheduleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to update.")
class UpdateScheduleRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the schedule.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the schedule's purpose and scope.")
    all_time_coverage: bool | None = Field(default=None, validation_alias="all_time_coverage", serialization_alias="all_time_coverage", description="When enabled, indicates the schedule provides continuous 24/7 coverage.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="A list of team or group identifiers that own and manage this schedule. Order and format follow the API's standard array serialization.")
    owner_user_id: int | None = Field(default=None, validation_alias="owner_user_id", serialization_alias="owner_user_id", description="The numeric identifier of the user responsible for owning and administering this schedule.")
class UpdateScheduleRequestBodyData(StrictModel):
    type_: Literal["schedules"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'schedules' to specify this operation targets schedule resources.")
    attributes: UpdateScheduleRequestBodyDataAttributes | None = None
class UpdateScheduleRequestBody(StrictModel):
    data: UpdateScheduleRequestBodyData
class UpdateScheduleRequest(StrictModel):
    """Updates an existing schedule with new configuration details such as name, description, coverage settings, and ownership assignments."""
    path: UpdateScheduleRequestPath
    body: UpdateScheduleRequestBody

# Operation: delete_schedule
class DeleteScheduleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to delete.")
class DeleteScheduleRequest(StrictModel):
    """Permanently delete a schedule by its unique identifier. This action cannot be undone."""
    path: DeleteScheduleRequestPath

# Operation: list_schedule_shifts
class GetScheduleShiftsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule whose shifts you want to retrieve.")
class GetScheduleShiftsRequestQuery(StrictModel):
    to: str | None = Field(default=None, description="Optional end date for filtering shifts. Shifts on or before this date will be included in the results. Use ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Optional start date for filtering shifts. Shifts on or after this date will be included in the results. Use ISO 8601 format.")
class GetScheduleShiftsRequest(StrictModel):
    """Retrieves all shifts for a specific schedule, with optional filtering by date range. Use this to view scheduled shifts within a given time period."""
    path: GetScheduleShiftsRequestPath
    query: GetScheduleShiftsRequestQuery | None = None

# Operation: get_secret
class GetSecretRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the secret to retrieve.")
class GetSecretRequest(StrictModel):
    """Retrieve a specific secret by its unique identifier. Returns the secret details if found and accessible."""
    path: GetSecretRequestPath

# Operation: update_secret
class UpdateSecretRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the secret to update.")
class UpdateSecretRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the secret. Used to identify and reference the secret.")
    secret: str | None = Field(default=None, validation_alias="secret", serialization_alias="secret", description="The secret value or credential data to store.")
    hashicorp_vault_mount: str | None = Field(default=None, validation_alias="hashicorp_vault_mount", serialization_alias="hashicorp_vault_mount", description="The HashiCorp Vault secret mount path where the secret is stored. Defaults to 'secret' if not specified.")
    hashicorp_vault_path: str | None = Field(default=None, validation_alias="hashicorp_vault_path", serialization_alias="hashicorp_vault_path", description="The path within the HashiCorp Vault mount where the secret is located.")
    hashicorp_vault_version: int | None = Field(default=None, validation_alias="hashicorp_vault_version", serialization_alias="hashicorp_vault_version", description="The version number of the secret in HashiCorp Vault. Defaults to 0 (latest version) if not specified.")
class UpdateSecretRequestBodyData(StrictModel):
    type_: Literal["secrets"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'secrets' for this operation.")
    attributes: UpdateSecretRequestBodyDataAttributes
class UpdateSecretRequestBody(StrictModel):
    data: UpdateSecretRequestBodyData
class UpdateSecretRequest(StrictModel):
    """Update an existing secret by its ID. Modify the secret's name, value, and HashiCorp Vault configuration settings."""
    path: UpdateSecretRequestPath
    body: UpdateSecretRequestBody

# Operation: delete_secret
class DeleteSecretRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the secret to delete.")
class DeleteSecretRequest(StrictModel):
    """Permanently delete a secret by its unique identifier. This action cannot be undone."""
    path: DeleteSecretRequestPath

# Operation: list_services
class ListServicesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., owners, tags, metadata).")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination, starting from 1. Use with page[size] to control result set boundaries.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of services to return per page. Defines the maximum number of results in each paginated response.")
    filter_backstage_id: str | None = Field(default=None, validation_alias="filter[backstage_id]", serialization_alias="filter[backstage_id]", description="Filter services by their Backstage identifier. Returns only services matching this exact ID.")
    filter_cortex_id: str | None = Field(default=None, validation_alias="filter[cortex_id]", serialization_alias="filter[cortex_id]", description="Filter services by their Cortex identifier. Returns only services matching this exact ID.")
    filter_opslevel_id: str | None = Field(default=None, validation_alias="filter[opslevel_id]", serialization_alias="filter[opslevel_id]", description="Filter services by their OpsLevel identifier. Returns only services matching this exact ID.")
    filter_external_id: str | None = Field(default=None, validation_alias="filter[external_id]", serialization_alias="filter[external_id]", description="Filter services by their external system identifier. Returns only services matching this exact ID.")
    sort: str | None = Field(default=None, description="Sort results by specified field(s). Use format like 'name' or 'name,-created_at' for ascending/descending order.")
class ListServicesRequest(StrictModel):
    """Retrieve a paginated list of services with optional filtering by external system identifiers and sorting capabilities."""
    query: ListServicesRequestQuery | None = None

# Operation: create_service
class CreateServiceRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the service.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Internal description of the service for team reference.")
    public_description: str | None = Field(default=None, validation_alias="public_description", serialization_alias="public_description", description="Public-facing description of the service visible to external stakeholders.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="Email addresses to receive service notifications; accepts multiple values.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hex color code for visual identification of the service in dashboards and lists.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="Display order of the service in lists and navigation; lower values appear first.")
    show_uptime: bool | None = Field(default=None, validation_alias="show_uptime", serialization_alias="show_uptime", description="Whether to display uptime metrics for this service.")
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(default=None, validation_alias="show_uptime_last_days", serialization_alias="show_uptime_last_days", description="Time window for uptime calculation; choose from 30, 60, or 90 days (defaults to 60 days).")
    backstage_id: str | None = Field(default=None, validation_alias="backstage_id", serialization_alias="backstage_id", description="Backstage entity identifier in the format namespace/kind/entity_name for catalog integration.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="External system identifier for cross-platform service tracking.")
    opsgenie_team_id: str | None = Field(default=None, validation_alias="opsgenie_team_id", serialization_alias="opsgenie_team_id", description="Opsgenie team identifier for incident management integration.")
    cortex_id: str | None = Field(default=None, validation_alias="cortex_id", serialization_alias="cortex_id", description="Cortex group identifier for service grouping and organization.")
    service_now_ci_sys_id: str | None = Field(default=None, validation_alias="service_now_ci_sys_id", serialization_alias="service_now_ci_sys_id", description="ServiceNow configuration item system ID for ITSM integration.")
    github_repository_name: str | None = Field(default=None, validation_alias="github_repository_name", serialization_alias="github_repository_name", description="GitHub repository identifier in the format owner/repository_name.")
    github_repository_branch: str | None = Field(default=None, validation_alias="github_repository_branch", serialization_alias="github_repository_branch", description="GitHub branch name (e.g., main, develop) for source code tracking.")
    gitlab_repository_name: str | None = Field(default=None, validation_alias="gitlab_repository_name", serialization_alias="gitlab_repository_name", description="GitLab repository identifier in the format group/project_name.")
    gitlab_repository_branch: str | None = Field(default=None, validation_alias="gitlab_repository_branch", serialization_alias="gitlab_repository_branch", description="GitLab branch name (e.g., main, develop) for source code tracking.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="IDs of environments where this service is deployed; accepts multiple values.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="IDs of services that depend on this service; accepts multiple values to define service dependencies.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="IDs of teams with ownership responsibility for this service; accepts multiple values.")
    owner_user_ids: list[int] | None = Field(default=None, validation_alias="owner_user_ids", serialization_alias="owner_user_ids", description="IDs of individual users with ownership responsibility for this service; accepts multiple values.")
    alerts_email_enabled: bool | None = Field(default=None, validation_alias="alerts_email_enabled", serialization_alias="alerts_email_enabled", description="Enable email notifications for service alerts and incidents.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="Alert urgency level ID that determines notification priority and escalation behavior.")
    slack_channels: list[CreateServiceBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="Slack channel identifiers for service notifications; accepts multiple channels.")
    slack_aliases: list[CreateServiceBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="Slack aliases or mentions (e.g., @service-team) for automated notifications; accepts multiple values.")
class CreateServiceRequestBodyData(StrictModel):
    type_: Literal["services"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'services'.")
    attributes: CreateServiceRequestBodyDataAttributes
class CreateServiceRequestBody(StrictModel):
    data: CreateServiceRequestBodyData
class CreateServiceRequest(StrictModel):
    """Creates a new service with optional integrations, ownership, and monitoring configuration. Supports linking to external systems like GitHub, GitLab, Backstage, Opsgenie, and ServiceNow."""
    body: CreateServiceRequestBody

# Operation: get_service
class GetServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to retrieve.")
class GetServiceRequest(StrictModel):
    """Retrieves a specific service by its unique identifier. Use this operation to fetch detailed information about a single service."""
    path: GetServiceRequestPath

# Operation: update_service
class UpdateServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to update.")
class UpdateServiceRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Internal description of the service for team reference.")
    public_description: str | None = Field(default=None, validation_alias="public_description", serialization_alias="public_description", description="Public-facing description of the service visible to external stakeholders.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="Email addresses to receive notifications related to this service. Provide as a list of valid email addresses.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="Hexadecimal color code for visual identification of the service in dashboards and lists.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="Display order of the service in lists and navigation. Lower numbers appear first.")
    backstage_id: str | None = Field(default=None, validation_alias="backstage_id", serialization_alias="backstage_id", description="Backstage entity reference for integration with Backstage catalog. Format: namespace/kind/entity_name.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="External identifier for tracking this service in third-party systems or internal databases.")
    cortex_id: str | None = Field(default=None, validation_alias="cortex_id", serialization_alias="cortex_id", description="Cortex group identifier to associate this service with a Cortex group for metrics and insights.")
    service_now_ci_sys_id: str | None = Field(default=None, validation_alias="service_now_ci_sys_id", serialization_alias="service_now_ci_sys_id", description="ServiceNow Configuration Item system ID for ITSM integration and change tracking.")
    github_repository_name: str | None = Field(default=None, validation_alias="github_repository_name", serialization_alias="github_repository_name", description="GitHub repository identifier for source code integration. Format: owner/repository_name.")
    github_repository_branch: str | None = Field(default=None, validation_alias="github_repository_branch", serialization_alias="github_repository_branch", description="Default branch in the GitHub repository to track for deployments and changes. Example: main or develop.")
    gitlab_repository_name: str | None = Field(default=None, validation_alias="gitlab_repository_name", serialization_alias="gitlab_repository_name", description="GitLab repository identifier for source code integration. Format: group/project_name.")
    gitlab_repository_branch: str | None = Field(default=None, validation_alias="gitlab_repository_branch", serialization_alias="gitlab_repository_branch", description="Default branch in the GitLab repository to track for deployments and changes. Example: main or develop.")
    environment_ids: list[str] | None = Field(default=None, validation_alias="environment_ids", serialization_alias="environment_ids", description="List of environment IDs where this service is deployed or operates.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="List of service IDs that depend on this service, establishing service dependency relationships.")
    owner_group_ids: list[str] | None = Field(default=None, validation_alias="owner_group_ids", serialization_alias="owner_group_ids", description="List of team/group IDs that own and are responsible for this service.")
    owner_user_ids: list[int] | None = Field(default=None, validation_alias="owner_user_ids", serialization_alias="owner_user_ids", description="List of user IDs designated as owners responsible for this service.")
    alerts_email_enabled: bool | None = Field(default=None, validation_alias="alerts_email_enabled", serialization_alias="alerts_email_enabled", description="Enable or disable email notifications for alerts and incidents related to this service.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="Alert urgency level ID that determines the severity classification and routing of alerts for this service.")
    slack_channels: list[UpdateServiceBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="List of Slack channel identifiers to receive notifications and alerts for this service.")
    slack_aliases: list[UpdateServiceBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="List of Slack aliases or handles to mention when sending notifications about this service.")
class UpdateServiceRequestBodyData(StrictModel):
    type_: Literal["services"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'services' for this operation.")
    attributes: UpdateServiceRequestBodyDataAttributes | None = None
class UpdateServiceRequestBody(StrictModel):
    data: UpdateServiceRequestBodyData
class UpdateServiceRequest(StrictModel):
    """Update an existing service with new metadata, integrations, ownership, and notification settings. Modify service details such as description, color, position, external system associations, and linked resources."""
    path: UpdateServiceRequestPath
    body: UpdateServiceRequestBody

# Operation: delete_service
class DeleteServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to delete.")
class DeleteServiceRequest(StrictModel):
    """Permanently delete a service by its unique identifier. This action cannot be undone."""
    path: DeleteServiceRequestPath

# Operation: get_service_incidents_chart
class GetServiceIncidentsChartRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service for which to retrieve incident chart data.")
class GetServiceIncidentsChartRequestQuery(StrictModel):
    period: str = Field(default=..., description="The time period for the incident chart data (e.g., last 7 days, last 30 days, or a specific date range). Specify the period in the format expected by the API.")
class GetServiceIncidentsChartRequest(StrictModel):
    """Retrieve a chart visualization of incidents for a specific service over a defined time period. This helps track incident trends and patterns for the service."""
    path: GetServiceIncidentsChartRequestPath
    query: GetServiceIncidentsChartRequestQuery

# Operation: get_service_uptime_chart
class GetServiceUptimeChartRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service for which to retrieve the uptime chart.")
class GetServiceUptimeChartRequestQuery(StrictModel):
    period: str | None = Field(default=None, description="The time period to display in the chart (e.g., last 7 days, 30 days, or 90 days). If not specified, a default period will be used.")
class GetServiceUptimeChartRequest(StrictModel):
    """Retrieve a visual uptime chart for a specific service, showing availability metrics over a selected time period."""
    path: GetServiceUptimeChartRequestPath
    query: GetServiceUptimeChartRequestQuery | None = None

# Operation: list_severities
class ListSeveritiesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., metadata, counts). Specify which associations should be expanded in the result.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to control result set boundaries.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of results per page. Defines how many severity records are returned in each paginated response.")
    filter_color: str | None = Field(default=None, validation_alias="filter[color]", serialization_alias="filter[color]", description="Filter results by severity color value. Narrows the list to severities matching the specified color.")
    sort: str | None = Field(default=None, description="Comma-separated list of fields to sort by, with optional direction indicators (e.g., 'name,-created_at'). Controls the order of returned results.")
class ListSeveritiesRequest(StrictModel):
    """Retrieve a paginated list of severity levels, with optional filtering by color and custom sorting capabilities."""
    query: ListSeveritiesRequestQuery | None = None

# Operation: create_severity
class CreateSeverityRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for this severity level (e.g., 'Critical', 'High Priority').")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed explanation of when this severity level should be used and its implications.")
    severity: Literal["critical", "high", "medium", "low"] | None = Field(default=None, validation_alias="severity", serialization_alias="severity", description="The severity tier classification. Choose from: critical (highest priority), high, medium, or low (lowest priority).")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hexadecimal color code (e.g., #FF0000) used to visually represent this severity in the UI.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this severity relative to others; lower numbers appear first in lists and hierarchies.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="Email addresses that should receive notifications when incidents of this severity are created or escalated. Provide as an array of valid email addresses.")
    slack_channels: list[CreateSeverityBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="Slack channel identifiers or names to automatically post incident notifications. Provide as an array of channel references.")
    slack_aliases: list[CreateSeverityBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="Slack user aliases or group handles to mention in severity-related notifications. Provide as an array of alias strings.")
class CreateSeverityRequestBodyData(StrictModel):
    type_: Literal["severities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'severities' to indicate this is a severity resource.")
    attributes: CreateSeverityRequestBodyDataAttributes
class CreateSeverityRequestBody(StrictModel):
    data: CreateSeverityRequestBodyData
class CreateSeverityRequest(StrictModel):
    """Creates a new severity level for categorizing and routing incidents. Severities can be configured with notification channels, visual indicators, and organizational metadata."""
    body: CreateSeverityRequestBody

# Operation: get_severity
class GetSeverityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the severity to retrieve.")
class GetSeverityRequest(StrictModel):
    """Retrieves a specific severity record by its unique identifier. Use this to fetch detailed information about a severity level."""
    path: GetSeverityRequestPath

# Operation: update_severity
class UpdateSeverityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the severity to update.")
class UpdateSeverityRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A descriptive label or explanation for this severity level.")
    severity: Literal["critical", "high", "medium", "low"] | None = Field(default=None, validation_alias="severity", serialization_alias="severity", description="The severity level classification; must be one of: critical, high, medium, or low.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hexadecimal color code used to visually represent this severity in the UI.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of this severity relative to others; lower numbers appear first.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="A list of email addresses that should receive notifications when incidents of this severity are triggered.")
    slack_channels: list[UpdateSeverityBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="A list of Slack channel identifiers or names where notifications for this severity should be posted.")
    slack_aliases: list[UpdateSeverityBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="A list of Slack user aliases or group handles that should be notified when incidents of this severity occur.")
class UpdateSeverityRequestBodyData(StrictModel):
    type_: Literal["severities"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'severities' to specify this is a severity resource.")
    attributes: UpdateSeverityRequestBodyDataAttributes | None = None
class UpdateSeverityRequestBody(StrictModel):
    data: UpdateSeverityRequestBodyData
class UpdateSeverityRequest(StrictModel):
    """Update an existing severity configuration by ID, allowing modification of its description, level, visual appearance, notification settings, and associated communication channels."""
    path: UpdateSeverityRequestPath
    body: UpdateSeverityRequestBody

# Operation: delete_severity
class DeleteSeverityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the severity to delete.")
class DeleteSeverityRequest(StrictModel):
    """Permanently delete a severity by its unique identifier. This action cannot be undone."""
    path: DeleteSeverityRequestPath

# Operation: list_shifts
class ListShiftsRequestQuery(StrictModel):
    include: Literal["shift_override", "user"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Valid options are shift_override (to include override details) and user (to include user information).")
    to: str | None = Field(default=None, description="End of the time range for filtering shifts. Use ISO 8601 format for the date/time value.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the time range for filtering shifts. Use ISO 8601 format for the date/time value.")
    user_ids: list[int] | None = Field(default=None, validation_alias="user_ids[]", serialization_alias="user_ids[]", description="Array of user IDs to filter shifts by specific users. Only shifts assigned to these users will be returned.")
    schedule_ids: list[str] | None = Field(default=None, validation_alias="schedule_ids[]", serialization_alias="schedule_ids[]", description="Array of schedule IDs to filter shifts by specific schedules. Only shifts belonging to these schedules will be returned.")
class ListShiftsRequest(StrictModel):
    """Retrieve a list of shifts, optionally filtered by users or schedules and within a specified time range. Supports including related data such as shift overrides and user information."""
    query: ListShiftsRequestQuery | None = None

# Operation: list_status_page_templates
class ListStatusPageTemplatesRequestPath(StrictModel):
    status_page_id: str = Field(default=..., description="The unique identifier of the status page for which to list templates.")
class ListStatusPageTemplatesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., components, incidents). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of templates to return per page. Adjust to balance response size and number of requests needed.")
class ListStatusPageTemplatesRequest(StrictModel):
    """Retrieve a paginated list of templates available for a specific status page. Templates define the layout and structure for status page content."""
    path: ListStatusPageTemplatesRequestPath
    query: ListStatusPageTemplatesRequestQuery | None = None

# Operation: get_status_page_template
class GetStatusPageTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page template to retrieve.")
class GetStatusPageTemplateRequest(StrictModel):
    """Retrieves a specific status page template by its unique identifier. Use this to fetch the full details and configuration of a template for viewing or further operations."""
    path: GetStatusPageTemplateRequestPath

# Operation: delete_status_page_template
class DeleteStatusPageTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page template to delete.")
class DeleteStatusPageTemplateRequest(StrictModel):
    """Delete a specific status page template by its unique identifier. This operation permanently removes the template and cannot be undone."""
    path: DeleteStatusPageTemplateRequestPath

# Operation: list_status_pages
class ListStatusPagesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., components, incidents). Reduces the need for additional API calls.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to navigate through results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of status pages to return per page. Adjust to control result set size for pagination.")
    sort: str | None = Field(default=None, description="Sort the results by a specified field and direction (e.g., name, created_at). Use ascending or descending order to organize the list.")
class ListStatusPagesRequest(StrictModel):
    """Retrieve a paginated list of status pages. Use pagination parameters to control the number of results and navigate through pages."""
    query: ListStatusPagesRequestQuery | None = None

# Operation: create_status_page
class CreateStatusPageRequestBodyDataAttributes(StrictModel):
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="The internal title of the status page used for identification and management.")
    public_title: str | None = Field(default=None, validation_alias="public_title", serialization_alias="public_title", description="The title displayed to public visitors on the status page.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Internal description for reference and documentation purposes.")
    public_description: str | None = Field(default=None, validation_alias="public_description", serialization_alias="public_description", description="Description visible to public visitors on the status page.")
    header_color: str | None = Field(default=None, validation_alias="header_color", serialization_alias="header_color", description="Hex color code for the page header (e.g., '#0061F2').")
    footer_color: str | None = Field(default=None, validation_alias="footer_color", serialization_alias="footer_color", description="Hex color code for the page footer (e.g., '#1F2F41').")
    allow_search_engine_index: bool | None = Field(default=None, validation_alias="allow_search_engine_index", serialization_alias="allow_search_engine_index", description="When enabled, allows search engines to index and include your public status page in search results.")
    show_uptime: bool | None = Field(default=None, validation_alias="show_uptime", serialization_alias="show_uptime", description="When enabled, displays uptime statistics on the status page.")
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(default=None, validation_alias="show_uptime_last_days", serialization_alias="show_uptime_last_days", description="The time period over which uptime is calculated and displayed; choose from 30, 60, or 90 days.")
    success_message: str | None = Field(default=None, validation_alias="success_message", serialization_alias="success_message", description="Custom message displayed when all monitored components are operational.")
    failure_message: str | None = Field(default=None, validation_alias="failure_message", serialization_alias="failure_message", description="Custom message displayed when one or more monitored components are experiencing issues.")
    authentication_enabled: bool | None = Field(default=None, validation_alias="authentication_enabled", serialization_alias="authentication_enabled", description="When enabled, requires a password to access the status page; defaults to disabled.")
    authentication_password: str | None = Field(default=None, validation_alias="authentication_password", serialization_alias="authentication_password", description="Password required for accessing the status page when authentication is enabled.")
    website_url: str | None = Field(default=None, validation_alias="website_url", serialization_alias="website_url", description="URL to your organization's website, displayed as a link on the status page.")
    website_privacy_url: str | None = Field(default=None, validation_alias="website_privacy_url", serialization_alias="website_privacy_url", description="URL to your organization's privacy policy, displayed as a link on the status page.")
    website_support_url: str | None = Field(default=None, validation_alias="website_support_url", serialization_alias="website_support_url", description="URL to your organization's support or help center, displayed as a link on the status page.")
    ga_tracking_id: str | None = Field(default=None, validation_alias="ga_tracking_id", serialization_alias="ga_tracking_id", description="Google Analytics tracking ID for monitoring visitor analytics on the status page.")
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="IANA time zone name for displaying incident times and uptime calculations; defaults to 'Etc/UTC'.")
    public: bool | None = Field(default=None, validation_alias="public", serialization_alias="public", description="When enabled, makes the status page publicly accessible; when disabled, restricts access.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service IDs to attach and monitor on this status page.")
    functionality_ids: list[str] | None = Field(default=None, validation_alias="functionality_ids", serialization_alias="functionality_ids", description="Array of functionality IDs to attach and display on this status page.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="When enabled, the status page is active and operational; when disabled, the page is inactive.")
class CreateStatusPageRequestBodyData(StrictModel):
    type_: Literal["status_pages"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'status_pages'.")
    attributes: CreateStatusPageRequestBodyDataAttributes
class CreateStatusPageRequestBody(StrictModel):
    data: CreateStatusPageRequestBodyData
class CreateStatusPageRequest(StrictModel):
    """Creates a new status page with customizable branding, authentication, and component tracking. Configure visibility settings, messaging, and integrations to monitor service status."""
    body: CreateStatusPageRequestBody

# Operation: get_status_page
class GetStatusPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page to retrieve.")
class GetStatusPageRequest(StrictModel):
    """Retrieves a specific status page by its unique identifier. Use this to fetch detailed information about a status page including its current state and configuration."""
    path: GetStatusPageRequestPath

# Operation: update_status_page
class UpdateStatusPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page to update.")
class UpdateStatusPageRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The internal title of the status page used for administrative purposes.")
    public_title: str | None = Field(default=None, validation_alias="public_title", serialization_alias="public_title", description="The title displayed to the public on the status page.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Internal description of the status page for administrative reference.")
    public_description: str | None = Field(default=None, validation_alias="public_description", serialization_alias="public_description", description="Public-facing description displayed on the status page.")
    header_color: str | None = Field(default=None, validation_alias="header_color", serialization_alias="header_color", description="Hex color code for the page header (e.g., '#0061F2').")
    footer_color: str | None = Field(default=None, validation_alias="footer_color", serialization_alias="footer_color", description="Hex color code for the page footer (e.g., '#1F2F41').")
    allow_search_engine_index: bool | None = Field(default=None, validation_alias="allow_search_engine_index", serialization_alias="allow_search_engine_index", description="Whether to allow search engines to index and include this status page in search results.")
    show_uptime: bool | None = Field(default=None, validation_alias="show_uptime", serialization_alias="show_uptime", description="Whether to display uptime statistics on the status page.")
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(default=None, validation_alias="show_uptime_last_days", serialization_alias="show_uptime_last_days", description="The time period in days for uptime calculation; choose from 30, 60, or 90 days.")
    success_message: str | None = Field(default=None, validation_alias="success_message", serialization_alias="success_message", description="Custom message displayed when all monitored components are operational.")
    failure_message: str | None = Field(default=None, validation_alias="failure_message", serialization_alias="failure_message", description="Custom message displayed when one or more monitored components are experiencing issues.")
    authentication_enabled: bool | None = Field(default=None, validation_alias="authentication_enabled", serialization_alias="authentication_enabled", description="Enable password protection for accessing the status page; defaults to disabled.")
    authentication_password: str | None = Field(default=None, validation_alias="authentication_password", serialization_alias="authentication_password", description="Password required to access the status page when authentication is enabled.")
    website_url: str | None = Field(default=None, validation_alias="website_url", serialization_alias="website_url", description="URL to your organization's main website.")
    website_privacy_url: str | None = Field(default=None, validation_alias="website_privacy_url", serialization_alias="website_privacy_url", description="URL to your organization's privacy policy.")
    website_support_url: str | None = Field(default=None, validation_alias="website_support_url", serialization_alias="website_support_url", description="URL to your organization's support or help center.")
    ga_tracking_id: str | None = Field(default=None, validation_alias="ga_tracking_id", serialization_alias="ga_tracking_id", description="Google Analytics tracking ID for monitoring status page traffic and user behavior.")
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="IANA time zone name for displaying timestamps on the status page; defaults to 'Etc/UTC'.")
    public: bool | None = Field(default=None, validation_alias="public", serialization_alias="public", description="Make the status page publicly accessible without authentication.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service IDs to attach and display on the status page.")
    functionality_ids: list[str] | None = Field(default=None, validation_alias="functionality_ids", serialization_alias="functionality_ids", description="Array of functionality IDs to attach and display on the status page.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Enable or disable the status page; disabled pages are not accessible.")
class UpdateStatusPageRequestBodyData(StrictModel):
    type_: Literal["status_pages"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'status_pages'.")
    attributes: UpdateStatusPageRequestBodyDataAttributes | None = None
class UpdateStatusPageRequestBody(StrictModel):
    data: UpdateStatusPageRequestBodyData
class UpdateStatusPageRequest(StrictModel):
    """Update an existing status page configuration, including branding, visibility settings, authentication, and attached services or functionalities."""
    path: UpdateStatusPageRequestPath
    body: UpdateStatusPageRequestBody

# Operation: delete_status_page
class DeleteStatusPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page to delete.")
class DeleteStatusPageRequest(StrictModel):
    """Permanently delete a status page by its unique identifier. This action cannot be undone and will remove the status page and all associated data."""
    path: DeleteStatusPageRequestPath

# Operation: list_teams
class ListTeamsRequestQuery(StrictModel):
    include: Literal["users"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Use 'users' to include team member information.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="Page number for pagination (1-indexed). Use with page[size] to retrieve specific result sets.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of teams to return per page. Use with page[number] to control pagination.")
    filter_backstage_id: str | None = Field(default=None, validation_alias="filter[backstage_id]", serialization_alias="filter[backstage_id]", description="Filter teams by their Backstage identifier.")
    filter_cortex_id: str | None = Field(default=None, validation_alias="filter[cortex_id]", serialization_alias="filter[cortex_id]", description="Filter teams by their Cortex identifier.")
    filter_opslevel_id: str | None = Field(default=None, validation_alias="filter[opslevel_id]", serialization_alias="filter[opslevel_id]", description="Filter teams by their OpsLevel identifier.")
    filter_external_id: str | None = Field(default=None, validation_alias="filter[external_id]", serialization_alias="filter[external_id]", description="Filter teams by their external identifier (used for cross-system references).")
    filter_color: str | None = Field(default=None, validation_alias="filter[color]", serialization_alias="filter[color]", description="Filter teams by their display color.")
    sort: str | None = Field(default=None, description="Sort results by a specified field. Consult API documentation for available sort fields and order direction syntax.")
class ListTeamsRequest(StrictModel):
    """Retrieve a paginated list of teams with optional filtering by external identifiers and sorting. Optionally include related user data for each team."""
    query: ListTeamsRequestQuery | None = None

# Operation: create_team
class CreateTeamRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the team; used as the primary identifier in the UI.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the team's purpose, scope, or other relevant information.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="Email addresses to associate with the team for notifications and communications; provided as an array of email strings.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="A hexadecimal color code (e.g., #FF5733) used to visually represent the team in the UI.")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The display order of the team in lists and navigation; lower numbers appear first.")
    backstage_id: str | None = Field(default=None, validation_alias="backstage_id", serialization_alias="backstage_id", description="The Backstage entity reference for this team, formatted as namespace/kind/entity_name to enable integration with Backstage catalogs.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="An external identifier from your organization's system to link this team with external records or systems.")
    pagerduty_service_id: str | None = Field(default=None, validation_alias="pagerduty_service_id", serialization_alias="pagerduty_service_id", description="The PagerDuty service ID to associate with this team for incident management and on-call scheduling.")
    opsgenie_team_id: str | None = Field(default=None, validation_alias="opsgenie_team_id", serialization_alias="opsgenie_team_id", description="The Opsgenie team ID to associate with this team for alert routing and escalation policies.")
    victor_ops_id: str | None = Field(default=None, validation_alias="victor_ops_id", serialization_alias="victor_ops_id", description="The VictorOps group ID to associate with this team for incident response and alerting.")
    pagertree_id: str | None = Field(default=None, validation_alias="pagertree_id", serialization_alias="pagertree_id", description="The PagerTree group ID to associate with this team for incident management and team coordination.")
    cortex_id: str | None = Field(default=None, validation_alias="cortex_id", serialization_alias="cortex_id", description="The Cortex group ID to associate with this team for engineering metrics and insights.")
    service_now_ci_sys_id: str | None = Field(default=None, validation_alias="service_now_ci_sys_id", serialization_alias="service_now_ci_sys_id", description="The ServiceNow Configuration Item (CI) system ID to link this team with IT asset management records.")
    user_ids: list[int] | None = Field(default=None, validation_alias="user_ids", serialization_alias="user_ids", description="User IDs of team members to add to this team; provided as an array of user identifiers.")
    admin_ids: list[int] | None = Field(default=None, validation_alias="admin_ids", serialization_alias="admin_ids", description="User IDs of team administrators; these users must also be included in the user_ids array and will have elevated permissions for team management.")
    alerts_email_enabled: bool | None = Field(default=None, validation_alias="alerts_email_enabled", serialization_alias="alerts_email_enabled", description="Enable or disable email notifications for alerts sent to this team.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The alert urgency level ID for this team, determining how alerts are prioritized and routed.")
    slack_channels: list[CreateTeamBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="Slack channel names or IDs to associate with this team for notifications and integrations; provided as an array.")
    slack_aliases: list[CreateTeamBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="Slack aliases or handles to associate with this team for mentions and direct messaging; provided as an array.")
class CreateTeamRequestBodyData(StrictModel):
    type_: Literal["groups"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of entity being created; must be 'groups' to indicate this is a team/group resource.")
    attributes: CreateTeamRequestBodyDataAttributes
class CreateTeamRequestBody(StrictModel):
    data: CreateTeamRequestBodyData
class CreateTeamRequest(StrictModel):
    """Creates a new team with the specified configuration, including optional integrations with external services like PagerDuty, Opsgenie, Slack, and Backstage. The team can include members and admins, and supports email-based alerts."""
    body: CreateTeamRequestBody

# Operation: get_team
class GetTeamRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to retrieve.")
class GetTeamRequestQuery(StrictModel):
    include: Literal["users"] | None = Field(default=None, description="Comma-separated list of related resources to include in the response. Supported values: users (to include team members).")
class GetTeamRequest(StrictModel):
    """Retrieves a specific team by its unique identifier. Optionally include related resources such as team members in the response."""
    path: GetTeamRequestPath
    query: GetTeamRequestQuery | None = None

# Operation: update_team
class UpdateTeamRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to update.")
class UpdateTeamRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the team's purpose or scope.")
    notify_emails: list[str] | None = Field(default=None, validation_alias="notify_emails", serialization_alias="notify_emails", description="Email addresses to receive team notifications. Provide as an array of valid email addresses.")
    color: str | None = Field(default=None, validation_alias="color", serialization_alias="color", description="The team's display color as a hexadecimal color code (e.g., #FF5733).")
    position: int | None = Field(default=None, validation_alias="position", serialization_alias="position", description="The team's display order in lists and hierarchies. Lower numbers appear first.")
    backstage_id: str | None = Field(default=None, validation_alias="backstage_id", serialization_alias="backstage_id", description="The Backstage catalog entity reference for this team, formatted as namespace/kind/entity_name.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="An external identifier for this team in third-party systems.")
    pagerduty_service_id: str | None = Field(default=None, validation_alias="pagerduty_service_id", serialization_alias="pagerduty_service_id", description="The PagerDuty service ID linked to this team for incident management.")
    victor_ops_id: str | None = Field(default=None, validation_alias="victor_ops_id", serialization_alias="victor_ops_id", description="The VictorOps group ID linked to this team for on-call management.")
    pagertree_id: str | None = Field(default=None, validation_alias="pagertree_id", serialization_alias="pagertree_id", description="The PagerTree group ID linked to this team for incident tracking.")
    cortex_id: str | None = Field(default=None, validation_alias="cortex_id", serialization_alias="cortex_id", description="The Cortex group ID linked to this team for engineering metrics.")
    service_now_ci_sys_id: str | None = Field(default=None, validation_alias="service_now_ci_sys_id", serialization_alias="service_now_ci_sys_id", description="The ServiceNow configuration item system ID linked to this team.")
    user_ids: list[int] | None = Field(default=None, validation_alias="user_ids", serialization_alias="user_ids", description="Array of user IDs who are members of this team. Order is not significant.")
    admin_ids: list[int] | None = Field(default=None, validation_alias="admin_ids", serialization_alias="admin_ids", description="Array of user IDs with admin privileges for this team. All admin IDs must also be included in the user_ids array.")
    alerts_email_enabled: bool | None = Field(default=None, validation_alias="alerts_email_enabled", serialization_alias="alerts_email_enabled", description="Enable or disable email notifications for team alerts.")
    alert_urgency_id: str | None = Field(default=None, validation_alias="alert_urgency_id", serialization_alias="alert_urgency_id", description="The alert urgency level ID that determines notification priority for this team.")
    slack_channels: list[UpdateTeamBodyDataAttributesSlackChannelsItem] | None = Field(default=None, validation_alias="slack_channels", serialization_alias="slack_channels", description="Slack channels to associate with this team for notifications and updates. Provide as an array of channel identifiers or names.")
    slack_aliases: list[UpdateTeamBodyDataAttributesSlackAliasesItem] | None = Field(default=None, validation_alias="slack_aliases", serialization_alias="slack_aliases", description="Slack aliases or mentions associated with this team for easy reference. Provide as an array of alias strings.")
class UpdateTeamRequestBodyData(StrictModel):
    type_: Literal["groups"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'groups' for team operations.")
    attributes: UpdateTeamRequestBodyDataAttributes | None = None
class UpdateTeamRequestBody(StrictModel):
    data: UpdateTeamRequestBodyData
class UpdateTeamRequest(StrictModel):
    """Update team configuration including metadata, integrations, members, and notification settings. Requires team ID and type specification."""
    path: UpdateTeamRequestPath
    body: UpdateTeamRequestBody

# Operation: delete_team
class DeleteTeamRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to delete.")
class DeleteTeamRequest(StrictModel):
    """Permanently delete a team by its unique identifier. This action cannot be undone and will remove the team and all associated data."""
    path: DeleteTeamRequestPath

# Operation: get_team_incidents_chart
class GetTeamIncidentsChartRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team for which to retrieve incident chart data.")
class GetTeamIncidentsChartRequestQuery(StrictModel):
    period: str = Field(default=..., description="The time period for which to retrieve incident data. Specify the desired reporting window (e.g., daily, weekly, monthly, or a specific date range).")
class GetTeamIncidentsChartRequest(StrictModel):
    """Retrieve a chart visualization of incidents for a specific team over a defined time period. This provides aggregated incident data suitable for dashboard and reporting purposes."""
    path: GetTeamIncidentsChartRequestPath
    query: GetTeamIncidentsChartRequestQuery

# Operation: list_user_email_addresses
class GetUserEmailAddressesRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose email addresses should be retrieved.")
class GetUserEmailAddressesRequest(StrictModel):
    """Retrieves all email addresses associated with a specific user account. Returns a collection of email addresses linked to the user's profile."""
    path: GetUserEmailAddressesRequestPath

# Operation: add_email_address_to_user
class CreateUserEmailAddressRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to whom the email address will be added.")
class CreateUserEmailAddressRequestBodyDataAttributes(StrictModel):
    email: str = Field(default=..., validation_alias="email", serialization_alias="email", description="The email address to add to the user account. Must be a valid email format.")
class CreateUserEmailAddressRequestBodyData(StrictModel):
    type_: Literal["user_email_addresses"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of email address being created. Must be set to 'user_email_addresses' to indicate this is a standard user email address.")
    attributes: CreateUserEmailAddressRequestBodyDataAttributes
class CreateUserEmailAddressRequestBody(StrictModel):
    data: CreateUserEmailAddressRequestBodyData
class CreateUserEmailAddressRequest(StrictModel):
    """Adds a new email address to a user account. The email address is created as a user email address type and becomes associated with the specified user."""
    path: CreateUserEmailAddressRequestPath
    body: CreateUserEmailAddressRequestBody

# Operation: get_email_address
class ShowUserEmailAddressRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email address to retrieve.")
class ShowUserEmailAddressRequest(StrictModel):
    """Retrieves a specific user email address by its unique identifier."""
    path: ShowUserEmailAddressRequestPath

# Operation: update_user_email_address
class UpdateUserEmailAddressRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user email address record to update.")
class UpdateUserEmailAddressRequestBodyDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The new email address value to assign to this record.")
class UpdateUserEmailAddressRequestBodyData(StrictModel):
    type_: Literal["user_email_addresses"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'user_email_addresses' to specify this is a user email address resource.")
    attributes: UpdateUserEmailAddressRequestBodyDataAttributes | None = None
class UpdateUserEmailAddressRequestBody(StrictModel):
    data: UpdateUserEmailAddressRequestBodyData
class UpdateUserEmailAddressRequest(StrictModel):
    """Updates an existing user email address record. Specify the email address ID and provide the new email value to modify."""
    path: UpdateUserEmailAddressRequestPath
    body: UpdateUserEmailAddressRequestBody

# Operation: delete_email_address
class DeleteUserEmailAddressRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email address to delete.")
class DeleteUserEmailAddressRequest(StrictModel):
    """Permanently deletes a user's email address by its unique identifier. This action cannot be undone."""
    path: DeleteUserEmailAddressRequestPath

# Operation: get_notification_rule
class GetUserNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification rule to retrieve.")
class GetUserNotificationRuleRequest(StrictModel):
    """Retrieves a specific notification rule by its unique identifier. Use this to fetch the configuration and settings for a particular user notification rule."""
    path: GetUserNotificationRuleRequestPath

# Operation: delete_notification_rule
class DeleteUserNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification rule to delete.")
class DeleteUserNotificationRuleRequest(StrictModel):
    """Delete a specific notification rule by its unique identifier. This operation permanently removes the rule and stops any notifications governed by it."""
    path: DeleteUserNotificationRuleRequestPath

# Operation: list_user_phone_numbers
class GetUserPhoneNumbersRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose phone numbers should be retrieved.")
class GetUserPhoneNumbersRequest(StrictModel):
    """Retrieves all phone numbers associated with a specific user account. Returns a collection of phone number records for the given user."""
    path: GetUserPhoneNumbersRequestPath

# Operation: add_phone_number_to_user
class CreateUserPhoneNumberRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to whom the phone number will be added.")
class CreateUserPhoneNumberRequestBodyDataAttributes(StrictModel):
    phone: str = Field(default=..., validation_alias="phone", serialization_alias="phone", description="The phone number in international format (e.g., +1 country code followed by the number).")
class CreateUserPhoneNumberRequestBodyData(StrictModel):
    type_: Literal["user_phone_numbers"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of phone number resource being created. Must be set to 'user_phone_numbers'.")
    attributes: CreateUserPhoneNumberRequestBodyDataAttributes
class CreateUserPhoneNumberRequestBody(StrictModel):
    data: CreateUserPhoneNumberRequestBodyData
class CreateUserPhoneNumberRequest(StrictModel):
    """Adds a new phone number to a user's account. The phone number must be provided in international format."""
    path: CreateUserPhoneNumberRequestPath
    body: CreateUserPhoneNumberRequestBody

# Operation: get_phone_number
class ShowUserPhoneNumberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number record to retrieve.")
class ShowUserPhoneNumberRequest(StrictModel):
    """Retrieves the details of a specific user phone number by its unique identifier."""
    path: ShowUserPhoneNumberRequestPath

# Operation: update_user_phone_number
class UpdateUserPhoneNumberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user phone number record to update.")
class UpdateUserPhoneNumberRequestBodyDataAttributes(StrictModel):
    phone: str | None = Field(default=None, validation_alias="phone", serialization_alias="phone", description="The new phone number in international format (e.g., +1 country code followed by the number).")
class UpdateUserPhoneNumberRequestBodyData(StrictModel):
    type_: Literal["user_phone_numbers"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'user_phone_numbers' to specify this is a user phone number resource.")
    attributes: UpdateUserPhoneNumberRequestBodyDataAttributes | None = None
class UpdateUserPhoneNumberRequestBody(StrictModel):
    data: UpdateUserPhoneNumberRequestBodyData
class UpdateUserPhoneNumberRequest(StrictModel):
    """Updates a user's phone number by ID. The phone number must be provided in international format."""
    path: UpdateUserPhoneNumberRequestPath
    body: UpdateUserPhoneNumberRequestBody

# Operation: delete_user_phone_number
class DeleteUserPhoneNumberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to delete.")
class DeleteUserPhoneNumberRequest(StrictModel):
    """Permanently deletes a specific user phone number by its unique identifier. This action cannot be undone."""
    path: DeleteUserPhoneNumberRequestPath

# Operation: list_users
class ListUsersRequestQuery(StrictModel):
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination (1-indexed). Use with page[size] to control result offset.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of users to return per page. Use with page[number] to paginate through results.")
    filter_email: str | None = Field(default=None, validation_alias="filter[email]", serialization_alias="filter[email]", description="Filter results by user email address. Matches against the email field.")
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Field(default=None, description="Sort results by one or more fields in comma-separated format. Prefix field name with hyphen (-) for descending order. Valid fields are created_at and updated_at.")
    include: Literal["email_addresses", "phone_numbers", "devices", "role", "on_call_role"] | None = Field(default=None, description="Include related resources in the response as comma-separated values. Available relationships are email_addresses, phone_numbers, devices, role, and on_call_role.")
class ListUsersRequest(StrictModel):
    """Retrieve a paginated list of users with optional filtering, sorting, and relationship inclusion. Supports email-based filtering and customizable result ordering."""
    query: ListUsersRequestQuery | None = None

# Operation: get_user
class GetUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to retrieve.")
class GetUserRequestQuery(StrictModel):
    include: Literal["email_addresses", "phone_numbers", "devices", "role", "on_call_role"] | None = Field(default=None, description="Comma-separated list of related data to include in the response. Valid options are: email_addresses, phone_numbers, devices, role, and on_call_role.")
class GetUserRequest(StrictModel):
    """Retrieves a specific user by their unique identifier. Optionally include related data such as contact information, devices, and role assignments."""
    path: GetUserRequestPath
    query: GetUserRequestQuery | None = None

# Operation: update_user
class UpdateUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to update.")
class UpdateUserRequestBodyDataAttributes(StrictModel):
    first_name: str | None = Field(default=None, validation_alias="first_name", serialization_alias="first_name", description="The user's first name.")
    last_name: str | None = Field(default=None, validation_alias="last_name", serialization_alias="last_name", description="The user's last name.")
    role_id: str | None = Field(default=None, validation_alias="role_id", serialization_alias="role_id", description="The ID of the role to assign to this user, determining their primary permissions and access level.")
    on_call_role_id: str | None = Field(default=None, validation_alias="on_call_role_id", serialization_alias="on_call_role_id", description="The ID of the on-call role to assign to this user, defining their on-call responsibilities and escalation policies.")
class UpdateUserRequestBodyData(StrictModel):
    type_: Literal["users"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'users' to specify this operation targets user resources.")
    attributes: UpdateUserRequestBodyDataAttributes | None = None
class UpdateUserRequestBody(StrictModel):
    data: UpdateUserRequestBodyData
class UpdateUserRequest(StrictModel):
    """Update user details including name and role assignments for a specific user by their ID."""
    path: UpdateUserRequestPath
    body: UpdateUserRequestBody

# Operation: delete_user
class DeleteUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to delete.")
class DeleteUserRequest(StrictModel):
    """Permanently delete a user account by its unique identifier. This action cannot be undone."""
    path: DeleteUserRequestPath

# Operation: list_webhook_deliveries
class ListWebhooksDeliveriesRequestPath(StrictModel):
    endpoint_id: str = Field(default=..., description="The unique identifier of the webhook endpoint for which to retrieve deliveries.")
class ListWebhooksDeliveriesRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related resources to include in the response (e.g., request details, response data). Specify which additional fields should be populated in the delivery records.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The number of delivery records to return per page. Controls the size of each paginated result set.")
class ListWebhooksDeliveriesRequest(StrictModel):
    """Retrieve a paginated list of webhook delivery attempts for a specific webhook endpoint, including details about each delivery's status and outcome."""
    path: ListWebhooksDeliveriesRequestPath
    query: ListWebhooksDeliveriesRequestQuery | None = None

# Operation: retry_webhook_delivery
class DeliverWebhooksDeliveryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook delivery to retry.")
class DeliverWebhooksDeliveryRequest(StrictModel):
    """Retries the delivery of a previously failed webhook event. Use this operation to manually re-attempt sending a webhook that did not reach its destination."""
    path: DeliverWebhooksDeliveryRequestPath

# Operation: get_webhook_delivery
class GetWebhooksDeliveryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook delivery to retrieve.")
class GetWebhooksDeliveryRequest(StrictModel):
    """Retrieves detailed information about a specific webhook delivery event, including its status, payload, and response data."""
    path: GetWebhooksDeliveryRequestPath

# Operation: list_webhook_endpoints
class ListWebhooksEndpointsRequestQuery(StrictModel):
    include: str | None = Field(default=None, description="Comma-separated list of related fields to include in the response for each webhook endpoint, such as event types or configuration details.")
    page_number: int | None = Field(default=None, validation_alias="page[number]", serialization_alias="page[number]", description="The page number to retrieve when paginating through results, starting from page 1.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="The maximum number of webhook endpoints to return per page.")
class ListWebhooksEndpointsRequest(StrictModel):
    """Retrieve a paginated list of all configured webhook endpoints. Use pagination parameters to control the number of results and navigate through pages."""
    query: ListWebhooksEndpointsRequestQuery | None = None

# Operation: get_webhook_endpoint
class GetWebhooksEndpointRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook endpoint to retrieve.")
class GetWebhooksEndpointRequest(StrictModel):
    """Retrieves the configuration and details of a specific webhook endpoint by its unique identifier."""
    path: GetWebhooksEndpointRequestPath

# Operation: update_webhooks_endpoint
class UpdateWebhooksEndpointRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook endpoint to update.")
class UpdateWebhooksEndpointRequestBodyDataAttributes(StrictModel):
    event_types: list[Literal["incident.created", "incident.updated", "incident.in_triage", "incident.mitigated", "incident.resolved", "incident.cancelled", "incident.deleted", "incident.scheduled.created", "incident.scheduled.updated", "incident.scheduled.in_progress", "incident.scheduled.completed", "incident.scheduled.deleted", "incident_post_mortem.created", "incident_post_mortem.updated", "incident_post_mortem.published", "incident_post_mortem.deleted", "incident_status_page_event.created", "incident_status_page_event.updated", "incident_status_page_event.deleted", "incident_event.created", "incident_event.updated", "incident_event.deleted", "alert.created", "pulse.created", "genius_workflow_run.queued", "genius_workflow_run.started", "genius_workflow_run.completed", "genius_workflow_run.failed", "genius_workflow_run.canceled"]] | None = Field(default=None, validation_alias="event_types", serialization_alias="event_types", description="An array of event type strings that this webhook endpoint should subscribe to. Events not included in this list will not trigger the webhook.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="A boolean flag indicating whether this webhook endpoint is active and should receive events. Set to true to enable or false to disable.")
class UpdateWebhooksEndpointRequestBodyData(StrictModel):
    type_: Literal["webhooks_endpoints"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be set to 'webhooks_endpoints' to specify this is a webhook endpoint resource.")
    attributes: UpdateWebhooksEndpointRequestBodyDataAttributes | None = None
class UpdateWebhooksEndpointRequestBody(StrictModel):
    data: UpdateWebhooksEndpointRequestBodyData
class UpdateWebhooksEndpointRequest(StrictModel):
    """Update the configuration of a specific webhook endpoint, including its event subscriptions and enabled status."""
    path: UpdateWebhooksEndpointRequestPath
    body: UpdateWebhooksEndpointRequestBody

# Operation: delete_webhook_endpoint
class DeleteWebhooksEndpointRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook endpoint to delete.")
class DeleteWebhooksEndpointRequest(StrictModel):
    """Permanently delete a webhook endpoint by its unique identifier. This action cannot be undone and will stop all webhook deliveries to this endpoint."""
    path: DeleteWebhooksEndpointRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AddActionItemTaskParamsAssignedToUser(PermissiveModel):
    """ The user this action item is assigned to"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddActionItemTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddActionItemTaskParams(PermissiveModel):
    task_type: Literal["add_action_item"] | None = None
    attribute_to_query_by: Literal["jira_issue_id"] | None = Field(None, description="Attribute of the Incident to match against")
    query_value: str | None = Field(None, description="Value that attribute_to_query_by to uses to match against")
    incident_role_id: str | None = Field(None, description="The role id this action item is associated with")
    assigned_to_user_id: str | None = Field(None, description="[DEPRECATED] Use assigned_to_user attribute instead. The user id this action item is assigned to")
    assigned_to_user: AddActionItemTaskParamsAssignedToUser | None = Field(None, description=" The user this action item is assigned to")
    priority: Literal["high", "medium", "low"] = Field(..., description="The action item priority")
    kind: str | None = Field(None, description="The action item kind")
    summary: str = Field(..., description="The action item summary")
    description: str | None = Field(None, description="The action item description")
    status: Literal["open", "in_progress", "cancelled", "done"] = Field(..., description="The action item status")
    post_to_incident_timeline: bool | None = None
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    post_to_slack_channels: list[AddActionItemTaskParamsPostToSlackChannelsItem] | None = None

class AddMicrosoftTeamsTabTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddMicrosoftTeamsTabTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddMicrosoftTeamsTabTaskParams(PermissiveModel):
    task_type: Literal["add_microsoft_teams_tab"] | None = None
    playbook_id: str | None = Field(None, description="The playbook id if tab is of an incident playbook")
    team: AddMicrosoftTeamsTabTaskParamsTeam
    channel: AddMicrosoftTeamsTabTaskParamsChannel
    title: str | None = Field(None, description="The tab title. Required if not a playbook tab")
    link: str | None = Field(None, description="The tab link. Required if not a playbook tab")

class AddRoleTaskParamsAssignedToUser(PermissiveModel):
    """ The user this role is assigned to"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddRoleTaskParams(PermissiveModel):
    task_type: Literal["add_role"] | None = None
    incident_role_id: str = Field(..., description="The role id to add to the incident")
    assigned_to_user_id: str | None = Field(None, description="[DEPRECATED] Use assigned_to_user attribute instead. The user id this role is assigned to")
    assigned_to_user: AddRoleTaskParamsAssignedToUser | None = Field(None, description=" The user this role is assigned to")

class AddSlackBookmarkTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddSlackBookmarkTaskParams(PermissiveModel):
    task_type: Literal["add_slack_bookmark"] | None = None
    playbook_id: str | None = Field(None, description="The playbook id if bookmark is of an incident playbook")
    channel: AddSlackBookmarkTaskParamsChannel
    title: str | None = Field(None, description="The bookmark title. Required if not a playbook bookmark")
    link: str | None = Field(None, description="The bookmark link. Required if not a playbook bookmark")
    emoji: str | None = Field(None, description="The bookmark emoji")

class AddTeamTaskParams(PermissiveModel):
    task_type: Literal["add_team"] | None = None
    group_id: str = Field(..., description="The team id")

class AddToTimelineTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AddToTimelineTaskParams(PermissiveModel):
    task_type: Literal["add_to_timeline"] | None = None
    event: str = Field(..., description="The timeline event description")
    url: str | None = Field(None, description="A URL for the timeline event")
    post_to_slack_channels: list[AddToTimelineTaskParamsPostToSlackChannelsItem] | None = None

class AlertField(PermissiveModel):
    slug: str = Field(..., description="The slug of the alert field")
    name: str = Field(..., description="The name of the alert field")
    kind: str = Field(..., description="The kind of alert field")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class AlertLabelsItem(PermissiveModel):
    key: str = Field(..., description="Key of the tag")
    value: str = Field(..., description="Value of the tag")

class ArchiveMicrosoftTeamsChannelsTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class ArchiveMicrosoftTeamsChannelsTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class ArchiveMicrosoftTeamsChannelsTaskParams(PermissiveModel):
    task_type: Literal["archive_microsoft_teams_channels"] | None = None
    team: ArchiveMicrosoftTeamsChannelsTaskParamsTeam
    channels: list[ArchiveMicrosoftTeamsChannelsTaskParamsChannelsItem]

class ArchiveSlackChannelsTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class ArchiveSlackChannelsTaskParams(PermissiveModel):
    task_type: Literal["archive_slack_channels"] | None = None
    channels: list[ArchiveSlackChannelsTaskParamsChannelsItem]

class AttachDatadogDashboardsTaskParamsDashboardsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AttachDatadogDashboardsTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AttachDatadogDashboardsTaskParams(PermissiveModel):
    task_type: Literal["attach_datadog_dashboards"] | None = None
    dashboards: list[AttachDatadogDashboardsTaskParamsDashboardsItem]
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[AttachDatadogDashboardsTaskParamsPostToSlackChannelsItem] | None = None

class AutoAssignRoleOpsgenieTaskParamsSchedule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleOpsgenieTaskParams(PermissiveModel):
    task_type: Literal["auto_assign_role_opsgenie"] | None = None
    incident_role_id: str = Field(..., description="The role id")
    schedule: AutoAssignRoleOpsgenieTaskParamsSchedule

class AutoAssignRolePagerdutyTaskParamsEscalationPolicy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRolePagerdutyTaskParamsSchedule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRolePagerdutyTaskParamsService(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRolePagerdutyTaskParams(PermissiveModel):
    task_type: Literal["auto_assign_role_pagerduty"] | None = None
    incident_role_id: str = Field(..., description="The role id")
    service: AutoAssignRolePagerdutyTaskParamsService | None = None
    schedule: AutoAssignRolePagerdutyTaskParamsSchedule | None = None
    escalation_policy: AutoAssignRolePagerdutyTaskParamsEscalationPolicy | None = None

class AutoAssignRoleRootlyTaskParamsEscalationPolicyTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleRootlyTaskParamsGroupTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleRootlyTaskParamsScheduleTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleRootlyTaskParamsServiceTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleRootlyTaskParamsUserTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleRootlyTaskParams(PermissiveModel):
    task_type: Literal["auto_assign_role_rootly"] | None = None
    incident_role_id: str = Field(..., description="The role id")
    escalation_policy_target: AutoAssignRoleRootlyTaskParamsEscalationPolicyTarget | None = None
    service_target: AutoAssignRoleRootlyTaskParamsServiceTarget | None = None
    user_target: AutoAssignRoleRootlyTaskParamsUserTarget | None = None
    group_target: AutoAssignRoleRootlyTaskParamsGroupTarget | None = None
    schedule_target: AutoAssignRoleRootlyTaskParamsScheduleTarget | None = None

class AutoAssignRoleVictorOpsTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class AutoAssignRoleVictorOpsTaskParams(PermissiveModel):
    task_type: Literal["auto_assign_role_victor_ops"] | None = None
    incident_role_id: str = Field(..., description="The role id")
    team: AutoAssignRoleVictorOpsTaskParamsTeam

class CallPeopleTaskParams(PermissiveModel):
    task_type: Literal["call_people"] | None = None
    phone_numbers: list[str]
    name: str = Field(..., description="The name")
    content: str = Field(..., description="The message to be read by text-to-voice")

class Catalog(PermissiveModel):
    name: str
    description: str | None = None
    icon: Literal["globe-alt", "server-stack", "users", "user-group", "chart-bar", "shapes", "light-bulb", "cursor-arrow-ripple"]
    position: int | None = Field(..., description="Default position of the catalog when displayed in a list.")
    created_at: str
    updated_at: str

class ChangeSlackChannelPrivacyTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class ChangeSlackChannelPrivacyTaskParams(PermissiveModel):
    task_type: Literal["rename_slack_channel"] | None = None
    channel: ChangeSlackChannelPrivacyTaskParamsChannel | None = None
    privacy: Literal["private", "public"]

class CreateAirtableTableRecordTaskParamsBase(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateAirtableTableRecordTaskParamsTable(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateAirtableTableRecordTaskParams(PermissiveModel):
    task_type: Literal["create_airtable_table_record"] | None = None
    base: CreateAirtableTableRecordTaskParamsBase
    table: CreateAirtableTableRecordTaskParamsTable
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")

class CreateAlertGroupBodyDataAttributesConditionsItem(PermissiveModel):
    property_field_type: Literal["attribute", "payload", "alert_field"] = Field(..., description="The type of the property field")
    property_field_name: str | None = Field(None, description="The name of the property field. If the property field type is selected as 'attribute', then the allowed property field names are 'summary' (for Title), 'description', 'alert_urgency' and 'external_url' (for Alert Source URL). If the property field type is selected as 'payload', then the property field name should be supplied in JSON Path syntax.")
    property_field_condition_type: Literal["is_one_of", "is_not_one_of", "contains", "does_not_contain", "starts_with", "ends_with", "matches_regex", "is_empty", "matches_existing_alert"] = Field(..., description="The condition type of the property field")
    property_field_value: str | None = Field(None, description="The value of the property field. Can be null if the property field condition type is 'is_one_of' or 'is_not_one_of'")
    property_field_values: list[str] | None = Field(None, description="The values of the property field. Need to be passed if the property field condition type is 'is_one_of' or 'is_not_one_of' except for when property field name is 'alert_urgency'")
    alert_urgency_ids: list[str] | None = Field(None, description="The Alert Urgency ID's to check in the condition. Only need to be set when the property field type is 'attribute', the property field name is 'alert_urgency' and the property field condition type is 'is_one_of' or 'is_not_one_of'")
    conditionable_type: Literal["AlertField"] | None = Field(None, description="The type of the conditionable")
    conditionable_id: str | None = Field(None, description="The ID of the conditionable. If conditionable_type is AlertField, this is the ID of the alert field.")

class CreateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem(PermissiveModel):
    alert_field_id: str | None = Field(None, description="The ID of the alert field")
    template_body: str | None = Field(None, description="Liquid expression to extract a specific value from the alert's payload for evaluation")

class CreateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem(PermissiveModel):
    json_path: str | None = Field(None, description="JSON path expression to extract a specific value from the alert's payload for evaluation")
    operator: Literal["is", "is_not", "contains", "does_not_contain"] | None = Field(None, description="Comparison operator used to evaluate the extracted value against the specified condition")
    value: str | None = Field(None, description="Value that the extracted payload data is compared to using the specified operator to determine a match")
    conditionable_type: Literal["AlertField"] | None = Field(None, description="The type of the conditionable")
    conditionable_id: str | None = Field(None, description="The ID of the conditionable. If conditionable_type is AlertField, this is the ID of the alert field.")
    kind: Literal["payload", "alert_field"] | None = Field(None, description="The kind of the conditionable")
    alert_urgency_id: str | None = Field(None, description="The ID of the alert urgency")

class CreateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem(PermissiveModel):
    field: str | None = Field(None, description="JSON path expression to extract a specific value from the alert's payload for evaluation")
    operator: Literal["is", "is_not", "contains", "does_not_contain", "starts_with", "ends_with"] | None = Field(None, description="Comparison operator used to evaluate the extracted value against the specified condition")
    value: str | None = Field(None, description="Value that the extracted payload data is compared to using the specified operator to determine a match")
    conditionable_type: Literal["AlertField"] | None = Field(None, description="The type of the conditionable")
    conditionable_id: str | None = Field(None, description="The ID of the conditionable. If conditionable_type is AlertField, this is the ID of the alert field.")
    kind: Literal["payload", "alert_field"] | None = Field(None, description="The kind of the conditionable")

class CreateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem(PermissiveModel):
    field: Literal["external_id", "state", "alert_title", "alert_external_url", "notification_target_type", "notification_target_id"] | None = Field(None, description="Select the field on which the condition to be evaluated")
    json_path: str | None = Field(None, description="JSON path expression to extract a specific value from the alert's payload for evaluation")

class CreateAsanaSubtaskTaskParamsCompletion(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateAsanaSubtaskTaskParams(PermissiveModel):
    task_type: Literal["create_asana_subtask"] | None = None
    parent_task_id: str = Field(..., description="The parent task id")
    title: str = Field(..., description="The subtask title")
    notes: str | None = None
    assign_user_email: str | None = Field(None, description="The assigned user's email")
    completion: CreateAsanaSubtaskTaskParamsCompletion
    due_date: str | None = Field(None, description="The due date")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    dependency_direction: Literal["blocking", "blocked_by"] | None = 'blocking'
    dependent_task_ids: list[str] | None = Field(None, description="Dependent task ids. Supports liquid syntax")

class CreateAsanaTaskTaskParamsCompletion(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateAsanaTaskTaskParamsProjectsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateAsanaTaskTaskParamsWorkspace(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateAsanaTaskTaskParams(PermissiveModel):
    task_type: Literal["create_asana_task"] | None = None
    workspace: CreateAsanaTaskTaskParamsWorkspace
    projects: list[CreateAsanaTaskTaskParamsProjectsItem]
    title: str = Field(..., description="The task title")
    notes: str | None = None
    assign_user_email: str | None = Field(None, description="The assigned user's email")
    completion: CreateAsanaTaskTaskParamsCompletion
    due_date: str | None = Field(None, description="The due date")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    dependency_direction: Literal["blocking", "blocked_by"] | None = 'blocking'
    dependent_task_ids: list[str] | None = Field(None, description="Dependent task ids. Supports liquid syntax")

class CreateClickupTaskTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateClickupTaskTaskParams(PermissiveModel):
    task_type: Literal["create_clickup_task"] | None = None
    title: str = Field(..., description="The task title")
    description: str | None = Field(None, description="The task description")
    tags: str | None = Field(None, description="The task tags")
    priority: CreateClickupTaskTaskParamsPriority | None = Field(None, description="The priority id and display name")
    due_date: str | None = Field(None, description="The due date")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    task_payload: str | None = Field(None, description="Additional ClickUp task attributes. Will be merged into whatever was specified in this tasks current parameters. Can contain liquid markup and need to be valid JSON")

class CreateCodaPageTaskParamsTemplate(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Combined doc_id/page_id in format 'doc_id/page_id'")
    name: str | None = None

class CreateCodaPageTaskParams(PermissiveModel):
    task_type: Literal["create_coda_page"] | None = None
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page, if desired")
    mark_post_mortem_as_published: bool | None = True
    title: str = Field(..., description="The Coda page title")
    subtitle: str | None = Field(None, description="The Coda page subtitle")
    content: str | None = Field(None, description="The Coda page content")
    template: CreateCodaPageTaskParamsTemplate | None = None
    folder_id: str | None = Field(None, description="The Coda folder id")

class CreateConfluencePageTaskParamsAncestor(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateConfluencePageTaskParamsIntegration(PermissiveModel):
    """Specify integration id if you have more than one Confluence instance"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateConfluencePageTaskParamsSpace(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateConfluencePageTaskParamsTemplate(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateConfluencePageTaskParams(PermissiveModel):
    task_type: Literal["create_confluence_page"] | None = None
    integration: CreateConfluencePageTaskParamsIntegration | None = Field(None, description="Specify integration id if you have more than one Confluence instance")
    space: CreateConfluencePageTaskParamsSpace
    ancestor: CreateConfluencePageTaskParamsAncestor | None = None
    template: CreateConfluencePageTaskParamsTemplate | None = None
    title: str = Field(..., description="The page title")
    content: str | None = Field(None, description="The page content")
    post_mortem_template_id: str | None = Field(None, description="The Retrospective template to use")
    mark_post_mortem_as_published: bool | None = True

class CreateDashboardPanelBodyDataAttributesParamsDatasetsItemAggregate(PermissiveModel):
    operation: Literal["count", "sum", "average"] | None = None
    key: str | None = None
    cumulative: bool | None = None

class CreateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItemRulesItem(PermissiveModel):
    operation: Literal["and", "or"] | None = None
    condition: Literal["=", "!=", ">=", "<=", "exists", "not_exists", "contains", "not_contains"] | None = None
    key: str | None = None
    value: str | None = None

class CreateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItem(PermissiveModel):
    operation: Literal["and", "or"] | None = None
    rules: list[CreateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItemRulesItem] | None = None

class CreateDashboardPanelBodyDataAttributesParamsDatasetsItem(PermissiveModel):
    name: str | None = None
    collection: Literal["alerts", "incidents", "incident_post_mortems", "incident_action_items", "users"] | None = None
    filter_: list[CreateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItem] | None = Field(None, validation_alias="filter", serialization_alias="filter")
    group_by: str | None = None
    aggregate: CreateDashboardPanelBodyDataAttributesParamsDatasetsItemAggregate | None = None

class CreateDatadogNotebookTaskParamsTemplate(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateDatadogNotebookTaskParams(PermissiveModel):
    task_type: Literal["create_datadog_notebook"] | None = None
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating notebook, if desired")
    mark_post_mortem_as_published: bool | None = True
    template: CreateDatadogNotebookTaskParamsTemplate | None = None
    title: str = Field(..., description="The notebook title")
    kind: Literal["postmortem", "runbook", "investigation", "documentation", "report"] = Field(..., description="The notebook kind")
    content: str | None = Field(None, description="The notebook content")

class CreateDropboxPaperPageTaskParamsNamespace(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateDropboxPaperPageTaskParamsParentFolder(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateDropboxPaperPageTaskParams(PermissiveModel):
    task_type: Literal["create_dropbox_paper_page"] | None = None
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page task, if desired")
    mark_post_mortem_as_published: bool | None = True
    title: str = Field(..., description="The page task title")
    content: str | None = Field(None, description="The page content")
    namespace: CreateDropboxPaperPageTaskParamsNamespace | None = None
    parent_folder: CreateDropboxPaperPageTaskParamsParentFolder | None = None

class CreateEnvironmentBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class CreateEnvironmentBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class CreateEscalationLevelBodyDataAttributesNotificationTargetParamsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of notification target. If Slack channel, then id of the slack channel (eg. C06Q2JK7RQW)")
    type_: Literal["team", "user", "schedule", "slack_channel", "service"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the notification target")
    team_members: Literal["all", "admins", "escalate"] | None = Field(None, description="For targets with type=team, controls whether to notify admins, all team members, or escalate to team EP.")

class CreateEscalationLevelPathsBodyDataAttributesNotificationTargetParamsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of notification target. If Slack channel, then id of the slack channel (eg. C06Q2JK7RQW)")
    type_: Literal["team", "user", "schedule", "slack_channel", "service"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the notification target")
    team_members: Literal["all", "admins", "escalate"] | None = Field(None, description="For targets with type=team, controls whether to notify admins, all team members, or escalate to team EP.")

class CreateFunctionalityBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class CreateFunctionalityBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class CreateGithubIssueTaskParamsRepository(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGithubIssueTaskParams(PermissiveModel):
    task_type: Literal["create_github_issue"] | None = None
    title: str = Field(..., description="The issue title")
    body: str | None = Field(None, description="The issue body")
    repository: CreateGithubIssueTaskParamsRepository

class CreateGitlabIssueTaskParamsRepository(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGitlabIssueTaskParams(PermissiveModel):
    task_type: Literal["create_gitlab_issue"] | None = None
    issue_type: Literal["issue", "incident", "test_case", "task"] | None = Field(None, description="The issue type")
    title: str = Field(..., description="The issue title")
    description: str | None = Field(None, description="The issue description")
    repository: CreateGitlabIssueTaskParamsRepository
    labels: str | None = Field(None, description="The issue labels")
    due_date: str | None = Field(None, description="The due date")

class CreateGoToMeetingTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGoToMeetingTaskParams(PermissiveModel):
    task_type: Literal["create_go_to_meeting_task"] | None = None
    subject: str = Field(..., description="The meeting subject")
    conference_call_info: Literal["ptsn", "free", "hyrid", "voip"] | None = 'voip'
    password_required: bool | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateGoToMeetingTaskParamsPostToSlackChannelsItem] | None = None

class CreateGoogleCalendarEventTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGoogleCalendarEventTaskParams(PermissiveModel):
    task_type: Literal["create_google_calendar_event"] | None = None
    attendees: list[str] | None = Field(None, description="Emails of attendees")
    time_zone: str | None = Field(None, description="A valid IANA time zone name.")
    calendar_id: str | None = 'primary'
    days_until_meeting: int = Field(..., description="The days until meeting", ge=0, le=31)
    time_of_meeting: str = Field(..., description="Time of meeting in format HH:MM")
    meeting_duration: str = Field(..., description="Meeting duration in format like '1 hour', '30 minutes'")
    send_updates: bool | None = Field(None, description="Send an email to the attendees notifying them of the event")
    can_guests_modify_event: bool | None = None
    can_guests_see_other_guests: bool | None = None
    can_guests_invite_others: bool | None = None
    summary: str = Field(..., description="The event summary")
    description: str = Field(..., description="The event description")
    exclude_weekends: bool | None = None
    conference_solution_key: Literal["eventHangout", "eventNamedHangout", "hangoutsMeet", "addOn"] | None = Field(None, description="Sets the video conference type attached to the meeting")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateGoogleCalendarEventTaskParamsPostToSlackChannelsItem] | None = None

class CreateGoogleDocsPageTaskParamsDrive(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGoogleDocsPageTaskParamsParentFolder(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGoogleDocsPageTaskParams(PermissiveModel):
    task_type: Literal["create_google_docs_page"] | None = None
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page, if desired")
    mark_post_mortem_as_published: bool | None = True
    title: str = Field(..., description="The page title")
    drive: CreateGoogleDocsPageTaskParamsDrive | None = None
    parent_folder: CreateGoogleDocsPageTaskParamsParentFolder | None = None
    content: str | None = Field(None, description="The page content")
    template_id: str | None = Field(None, description="The Google Doc file ID to use as a template")
    permissions: str | None = Field(None, description="Page permissions JSON")

class CreateGoogleDocsPermissionsTaskParams(PermissiveModel):
    task_type: Literal["create_google_docs_permissions"] | None = None
    file_id: str = Field(..., description="The Google Doc file ID")
    permissions: str = Field(..., description="Page permissions JSON")
    send_notification_email: bool | None = None
    email_message: str | None = Field(None, description="Email message notification")

class CreateGoogleMeetingTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateGoogleMeetingTaskParams(PermissiveModel):
    task_type: Literal["create_google_meeting"] | None = None
    summary: str | None = Field(..., description="[DEPRECATED] The meeting summary")
    description: str | None = Field(..., description="[DEPRECATED] The meeting description")
    conference_solution_key: Literal["eventHangout", "eventNamedHangout", "hangoutsMeet", "addOn"] | None = Field(None, description="[DEPRECATED] Sets the video conference type attached to the meeting")
    record_meeting: bool | None = Field(None, description="Rootly AI will record the meeting and automatically generate a transcript and summary from your meeting")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateGoogleMeetingTaskParamsPostToSlackChannelsItem] | None = None

class CreateIncidentPostmortemTaskParamsTemplate(PermissiveModel):
    """Retrospective template to use"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateIncidentPostmortemTaskParams(PermissiveModel):
    task_type: Literal["create_incident_postmortem"] | None = None
    incident_id: str = Field(..., description="UUID of the incident that needs a retrospective")
    title: str = Field(..., description="The retrospective title")
    status: str | None = None
    template: CreateIncidentPostmortemTaskParamsTemplate | None = Field(None, description="Retrospective template to use")

class CreateIncidentTaskParams(PermissiveModel):
    task_type: Literal["create_incident"] | None = None
    title: str = Field(..., description="The incident title")
    summary: str | None = Field(None, description="The incident summary")
    severity_id: str | None = None
    incident_type_ids: list[str] | None = None
    service_ids: list[str] | None = None
    functionality_ids: list[str] | None = None
    environment_ids: list[str] | None = None
    group_ids: list[str] | None = None
    private: bool | None = None
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")

class CreateIncidentTypeBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class CreateIncidentTypeBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class CreateJiraIssueTaskParamsIntegration(PermissiveModel):
    """Specify integration id if you have more than one Jira instance"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraIssueTaskParamsIssueType(PermissiveModel):
    """The issue type id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraIssueTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraIssueTaskParamsStatus(PermissiveModel):
    """The status id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraIssueTaskParams(PermissiveModel):
    task_type: Literal["create_jira_issue"] | None = None
    integration: CreateJiraIssueTaskParamsIntegration | None = Field(None, description="Specify integration id if you have more than one Jira instance")
    title: str = Field(..., description="The issue title")
    description: str | None = Field(None, description="The issue description")
    labels: str | None = Field(None, description="The issue labels")
    assign_user_email: str | None = Field(None, description="The assigned user's email")
    reporter_user_email: str | None = Field(None, description="The reporter user's email")
    project_key: str = Field(..., description="The project key")
    due_date: str | None = Field(None, description="The due date")
    issue_type: CreateJiraIssueTaskParamsIssueType = Field(..., description="The issue type id and display name")
    priority: CreateJiraIssueTaskParamsPriority | None = Field(None, description="The priority id and display name")
    status: CreateJiraIssueTaskParamsStatus | None = Field(None, description="The status id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    update_payload: str | None = Field(None, description="Update payload. Can contain liquid markup and need to be valid JSON")

class CreateJiraSubtaskTaskParamsIntegration(PermissiveModel):
    """Specify integration id if you have more than one Jira instance"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraSubtaskTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraSubtaskTaskParamsStatus(PermissiveModel):
    """The status id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraSubtaskTaskParamsSubtaskIssueType(PermissiveModel):
    """The issue type id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateJiraSubtaskTaskParams(PermissiveModel):
    task_type: Literal["create_jira_subtask"] | None = None
    integration: CreateJiraSubtaskTaskParamsIntegration | None = Field(None, description="Specify integration id if you have more than one Jira instance")
    project_key: str = Field(..., description="The project key")
    parent_issue_id: str = Field(..., description="The parent issue")
    title: str = Field(..., description="The issue title")
    description: str | None = Field(None, description="The issue description")
    subtask_issue_type: CreateJiraSubtaskTaskParamsSubtaskIssueType = Field(..., description="The issue type id and display name")
    labels: str | None = Field(None, description="The issue labels")
    due_date: str | None = Field(None, description="The due date")
    assign_user_email: str | None = Field(None, description="The assigned user's email")
    reporter_user_email: str | None = Field(None, description="The reporter user's email")
    priority: CreateJiraSubtaskTaskParamsPriority | None = Field(None, description="The priority id and display name")
    status: CreateJiraSubtaskTaskParamsStatus | None = Field(None, description="The status id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    update_payload: str | None = Field(None, description="Update payload. Can contain liquid markup and need to be valid JSON")

class CreateLinearIssueCommentTaskParams(PermissiveModel):
    task_type: Literal["create_linear_issue_comment"] | None = None
    issue_id: str = Field(..., description="The issue id")
    body: str = Field(..., description="The issue description")

class CreateLinearIssueTaskParamsLabelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearIssueTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearIssueTaskParamsProject(PermissiveModel):
    """The project id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearIssueTaskParamsState(PermissiveModel):
    """The state id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearIssueTaskParamsTeam(PermissiveModel):
    """The team id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearIssueTaskParams(PermissiveModel):
    task_type: Literal["create_linear_issue"] | None = None
    title: str = Field(..., description="The issue title")
    description: str | None = Field(None, description="The issue description")
    team: CreateLinearIssueTaskParamsTeam = Field(..., description="The team id and display name")
    state: CreateLinearIssueTaskParamsState = Field(..., description="The state id and display name")
    project: CreateLinearIssueTaskParamsProject | None = Field(None, description="The project id and display name")
    labels: list[CreateLinearIssueTaskParamsLabelsItem] | None = None
    priority: CreateLinearIssueTaskParamsPriority | None = Field(None, description="The priority id and display name")
    assign_user_email: str | None = Field(None, description="The assigned user's email")

class CreateLinearSubtaskIssueTaskParamsLabelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearSubtaskIssueTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearSubtaskIssueTaskParamsState(PermissiveModel):
    """The state id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateLinearSubtaskIssueTaskParams(PermissiveModel):
    task_type: Literal["create_linear_subtask_issue"] | None = None
    parent_issue_id: str = Field(..., description="The parent issue")
    title: str = Field(..., description="The issue title")
    description: str | None = Field(None, description="The issue description")
    state: CreateLinearSubtaskIssueTaskParamsState = Field(..., description="The state id and display name")
    priority: CreateLinearSubtaskIssueTaskParamsPriority | None = Field(None, description="The priority id and display name")
    labels: list[CreateLinearSubtaskIssueTaskParamsLabelsItem] | None = None
    assign_user_email: str | None = Field(None, description="The assigned user's email")

class CreateLiveCallRouterBodyDataAttributesPagingTargetsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of paging target")
    type_: Literal["service", "team", "escalation_policy"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the paging target")
    alert_urgency_id: str = Field(..., description="This is used in escalation paths to determine who to page")

class CreateMicrosoftTeamsChannelTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateMicrosoftTeamsChannelTaskParams(PermissiveModel):
    task_type: Literal["create_microsoft_teams_channel"] | None = None
    team: CreateMicrosoftTeamsChannelTaskParamsTeam | None = None
    title: str = Field(..., description="Microsoft Team channel title")
    description: str | None = Field(None, description="Microsoft Team channel description")
    private: Literal["auto", "true", "false"] | None = 'auto'

class CreateMicrosoftTeamsMeetingTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateMicrosoftTeamsMeetingTaskParams(PermissiveModel):
    task_type: Literal["create_microsoft_teams_meeting"] | None = None
    name: str = Field(..., description="The meeting name")
    subject: str = Field(..., description="The meeting subject")
    record_meeting: bool | None = Field(None, description="Rootly AI will record the meeting and automatically generate a transcript and summary from your meeting")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateMicrosoftTeamsMeetingTaskParamsPostToSlackChannelsItem] | None = None

class CreateMotionTaskTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateMotionTaskTaskParamsProject(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateMotionTaskTaskParamsStatus(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateMotionTaskTaskParamsWorkspace(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateMotionTaskTaskParams(PermissiveModel):
    task_type: Literal["create_motion_task"] | None = None
    workspace: CreateMotionTaskTaskParamsWorkspace
    project: CreateMotionTaskTaskParamsProject | None = None
    status: CreateMotionTaskTaskParamsStatus | None = None
    title: str = Field(..., description="The task title")
    description: str | None = Field(None, description="The task description")
    labels: list[str] | None = None
    priority: CreateMotionTaskTaskParamsPriority | None = Field(None, description="The priority id and display name")
    duration: str | None = Field(None, description="The duration. Eg.  \"NONE\", \"REMINDER\", or a integer greater than 0.")
    due_date: str | None = Field(None, description="The due date")

class CreateNotionPageTaskParamsParentPage(PermissiveModel):
    """The parent page id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateNotionPageTaskParams(PermissiveModel):
    task_type: Literal["create_notion_page"] | None = None
    title: str = Field(..., description="The Notion page title")
    parent_page: CreateNotionPageTaskParamsParentPage = Field(..., description="The parent page id and display name")
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page task, if desired")
    content: str | None = Field(None, description="Custom page content with liquid templating support. When provided, only this content will be rendered (no default sections)")
    mark_post_mortem_as_published: bool | None = True
    show_timeline_as_table: bool | None = None
    show_action_items_as_table: bool | None = None

class CreateOpsgenieAlertTaskParamsEscalationsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateOpsgenieAlertTaskParamsSchedulesItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateOpsgenieAlertTaskParamsTeamsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateOpsgenieAlertTaskParamsUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateOpsgenieAlertTaskParams(PermissiveModel):
    task_type: Literal["create_opsgenie_alert"] | None = None
    message: str = Field(..., description="Message of the alert")
    description: str | None = Field(None, description="Description field of the alert that is generally used to provide a detailed information about the alert")
    teams: list[CreateOpsgenieAlertTaskParamsTeamsItem] | None = None
    users: list[CreateOpsgenieAlertTaskParamsUsersItem] | None = None
    schedules: list[CreateOpsgenieAlertTaskParamsSchedulesItem] | None = None
    escalations: list[CreateOpsgenieAlertTaskParamsEscalationsItem] | None = None
    priority: Literal["P1", "P2", "P3", "P4", "P5", "auto"] | None = 'P1'
    details: str | None = Field(None, description="Details payload. Can contain liquid markup and need to be valid JSON")

class CreateOutlookEventTaskParamsCalendar(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateOutlookEventTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateOutlookEventTaskParams(PermissiveModel):
    task_type: Literal["create_outlook_event"] | None = None
    calendar: CreateOutlookEventTaskParamsCalendar
    attendees: list[str] | None = Field(None, description="Emails of attendees")
    time_zone: str | None = Field(None, description="A valid IANA time zone name.")
    days_until_meeting: int = Field(..., description="The days until meeting", ge=0, le=31)
    time_of_meeting: str = Field(..., description="Time of meeting in format HH:MM")
    meeting_duration: str = Field(..., description="Meeting duration in format like '1 hour', '30 minutes'")
    summary: str = Field(..., description="The event summary")
    description: str = Field(..., description="The event description")
    exclude_weekends: bool | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateOutlookEventTaskParamsPostToSlackChannelsItem] | None = None

class CreatePagerdutyStatusUpdateTaskParams(PermissiveModel):
    task_type: Literal["create_pagerduty_status_update"] | None = None
    pagerduty_incident_id: str = Field(..., description="PagerDuty incident id")
    message: str = Field(..., description="A message outlining the incident's resolution in PagerDuty")

class CreatePagertreeAlertTaskParamsTeamsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreatePagertreeAlertTaskParamsUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreatePagertreeAlertTaskParams(PermissiveModel):
    task_type: Literal["create_pagertree_alert"] | None = None
    title: str | None = Field(None, description="Title of alert as text")
    description: str | None = Field(None, description="Description of alert as text")
    urgency: Literal["auto", "critical", "high", "medium", "low"] | None = None
    severity: Literal["auto", "SEV-1", "SEV-2", "SEV-3", "SEV-4"] | None = None
    teams: list[CreatePagertreeAlertTaskParamsTeamsItem] | None = None
    users: list[CreatePagertreeAlertTaskParamsUsersItem] | None = None
    incident: bool | None = Field(None, description="Setting to true makes an alert a Pagertree incident")

class CreateQuipPageTaskParams(PermissiveModel):
    task_type: Literal["create_google_docs_page"] | None = None
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page, if desired")
    title: str = Field(..., description="The page title")
    parent_folder_id: str | None = Field(None, description="The parent folder id")
    content: str | None = Field(None, description="The page content")
    template_id: str | None = Field(None, description="The Quip file ID to use as a template")
    mark_post_mortem_as_published: bool | None = True

class CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0(StrictModel):
    severity_ids: list[str] = Field(..., description="Severity ID's for retrospective process matching criteria")

class CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1(StrictModel):
    group_ids: list[str] = Field(..., description="Team ID's for retrospective process matching criteria")

class CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2(StrictModel):
    incident_type_ids: list[str] = Field(..., description="Incident type ID's for retrospective process matching criteria")

class CreateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem(PermissiveModel):
    start_time: str | None = Field(None, description="Start time for schedule rotation active time", json_schema_extra={'format': 'time'})
    end_time: str | None = Field(None, description="End time for schedule rotation active time", json_schema_extra={'format': 'time'})

class CreateScheduleRotationBodyDataAttributesActiveTimeAttributesItem(PermissiveModel):
    start_time: str = Field(..., description="Start time for schedule rotation active time", json_schema_extra={'format': 'time'})
    end_time: str = Field(..., description="End time for schedule rotation active time", json_schema_extra={'format': 'time'})

class CreateScheduleRotationBodyDataAttributesScheduleRotationableAttributes(PermissiveModel):
    handoff_time: str = Field(..., description="Hand off time for daily rotation", json_schema_extra={'format': 'time'})
    handoff_day: Literal["F", "M", "R", "S", "T", "U", "W", "first_day_of_month", "last_day_of_month"] | None = Field(None, description="Hand off day for weekly/biweekly rotation")
    shift_length: int | None = Field(None, description="Shift length for custom rotation")
    shift_length_unit: Literal["days", "hours", "weeks"] | None = Field(None, description="Shift length unit for custom rotation")

class CreateServiceBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class CreateServiceBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class CreateServiceNowIncidentTaskParamsCompletion(PermissiveModel):
    """The completion id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateServiceNowIncidentTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateServiceNowIncidentTaskParams(PermissiveModel):
    task_type: Literal["create_service_now_incident"] | None = None
    title: str = Field(..., description="The incident title")
    description: str | None = Field(None, description="The incident description")
    priority: CreateServiceNowIncidentTaskParamsPriority | None = Field(None, description="The priority id and display name")
    completion: CreateServiceNowIncidentTaskParamsCompletion | None = Field(None, description="The completion id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")

class CreateSeverityBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class CreateSeverityBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class CreateSharepointPageTaskParamsDrive(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateSharepointPageTaskParamsParentFolder(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateSharepointPageTaskParamsSite(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateSharepointPageTaskParams(PermissiveModel):
    task_type: Literal["create_sharepoint_page"] | None = None
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page, if desired")
    mark_post_mortem_as_published: bool | None = True
    title: str = Field(..., description="The page title")
    site: CreateSharepointPageTaskParamsSite
    drive: CreateSharepointPageTaskParamsDrive
    parent_folder: CreateSharepointPageTaskParamsParentFolder | None = None
    content: str | None = Field(None, description="The page content")
    template_id: str | None = Field(None, description="The SharePoint file ID to use as a template")

class CreateShortcutStoryTaskParamsArchivation(PermissiveModel):
    """The archivation id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateShortcutStoryTaskParamsGroup(PermissiveModel):
    """The group id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateShortcutStoryTaskParamsProject(PermissiveModel):
    """The project id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateShortcutStoryTaskParamsWorkflowState(PermissiveModel):
    """The workflow state id workflow state name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateShortcutStoryTaskParams(PermissiveModel):
    task_type: Literal["create_shortcut_story"] | None = None
    title: str = Field(..., description="The incident title")
    kind: Literal["bug", "chore", "feature"]
    description: str | None = Field(None, description="The incident description")
    labels: str | None = Field(None, description="The story labels")
    due_date: str | None = Field(None, description="The due date")
    archivation: CreateShortcutStoryTaskParamsArchivation = Field(..., description="The archivation id and display name")
    group: CreateShortcutStoryTaskParamsGroup | None = Field(None, description="The group id and display name")
    project: CreateShortcutStoryTaskParamsProject | None = Field(None, description="The project id and display name")
    workflow_state: CreateShortcutStoryTaskParamsWorkflowState | None = Field(None, description="The workflow state id workflow state name")

class CreateShortcutTaskTaskParamsCompletion(PermissiveModel):
    """The completion id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateShortcutTaskTaskParams(PermissiveModel):
    task_type: Literal["create_shortcut_task"] | None = None
    parent_story_id: str = Field(..., description="The parent story")
    description: str = Field(..., description="The task description")
    completion: CreateShortcutTaskTaskParamsCompletion = Field(..., description="The completion id and display name")

class CreateSlackChannelTaskParamsWorkspace(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateSlackChannelTaskParams(PermissiveModel):
    task_type: Literal["create_slack_channel"] | None = None
    workspace: CreateSlackChannelTaskParamsWorkspace
    title: str = Field(..., description="Slack channel title")
    private: Literal["auto", "true", "false"] | None = 'auto'

class CreateTeamBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class CreateTeamBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class CreateTrelloCardTaskParamsArchivation(PermissiveModel):
    """The archivation id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateTrelloCardTaskParamsBoard(PermissiveModel):
    """The board id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateTrelloCardTaskParamsLabelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateTrelloCardTaskParamsList(PermissiveModel):
    """The list id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateTrelloCardTaskParams(PermissiveModel):
    task_type: Literal["create_trello_card"] | None = None
    title: str = Field(..., description="The card title")
    description: str | None = Field(None, description="The card description")
    due_date: str | None = Field(None, description="The due date")
    board: CreateTrelloCardTaskParamsBoard = Field(..., description="The board id and display name")
    list_: CreateTrelloCardTaskParamsList = Field(..., validation_alias="list", serialization_alias="list", description="The list id and display name")
    labels: list[CreateTrelloCardTaskParamsLabelsItem] | None = None
    archivation: CreateTrelloCardTaskParamsArchivation | None = Field(None, description="The archivation id and display name")

class CreateWebexMeetingTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateWebexMeetingTaskParams(PermissiveModel):
    task_type: Literal["create_webex_meeting"] | None = None
    topic: str = Field(..., description="The meeting topic")
    password: str | None = Field(None, description="The meeting password")
    record_meeting: bool | None = Field(None, description="Rootly AI will record the meeting and automatically generate a transcript and summary from your meeting")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateWebexMeetingTaskParamsPostToSlackChannelsItem] | None = None

class CreateWorkflowRunBodyDataAttributesV0(PermissiveModel):
    immediate: bool | None = Field(True, description="If false, this will respect wait time configured on the workflow.")
    check_conditions: bool | None = Field(False, description="If true, this will check conditions. If conditions are not satisfied the run will not be created.")
    context: dict[str, Any] | None = None

class CreateWorkflowRunBodyDataAttributesV1(PermissiveModel):
    incident_id: str
    immediate: bool | None = Field(True, description="If false, this will respect wait time configured on the workflow")
    check_conditions: bool | None = Field(False, description="If true, this will check conditions. If conditions are not satisfied the run will not be created")
    context: dict[str, Any] | None = None

class CreateWorkflowRunBodyDataAttributesV2(PermissiveModel):
    post_mortem_id: str
    immediate: bool | None = Field(True, description="If false, this will respect wait time configured on the workflow")
    check_conditions: bool | None = Field(False, description="If true, this will check conditions. If conditions are not satisfied the run will not be created")
    context: dict[str, Any] | None = None

class CreateWorkflowRunBodyDataAttributesV3(PermissiveModel):
    action_item_id: str
    immediate: bool | None = Field(True, description="If false, this will respect wait time configured on the workflow")
    check_conditions: bool | None = Field(False, description="If true, this will check conditions. If conditions are not satisfied the run will not be created")
    context: dict[str, Any] | None = None

class CreateWorkflowRunBodyDataAttributesV4(PermissiveModel):
    alert_id: str
    immediate: bool | None = Field(True, description="If false, this will respect wait time configured on the workflow")
    check_conditions: bool | None = Field(False, description="If true, this will check conditions. If conditions are not satisfied the run will not be created")
    context: dict[str, Any] | None = None

class CreateWorkflowRunBodyDataAttributesV5(PermissiveModel):
    pulse_id: str
    immediate: bool | None = Field(True, description="If false, this will respect wait time configured on the workflow")
    check_conditions: bool | None = Field(False, description="If true, this will check conditions. If conditions are not satisfied the run will not be created")
    context: dict[str, Any] | None = None

class CreateZendeskJiraLinkTaskParams(PermissiveModel):
    task_type: Literal["create_zendesk_jira_link"] | None = None
    jira_issue_id: str = Field(..., description="Jira Issue Id.")
    jira_issue_key: str = Field(..., description="Jira Issue Key.")
    zendesk_ticket_id: str = Field(..., description="Zendesk Ticket Id.")

class CreateZendeskTicketTaskParamsCompletion(PermissiveModel):
    """The completion id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateZendeskTicketTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateZendeskTicketTaskParams(PermissiveModel):
    task_type: Literal["create_zendesk_ticket"] | None = None
    kind: Literal["problem", "incident", "question", "task"]
    subject: str = Field(..., description="The ticket subject")
    comment: str | None = Field(None, description="The ticket comment")
    tags: str | None = Field(None, description="The ticket tags")
    priority: CreateZendeskTicketTaskParamsPriority | None = Field(None, description="The priority id and display name")
    completion: CreateZendeskTicketTaskParamsCompletion | None = Field(None, description="The completion id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    ticket_payload: str | None = Field(None, description="Additional Zendesk ticket attributes. Will be merged into whatever was specified in this tasks current parameters. Can contain liquid markup and need to be valid JSON")

class CreateZoomMeetingTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class CreateZoomMeetingTaskParams(PermissiveModel):
    task_type: Literal["create_zoom_meeting"] | None = None
    topic: str = Field(..., description="The meeting topic")
    password: str | None = Field(None, description="The meeting password")
    create_as_email: str | None = Field(None, description="The email to use if creating as email")
    alternative_hosts: list[str] | None = None
    auto_recording: Literal["none", "local", "cloud"] | None = 'none'
    record_meeting: bool | None = Field(None, description="Rootly AI will record the meeting and automatically generate a transcript and summary from your meeting")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[CreateZoomMeetingTaskParamsPostToSlackChannelsItem] | None = None

class EnvironmentSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class EnvironmentSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class Environment(PermissiveModel):
    name: str = Field(..., description="The name of the environment")
    slug: str | None = Field(None, description="The slug of the environment")
    description: str | None = Field(None, description="The description of the environment")
    notify_emails: list[str] | None = Field(None, description="Emails attached to the environment")
    color: str | None = Field(None, description="The hex color of the environment")
    position: int | None = Field(None, description="Position of the environment")
    slack_channels: list[EnvironmentSlackChannelsItem] | None = Field(None, description="Slack Channels associated with this environment")
    slack_aliases: list[EnvironmentSlackAliasesItem] | None = Field(None, description="Slack Aliases associated with this environment")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class EnvironmentResponseData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of the environment")
    type_: Literal["environments"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: Environment

class EnvironmentResponse(PermissiveModel):
    data: EnvironmentResponseData

class EscalationPolicyBusinessHours(PermissiveModel):
    time_zone: str | None = Field(None, description="Time zone for business hours")
    days: list[Literal["M", "T", "W", "R", "F", "U", "S"]] | None = Field(None, description="Business days")
    start_time: str | None = Field(None, description="Start time for business hours (HH:MM)")
    end_time: str | None = Field(None, description="End time for business hours (HH:MM)")

class EscalationPolicy(PermissiveModel):
    name: str = Field(..., description="The name of the escalation policy")
    description: str | None = Field(None, description="The description of the escalation policy")
    repeat_count: int = Field(..., description="The number of times this policy will be executed until someone acknowledges the alert")
    created_by_user_id: int = Field(..., description="User who created the escalation policy")
    last_updated_by_user_id: int | None = Field(None, description="User who updated the escalation policy")
    group_ids: list[str] | None = Field(None, description="Associated groups (alerting the group will trigger escalation policy)")
    service_ids: list[str] | None = Field(None, description="Associated services (alerting the service will trigger escalation policy)")
    business_hours: EscalationPolicyBusinessHours | None = None
    created_at: str | None = Field(None, description="Date of creation")
    updated_at: str | None = Field(None, description="Date of last update")

class FunctionalitySlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class FunctionalitySlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class Functionality(PermissiveModel):
    name: str = Field(..., description="The name of the functionality")
    slug: str | None = Field(None, description="The slug of the functionality")
    description: str | None = Field(None, description="The description of the functionality")
    public_description: str | None = Field(None, description="The public description of the functionality")
    notify_emails: list[str] | None = Field(None, description="Emails attached to the functionality")
    color: str | None = Field(None, description="The hex color of the functionality")
    backstage_id: str | None = Field(None, description="The Backstage entity id associated to this functionality. eg: :namespace/:kind/:entity_name")
    external_id: str | None = Field(None, description="The external id associated to this functionality")
    pagerduty_id: str | None = Field(None, description="The PagerDuty service id associated to this functionality")
    opsgenie_id: str | None = Field(None, description="The Opsgenie service id associated to this functionality")
    opsgenie_team_id: str | None = Field(None, description="The Opsgenie team id associated to this functionality")
    cortex_id: str | None = Field(None, description="The Cortex group id associated to this functionality")
    service_now_ci_sys_id: str | None = Field(None, description="The Service Now CI sys id associated to this functionality")
    position: int | None = Field(None, description="Position of the functionality")
    environment_ids: list[str] | None = Field(None, description="Environments associated with this functionality")
    service_ids: list[str] | None = Field(None, description="Services associated with this functionality")
    owner_group_ids: list[str] | None = Field(None, description="Owner Teams associated with this functionality")
    owner_user_ids: list[int] | None = Field(None, description="Owner Users associated with this functionality")
    slack_channels: list[FunctionalitySlackChannelsItem] | None = Field(None, description="Slack Channels associated with this functionality")
    slack_aliases: list[FunctionalitySlackAliasesItem] | None = Field(None, description="Slack Aliases associated with this functionality")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class FunctionalityResponseData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of the functionality")
    type_: Literal["functionalities"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: Functionality

class FunctionalityResponse(PermissiveModel):
    data: FunctionalityResponseData

class GeniusCreateAnthropicChatCompletionTaskParamsModel(PermissiveModel):
    """The Anthropic model. eg: claude-3-5-sonnet-20241022"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GeniusCreateAnthropicChatCompletionTaskParams(PermissiveModel):
    task_type: Literal["genius_create_anthropic_chat_completion_task"] | None = None
    model: GeniusCreateAnthropicChatCompletionTaskParamsModel = Field(..., description="The Anthropic model. eg: claude-3-5-sonnet-20241022")
    system_prompt: str | None = Field(None, description="The system prompt to send to Anthropic (optional)")
    prompt: str = Field(..., description="The prompt to send to Anthropic")

class GeniusCreateGoogleGeminiChatCompletionTaskParamsModel(PermissiveModel):
    """The Gemini model. eg: gemini-2.0-flash"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GeniusCreateGoogleGeminiChatCompletionTaskParams(PermissiveModel):
    task_type: Literal["genius_create_google_gemini_chat_completion_task"] | None = None
    model: GeniusCreateGoogleGeminiChatCompletionTaskParamsModel = Field(..., description="The Gemini model. eg: gemini-2.0-flash")
    system_prompt: str | None = Field(None, description="The system prompt to send to Gemini (optional)")
    prompt: str = Field(..., description="The prompt to send to Gemini")

class GeniusCreateOpenaiChatCompletionTaskParamsModel(PermissiveModel):
    """The OpenAI model. eg: gpt-4o-mini"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GeniusCreateOpenaiChatCompletionTaskParams(PermissiveModel):
    task_type: Literal["genius_openai_chat_completion"] | None = None
    model: GeniusCreateOpenaiChatCompletionTaskParamsModel = Field(..., description="The OpenAI model. eg: gpt-4o-mini")
    system_prompt: str | None = Field(None, description="The system prompt to send to OpenAI (optional)")
    prompt: str = Field(..., description="The prompt to send to OpenAI")

class GeniusCreateWatsonxChatCompletionTaskParamsModel(PermissiveModel):
    """The WatsonX model. eg: ibm/granite-3-b8b-instruct"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GeniusCreateWatsonxChatCompletionTaskParams(PermissiveModel):
    task_type: Literal["genius_create_watsonx_chat_completion_task"] | None = None
    model: GeniusCreateWatsonxChatCompletionTaskParamsModel = Field(..., description="The WatsonX model. eg: ibm/granite-3-b8b-instruct")
    system_prompt: str | None = Field(None, description="The system prompt to send to WatsonX (optional)")
    prompt: str = Field(..., description="The prompt to send to WatsonX")
    project_id: str

class GetAlertsTaskParamsParentMessageThreadTask(PermissiveModel):
    """A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GetAlertsTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GetAlertsTaskParams(PermissiveModel):
    task_type: Literal["get_alerts"] | None = None
    service_ids: list[str] | None = None
    environment_ids: list[str] | None = None
    labels: list[str] | None = None
    sources: list[str] | None = None
    past_duration: str = Field(..., description="How far back to fetch commits (in format '1 minute', '30 days', '3 months', etc.)")
    services_impacted_by_incident: bool | None = None
    environments_impacted_by_incident: bool | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[GetAlertsTaskParamsPostToSlackChannelsItem] | None = None
    parent_message_thread_task: GetAlertsTaskParamsParentMessageThreadTask | None = Field(None, description="A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task")

class GetGithubCommitsTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GetGithubCommitsTaskParams(PermissiveModel):
    task_type: Literal["get_github_commits"] | None = None
    service_ids: list[str] | None = None
    github_repository_names: list[str] | None = None
    branch: str = Field(..., description="The branch")
    past_duration: str = Field(..., description="How far back to fetch commits (in format '1 minute', '30 days', '3 months', etc.)")
    services_impacted_by_incident: bool | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[GetGithubCommitsTaskParamsPostToSlackChannelsItem] | None = None

class GetGitlabCommitsTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GetGitlabCommitsTaskParams(PermissiveModel):
    task_type: Literal["get_gitlab_commits"] | None = None
    service_ids: list[str] | None = None
    gitlab_repository_names: list[str] | None = None
    branch: str = Field(..., description="The branch")
    past_duration: str = Field(..., description="How far back to fetch commits (in format '1 minute', '30 days', '3 months', etc.)")
    services_impacted_by_incident: bool | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[GetGitlabCommitsTaskParamsPostToSlackChannelsItem] | None = None

class GetPulsesTaskParamsParentMessageThreadTask(PermissiveModel):
    """A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GetPulsesTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class GetPulsesTaskParams(PermissiveModel):
    task_type: Literal["get_pulses"] | None = None
    service_ids: list[str] | None = None
    environment_ids: list[str] | None = None
    labels: list[str] | None = None
    refs: list[str] | None = None
    sources: list[str] | None = None
    past_duration: str = Field(..., description="How far back to fetch commits (in format '1 minute', '30 days', '3 months', etc.)")
    services_impacted_by_incident: bool | None = None
    environments_impacted_by_incident: bool | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[GetPulsesTaskParamsPostToSlackChannelsItem] | None = None
    parent_message_thread_task: GetPulsesTaskParamsParentMessageThreadTask | None = Field(None, description="A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task")

class HttpClientTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class HttpClientTaskParams(PermissiveModel):
    task_type: Literal["http_client"] | None = None
    headers: str | None = Field(None, description="JSON map of HTTP headers")
    params: str | None = Field(None, description="JSON map of HTTP query parameters")
    body: str | None = Field(None, description="HTTP body")
    url: str = Field(..., description="URL endpoint")
    event_url: str | None = None
    event_message: str | None = None
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"] | None = Field('GET', description="HTTP method")
    succeed_on_status: str = Field(..., description="HTTP status code expected. Can be a regular expression. Eg: 200, 200|203, 20[0-3]")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[HttpClientTaskParamsPostToSlackChannelsItem] | None = None

class IncidentTypeSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class IncidentTypeSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class IncidentType(PermissiveModel):
    name: str = Field(..., description="The name of the incident type")
    slug: str | None = Field(None, description="The slug of the incident type")
    description: str | None = Field(None, description="The description of the incident type")
    color: str | None = Field(None, description="The hex color of the incident type")
    position: int | None = Field(None, description="Position of the incident type")
    notify_emails: list[str] | None = Field(None, description="Emails to attach to the incident type")
    slack_channels: list[IncidentTypeSlackChannelsItem] | None = Field(None, description="Slack Channels associated with this incident type")
    slack_aliases: list[IncidentTypeSlackAliasesItem] | None = Field(None, description="Slack Aliases associated with this incident type")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class IncidentTypeResponseData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of the incident type")
    type_: Literal["incident_types"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: IncidentType

class IncidentTypeResponse(PermissiveModel):
    data: IncidentTypeResponseData

class InviteToMicrosoftTeamsChannelTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToMicrosoftTeamsChannelTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToMicrosoftTeamsChannelTaskParams(PermissiveModel):
    task_type: Literal["invite_to_microsoft_teams_channel"] | None = None
    team: InviteToMicrosoftTeamsChannelTaskParamsTeam | None = None
    channel: InviteToMicrosoftTeamsChannelTaskParamsChannel
    emails: str = Field(..., description="Comma separated list of emails to invite")

class InviteToSlackChannelOpsgenieTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelOpsgenieTaskParamsSchedule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelOpsgenieTaskParams(PermissiveModel):
    task_type: Literal["invite_to_slack_channel_opsgenie"] | None = None
    channels: list[InviteToSlackChannelOpsgenieTaskParamsChannelsItem]
    schedule: InviteToSlackChannelOpsgenieTaskParamsSchedule

class InviteToSlackChannelPagerdutyTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelPagerdutyTaskParamsEscalationPolicy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelPagerdutyTaskParamsSchedule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelPagerdutyTaskParamsService(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelPagerdutyTaskParams(PermissiveModel):
    task_type: Literal["invite_to_slack_channel_pagerduty"] | None = None
    channels: list[InviteToSlackChannelPagerdutyTaskParamsChannelsItem]
    escalation_policy: InviteToSlackChannelPagerdutyTaskParamsEscalationPolicy | None = None
    schedule: InviteToSlackChannelPagerdutyTaskParamsSchedule | None = None
    service: InviteToSlackChannelPagerdutyTaskParamsService | None = None

class InviteToSlackChannelRootlyTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelRootlyTaskParamsEscalationPolicyTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelRootlyTaskParamsGroupTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelRootlyTaskParamsScheduleTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelRootlyTaskParamsServiceTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelRootlyTaskParamsUserTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelRootlyTaskParams(PermissiveModel):
    task_type: Literal["invite_to_slack_channel_rootly"] | None = None
    channels: list[InviteToSlackChannelRootlyTaskParamsChannelsItem]
    escalation_policy_target: InviteToSlackChannelRootlyTaskParamsEscalationPolicyTarget | None = None
    service_target: InviteToSlackChannelRootlyTaskParamsServiceTarget | None = None
    user_target: InviteToSlackChannelRootlyTaskParamsUserTarget | None = None
    group_target: InviteToSlackChannelRootlyTaskParamsGroupTarget | None = None
    schedule_target: InviteToSlackChannelRootlyTaskParamsScheduleTarget | None = None

class InviteToSlackChannelTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelTaskParamsSlackUserGroupsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelTaskParamsSlackUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelTaskParams(PermissiveModel):
    task_type: Literal["invite_to_slack_channel"] | None = None
    channel: InviteToSlackChannelTaskParamsChannel
    slack_users: list[InviteToSlackChannelTaskParamsSlackUsersItem] | None = None
    slack_user_groups: list[InviteToSlackChannelTaskParamsSlackUserGroupsItem] | None = None
    slack_emails: str | None = Field(None, description="Comma separated list of emails to invite to the channel")

class InviteToSlackChannelVictorOpsTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelVictorOpsTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class InviteToSlackChannelVictorOpsTaskParams(PermissiveModel):
    task_type: Literal["invite_to_slack_channel_victor_ops"] | None = None
    channels: list[InviteToSlackChannelVictorOpsTaskParamsChannelsItem]
    team: InviteToSlackChannelVictorOpsTaskParamsTeam

class PageOpsgenieOnCallRespondersTaskParamsTeamsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageOpsgenieOnCallRespondersTaskParamsUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageOpsgenieOnCallRespondersTaskParams(PermissiveModel):
    task_type: Literal["page_opsgenie_on_call_responders"] | None = None
    title: str | None = Field(None, description="Incident title.")
    message: str | None = Field(None, description="Message of the incident")
    description: str | None = Field(None, description="Description field of the incident that is generally used to provide a detailed information about the incident")
    teams: list[PageOpsgenieOnCallRespondersTaskParamsTeamsItem] | None = None
    users: list[PageOpsgenieOnCallRespondersTaskParamsUsersItem] | None = None
    priority: Literal["P1", "P2", "P3", "P4", "P5", "auto"] | None = 'P1'

class PagePagerdutyOnCallRespondersTaskParamsEscalationPoliciesItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PagePagerdutyOnCallRespondersTaskParamsService(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PagePagerdutyOnCallRespondersTaskParamsUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PagePagerdutyOnCallRespondersTaskParams(PermissiveModel):
    task_type: Literal["page_pagerduty_on_call_responders"] | None = None
    service: PagePagerdutyOnCallRespondersTaskParamsService
    escalation_policies: list[PagePagerdutyOnCallRespondersTaskParamsEscalationPoliciesItem] | None = None
    users: list[PagePagerdutyOnCallRespondersTaskParamsUsersItem] | None = None
    title: str | None = Field(None, description="Incident title.")
    message: str | None = None
    urgency: Literal["high", "low", "auto"] | None = 'high'
    priority: str | None = Field(None, description="PagerDuty incident priority, selecting auto will let Rootly auto map our incident severity")
    create_new_incident_on_conflict: bool | None = Field(False, description="Rootly only supports linking to a single PagerDuty incident. If this feature is disabled Rootly will add responders from any additional pages to the existing PagerDuty incident that is linked to the Rootly incident. If enabled, Rootly will create a new PagerDuty incident that is not linked to any Rootly incidents")

class PageRootlyOnCallRespondersTaskParamsEscalationPolicyTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageRootlyOnCallRespondersTaskParamsGroupTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageRootlyOnCallRespondersTaskParamsServiceTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageRootlyOnCallRespondersTaskParamsUserTarget(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageRootlyOnCallRespondersTaskParams(PermissiveModel):
    task_type: Literal["page_rootly_on_call_responders"] | None = None
    escalation_policy_target: PageRootlyOnCallRespondersTaskParamsEscalationPolicyTarget | None = None
    service_target: PageRootlyOnCallRespondersTaskParamsServiceTarget | None = None
    user_target: PageRootlyOnCallRespondersTaskParamsUserTarget | None = None
    group_target: PageRootlyOnCallRespondersTaskParamsGroupTarget | None = None
    alert_urgency_id: str | None = Field(None, description="Alert urgency ID")
    summary: str = Field(..., description="Alert title")
    description: str | None = Field(None, description="Alert description")
    escalation_note: str | None = None

class PageVictorOpsOnCallRespondersTaskParamsEscalationPoliciesItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageVictorOpsOnCallRespondersTaskParamsUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PageVictorOpsOnCallRespondersTaskParams(PermissiveModel):
    task_type: Literal["page_victor_ops_on_call_responders"] | None = None
    escalation_policies: list[PageVictorOpsOnCallRespondersTaskParamsEscalationPoliciesItem] | None = None
    users: list[PageVictorOpsOnCallRespondersTaskParamsUsersItem] | None = None
    title: str | None = Field(None, description="Alert title.")

class PrintTaskParams(PermissiveModel):
    task_type: Literal["print"] | None = None
    message: str = Field(..., description="The message to print")

class PublishIncidentTaskParamsIncident(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PublishIncidentTaskParamsStatusPageTemplate(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class PublishIncidentTaskParams(PermissiveModel):
    task_type: Literal["publish_incident"] | None = None
    incident: PublishIncidentTaskParamsIncident
    public_title: str
    event: str | None = Field(None, description="Incident event description")
    status: Literal["investigating", "identified", "monitoring", "resolved", "scheduled", "in_progress", "verifying", "completed"]
    notify_subscribers: bool | None = Field(False, description="When true notifies subscribers of the status page by email/text")
    should_tweet: bool | None = Field(False, description="For Statuspage.io integrated pages auto publishes a tweet for your update")
    status_page_template: PublishIncidentTaskParamsStatusPageTemplate | None = None
    status_page_id: str
    integration_payload: str | None = Field(None, description="Additional API Payload you can pass to statuspage.io for example. Can contain liquid markup and need to be valid JSON")

class RedisClientTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class RedisClientTaskParams(PermissiveModel):
    task_type: Literal["redis_client"] | None = None
    url: str
    commands: str
    event_url: str | None = None
    event_message: str | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[RedisClientTaskParamsPostToSlackChannelsItem] | None = None

class RemoveGoogleDocsPermissionsTaskParams(PermissiveModel):
    task_type: Literal["remove_google_docs_permissions"] | None = None
    file_id: str = Field(..., description="The Google Doc file ID")
    attribute_to_query_by: Literal["type", "role", "email_address"]
    value: str

class RenameMicrosoftTeamsChannelTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class RenameMicrosoftTeamsChannelTaskParamsTeam(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class RenameMicrosoftTeamsChannelTaskParams(PermissiveModel):
    task_type: Literal["rename_microsoft_teams_channel"] | None = None
    team: RenameMicrosoftTeamsChannelTaskParamsTeam
    channel: RenameMicrosoftTeamsChannelTaskParamsChannel
    title: str

class RenameSlackChannelTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class RenameSlackChannelTaskParams(PermissiveModel):
    task_type: Literal["rename_slack_channel"] | None = None
    channel: RenameSlackChannelTaskParamsChannel
    title: str

class Role(PermissiveModel):
    name: str = Field(..., description="The role name.")
    slug: str = Field(..., description="The role slug.")
    incident_permission_set_id: str | None = Field(None, description="Associated incident permissions set.")
    is_deletable: bool | None = Field(None, description="Whether the role can be deleted.")
    is_editable: bool | None = Field(None, description="Whether the role can be edited.")
    alerts_permissions: list[Literal["create", "read"]] | None = None
    api_keys_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    audits_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    billing_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    environments_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    form_fields_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    functionalities_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    groups_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    incident_causes_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    incident_feedbacks_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    incident_roles_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    incident_types_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    incidents_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    integrations_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    invitations_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    playbooks_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    private_incidents_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    pulses_permissions: list[Literal["create", "update", "read"]] | None = None
    retrospective_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    roles_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    secrets_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    services_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    severities_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    status_pages_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    webhooks_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    workflows_permissions: list[Literal["create", "read", "update", "delete"]] | None = None
    created_at: str
    updated_at: str

class RunCommandHerokuTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class RunCommandHerokuTaskParams(PermissiveModel):
    task_type: Literal["run_command_heroku"] | None = None
    command: str
    app_name: str
    size: Literal["standard-1X", "standard-2X"]
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[RunCommandHerokuTaskParamsPostToSlackChannelsItem] | None = None

class ScheduleSlackUserGroup(PermissiveModel):
    """Synced slack group of the schedule"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str | None = Field(None, description="Slack channel name")

class Schedule(PermissiveModel):
    name: str = Field(..., description="The name of the schedule")
    description: str | None = Field(None, description="The description of the schedule")
    all_time_coverage: bool | None = Field(None, description="24/7 coverage of the schedule")
    slack_user_group: ScheduleSlackUserGroup | None = Field(None, description="Synced slack group of the schedule")
    owner_group_ids: list[str] | None = Field(None, description="Owning teams.")
    owner_user_id: int | None = Field(None, description="ID of user assigned as owner of the schedule")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class SendDashboardReportTaskParams(PermissiveModel):
    task_type: Literal["send_dashboard_report"] | None = None
    dashboard_ids: list[str]
    from_: str | None = Field('Rootly <workflows@rootly.com>', validation_alias="from", serialization_alias="from", description="The from email address. Need to use SMTP integration if different than rootly.com")
    to: list[str]
    subject: str = Field(..., description="The subject")
    preheader: str | None = Field(None, description="The preheader")
    body: str | None = Field(..., description="The email body")

class SendEmailTaskParams(PermissiveModel):
    task_type: Literal["send_email"] | None = None
    from_: str | None = Field('Rootly <workflows@rootly.com>', validation_alias="from", serialization_alias="from", description="The from email address. Need to use SMTP integration if different than rootly.com")
    to: list[str]
    cc: list[str] | None = None
    bcc: list[str] | None = None
    subject: str = Field(..., description="The subject")
    preheader: str | None = Field(None, description="The preheader")
    body: str | None = Field(..., description="The email body")
    include_header: bool | None = None
    include_footer: bool | None = None
    custom_logo_url: str | None = Field(None, description="URL to your custom email logo")

class SendMicrosoftTeamsBlocksTaskParams(PermissiveModel):
    task_type: Literal["send_microsoft_teams_blocks"] | None = None
    attachments: str = Field(..., description="Support liquid markup. Needs to be a valid JSON string after liquid is parsed")

class SendMicrosoftTeamsMessageTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendMicrosoftTeamsMessageTaskParams(PermissiveModel):
    task_type: Literal["send_microsoft_teams_message"] | None = None
    channels: list[SendMicrosoftTeamsMessageTaskParamsChannelsItem] | None = None
    text: str = Field(..., description="The message text")

class SendSlackBlocksTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackBlocksTaskParamsParentMessageThreadTask(PermissiveModel):
    """A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackBlocksTaskParamsSlackUserGroupsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackBlocksTaskParamsSlackUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackBlocksTaskParams(PermissiveModel):
    task_type: Literal["send_slack_blocks"] | None = None
    message: str | None = None
    blocks: str = Field(..., description="Support liquid markup. Needs to be a valid JSON string after liquid is parsed")
    attachments: str | None = Field(None, description="Support liquid markup. Needs to be a valid JSON string after liquid is parsed")
    channels: list[SendSlackBlocksTaskParamsChannelsItem] | None = None
    slack_users: list[SendSlackBlocksTaskParamsSlackUsersItem] | None = None
    slack_user_groups: list[SendSlackBlocksTaskParamsSlackUserGroupsItem] | None = None
    broadcast_thread_reply_to_channel: bool | None = None
    send_as_ephemeral: bool | None = None
    pin_to_channel: bool | None = None
    thread_ts: str | None = Field(None, description="The thread to send the message into")
    update_parent_message: bool | None = None
    parent_message_thread_task: SendSlackBlocksTaskParamsParentMessageThreadTask | None = Field(None, description="A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task")
    send_only_as_threaded_message: bool | None = Field(None, description="When set to true, if the parent for this threaded message cannot be found the message will be skipped.")

class SendSlackMessageTaskParamsChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackMessageTaskParamsParentMessageThreadTask(PermissiveModel):
    """A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackMessageTaskParamsSlackUserGroupsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackMessageTaskParamsSlackUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SendSlackMessageTaskParams(PermissiveModel):
    task_type: Literal["send_slack_message"] | None = None
    channels: list[SendSlackMessageTaskParamsChannelsItem] | None = None
    slack_users: list[SendSlackMessageTaskParamsSlackUsersItem] | None = None
    slack_user_groups: list[SendSlackMessageTaskParamsSlackUserGroupsItem] | None = None
    actionables: list[Literal["update_summary", "update_status", "archive_channel", "manage_incident_roles", "update_incident", "all_commands", "leave_feedback", "manage_form_fields", "manage_action_items", "view_tasks", "add_pagerduty_responders", "add_opsgenie_responders", "add_victor_ops_responders", "update_status_page", "pause_reminder", "snooze_reminder", "restart_reminder", "cancel_incident", "delete_message"]] | None = None
    broadcast_thread_reply_to_channel: bool | None = None
    send_as_ephemeral: bool | None = None
    color: str | None = Field(None, description="A hex color ex. #FFFFFF")
    pin_to_channel: bool | None = None
    update_parent_message: bool | None = None
    thread_ts: str | None = Field(None, description="The thread to send the message into")
    parent_message_thread_task: SendSlackMessageTaskParamsParentMessageThreadTask | None = Field(None, description="A hash where [id] is the task id of the parent task that sent a message, and [name] is the name of the parent task")
    text: str = Field(..., description="The message text")
    send_only_as_threaded_message: bool | None = Field(None, description="When set to true, if the parent for this threaded message cannot be found the message will be skipped.")

class SendSmsTaskParams(PermissiveModel):
    task_type: Literal["send_sms"] | None = None
    phone_numbers: list[str]
    name: str = Field(..., description="The name")
    content: str = Field(..., description="The SMS message")

class SendWhatsappMessageTaskParams(PermissiveModel):
    task_type: Literal["send_whatsapp_message"] | None = None
    phone_numbers: list[str]
    name: str = Field(..., description="The name")
    content: str = Field(..., description="The WhatsApp message")

class ServiceSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class ServiceSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class Service(PermissiveModel):
    name: str = Field(..., description="The name of the service")
    slug: str | None = Field(None, description="The slug of the service")
    description: str | None = Field(None, description="The description of the service")
    public_description: str | None = Field(None, description="The public description of the service")
    notify_emails: list[str] | None = Field(None, description="Emails attached to the service")
    color: str | None = Field(None, description="The hex color of the service")
    position: int | None = Field(None, description="Position of the service")
    backstage_id: str | None = Field(None, description="The Backstage entity id associated to this service. eg: :namespace/:kind/:entity_name")
    external_id: str | None = Field(None, description="The external id associated to this service")
    pagerduty_id: str | None = Field(None, description="The PagerDuty service id associated to this service")
    opsgenie_id: str | None = Field(None, description="The Opsgenie service id associated to this service")
    cortex_id: str | None = Field(None, description="The Cortex group id associated to this service")
    service_now_ci_sys_id: str | None = Field(None, description="The Service Now CI sys id associated to this service")
    github_repository_name: str | None = Field(None, description="The GitHub repository name associated to this service. eg: rootlyhq/my-service")
    github_repository_branch: str | None = Field(None, description="The GitHub repository branch associated to this service. eg: main")
    gitlab_repository_name: str | None = Field(None, description="The GitLab repository name associated to this service. eg: rootlyhq/my-service")
    gitlab_repository_branch: str | None = Field(None, description="The GitLab repository branch associated to this service. eg: main")
    environment_ids: list[str] | None = Field(None, description="Environments associated with this service")
    service_ids: list[str] | None = Field(None, description="Services dependent on this service")
    owner_group_ids: list[str] | None = Field(None, description="Owner Teams associated with this service")
    owner_user_ids: list[int] | None = Field(None, description="Owner Users associated with this service")
    alert_urgency_id: str | None = Field(None, description="The alert urgency id of the service")
    alerts_email_enabled: bool | None = Field(None, description="Enable alerts through email")
    alerts_email_address: str | None = Field(None, description="Email generated to send alerts to")
    slack_channels: list[ServiceSlackChannelsItem] | None = Field(None, description="Slack Channels associated with this service")
    slack_aliases: list[ServiceSlackAliasesItem] | None = Field(None, description="Slack Aliases associated with this service")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class CreateAlertGroupBodyDataAttributesTargetsItem(PermissiveModel):
    target_type: Literal["Group", "Service", "EscalationPolicy"] = Field(..., description="The type of the target.")
    target_id: str = Field(..., description="id for the Group, Service or EscalationPolicy", json_schema_extra={'format': 'uuid'})

class ServiceResponseData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of the service")
    type_: Literal["services"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: Service

class ServiceResponse(PermissiveModel):
    data: ServiceResponseData

class SeveritySlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class SeveritySlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class Severity(PermissiveModel):
    name: str = Field(..., description="The name of the severity")
    slug: str | None = Field(None, description="The slug of the severity")
    description: str | None = Field(None, description="The description of the severity")
    severity: Literal["critical", "high", "medium", "low"] | None = Field(None, description="The severity of the severity")
    color: str | None = Field(None, description="The hex color of the severity")
    position: int | None = Field(None, description="Position of the severity")
    notify_emails: list[str] | None = Field(None, description="Emails to attach to the severity")
    slack_channels: list[SeveritySlackChannelsItem] | None = Field(None, description="Slack Channels associated with this severity")
    slack_aliases: list[SeveritySlackAliasesItem] | None = Field(None, description="Slack Aliases associated with this severity")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class SeverityResponseData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of the severity")
    type_: Literal["severities"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: Severity

class SeverityResponse(PermissiveModel):
    data: SeverityResponseData

class SnapshotDatadogGraphTaskParamsDashboardsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotDatadogGraphTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotDatadogGraphTaskParams(PermissiveModel):
    task_type: Literal["snapshot_datadog_graph"] | None = None
    dashboards: list[SnapshotDatadogGraphTaskParamsDashboardsItem] | None = None
    past_duration: str = Field(..., description="in format '1 minute', '30 days', '3 months', etc")
    metric_queries: list[str] | None = None
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[SnapshotDatadogGraphTaskParamsPostToSlackChannelsItem] | None = None

class SnapshotGrafanaDashboardTaskParamsDashboardsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotGrafanaDashboardTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotGrafanaDashboardTaskParams(PermissiveModel):
    task_type: Literal["snapshot_grafana_dashboard"] | None = None
    dashboards: list[SnapshotGrafanaDashboardTaskParamsDashboardsItem]
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[SnapshotGrafanaDashboardTaskParamsPostToSlackChannelsItem] | None = None

class SnapshotLookerLookTaskParamsDashboardsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotLookerLookTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotLookerLookTaskParams(PermissiveModel):
    task_type: Literal["snapshot_looker_look"] | None = None
    dashboards: list[SnapshotLookerLookTaskParamsDashboardsItem]
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[SnapshotLookerLookTaskParamsPostToSlackChannelsItem] | None = None

class SnapshotNewRelicGraphTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class SnapshotNewRelicGraphTaskParams(PermissiveModel):
    task_type: Literal["snapshot_looker_graph"] | None = None
    metric_query: str
    metric_type: Literal["APDEX", "AREA", "BAR", "BASELINE", "BILLBOARD", "BULLET", "EVENT_FEED", "FUNNEL", "HEATMAP", "HISTOGRAM", "LINE", "PIE", "SCATTER", "STACKED_HORIZONTAL_BAR", "TABLE", "VERTICAL_BAR"]
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[SnapshotNewRelicGraphTaskParamsPostToSlackChannelsItem] | None = None

class TeamSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class TeamSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class Team(PermissiveModel):
    name: str = Field(..., description="The name of the team")
    slug: str | None = None
    description: str | None = Field(None, description="The description of the team")
    notify_emails: list[str] | None = Field(None, description="Emails to attach to the team")
    color: str | None = Field(None, description="The hex color of the team")
    position: int | None = Field(None, description="Position of the team")
    backstage_id: str | None = Field(None, description="The Backstage entity id associated to this team. eg: :namespace/:kind/:entity_name")
    external_id: str | None = Field(None, description="The external id associated to this team")
    pagerduty_id: str | None = Field(None, description="The PagerDuty group id associated to this team")
    pagerduty_service_id: str | None = Field(None, description="The PagerDuty service id associated to this team")
    opsgenie_id: str | None = Field(None, description="The Opsgenie group id associated to this team")
    victor_ops_id: str | None = Field(None, description="The VictorOps group id associated to this team")
    pagertree_id: str | None = Field(None, description="The PagerTree group id associated to this team")
    cortex_id: str | None = Field(None, description="The Cortex group id associated to this team")
    service_now_ci_sys_id: str | None = Field(None, description="The Service Now CI sys id associated to this team")
    user_ids: list[int] | None = Field(None, description="The user ids of the members of this team.")
    admin_ids: list[int] | None = Field(None, description="The user ids of the admins of this team. These users must also be present in user_ids attribute.")
    alerts_email_enabled: bool | None = Field(None, description="Enable alerts through email")
    alerts_email_address: str | None = Field(None, description="Email generated to send alerts to")
    alert_urgency_id: str | None = Field(None, description="The alert urgency id of the team")
    slack_channels: list[TeamSlackChannelsItem] | None = Field(None, description="Slack Channels associated with this team")
    slack_aliases: list[TeamSlackAliasesItem] | None = Field(None, description="Slack Aliases associated with this team")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class Alert(PermissiveModel):
    noise: Literal["noise", "not_noise"] | None = Field(None, description="Whether the alert is marked as noise")
    source: Literal["rootly", "manual", "api", "web", "slack", "email", "workflow", "live_call_routing", "pagerduty", "opsgenie", "victorops", "pagertree", "datadog", "nobl9", "zendesk", "asana", "clickup", "sentry", "rollbar", "jira", "honeycomb", "service_now", "linear", "grafana", "alertmanager", "google_cloud", "generic_webhook", "cloud_watch", "azure", "splunk", "chronosphere", "app_optics", "bug_snag", "monte_carlo", "nagios", "prtg", "catchpoint", "app_dynamics", "checkly", "new_relic", "gitlab"] = Field(..., description="The source of the alert")
    status: Literal["open", "triggered", "acknowledged", "resolved"] | None = Field(None, description="The status of the alert")
    summary: str = Field(..., description="The summary of the alert")
    description: str | None = Field(None, description="The description of the alert")
    services: list[Service] | None = Field(None, description="Services attached to the alert")
    groups: list[Team] | None = Field(None, description="Groups attached to the alert")
    environments: list[Environment] | None = Field(None, description="Environments attached to the alert")
    service_ids: list[str] | None = Field(None, description="The Service ID's to attach to the alert. If your organization has On-Call enabled and your notification target is a Service. This field will be automatically set for you.")
    group_ids: list[str] | None = Field(None, description="The Group ID's to attach to the alert. If your organization has On-Call enabled and your notification target is a Group. This field will be automatically set for you.")
    environment_ids: list[str] | None = Field(None, description="The Environment ID's to attach to the alert")
    external_id: str | None = Field(None, description="External ID")
    external_url: str | None = Field(None, description="External Url")
    alert_urgency_id: str | None = Field(None, description="The ID of the alert urgency")
    labels: list[AlertLabelsItem] | None = None
    data: dict[str, Any] | None = Field(None, description="Additional data")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class TeamResponseData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique ID of the team")
    type_: Literal["groups"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: Team

class TeamResponse(PermissiveModel):
    data: TeamResponseData

class Incident(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique ID of the incident")
    sequential_id: int | None = Field(None, description="Sequential ID of the incident")
    title: str = Field(..., description="The title of the incident")
    kind: str | None = Field(None, description="The kind of the incident")
    slug: str = Field(..., description="The slug of the incident")
    parent_incident_id: str | None = Field(None, description="ID of parent incident")
    duplicate_incident_id: str | None = Field(None, description="ID of duplicated incident")
    summary: str | None = Field(None, description="The summary of the incident")
    private: bool | None = Field(False, description="Create an incident as private")
    source: str | None = Field(None, description="The source of the incident")
    status: str | None = Field(None, description="The status of the incident")
    url: str | None = Field(None, description="The url to the incident")
    short_url: str | None = Field(None, description="The short url to the incident")
    public_title: str | None = Field(None, description="The public title of the incident")
    user: dict[str, Any] | None = Field(None, description="The user who created the incident")
    severity: SeverityResponse | None = Field(None, description="The Severity of the incident")
    environments: list[EnvironmentResponse] | None = Field(None, description="The Environments of the incident")
    incident_types: list[IncidentTypeResponse] | None = Field(None, description="The Incident Types of the incident")
    services: list[ServiceResponse] | None = Field(None, description="The Services of the incident")
    functionalities: list[FunctionalityResponse] | None = Field(None, description="The Functionalities of the incident")
    groups: list[TeamResponse] | None = Field(None, description="The Teams of to the incident")
    labels: dict[str, Any] | None = Field(None, description="Labels to attach to the incidents. eg: {\"platform\":\"osx\", \"version\": \"1.29\"}")
    slack_channel_id: str | None = Field(None, description="Slack channel id")
    slack_channel_name: str | None = Field(None, description="Slack channel name")
    slack_channel_url: str | None = Field(None, description="Slack channel url")
    slack_channel_short_url: str | None = Field(None, description="Slack channel short url")
    slack_channel_deep_link: str | None = Field(None, description="Slack channel deep link")
    slack_channel_archived: bool | None = Field(None, description="Whether the Slack channel is archived")
    slack_last_message_ts: str | None = Field(None, description="Timestamp of last Slack message")
    zoom_meeting_id: str | None = Field(None, description="Zoom meeting ID")
    zoom_meeting_start_url: str | None = Field(None, description="Zoom meeting start URL")
    zoom_meeting_join_url: str | None = Field(None, description="Zoom meeting join URL")
    zoom_meeting_password: str | None = Field(None, description="Zoom meeting password")
    zoom_meeting_pstn_password: str | None = Field(None, description="Zoom meeting PSTN password")
    zoom_meeting_h323_password: str | None = Field(None, description="Zoom meeting H323 password")
    zoom_meeting_global_dial_in_numbers: list[str] | None = Field(None, description="Zoom meeting global dial-in numbers")
    google_drive_id: str | None = Field(None, description="Google Drive document ID")
    google_drive_parent_id: str | None = Field(None, description="Google Drive parent folder ID")
    google_drive_url: str | None = Field(None, description="Google Drive URL")
    google_meeting_id: str | None = Field(None, description="Google meeting ID")
    google_meeting_url: str | None = Field(None, description="Google meeting URL")
    jira_issue_key: str | None = Field(None, description="Jira issue key")
    jira_issue_id: str | None = Field(None, description="Jira issue ID")
    jira_issue_url: str | None = Field(None, description="Jira issue URL")
    github_issue_id: str | None = Field(None, description="GitHub issue ID")
    github_issue_url: str | None = Field(None, description="GitHub issue URL")
    gitlab_issue_id: str | None = Field(None, description="GitLab issue ID")
    gitlab_issue_url: str | None = Field(None, description="GitLab issue URL")
    asana_task_id: str | None = Field(None, description="Asana task ID")
    asana_task_url: str | None = Field(None, description="Asana task URL")
    linear_issue_id: str | None = Field(None, description="Linear issue ID")
    linear_issue_url: str | None = Field(None, description="Linear issue URL")
    trello_card_id: str | None = Field(None, description="Trello card ID")
    trello_card_url: str | None = Field(None, description="Trello card URL")
    zendesk_ticket_id: str | None = Field(None, description="Zendesk ticket ID")
    zendesk_ticket_url: str | None = Field(None, description="Zendesk ticket URL")
    pagerduty_incident_id: str | None = Field(None, description="PagerDuty incident ID")
    pagerduty_incident_number: str | None = Field(None, description="PagerDuty incident number")
    pagerduty_incident_url: str | None = Field(None, description="PagerDuty incident URL")
    opsgenie_incident_id: str | None = Field(None, description="Opsgenie incident ID")
    opsgenie_incident_url: str | None = Field(None, description="Opsgenie incident URL")
    opsgenie_alert_id: str | None = Field(None, description="Opsgenie alert ID")
    opsgenie_alert_url: str | None = Field(None, description="Opsgenie alert URL")
    service_now_incident_id: str | None = Field(None, description="ServiceNow incident ID")
    service_now_incident_key: str | None = Field(None, description="ServiceNow incident key")
    service_now_incident_url: str | None = Field(None, description="ServiceNow incident URL")
    mattermost_channel_id: str | None = Field(None, description="Mattermost channel ID")
    mattermost_channel_name: str | None = Field(None, description="Mattermost channel name")
    mattermost_channel_url: str | None = Field(None, description="Mattermost channel URL")
    confluence_page_id: str | None = Field(None, description="Confluence page ID")
    confluence_page_url: str | None = Field(None, description="Confluence page URL")
    datadog_notebook_id: str | None = Field(None, description="Datadog notebook ID")
    datadog_notebook_url: str | None = Field(None, description="Datadog notebook URL")
    shortcut_story_id: str | None = Field(None, description="Shortcut story ID")
    shortcut_story_url: str | None = Field(None, description="Shortcut story URL")
    shortcut_task_id: str | None = Field(None, description="Shortcut task ID")
    shortcut_task_url: str | None = Field(None, description="Shortcut task URL")
    motion_task_id: str | None = Field(None, description="Motion task ID")
    motion_task_url: str | None = Field(None, description="Motion task URL")
    clickup_task_id: str | None = Field(None, description="ClickUp task ID")
    clickup_task_url: str | None = Field(None, description="ClickUp task URL")
    victor_ops_incident_id: str | None = Field(None, description="VictorOps incident ID")
    victor_ops_incident_url: str | None = Field(None, description="VictorOps incident URL")
    quip_page_id: str | None = Field(None, description="Quip page ID")
    quip_page_url: str | None = Field(None, description="Quip page URL")
    sharepoint_page_id: str | None = Field(None, description="SharePoint page ID")
    sharepoint_page_url: str | None = Field(None, description="SharePoint page URL")
    airtable_base_key: str | None = Field(None, description="Airtable base key")
    airtable_table_name: str | None = Field(None, description="Airtable table name")
    airtable_record_id: str | None = Field(None, description="Airtable record ID")
    airtable_record_url: str | None = Field(None, description="Airtable record URL")
    freshservice_ticket_id: str | None = Field(None, description="Freshservice ticket ID")
    freshservice_ticket_url: str | None = Field(None, description="Freshservice ticket URL")
    freshservice_task_id: str | None = Field(None, description="Freshservice task ID")
    freshservice_task_url: str | None = Field(None, description="Freshservice task URL")
    mitigation_message: str | None = Field(None, description="How was the incident mitigated?")
    resolution_message: str | None = Field(None, description="How was the incident resolved?")
    cancellation_message: str | None = Field(None, description="Why was the incident cancelled?")
    scheduled_for: str | None = Field(None, description="Date of when the maintenance begins")
    scheduled_until: str | None = Field(None, description="Date of when the maintenance ends")
    retrospective_progress_status: Literal["not_started", "active", "completed", "skipped"] | None = Field(None, description="The status of the retrospective progress")
    in_triage_by: dict[str, Any] | None = Field(None, description="The user who triaged the incident")
    started_by: dict[str, Any] | None = Field(None, description="The user who started the incident")
    mitigated_by: dict[str, Any] | None = Field(None, description="The user who mitigated the incident")
    resolved_by: dict[str, Any] | None = Field(None, description="The user who resolved the incident")
    closed_by: dict[str, Any] | None = Field(None, description="The user who closed the incident")
    cancelled_by: dict[str, Any] | None = Field(None, description="The user who cancelled the incident")
    in_triage_at: str | None = Field(None, description="Date of triage")
    started_at: str | None = Field(None, description="Date of start")
    detected_at: str | None = Field(None, description="Date of detection")
    acknowledged_at: str | None = Field(None, description="Date of acknowledgment")
    mitigated_at: str | None = Field(None, description="Date of mitigation")
    resolved_at: str | None = Field(None, description="Date of resolution")
    closed_at: str | None = Field(None, description="Date of closure")
    cancelled_at: str | None = Field(None, description="Date of cancellation")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")

class TriggerWorkflowTaskParamsResource(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class TriggerWorkflowTaskParamsWorkflow(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class TriggerWorkflowTaskParams(PermissiveModel):
    task_type: Literal["trigger_workflow"] | None = None
    kind: Literal["incident", "post_mortem", "action_item", "pulse", "alert"]
    attribute_to_query_by: Literal["id", "slug", "sequential_id", "pagerduty_incident_id", "opsgenie_incident_id", "victor_ops_incident_id", "jira_issue_id", "asana_task_id", "shortcut_task_id", "linear_issue_id", "zendesk_ticket_id", "motion_task_id", "trello_card_id", "airtable_record_id", "shortcut_story_id", "github_issue_id", "freshservice_ticket_id", "freshservice_task_id", "clickup_task_id"] = Field(..., description="[\"(incident) kind can only match [:id, :slug, :sequential_id, :pagerduty_incident_id, :opsgenie_incident_id, :victor_ops_incident_id, :jira_issue_id, :asana_task_id, :shortcut_task_id, :linear_issue_id, :zendesk_ticket_id, :motion_task_id, :trello_card_id, :airtable_record_id, :shortcut_story_id, :github_issue_id, :freshservice_ticket_id, :freshservice_task_id, :clickup_task_id]\", \"(post_mortem) kind can only match [:id]\", \"(action_item) kind can only match [:id, :jira_issue_id, :asana_task_id, :shortcut_task_id, :linear_issue_id, :zendesk_ticket_id, :motion_task_id, :trello_card_id, :airtable_record_id, :shortcut_story_id, :github_issue_id, :freshservice_ticket_id, :freshservice_task_id, :clickup_task_id]\", \"(pulse) kind can only match [:id]\", \"(alert) kind can only match [:id]\"]")
    resource: TriggerWorkflowTaskParamsResource
    workflow: TriggerWorkflowTaskParamsWorkflow
    check_workflow_conditions: bool | None = None

class TweetTwitterMessageTaskParams(PermissiveModel):
    task_type: Literal["tweet_twitter_message"] | None = None
    message: str

class UpdateActionItemTaskParamsAssignedToUser(PermissiveModel):
    """ The user this action item is assigned to"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateActionItemTaskParams(PermissiveModel):
    task_type: Literal["update_action_item"] | None = None
    query_value: str = Field(..., description="Value that attribute_to_query_by to uses to match against")
    attribute_to_query_by: Literal["id", "jira_issue_id", "asana_task_id", "shortcut_task_id", "linear_issue_id", "zendesk_ticket_id", "motion_task_id", "trello_card_id", "airtable_record_id", "shortcut_story_id", "github_issue_id", "gitlab_issue_id", "freshservice_ticket_id", "freshservice_task_id", "clickup_task_id"] = Field(..., description="Attribute of the action item to match against")
    summary: str | None = Field(None, description="Brief description of the action item")
    assigned_to_user_id: str | None = Field(None, description="[DEPRECATED] Use assigned_to_user attribute instead. The user id this action item is assigned to")
    assigned_to_user: UpdateActionItemTaskParamsAssignedToUser | None = Field(None, description=" The user this action item is assigned to")
    group_ids: list[str] | None = None
    description: str | None = Field(None, description="The action item description")
    priority: Literal["high", "medium", "low"] | None = Field(None, description="The action item priority")
    status: Literal["open", "in_progress", "cancelled", "done"] | None = Field(None, description="The action item status")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    post_to_incident_timeline: bool | None = None

class UpdateAirtableTableRecordTaskParams(PermissiveModel):
    task_type: Literal["update_airtable_table_record"] | None = None
    base_key: str = Field(..., description="The base key")
    table_name: str = Field(..., description="The table name")
    record_id: str = Field(..., description="The record id")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")

class UpdateAlertGroupBodyDataAttributesConditionsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the alert group condition", json_schema_extra={'format': 'uuid'})
    property_field_type: Literal["attribute", "payload", "alert_field"] = Field(..., description="The type of the property field")
    property_field_name: str | None = Field(None, description="The name of the property field. If the property field type is selected as 'attribute', then the allowed property field names are 'summary' (for Title), 'description', 'alert_urgency' and 'external_url' (for Alert Source URL). If the property field type is selected as 'payload', then the property field name should be supplied in JSON Path syntax.")
    property_field_condition_type: Literal["is_one_of", "is_not_one_of", "contains", "does_not_contain", "starts_with", "ends_with", "matches_regex", "is_empty", "matches_existing_alert"] = Field(..., description="The condition type of the property field")
    property_field_value: str | None = Field(None, description="The value of the property field. Can be null if the property field condition type is 'is_one_of' or 'is_not_one_of'")
    property_field_values: list[str] | None = Field(None, description="The values of the property field. Need to be passed if the property field condition type is 'is_one_of' or 'is_not_one_of' except for when property field name is 'alert_urgency'")
    alert_urgency_ids: list[str] | None = Field(None, description="The Alert Urgency ID's to check in the condition. Only need to be set when the property field type is 'attribute', the property field name is 'alert_urgency' and the property field condition type is 'is_one_of' or 'is_not_one_of'")
    conditionable_type: Literal["AlertField"] | None = Field(None, description="The type of the conditionable")
    conditionable_id: str | None = Field(None, description="The ID of the conditionable. If conditionable_type is AlertField, this is the ID of the alert field.")

class UpdateAlertGroupBodyDataAttributesTargetsItem(PermissiveModel):
    target_type: Literal["Group", "Service", "EscalationPolicy"] = Field(..., description="The type of the target.")
    target_id: str = Field(..., description="id for the Group, Service or EscalationPolicy", json_schema_extra={'format': 'uuid'})

class UpdateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem(PermissiveModel):
    alert_field_id: str | None = Field(None, description="The ID of the alert field")
    template_body: str | None = Field(None, description="Liquid expression to extract a specific value from the alert's payload for evaluation")

class UpdateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem(PermissiveModel):
    json_path: str | None = Field(None, description="JSON path expression to extract a specific value from the alert's payload for evaluation")
    operator: Literal["is", "is_not", "contains", "does_not_contain"] | None = Field(None, description="Comparison operator used to evaluate the extracted value against the specified condition")
    value: str | None = Field(None, description="Value that the extracted payload data is compared to using the specified operator to determine a match")
    conditionable_type: Literal["AlertField"] | None = Field(None, description="The type of the conditionable")
    conditionable_id: str | None = Field(None, description="The ID of the conditionable. If conditionable_type is AlertField, this is the ID of the alert field.")
    kind: Literal["payload", "alert_field"] | None = Field(None, description="The kind of the conditionable")
    alert_urgency_id: str | None = Field(None, description="The ID of the alert urgency")

class UpdateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem(PermissiveModel):
    field: str | None = Field(None, description="JSON path expression to extract a specific value from the alert's payload for evaluation")
    operator: Literal["is", "is_not", "contains", "does_not_contain", "starts_with", "ends_with"] | None = Field(None, description="Comparison operator used to evaluate the extracted value against the specified condition")
    value: str | None = Field(None, description="Value that the extracted payload data is compared to using the specified operator to determine a match")
    conditionable_type: Literal["AlertField"] | None = Field(None, description="The type of the conditionable")
    conditionable_id: str | None = Field(None, description="The ID of the conditionable. If conditionable_type is AlertField, this is the ID of the alert field.")
    kind: Literal["payload", "alert_field"] | None = Field(None, description="The kind of the conditionable")

class UpdateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem(PermissiveModel):
    field: Literal["external_id", "state", "alert_title", "alert_external_url", "notification_target_type", "notification_target_id"] | None = Field(None, description="Select the field on which the condition to be evaluated")
    json_path: str | None = Field(None, description="JSON path expression to extract a specific value from the alert's payload for evaluation")

class UpdateAsanaTaskTaskParamsCompletion(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateAsanaTaskTaskParams(PermissiveModel):
    task_type: Literal["update_asana_task"] | None = None
    task_id: str = Field(..., description="The task id")
    title: str | None = Field(None, description="The task title")
    notes: str | None = None
    assign_user_email: str | None = Field(None, description="The assigned user's email")
    completion: UpdateAsanaTaskTaskParamsCompletion
    due_date: str | None = Field(None, description="The due date")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    dependency_direction: Literal["blocking", "blocked_by"] | None = 'blocking'
    dependent_task_ids: list[str] | None = Field(None, description="Dependent task ids. Supports liquid syntax")

class UpdateAttachedAlertsTaskParams(PermissiveModel):
    task_type: Literal["update_attached_alerts"] | None = None
    status: Literal["acknowledged", "resolved"]

class UpdateClickupTaskTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateClickupTaskTaskParams(PermissiveModel):
    task_type: Literal["update_clickup_task"] | None = None
    task_id: str = Field(..., description="The task id")
    title: str | None = Field(None, description="The task title")
    description: str | None = Field(None, description="The task description")
    tags: str | None = Field(None, description="The task tags")
    priority: UpdateClickupTaskTaskParamsPriority | None = Field(None, description="The priority id and display name")
    due_date: str | None = Field(None, description="The due date")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    task_payload: str | None = Field(None, description="Additional ClickUp task attributes. Will be merged into whatever was specified in this tasks current parameters. Can contain liquid markup and need to be valid JSON")

class UpdateCodaPageTaskParamsTemplate(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Combined doc_id/page_id in format 'doc_id/page_id'")
    name: str | None = None

class UpdateCodaPageTaskParams(PermissiveModel):
    task_type: Literal["update_coda_page"] | None = None
    doc_id: str | None = Field(None, description="The Coda doc id")
    page_id: str = Field(..., description="The Coda page id")
    title: str | None = Field(None, description="The Coda page title")
    subtitle: str | None = Field(None, description="The Coda page subtitle")
    content: str | None = Field(None, description="The Coda page content")
    template: UpdateCodaPageTaskParamsTemplate | None = None

class UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemAggregate(PermissiveModel):
    operation: Literal["count", "sum", "average"] | None = None
    key: str | None = None
    cumulative: bool | None = None

class UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItemRulesItem(PermissiveModel):
    operation: Literal["and", "or"] | None = None
    condition: Literal["=", "!=", ">=", "<=", "exists", "not_exists", "contains", "not_contains"] | None = None
    key: str | None = None
    value: str | None = None

class UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItem(PermissiveModel):
    operation: Literal["and", "or"] | None = None
    rules: list[UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItemRulesItem] | None = None

class UpdateDashboardPanelBodyDataAttributesParamsDatasetsItem(PermissiveModel):
    name: str | None = None
    collection: Literal["alerts", "incidents", "incident_post_mortems", "incident_action_items", "users"] | None = None
    filter_: list[UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItem] | None = Field(None, validation_alias="filter", serialization_alias="filter")
    group_by: str | None = None
    aggregate: UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemAggregate | None = None

class UpdateEnvironmentBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class UpdateEnvironmentBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class UpdateEscalationLevelBodyDataAttributesNotificationTargetParamsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of notification target")
    type_: Literal["team", "user", "schedule", "slack_channel", "service"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the notification target")
    team_members: Literal["all", "admins", "escalate"] | None = Field(None, description="For targets with type=team, controls whether to notify admins, all team members, or escalate to team EP.")

class UpdateEscalationPathBodyDataAttributesRulesItemV0(PermissiveModel):
    rule_type: Literal["alert_urgency"] = Field(..., description="The type of the escalation path rule")
    urgency_ids: list[Any] = Field(..., description="Alert urgency ids for which this escalation path should be used")

class UpdateEscalationPathBodyDataAttributesRulesItemV1(PermissiveModel):
    rule_type: Literal["working_hour"] = Field(..., description="The type of the escalation path rule")
    within_working_hour: bool = Field(..., description="Whether the escalation path should be used within working hours")

class UpdateEscalationPathBodyDataAttributesRulesItemV2(PermissiveModel):
    rule_type: Literal["json_path"] = Field(..., description="The type of the escalation path rule")
    json_path: str = Field(..., description="JSON path to extract value from payload")
    operator: Literal["is", "is_not", "contains", "does_not_contain"] = Field(..., description="How JSON path value should be matched")
    value: str = Field(..., description="Value with which JSON path value should be matched")

class UpdateEscalationPathBodyDataAttributesTimeRestrictionsItem(PermissiveModel):
    start_day: Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] | None = None
    start_time: str | None = Field(None, description="Formatted as HH:MM")
    end_day: Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] | None = None
    end_time: str | None = Field(None, description="Formatted as HH:MM")

class UpdateFunctionalityBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class UpdateFunctionalityBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class UpdateGithubIssueTaskParamsCompletion(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateGithubIssueTaskParams(PermissiveModel):
    task_type: Literal["update_github_issue"] | None = None
    issue_id: str = Field(..., description="The issue id")
    title: str | None = Field(None, description="The issue title")
    body: str | None = Field(None, description="The issue body")
    completion: UpdateGithubIssueTaskParamsCompletion

class UpdateGitlabIssueTaskParamsCompletion(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateGitlabIssueTaskParams(PermissiveModel):
    task_type: Literal["update_gitlab_issue"] | None = None
    issue_id: str = Field(..., description="The issue id")
    issue_type: Literal["issue", "incident", "test_case", "task"] | None = Field(None, description="The issue type")
    title: str | None = Field(None, description="The issue title")
    description: str | None = Field(None, description="The issue description")
    labels: str | None = Field(None, description="The issue labels")
    due_date: str | None = Field(None, description="The due date")
    completion: UpdateGitlabIssueTaskParamsCompletion

class UpdateGoogleCalendarEventTaskParamsPostToSlackChannelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateGoogleCalendarEventTaskParams(PermissiveModel):
    task_type: Literal["create_google_calendar_event"] | None = None
    calendar_id: str | None = 'primary'
    event_id: str = Field(..., description="The event ID")
    summary: str | None = Field(None, description="The event summary")
    description: str | None = Field(None, description="The event description")
    adjustment_days: int | None = Field(None, description="Days to adjust meeting by", ge=0, le=31)
    time_of_meeting: str | None = Field(None, description="Time of meeting in format HH:MM")
    meeting_duration: str | None = Field(None, description="Meeting duration in format like '1 hour', '30 minutes'")
    send_updates: bool | None = Field(None, description="Send an email to the attendees notifying them of the event")
    can_guests_modify_event: bool | None = None
    can_guests_see_other_guests: bool | None = None
    can_guests_invite_others: bool | None = None
    attendees: list[str] | None = Field(None, description="Emails of attendees")
    replace_attendees: bool | None = None
    conference_solution_key: Literal["eventHangout", "eventNamedHangout", "hangoutsMeet", "addOn"] | None = Field(None, description="Sets the video conference type attached to the meeting")
    post_to_incident_timeline: bool | None = None
    post_to_slack_channels: list[UpdateGoogleCalendarEventTaskParamsPostToSlackChannelsItem] | None = None

class UpdateGoogleDocsPageTaskParams(PermissiveModel):
    task_type: Literal["update_google_docs_page"] | None = None
    file_id: str = Field(..., description="The Google Doc file ID")
    title: str | None = Field(None, description="The Google Doc title")
    content: str | None = Field(None, description="The Google Doc content")
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when updating page, if desired")
    template_id: str | None = Field(None, description="The Google Doc file ID to use as a template.")

class UpdateIncidentPostmortemTaskParams(PermissiveModel):
    task_type: Literal["update_incident_postmortem"] | None = None
    postmortem_id: str = Field(..., description="UUID of the retrospective that needs to be updated")
    title: str | None = Field(None, description="The incident title")
    status: str | None = None

class UpdateIncidentStatusTimestampTaskParams(PermissiveModel):
    task_type: Literal["update_status"] | None = None
    sub_status_id: str = Field(..., description="Sub-status to update timestamp for")
    assigned_at: str = Field(..., description="Timestamp of when the sub-status was assigned")

class UpdateIncidentTaskParams(PermissiveModel):
    task_type: Literal["update_incident"] | None = None
    attribute_to_query_by: Literal["id", "slug", "sequential_id", "pagerduty_incident_id", "opsgenie_incident_id", "victor_ops_incident_id", "jira_issue_id", "asana_task_id", "shortcut_task_id", "linear_issue_id", "zendesk_ticket_id", "motion_task_id", "trello_card_id", "airtable_record_id", "shortcut_story_id", "github_issue_id", "gitlab_issue_id", "freshservice_ticket_id", "freshservice_task_id", "clickup_task_id"] | None = 'id'
    incident_id: str = Field(..., description="The incident id to update or id of any attribute on the incident")
    title: str | None = Field(None, description="The incident title")
    summary: str | None = Field(None, description="The incident summary")
    status: str | None = None
    severity_id: str | None = None
    incident_type_ids: list[str] | None = None
    service_ids: list[str] | None = None
    functionality_ids: list[str] | None = None
    environment_ids: list[str] | None = None
    group_ids: list[str] | None = None
    started_at: str | None = None
    detected_at: str | None = None
    acknowledged_at: str | None = None
    mitigated_at: str | None = None
    resolved_at: str | None = None
    private: bool | None = None
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")

class UpdateIncidentTypeBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class UpdateIncidentTypeBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class UpdateJiraIssueTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateJiraIssueTaskParamsStatus(PermissiveModel):
    """The status id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateJiraIssueTaskParams(PermissiveModel):
    task_type: Literal["update_jira_issue"] | None = None
    issue_id: str = Field(..., description="The issue id")
    title: str | None = Field(None, description="The issue title")
    description: str | None = Field(None, description="The issue description")
    labels: str | None = Field(None, description="The issue labels")
    assign_user_email: str | None = Field(None, description="The assigned user's email")
    reporter_user_email: str | None = Field(None, description="The reporter user's email")
    project_key: str = Field(..., description="The project key")
    due_date: str | None = Field(None, description="The due date")
    priority: UpdateJiraIssueTaskParamsPriority | None = Field(None, description="The priority id and display name")
    status: UpdateJiraIssueTaskParamsStatus | None = Field(None, description="The status id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    update_payload: str | None = Field(None, description="Update payload. Can contain liquid markup and need to be valid JSON")

class UpdateLinearIssueTaskParamsLabelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateLinearIssueTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateLinearIssueTaskParamsProject(PermissiveModel):
    """The project id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateLinearIssueTaskParamsState(PermissiveModel):
    """The state id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateLinearIssueTaskParams(PermissiveModel):
    task_type: Literal["update_linear_issue"] | None = None
    issue_id: str = Field(..., description="The issue id")
    title: str | None = Field(None, description="The issue title")
    description: str | None = Field(None, description="The issue description")
    state: UpdateLinearIssueTaskParamsState | None = Field(None, description="The state id and display name")
    project: UpdateLinearIssueTaskParamsProject | None = Field(None, description="The project id and display name")
    labels: list[UpdateLinearIssueTaskParamsLabelsItem] | None = None
    priority: UpdateLinearIssueTaskParamsPriority | None = Field(None, description="The priority id and display name")
    assign_user_email: str | None = Field(None, description="The assigned user's email")

class UpdateLiveCallRouterBodyDataAttributesPagingTargetsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of paging target")
    type_: Literal["service", "team", "escalation_policy"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the paging target")
    alert_urgency_id: str = Field(..., description="This is used in escalation paths to determine who to page")

class UpdateMotionTaskTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateMotionTaskTaskParams(PermissiveModel):
    task_type: Literal["update_motion_task"] | None = None
    task_id: str = Field(..., description="The task id")
    title: str | None = Field(None, description="The task title")
    description: str | None = Field(None, description="The task description")
    labels: list[str] | None = None
    priority: UpdateMotionTaskTaskParamsPriority | None = Field(None, description="The priority id and display name")
    duration: str | None = Field(None, description="The duration. Eg.  \"NONE\", \"REMINDER\", or a integer greater than 0.")
    due_date: str | None = Field(None, description="The due date")

class UpdateNotionPageTaskParams(PermissiveModel):
    task_type: Literal["update_notion_page"] | None = None
    file_id: str = Field(..., description="The Notion page ID")
    title: str | None = Field(None, description="The Notion page title")
    post_mortem_template_id: str | None = Field(None, description="Retrospective template to use when creating page task, if desired")
    content: str | None = Field(None, description="Custom page content with liquid templating support. When provided, only this content will be rendered (no default sections)")
    show_timeline_as_table: bool | None = None
    show_action_items_as_table: bool | None = None

class UpdateOpsgenieAlertTaskParamsCompletion(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateOpsgenieAlertTaskParams(PermissiveModel):
    alert_id: str = Field(..., description="Opsgenie Alert ID")
    task_type: Literal["update_opsgenie_alert"] | None = None
    message: str | None = Field(None, description="Message of the alert")
    description: str | None = Field(None, description="Description field of the alert that is generally used to provide a detailed information about the alert")
    priority: Literal["P1", "P2", "P3", "P4", "P5", "auto"]
    completion: UpdateOpsgenieAlertTaskParamsCompletion

class UpdateOpsgenieIncidentTaskParams(PermissiveModel):
    task_type: Literal["update_opsgenie_incident"] | None = None
    opsgenie_incident_id: str = Field(..., description="The Opsgenie incident ID, this can also be a Rootly incident variable ex. {{ incident.opsgenie_incident_id }}")
    message: str | None = Field(None, description="Message of the alert")
    description: str | None = Field(None, description="Description field of the alert that is generally used to provide a detailed information about the alert")
    status: Literal["resolve", "open", "close", "auto"] | None = None
    priority: Literal["P1", "P2", "P3", "P4", "P5", "auto"] | None = None

class UpdatePagerdutyIncidentTaskParams(PermissiveModel):
    task_type: Literal["update_pagerduty_incident"] | None = None
    pagerduty_incident_id: str = Field(..., description="Pagerduty incident id")
    title: str | None = Field(None, description="Title to update to")
    status: Literal["resolved", "acknowledged", "auto"] | None = None
    resolution: str | None = Field(None, description="A message outlining the incident's resolution in PagerDuty")
    escalation_level: int | None = Field(None, description="Escalation level of policy attached to incident", ge=1, le=20)
    urgency: Literal["high", "low", "auto"] | None = Field(None, description="PagerDuty incident urgency, selecting auto will let Rootly auto map our incident severity")
    priority: str | None = Field(None, description="PagerDuty incident priority, selecting auto will let Rootly auto map our incident severity")

class UpdatePagertreeAlertTaskParamsTeamsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdatePagertreeAlertTaskParamsUsersItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdatePagertreeAlertTaskParams(PermissiveModel):
    task_type: Literal["update_pagertree_alert"] | None = None
    pagertree_alert_id: str | None = Field(None, description="The prefix ID of the Pagertree alert")
    title: str | None = Field(None, description="Title of alert as text")
    description: str | None = Field(None, description="Description of alert as text")
    urgency: Literal["auto", "critical", "high", "medium", "low"] | None = None
    severity: Literal["auto", "SEV-1", "SEV-2", "SEV-3", "SEV-4"] | None = None
    teams: list[UpdatePagertreeAlertTaskParamsTeamsItem] | None = None
    users: list[UpdatePagertreeAlertTaskParamsUsersItem] | None = None
    incident: bool | None = Field(None, description="Setting to true makes an alert a Pagertree incident")

class UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0(StrictModel):
    severity_ids: list[str] = Field(..., description="Severity ID's for retrospective process matching criteria")

class UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1(StrictModel):
    group_ids: list[str] = Field(..., description="Team ID's for retrospective process matching criteria")

class UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2(StrictModel):
    incident_type_ids: list[str] = Field(..., description="Incident type ID's for retrospective process matching criteria")

class UpdateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem(PermissiveModel):
    start_time: str | None = Field(None, description="Start time for schedule rotation active time", json_schema_extra={'format': 'time'})
    end_time: str | None = Field(None, description="End time for schedule rotation active time", json_schema_extra={'format': 'time'})

class UpdateScheduleRotationBodyDataAttributesActiveTimeAttributesItem(PermissiveModel):
    start_time: str = Field(..., description="Start time for schedule rotation active time", json_schema_extra={'format': 'time'})
    end_time: str = Field(..., description="End time for schedule rotation active time", json_schema_extra={'format': 'time'})

class UpdateScheduleRotationBodyDataAttributesScheduleRotationableAttributes(PermissiveModel):
    handoff_time: str = Field(..., description="Hand off time for daily rotation", json_schema_extra={'format': 'time'})
    handoff_day: Literal["F", "M", "R", "S", "T", "U", "W", "first_day_of_month", "last_day_of_month"] | None = Field(None, description="Hand off day for weekly/biweekly rotation")
    shift_length: int | None = Field(None, description="Shift length for custom rotation")
    shift_length_unit: Literal["days", "hours", "weeks"] | None = Field(None, description="Shift length unit for custom rotation")

class UpdateServiceBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class UpdateServiceBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class UpdateServiceNowIncidentTaskParamsCompletion(PermissiveModel):
    """The completion id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateServiceNowIncidentTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateServiceNowIncidentTaskParams(PermissiveModel):
    task_type: Literal["update_service_now_incident"] | None = None
    incident_id: str = Field(..., description="The incident id")
    title: str | None = Field(None, description="The incident title")
    description: str | None = Field(None, description="The incident description")
    priority: UpdateServiceNowIncidentTaskParamsPriority | None = Field(None, description="The priority id and display name")
    completion: UpdateServiceNowIncidentTaskParamsCompletion | None = Field(None, description="The completion id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")

class UpdateSeverityBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class UpdateSeverityBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class UpdateShortcutStoryTaskParamsArchivation(PermissiveModel):
    """The archivation id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateShortcutStoryTaskParams(PermissiveModel):
    task_type: Literal["update_shortcut_story"] | None = None
    story_id: str = Field(..., description="The story id")
    title: str | None = Field(None, description="The incident title")
    description: str | None = Field(None, description="The incident description")
    labels: str | None = Field(None, description="The story labels")
    due_date: str | None = Field(None, description="The due date")
    archivation: UpdateShortcutStoryTaskParamsArchivation = Field(..., description="The archivation id and display name")

class UpdateShortcutTaskTaskParamsCompletion(PermissiveModel):
    """The completion id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateShortcutTaskTaskParams(PermissiveModel):
    task_type: Literal["update_shortcut_task"] | None = None
    task_id: str = Field(..., description="The task id")
    parent_story_id: str = Field(..., description="The parent story")
    description: str | None = Field(None, description="The task description")
    completion: UpdateShortcutTaskTaskParamsCompletion = Field(..., description="The completion id and display name")

class UpdateSlackChannelTopicTaskParamsChannel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateSlackChannelTopicTaskParams(PermissiveModel):
    task_type: Literal["update_slack_channel_topic"] | None = None
    channel: UpdateSlackChannelTopicTaskParamsChannel
    topic: str

class UpdateStatusTaskParams(PermissiveModel):
    task_type: Literal["update_status"] | None = None
    status: Literal["in_triage", "started", "mitigated", "resolved", "closed", "cancelled"]
    inactivity_timeout: str | None = Field(None, description="In format '1 hour', '1 day', etc")

class UpdateTeamBodyDataAttributesSlackAliasesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack alias ID")
    name: str = Field(..., description="Slack alias name")

class UpdateTeamBodyDataAttributesSlackChannelsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Slack channel ID")
    name: str = Field(..., description="Slack channel name")

class UpdateTrelloCardTaskParamsArchivation(PermissiveModel):
    """The archivation id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateTrelloCardTaskParamsBoard(PermissiveModel):
    """The board id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateTrelloCardTaskParamsLabelsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateTrelloCardTaskParamsList(PermissiveModel):
    """The list id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateTrelloCardTaskParams(PermissiveModel):
    task_type: Literal["update_trello_card"] | None = None
    card_id: str = Field(..., description="The card id")
    title: str | None = Field(None, description="The card title")
    description: str | None = Field(None, description="The card description")
    due_date: str | None = Field(None, description="The due date")
    board: UpdateTrelloCardTaskParamsBoard | None = Field(None, description="The board id and display name")
    list_: UpdateTrelloCardTaskParamsList | None = Field(None, validation_alias="list", serialization_alias="list", description="The list id and display name")
    labels: list[UpdateTrelloCardTaskParamsLabelsItem] | None = None
    archivation: UpdateTrelloCardTaskParamsArchivation = Field(..., description="The archivation id and display name")

class UpdateVictorOpsIncidentTaskParams(PermissiveModel):
    task_type: Literal["update_victor_ops_incident"] | None = None
    victor_ops_incident_id: str = Field(..., description="The victor_ops incident ID, this can also be a Rootly incident variable ex. {{ incident.victor_ops_incident_id }}")
    status: Literal["resolve", "ack", "auto"]
    resolution_message: str | None = Field(None, description="Resolution message")

class UpdateZendeskTicketTaskParamsCompletion(PermissiveModel):
    """The completion id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateZendeskTicketTaskParamsPriority(PermissiveModel):
    """The priority id and display name"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateZendeskTicketTaskParams(PermissiveModel):
    task_type: Literal["update_zendesk_ticket"] | None = None
    ticket_id: str = Field(..., description="The ticket id")
    subject: str | None = Field(None, description="The ticket subject")
    tags: str | None = Field(None, description="The ticket tags")
    priority: UpdateZendeskTicketTaskParamsPriority | None = Field(None, description="The priority id and display name")
    completion: UpdateZendeskTicketTaskParamsCompletion | None = Field(None, description="The completion id and display name")
    custom_fields_mapping: str | None = Field(None, description="Custom field mappings. Can contain liquid markup and need to be valid JSON")
    ticket_payload: str | None = Field(None, description="Additional Zendesk ticket attributes. Will be merged into whatever was specified in this tasks current parameters. Can contain liquid markup and need to be valid JSON")

class User(PermissiveModel):
    email: str = Field(..., description="The email of the user")
    first_name: str | None = Field(None, description="First name of the user")
    last_name: str | None = Field(None, description="Last name of the user")
    full_name: str | None = Field(None, description="The full name of the user")
    full_name_with_team: str | None = Field(None, description="The full name with team of the user")
    time_zone: str | None = Field(None, description="Configured time zone")
    created_at: str = Field(..., description="Date of creation")
    updated_at: str = Field(..., description="Date of last update")


# Rebuild models to resolve forward references (required for circular refs)
AddActionItemTaskParams.model_rebuild()
AddActionItemTaskParamsAssignedToUser.model_rebuild()
AddActionItemTaskParamsPostToSlackChannelsItem.model_rebuild()
AddMicrosoftTeamsTabTaskParams.model_rebuild()
AddMicrosoftTeamsTabTaskParamsChannel.model_rebuild()
AddMicrosoftTeamsTabTaskParamsTeam.model_rebuild()
AddRoleTaskParams.model_rebuild()
AddRoleTaskParamsAssignedToUser.model_rebuild()
AddSlackBookmarkTaskParams.model_rebuild()
AddSlackBookmarkTaskParamsChannel.model_rebuild()
AddTeamTaskParams.model_rebuild()
AddToTimelineTaskParams.model_rebuild()
AddToTimelineTaskParamsPostToSlackChannelsItem.model_rebuild()
Alert.model_rebuild()
AlertField.model_rebuild()
AlertLabelsItem.model_rebuild()
ArchiveMicrosoftTeamsChannelsTaskParams.model_rebuild()
ArchiveMicrosoftTeamsChannelsTaskParamsChannelsItem.model_rebuild()
ArchiveMicrosoftTeamsChannelsTaskParamsTeam.model_rebuild()
ArchiveSlackChannelsTaskParams.model_rebuild()
ArchiveSlackChannelsTaskParamsChannelsItem.model_rebuild()
AttachDatadogDashboardsTaskParams.model_rebuild()
AttachDatadogDashboardsTaskParamsDashboardsItem.model_rebuild()
AttachDatadogDashboardsTaskParamsPostToSlackChannelsItem.model_rebuild()
AutoAssignRoleOpsgenieTaskParams.model_rebuild()
AutoAssignRoleOpsgenieTaskParamsSchedule.model_rebuild()
AutoAssignRolePagerdutyTaskParams.model_rebuild()
AutoAssignRolePagerdutyTaskParamsEscalationPolicy.model_rebuild()
AutoAssignRolePagerdutyTaskParamsSchedule.model_rebuild()
AutoAssignRolePagerdutyTaskParamsService.model_rebuild()
AutoAssignRoleRootlyTaskParams.model_rebuild()
AutoAssignRoleRootlyTaskParamsEscalationPolicyTarget.model_rebuild()
AutoAssignRoleRootlyTaskParamsGroupTarget.model_rebuild()
AutoAssignRoleRootlyTaskParamsScheduleTarget.model_rebuild()
AutoAssignRoleRootlyTaskParamsServiceTarget.model_rebuild()
AutoAssignRoleRootlyTaskParamsUserTarget.model_rebuild()
AutoAssignRoleVictorOpsTaskParams.model_rebuild()
AutoAssignRoleVictorOpsTaskParamsTeam.model_rebuild()
CallPeopleTaskParams.model_rebuild()
Catalog.model_rebuild()
ChangeSlackChannelPrivacyTaskParams.model_rebuild()
ChangeSlackChannelPrivacyTaskParamsChannel.model_rebuild()
CreateAirtableTableRecordTaskParams.model_rebuild()
CreateAirtableTableRecordTaskParamsBase.model_rebuild()
CreateAirtableTableRecordTaskParamsTable.model_rebuild()
CreateAlertGroupBodyDataAttributesConditionsItem.model_rebuild()
CreateAlertGroupBodyDataAttributesTargetsItem.model_rebuild()
CreateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem.model_rebuild()
CreateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem.model_rebuild()
CreateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem.model_rebuild()
CreateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem.model_rebuild()
CreateAsanaSubtaskTaskParams.model_rebuild()
CreateAsanaSubtaskTaskParamsCompletion.model_rebuild()
CreateAsanaTaskTaskParams.model_rebuild()
CreateAsanaTaskTaskParamsCompletion.model_rebuild()
CreateAsanaTaskTaskParamsProjectsItem.model_rebuild()
CreateAsanaTaskTaskParamsWorkspace.model_rebuild()
CreateClickupTaskTaskParams.model_rebuild()
CreateClickupTaskTaskParamsPriority.model_rebuild()
CreateCodaPageTaskParams.model_rebuild()
CreateCodaPageTaskParamsTemplate.model_rebuild()
CreateConfluencePageTaskParams.model_rebuild()
CreateConfluencePageTaskParamsAncestor.model_rebuild()
CreateConfluencePageTaskParamsIntegration.model_rebuild()
CreateConfluencePageTaskParamsSpace.model_rebuild()
CreateConfluencePageTaskParamsTemplate.model_rebuild()
CreateDashboardPanelBodyDataAttributesParamsDatasetsItem.model_rebuild()
CreateDashboardPanelBodyDataAttributesParamsDatasetsItemAggregate.model_rebuild()
CreateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItem.model_rebuild()
CreateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItemRulesItem.model_rebuild()
CreateDatadogNotebookTaskParams.model_rebuild()
CreateDatadogNotebookTaskParamsTemplate.model_rebuild()
CreateDropboxPaperPageTaskParams.model_rebuild()
CreateDropboxPaperPageTaskParamsNamespace.model_rebuild()
CreateDropboxPaperPageTaskParamsParentFolder.model_rebuild()
CreateEnvironmentBodyDataAttributesSlackAliasesItem.model_rebuild()
CreateEnvironmentBodyDataAttributesSlackChannelsItem.model_rebuild()
CreateEscalationLevelBodyDataAttributesNotificationTargetParamsItem.model_rebuild()
CreateEscalationLevelPathsBodyDataAttributesNotificationTargetParamsItem.model_rebuild()
CreateFunctionalityBodyDataAttributesSlackAliasesItem.model_rebuild()
CreateFunctionalityBodyDataAttributesSlackChannelsItem.model_rebuild()
CreateGithubIssueTaskParams.model_rebuild()
CreateGithubIssueTaskParamsRepository.model_rebuild()
CreateGitlabIssueTaskParams.model_rebuild()
CreateGitlabIssueTaskParamsRepository.model_rebuild()
CreateGoogleCalendarEventTaskParams.model_rebuild()
CreateGoogleCalendarEventTaskParamsPostToSlackChannelsItem.model_rebuild()
CreateGoogleDocsPageTaskParams.model_rebuild()
CreateGoogleDocsPageTaskParamsDrive.model_rebuild()
CreateGoogleDocsPageTaskParamsParentFolder.model_rebuild()
CreateGoogleDocsPermissionsTaskParams.model_rebuild()
CreateGoogleMeetingTaskParams.model_rebuild()
CreateGoogleMeetingTaskParamsPostToSlackChannelsItem.model_rebuild()
CreateGoToMeetingTaskParams.model_rebuild()
CreateGoToMeetingTaskParamsPostToSlackChannelsItem.model_rebuild()
CreateIncidentPostmortemTaskParams.model_rebuild()
CreateIncidentPostmortemTaskParamsTemplate.model_rebuild()
CreateIncidentTaskParams.model_rebuild()
CreateIncidentTypeBodyDataAttributesSlackAliasesItem.model_rebuild()
CreateIncidentTypeBodyDataAttributesSlackChannelsItem.model_rebuild()
CreateJiraIssueTaskParams.model_rebuild()
CreateJiraIssueTaskParamsIntegration.model_rebuild()
CreateJiraIssueTaskParamsIssueType.model_rebuild()
CreateJiraIssueTaskParamsPriority.model_rebuild()
CreateJiraIssueTaskParamsStatus.model_rebuild()
CreateJiraSubtaskTaskParams.model_rebuild()
CreateJiraSubtaskTaskParamsIntegration.model_rebuild()
CreateJiraSubtaskTaskParamsPriority.model_rebuild()
CreateJiraSubtaskTaskParamsStatus.model_rebuild()
CreateJiraSubtaskTaskParamsSubtaskIssueType.model_rebuild()
CreateLinearIssueCommentTaskParams.model_rebuild()
CreateLinearIssueTaskParams.model_rebuild()
CreateLinearIssueTaskParamsLabelsItem.model_rebuild()
CreateLinearIssueTaskParamsPriority.model_rebuild()
CreateLinearIssueTaskParamsProject.model_rebuild()
CreateLinearIssueTaskParamsState.model_rebuild()
CreateLinearIssueTaskParamsTeam.model_rebuild()
CreateLinearSubtaskIssueTaskParams.model_rebuild()
CreateLinearSubtaskIssueTaskParamsLabelsItem.model_rebuild()
CreateLinearSubtaskIssueTaskParamsPriority.model_rebuild()
CreateLinearSubtaskIssueTaskParamsState.model_rebuild()
CreateLiveCallRouterBodyDataAttributesPagingTargetsItem.model_rebuild()
CreateMicrosoftTeamsChannelTaskParams.model_rebuild()
CreateMicrosoftTeamsChannelTaskParamsTeam.model_rebuild()
CreateMicrosoftTeamsMeetingTaskParams.model_rebuild()
CreateMicrosoftTeamsMeetingTaskParamsPostToSlackChannelsItem.model_rebuild()
CreateMotionTaskTaskParams.model_rebuild()
CreateMotionTaskTaskParamsPriority.model_rebuild()
CreateMotionTaskTaskParamsProject.model_rebuild()
CreateMotionTaskTaskParamsStatus.model_rebuild()
CreateMotionTaskTaskParamsWorkspace.model_rebuild()
CreateNotionPageTaskParams.model_rebuild()
CreateNotionPageTaskParamsParentPage.model_rebuild()
CreateOpsgenieAlertTaskParams.model_rebuild()
CreateOpsgenieAlertTaskParamsEscalationsItem.model_rebuild()
CreateOpsgenieAlertTaskParamsSchedulesItem.model_rebuild()
CreateOpsgenieAlertTaskParamsTeamsItem.model_rebuild()
CreateOpsgenieAlertTaskParamsUsersItem.model_rebuild()
CreateOutlookEventTaskParams.model_rebuild()
CreateOutlookEventTaskParamsCalendar.model_rebuild()
CreateOutlookEventTaskParamsPostToSlackChannelsItem.model_rebuild()
CreatePagerdutyStatusUpdateTaskParams.model_rebuild()
CreatePagertreeAlertTaskParams.model_rebuild()
CreatePagertreeAlertTaskParamsTeamsItem.model_rebuild()
CreatePagertreeAlertTaskParamsUsersItem.model_rebuild()
CreateQuipPageTaskParams.model_rebuild()
CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0.model_rebuild()
CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1.model_rebuild()
CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2.model_rebuild()
CreateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem.model_rebuild()
CreateScheduleRotationBodyDataAttributesActiveTimeAttributesItem.model_rebuild()
CreateScheduleRotationBodyDataAttributesScheduleRotationableAttributes.model_rebuild()
CreateServiceBodyDataAttributesSlackAliasesItem.model_rebuild()
CreateServiceBodyDataAttributesSlackChannelsItem.model_rebuild()
CreateServiceNowIncidentTaskParams.model_rebuild()
CreateServiceNowIncidentTaskParamsCompletion.model_rebuild()
CreateServiceNowIncidentTaskParamsPriority.model_rebuild()
CreateSeverityBodyDataAttributesSlackAliasesItem.model_rebuild()
CreateSeverityBodyDataAttributesSlackChannelsItem.model_rebuild()
CreateSharepointPageTaskParams.model_rebuild()
CreateSharepointPageTaskParamsDrive.model_rebuild()
CreateSharepointPageTaskParamsParentFolder.model_rebuild()
CreateSharepointPageTaskParamsSite.model_rebuild()
CreateShortcutStoryTaskParams.model_rebuild()
CreateShortcutStoryTaskParamsArchivation.model_rebuild()
CreateShortcutStoryTaskParamsGroup.model_rebuild()
CreateShortcutStoryTaskParamsProject.model_rebuild()
CreateShortcutStoryTaskParamsWorkflowState.model_rebuild()
CreateShortcutTaskTaskParams.model_rebuild()
CreateShortcutTaskTaskParamsCompletion.model_rebuild()
CreateSlackChannelTaskParams.model_rebuild()
CreateSlackChannelTaskParamsWorkspace.model_rebuild()
CreateTeamBodyDataAttributesSlackAliasesItem.model_rebuild()
CreateTeamBodyDataAttributesSlackChannelsItem.model_rebuild()
CreateTrelloCardTaskParams.model_rebuild()
CreateTrelloCardTaskParamsArchivation.model_rebuild()
CreateTrelloCardTaskParamsBoard.model_rebuild()
CreateTrelloCardTaskParamsLabelsItem.model_rebuild()
CreateTrelloCardTaskParamsList.model_rebuild()
CreateWebexMeetingTaskParams.model_rebuild()
CreateWebexMeetingTaskParamsPostToSlackChannelsItem.model_rebuild()
CreateWorkflowRunBodyDataAttributesV0.model_rebuild()
CreateWorkflowRunBodyDataAttributesV1.model_rebuild()
CreateWorkflowRunBodyDataAttributesV2.model_rebuild()
CreateWorkflowRunBodyDataAttributesV3.model_rebuild()
CreateWorkflowRunBodyDataAttributesV4.model_rebuild()
CreateWorkflowRunBodyDataAttributesV5.model_rebuild()
CreateZendeskJiraLinkTaskParams.model_rebuild()
CreateZendeskTicketTaskParams.model_rebuild()
CreateZendeskTicketTaskParamsCompletion.model_rebuild()
CreateZendeskTicketTaskParamsPriority.model_rebuild()
CreateZoomMeetingTaskParams.model_rebuild()
CreateZoomMeetingTaskParamsPostToSlackChannelsItem.model_rebuild()
Environment.model_rebuild()
EnvironmentResponse.model_rebuild()
EnvironmentResponseData.model_rebuild()
EnvironmentSlackAliasesItem.model_rebuild()
EnvironmentSlackChannelsItem.model_rebuild()
EscalationPolicy.model_rebuild()
EscalationPolicyBusinessHours.model_rebuild()
Functionality.model_rebuild()
FunctionalityResponse.model_rebuild()
FunctionalityResponseData.model_rebuild()
FunctionalitySlackAliasesItem.model_rebuild()
FunctionalitySlackChannelsItem.model_rebuild()
GeniusCreateAnthropicChatCompletionTaskParams.model_rebuild()
GeniusCreateAnthropicChatCompletionTaskParamsModel.model_rebuild()
GeniusCreateGoogleGeminiChatCompletionTaskParams.model_rebuild()
GeniusCreateGoogleGeminiChatCompletionTaskParamsModel.model_rebuild()
GeniusCreateOpenaiChatCompletionTaskParams.model_rebuild()
GeniusCreateOpenaiChatCompletionTaskParamsModel.model_rebuild()
GeniusCreateWatsonxChatCompletionTaskParams.model_rebuild()
GeniusCreateWatsonxChatCompletionTaskParamsModel.model_rebuild()
GetAlertsTaskParams.model_rebuild()
GetAlertsTaskParamsParentMessageThreadTask.model_rebuild()
GetAlertsTaskParamsPostToSlackChannelsItem.model_rebuild()
GetGithubCommitsTaskParams.model_rebuild()
GetGithubCommitsTaskParamsPostToSlackChannelsItem.model_rebuild()
GetGitlabCommitsTaskParams.model_rebuild()
GetGitlabCommitsTaskParamsPostToSlackChannelsItem.model_rebuild()
GetPulsesTaskParams.model_rebuild()
GetPulsesTaskParamsParentMessageThreadTask.model_rebuild()
GetPulsesTaskParamsPostToSlackChannelsItem.model_rebuild()
HttpClientTaskParams.model_rebuild()
HttpClientTaskParamsPostToSlackChannelsItem.model_rebuild()
Incident.model_rebuild()
IncidentType.model_rebuild()
IncidentTypeResponse.model_rebuild()
IncidentTypeResponseData.model_rebuild()
IncidentTypeSlackAliasesItem.model_rebuild()
IncidentTypeSlackChannelsItem.model_rebuild()
InviteToMicrosoftTeamsChannelTaskParams.model_rebuild()
InviteToMicrosoftTeamsChannelTaskParamsChannel.model_rebuild()
InviteToMicrosoftTeamsChannelTaskParamsTeam.model_rebuild()
InviteToSlackChannelOpsgenieTaskParams.model_rebuild()
InviteToSlackChannelOpsgenieTaskParamsChannelsItem.model_rebuild()
InviteToSlackChannelOpsgenieTaskParamsSchedule.model_rebuild()
InviteToSlackChannelPagerdutyTaskParams.model_rebuild()
InviteToSlackChannelPagerdutyTaskParamsChannelsItem.model_rebuild()
InviteToSlackChannelPagerdutyTaskParamsEscalationPolicy.model_rebuild()
InviteToSlackChannelPagerdutyTaskParamsSchedule.model_rebuild()
InviteToSlackChannelPagerdutyTaskParamsService.model_rebuild()
InviteToSlackChannelRootlyTaskParams.model_rebuild()
InviteToSlackChannelRootlyTaskParamsChannelsItem.model_rebuild()
InviteToSlackChannelRootlyTaskParamsEscalationPolicyTarget.model_rebuild()
InviteToSlackChannelRootlyTaskParamsGroupTarget.model_rebuild()
InviteToSlackChannelRootlyTaskParamsScheduleTarget.model_rebuild()
InviteToSlackChannelRootlyTaskParamsServiceTarget.model_rebuild()
InviteToSlackChannelRootlyTaskParamsUserTarget.model_rebuild()
InviteToSlackChannelTaskParams.model_rebuild()
InviteToSlackChannelTaskParamsChannel.model_rebuild()
InviteToSlackChannelTaskParamsSlackUserGroupsItem.model_rebuild()
InviteToSlackChannelTaskParamsSlackUsersItem.model_rebuild()
InviteToSlackChannelVictorOpsTaskParams.model_rebuild()
InviteToSlackChannelVictorOpsTaskParamsChannelsItem.model_rebuild()
InviteToSlackChannelVictorOpsTaskParamsTeam.model_rebuild()
PageOpsgenieOnCallRespondersTaskParams.model_rebuild()
PageOpsgenieOnCallRespondersTaskParamsTeamsItem.model_rebuild()
PageOpsgenieOnCallRespondersTaskParamsUsersItem.model_rebuild()
PagePagerdutyOnCallRespondersTaskParams.model_rebuild()
PagePagerdutyOnCallRespondersTaskParamsEscalationPoliciesItem.model_rebuild()
PagePagerdutyOnCallRespondersTaskParamsService.model_rebuild()
PagePagerdutyOnCallRespondersTaskParamsUsersItem.model_rebuild()
PageRootlyOnCallRespondersTaskParams.model_rebuild()
PageRootlyOnCallRespondersTaskParamsEscalationPolicyTarget.model_rebuild()
PageRootlyOnCallRespondersTaskParamsGroupTarget.model_rebuild()
PageRootlyOnCallRespondersTaskParamsServiceTarget.model_rebuild()
PageRootlyOnCallRespondersTaskParamsUserTarget.model_rebuild()
PageVictorOpsOnCallRespondersTaskParams.model_rebuild()
PageVictorOpsOnCallRespondersTaskParamsEscalationPoliciesItem.model_rebuild()
PageVictorOpsOnCallRespondersTaskParamsUsersItem.model_rebuild()
PrintTaskParams.model_rebuild()
PublishIncidentTaskParams.model_rebuild()
PublishIncidentTaskParamsIncident.model_rebuild()
PublishIncidentTaskParamsStatusPageTemplate.model_rebuild()
RedisClientTaskParams.model_rebuild()
RedisClientTaskParamsPostToSlackChannelsItem.model_rebuild()
RemoveGoogleDocsPermissionsTaskParams.model_rebuild()
RenameMicrosoftTeamsChannelTaskParams.model_rebuild()
RenameMicrosoftTeamsChannelTaskParamsChannel.model_rebuild()
RenameMicrosoftTeamsChannelTaskParamsTeam.model_rebuild()
RenameSlackChannelTaskParams.model_rebuild()
RenameSlackChannelTaskParamsChannel.model_rebuild()
Role.model_rebuild()
RunCommandHerokuTaskParams.model_rebuild()
RunCommandHerokuTaskParamsPostToSlackChannelsItem.model_rebuild()
Schedule.model_rebuild()
ScheduleSlackUserGroup.model_rebuild()
SendDashboardReportTaskParams.model_rebuild()
SendEmailTaskParams.model_rebuild()
SendMicrosoftTeamsBlocksTaskParams.model_rebuild()
SendMicrosoftTeamsMessageTaskParams.model_rebuild()
SendMicrosoftTeamsMessageTaskParamsChannelsItem.model_rebuild()
SendSlackBlocksTaskParams.model_rebuild()
SendSlackBlocksTaskParamsChannelsItem.model_rebuild()
SendSlackBlocksTaskParamsParentMessageThreadTask.model_rebuild()
SendSlackBlocksTaskParamsSlackUserGroupsItem.model_rebuild()
SendSlackBlocksTaskParamsSlackUsersItem.model_rebuild()
SendSlackMessageTaskParams.model_rebuild()
SendSlackMessageTaskParamsChannelsItem.model_rebuild()
SendSlackMessageTaskParamsParentMessageThreadTask.model_rebuild()
SendSlackMessageTaskParamsSlackUserGroupsItem.model_rebuild()
SendSlackMessageTaskParamsSlackUsersItem.model_rebuild()
SendSmsTaskParams.model_rebuild()
SendWhatsappMessageTaskParams.model_rebuild()
Service.model_rebuild()
ServiceResponse.model_rebuild()
ServiceResponseData.model_rebuild()
ServiceSlackAliasesItem.model_rebuild()
ServiceSlackChannelsItem.model_rebuild()
Severity.model_rebuild()
SeverityResponse.model_rebuild()
SeverityResponseData.model_rebuild()
SeveritySlackAliasesItem.model_rebuild()
SeveritySlackChannelsItem.model_rebuild()
SnapshotDatadogGraphTaskParams.model_rebuild()
SnapshotDatadogGraphTaskParamsDashboardsItem.model_rebuild()
SnapshotDatadogGraphTaskParamsPostToSlackChannelsItem.model_rebuild()
SnapshotGrafanaDashboardTaskParams.model_rebuild()
SnapshotGrafanaDashboardTaskParamsDashboardsItem.model_rebuild()
SnapshotGrafanaDashboardTaskParamsPostToSlackChannelsItem.model_rebuild()
SnapshotLookerLookTaskParams.model_rebuild()
SnapshotLookerLookTaskParamsDashboardsItem.model_rebuild()
SnapshotLookerLookTaskParamsPostToSlackChannelsItem.model_rebuild()
SnapshotNewRelicGraphTaskParams.model_rebuild()
SnapshotNewRelicGraphTaskParamsPostToSlackChannelsItem.model_rebuild()
Team.model_rebuild()
TeamResponse.model_rebuild()
TeamResponseData.model_rebuild()
TeamSlackAliasesItem.model_rebuild()
TeamSlackChannelsItem.model_rebuild()
TriggerWorkflowTaskParams.model_rebuild()
TriggerWorkflowTaskParamsResource.model_rebuild()
TriggerWorkflowTaskParamsWorkflow.model_rebuild()
TweetTwitterMessageTaskParams.model_rebuild()
UpdateActionItemTaskParams.model_rebuild()
UpdateActionItemTaskParamsAssignedToUser.model_rebuild()
UpdateAirtableTableRecordTaskParams.model_rebuild()
UpdateAlertGroupBodyDataAttributesConditionsItem.model_rebuild()
UpdateAlertGroupBodyDataAttributesTargetsItem.model_rebuild()
UpdateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem.model_rebuild()
UpdateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem.model_rebuild()
UpdateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem.model_rebuild()
UpdateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem.model_rebuild()
UpdateAsanaTaskTaskParams.model_rebuild()
UpdateAsanaTaskTaskParamsCompletion.model_rebuild()
UpdateAttachedAlertsTaskParams.model_rebuild()
UpdateClickupTaskTaskParams.model_rebuild()
UpdateClickupTaskTaskParamsPriority.model_rebuild()
UpdateCodaPageTaskParams.model_rebuild()
UpdateCodaPageTaskParamsTemplate.model_rebuild()
UpdateDashboardPanelBodyDataAttributesParamsDatasetsItem.model_rebuild()
UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemAggregate.model_rebuild()
UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItem.model_rebuild()
UpdateDashboardPanelBodyDataAttributesParamsDatasetsItemFilterItemRulesItem.model_rebuild()
UpdateEnvironmentBodyDataAttributesSlackAliasesItem.model_rebuild()
UpdateEnvironmentBodyDataAttributesSlackChannelsItem.model_rebuild()
UpdateEscalationLevelBodyDataAttributesNotificationTargetParamsItem.model_rebuild()
UpdateEscalationPathBodyDataAttributesRulesItemV0.model_rebuild()
UpdateEscalationPathBodyDataAttributesRulesItemV1.model_rebuild()
UpdateEscalationPathBodyDataAttributesRulesItemV2.model_rebuild()
UpdateEscalationPathBodyDataAttributesTimeRestrictionsItem.model_rebuild()
UpdateFunctionalityBodyDataAttributesSlackAliasesItem.model_rebuild()
UpdateFunctionalityBodyDataAttributesSlackChannelsItem.model_rebuild()
UpdateGithubIssueTaskParams.model_rebuild()
UpdateGithubIssueTaskParamsCompletion.model_rebuild()
UpdateGitlabIssueTaskParams.model_rebuild()
UpdateGitlabIssueTaskParamsCompletion.model_rebuild()
UpdateGoogleCalendarEventTaskParams.model_rebuild()
UpdateGoogleCalendarEventTaskParamsPostToSlackChannelsItem.model_rebuild()
UpdateGoogleDocsPageTaskParams.model_rebuild()
UpdateIncidentPostmortemTaskParams.model_rebuild()
UpdateIncidentStatusTimestampTaskParams.model_rebuild()
UpdateIncidentTaskParams.model_rebuild()
UpdateIncidentTypeBodyDataAttributesSlackAliasesItem.model_rebuild()
UpdateIncidentTypeBodyDataAttributesSlackChannelsItem.model_rebuild()
UpdateJiraIssueTaskParams.model_rebuild()
UpdateJiraIssueTaskParamsPriority.model_rebuild()
UpdateJiraIssueTaskParamsStatus.model_rebuild()
UpdateLinearIssueTaskParams.model_rebuild()
UpdateLinearIssueTaskParamsLabelsItem.model_rebuild()
UpdateLinearIssueTaskParamsPriority.model_rebuild()
UpdateLinearIssueTaskParamsProject.model_rebuild()
UpdateLinearIssueTaskParamsState.model_rebuild()
UpdateLiveCallRouterBodyDataAttributesPagingTargetsItem.model_rebuild()
UpdateMotionTaskTaskParams.model_rebuild()
UpdateMotionTaskTaskParamsPriority.model_rebuild()
UpdateNotionPageTaskParams.model_rebuild()
UpdateOpsgenieAlertTaskParams.model_rebuild()
UpdateOpsgenieAlertTaskParamsCompletion.model_rebuild()
UpdateOpsgenieIncidentTaskParams.model_rebuild()
UpdatePagerdutyIncidentTaskParams.model_rebuild()
UpdatePagertreeAlertTaskParams.model_rebuild()
UpdatePagertreeAlertTaskParamsTeamsItem.model_rebuild()
UpdatePagertreeAlertTaskParamsUsersItem.model_rebuild()
UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0.model_rebuild()
UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1.model_rebuild()
UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2.model_rebuild()
UpdateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem.model_rebuild()
UpdateScheduleRotationBodyDataAttributesActiveTimeAttributesItem.model_rebuild()
UpdateScheduleRotationBodyDataAttributesScheduleRotationableAttributes.model_rebuild()
UpdateServiceBodyDataAttributesSlackAliasesItem.model_rebuild()
UpdateServiceBodyDataAttributesSlackChannelsItem.model_rebuild()
UpdateServiceNowIncidentTaskParams.model_rebuild()
UpdateServiceNowIncidentTaskParamsCompletion.model_rebuild()
UpdateServiceNowIncidentTaskParamsPriority.model_rebuild()
UpdateSeverityBodyDataAttributesSlackAliasesItem.model_rebuild()
UpdateSeverityBodyDataAttributesSlackChannelsItem.model_rebuild()
UpdateShortcutStoryTaskParams.model_rebuild()
UpdateShortcutStoryTaskParamsArchivation.model_rebuild()
UpdateShortcutTaskTaskParams.model_rebuild()
UpdateShortcutTaskTaskParamsCompletion.model_rebuild()
UpdateSlackChannelTopicTaskParams.model_rebuild()
UpdateSlackChannelTopicTaskParamsChannel.model_rebuild()
UpdateStatusTaskParams.model_rebuild()
UpdateTeamBodyDataAttributesSlackAliasesItem.model_rebuild()
UpdateTeamBodyDataAttributesSlackChannelsItem.model_rebuild()
UpdateTrelloCardTaskParams.model_rebuild()
UpdateTrelloCardTaskParamsArchivation.model_rebuild()
UpdateTrelloCardTaskParamsBoard.model_rebuild()
UpdateTrelloCardTaskParamsLabelsItem.model_rebuild()
UpdateTrelloCardTaskParamsList.model_rebuild()
UpdateVictorOpsIncidentTaskParams.model_rebuild()
UpdateZendeskTicketTaskParams.model_rebuild()
UpdateZendeskTicketTaskParamsCompletion.model_rebuild()
UpdateZendeskTicketTaskParamsPriority.model_rebuild()
User.model_rebuild()
